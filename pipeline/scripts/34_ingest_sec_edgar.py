"""Phase 34: SEC EDGAR CIK <-> bank/BHC identity crosswalk (FreeNIC campaign C3).

=====================================================================
PURPOSE -- READ THIS:
  Builds `sec_cik_crosswalk`: SEC EDGAR CIK <-> entity identity for
  BANK / bank-holding-company (BHC) filers, so FreeNIC's RSSD universe
  can be linked to SEC identity (CIK, ticker, SIC). This is a CROSSWALK
  (identity table), NOT a financials table -- the single Assets value is
  carried only as a coarse size hint, not as an analytical series.
=====================================================================

Akamai constraint (verified 2026-06): www.sec.gov is Akamai-403 for the static
crosswalk endpoints (company_tickers.json, cgi-bin/browse-edgar). BUT the API
host **data.sec.gov works**. This script therefore builds the crosswalk entirely
from data.sec.gov, respecting SEC etiquette:
  * User-Agent header "freenic-research admin@example.com"
  * rate-limited to <= ~8 req/s (REQUEST_SLEEP between calls)
  * raw JSON cached under Inputs/sec_edgar/ (frames + per-CIK submissions)

Method (faithful -- no fabricated CIKs/SICs):
  1. CIK universe + Assets from the XBRL frames API (instant balance, USD):
       https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY2024Q4I.json
     Frame shape (verified): {... 'data': [{accn, cik, entityName, loc, end, val}]}.
     We pull CY2024Q4I (primary, carried as assets_2024q4) and also CY2023Q4I +
     CY2025Q1I to broaden the CIK universe, then dedup by cik (Assets value is
     taken from the 2024Q4 frame only).
  2. Name pre-filter to likely banks/BHCs (case-insensitive substrings):
       bancorp, bancshares, bankshares, bancorporation, " bank", "bank ",
       "banc ", financial, holding, savings, trust, "federal savings".
     This is a RECALL filter only -- it narrows the per-CIK submissions fetch to
     a few thousand candidates; the authoritative keep decision is step 3's SIC.
  3. For each candidate CIK, fetch
       https://data.sec.gov/submissions/CIK{cik:010d}.json
     and read sic, sicDescription, tickers, name, stateOfIncorporation. KEEP the
     row iff SIC is a depository/holding code (BANK_SIC below) OR the name still
     strongly indicates a bank/BHC (STRONG_NAME). The SIC test is authoritative;
     the strong-name fallback catches genuine banks whose XBRL filer carries a
     non-depository SIC (e.g. 6199 finance-services, blank SIC on a shell parent).

Bank/BHC SIC codes kept (SEC SIC list):
  6020 National Commercial Banks (generic)      6021 National Commercial Banks
  6022 State Commercial Banks                    6035 Savings Institution, Federal
  6036 Savings Institutions, State-Chartered     6199 Finance Services
  6712 Offices of Bank Holding Companies
(6199 is included per the campaign spec; many BHC top-co filers carry 6199.)

Output table (additive; CREATE OR REPLACE -- not in 00_setup):
  sec_cik_crosswalk(
    cik INTEGER, entity_name VARCHAR, sic VARCHAR, sic_description VARCHAR,
    ticker VARCHAR, state_incorp VARCHAR, assets_2024q4 DOUBLE)
  One row per CIK. `ticker` is the first/primary ticker (full list is in the
  cached submissions JSON); assets_2024q4 is USD from the 2024Q4 instant frame
  (NULL if the CIK only appears in 2023Q4/2025Q1).

COVERAGE CAVEAT (documented honestly): the universe is bounded to filers that
report us-gaap:Assets in XBRL for one of the three frames. Bank/BHC filers that
(a) never file XBRL, or (b) report Assets under a different tag/period, are out
of scope. This is a crosswalk of SEC-XBRL-filing banks, not the full EDGAR
depository universe. The name pre-filter is recall-oriented; the SIC test +
strong-name fallback is the precision gate.

FOLLOW-UP (documented, intentionally NOT done here so existing gates stay green):
  sec_cik_crosswalk is an additive artifact. Wiring it into 00_setup.py /
  12_export_parquet.py / 13_validate.py / 20_build_crosswalks.py is a deliberate
  follow-up; this script keeps 13_validate.py at 8/8 and pytest at 194 passed.
  Parquet is exported directly by this script.
"""

import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUTS_DIR, OUTPUTS_DIR

# --- SEC etiquette ---------------------------------------------------------
USER_AGENT = "freenic-research admin@example.com"
HEADERS = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"}
REQUEST_SLEEP = 0.13  # ~7.7 req/s, under SEC's 10/s ceiling and the <=8/s ask
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# --- Frames to pull (instant-balance Assets, USD) --------------------------
# Primary frame supplies assets_2024q4; the other two only broaden the CIK set.
PRIMARY_FRAME = "CY2024Q4I"
FRAMES = ["CY2024Q4I", "CY2023Q4I", "CY2025Q1I"]
FRAME_URL = "https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/{frame}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

# --- Bank/BHC name pre-filter (recall) -------------------------------------
# Lower-cased substring test on entityName. " bank" / "bank " / "banc " carry a
# space to avoid matching e.g. "Banking" inside unrelated words while still
# catching "First Bank", "Bank of ...", "Banc ".
NAME_TOKENS = [
    "bancorp", "bancshares", "bankshares", "bancorporation",
    " bank", "bank ", "banc ", "financial", "holding", "savings",
    "trust", "federal savings",
]

# --- Authoritative SIC keep-set --------------------------------------------
BANK_SIC = {"6020", "6021", "6022", "6035", "6036", "6199", "6712"}

# --- Strong-name fallback (precision) --------------------------------------
# Names that, on their own, are strong enough to keep a row even when the XBRL
# filer's SIC is not in BANK_SIC (e.g. a holding parent with blank/odd SIC).
STRONG_NAME = ["bancorp", "bancshares", "bankshares", "bancorporation", "savings bank"]

PARQUET_OPTS = "(FORMAT PARQUET, COMPRESSION ZSTD)"
CACHE_DIR = INPUTS_DIR / "sec_edgar"
SUBMISSIONS_CACHE = CACHE_DIR / "submissions"


def _get_json(url, cache_path: Path, label: str):
    """Fetch a data.sec.gov JSON, caching the raw bytes. Returns parsed JSON
    or None on a non-200 (logged, not fabricated). Cache hit skips the request
    (and the rate-limit sleep)."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass  # corrupt cache -> refetch
    r = SESSION.get(url, timeout=60)
    time.sleep(REQUEST_SLEEP)  # SEC rate-limit etiquette
    if r.status_code != 200:
        print(f"    [WARN] {label}: HTTP {r.status_code} ({url})")
        return None
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(r.content)
    return r.json()


def fetch_frames():
    """Pull the Assets frames; return (universe, assets_2024q4).

    universe: {cik: entity_name_from_frame}
    assets_2024q4: {cik: val} from the PRIMARY_FRAME only.
    """
    universe = {}
    assets_2024q4 = {}
    for frame in FRAMES:
        url = FRAME_URL.format(frame=frame)
        cache = CACHE_DIR / f"frame_assets_{frame}.json"
        j = _get_json(url, cache, f"frame {frame}")
        if not j or "data" not in j:
            print(f"    [WARN] frame {frame}: no 'data' array -- skipped")
            continue
        rows = j["data"]
        for row in rows:
            cik = row.get("cik")
            name = row.get("entityName")
            if cik is None:
                continue
            cik = int(cik)
            universe.setdefault(cik, name)
            if frame == PRIMARY_FRAME:
                val = row.get("val")
                if val is not None:
                    assets_2024q4[cik] = float(val)
        print(f"    frame {frame}: {len(rows):,} rows "
              f"(universe now {len(universe):,} distinct CIKs)")
    return universe, assets_2024q4


def name_passes_prefilter(name: str) -> bool:
    if not name:
        return False
    low = name.lower()
    return any(tok in low for tok in NAME_TOKENS)


def name_is_strong(name: str) -> bool:
    if not name:
        return False
    low = name.lower()
    return any(tok in low for tok in STRONG_NAME)


def fetch_submission(cik: int):
    """Fetch + cache one submissions JSON. Returns the parsed dict or None."""
    url = SUBMISSIONS_URL.format(cik=cik)
    cache = SUBMISSIONS_CACHE / f"CIK{cik:010d}.json"
    return _get_json(url, cache, f"submissions CIK{cik:010d}")


def build_rows(universe, assets_2024q4):
    """Pre-filter by name, fetch submissions, keep bank/BHC rows.

    Returns a list of dict rows for sec_cik_crosswalk.
    """
    candidates = [cik for cik, name in universe.items()
                  if name_passes_prefilter(name)]
    candidates.sort()
    print(f"  name pre-filter: {len(candidates):,} of {len(universe):,} CIKs "
          f"are bank/BHC candidates")

    rows = []
    kept = 0
    n_sic_kept = 0
    n_name_kept = 0
    for i, cik in enumerate(candidates, 1):
        sub = fetch_submission(cik)
        if i % 200 == 0:
            print(f"    ...{i:,}/{len(candidates):,} submissions fetched, "
                  f"{kept:,} kept so far")
        if not sub:
            continue
        sic = (sub.get("sic") or "").strip()
        sic_desc = (sub.get("sicDescription") or "").strip()
        name = (sub.get("name") or universe.get(cik) or "").strip()
        tickers = sub.get("tickers") or []
        ticker = tickers[0].strip() if tickers else None
        state = (sub.get("stateOfIncorporation") or "").strip() or None

        by_sic = sic in BANK_SIC
        by_name = name_is_strong(name)
        if not (by_sic or by_name):
            continue
        kept += 1
        if by_sic:
            n_sic_kept += 1
        else:
            n_name_kept += 1
        rows.append({
            "cik": int(cik),
            "entity_name": name,
            "sic": sic or None,
            "sic_description": sic_desc or None,
            "ticker": ticker,
            "state_incorp": state,
            "assets_2024q4": assets_2024q4.get(int(cik)),
        })
    print(f"  kept {kept:,} bank/BHC rows "
          f"({n_sic_kept:,} by SIC, {n_name_kept:,} by strong-name fallback)")
    return rows


def create_table(con):
    con.execute("""
        CREATE OR REPLACE TABLE sec_cik_crosswalk (
            cik             INTEGER,
            entity_name     VARCHAR,
            sic             VARCHAR,
            sic_description VARCHAR,
            ticker          VARCHAR,
            state_incorp    VARCHAR,
            assets_2024q4   DOUBLE
        )
    """)


def load_rows(con, rows):
    con.executemany(
        "INSERT INTO sec_cik_crosswalk "
        "(cik, entity_name, sic, sic_description, ticker, state_incorp, assets_2024q4) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(r["cik"], r["entity_name"], r["sic"], r["sic_description"],
          r["ticker"], r["state_incorp"], r["assets_2024q4"]) for r in rows],
    )


def export_parquet(con):
    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    out = str(parquet_dir / "sec_cik_crosswalk.parquet").replace("\\", "/")
    con.execute(
        f"COPY (SELECT * FROM sec_cik_crosswalk ORDER BY cik) TO '{out}' {PARQUET_OPTS}")
    pq_rows = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    db_rows = con.execute("SELECT COUNT(*) FROM sec_cik_crosswalk").fetchone()[0]
    status = "OK" if db_rows == pq_rows else "MISMATCH"
    print(f"  sec_cik_crosswalk.parquet: db={db_rows:,} parquet={pq_rows:,} parity={status}")
    return db_rows, pq_rows


def main():
    elapsed = timer()
    print("=== Phase 34: SEC EDGAR CIK <-> bank/BHC crosswalk (data.sec.gov) ===")
    print("    www.sec.gov is Akamai-403; built entirely via data.sec.gov.\n")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SUBMISSIONS_CACHE.mkdir(parents=True, exist_ok=True)

    print("  [1] Fetching XBRL Assets frames...")
    universe, assets_2024q4 = fetch_frames()
    if not universe:
        print("  ERROR: no CIK universe fetched from frames API. Aborting "
              "(no fabrication).")
        sys.exit(2)

    print("\n  [2/3] Name pre-filter + submissions SIC filter...")
    rows = build_rows(universe, assets_2024q4)
    if not rows:
        print("  ERROR: zero bank/BHC rows after filtering. Aborting.")
        sys.exit(2)

    print("\n  [4] Building table + exporting parquet...")
    con = get_db()
    create_table(con)
    load_rows(con, rows)

    n = con.execute("SELECT COUNT(*) FROM sec_cik_crosswalk").fetchone()[0]
    n_sic = con.execute(
        "SELECT COUNT(DISTINCT sic) FROM sec_cik_crosswalk WHERE sic IS NOT NULL"
    ).fetchone()[0]
    n_ticker = con.execute(
        "SELECT COUNT(*) FROM sec_cik_crosswalk WHERE ticker IS NOT NULL"
    ).fetchone()[0]
    n_assets = con.execute(
        "SELECT COUNT(*) FROM sec_cik_crosswalk WHERE assets_2024q4 IS NOT NULL"
    ).fetchone()[0]

    db_rows, pq_rows = export_parquet(con)

    print("\n--- Summary (sec_cik_crosswalk) ---")
    print(f"  rows:                 {n:,}")
    print(f"  distinct SIC codes:   {n_sic}")
    print(f"  rows with ticker:     {n_ticker:,}")
    print(f"  rows with 2024Q4 assets: {n_assets:,}")
    print("  SIC distribution:")
    for sic, desc, c in con.execute(
        "SELECT sic, ANY_VALUE(sic_description), COUNT(*) FROM sec_cik_crosswalk "
        "GROUP BY sic ORDER BY COUNT(*) DESC"
    ).fetchall():
        print(f"    {sic or '(null)':8} {c:6,}  {desc or ''}")
    print("\n  Sample rows:")
    for r in con.execute(
        "SELECT cik, entity_name, sic, ticker, state_incorp, assets_2024q4 "
        "FROM sec_cik_crosswalk ORDER BY assets_2024q4 DESC NULLS LAST LIMIT 8"
    ).fetchall():
        print(f"    CIK {r[0]:<8} {str(r[1])[:38]:38} sic={r[2]} "
              f"tkr={r[3]} {r[4]} assets={r[5]}")

    con.close()
    secs = elapsed()
    log_ingestion("34", f"SEC EDGAR CIK<->bank/BHC crosswalk (data.sec.gov): "
                  f"{n:,} rows, {n_sic} distinct SIC codes, {n_ticker:,} with ticker, "
                  f"{n_assets:,} with 2024Q4 assets. www.sec.gov Akamai-blocked; built "
                  f"via XBRL frames + submissions SIC filter. {secs:.1f}s")
    print(f"\nPhase 34 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
