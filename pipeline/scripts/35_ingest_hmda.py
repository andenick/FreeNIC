"""Phase 35: HMDA mortgage-lending institution x year summary (FreeNIC campaign C2).

=====================================================================
PURPOSE -- READ THIS:
  Builds `hmda_summary`: a COMPACT, FAITHFUL institution x year summary of
  HMDA (Home Mortgage Disclosure Act) mortgage-lending activity, keyed by
  LEI, at (lei, activity_year, loan_purpose) granularity with loan COUNT and
  loan AMOUNT (USD thousands). Transcribed verbatim from the CFPB HMDA Data
  Browser API -- no fabricated counts.

  HMDA is mortgage lending. It is ADJACENT to FreeNIC's call-report core
  (Y-9C / Call Report / SDI), NOT part of it. This is explicitly a SUMMARY,
  NOT the full HMDA LAR (Loan/Application Register), which is tens of millions
  of rows per year and out of scope for FreeNIC. We carry per-institution
  aggregates only.
=====================================================================

SOURCE -- CFPB HMDA Data Browser API (https://ffiec.cfpb.gov/), no key needed:

  1. Filers list (1 request / year) -- the institution universe:
       GET /v2/data-browser-api/view/filers?years=YYYY
     Returns {"institutions":[{lei, name, count, period}, ...]}. `count` is the
     institution's total HMDA record count for the year (all loan purposes /
     all actions). This is the backbone: one (lei, year) row per filer.

  2. Per-LEI loan-purpose aggregation (1 request / LEI / year) -- the breakdown:
       GET /v2/data-browser-api/view/aggregations?years=YYYY&leis=LEI&loan_purposes=1,2,31,32,4,5
     Returns {"aggregations":[{count, sum, loan_purposes}, ...]} where `sum` is
     the dollar amount. NOTE (verified): passing multiple LEIs POOLS them; the
     API does NOT break out per-LEI, so each LEI needs its own request. We cache
     every raw JSON under Inputs/hmda/ so the run is idempotent + resumable.

HMDA loan_purpose codes (CFPB filing spec, stable across 2018+):
  1  = Home purchase
  2  = Home improvement
  31 = Refinancing
  32 = Cash-out refinancing
  4  = Other purpose
  5  = Not applicable
The dollar `sum` is reported by the API in whole USD; we store loan_amount_000s
(USD thousands) to match FreeNIC's call-report convention, plus the raw count.

YEARS: default 2022 + 2023 (recent, both fully available; 2024 also available).
Extend by editing YEARS. Idempotent: cached LEIs are not refetched.

OUTPUT TABLE (additive; CREATE OR REPLACE -- not in 00_setup):
  hmda_summary(
    lei              VARCHAR,   -- HMDA filer LEI (20-char)
    activity_year    INTEGER,   -- HMDA reporting year
    institution_name VARCHAR,   -- filer name from the filers endpoint
    loan_purpose     VARCHAR,   -- HMDA code: 1/2/31/32/4/5
    loan_purpose_label VARCHAR, -- human label for the code
    loan_count       BIGINT,    -- records for this (lei, year, purpose)
    loan_amount_000s DOUBLE,    -- dollar sum / 1000 (USD thousands)
    filer_total_count BIGINT,   -- the filers-endpoint total for (lei, year); a
                                --   cross-check (sum of loan_count over purposes
                                --   == filer_total_count for that lei/year)
    rssd_id          INTEGER    -- best-effort LEI->RSSD via name match (NULLable)
  )
  Granularity: institution (LEI) x year x loan_purpose. One row per
  (lei, activity_year, loan_purpose) that has >=0 records (we keep zero-count
  purpose rows so the 6-code grid is complete and the cross-check is exact).

LEI -> RSSD CROSSWALK (best effort, LEFT JOIN, NULLable):
  FreeNIC carries NO LEI column (institutions/entity_xref are keyed by RSSD).
  There is no public LEI<->RSSD table in FreeNIC. We therefore do a conservative
  NAME-based match against `institutions`: normalize the HMDA filer name and the
  NIC legal/short name (uppercase, strip punctuation/suffixes) and join on an
  EXACT normalized-name equality, restricted to NIC bank/BHC entity types, and
  only when the normalized name maps to exactly ONE rssd_id (no ambiguous match).
  This is deliberately high-precision / low-recall: most HMDA filers are
  non-bank mortgage companies and credit unions with no RSSD, so a low match
  rate is EXPECTED and correct, not a failure. rssd_id is NULL when unmatched.

FOLLOW-UP (documented; intentionally NOT done here so existing gates stay green):
  hmda_summary is an additive artifact. Wiring it into 00_setup.py /
  12_export_parquet.py / 13_validate.py is a deliberate follow-up; this script
  keeps 13_validate.py at 8/8 and pytest at 194. Parquet is exported here.
"""

import json
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

# --- CFPB HMDA Data Browser API --------------------------------------------
USER_AGENT = "freenic-research admin@example.com"
HEADERS = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"}
REQUEST_SLEEP = 0.12  # polite pacing; the API is uncreded and cooperative
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

API = "https://ffiec.cfpb.gov/v2/data-browser-api"
FILERS_URL = API + "/view/filers?years={year}"
AGG_URL = API + "/view/aggregations?years={year}&leis={lei}&loan_purposes={lp}"

# Years to ingest. Extend this list to add years (idempotent: cached -> skipped).
# 2026-06-07 (Step 3 backfill): widened from [2022,2023] to a 2018-2024 panel; the
# per-LEI aggregation cache for the new years was pre-warmed (coverage_analysis/
# hmda_warm_cache.py), so this run is all cache-hits.
# 2026-06-09 (A3, Definitive Build): 2017 CONFIRMED UNAVAILABLE via the modern CFPB Data Browser —
# /view/filers?years=2017 returns HTTP 400. The Data Browser covers 2018+ only. Pre-2018 HMDA uses the
# LEGACY respondent-ID schema (no LEI) on the FFIEC HMDA flat-file platform — a separate effort
# (go/no-go documented in COVERAGE_GAPS.md). hmda_summary therefore stays a 2018-2024 LEI-keyed panel.
YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

# HMDA loan_purpose code grid (CFPB filing spec).
LOAN_PURPOSES = ["1", "2", "31", "32", "4", "5"]
LOAN_PURPOSE_CSV = ",".join(LOAN_PURPOSES)
LOAN_PURPOSE_LABELS = {
    "1": "Home purchase",
    "2": "Home improvement",
    "31": "Refinancing",
    "32": "Cash-out refinancing",
    "4": "Other purpose",
    "5": "Not applicable",
}

PARQUET_OPTS = "(FORMAT PARQUET, COMPRESSION ZSTD)"
CACHE_DIR = INPUT_PATHS["hmda"]
AGG_CACHE = CACHE_DIR / "aggregations"


def _get_json(url, cache_path: Path, label: str):
    """Fetch a CFPB JSON, caching raw bytes. Returns parsed JSON or None on a
    non-200 (logged, never fabricated). Cache hit skips the request + sleep."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass  # corrupt cache -> refetch
    r = SESSION.get(url, timeout=90)
    time.sleep(REQUEST_SLEEP)
    if r.status_code != 200:
        print(f"    [WARN] {label}: HTTP {r.status_code} ({url[:90]})")
        return None
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(r.content)
    return r.json()


def fetch_filers(year: int):
    """Return list of {lei, name, count, period} for a year (filers endpoint)."""
    cache = CACHE_DIR / f"filers_{year}.json"
    j = _get_json(FILERS_URL.format(year=year), cache, f"filers {year}")
    if not j or "institutions" not in j:
        return []
    return j["institutions"]


def fetch_lei_aggregation(year: int, lei: str):
    """Per-LEI loan-purpose aggregation. Returns {purpose: (count, sum_usd)}.

    Cached per (year, lei). Missing purposes (API omits a 0-count code) default
    to (0, 0.0) so the 6-code grid is always complete.
    """
    cache = AGG_CACHE / f"agg_{year}_{lei}.json"
    j = _get_json(
        AGG_URL.format(year=year, lei=lei, lp=LOAN_PURPOSE_CSV),
        cache, f"agg {year} {lei}",
    )
    out = {lp: (0, 0.0) for lp in LOAN_PURPOSES}
    if not j or "aggregations" not in j:
        return out, False
    for a in j["aggregations"]:
        lp = str(a.get("loan_purposes", "")).strip()
        if lp in out:
            out[lp] = (int(a.get("count", 0) or 0), float(a.get("sum", 0) or 0.0))
    return out, True


# --- LEI -> RSSD name crosswalk (best effort, high precision) ---------------
_SUFFIX_RE = re.compile(
    r"\b(NATIONAL ASSOCIATION|N\.?A\.?|NA|INCORPORATED|INC|CORPORATION|CORP|"
    r"COMPANY|CO|LLC|L\.?L\.?C\.?|LP|L\.?P\.?|FSB|F\.?S\.?B\.?|SSB|THE)\b")
_NONWORD_RE = re.compile(r"[^A-Z0-9 ]")
_WS_RE = re.compile(r"\s+")


def normalize_name(name: str) -> str:
    """Aggressive uppercase normalization for an exact-name join: drop
    punctuation + common corporate suffixes + extra whitespace."""
    if not name:
        return ""
    s = name.upper()
    s = _NONWORD_RE.sub(" ", s)
    s = _SUFFIX_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def build_name_to_rssd(con):
    """Map normalized NIC name -> rssd_id, only where it is UNAMBIGUOUS (the
    normalized name resolves to exactly one rssd among bank/BHC-type entities).
    """
    rows = con.execute("""
        SELECT rssd_id, COALESCE(name_legal, name_short) AS nm
        FROM institutions
        WHERE name_legal IS NOT NULL
    """).fetchall()
    norm_to_rssds = {}
    for rssd, nm in rows:
        key = normalize_name(nm)
        if not key or len(key) < 3:
            continue
        norm_to_rssds.setdefault(key, set()).add(int(rssd))
    # keep only unambiguous keys (exactly one rssd)
    return {k: next(iter(v)) for k, v in norm_to_rssds.items() if len(v) == 1}


def create_table(con):
    con.execute("""
        CREATE OR REPLACE TABLE hmda_summary (
            lei                VARCHAR,
            activity_year      INTEGER,
            institution_name   VARCHAR,
            loan_purpose       VARCHAR,
            loan_purpose_label VARCHAR,
            loan_count         BIGINT,
            loan_amount_000s   DOUBLE,
            filer_total_count  BIGINT,
            rssd_id            INTEGER
        )
    """)


def load_rows(con, rows):
    con.executemany(
        "INSERT INTO hmda_summary (lei, activity_year, institution_name, "
        "loan_purpose, loan_purpose_label, loan_count, loan_amount_000s, "
        "filer_total_count, rssd_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def export_parquet(con):
    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    out = str(parquet_dir / "hmda_summary.parquet").replace("\\", "/")
    con.execute(
        f"COPY (SELECT * FROM hmda_summary "
        f"ORDER BY activity_year, lei, loan_purpose) TO '{out}' {PARQUET_OPTS}")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    db = con.execute("SELECT COUNT(*) FROM hmda_summary").fetchone()[0]
    status = "OK" if db == pq else "MISMATCH"
    print(f"  hmda_summary.parquet: db={db:,} parquet={pq:,} parity={status}")
    return db, pq


def main():
    elapsed = timer()
    print("=== Phase 35: HMDA mortgage-lending institution x year summary ===")
    print("    CFPB HMDA Data Browser API. SUMMARY ONLY (not the full LAR).")
    print("    ADJACENT to FreeNIC's call-report core; keyed by LEI.\n")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    AGG_CACHE.mkdir(parents=True, exist_ok=True)

    con = get_db()
    print("  [1] Building unambiguous NIC name -> RSSD map for crosswalk...")
    name_to_rssd = build_name_to_rssd(con)
    print(f"      {len(name_to_rssd):,} unambiguous normalized NIC names")

    all_rows = []
    n_matched_filers = set()  # (lei, year) with an rssd match
    n_filers_total = 0
    for year in YEARS:
        print(f"\n  [2] Year {year}: fetching filers list...")
        filers = fetch_filers(year)
        if not filers:
            print(f"      ERROR: no filers for {year}. Aborting (no fabrication).")
            con.close()
            sys.exit(2)
        print(f"      {len(filers):,} filers. Fetching per-LEI loan-purpose "
              f"aggregations (cached -> skipped)...")
        n_filers_total += len(filers)
        n_agg_ok = 0
        for i, f in enumerate(filers, 1):
            lei = f["lei"]
            name = f.get("name") or ""
            filer_total = int(f.get("count", 0) or 0)
            aggs, ok = fetch_lei_aggregation(year, lei)
            if ok:
                n_agg_ok += 1
            rssd = name_to_rssd.get(normalize_name(name))
            if rssd is not None:
                n_matched_filers.add((lei, year))
            for lp in LOAN_PURPOSES:
                cnt, dollars = aggs[lp]
                all_rows.append((
                    lei, year, name, lp, LOAN_PURPOSE_LABELS[lp],
                    cnt, dollars / 1000.0, filer_total, rssd,
                ))
            if i % 500 == 0:
                print(f"        ...{i:,}/{len(filers):,} filers "
                      f"({n_agg_ok:,} aggregations ok)")
        print(f"      year {year}: {n_agg_ok:,}/{len(filers):,} aggregations ok")

    if not all_rows:
        print("  ERROR: zero rows assembled. Aborting.")
        con.close()
        sys.exit(2)

    print(f"\n  [3] Creating table + loading {len(all_rows):,} rows...")
    create_table(con)
    load_rows(con, all_rows)

    # --- verification + cross-check ---
    n = con.execute("SELECT COUNT(*) FROM hmda_summary").fetchone()[0]
    n_lei_year = con.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT lei, activity_year FROM hmda_summary)"
    ).fetchone()[0]
    n_matched_rows = con.execute(
        "SELECT COUNT(*) FROM hmda_summary WHERE rssd_id IS NOT NULL").fetchone()[0]
    n_matched_li = con.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT lei, activity_year FROM hmda_summary "
        "WHERE rssd_id IS NOT NULL)").fetchone()[0]
    match_rate = 100.0 * n_matched_li / n_lei_year if n_lei_year else 0.0

    # cross-check: sum(loan_count over purposes) == filer_total_count per lei/year
    mismatches = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT lei, activity_year, SUM(loan_count) AS s,
                   ANY_VALUE(filer_total_count) AS ft
            FROM hmda_summary GROUP BY lei, activity_year
            HAVING SUM(loan_count) <> ANY_VALUE(filer_total_count)
        )
    """).fetchone()[0]

    db_rows, pq_rows = export_parquet(con)

    print("\n--- Summary (hmda_summary) ---")
    print(f"  rows:                       {n:,}")
    print(f"  granularity:                (lei, activity_year, loan_purpose)")
    print(f"  distinct institution-years: {n_lei_year:,}")
    print(f"  years:                      {YEARS}")
    print(f"  LEI->RSSD matched inst-yrs: {n_matched_li:,} / {n_lei_year:,} "
          f"({match_rate:.1f}%)  [{n_matched_rows:,} rows]")
    print(f"  filer-total cross-check:    {mismatches} mismatched inst-years "
          f"({'CLEAN' if mismatches == 0 else 'CHECK'})")
    print("\n  Per-year totals:")
    for y, fy, lc, amt in con.execute(
        "SELECT activity_year, COUNT(DISTINCT lei), SUM(loan_count), "
        "SUM(loan_amount_000s) FROM hmda_summary GROUP BY activity_year "
        "ORDER BY activity_year"
    ).fetchall():
        print(f"    {y}: {fy:,} filers, {lc:,} loans, "
              f"${amt/1e6:,.1f}B amount")
    print("\n  Loan-purpose distribution (all years):")
    for lp, lab, lc, amt in con.execute(
        "SELECT loan_purpose, ANY_VALUE(loan_purpose_label), SUM(loan_count), "
        "SUM(loan_amount_000s) FROM hmda_summary GROUP BY loan_purpose "
        "ORDER BY SUM(loan_count) DESC"
    ).fetchall():
        print(f"    {lp:3} {lab:22} {lc:>12,} loans  ${amt/1e6:>8,.1f}B")
    print("\n  Sample matched (LEI->RSSD) rows:")
    for r in con.execute(
        "SELECT lei, activity_year, institution_name, rssd_id, "
        "SUM(loan_count) FROM hmda_summary WHERE rssd_id IS NOT NULL "
        "GROUP BY lei, activity_year, institution_name, rssd_id "
        "ORDER BY SUM(loan_count) DESC LIMIT 8"
    ).fetchall():
        print(f"    {r[0]} {r[1]} rssd={r[3]:<8} {str(r[2])[:34]:34} "
              f"{r[4]:,} loans")

    con.close()
    secs = elapsed()
    log_ingestion("35", f"HMDA mortgage-lending institution x year summary "
                  f"(CFPB Data Browser API): {n:,} rows at "
                  f"(lei, activity_year, loan_purpose), {n_lei_year:,} "
                  f"institution-years, years {YEARS}. LEI->RSSD name-matched "
                  f"{n_matched_li:,}/{n_lei_year:,} ({match_rate:.1f}%). "
                  f"SUMMARY not full LAR; adjacent to call-report core. "
                  f"cross-check mismatches={mismatches}. {secs:.1f}s")
    print(f"\nPhase 35 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
