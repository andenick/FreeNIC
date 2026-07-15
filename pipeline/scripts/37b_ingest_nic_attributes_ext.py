"""Phase 37b: NIC attribute EXTENSION (geography + charter/reg codes + status/type).

Companion to 37 (identifiers). The NIC attribute CSVs carry 74 columns; 02 loaded ~13
and 37 captured the identifier crosswalk. This script captures the remaining high-value
Fed-direct attributes into a NEW additive table `nic_attributes_ext` (does NOT alter
institutions/institution_attributes, so the gate is unaffected). One row per RSSD,
ACTIVE preferred over CLOSED. Idempotent (CREATE OR REPLACE).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

ATTRS_DIR = INPUT_PATHS['attributes']
ACTIVE = (ATTRS_DIR / "CSV_ATTRIBUTES_ACTIVE" / "CSV_ATTRIBUTES_ACTIVE.CSV").as_posix()
CLOSED = (ATTRS_DIR / "CSV_ATTRIBUTES_CLOSED" / "CSV_ATTRIBUTES_CLOSED.CSV").as_posix()

# (output_col, source_col, cast)  cast in {'s','i'} (string / integer)
COLS = [
    ("street_line1", "STREET_LINE1", "s"), ("street_line2", "STREET_LINE2", "s"),
    ("zip_cd", "ZIP_CD", "s"), ("county_cd", "COUNTY_CD", "s"), ("place_cd", "PLACE_CD", "s"),
    ("state_home_cd", "STATE_HOME_CD", "s"), ("url", "URL", "s"),
    ("chtr_auth_cd", "CHTR_AUTH_CD", "i"), ("chtr_type_cd", "CHTR_TYPE_CD", "i"),
    ("func_reg", "FUNC_REG", "s"), ("prim_fed_reg", "PRIM_FED_REG", "s"),
    ("broad_reg_cd", "BROAD_REG_CD", "i"), ("dist_frs", "DIST_FRS", "i"),
    ("auth_reg_dist_frs", "AUTH_REG_DIST_FRS", "i"),
    ("state_inc_cd", "STATE_INC_CD", "s"), ("state_inc_abbr", "STATE_INC_ABBR_NM", "s"),
    ("cntry_inc_cd", "CNTRY_INC_CD", "s"),
    ("act_prim_cd", "ACT_PRIM_CD", "s"), ("est_type_cd", "EST_TYPE_CD", "i"),
    ("bnk_type_analys_cd", "BNK_TYPE_ANALYS_CD", "i"), ("org_type_cd", "ORG_TYPE_CD", "i"),
    ("reason_term_cd", "REASON_TERM_CD", "i"), ("mjr_own_mnrty", "MJR_OWN_MNRTY", "i"),
    ("cnsrvtr_cd", "CNSRVTR_CD", "i"), ("ihc_ind", "IHC_IND", "i"),
    ("fbo_4c9_ind", "FBO_4C9_IND", "i"), ("fncl_sub_ind", "FNCL_SUB_IND", "i"),
    ("ibf_ind", "IBF_IND", "i"), ("domestic_ind", "DOMESTIC_IND", "i"),
    ("slhc_type_ind", "SLHC_TYPE_IND", "i"), ("fisc_yrend_mmdd", "FISC_YREND_MMDD", "s"),
    ("dt_open", "DT_OPEN", "s"), ("dt_insur", "DT_INSUR", "s"),
]


def _expr(out, src, cast):
    # integer code/indicator cols: 0 is a valid category -> keep. string cols: NIC uses
    # both '' and '0' as missing-sentinels -> NULL both (no real url/zip/date/code is '0').
    if cast == "i":
        return f"TRY_CAST(NULLIF(TRIM(CAST({src} AS VARCHAR)),'') AS INTEGER) AS {out}"
    return f"NULLIF(NULLIF(TRIM(CAST({src} AS VARCHAR)),''),'0') AS {out}"


def _select(csv_path, status):
    sel = ",\n            ".join(_expr(o, s, c) for o, s, c in COLS)
    return f"""
        SELECT TRY_CAST("#ID_RSSD" AS INTEGER) AS rssd_id,
            {sel},
            '{status}' AS status
        FROM read_csv('{csv_path}', header=true, auto_detect=true, sample_size=5000, ignore_errors=true)
        WHERE TRY_CAST("#ID_RSSD" AS INTEGER) IS NOT NULL
    """


def main():
    elapsed = timer()
    print("=== Phase 37b: NIC attribute extension (geography + charter/reg + status) ===")
    con = get_db()
    con.execute("DROP TABLE IF EXISTS nic_attributes_ext")
    con.execute(f"""
        CREATE TABLE nic_attributes_ext AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY rssd_id
                ORDER BY CASE WHEN status='ACTIVE' THEN 0 ELSE 1 END) AS rn
            FROM (
                {_select(ACTIVE, 'ACTIVE')}
                UNION ALL
                {_select(CLOSED, 'CLOSED')}
            )
        ) WHERE rn = 1
    """)
    con.execute("CHECKPOINT")
    n = con.execute("SELECT COUNT(*) FROM nic_attributes_ext").fetchone()[0]
    cov = {c: con.execute(f"SELECT COUNT(*) FROM nic_attributes_ext WHERE {c} IS NOT NULL").fetchone()[0]
           for c in ['zip_cd', 'prim_fed_reg', 'chtr_type_cd', 'url', 'dt_open', 'state_inc_cd']}
    print(f"  nic_attributes_ext: {n:,} rows ({len(COLS)} attribute cols)")
    for k, v in cov.items():
        print(f"    {k}: {v:,}")
    out = (OUTPUTS_DIR / "parquet" / "nic_attributes_ext.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM nic_attributes_ext ORDER BY rssd_id) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  parquet={pq:,} parity={'OK' if pq == n else 'MISMATCH'}")
    con.close()
    log_ingestion("37b", f"NIC attribute extension: {n:,} rows, {len(COLS)} Fed-direct attribute cols "
                  f"(geography + charter/reg + status/type). {elapsed():.1f}s")
    print(f"\nPhase 37b complete in {elapsed():.1f}s.")


if __name__ == "__main__":
    main()
