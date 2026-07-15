"""C3: Data integrity tests — NULL dates, date ranges, duplicates, row counts."""

import pytest

# Tables with period_end date columns
FILING_TABLES_PERIOD_END = [
    ("bhcf_filings", "period_end"),
    ("call_report_filings", "period_end"),
    ("luck_call_reports", "period_end"),
    ("fdic_financials", "period_end"),
    ("pillar3_disclosures", "period_end"),
]

# Tables with other date columns
OTHER_DATE_TABLES = [
    ("occ_historical", "report_date"),
    ("bank_failures", "closing_date"),
]

ALL_DATE_TABLES = FILING_TABLES_PERIOD_END + OTHER_DATE_TABLES

# Expected date bounds
DATE_BOUNDS = {
    "bhcf_filings": ("1986-01-01", "2026-12-31"),
    # Call reports now extend to 2026Q1 (201 quarters) via FFIEC CDR bulk (07d/07e).
    "call_report_filings": ("1976-01-01", "2026-06-30"),
    # Luck slimmed 2026-06-05: pre-1976 core + 2,285 Fed-absent gap-fill cells (to 2023).
    "luck_call_reports": ("1959-01-01", "2026-12-31"),
    # OCC historical extended to 1941 by Phase 9b OCC-CLV finhist.
    "occ_historical": ("1860-01-01", "1942-01-01"),
    "fdic_financials": ("1984-01-01", "2026-12-31"),
    "bank_failures": ("1934-01-01", "2027-01-01"),
    "pillar3_disclosures": ("2020-01-01", "2026-12-31"),
}

# Minimum expected row counts
MIN_ROW_COUNTS = {
    "mdrm": 80000,
    "institutions": 200000,
    "bhcf_filings": 200000000,
    # Extended to 2025Q4 (200 quarters, ~1.912B rows) via FFIEC CDR bulk.
    "call_report_filings": 1800000000,
    # Luck slimmed to pre-1976 core + Fed-absent gap-fill (2026-06-05 dedup): ~38.1M rows.
    # 1976+ rows dropped as proven-redundant with Fed-direct call_report_filings (D1 gate, core 99.89%).
    "luck_call_reports": 35000000,
    "fdic_financials": 60000000,
    "fdic_sod": 2500000,
    # OCC original + Phase 9b OCC-CLV extension (~17.8M rows).
    "occ_historical": 17000000,
    "bank_failures": 4000,
    "dfast_results": 25000,
    "pillar3_disclosures": 7000,
    "variable_crosswalk": 60,
    # CLV-era tables promoted to permanent freeNIC tables (2026-05-31).
    "fdic_sdi_features": 400000,
    "cdr_unrealized_losses": 40000,
}


@pytest.mark.parametrize("table,col", ALL_DATE_TABLES)
def test_no_null_dates(db, table, col):
    null_count = db.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
    ).fetchone()[0]
    assert null_count == 0, f"{table}.{col} has {null_count} NULL values"


@pytest.mark.parametrize("table,col", ALL_DATE_TABLES)
def test_date_bounds(db, table, col):
    if table not in DATE_BOUNDS:
        pytest.skip(f"No bounds defined for {table}")
    lo, hi = DATE_BOUNDS[table]
    result = db.execute(
        f"SELECT MIN({col}), MAX({col}) FROM {table}"
    ).fetchone()
    assert str(result[0]) >= lo, f"{table} min date {result[0]} < {lo}"
    assert str(result[1]) <= hi, f"{table} max date {result[1]} > {hi}"


@pytest.mark.parametrize("table,min_rows", MIN_ROW_COUNTS.items())
def test_min_row_counts(db, table, min_rows):
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert count >= min_rows, f"{table}: {count} rows < minimum {min_rows}"


def test_no_duplicate_institutions(db):
    dupes = db.execute("""
        SELECT rssd_id, COUNT(*) FROM institutions
        GROUP BY rssd_id HAVING COUNT(*) > 1
    """).fetchone()
    assert dupes is None, f"Duplicate rssd_id in institutions: {dupes}"


def test_mdrm_duplicates_negligible(db):
    """MDRM source data has ~33 duplicate keys (description variants). Tolerate < 50."""
    dupes = db.execute("""
        SELECT COUNT(*) FROM (
            SELECT variable_id, reporting_form, start_date, COUNT(*) AS n FROM mdrm
            GROUP BY variable_id, reporting_form, start_date HAVING n > 1
        )
    """).fetchone()[0]
    assert dupes < 50, f"MDRM duplicate keys: {dupes} (expected < 50)"


def test_total_row_count(db):
    """Total rows across filing tables ~2.25B after the 2026-06-05 Luck dedup
    (was ~2.53B; -273.7M redundant Luck 1976+ rows now served by call_report_filings)."""
    tables = ["bhcf_filings", "call_report_filings", "luck_call_reports",
              "fdic_financials", "occ_historical", "fdic_sod",
              "dfast_results", "pillar3_disclosures"]
    total = sum(
        db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in tables
    )
    assert total > 2_200_000_000, f"Total rows {total:,} is below 2.2B"
