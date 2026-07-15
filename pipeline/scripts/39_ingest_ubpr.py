"""Phase 39: Ingest FFIEC UBPR (Uniform Bank Performance Report) ratios.

Source: Inputs/ubpr_bulk/ubpr_single_<YYYYMMDD>.zip (acquired by 07g via CDR bulk).
Each ZIP holds ~4,543 per-bank XBRL files; each carries ~2,466 UBPR concept facts.
(The CDR TSV format crashes headless Chromium, so XBRL is the reliable source.)

Output: ubpr_ratios(rssd_id, period_end, ubpr_code, value, source_file) — long form,
one row per (bank, period, UBPR concept). Faithful: the reported numeric value as-is.
Idempotent per period; commit per ZIP (bounded WAL). NO values fabricated.
"""
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

RAW = INPUT_PATHS['cdr_call_bulk'].parent / "ubpr_bulk"
# capture concept + contextRef + value. Each bank file carries ~12 contexts (report date +
# trailing-quarter comparatives); we keep ONLY the report-date context (the comparatives are
# redundant — each period is loaded from its own zip), giving a clean one-period grain.
FACT = re.compile(r'<[\w]+:(UBPR\w+)\b[^>]*\bcontextRef="([^"]+)"[^>]*>([^<]+)</')
RSSD = re.compile(r"(\d+)\(ID RSSD\)")
PERIOD = re.compile(r"ubpr_single_(\d{4})(\d{2})(\d{2})", re.I)


def create_table(con):
    con.execute("""CREATE TABLE IF NOT EXISTS ubpr_ratios (
        rssd_id INTEGER, period_end DATE, ubpr_code VARCHAR, value DOUBLE, source_file VARCHAR)""")


def period_of(zip_path: Path) -> str:
    m = PERIOD.search(zip_path.name)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"


def already_loaded(con, period_end) -> bool:
    return con.execute("SELECT COUNT(*) FROM ubpr_ratios WHERE period_end = ?",
                       [period_end]).fetchone()[0] > 0


def ingest_zip(con, zip_path: Path) -> int:
    period_end = period_of(zip_path)
    if already_loaded(con, period_end):
        print(f"  {zip_path.name}: {period_end} already loaded -- skip (idempotent)")
        return 0
    rssds, codes, vals = [], [], []
    src = zip_path.name
    with zipfile.ZipFile(zip_path) as z:
        members = [n for n in z.namelist() if n.lower().endswith(".xml")]
        for i, n in enumerate(members):
            rm = RSSD.search(n)
            if not rm:
                continue
            rssd = int(rm.group(1))
            raw = z.read(n).decode("utf-8", "replace")
            seen = set()  # (code) already taken for the report period in this file
            for code, ctx, val in FACT.findall(raw):
                if not ctx.endswith(period_end):  # keep only the report-date context
                    continue
                if code in seen:                  # rare instant+duration dup -> first wins
                    continue
                try:
                    v = float(val)
                except ValueError:
                    continue
                seen.add(code)
                rssds.append(rssd); codes.append(code); vals.append(v)
            if (i + 1) % 1000 == 0:
                print(f"    ...{i+1:,}/{len(members):,} banks parsed ({len(vals):,} facts)")
    df = pd.DataFrame({"rssd_id": rssds, "period_end": period_end,
                       "ubpr_code": codes, "value": vals, "source_file": src})
    con.register("ubpr_df", df)
    con.execute("INSERT INTO ubpr_ratios SELECT rssd_id, CAST(period_end AS DATE), "
                "ubpr_code, value, source_file FROM ubpr_df")
    con.unregister("ubpr_df")
    con.execute("CHECKPOINT")
    print(f"  {zip_path.name}: {len(df):,} facts from {df.rssd_id.nunique():,} banks")
    return len(df)


def main():
    elapsed = timer()
    print("=== Phase 39: UBPR ratios ingestion ===")
    zips = sorted(RAW.glob("ubpr_single_*.zip"))
    if not zips:
        print(f"  no UBPR zips in {RAW}; run 07g_acquire_ubpr.py first.")
        return
    con = get_db()
    create_table(con)
    total = 0
    for zp in zips:
        total += ingest_zip(con, zp)
    n = con.execute("SELECT COUNT(*) FROM ubpr_ratios").fetchone()[0]
    nb = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM ubpr_ratios").fetchone()[0]
    npd = con.execute("SELECT COUNT(DISTINCT period_end) FROM ubpr_ratios").fetchone()[0]
    nc = con.execute("SELECT COUNT(DISTINCT ubpr_code) FROM ubpr_ratios").fetchone()[0]
    print(f"\n  ubpr_ratios: {n:,} rows | {nb:,} banks | {npd} periods | {nc:,} UBPR concepts")
    out = (OUTPUTS_DIR / "parquet" / "ubpr_ratios.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM ubpr_ratios ORDER BY period_end, rssd_id, ubpr_code) "
                f"TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  parquet={pq:,} parity={'OK' if pq == n else 'MISMATCH'}")
    con.close()
    log_ingestion("39", f"UBPR ratios: {n:,} rows, {nb:,} banks, {npd} periods, {nc:,} concepts "
                  f"(XBRL from CDR bulk). {elapsed():.1f}s")
    print(f"\nPhase 39 complete in {elapsed():.1f}s.")


if __name__ == "__main__":
    main()
