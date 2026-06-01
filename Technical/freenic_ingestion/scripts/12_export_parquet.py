"""Phase 12: Export all tables to Parquet with ZSTD compression.

Outputs to Outputs/parquet/{table}.parquet for language-agnostic access.

Robustness: skip-if-current freshness gating, memory/temp spill safety, and
single-file period-chunk sort-then-concatenate for the >2 GB tables
(call_report_filings 1.9B rows, luck_call_reports, bhcf_filings, fdic_financials)
so no single billion-row global in-memory sort is attempted. See
``export_helpers.py``.

CONCURRENCY WARNING: do NOT run this full export at the same time as other heavy
local jobs that compete for RAM/disk — a 0-byte-tmp hang can occur under heavy
RAM/disk contention. Skip-if-current makes re-runs cheap, so prefer to run this
alone after ingestion settles.

Usage:
    python 12_export_parquet.py            # skip tables whose parquet is current
    python 12_export_parquet.py --force    # re-export every table regardless
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, OUTPUTS_DIR
import export_helpers as eh


# Tables to export (schema, table_name)
TABLES = [
    ('main', 'mdrm'),
    ('main', 'reporting_forms'),
    ('main', 'institutions'),
    ('main', 'institution_attributes'),
    ('main', 'branches'),
    ('main', 'relationships'),
    ('main', 'transformations'),
    ('main', 'crsp_mapping'),
    ('main', 'bhcf_filings'),
    ('main', 'call_report_filings'),
    ('main', 'luck_call_reports'),
    ('main', 'occ_historical'),
    ('main', 'filing_metadata'),
    ('main', 'bank_failures'),
    ('main', 'fdic_financials'),
    ('main', 'fdic_sod'),
    ('main', 'dfast_results'),
    ('main', 'pillar3_disclosures'),
    ('main', 'variable_crosswalk'),
    ('main', 'fdic_history'),
    ('main', 'fred_series'),
    ('main', 'robin_panel'),
    ('main', 'robin_deposits_historical'),
    ('main', 'robin_deposits_modern'),
    ('main', 'robin_crosswalk'),
    ('main', 'bhc_ownership'),
    ('main', 'sector_groupings'),
    ('main', 'stress_scenarios_domestic'),
    ('main', 'stress_scenarios_international'),
    ('main', 'fdic_sdi_features'),
    ('main', 'cdr_unrealized_losses'),
    ('main', 'entity_xref'),
    ('catalog', 'variables'),
    ('catalog', 'filing_coverage'),
    ('catalog', 'entity_coverage'),
    ('catalog', 'schema_evolution'),
    ('catalog', 'data_sources'),
]

# Sort keys for sorted Parquet export (B1.2 quick win: ~10x faster selective
# queries). The >2 GB tables (BIG_TABLES in export_helpers) carry their own
# (period_col, sort_key) there and bypass these.
SORT_KEYS = {
    'bhcf_filings': 'rssd_id, period_end',
    'call_report_filings': 'rssd_id, period_end',
    'luck_call_reports': 'entity_id, period_end',
    'fdic_financials': 'rssd_id, period_end',
    'fdic_sod': 'fdic_cert, year',
    'occ_historical': 'bank_id, report_date',
    'dfast_results': 'rssd_id, year',
    'pillar3_disclosures': 'rssd_id, period_end',
    'institutions': 'rssd_id',
    'relationships': 'rssd_parent, rssd_offspring',
    'transformations': 'rssd_successor, dt_trans',
    'bank_failures': 'closing_date',
    'crsp_mapping': 'rssd_id, dt_start',
    'robin_panel': 'bank_id, year',
    'robin_crosswalk': 'bank_id_robin',
    'bhc_ownership': 'rssd_id_bhc, rssd_id_bank',
    'fdic_sdi_features': 'rssd_id, year',
    'cdr_unrealized_losses': 'rssd_id, period_end',
    'entity_xref': 'rssd_id',
}


def main():
    parser = argparse.ArgumentParser(description="Export freenic tables to Parquet.")
    parser.add_argument(
        "--force", action="store_true",
        help="Re-export every table even if its parquet is already current.",
    )
    args = parser.parse_args()

    elapsed = timer()
    print("=== Phase 12: Export Parquet ===")
    print("    (run alone — not alongside OCR/GPU jobs; skip-if-current keeps "
          "re-runs cheap)")
    if args.force:
        print("    --force: ignoring freshness; re-exporting all tables")

    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(exist_ok=True)
    temp_dir = OUTPUTS_DIR / "_duckdb_tmp"

    # Clean any 0-byte / stale tmp parquet from a previously killed run so a
    # hung-run artifact never masks a real failure.
    removed = eh.cleanup_stale_tmp(parquet_dir)
    if removed:
        print(f"    cleaned {removed} stale tmp_*.parquet from a prior run")

    con = get_db(read_only=True)
    # Memory / spill safety: spill big sorts to a large fast disk with headroom
    # below the 50 GiB ceiling so they spill gracefully instead of hanging.
    eh.configure_session(con, temp_dir, memory_limit='40GB')
    print(f"    temp_directory={temp_dir}  memory_limit=40GB")

    # Resumable markers: a table flagged run_done in a prior partial run of THIS
    # invocation is skipped. --force clears the run flags so everything re-exports.
    markers = eh.load_markers(parquet_dir)
    if args.force:
        for m in markers.values():
            m.pop("run_done", None)

    total_size = 0.0
    n_exported = n_skipped = n_empty = n_error = 0

    for schema, table in TABLES:
        result = eh.export_table(
            con, schema, table, parquet_dir, SORT_KEYS, markers, force=args.force,
        )
        markers[table] = result
        # Persist markers after each table so a crash/kill is resumable.
        eh.save_markers(parquet_dir, markers)

        status = result.get("status")
        if status == "exported":
            n_exported += 1
            total_size += result.get("size_mb", 0.0)
        elif status == "skipped":
            n_skipped += 1
        elif status == "empty":
            n_empty += 1
        elif status == "error":
            n_error += 1

    con.close()

    # Clear the per-run resumability flags now the run finished cleanly, so the
    # NEXT invocation re-evaluates freshness from scratch (mtime vs last write).
    for m in markers.values():
        if isinstance(m, dict):
            m.pop("run_done", None)
    eh.save_markers(parquet_dir, markers)

    total_gb = total_size / 1024
    print(f"\n  Exported {n_exported}, skipped {n_skipped}, empty {n_empty}, "
          f"errors {n_error}")
    print(f"  Newly-written Parquet this run: {total_size:,.1f} MB ({total_gb:.2f} GB)")
    print(f"  Output: {parquet_dir}")

    secs = elapsed()
    log_ingestion(
        "12",
        f"Parquet export: {len(TABLES)} tables (exported {n_exported}, "
        f"skipped {n_skipped}, empty {n_empty}, errors {n_error}); "
        f"{total_size:,.1f} MB newly written. {secs:.1f}s",
    )
    print(f"\nPhase 12 complete in {secs:.1f}s ({secs/60:.1f} minutes).")
    if n_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
