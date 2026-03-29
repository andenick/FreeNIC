"""Phase 11: Build convenience views.

Creates enriched views that join filings with institution names and MDRM descriptions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


def main():
    elapsed = timer()
    print("=== Phase 11: Build Convenience Views ===")

    con = get_db()

    # 1. bhcf_enriched: Filings joined with institution names + MDRM descriptions
    print("  Creating bhcf_enriched view...")
    con.execute("""
        CREATE OR REPLACE VIEW bhcf_enriched AS
        SELECT
            f.rssd_id,
            i.name_legal AS institution_name,
            i.entity_type,
            i.state_code,
            f.period_end,
            f.variable_id,
            m.item_name AS variable_name,
            m.description AS variable_description,
            m.reporting_form,
            f.value,
            f.source_file
        FROM bhcf_filings f
        LEFT JOIN institutions i ON f.rssd_id = i.rssd_id
        LEFT JOIN (
            SELECT variable_id, item_name, description, reporting_form,
                   ROW_NUMBER() OVER (PARTITION BY variable_id ORDER BY start_date DESC NULLS LAST) AS rn
            FROM mdrm
        ) m ON f.variable_id = m.variable_id AND m.rn = 1
    """)

    # 2. current_hierarchy: Active parent-child relationships
    print("  Creating current_hierarchy view...")
    con.execute("""
        CREATE OR REPLACE VIEW current_hierarchy AS
        SELECT
            r.rssd_parent,
            p.name_legal AS parent_name,
            p.entity_type AS parent_type,
            r.rssd_offspring,
            c.name_legal AS offspring_name,
            c.entity_type AS offspring_type,
            r.dt_start,
            r.dt_end,
            r.pct_equity,
            r.relationship_level
        FROM relationships r
        LEFT JOIN institutions p ON r.rssd_parent = p.rssd_id
        LEFT JOIN institutions c ON r.rssd_offspring = c.rssd_id
        WHERE r.dt_end IS NULL
           OR r.dt_end > CURRENT_DATE
    """)

    # 3. entity_summary: Per-entity overview with filing counts
    print("  Creating entity_summary view...")
    con.execute("""
        CREATE OR REPLACE VIEW entity_summary AS
        SELECT
            i.rssd_id,
            i.name_legal,
            i.entity_type,
            i.charter_type,
            i.state_code,
            i.city,
            i.date_established,
            i.date_terminated,
            i.is_active,
            i.primary_fed_reg,
            i.fdic_cert,
            ec.filing_types,
            ec.first_filing,
            ec.last_filing,
            ec.total_filings,
            cr.permco
        FROM institutions i
        LEFT JOIN (
            SELECT rssd_id,
                   LIST(DISTINCT filing_type ORDER BY filing_type) AS filing_types,
                   MIN(first_filing) AS first_filing,
                   MAX(last_filing) AS last_filing,
                   SUM(total_filings) AS total_filings
            FROM catalog.entity_coverage
            GROUP BY rssd_id
        ) ec ON i.rssd_id = ec.rssd_id
        LEFT JOIN (
            SELECT DISTINCT rssd_id, permco
            FROM crsp_mapping
        ) cr ON i.rssd_id = cr.rssd_id
    """)

    # 4. variable_dictionary: Human-readable variable lookup
    print("  Creating variable_dictionary view...")
    con.execute("""
        CREATE OR REPLACE VIEW variable_dictionary AS
        SELECT
            cv.variable_id,
            cv.canonical_name,
            cv.mnemonic,
            cv.filing_types,
            cv.first_observed,
            cv.last_observed,
            cv.quarters_available,
            cv.entities_reporting,
            cv.confidentiality,
            cv.description_short,
            cv.schedule,
            se.quarters_present AS total_quarters_present
        FROM catalog.variables cv
        LEFT JOIN catalog.schema_evolution se ON cv.variable_id = se.variable_id
    """)

    # 5. bank_failures_enriched: Failures joined with institution context
    print("  Creating bank_failures_enriched view...")
    con.execute("""
        CREATE OR REPLACE VIEW bank_failures_enriched AS
        SELECT
            bf.*,
            i.rssd_id,
            i.entity_type,
            i.primary_fed_reg,
            i.date_established,
            i.name_legal AS nic_name
        FROM bank_failures bf
        LEFT JOIN institutions i ON i.fdic_cert = bf.cert
    """)

    # 6. deposit_market_share: Per-institution deposit market share by county
    print("  Creating deposit_market_share view...")
    con.execute("""
        CREATE OR REPLACE VIEW deposit_market_share AS
        WITH inst_deps AS (
            SELECT state_code, county, year, fdic_cert,
                   SUM(branch_deposits) AS deposits
            FROM fdic_sod
            GROUP BY state_code, county, year, fdic_cert
        ),
        county_totals AS (
            SELECT state_code, county, year,
                   SUM(deposits) AS county_total
            FROM inst_deps
            GROUP BY state_code, county, year
        )
        SELECT d.state_code, d.county, d.year, d.fdic_cert,
               i.name_legal,
               d.deposits,
               d.deposits / NULLIF(ct.county_total, 0) AS market_share
        FROM inst_deps d
        JOIN county_totals ct
            ON d.state_code = ct.state_code
            AND d.county = ct.county
            AND d.year = ct.year
        LEFT JOIN institutions i ON i.fdic_cert = d.fdic_cert
    """)

    # 7. stress_test_summary: DFAST severely adverse results only
    print("  Creating stress_test_summary view...")
    con.execute("""
        CREATE OR REPLACE VIEW stress_test_summary AS
        SELECT * FROM dfast_results
        WHERE scenario LIKE '%Severely Adverse%'
    """)

    # 8. cross_source_financials: Unified financial data across sources via crosswalk
    print("  Creating cross_source_financials view...")
    con.execute("""
        CREATE OR REPLACE VIEW cross_source_financials AS
        -- BHCF filings (match on 4-digit MDRM item number, BHCK preferred)
        SELECT
            f.rssd_id,
            i.name_legal AS institution_name,
            f.period_end,
            xw.concept,
            f.variable_id AS source_variable,
            'bhcf_filings' AS source_table,
            f.value
        FROM bhcf_filings f
        JOIN (
            SELECT DISTINCT concept, RIGHT(mdrm_variable, 4) AS item_num
            FROM variable_crosswalk
            WHERE mdrm_variable IS NOT NULL AND concept IS NOT NULL
        ) xw ON RIGHT(f.variable_id, 4) = xw.item_num
        LEFT JOIN institutions i ON f.rssd_id = i.rssd_id
        WHERE LEFT(f.variable_id, 4) = 'BHCK'

        UNION ALL

        -- Luck call reports
        SELECT
            l.entity_id AS rssd_id,
            i.name_legal AS institution_name,
            l.period_end,
            xw.concept,
            l.variable_id AS source_variable,
            'luck_call_reports' AS source_table,
            l.value
        FROM luck_call_reports l
        JOIN variable_crosswalk xw
            ON l.variable_id = xw.source_variable
            AND xw.source_table = 'luck_call_reports'
        LEFT JOIN institutions i ON l.entity_id = i.rssd_id
        WHERE xw.concept IS NOT NULL

        UNION ALL

        -- FDIC SDI financials
        SELECT
            f.rssd_id,
            i.name_legal AS institution_name,
            f.period_end,
            xw.concept,
            f.variable_id AS source_variable,
            'fdic_financials' AS source_table,
            f.value
        FROM fdic_financials f
        JOIN variable_crosswalk xw
            ON f.variable_id = xw.source_variable
            AND xw.source_table = 'fdic_financials'
        LEFT JOIN institutions i ON f.rssd_id = i.rssd_id
        WHERE xw.concept IS NOT NULL
    """)

    # 9. robin_panel_enriched: Robin panel joined with crosswalk for RSSD linkage
    print("  Creating robin_panel_enriched view...")
    con.execute("""
        CREATE OR REPLACE VIEW robin_panel_enriched AS
        SELECT
            rp.*,
            xw.rssd_id,
            xw.fdic_cert,
            xw.name_ffiec,
            xw.match_confidence,
            xw.entity_type AS ffiec_entity_type,
            xw.rssd_id_bhc
        FROM robin_panel rp
        LEFT JOIN robin_crosswalk xw ON rp.bank_id = xw.bank_id_robin
    """)

    # 10. failure_timeline: Combined Robin failures + FDIC bank_failures
    print("  Creating failure_timeline view...")
    con.execute("""
        CREATE OR REPLACE VIEW failure_timeline AS
        SELECT
            rp.bank_id,
            rp.canonical_bank_name,
            rp.state_abbrev,
            rp.year,
            rp.assets,
            rp.deposits,
            rp.equity,
            rp.failed_bank,
            rp.receivership_date,
            rp.time_to_fail,
            rp.run AS bank_run_indicator,
            xw.rssd_id,
            xw.fdic_cert,
            bf.bank_name AS fdic_name,
            bf.closing_date AS fdic_closing_date,
            bf.acquiring_institution,
            bf.fund
        FROM robin_panel rp
        LEFT JOIN robin_crosswalk xw ON rp.bank_id = xw.bank_id_robin
        LEFT JOIN bank_failures bf ON xw.fdic_cert = bf.cert
        WHERE rp.failed_bank = 1
    """)

    # Verify views work
    print("\n  Verifying views...")
    views = ['bhcf_enriched', 'current_hierarchy', 'entity_summary', 'variable_dictionary',
             'bank_failures_enriched', 'deposit_market_share', 'stress_test_summary',
             'cross_source_financials', 'robin_panel_enriched', 'failure_timeline']
    for v in views:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {v} LIMIT 1").fetchone()[0]
            sample = con.execute(f"SELECT * FROM {v} LIMIT 1").fetchdf()
            cols = len(sample.columns)
            print(f"    {v}: {count:,} rows, {cols} columns")
        except Exception as e:
            print(f"    {v}: ERROR - {e}")

    con.close()

    secs = elapsed()
    log_ingestion("11", f"Built 10 convenience views. {secs:.1f}s")
    print(f"\nPhase 11 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
