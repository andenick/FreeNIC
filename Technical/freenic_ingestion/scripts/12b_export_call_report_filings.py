"""Single-table re-exporter for call_report_filings.parquet.

Originally written for the Phase 0A closeout (re-export so the canonical parquet
reflects all quarters). As of the Track 1 robustness work (2026-06-01) it now uses
the shared period-chunk sort-then-concatenate path in ``export_helpers.py`` — the
same mechanism Phase 12 uses for the >2 GB tables — so it no longer attempts a
single 1.9B-row global in-memory sort (the cause of the 0-byte-tmp hang). It still
verifies DB==parquet parity after writing.

Read-only connection: COPY ... TO <file> only reads the table and writes OS files;
it does not mutate the database.

Usage:
    python 12b_export_call_report_filings.py            # skip if parquet is current
    python 12b_export_call_report_filings.py --force    # re-export regardless
"""

import argparse
import datetime
import duckdb

from utils import OUTPUTS_DIR, DB_PATH, log_ingestion
import export_helpers as eh

TABLE = "call_report_filings"


def main():
    parser = argparse.ArgumentParser(
        description="Re-export call_report_filings.parquet robustly."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-export even if the parquet is already current.",
    )
    args = parser.parse_args()

    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(exist_ok=True)
    temp_dir = OUTPUTS_DIR / "_duckdb_tmp"
    out_path = parquet_dir / f"{TABLE}.parquet"
    out_str = str(out_path).replace("\\", "/")

    print(f"=== Re-exporting {TABLE}.parquet (period-chunk, spill-safe) ===")
    print("    (run alone — not alongside OCR/GPU jobs)")

    eh.cleanup_stale_tmp(parquet_dir)

    con = duckdb.connect(str(DB_PATH), read_only=True)
    eh.configure_session(con, temp_dir, memory_limit="40GB")

    markers = eh.load_markers(parquet_dir)
    if args.force:
        markers.get(TABLE, {}).pop("run_done", None)

    result = eh.export_table(
        con, "main", TABLE, parquet_dir, eh.SORT_KEYS_NONE, markers,
        force=args.force,
    )
    markers[TABLE] = result
    # Drop the per-run flag so the next invocation re-evaluates freshness.
    if isinstance(result, dict):
        result.pop("run_done", None)
    eh.save_markers(parquet_dir, markers)

    if result.get("status") == "error":
        con.close()
        print(f">>> EXPORT FAILED: {result.get('error')}")
        raise SystemExit(1)

    if result.get("status") == "skipped":
        con.close()
        print(">>> SKIPPED: parquet already current (use --force to re-export)")
        return

    # Parity check (DB vs parquet) on the freshly-written file.
    db = con.execute(
        "SELECT COUNT(*), MIN(period_end), MAX(period_end), "
        "COUNT(DISTINCT period_end) FROM call_report_filings"
    ).fetchone()
    con.close()

    pq = duckdb.connect().execute(
        f"SELECT COUNT(*), MIN(period_end), MAX(period_end), "
        f"COUNT(DISTINCT period_end) FROM read_parquet('{out_str}')"
    ).fetchone()
    size_mb = out_path.stat().st_size / (1024 ** 2)

    print(f"DB     : {db[0]:,} rows | {db[1]}..{db[2]} | {db[3]} quarters")
    print(f"PARQUET: {pq[0]:,} rows | {pq[1]}..{pq[2]} | {pq[3]} quarters | "
          f"{size_mb:,.1f} MB")
    match = (db[0] == pq[0] and db[3] == pq[3])
    print(f"PARITY (db==parquet): {match}")
    if match:
        log_ingestion(
            "12b",
            f"Re-export {TABLE}.parquet (period-chunk, spill-safe): {pq[0]:,} rows, "
            f"{pq[3]} quarters, {size_mb:,.1f} MB. {datetime.date.today()}.",
        )
        print(">>> parquet == DB (parity holds)")
    else:
        print(">>> MISMATCH after export — investigate before relying on parquet")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
