"""C2: Schema and structure tests — verify all tables, views, and Parquet files exist."""

import pytest

MAIN_TABLES = [
    "mdrm", "reporting_forms", "institutions", "institution_attributes",
    "branches", "relationships", "transformations", "crsp_mapping",
    "bhcf_filings", "call_report_filings", "luck_call_reports",
    "occ_historical", "filing_metadata", "bank_failures",
    "fdic_financials", "fdic_sod", "dfast_results", "pillar3_disclosures",
    "variable_crosswalk",
    "fdic_history",
    "fred_series",
    "robin_panel",
    "robin_deposits_historical",
    "robin_deposits_modern",
    "robin_crosswalk",
    "bhc_ownership",
    "sector_groupings",
    "stress_scenarios_domestic",
    "stress_scenarios_international",
]

CATALOG_TABLES = [
    "variables", "filing_coverage", "entity_coverage",
    "schema_evolution", "data_sources",
]

VIEWS = [
    "bhcf_enriched", "current_hierarchy", "entity_summary",
    "variable_dictionary", "bank_failures_enriched",
    "deposit_market_share", "stress_test_summary",
    "cross_source_financials",
    "robin_panel_enriched", "failure_timeline",
]

PARQUET_FILES = [
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
    "fdic_history.parquet",
    "fred_series.parquet",
    "robin_panel.parquet",
    "robin_deposits_historical.parquet",
    "robin_deposits_modern.parquet",
    "robin_crosswalk.parquet",
    "bhc_ownership.parquet",
    "sector_groupings.parquet",
    "stress_scenarios_domestic.parquet",
    "stress_scenarios_international.parquet",
]


@pytest.mark.parametrize("table", MAIN_TABLES)
def test_main_table_exists(db, table):
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert count > 0, f"Table {table} is empty"


@pytest.mark.parametrize("table", CATALOG_TABLES)
def test_catalog_table_exists(db, table):
    count = db.execute(f"SELECT COUNT(*) FROM catalog.{table}").fetchone()[0]
    assert count > 0, f"Catalog table {table} is empty"


@pytest.mark.parametrize("view", VIEWS)
def test_view_queryable(db, view):
    result = db.execute(f"SELECT * FROM {view} LIMIT 1").fetchone()
    assert result is not None, f"View {view} returned no rows"


@pytest.mark.parametrize("filename", PARQUET_FILES)
def test_parquet_exists(parquet_dir, filename):
    path = parquet_dir / filename
    assert path.exists(), f"Parquet file {filename} missing"
    assert path.stat().st_size > 0, f"Parquet file {filename} is empty"


def test_main_table_count(db):
    tables = db.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
    """).fetchall()
    names = {t[0] for t in tables}
    for t in MAIN_TABLES:
        assert t in names, f"Missing main table: {t}"


def test_catalog_table_count(db):
    tables = db.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'catalog'
    """).fetchall()
    names = {t[0] for t in tables}
    for t in CATALOG_TABLES:
        assert t in names, f"Missing catalog table: {t}"
