"""Phase 44: Variable-dictionary completeness for non-MDRM code namespaces (Q3, Definitive Build).

catalog.variables (built by 10_build_catalog) covers only MDRM codes observed in call/bhcf filings.
Three fact-table namespaces use their own codes and were undescribed ("orphans"):
  - UBPR  (ubpr_ratios.ubpr_code)            -> described from the mdrm table (mnemonic||item_code)
  - RISK  (y15_systemic_indicators.risk_code) -> described from the mdrm table
  - FS220 (ncua_5300.account_code)            -> described from NCUA AcctDesc.txt (inside the bulk zip)

This builds a SEPARATE, idempotent table catalog.namespace_variables (CREATE OR REPLACE) so a future
10_build_catalog rebuild (which DELETEs catalog.variables) cannot wipe it. EVERY distinct fact-table code
is registered (LEFT JOIN to its description source); description is filled where a real source row exists
and left NULL otherwise (NO fabricated descriptions). Description-coverage % is reported.

Run AFTER 10_build_catalog. Idempotent. Read sources are on-disk (no network).
"""
import csv
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, INPUT_PATHS, timer, log_ingestion


def _load_ncua_acctdesc(con):
    """Union AcctDesc.txt across ALL NCUA bulk zips (account sets drift by quarter), keeping one
    description per account (prefer a non-null description), and register as a DuckDB temp table."""
    zips = sorted(Path(INPUT_PATHS["ncua"]).glob("**/*.zip"))
    con.execute("CREATE OR REPLACE TEMP TABLE acctdesc(account VARCHAR, acctname VARCHAR, acctdesc VARCHAR, tablename VARCHAR)")
    if not zips:
        print("    no NCUA zip found -> FS220 descriptions unavailable")
        return
    best = {}  # account -> (name, desc, table); prefer rows with a non-null desc
    for zp in zips:
        try:
            with zipfile.ZipFile(zp) as z:
                if "AcctDesc.txt" not in z.namelist():
                    continue
                raw = z.read("AcctDesc.txt").decode("latin-1", "replace")
        except Exception:
            continue
        for r in csv.DictReader(io.StringIO(raw)):
            acct = str(r.get("Account", "")).upper()
            if not acct:
                continue
            desc = r.get("AcctDesc")
            cur = best.get(acct)
            if cur is None or (not cur[1] and desc):
                best[acct] = (r.get("AcctName"), desc, r.get("TableName"))
    rows = [(a, v[0], v[1], v[2]) for a, v in best.items()]
    con.executemany("INSERT INTO acctdesc VALUES (?,?,?,?)", rows)
    print(f"    loaded {len(rows):,} unique NCUA AcctDesc rows from {len(zips)} zips")


def build_namespace_variables(con):
    print("\n  Building catalog.namespace_variables (UBPR / RISK / FS220)...")
    con.execute("""
        CREATE OR REPLACE TABLE catalog.namespace_variables (
            variable_id   VARCHAR,
            namespace     VARCHAR,
            canonical_name VARCHAR,
            description   VARCHAR,
            schedule      VARCHAR,
            source        VARCHAR
        )
    """)

    # --- UBPR + RISK from the mdrm table (mnemonic||item_code), one row per code ---
    for ns, table, col in [("UBPR", "ubpr_ratios", "ubpr_code"),
                           ("RISK", "y15_systemic_indicators", "risk_code")]:
        con.execute(f"""
            INSERT INTO catalog.namespace_variables
            WITH codes AS (SELECT DISTINCT {col} AS code FROM {table}),
                 md AS (
                     SELECT code, item_name, description, mnemonic
                     FROM (
                         SELECT c.code, m.item_name, m.description, m.mnemonic,
                                ROW_NUMBER() OVER (PARTITION BY c.code
                                    ORDER BY (m.item_name IS NULL), (m.description IS NULL),
                                             m.end_date DESC NULLS LAST) rn
                         FROM codes c
                         LEFT JOIN mdrm m ON c.code = m.mnemonic || m.item_code
                     ) WHERE rn = 1
                 )
            SELECT code, '{ns}', item_name, description, mnemonic, 'mdrm'
            FROM md
        """)
        n = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables WHERE namespace=?", [ns]).fetchone()[0]
        desc = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables WHERE namespace=? AND description IS NOT NULL", [ns]).fetchone()[0]
        print(f"    {ns}: {n:,} codes registered, {desc:,} described ({desc/n*100:.1f}%)" if n else f"    {ns}: 0 codes")

    # --- FS220 from NCUA AcctDesc ---
    _load_ncua_acctdesc(con)
    con.execute("""
        INSERT INTO catalog.namespace_variables
        WITH codes AS (SELECT DISTINCT account_code AS code FROM ncua_5300)
        SELECT c.code, 'FS220', a.acctname, a.acctdesc, a.tablename, 'ncua_acctdesc'
        FROM codes c LEFT JOIN acctdesc a ON c.code = a.account
    """)
    n = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables WHERE namespace='FS220'").fetchone()[0]
    desc = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables WHERE namespace='FS220' AND description IS NOT NULL").fetchone()[0]
    print(f"    FS220: {n:,} codes registered, {desc:,} described ({desc/n*100:.1f}%)" if n else "    FS220: 0 codes")

    total = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables").fetchone()[0]
    tdesc = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables WHERE description IS NOT NULL").fetchone()[0]
    print(f"    TOTAL: {total:,} namespace codes registered, {tdesc:,} described ({tdesc/total*100:.1f}%)")


def export_parquet(con):
    """Self-export the parquet (12_export skip-if-current can miss a CREATE OR REPLACE rebuild)."""
    from utils import OUTPUTS_DIR
    out = (OUTPUTS_DIR / "parquet" / "catalog_namespace_variables.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM catalog.namespace_variables ORDER BY namespace, variable_id) "
                f"TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    db = con.execute("SELECT COUNT(*) FROM catalog.namespace_variables").fetchone()[0]
    pq = con.execute("SELECT COUNT(*) FROM read_parquet(?)", [out]).fetchone()[0]
    print(f"    catalog_namespace_variables.parquet: db={db:,} parquet={pq:,} "
          f"parity={'OK' if db == pq else 'MISMATCH'}")


def main():
    elapsed = timer()
    print("=== Phase 44: Variable Dictionary (namespace codes) ===")
    con = get_db()
    build_namespace_variables(con)
    export_parquet(con)
    con.close()
    secs = elapsed()
    log_ingestion("44", f"Built catalog.namespace_variables. {secs:.1f}s")
    print(f"\nPhase 44 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
