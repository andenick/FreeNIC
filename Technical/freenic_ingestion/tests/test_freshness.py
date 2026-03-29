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
]


@pytest.mark.parametrize("filename", EXPECTED_PARQUETS)
def test_parquet_not_zero_bytes(parquet_dir, filename):
    path = parquet_dir / filename
    if not path.exists():
        pytest.skip(f"{filename} not found")
    assert path.stat().st_size > 0, f"{filename} is 0 bytes"


def test_parquet_files_not_stale(parquet_dir):
    """No Parquet file should be more than 30 days older than the DB file."""
    from conftest import DB_PATH
    if not DB_PATH.exists():
        pytest.skip("Database file not found")

    db_mtime = DB_PATH.stat().st_mtime
    max_age_seconds = 30 * 24 * 3600  # 30 days

    stale = []
    for f in EXPECTED_PARQUETS:
        p = parquet_dir / f
        if p.exists():
            age_diff = db_mtime - p.stat().st_mtime
            if age_diff > max_age_seconds:
                stale.append((f, age_diff / 86400))

    assert not stale, f"Stale Parquet files: {stale}"


def test_all_expected_parquets_exist(parquet_dir):
    missing = [f for f in EXPECTED_PARQUETS if not (parquet_dir / f).exists()]
    assert not missing, f"Missing Parquet files: {missing}"
