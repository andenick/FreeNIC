"""Phase 37: NIC entity identifiers (authoritative Fed multi-regulator crosswalk).

The NIC attribute CSVs carry 74 columns; the original 02_ingest_attributes.py loaded
only a simplified subset and dropped the identifier crosswalk. This script harvests
the authoritative Fed identifiers per RSSD into a new canonical table:

  nic_entity_identifiers(rssd_id, id_lei, id_cusip, id_thrift, id_thrift_hc,
                         id_aba_prim, id_fdic_cert, id_ncua, id_occ, id_tax,
                         id_rssd_hd_off, status)

These are Fed-direct (T1) — far better than name-matching. id_crosswalk (36) is then
rebuilt to PREFER these authoritative IDs. One row per RSSD that carries >=1 external
identifier; ACTIVE preferred over CLOSED on conflict. Idempotent (CREATE OR REPLACE).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

ATTRS_DIR = INPUT_PATHS['attributes']
ACTIVE = (ATTRS_DIR / "CSV_ATTRIBUTES_ACTIVE" / "CSV_ATTRIBUTES_ACTIVE.CSV").as_posix()
CLOSED = (ATTRS_DIR / "CSV_ATTRIBUTES_CLOSED" / "CSV_ATTRIBUTES_CLOSED.CSV").as_posix()

# normalize a NIC id cell: blank or '0' -> NULL (these are "no identifier" sentinels)
def _norm(col):
    return f"NULLIF(NULLIF(TRIM(CAST({col} AS VARCHAR)),''),'0')"


def _select(csv_path, status):
    rssd = '"#ID_RSSD"'  # NIC CSVs prefix the first column with '#'
    return f"""
        SELECT
            TRY_CAST({rssd} AS INTEGER)        AS rssd_id,
            {_norm('ID_LEI')}                  AS id_lei,
            {_norm('ID_CUSIP')}                AS id_cusip,
            {_norm('ID_THRIFT')}               AS id_thrift,
            {_norm('ID_THRIFT_HC')}            AS id_thrift_hc,
            {_norm('ID_ABA_PRIM')}             AS id_aba_prim,
            TRY_CAST({_norm('ID_FDIC_CERT')} AS INTEGER) AS id_fdic_cert,
            {_norm('ID_NCUA')}                 AS id_ncua,
            {_norm('ID_OCC')}                  AS id_occ,
            {_norm('ID_TAX')}                  AS id_tax,
            TRY_CAST({_norm('ID_RSSD_HD_OFF')} AS INTEGER) AS id_rssd_hd_off,
            '{status}'                         AS status
        FROM read_csv('{csv_path}', header=true, auto_detect=true,
                      sample_size=5000, ignore_errors=true)
        WHERE TRY_CAST({rssd} AS INTEGER) IS NOT NULL
    """


def main():
    elapsed = timer()
    print("=== Phase 37: NIC entity identifiers (authoritative Fed crosswalk) ===")
    con = get_db()

    con.execute("DROP TABLE IF EXISTS nic_entity_identifiers")
    con.execute(f"""
        CREATE TABLE nic_entity_identifiers AS
        WITH unioned AS (
            {_select(ACTIVE, 'ACTIVE')}
            UNION ALL
            {_select(CLOSED, 'CLOSED')}
        ),
        -- keep only rows carrying >=1 external identifier
        filtered AS (
            SELECT * FROM unioned
            WHERE COALESCE(id_lei,id_cusip,id_thrift,id_thrift_hc,id_aba_prim,
                           id_ncua,id_occ,id_tax) IS NOT NULL
               OR id_fdic_cert IS NOT NULL
        )
        -- one row per rssd; ACTIVE wins over CLOSED, then most-populated
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY rssd_id
                ORDER BY CASE WHEN status='ACTIVE' THEN 0 ELSE 1 END,
                         (CASE WHEN id_lei IS NOT NULL THEN 1 ELSE 0 END
                          + CASE WHEN id_fdic_cert IS NOT NULL THEN 1 ELSE 0 END
                          + CASE WHEN id_occ IS NOT NULL THEN 1 ELSE 0 END
                          + CASE WHEN id_ncua IS NOT NULL THEN 1 ELSE 0 END) DESC
            ) AS rn FROM filtered
        ) WHERE rn = 1
    """)
    con.execute("CHECKPOINT")

    n = con.execute("SELECT COUNT(*) FROM nic_entity_identifiers").fetchone()[0]
    cov = {c: con.execute(f"SELECT COUNT(*) FROM nic_entity_identifiers WHERE {c} IS NOT NULL").fetchone()[0]
           for c in ['id_lei', 'id_fdic_cert', 'id_occ', 'id_ncua', 'id_thrift', 'id_cusip', 'id_aba_prim', 'id_tax']}
    print(f"  nic_entity_identifiers: {n:,} rows (one per RSSD with >=1 external id)")
    for k, v in cov.items():
        print(f"    {k}: {v:,}")

    # export parquet
    out = (OUTPUTS_DIR / "parquet" / "nic_entity_identifiers.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM nic_entity_identifiers ORDER BY rssd_id) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  parquet={pq:,} parity={'OK' if pq == n else 'MISMATCH'}")
    con.close()

    log_ingestion("37", f"NIC entity identifiers (authoritative Fed crosswalk): {n:,} rows; "
                  f"lei={cov['id_lei']:,} occ={cov['id_occ']:,} ncua={cov['id_ncua']:,} "
                  f"cert={cov['id_fdic_cert']:,}. {elapsed():.1f}s")
    print(f"\nPhase 37 complete in {elapsed():.1f}s.")


if __name__ == "__main__":
    main()
