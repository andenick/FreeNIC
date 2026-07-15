"""C5: Known-value regression tests — values that must never change."""

import pytest


def test_jpmorgan_exists(db):
    row = db.execute("""
        SELECT rssd_id, name_legal, entity_type, state_code, is_active
        FROM institutions WHERE rssd_id = 1039502
    """).fetchone()
    assert row is not None, "JPMorgan (1039502) not found"
    assert row[2] == 'FHD', f"JPM entity_type={row[2]}, expected FHD"
    assert row[3] == 'NY', f"JPM state={row[3]}, expected NY"
    assert row[4] is True, "JPM should be active"


def test_jpmorgan_has_assets(db):
    row = db.execute("""
        SELECT MAX(value) FROM bhcf_filings
        WHERE rssd_id = 1039502 AND variable_id = 'BHCK2170'
    """).fetchone()
    assert row[0] is not None, "No BHCK2170 data for JPM"
    assert row[0] > 3_000_000_000, f"JPM max assets {row[0]:,.0f} < $3T (in thousands)"


def test_bank_failures_count(db):
    count = db.execute("SELECT COUNT(*) FROM bank_failures").fetchone()[0]
    assert count >= 4114, f"Bank failures {count} < 4,114"


def test_occ_historical_dates(db):
    # Span extended by Phase 9b OCC-CLV finhist: original 1867-1904 layer now
    # joined by a 1863-1941 extension. Min is 1863, max is 1941.
    result = db.execute(
        "SELECT MIN(report_date), MAX(report_date) FROM occ_historical"
    ).fetchone()
    assert str(result[0]).startswith("1863"), f"OCC min date: {result[0]}"
    assert str(result[1]).startswith("1941"), f"OCC max date: {result[1]}"


def test_luck_start_date(db):
    result = db.execute(
        "SELECT MIN(period_end) FROM luck_call_reports"
    ).fetchone()
    assert str(result[0]) == "1959-12-31", f"Luck min date: {result[0]}"


def test_mdrm_count(db):
    count = db.execute("SELECT COUNT(*) FROM mdrm").fetchone()[0]
    assert count >= 87000, f"MDRM rows {count} < 87,000"


def test_fdic_sod_coverage(db):
    count = db.execute("SELECT COUNT(*) FROM fdic_sod").fetchone()[0]
    years = db.execute("SELECT COUNT(DISTINCT year) FROM fdic_sod").fetchone()[0]
    assert count >= 2700000, f"FDIC SOD rows {count} < 2.7M"
    assert years >= 30, f"FDIC SOD years {years} < 30"


def test_crosswalk_count(db):
    count = db.execute("SELECT COUNT(*) FROM variable_crosswalk").fetchone()[0]
    assert count >= 60, f"Crosswalk entries {count} < 60"


def test_institutions_count(db):
    count = db.execute("SELECT COUNT(*) FROM institutions").fetchone()[0]
    assert count >= 200000, f"Institutions {count} < 200,000"


def test_crsp_mapping_count(db):
    count = db.execute("SELECT COUNT(*) FROM crsp_mapping").fetchone()[0]
    assert count >= 15000, f"CRSP mappings {count} < 15,000"


def test_fdic_history_count(db):
    count = db.execute("SELECT COUNT(*) FROM fdic_history").fetchone()[0]
    assert count >= 500000, f"FDIC history {count} < 500,000"


def test_fred_series_count(db):
    count = db.execute("SELECT COUNT(*) FROM fred_series").fetchone()[0]
    assert count >= 50000, f"FRED series {count} < 50,000"
    series = db.execute("SELECT COUNT(DISTINCT series_id) FROM fred_series").fetchone()[0]
    assert series >= 10, f"FRED distinct series {series} < 10"


def test_robin_panel_count(db):
    count = db.execute("SELECT COUNT(*) FROM robin_panel").fetchone()[0]
    assert count >= 2800000, f"Robin panel {count} < 2,800,000"
    banks = db.execute("SELECT COUNT(DISTINCT bank_id) FROM robin_panel").fetchone()[0]
    assert banks >= 39000, f"Robin distinct banks {banks} < 39,000"
    years = db.execute("SELECT MIN(year), MAX(year) FROM robin_panel").fetchone()
    assert years[0] <= 1870, f"Robin min year {years[0]} > 1870"
    assert years[1] >= 2020, f"Robin max year {years[1]} < 2020"


def test_robin_crosswalk_count(db):
    count = db.execute("SELECT COUNT(*) FROM robin_crosswalk").fetchone()[0]
    assert count >= 14000, f"Robin crosswalk {count} < 14,000"


def test_bhc_ownership_count(db):
    count = db.execute("SELECT COUNT(*) FROM bhc_ownership").fetchone()[0]
    assert count >= 36000, f"BHC ownership {count} < 36,000"


def test_stress_scenarios_count(db):
    count = db.execute("SELECT COUNT(*) FROM stress_scenarios_domestic").fetchone()[0]
    assert count >= 200, f"Stress scenarios domestic {count} < 200"
