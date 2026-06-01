"""Re-export ONLY occ_historical.parquet (mirrors 12_export_parquet's mechanism)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, OUTPUTS_DIR, log_ingestion, timer

def main():
    elapsed = timer()
    parquet_dir = OUTPUTS_DIR / "parquet"
    out_path = parquet_dir / "occ_historical.parquet"
    out_str = str(out_path).replace('\\', '/')
    con = get_db(read_only=True)
    table_count = con.execute("SELECT COUNT(*) FROM occ_historical").fetchone()[0]
    # same sort key as 12_export_parquet
    con.execute(f"""
        COPY (SELECT * FROM occ_historical ORDER BY bank_id, report_date) TO '{out_str}'
        (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 122880)
    """)
    con.close()
    # verify parquet row count
    import duckdb
    pq_count = duckdb.connect().execute(f"SELECT COUNT(*) FROM read_parquet('{out_str}')").fetchone()[0]
    by_src = duckdb.connect().execute(
        f"SELECT source, COUNT(*) FROM read_parquet('{out_str}') GROUP BY source ORDER BY source"
    ).fetchall()
    size_mb = out_path.stat().st_size / (1024**2)
    print(f"Table rows:   {table_count:,}")
    print(f"Parquet rows: {pq_count:,}")
    print(f"Match: {table_count == pq_count}")
    print(f"By source in parquet: {by_src}")
    print(f"Parquet size: {size_mb:.1f} MB -> {out_path}")
    log_ingestion("9b", f"occ_historical.parquet re-export: {pq_count:,} rows ({size_mb:.1f} MB). {elapsed():.1f}s")

if __name__ == "__main__":
    main()
