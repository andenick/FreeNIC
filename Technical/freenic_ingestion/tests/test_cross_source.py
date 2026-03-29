"""C6: Cross-source tests — crosswalk integrity and cross-source query validation."""

import pytest


def test_cross_source_view_has_data(db):
    count = db.execute("""
        SELECT COUNT(*) FROM cross_source_financials
        WHERE concept = 'total_assets' LIMIT 1
    """).fetchone()[0]
    assert count > 0, "cross_source_financials has no total_assets data"


def test_crosswalk_covers_multiple_sources(db):
    multi = db.execute("""
        SELECT concept, COUNT(DISTINCT source_table) AS sources
        FROM variable_crosswalk
        WHERE concept NOT IN ('fdic_cert', 'occ_charter', 'state_code')
        GROUP BY concept
        HAVING sources >= 2
    """).fetchall()
    assert len(multi) >= 14, f"Only {len(multi)} concepts mapped in 2+ sources"


def test_crosswalk_covers_all_source_tables(db):
    tables = db.execute(
        "SELECT DISTINCT source_table FROM variable_crosswalk ORDER BY source_table"
    ).fetchall()
    table_names = {t[0] for t in tables}
    for expected in ["luck_call_reports", "fdic_financials", "dfast_results"]:
        assert expected in table_names, f"Missing source table: {expected}"


def test_gsib_assets_cross_source_consistency(db):
    """G-SIB total assets from BHCF should be within 25% of FDIC SDI for recent quarter."""
    result = db.execute("""
        WITH bhcf AS (
            SELECT rssd_id, period_end, value AS bhcf_val
            FROM bhcf_filings
            WHERE variable_id = 'BHCK2170'
              AND period_end = '2024-12-31'
              AND rssd_id IN (1039502, 1073757, 1120754)
        ),
        fdic AS (
            SELECT rssd_id, period_end, value AS fdic_val
            FROM cross_source_financials
            WHERE concept = 'total_assets'
              AND source_table = 'fdic_financials'
              AND period_end = '2024-12-31'
              AND rssd_id IN (1039502, 1073757, 1120754)
        )
        SELECT b.rssd_id, b.bhcf_val, f.fdic_val,
               ABS(b.bhcf_val - f.fdic_val) / NULLIF(b.bhcf_val, 0) AS pct_diff
        FROM bhcf b
        JOIN fdic f ON b.rssd_id = f.rssd_id AND b.period_end = f.period_end
    """).fetchall()
    for row in result:
        rssd, bhcf, fdic, pct = row
        if pct is not None:
            assert pct < 0.25, f"RSSD {rssd}: BHCF/FDIC divergence {pct:.1%} > 25%"


def test_cross_source_has_multiple_sources_per_entity(db):
    """At least one entity should have data from 2+ sources."""
    result = db.execute("""
        SELECT rssd_id, COUNT(DISTINCT source_table) AS n
        FROM cross_source_financials
        WHERE concept = 'total_assets'
        GROUP BY rssd_id
        HAVING n >= 2
        LIMIT 1
    """).fetchone()
    assert result is not None, "No entity has total_assets from 2+ sources"
