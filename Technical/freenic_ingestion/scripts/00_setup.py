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
