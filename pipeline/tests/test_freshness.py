"""C8: Freshness tests — Parquet files exist, non-empty, reasonably recent."""

import os
from pathlib import Path

import pytest

EXPECTED_PARQUETS = [
    "mdrm.parquet", "reporting_forms.parquet", "institutions.parquet",
    "institution_attributes.parquet", "branches.parquet",
    "relationships.parquet", "transformations.parquet",
    "crsp_mapping.parquet", "bhcf_filings.parquet",
    "call_report_filings.parquet", "luck_call_reports.parquet",
    "occ_historical.parquet", "filing_metadata.parquet",
    "bank_failures.parquet", "fdic_financials.parquet",
    "fdic_sod.parquet", "dfast_results.parquet",
    "pillar3_disclosures.parquet", "variable_crosswalk.parquet",
    "catalog_variables.parquet", "catalog_filing_coverage.parquet",
    "catalog_entity_coverage.parquet", "catalog_schema_evolution.parquet",
    "catalog_data_sources.parquet",
    "fdic_sdi_features.parquet", "cdr_unrealized_losses.parquet",
]


@pytest.mark.parametrize("filename", EXPECTED_PARQUETS)
def test_parquet_not_zero_bytes(parquet_dir, filename):
    path = parquet_dir / filename
    if not path.exists():
        pytest.skip(f"{filename} not found")
    assert path.stat().st_size > 0, f"{filename} is 0 bytes"


# name -> (schema) for the DB base table each expected parquet is exported from. The
# catalog_* parquets export the catalog-schema tables (prefix stripped); everything else
# is a main-schema base table. Confirmed against information_schema 2026-07-16 (all 26 are
# BASE TABLEs, none views — so COUNT(*) uses table metadata and never scans).
_CATALOG_PARQUETS = {
    "catalog_variables", "catalog_filing_coverage", "catalog_entity_coverage",
    "catalog_schema_evolution", "catalog_data_sources",
}


def _db_ref(parquet_filename: str) -> str:
    stem = parquet_filename[:-len(".parquet")]
    if stem in _CATALOG_PARQUETS:
        return f'catalog."{stem[len("catalog_"):]}"'
    return f'main."{stem}"'


def test_parquet_matches_db_rowcount(db, parquet_dir):
    """Freshness = content parity: every exported parquet's row count must equal its live
    DB source table's row count.

    This replaces the former "parquet mtime must be < 30 days older than freenic.duckdb's
    file mtime" heuristic, which is unreliable and produced an all-tables false positive:
    the warehouse *file* mtime moves whenever the DB is opened read-write, VACUUM-tested, or
    integration-touched (the 2026-07-15 canonical-DB validation + reconstruction-table
    integration touched it to 2026-07-15) WITHOUT re-exporting the core parquets. That marked
    every June export "stale" even though the exported data is byte-for-byte current — see
    Outputs/CANONICAL_DB_DECISION_20260715.md (no DB swap; core tables unchanged). Row-count
    parity checks the thing that actually matters — did a real data change land in the DB but
    not the parquet — and a forgotten re-export after a genuine row-count change WILL fail
    here, while a mere file touch will not. No re-export is required for this gate.
    """
    from conftest import DB_PATH
    if not DB_PATH.exists():
        pytest.skip("Database file not found")

    mismatches = []
    for f in EXPECTED_PARQUETS:
        p = parquet_dir / f
        if not p.exists():
            continue  # existence is asserted by test_all_expected_parquets_exist
        pq_rows = db.execute(
            f"SELECT COUNT(*) FROM read_parquet('{p.as_posix()}')").fetchone()[0]
        db_rows = db.execute(f"SELECT COUNT(*) FROM {_db_ref(f)}").fetchone()[0]
        if pq_rows != db_rows:
            mismatches.append((f, pq_rows, db_rows))

    assert not mismatches, (
        "parquet row count != live DB table (re-export needed): "
        + ", ".join(f"{f}: parquet={pq:,} db={dbn:,}" for f, pq, dbn in mismatches))


def test_all_expected_parquets_exist(parquet_dir):
    missing = [f for f in EXPECTED_PARQUETS if not (parquet_dir / f).exists()]
    assert not missing, f"Missing Parquet files: {missing}"
