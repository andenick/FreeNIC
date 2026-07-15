"""Phase 29: Ingest bank-identifier catalog data (crosswalk, hierarchy, sectors).

Source: place the catalog CSVs under Inputs/catalogs/ (bundled) or
$DATA_ROOT/catalogs/ (external source root; see README "## Setup" and
data/MANIFEST.md). Required files:
- bank_identifier_crosswalk.csv: 14,287 bank_id↔RSSD↔FDIC cert mappings
- bhc_hierarchy.csv: 36,668 BHC parent-child relationships with ownership %
- sector_groupings.csv: 16,548 CIK→SIC→sector classifications
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUTS_DIR, DATA_ROOT

_BUNDLED = INPUTS_DIR / "catalogs"
CATALOGS = _BUNDLED if _BUNDLED.exists() else DATA_ROOT / "catalogs"


def ingest_crosswalk(con):
    """Ingest the bank-identifier crosswalk (Failing Banks bank_id ↔ FFIEC RSSD ↔ FDIC cert)."""
    csv_path = str(CATALOGS / "bank_identifier_crosswalk.csv").replace("\\", "/")

    con.execute("DROP TABLE IF EXISTS robin_crosswalk")
    con.execute(f"""
        CREATE TABLE robin_crosswalk AS
        SELECT
            CAST(bank_id_robin AS INTEGER) AS bank_id_robin,
            CAST(charter_robin AS INTEGER) AS charter_robin,
            CAST(rssd_id AS INTEGER) AS rssd_id,
            CAST(fdic_cert AS INTEGER) AS fdic_cert,
            canonical_name_robin,
            name_ffiec,
            city_robin,
            city_ffiec,
            state_abbrev,
            match_method,
            CAST(match_confidence AS DOUBLE) AS match_confidence,
            CAST(robin_year_min AS INTEGER) AS robin_year_min,
            CAST(robin_year_max AS INTEGER) AS robin_year_max,
            CAST(ffiec_year_start AS INTEGER) AS ffiec_year_start,
            CAST(ffiec_year_end AS INTEGER) AS ffiec_year_end,
            entity_type,
            CAST(is_bhc AS BOOLEAN) AS is_bhc,
            CAST(failed AS INTEGER) AS failed,
            CAST(rssd_id_bhc AS INTEGER) AS rssd_id_bhc
        FROM read_csv_auto('{csv_path}', header=true)
    """)

    count = con.execute("SELECT COUNT(*) FROM robin_crosswalk").fetchone()[0]
    matched = con.execute("""
        SELECT COUNT(*) FROM robin_crosswalk xw
        JOIN institutions i ON xw.rssd_id = i.rssd_id
    """).fetchone()[0]
    print(f"  robin_crosswalk: {count:,} rows ({matched:,} matched to institutions)")
    return count


def ingest_hierarchy(con):
    """Ingest BHC hierarchy with ownership percentages."""
    csv_path = str(CATALOGS / "bhc_hierarchy.csv").replace("\\", "/")

    con.execute("DROP TABLE IF EXISTS bhc_ownership")
    con.execute(f"""
        CREATE TABLE bhc_ownership AS
        SELECT
            CAST(rssd_id_bhc AS INTEGER) AS rssd_id_bhc,
            CAST(rssd_id_bank AS INTEGER) AS rssd_id_bank,
            CAST(fdic_cert AS INTEGER) AS fdic_cert,
            CAST(hierarchy_level AS INTEGER) AS hierarchy_level,
            relationship_type,
            CAST(pct_equity AS DOUBLE) AS pct_equity,
            nm_lgl,
            nm_short,
            city,
            state_abbr,
            entity_type,
            CAST(is_bhc AS BOOLEAN) AS is_bhc,
            CAST(is_primary_bank AS BOOLEAN) AS is_primary_bank,
            status
        FROM read_csv_auto('{csv_path}', header=true)
    """)

    count = con.execute("SELECT COUNT(*) FROM bhc_ownership").fetchone()[0]
    active = con.execute("SELECT COUNT(*) FROM bhc_ownership WHERE status != 'CLOSED'").fetchone()[0]
    print(f"  bhc_ownership: {count:,} rows ({active:,} active)")
    return count


def ingest_sectors(con):
    """Ingest sector/SIC groupings."""
    csv_path = str(CATALOGS / "sector_groupings.csv").replace("\\", "/")

    con.execute("DROP TABLE IF EXISTS sector_groupings")
    con.execute(f"""
        CREATE TABLE sector_groupings AS
        SELECT
            cik,
            ticker,
            company_name,
            sic_code,
            sector_group
        FROM read_csv_auto('{csv_path}', header=true)
    """)

    count = con.execute("SELECT COUNT(*) FROM sector_groupings").fetchone()[0]
    banking = con.execute("""
        SELECT COUNT(*) FROM sector_groupings
        WHERE sector_group LIKE '%Bank%' OR CAST(sic_code AS VARCHAR) LIKE '60%'
    """).fetchone()[0]
    print(f"  sector_groupings: {count:,} rows ({banking:,} banking-related)")
    return count


def main():
    elapsed = timer()
    print("=== Phase 29: Bank-Identifier Catalogs ===\n")

    con = get_db()

    xw_count = ingest_crosswalk(con)
    hier_count = ingest_hierarchy(con)
    sec_count = ingest_sectors(con)

    con.close()

    total = xw_count + hier_count + sec_count
    secs = elapsed()
    print(f"\n  Total: {total:,} rows across 3 tables")
    log_ingestion("29", f"Catalogs: crosswalk={xw_count:,}, hierarchy={hier_count:,}, sectors={sec_count:,}. {secs:.1f}s")
    print(f"\nPhase 29 complete in {secs:.1f}s")


if __name__ == "__main__":
    main()
