"""Finish Phase 0A: complete the incremental XPT ingestion (07b) then re-export
call_report_filings.parquet with the canonical sorted/ZSTD pattern (12_export)."""

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

# 1) Run 07b incremental ingestion (skips the 119 already-loaded, finishes 2009Q3-2011Q4).
spec = importlib.util.spec_from_file_location(
    "ingest07b", SCRIPTS / "07b_ingest_call_reports_incremental.py"
)
ingest07b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest07b)
ingest07b.main()

# 2) Re-export call_report_filings.parquet (match 12_export_parquet.py exactly).
from utils import get_db, OUTPUTS_DIR  # noqa: E402

out_path = OUTPUTS_DIR / "parquet" / "call_report_filings.parquet"
out_str = str(out_path).replace("\\", "/")

con = get_db()
print("\n=== Re-exporting call_report_filings.parquet ===")
con.execute(
    f"COPY (SELECT * FROM call_report_filings ORDER BY rssd_id, period_end) "
    f"TO '{out_str}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 122880)"
)
db_stats = con.execute(
    "SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end), COUNT(*) "
    "FROM call_report_filings"
).fetchone()
con.close()

import duckdb  # noqa: E402

pq = duckdb.connect().execute(
    f"SELECT COUNT(*), MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) "
    f"FROM read_parquet('{out_str}')"
).fetchone()

size_mb = out_path.stat().st_size / (1024 ** 2)
print(f"\nDB  call_report_filings: span {db_stats[0]}..{db_stats[1]}, "
      f"{db_stats[2]} quarters, {db_stats[3]:,} rows")
print(f"PARQUET: {pq[0]:,} rows, span {pq[1]}..{pq[2]}, {pq[3]} quarters, {size_mb:,.1f} MB")
print(f"ROW-COUNT MATCH (db==parquet): {db_stats[3] == pq[0]}")
print("=== Phase 0A finish complete ===")
