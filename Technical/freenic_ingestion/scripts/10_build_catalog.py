"""Phase 10: Build comprehensive catalog tables.

Populates catalog.variables, catalog.filing_coverage, catalog.entity_coverage,
catalog.schema_evolution, and catalog.data_sources from all loaded data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


def build_variables_catalog(con):
    """Build catalog.variables — every variable ever observed across all filing types."""
    print("\n  Building catalog.variables...")

    con.execute("DELETE FROM catalog.variables")

    # Collect variable stats from each filing table
    con.execute("""
        CREATE OR REPLACE TEMP TABLE all_variable_stats AS

        -- BHCF filings
        SELECT
            variable_id,
            'bhcf' AS filing_type,
            MIN(period_end) AS first_observed,
            MAX(period_end) AS last_observed,
            COUNT(DISTINCT period_end) AS quarters_available,
            COUNT(DISTINCT rssd_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM bhcf_filings
        GROUP BY variable_id

        UNION ALL

        -- Call report filings
        SELECT
            variable_id,
            'call_report' AS filing_type,
            MIN(period_end) AS first_observed,
            MAX(period_end) AS last_observed,
            COUNT(DISTINCT period_end) AS quarters_available,
            COUNT(DISTINCT rssd_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM call_report_filings
        GROUP BY variable_id

        UNION ALL

        -- Luck call reports
        SELECT
            variable_id,
            'luck' AS filing_type,
            MIN(period_end) AS first_observed,
            MAX(period_end) AS last_observed,
            COUNT(DISTINCT period_end) AS quarters_available,
            COUNT(DISTINCT entity_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM luck_call_reports
        GROUP BY variable_id

        UNION ALL

        -- OCC historical
        SELECT
            variable_id,
            'occ' AS filing_type,
            MIN(CAST(report_date AS DATE)) AS first_observed,
            MAX(CAST(report_date AS DATE)) AS last_observed,
            COUNT(DISTINCT report_date) AS quarters_available,
            COUNT(DISTINCT bank_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM occ_historical
        GROUP BY variable_id

        UNION ALL

        -- FDIC financials
        SELECT
            variable_id,
            'fdic_sdi' AS filing_type,
            MIN(period_end) AS first_observed,
            MAX(period_end) AS last_observed,
            COUNT(DISTINCT period_end) AS quarters_available,
            COUNT(DISTINCT fdic_cert) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM fdic_financials
        GROUP BY variable_id

        UNION ALL

        -- DFAST results
        SELECT
            variable_id,
            'dfast' AS filing_type,
            MIN(MAKE_DATE(year, 6, 30)) AS first_observed,
            MAX(MAKE_DATE(year, 6, 30)) AS last_observed,
            COUNT(DISTINCT year) AS quarters_available,
            COUNT(DISTINCT rssd_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM dfast_results
        GROUP BY variable_id

        UNION ALL

        -- Pillar 3 disclosures
        SELECT
            variable_id,
            'pillar3' AS filing_type,
            MIN(period_end) AS first_observed,
            MAX(period_end) AS last_observed,
            COUNT(DISTINCT period_end) AS quarters_available,
            COUNT(DISTINCT rssd_id) AS entities_reporting,
            COUNT(*) AS total_obs
        FROM pillar3_disclosures
        GROUP BY variable_id
    """)

    var_count = con.execute("SELECT COUNT(DISTINCT variable_id) FROM all_variable_stats").fetchone()[0]
    print(f"    Found {var_count:,} unique variables across all filing types")

    # Deduplicate MDRM (one row per variable_id, take first match)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE mdrm_dedup AS
        SELECT variable_id, mnemonic, item_code, item_name, confidentiality,
               description, reporting_form,
               ROW_NUMBER() OVER (PARTITION BY variable_id ORDER BY start_date DESC NULLS LAST) AS rn
        FROM mdrm
    """)

    # Aggregate across filing types and join with deduplicated MDRM
    con.execute("""
        INSERT INTO catalog.variables
        SELECT
            avs.variable_id,
            m.mnemonic,
            m.item_code,
            COALESCE(m.item_name, avs.variable_id) AS canonical_name,
            STRING_SPLIT(avs.filing_type, ',') AS filing_types,
            avs.first_observed,
            avs.last_observed,
            avs.quarters_available,
            avs.entities_reporting,
            NULL AS pct_non_null,
            m.confidentiality,
            LEFT(m.description, 200) AS description_short,
            m.description AS description_full,
            m.reporting_form AS schedule
        FROM (
            SELECT
                variable_id,
                STRING_AGG(DISTINCT filing_type, ',' ORDER BY filing_type) AS filing_type,
                MIN(first_observed) AS first_observed,
                MAX(last_observed) AS last_observed,
                SUM(quarters_available) AS quarters_available,
                MAX(entities_reporting) AS entities_reporting,
                SUM(total_obs) AS total_obs
            FROM all_variable_stats
            GROUP BY variable_id
        ) avs
        LEFT JOIN mdrm_dedup m ON UPPER(avs.variable_id) = UPPER(m.variable_id) AND m.rn = 1
    """)

    count = con.execute("SELECT COUNT(*) FROM catalog.variables").fetchone()[0]
    mdrm_matched = con.execute("SELECT COUNT(*) FROM catalog.variables WHERE mnemonic IS NOT NULL").fetchone()[0]
    print(f"    catalog.variables: {count:,} variables ({mdrm_matched:,} matched to MDRM)")

    con.execute("DROP TABLE IF EXISTS all_variable_stats")


def build_filing_coverage(con):
    """Build catalog.filing_coverage — entity/variable counts per quarter per filing type."""
    print("\n  Building catalog.filing_coverage...")

    con.execute("DELETE FROM catalog.filing_coverage")

    con.execute("""
        INSERT INTO catalog.filing_coverage (filing_type, period_end, entity_count, variable_count, total_observations)

        SELECT 'bhcf', period_end,
               COUNT(DISTINCT rssd_id), COUNT(DISTINCT variable_id), COUNT(*)
        FROM bhcf_filings
        GROUP BY period_end

        UNION ALL

        SELECT 'call_report', period_end,
               COUNT(DISTINCT rssd_id), COUNT(DISTINCT variable_id), COUNT(*)
        FROM call_report_filings
        GROUP BY period_end

        UNION ALL

        SELECT 'luck', period_end,
               COUNT(DISTINCT entity_id), COUNT(DISTINCT variable_id), COUNT(*)
        FROM luck_call_reports
        GROUP BY period_end

        UNION ALL

        SELECT 'occ', CAST(report_date AS DATE),
               COUNT(DISTINCT bank_id), COUNT(DISTINCT variable_id), COUNT(*)
        FROM occ_historical
        GROUP BY report_date

        UNION ALL

        SELECT 'fdic_sdi', period_end,
               COUNT(DISTINCT fdic_cert), COUNT(DISTINCT variable_id), COUNT(*)
        FROM fdic_financials
        GROUP BY period_end

        UNION ALL

        SELECT 'dfast', MAKE_DATE(year, 6, 30),
               COUNT(DISTINCT rssd_id), COUNT(DISTINCT variable_id), COUNT(*)
        FROM dfast_results
        GROUP BY year

        UNION ALL

        -- Robin panel (wide-format, 156 columns as "variables")
        SELECT 'robin', MAKE_DATE(year, 12, 31),
               COUNT(*), 156, COUNT(*)
        FROM robin_panel
        GROUP BY year

        UNION ALL

        -- FRED series
        SELECT 'fred', observation_date,
               1, COUNT(DISTINCT series_id), COUNT(*)
        FROM fred_series
        GROUP BY observation_date

        UNION ALL

        -- FDIC history events
        SELECT 'fdic_history', effective_date,
               COUNT(DISTINCT fdic_cert), 1, COUNT(*)
        FROM fdic_history
        WHERE effective_date IS NOT NULL
        GROUP BY effective_date
    """)

    count = con.execute("SELECT COUNT(*) FROM catalog.filing_coverage").fetchone()[0]
    print(f"    catalog.filing_coverage: {count:,} rows")

    # Print summary per filing type
    summary = con.execute("""
        SELECT filing_type,
               COUNT(*) AS quarters,
               MIN(period_end) AS first_q,
               MAX(period_end) AS last_q,
               AVG(entity_count)::INT AS avg_entities,
               AVG(variable_count)::INT AS avg_variables,
               SUM(total_observations) AS total_obs
        FROM catalog.filing_coverage
        GROUP BY filing_type
        ORDER BY filing_type
    """).fetchdf()
    print(summary.to_string(index=False))


def build_entity_coverage(con):
    """Build catalog.entity_coverage — per-entity filing history."""
    print("\n  Building catalog.entity_coverage...")

    con.execute("DELETE FROM catalog.entity_coverage")

    con.execute("""
        INSERT INTO catalog.entity_coverage (rssd_id, filing_type, first_filing, last_filing, total_filings)

        SELECT rssd_id, 'bhcf', MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end)
        FROM bhcf_filings
        GROUP BY rssd_id

        UNION ALL

        SELECT rssd_id, 'call_report', MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end)
        FROM call_report_filings
        GROUP BY rssd_id

        UNION ALL

        SELECT entity_id, 'luck', MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end)
        FROM luck_call_reports
        GROUP BY entity_id

        UNION ALL

        SELECT bank_id, 'occ', MIN(CAST(report_date AS DATE)), MAX(CAST(report_date AS DATE)),
               COUNT(DISTINCT report_date)
        FROM occ_historical
        GROUP BY bank_id

        UNION ALL

        SELECT CAST(fdic_cert AS INTEGER), 'fdic_sdi', MIN(period_end), MAX(period_end),
               COUNT(DISTINCT period_end)
        FROM fdic_financials
        GROUP BY fdic_cert

        UNION ALL

        SELECT rssd_id, 'dfast', MIN(MAKE_DATE(year, 6, 30)), MAX(MAKE_DATE(year, 6, 30)),
               COUNT(DISTINCT year)
        FROM dfast_results
        GROUP BY rssd_id

        UNION ALL

        SELECT rssd_id, 'pillar3', MIN(period_end), MAX(period_end),
               COUNT(DISTINCT period_end)
        FROM pillar3_disclosures
        GROUP BY rssd_id

        UNION ALL

        -- Robin panel entities (only those with RSSD mapping via crosswalk)
        SELECT rc.rssd_id, 'robin',
               MIN(MAKE_DATE(rp.year, 12, 31)), MAX(MAKE_DATE(rp.year, 12, 31)),
               COUNT(DISTINCT rp.year)
        FROM robin_panel rp
        JOIN robin_crosswalk rc ON CAST(rp.bank_id AS BIGINT) = CAST(rc.bank_id_robin AS BIGINT)
        WHERE rc.rssd_id IS NOT NULL
        GROUP BY rc.rssd_id

        UNION ALL

        -- FDIC history entities
        SELECT fdic_cert, 'fdic_history',
               MIN(effective_date), MAX(effective_date),
               COUNT(*)
        FROM fdic_history
        WHERE effective_date IS NOT NULL
        GROUP BY fdic_cert
    """)

    count = con.execute("SELECT COUNT(*) FROM catalog.entity_coverage").fetchone()[0]
    entities = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM catalog.entity_coverage").fetchone()[0]
    print(f"    catalog.entity_coverage: {count:,} rows ({entities:,} unique entities)")


def build_schema_evolution(con):
    """Build catalog.schema_evolution — variable presence/absence across quarters."""
    print("\n  Building catalog.schema_evolution...")

    con.execute("DELETE FROM catalog.schema_evolution")

    con.execute("""
        INSERT INTO catalog.schema_evolution (variable_id, first_quarter, last_quarter, quarters_present)

        SELECT variable_id, MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end)
        FROM (
            SELECT variable_id, period_end FROM bhcf_filings
            UNION ALL
            SELECT variable_id, period_end FROM call_report_filings
            UNION ALL
            SELECT variable_id, period_end FROM luck_call_reports
            UNION ALL
            SELECT variable_id, CAST(report_date AS DATE) FROM occ_historical
            UNION ALL
            SELECT variable_id, period_end FROM fdic_financials
            UNION ALL
            SELECT variable_id, MAKE_DATE(year, 6, 30) FROM dfast_results
            UNION ALL
            SELECT variable_id, period_end FROM pillar3_disclosures
        ) all_vars
        GROUP BY variable_id
    """)

    count = con.execute("SELECT COUNT(*) FROM catalog.schema_evolution").fetchone()[0]
    print(f"    catalog.schema_evolution: {count:,} variables tracked")

    # Show some interesting stats
    stats = con.execute("""
        SELECT
            COUNT(*) AS total_vars,
            COUNT(CASE WHEN quarters_present >= 100 THEN 1 END) AS vars_100plus_quarters,
            COUNT(CASE WHEN quarters_present >= 50 THEN 1 END) AS vars_50plus_quarters,
            COUNT(CASE WHEN quarters_present = 1 THEN 1 END) AS single_quarter_vars,
            AVG(quarters_present)::INT AS avg_quarters
        FROM catalog.schema_evolution
    """).fetchone()
    print(f"    Variables with 100+ quarters: {stats[1]:,}")
    print(f"    Variables with 50+ quarters: {stats[2]:,}")
    print(f"    Single-quarter variables: {stats[3]:,}")
    print(f"    Avg quarters per variable: {stats[4]}")


def build_data_sources(con):
    """Build catalog.data_sources — provenance for input files."""
    print("\n  Building catalog.data_sources...")

    con.execute("DELETE FROM catalog.data_sources")

    # Get source file info from filing tables
    con.execute("""
        INSERT INTO catalog.data_sources (source_id, file_path, file_type, description, ingestion_script)

        SELECT DISTINCT
            source_file AS source_id,
            source_file AS file_path,
            'bhcf_txt' AS file_type,
            'BHCF caret-delimited filing data' AS description,
            '04_ingest_bhcf_txt.py' AS ingestion_script
        FROM bhcf_filings
        WHERE source_file LIKE '%.txt'

        UNION ALL

        SELECT DISTINCT
            source_file AS source_id,
            source_file AS file_path,
            'bhcf_csv' AS file_type,
            'BHCF pre-2000 CSV filing data' AS description,
            '05_ingest_bhcf_csv.py' AS ingestion_script
        FROM bhcf_filings
        WHERE source_file LIKE '%.csv'

        UNION ALL

        SELECT DISTINCT
            source_file AS source_id,
            source_file AS file_path,
            'call_report_xpt' AS file_type,
            'Chicago Fed Call Report SAS transport file' AS description,
            '07_ingest_call_reports.py' AS ingestion_script
        FROM call_report_filings

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'luck_dta' AS file_type,
            'Luck Database Stata DTA file' AS description,
            '08_ingest_luck.py' AS ingestion_script
        FROM luck_call_reports

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'occ_tsv' AS file_type,
            'OCC Historical TSV balance sheet data' AS description,
            '09_ingest_occ.py' AS ingestion_script
        FROM occ_historical

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'fdic_api' AS file_type,
            'FDIC BankFind API bank failures data' AS description,
            '16_ingest_fdic_failures.py' AS ingestion_script
        FROM bank_failures

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'fdic_sdi_json' AS file_type,
            'FDIC SDI quarterly financial data via BankFind API' AS description,
            '17_ingest_fdic_financials.py' AS ingestion_script
        FROM fdic_financials

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'fdic_sod_json' AS file_type,
            'FDIC Summary of Deposits via BankFind API' AS description,
            '19_ingest_fdic_sod.py' AS ingestion_script
        FROM fdic_sod

        UNION ALL

        SELECT DISTINCT
            source AS source_id,
            source AS file_path,
            'dfast_csv' AS file_type,
            'Federal Reserve DFAST stress test results CSV' AS description,
            '23_ingest_dfast.py' AS ingestion_script
        FROM dfast_results

        UNION ALL

        SELECT DISTINCT
            source_file AS source_id,
            source_file AS file_path,
            'pillar3_csv' AS file_type,
            'Pillar 3 quarterly disclosure CSV from HDARP extraction' AS description,
            '24_ingest_pillar3.py' AS ingestion_script
        FROM pillar3_disclosures

        UNION ALL

        SELECT 'fdic_history_api', 'Inputs/fdic_history/', 'fdic_api',
            'FDIC institution history events via api.fdic.gov', '25_ingest_fdic_history.py'

        UNION ALL

        SELECT 'fred_banking_macro', 'Inputs/fred_h8/', 'fred_csv',
            'FRED banking and macroeconomic time series', '27_ingest_fed_h8.py'

        UNION ALL

        SELECT 'robin_panel', 'Volcker/Inputs/Robin/FAILING_BANKS/', 'robin_csv',
            'Robin Failing Banks annual panel (1863-2024)', '28_ingest_robin_panel.py'

        UNION ALL

        SELECT 'robin_deposits', 'Volcker/Inputs/Robin/FAILING_BANKS/', 'robin_csv',
            'Robin deposit dynamics (historical + modern)', '28_ingest_robin_panel.py'

        UNION ALL

        SELECT 'robin_crosswalk', 'Volcker/Technical/Catalogs/bank_identifier_crosswalk.csv', 'csv',
            'Robin bank_id to RSSD/FDIC cert crosswalk', '29_ingest_volcker_catalogs.py'

        UNION ALL

        SELECT 'bhc_ownership', 'Volcker/Technical/Catalogs/bhc_hierarchy.csv', 'csv',
            'BHC parent-child ownership hierarchy', '29_ingest_volcker_catalogs.py'

        UNION ALL

        SELECT 'sector_groupings', 'Volcker/Technical/Catalogs/sec_filings_catalog.csv', 'csv',
            'CIK to SIC to sector classifications', '29_ingest_volcker_catalogs.py'

        UNION ALL

        SELECT 'stress_scenarios', 'Inputs/dfast/', 'dfast_csv',
            'Fed stress test scenario definitions (domestic + international)', '30_ingest_stress_scenarios.py'
    """)

    count = con.execute("SELECT COUNT(*) FROM catalog.data_sources").fetchone()[0]
    print(f"    catalog.data_sources: {count:,} source files cataloged")


def main():
    elapsed = timer()
    print("=== Phase 10: Build Catalog ===")

    con = get_db()

    build_variables_catalog(con)
    build_filing_coverage(con)
    build_entity_coverage(con)
    build_schema_evolution(con)
    build_data_sources(con)

    # Final catalog summary
    print("\n--- Catalog Summary ---")
    for table in ['variables', 'filing_coverage', 'entity_coverage', 'schema_evolution', 'data_sources']:
        count = con.execute(f"SELECT COUNT(*) FROM catalog.{table}").fetchone()[0]
        print(f"  catalog.{table:<20} {count:>10,} rows")

    con.close()

    secs = elapsed()
    log_ingestion("10", f"Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. {secs:.1f}s")
    print(f"\nPhase 10 complete in {secs:.1f}s ({secs/60:.1f} minutes).")


if __name__ == "__main__":
    main()
