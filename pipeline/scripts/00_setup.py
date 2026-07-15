"""Phase 0: Create empty DuckDB database with schema structure."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from utils import get_db, init_log, log_ingestion, DB_PATH, OUTPUTS_DIR

def main():
    print("=== Phase 0: Setup ===")

    # Initialize ingestion log
    init_log()

    # Create/reset database
    print(f"Creating database at {DB_PATH}")
    con = get_db()

    # Create catalog schema
    con.execute("CREATE SCHEMA IF NOT EXISTS catalog")

    # --- Reference Layer ---
    con.execute("""
        CREATE TABLE IF NOT EXISTS mdrm (
            mnemonic        VARCHAR,
            item_code       VARCHAR,
            variable_id     VARCHAR,
            item_name       VARCHAR,
            start_date      DATE,
            end_date        DATE,
            confidentiality VARCHAR,
            item_type       VARCHAR,
            reporting_form  VARCHAR,
            description     VARCHAR,
            series_glossary VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS reporting_forms (
            form_code       VARCHAR PRIMARY KEY,
            form_name       VARCHAR,
            filing_type     VARCHAR
        )
    """)

    # --- Entity Layer ---
    con.execute("""
        CREATE TABLE IF NOT EXISTS institutions (
            rssd_id         INTEGER PRIMARY KEY,
            name_legal      VARCHAR,
            name_short      VARCHAR,
            entity_type     VARCHAR,
            charter_type    INTEGER,
            charter_auth    INTEGER,
            city            VARCHAR,
            state_code      VARCHAR,
            country         VARCHAR,
            fdic_cert       INTEGER,
            date_established DATE,
            date_terminated  DATE,
            primary_fed_reg  VARCHAR,
            is_active        BOOLEAN,
            source_file      VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS institution_attributes (
            rssd_id         INTEGER,
            dt_start        DATE,
            dt_end          DATE,
            attributes      VARCHAR,
            PRIMARY KEY (rssd_id, dt_start)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            rssd_id         INTEGER,
            branch_id       INTEGER,
            dt_start        DATE,
            dt_end          DATE,
            branch_name     VARCHAR,
            city            VARCHAR,
            state_code      VARCHAR,
            country         VARCHAR,
            PRIMARY KEY (rssd_id, branch_id, dt_start)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            rssd_parent     INTEGER,
            rssd_offspring  INTEGER,
            dt_start        DATE,
            dt_end          DATE,
            relationship_level INTEGER,
            control_ind     INTEGER,
            equity_ind      INTEGER,
            pct_equity      DOUBLE,
            pct_other       DOUBLE,
            PRIMARY KEY (rssd_parent, rssd_offspring, dt_start)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS transformations (
            rssd_predecessor INTEGER,
            rssd_successor   INTEGER,
            dt_trans         DATE,
            transform_code   INTEGER,
            acct_method      INTEGER,
            PRIMARY KEY (rssd_predecessor, rssd_successor, dt_trans)
        )
    """)

    # --- Filing Layer ---
    con.execute("""
        CREATE TABLE IF NOT EXISTS bhcf_filings (
            rssd_id         INTEGER,
            period_end      DATE,
            variable_id     VARCHAR,
            value           DOUBLE,
            source_file     VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS call_report_filings (
            rssd_id         INTEGER,
            period_end      DATE,
            schedule        VARCHAR,
            variable_id     VARCHAR,
            value           DOUBLE,
            source_file     VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS luck_call_reports (
            entity_id       INTEGER,
            period_end      DATE,
            variable_id     VARCHAR,
            value           DOUBLE,
            source          VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS occ_historical (
            bank_id         INTEGER,
            report_date     DATE,
            variable_id     VARCHAR,
            value           DOUBLE,
            source          VARCHAR
        )
    """)

    # --- Public-Data Feature Layer (CLV/W16 era) ---
    # Canonical schemas for the two CLV-derived public tables. The builders
    # (31_build_sdi_feature_panel.py, 33_parse_cdr_unrealized.py) use
    # CREATE OR REPLACE TABLE, so these CREATE IF NOT EXISTS stubs exist for
    # documentation / bootstrap parity (they define the canonical column set).

    # fdic_sdi_features: SDI-derived annual feature panel, one row per (rssd_id, year),
    # 1984-2025 Q4 (413K rows). Reconciles to fdic_financials ASSET within ~0.35%.
    con.execute("""
        CREATE TABLE IF NOT EXISTS fdic_sdi_features (
            rssd_id          INTEGER,
            year             INTEGER,
            assets           DOUBLE,
            income_ratio     DOUBLE,
            noncore_proxy    DOUBLE,
            uninsured_ratio  DOUBLE,
            insured_ratio    DOUBLE,
            securities_ratio DOUBLE,
            equity_ratio     DOUBLE,
            nim              DOUBLE,
            nim_ratio        DOUBLE,
            roa              DOUBLE,
            log_age          DOUBLE,
            F1_failure       INTEGER,
            F3_failure       INTEGER,
            F5_failure       INTEGER,
            PRIMARY KEY (rssd_id, year)
        )
    """)

    # cdr_unrealized_losses: FFIEC CDR Public bulk fair-value / unrealized-loss layer,
    # one row per (rssd_id, period_end), 2019Q4-2025Q4 (46.9K rows). Values in $ thousands.
    con.execute("""
        CREATE TABLE IF NOT EXISTS cdr_unrealized_losses (
            rssd_id              INTEGER,
            cert                 INTEGER,
            period_end           DATE,
            year                 INTEGER,
            afs_amort_cost       DOUBLE,
            afs_fair_value       DOUBLE,
            htm_amort_cost       DOUBLE,
            htm_fair_value       DOUBLE,
            afs_unrealized_loss  DOUBLE,
            htm_unrealized_loss  DOUBLE,
            total_unrealized_loss DOUBLE,
            aoci                 DOUBLE,
            brokered_deposits    DOUBLE,
            time_dep_100_250k    DOUBLE,
            time_dep_gt_250k     DOUBLE,
            PRIMARY KEY (rssd_id, period_end)
        )
    """)

    # --- C3 New Sources (2026-06) ---
    # Canonical schemas; the builders (26_ingest_ncua, 34_ingest_sec_edgar, 35_ingest_hmda)
    # use CREATE OR REPLACE, so these CREATE IF NOT EXISTS define the canonical column set.
    # NCUA = credit unions (scope expansion beyond FDIC/BHC; keyed by cu_number, NOT rssd).
    con.execute("""
        CREATE TABLE IF NOT EXISTS ncua_5300 (
            cu_number       INTEGER,
            period_end      DATE,
            schedule        VARCHAR,
            account_code    VARCHAR,
            value           DOUBLE,
            source_file     VARCHAR
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ncua_cu_directory (
            cu_number       INTEGER,
            period_end      DATE,
            cu_name         VARCHAR,
            charter_state   VARCHAR,
            state           VARCHAR,
            rssd            INTEGER
        )
    """)
    # SEC EDGAR bank/BHC CIK <-> identity crosswalk (from data.sec.gov XBRL frames + submissions SIC).
    con.execute("""
        CREATE TABLE IF NOT EXISTS sec_cik_crosswalk (
            cik             INTEGER,
            entity_name     VARCHAR,
            sic             VARCHAR,
            sic_description VARCHAR,
            ticker          VARCHAR,
            state_incorp    VARCHAR,
            assets_2024q4   DOUBLE
        )
    """)
    # HMDA mortgage-lending institution x year summary (CFPB; adjacent to call-report core; keyed by LEI).
    con.execute("""
        CREATE TABLE IF NOT EXISTS hmda_summary (
            lei                VARCHAR,
            activity_year      INTEGER,
            institution_name   VARCHAR,
            loan_purpose       VARCHAR,
            loan_purpose_label VARCHAR,
            loan_count         BIGINT,
            loan_amount_000s   DOUBLE,
            filer_total_count  BIGINT,
            rssd_id            INTEGER
        )
    """)
    # nic_entity_identifiers: authoritative Fed multi-regulator ID crosswalk (37_ingest_nic_identifiers.py).
    con.execute("""
        CREATE TABLE IF NOT EXISTS nic_entity_identifiers (
            rssd_id        INTEGER,
            id_lei         VARCHAR,
            id_cusip       VARCHAR,
            id_thrift      VARCHAR,
            id_thrift_hc   VARCHAR,
            id_aba_prim    VARCHAR,
            id_fdic_cert   INTEGER,
            id_ncua        VARCHAR,
            id_occ         VARCHAR,
            id_tax         VARCHAR,
            id_rssd_hd_off INTEGER,
            status         VARCHAR
        )
    """)

    # ubpr_ratios: FFIEC UBPR standardized analytical ratios (39_ingest_ubpr.py; XBRL from CDR bulk).
    con.execute("""
        CREATE TABLE IF NOT EXISTS ubpr_ratios (
            rssd_id INTEGER, period_end DATE, ubpr_code VARCHAR, value DOUBLE, source_file VARCHAR
        )
    """)

    # y15_systemic_indicators: FR Y-15 banking-org systemic-risk / G-SIB indicators (41_ingest_y15.py).
    con.execute("""
        CREATE TABLE IF NOT EXISTS y15_systemic_indicators (
            rssd_id INTEGER, period_end DATE, risk_code VARCHAR, value DOUBLE, source_file VARCHAR
        )
    """)

    # nic_attributes_ext: additive NIC attribute extension (geography + charter/reg + status;
    # the ~30 high-value cols beyond the simplified 02 load) (37b_ingest_nic_attributes_ext.py).
    con.execute("""
        CREATE TABLE IF NOT EXISTS nic_attributes_ext (
            rssd_id INTEGER, street_line1 VARCHAR, street_line2 VARCHAR, zip_cd VARCHAR,
            county_cd VARCHAR, place_cd VARCHAR, state_home_cd VARCHAR, url VARCHAR,
            chtr_auth_cd INTEGER, chtr_type_cd INTEGER, func_reg VARCHAR, prim_fed_reg VARCHAR,
            broad_reg_cd INTEGER, dist_frs INTEGER, auth_reg_dist_frs INTEGER,
            state_inc_cd VARCHAR, state_inc_abbr VARCHAR, cntry_inc_cd VARCHAR,
            act_prim_cd VARCHAR, est_type_cd INTEGER, bnk_type_analys_cd INTEGER, org_type_cd INTEGER,
            reason_term_cd INTEGER, mjr_own_mnrty INTEGER, cnsrvtr_cd INTEGER, ihc_ind INTEGER,
            fbo_4c9_ind INTEGER, fncl_sub_ind INTEGER, ibf_ind INTEGER, domestic_ind INTEGER,
            slhc_type_ind INTEGER, fisc_yrend_mmdd VARCHAR, dt_open VARCHAR, dt_insur VARCHAR,
            status VARCHAR
        )
    """)

    # id_crosswalk: keystone identity join RSSD<->FDIC cert<->SEC CIK<->LEI + NIC reg IDs
    # (36_build_id_crosswalk.py; LEI/reg IDs authoritative from nic_entity_identifiers).
    con.execute("""
        CREATE TABLE IF NOT EXISTS id_crosswalk (
            rssd_id     INTEGER,
            fdic_cert   INTEGER,
            name_legal  VARCHAR,
            entity_type VARCHAR,
            cik         INTEGER,
            ticker      VARCHAR,
            lei         VARCHAR,
            lei_source  VARCHAR,
            id_occ      VARCHAR,
            id_ncua     VARCHAR,
            id_thrift   VARCHAR,
            id_cusip    VARCHAR,
            id_aba_prim VARCHAR,
            id_tax      VARCHAR
        )
    """)

    # --- Crosswalk Layer ---
    con.execute("""
        CREATE TABLE IF NOT EXISTS crsp_mapping (
            permco          INTEGER,
            rssd_id         INTEGER,
            name            VARCHAR,
            inst_type       VARCHAR,
            dt_start        DATE,
            dt_end          DATE,
            source_file     VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS filing_metadata (
            filing_type     VARCHAR,
            period_end      DATE,
            source_file     VARCHAR,
            entity_count    INTEGER,
            variable_count  INTEGER,
            ingestion_ts    TIMESTAMP,
            PRIMARY KEY (filing_type, period_end)
        )
    """)

    # --- Catalog Schema ---
    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog.variables (
            variable_id         VARCHAR PRIMARY KEY,
            mnemonic            VARCHAR,
            item_code           VARCHAR,
            canonical_name      VARCHAR,
            filing_types        VARCHAR[],
            first_observed      DATE,
            last_observed       DATE,
            quarters_available  INTEGER,
            entities_reporting  INTEGER,
            pct_non_null        DOUBLE,
            confidentiality     VARCHAR,
            description_short   VARCHAR,
            description_full    VARCHAR,
            schedule            VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog.filing_coverage (
            filing_type     VARCHAR,
            period_end      DATE,
            entity_count    INTEGER,
            variable_count  INTEGER,
            total_observations INTEGER,
            pct_populated   DOUBLE,
            source_files    VARCHAR[]
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog.entity_coverage (
            rssd_id         INTEGER,
            filing_type     VARCHAR,
            first_filing    DATE,
            last_filing     DATE,
            total_filings   INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog.data_sources (
            source_id       VARCHAR PRIMARY KEY,
            file_path       VARCHAR,
            file_type       VARCHAR,
            file_size_bytes BIGINT,
            row_count       INTEGER,
            column_count    INTEGER,
            date_range      VARCHAR,
            description     VARCHAR,
            ingestion_ts    TIMESTAMP,
            ingestion_script VARCHAR,
            checksum_sha256  VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog.schema_evolution (
            variable_id     VARCHAR,
            first_quarter   DATE,
            last_quarter    DATE,
            quarters_present INTEGER
        )
    """)

    # --- Robin / Volcker Layer (Session 8) ---
    # Note: These tables are created via CREATE TABLE AS SELECT in scripts 28-30.
    # Schemas documented here for reference only.
    # robin_panel: 2.87M bank-year observations (1863-2024, 156 vars)
    # robin_deposits_historical: 2,961 pre-FDIC deposit dynamics
    # robin_deposits_modern: 547 modern deposit dynamics with bank run indicator
    # robin_crosswalk: 14,286 Robin↔RSSD↔FDIC cert mappings
    # bhc_ownership: 36,668 BHC parent-child relationships with ownership %
    # sector_groupings: 16,548 CIK→SIC→sector classifications
    # stress_scenarios_domestic: 226 Fed domestic scenario rows
    # stress_scenarios_international: 226 Fed international scenario rows

    # Verify
    tables = con.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('main', 'catalog') ORDER BY table_schema, table_name").fetchall()
    print(f"\nCreated {len(tables)} tables:")
    for schema, name in tables:
        print(f"  {schema}.{name}")

    log_ingestion("0", f"Database created with {len(tables)} tables")

    con.close()
    print(f"\nDatabase size: {DB_PATH.stat().st_size / 1024:.1f} KB")
    print("Phase 0 complete.")

if __name__ == "__main__":
    main()
