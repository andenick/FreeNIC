"""Phase 2: Ingest NIC Attributes Tables using DuckDB native CSV reader.

Sources: CSV_ATTRIBUTES_ACTIVE, CSV_ATTRIBUTES_CLOSED, CSV_ATTRIBUTES_BRANCHES,
         CSV_RELATIONSHIPS, CSV_TRANSFORMATIONS
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

ATTRS_DIR = INPUT_PATHS['attributes']


def main():
    elapsed = timer()
    print("=== Phase 2: Entity/Attributes Ingestion (DuckDB native) ===")

    con = get_db()

    # Clear existing data
    for table in ['institutions', 'institution_attributes', 'branches', 'relationships', 'transformations']:
        con.execute(f"DELETE FROM {table}")

    # Drop and recreate institution_attributes with simpler schema
    con.execute("DROP TABLE IF EXISTS institution_attributes")
    con.execute("""
        CREATE TABLE institution_attributes (
            rssd_id         INTEGER,
            dt_start        VARCHAR,
            dt_end          VARCHAR,
            bhc_ind         INTEGER,
            fhc_ind         INTEGER,
            slhc_ind        INTEGER,
            broad_reg_cd    INTEGER,
            insur_pri_cd    INTEGER,
            mbr_frs_ind     INTEGER,
            mbr_fhlbs_ind   INTEGER,
            sec_rptg_status INTEGER,
            bank_cnt        INTEGER,
            source          VARCHAR
        )
    """)

    # --- 1. ACTIVE INSTITUTIONS ---
    active_path = ATTRS_DIR / "CSV_ATTRIBUTES_ACTIVE" / "CSV_ATTRIBUTES_ACTIVE.CSV"
    print(f"\n1. Loading Active institutions from {active_path.name}...")

    # Read raw into a temp table, then extract
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE raw_active AS
        SELECT * FROM read_csv('{str(active_path).replace(chr(92), "/")}',
            header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
    """)
    n_raw = con.execute("SELECT COUNT(*) FROM raw_active").fetchone()[0]
    print(f"  Raw rows loaded: {n_raw:,}")

    # Get column names
    cols = [desc[0] for desc in con.execute("SELECT * FROM raw_active LIMIT 0").description]
    print(f"  Columns: {len(cols)}")

    # Find the RSSD column (might be #ID_RSSD or ID_RSSD)
    rssd_col = next((c for c in cols if 'ID_RSSD' in c.upper()), cols[0])
    print(f"  RSSD column: {rssd_col}")

    # Insert into institutions
    con.execute(f"""
        INSERT OR IGNORE INTO institutions
        (rssd_id, name_legal, name_short, entity_type, charter_type, charter_auth,
         city, state_code, country, fdic_cert, date_established, date_terminated,
         primary_fed_reg, is_active, source_file)
        SELECT DISTINCT ON ("{rssd_col}")
            CAST("{rssd_col}" AS INTEGER),
            TRIM(NM_LGL),
            TRIM(NM_SHORT),
            TRIM(ENTITY_TYPE),
            TRY_CAST(CHTR_TYPE_CD AS INTEGER),
            TRY_CAST(CHTR_AUTH_CD AS INTEGER),
            TRIM(CITY),
            TRIM(STATE_ABBR_NM),
            TRIM(CNTRY_NM),
            TRY_CAST(ID_FDIC_CERT AS INTEGER),
            TRY_CAST(DT_EXIST_CMNC AS DATE),
            TRY_CAST(DT_EXIST_TERM AS DATE),
            TRIM(CAST(PRIM_FED_REG AS VARCHAR)),
            TRUE,
            'ACTIVE'
        FROM raw_active
        WHERE "{rssd_col}" IS NOT NULL AND CAST("{rssd_col}" AS INTEGER) != 0
    """)
    n_active = con.execute("SELECT COUNT(*) FROM institutions WHERE is_active = TRUE").fetchone()[0]
    print(f"  Active institutions inserted: {n_active:,}")

    # Insert attribute records
    con.execute(f"""
        INSERT INTO institution_attributes
        (rssd_id, dt_start, dt_end, bhc_ind, fhc_ind, slhc_ind, broad_reg_cd,
         insur_pri_cd, mbr_frs_ind, mbr_fhlbs_ind, sec_rptg_status, bank_cnt, source)
        SELECT
            CAST("{rssd_col}" AS INTEGER),
            CAST(D_DT_START AS VARCHAR),
            CAST(D_DT_END AS VARCHAR),
            TRY_CAST(BHC_IND AS INTEGER),
            TRY_CAST(FHC_IND AS INTEGER),
            TRY_CAST(SLHC_IND AS INTEGER),
            TRY_CAST(BROAD_REG_CD AS INTEGER),
            TRY_CAST(INSUR_PRI_CD AS INTEGER),
            TRY_CAST(MBR_FRS_IND AS INTEGER),
            TRY_CAST(MBR_FHLBS_IND AS INTEGER),
            TRY_CAST(SEC_RPTG_STATUS AS INTEGER),
            TRY_CAST(BANK_CNT AS INTEGER),
            'ACTIVE'
        FROM raw_active
        WHERE "{rssd_col}" IS NOT NULL
    """)
    n_active_attrs = con.execute("SELECT COUNT(*) FROM institution_attributes WHERE source='ACTIVE'").fetchone()[0]
    print(f"  Active attribute records: {n_active_attrs:,}")
    con.execute("DROP TABLE IF EXISTS raw_active")

    # --- 2. CLOSED INSTITUTIONS ---
    closed_path = ATTRS_DIR / "CSV_ATTRIBUTES_CLOSED" / "CSV_ATTRIBUTES_CLOSED.CSV"
    print(f"\n2. Loading Closed institutions from {closed_path.name}...")

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE raw_closed AS
        SELECT * FROM read_csv('{str(closed_path).replace(chr(92), "/")}',
            header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
    """)
    n_raw_closed = con.execute("SELECT COUNT(*) FROM raw_closed").fetchone()[0]
    cols_closed = [desc[0] for desc in con.execute("SELECT * FROM raw_closed LIMIT 0").description]
    rssd_col_c = next((c for c in cols_closed if 'ID_RSSD' in c.upper()), cols_closed[0])
    print(f"  Raw rows: {n_raw_closed:,}, RSSD column: {rssd_col_c}")

    con.execute(f"""
        INSERT OR IGNORE INTO institutions
        (rssd_id, name_legal, name_short, entity_type, charter_type, charter_auth,
         city, state_code, country, fdic_cert, date_established, date_terminated,
         primary_fed_reg, is_active, source_file)
        SELECT DISTINCT ON ("{rssd_col_c}")
            CAST("{rssd_col_c}" AS INTEGER),
            TRIM(NM_LGL),
            TRIM(NM_SHORT),
            TRIM(ENTITY_TYPE),
            TRY_CAST(CHTR_TYPE_CD AS INTEGER),
            TRY_CAST(CHTR_AUTH_CD AS INTEGER),
            TRIM(CITY),
            TRIM(STATE_ABBR_NM),
            TRIM(CNTRY_NM),
            TRY_CAST(ID_FDIC_CERT AS INTEGER),
            TRY_CAST(DT_EXIST_CMNC AS DATE),
            TRY_CAST(DT_EXIST_TERM AS DATE),
            TRIM(CAST(PRIM_FED_REG AS VARCHAR)),
            FALSE,
            'CLOSED'
        FROM raw_closed
        WHERE "{rssd_col_c}" IS NOT NULL AND CAST("{rssd_col_c}" AS INTEGER) != 0
    """)
    n_closed = con.execute("SELECT COUNT(*) FROM institutions WHERE is_active = FALSE").fetchone()[0]
    print(f"  Closed institutions inserted: {n_closed:,}")

    con.execute(f"""
        INSERT INTO institution_attributes
        (rssd_id, dt_start, dt_end, bhc_ind, fhc_ind, slhc_ind, broad_reg_cd,
         insur_pri_cd, mbr_frs_ind, mbr_fhlbs_ind, sec_rptg_status, bank_cnt, source)
        SELECT
            CAST("{rssd_col_c}" AS INTEGER),
            CAST(D_DT_START AS VARCHAR),
            CAST(D_DT_END AS VARCHAR),
            TRY_CAST(BHC_IND AS INTEGER),
            TRY_CAST(FHC_IND AS INTEGER),
            TRY_CAST(SLHC_IND AS INTEGER),
            TRY_CAST(BROAD_REG_CD AS INTEGER),
            TRY_CAST(INSUR_PRI_CD AS INTEGER),
            TRY_CAST(MBR_FRS_IND AS INTEGER),
            TRY_CAST(MBR_FHLBS_IND AS INTEGER),
            TRY_CAST(SEC_RPTG_STATUS AS INTEGER),
            TRY_CAST(BANK_CNT AS INTEGER),
            'CLOSED'
        FROM raw_closed
        WHERE "{rssd_col_c}" IS NOT NULL
    """)
    n_closed_attrs = con.execute("SELECT COUNT(*) FROM institution_attributes WHERE source='CLOSED'").fetchone()[0]
    print(f"  Closed attribute records: {n_closed_attrs:,}")
    con.execute("DROP TABLE IF EXISTS raw_closed")

    # --- 3. BRANCHES ---
    branches_path = ATTRS_DIR / "CSV_ATTRIBUTES_BRANCHES" / "CSV_ATTRIBUTES_BRANCHES.CSV"
    print(f"\n3. Loading Branches from {branches_path.name}...")

    # Drop and recreate branches with simpler approach
    con.execute("DROP TABLE IF EXISTS branches")
    con.execute(f"""
        CREATE TABLE branches AS
        SELECT
            CAST("{rssd_col}" AS INTEGER) as rssd_id,
            TRY_CAST(ID_RSSD_HD_OFF AS INTEGER) as head_office_rssd,
            CAST(D_DT_START AS VARCHAR) as dt_start,
            CAST(D_DT_END AS VARCHAR) as dt_end,
            TRIM(NM_LGL) as branch_name,
            TRIM(CITY) as city,
            TRIM(STATE_ABBR_NM) as state_code,
            TRIM(CNTRY_NM) as country,
            TRIM(ENTITY_TYPE) as entity_type
        FROM read_csv('{str(branches_path).replace(chr(92), "/")}',
            header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
    """)
    n_branches = con.execute("SELECT COUNT(*) FROM branches").fetchone()[0]
    print(f"  Branches: {n_branches:,}")

    # --- 4. RELATIONSHIPS ---
    rel_path = ATTRS_DIR / "CSV_RELATIONSHIPS" / "CSV_RELATIONSHIPS.CSV"
    print(f"\n4. Loading Relationships from {rel_path.name}...")

    con.execute("DELETE FROM relationships")
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE raw_rels AS
        SELECT * FROM read_csv('{str(rel_path).replace(chr(92), "/")}',
            header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
    """)
    cols_rel = [desc[0] for desc in con.execute("SELECT * FROM raw_rels LIMIT 0").description]
    parent_col = next((c for c in cols_rel if 'PARENT' in c.upper()), cols_rel[0])
    offspring_col = next((c for c in cols_rel if 'OFFSPRING' in c.upper()), cols_rel[1])

    # Drop and recreate without PK constraint (some dates are NULL)
    con.execute("DROP TABLE IF EXISTS relationships")
    con.execute("""
        CREATE TABLE relationships (
            rssd_parent     INTEGER,
            rssd_offspring  INTEGER,
            dt_start        DATE,
            dt_end          DATE,
            relationship_level INTEGER,
            control_ind     INTEGER,
            equity_ind      INTEGER,
            pct_equity      DOUBLE,
            pct_other       DOUBLE
        )
    """)
    con.execute(f"""
        INSERT INTO relationships
        (rssd_parent, rssd_offspring, dt_start, dt_end,
         relationship_level, control_ind, equity_ind, pct_equity, pct_other)
        SELECT
            CAST("{parent_col}" AS INTEGER),
            CAST("{offspring_col}" AS INTEGER),
            TRY_CAST(D_DT_START AS DATE),
            TRY_CAST(D_DT_END AS DATE),
            TRY_CAST(RELN_LVL AS INTEGER),
            TRY_CAST(CTRL_IND AS INTEGER),
            TRY_CAST(EQUITY_IND AS INTEGER),
            TRY_CAST(PCT_EQUITY AS DOUBLE),
            TRY_CAST(PCT_OTHER AS DOUBLE)
        FROM raw_rels
        WHERE "{parent_col}" IS NOT NULL AND "{offspring_col}" IS NOT NULL
    """)
    n_rels = con.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    print(f"  Relationships: {n_rels:,}")
    con.execute("DROP TABLE IF EXISTS raw_rels")

    # --- 5. TRANSFORMATIONS ---
    trans_path = ATTRS_DIR / "CSV_TRANSFORMATIONS" / "CSV_TRANSFORMATIONS.CSV"
    print(f"\n5. Loading Transformations from {trans_path.name}...")

    con.execute("DROP TABLE IF EXISTS transformations")
    con.execute("""
        CREATE TABLE transformations (
            rssd_predecessor INTEGER,
            rssd_successor   INTEGER,
            dt_trans         DATE,
            transform_code   INTEGER,
            acct_method      INTEGER
        )
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE raw_trans AS
        SELECT * FROM read_csv('{str(trans_path).replace(chr(92), "/")}',
            header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
    """)
    cols_trans = [desc[0] for desc in con.execute("SELECT * FROM raw_trans LIMIT 0").description]
    pred_col = next((c for c in cols_trans if 'PREDECESSOR' in c.upper()), cols_trans[0])
    succ_col = next((c for c in cols_trans if 'SUCCESSOR' in c.upper()), cols_trans[1])

    con.execute(f"""
        INSERT INTO transformations
        (rssd_predecessor, rssd_successor, dt_trans, transform_code, acct_method)
        SELECT
            CAST("{pred_col}" AS INTEGER),
            CAST("{succ_col}" AS INTEGER),
            TRY_CAST(D_DT_TRANS AS DATE),
            TRY_CAST(TRNSFM_CD AS INTEGER),
            TRY_CAST(ACCT_METHOD AS INTEGER)
        FROM raw_trans
        WHERE "{pred_col}" IS NOT NULL AND "{succ_col}" IS NOT NULL
    """)
    n_trans = con.execute("SELECT COUNT(*) FROM transformations").fetchone()[0]
    print(f"  Transformations: {n_trans:,}")
    con.execute("DROP TABLE IF EXISTS raw_trans")

    # --- SUMMARY ---
    print("\n--- Summary ---")
    for table in ['institutions', 'institution_attributes', 'branches', 'relationships', 'transformations']:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count:,} rows")

    print("\nEntity types (top 10):")
    types = con.execute("""
        SELECT entity_type, COUNT(*) as cnt, SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
        FROM institutions
        GROUP BY entity_type
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()
    for t, c, a in types:
        print(f"  {t}: {c:,} ({a:,} active)")

    print("\nRelationship types:")
    rel_types = con.execute("""
        SELECT control_ind, COUNT(*) as cnt
        FROM relationships
        GROUP BY control_ind
        ORDER BY cnt DESC
    """).fetchall()
    for ci, c in rel_types:
        label = {0: 'No control', 1: 'Controlling', 2: 'Minority'}.get(ci, f'Code {ci}')
        print(f"  {label}: {c:,}")

    secs = elapsed()
    log_ingestion("2", f"Entities: {n_active:,} active + {n_closed:,} closed institutions, {n_branches:,} branches, {n_rels:,} relationships, {n_trans:,} transformations. {secs:.1f}s")

    con.close()
    print(f"\nPhase 2 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
