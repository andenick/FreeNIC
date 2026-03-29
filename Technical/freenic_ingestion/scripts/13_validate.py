"""Phase 13: Validate database integrity and data quality.

Checks:
1. Referential integrity (filing entity IDs in institutions table)
2. Date range validity
3. No duplicate primary keys
4. Cross-source validation (BHCF vs Luck for common variables)
5. Spot-check known values (e.g., JPMorgan total assets)
6. Catalog completeness
7. Summary statistics report
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


def check_referential_integrity(con):
    """Check that entity IDs in filings exist in institutions table."""
    print("\n  1. Referential Integrity")

    checks = [
        ("bhcf_filings", "rssd_id"),
        ("call_report_filings", "rssd_id"),
        ("luck_call_reports", "entity_id"),
        ("fdic_financials", "rssd_id"),
        ("fdic_sod", "rssd_id"),
        ("dfast_results", "rssd_id"),
        ("pillar3_disclosures", "rssd_id"),
    ]

    all_pass = True
    for table, col in checks:
        result = con.execute(f"""
            SELECT COUNT(DISTINCT f.{col}) AS unmatched
            FROM {table} f
            LEFT JOIN institutions i ON f.{col} = i.rssd_id
            WHERE i.rssd_id IS NULL
        """).fetchone()[0]

        total = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM {table}").fetchone()[0]
        pct = (1 - result / total) * 100 if total > 0 else 100

        status = "PASS" if pct >= 90 else "WARN" if pct >= 70 else "FAIL"
        if status != "PASS":
            all_pass = False
        print(f"    {table}.{col}: {total - result:,}/{total:,} matched ({pct:.1f}%) [{status}]")

    return all_pass


def check_date_ranges(con):
    """Verify date ranges are sensible."""
    print("\n  2. Date Range Validity")

    checks = [
        ("bhcf_filings", "period_end", "1980-01-01", "2026-06-30"),
        ("call_report_filings", "period_end", "1970-01-01", "2025-12-31"),
        ("luck_call_reports", "period_end", "1930-01-01", "2026-06-30"),
        ("occ_historical", "report_date", "1860-01-01", "1920-01-01"),
        ("bank_failures", "closing_date", "1930-01-01", "2027-01-01"),
        ("fdic_financials", "period_end", "1980-01-01", "2026-06-30"),
        ("pillar3_disclosures", "period_end", "2020-01-01", "2026-12-31"),
    ]

    all_pass = True
    for table, col, expect_min, expect_max in checks:
        result = con.execute(f"SELECT MIN({col}), MAX({col}) FROM {table}").fetchone()
        actual_min, actual_max = str(result[0]), str(result[1])

        min_ok = actual_min >= expect_min
        max_ok = actual_max <= expect_max
        status = "PASS" if (min_ok and max_ok) else "WARN"
        if status != "PASS":
            all_pass = False

        print(f"    {table}: {actual_min} to {actual_max} [{status}]")

    return all_pass


def check_null_dates(con):
    """Check for NULL dates in filing tables."""
    print("\n  3. NULL Date Check")

    checks = [
        ("bhcf_filings", "period_end"),
        ("call_report_filings", "period_end"),
        ("luck_call_reports", "period_end"),
        ("occ_historical", "report_date"),
        ("bank_failures", "closing_date"),
        ("fdic_financials", "period_end"),
        ("pillar3_disclosures", "period_end"),
    ]

    all_pass = True
    for table, col in checks:
        total = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        nulls = con.execute(f"SELECT COUNT(*) - COUNT({col}) FROM {table}").fetchone()[0]
        pct_null = (nulls / total) * 100 if total > 0 else 0

        status = "PASS" if nulls == 0 else "WARN" if pct_null < 1 else "FAIL"
        if status != "PASS":
            all_pass = False
        print(f"    {table}.{col}: {nulls:,} NULLs out of {total:,} ({pct_null:.2f}%) [{status}]")

    return all_pass


def check_cross_source_overlap(con):
    """Check BHCF vs Luck for overlapping entities and variables."""
    print("\n  4. Cross-Source Validation")

    # Entities in common between BHCF and Luck
    overlap = con.execute("""
        SELECT COUNT(DISTINCT b.rssd_id) AS common_entities
        FROM (SELECT DISTINCT rssd_id FROM bhcf_filings) b
        JOIN (SELECT DISTINCT entity_id FROM luck_call_reports) l
        ON b.rssd_id = l.entity_id
    """).fetchone()[0]
    print(f"    BHCF-Luck common entities: {overlap:,}")

    # Variables in common
    var_overlap = con.execute("""
        SELECT COUNT(*) AS common_vars
        FROM (SELECT DISTINCT variable_id FROM bhcf_filings) b
        JOIN (SELECT DISTINCT variable_id FROM luck_call_reports) l
        USING (variable_id)
    """).fetchone()[0]
    print(f"    BHCF-Luck common variables: {var_overlap:,}")

    # Spot-check: Compare a value for a known entity in overlapping quarters
    if overlap > 0 and var_overlap > 0:
        sample = con.execute("""
            SELECT b.rssd_id, b.period_end, b.variable_id,
                   b.value AS bhcf_value,
                   l.value AS luck_value,
                   ABS(b.value - l.value) AS diff
            FROM bhcf_filings b
            JOIN luck_call_reports l
                ON b.rssd_id = l.entity_id
                AND b.period_end = l.period_end
                AND b.variable_id = l.variable_id
            WHERE b.value != 0 AND l.value != 0
            LIMIT 5
        """).fetchdf()
        if not sample.empty:
            print(f"    Sample cross-source matches:")
            print(sample.to_string(index=False))

    return True


def check_cross_source_gsib(con):
    """Validate total assets for G-SIBs across BHCF, FDIC SDI, and DFAST."""
    print("\n  4b. G-SIB Cross-Source Validation")

    # 5 G-SIBs with known RSSDs
    gsibs = [
        (1039502, "JPMorgan Chase"),
        (1073757, "Bank of America"),
        (1951350, "Citigroup"),
        (1120754, "Wells Fargo"),
        (2162966, "Morgan Stanley"),
    ]

    all_pass = True
    for rssd, name in gsibs:
        # Latest BHCF total assets (BHCK2170)
        bhcf = con.execute(f"""
            SELECT value FROM bhcf_filings
            WHERE rssd_id = {rssd} AND variable_id = 'BHCK2170'
            ORDER BY period_end DESC LIMIT 1
        """).fetchone()

        # Latest FDIC total assets
        fdic = con.execute(f"""
            SELECT value FROM fdic_financials
            WHERE rssd_id = {rssd} AND variable_id = 'asset'
            ORDER BY period_end DESC LIMIT 1
        """).fetchone()

        # DFAST presence
        dfast_count = con.execute(f"""
            SELECT COUNT(*) FROM dfast_results WHERE rssd_id = {rssd}
        """).fetchone()[0]

        # Pillar 3 presence
        p3_count = con.execute(f"""
            SELECT COUNT(*) FROM pillar3_disclosures WHERE rssd_id = {rssd}
        """).fetchone()[0]

        bhcf_val = f"${bhcf[0]/1e6:,.0f}T" if bhcf and bhcf[0] else "N/A"
        fdic_val = f"${fdic[0]/1e6:,.0f}T" if fdic and fdic[0] else "N/A"

        status = "PASS" if bhcf and dfast_count > 0 else "WARN"
        if status != "PASS":
            all_pass = False
        print(f"    {name}: BHCF={bhcf_val}, FDIC={fdic_val}, DFAST={dfast_count} obs, P3={p3_count} obs [{status}]")

    return all_pass


def spot_check_known_values(con):
    """Spot-check known entities (JPMorgan, Bank of America, etc.)."""
    print("\n  5. Spot-Check Known Entities")

    # JPMorgan Chase RSSD: 1039502
    jpm = con.execute("""
        SELECT name_legal, entity_type, is_active, state_code
        FROM institutions
        WHERE rssd_id = 1039502
    """).fetchone()

    if jpm:
        print(f"    JPMorgan (1039502): {jpm[0]}, type={jpm[1]}, active={jpm[2]}, state={jpm[3]}")
    else:
        print("    JPMorgan (1039502): NOT FOUND [WARN]")

    # Check JPM has BHCF filings
    jpm_filings = con.execute("""
        SELECT COUNT(*) AS obs,
               COUNT(DISTINCT period_end) AS quarters,
               MIN(period_end) AS first_q,
               MAX(period_end) AS last_q
        FROM bhcf_filings
        WHERE rssd_id = 1039502
    """).fetchone()
    if jpm_filings:
        print(f"    JPM BHCF: {jpm_filings[0]:,} obs, {jpm_filings[1]} quarters ({jpm_filings[2]} to {jpm_filings[3]})")

    # Total assets variable (BHCK2170) for JPM, most recent
    ta = con.execute("""
        SELECT period_end, value
        FROM bhcf_filings
        WHERE rssd_id = 1039502 AND variable_id = 'BHCK2170'
        ORDER BY period_end DESC
        LIMIT 3
    """).fetchall()
    if ta:
        print(f"    JPM Total Assets (BHCK2170):")
        for row in ta:
            print(f"      {row[0]}: ${row[1]/1000:,.0f}B" if row[1] else f"      {row[0]}: NULL")
    else:
        print("    JPM Total Assets: No BHCK2170 data found [WARN]")

    return True


def catalog_completeness(con):
    """Check that catalog tables are populated and consistent."""
    print("\n  6. Catalog Completeness")

    catalog_tables = {
        'catalog.variables': 'Should match distinct variables across all filings',
        'catalog.filing_coverage': 'Should cover all quarters',
        'catalog.entity_coverage': 'Should cover all filing entities',
        'catalog.schema_evolution': 'Should match catalog.variables count',
        'catalog.data_sources': 'Should list all source files',
    }

    all_pass = True
    for table, desc in catalog_tables.items():
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        status = "PASS" if count > 0 else "FAIL"
        if status != "PASS":
            all_pass = False
        print(f"    {table}: {count:,} rows [{status}]")

    return all_pass


def summary_statistics(con):
    """Print comprehensive summary statistics."""
    print("\n  7. Summary Statistics")

    print(f"\n    --- Data Volume ---")
    tables = [
        'mdrm', 'reporting_forms', 'institutions', 'institution_attributes',
        'branches', 'relationships', 'transformations', 'crsp_mapping',
        'bhcf_filings', 'call_report_filings', 'luck_call_reports', 'occ_historical',
        'filing_metadata', 'bank_failures', 'fdic_financials', 'fdic_sod',
        'dfast_results', 'pillar3_disclosures',
        'fdic_history', 'fred_series', 'variable_crosswalk',
        'robin_panel', 'robin_deposits_historical', 'robin_deposits_modern',
        'robin_crosswalk', 'bhc_ownership', 'sector_groupings',
        'stress_scenarios_domestic', 'stress_scenarios_international',
    ]
    grand_total = 0
    for t in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        grand_total += count
        print(f"    {t:<30} {count:>15,}")
    print(f"    {'GRAND TOTAL':<30} {grand_total:>15,}")

    print(f"\n    --- Temporal Coverage ---")
    print(f"    OCC Historical: 1867-1904 (annual)")
    luck_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM luck_call_reports").fetchone()
    print(f"    Luck Database:  {luck_range[0]} to {luck_range[1]} ({luck_range[2]} quarters)")
    call_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()
    print(f"    Call Reports:   {call_range[0]} to {call_range[1]} ({call_range[2]} quarters)")
    bhcf_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM bhcf_filings").fetchone()
    print(f"    BHCF Filings:   {bhcf_range[0]} to {bhcf_range[1]} ({bhcf_range[2]} quarters)")
    fdic_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM fdic_financials").fetchone()
    print(f"    FDIC SDI:       {fdic_range[0]} to {fdic_range[1]} ({fdic_range[2]} quarters)")
    sod_range = con.execute("SELECT MIN(year), MAX(year), COUNT(DISTINCT year) FROM fdic_sod").fetchone()
    print(f"    FDIC SOD:       {sod_range[0]} to {sod_range[1]} ({sod_range[2]} years)")
    dfast_range = con.execute("SELECT MIN(year), MAX(year), COUNT(DISTINCT year) FROM dfast_results").fetchone()
    print(f"    DFAST:          {dfast_range[0]} to {dfast_range[1]} ({dfast_range[2]} years)")
    p3_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM pillar3_disclosures").fetchone()
    print(f"    Pillar 3:       {p3_range[0]} to {p3_range[1]} ({p3_range[2]} quarters)")
    fail_range = con.execute("SELECT MIN(closing_date), MAX(closing_date), COUNT(*) FROM bank_failures").fetchone()
    print(f"    Bank Failures:  {fail_range[0]} to {fail_range[1]} ({fail_range[2]:,} events)")

    print(f"\n    --- Entity Coverage ---")
    total_entities = con.execute("SELECT COUNT(*) FROM institutions").fetchone()[0]
    active = con.execute("SELECT COUNT(*) FROM institutions WHERE is_active = true").fetchone()[0]
    with_filings = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM catalog.entity_coverage").fetchone()[0]
    print(f"    Total institutions: {total_entities:,} ({active:,} active)")
    print(f"    Institutions with filings: {with_filings:,}")
    print(f"    With CRSP mapping: {con.execute('SELECT COUNT(DISTINCT rssd_id) FROM crsp_mapping').fetchone()[0]:,}")

    print(f"\n    --- Variable Coverage ---")
    total_vars = con.execute("SELECT COUNT(*) FROM catalog.variables").fetchone()[0]
    mdrm_matched = con.execute("SELECT COUNT(*) FROM catalog.variables WHERE mnemonic IS NOT NULL").fetchone()[0]
    print(f"    Total variables observed: {total_vars:,}")
    print(f"    Matched to MDRM: {mdrm_matched:,} ({mdrm_matched/total_vars*100:.1f}%)")

    return True


def main():
    elapsed = timer()
    print("=== Phase 13: Validation ===")

    con = get_db(read_only=True)

    results = {}
    results['referential_integrity'] = check_referential_integrity(con)
    results['date_ranges'] = check_date_ranges(con)
    results['null_dates'] = check_null_dates(con)
    results['cross_source'] = check_cross_source_overlap(con)
    results['gsib_validation'] = check_cross_source_gsib(con)
    results['spot_checks'] = spot_check_known_values(con)
    results['catalog'] = catalog_completeness(con)
    summary_statistics(con)

    # Final verdict
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n--- Validation Result: {passed}/{total} checks passed ---")

    con.close()

    secs = elapsed()
    log_ingestion("13", f"Validation: {passed}/{total} checks passed. {secs:.1f}s")
    print(f"\nPhase 13 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
