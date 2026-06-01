"""WS4 recovery: the full 12_export_parquet hung re-exporting the 1.9B-row
call_report_filings (already current from the 7b/12b re-export at 23:17). Export ONLY
the tables that actually changed this update — fast, avoids the giant re-sort.
Matches 12_export_parquet.py's sorted/ZSTD pattern (tmp file + atomic rename)."""

import duckdb
from pathlib import Path
from utils import DB_PATH, OUTPUTS_DIR, log_ingestion

PQ = OUTPUTS_DIR / "parquet"
# (schema, table, sort_key) — only the changed/new tables this update touched.
CHANGED = [
    ("main", "fdic_sdi_features", "rssd_id, year"),       # NEW (WS1)
    ("main", "cdr_unrealized_losses", "rssd_id, period_end"),  # NEW (WS1)
    ("main", "fdic_financials", "rssd_id, period_end"),   # WS2b +2026Q1
    ("main", "bank_failures", "closing_date"),            # WS2b +1 row + state_code fix
    ("main", "fred_series", ""),                          # WS2b refreshed
    ("main", "fdic_history", ""),                         # WS2b refreshed
    ("main", "fdic_sod", "fdic_cert, year"),              # WS2b +75k
    ("catalog", "variables", ""),                         # WS4 step 10 rebuilt
    ("catalog", "filing_coverage", ""),
    ("catalog", "entity_coverage", ""),
    ("catalog", "schema_evolution", ""),
    ("catalog", "data_sources", ""),
]

# remove the stale 0-byte tmp left by the hung full export
for t in PQ.glob("tmp_*.parquet"):
    print(f"removing stale tmp {t.name}"); t.unlink()

con = duckdb.connect(str(DB_PATH), read_only=True)
total_mb = 0.0
for schema, table, sort_key in CHANGED:
    qual = f"{schema}.{table}" if schema != "main" else table
    out_name = f"catalog_{table}" if schema == "catalog" else table
    out = PQ / f"{out_name}.parquet"
    tmp = PQ / f"tmp_{out_name}.parquet"
    try:
        n = con.execute(f"SELECT COUNT(*) FROM {qual}").fetchone()[0]
        if n == 0:
            print(f"  {qual}: empty, skip"); continue
        order = f" ORDER BY {sort_key}" if sort_key else ""
        con.execute(
            f"COPY (SELECT * FROM {qual}{order}) TO '{str(tmp).replace(chr(92),'/')}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 122880)")
        tmp.replace(out)
        mb = out.stat().st_size / (1024**2); total_mb += mb
        # parity
        pc = duckdb.connect().execute(
            f"SELECT COUNT(*) FROM read_parquet('{str(out).replace(chr(92),'/')}')").fetchone()[0]
        print(f"  {out_name}: {n:,} rows -> {mb:,.1f} MB  parity={'OK' if pc==n else f'MISMATCH {pc}'}")
    except Exception as e:
        print(f"  {qual}: ERROR {str(e)[:120]}")
con.close()
log_ingestion("12", f"Targeted re-export of {len(CHANGED)} changed/new tables "
                    f"(fdic_sdi_features, cdr_unrealized_losses, refreshed FDIC/FRED + catalog); "
                    f"{total_mb:,.1f} MB. call_report_filings already current (7b 23:17).")
print(f"\nTotal: {total_mb:,.1f} MB across {len(CHANGED)} tables.")
