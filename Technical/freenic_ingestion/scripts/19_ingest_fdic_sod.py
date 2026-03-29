"""Phase 19: Ingest FDIC Summary of Deposits (SOD) into freenic.

Source: Inputs/fdic_sod/ (paginated JSON from Phase 18 download)
Target: fdic_sod table (branch-level deposit data, 1994-present)

Uses DuckDB native JSON reader for fast bulk loading.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

CACHE_DIR = INPUT_PATHS['fdic_sod']


def main():
    elapsed = timer()
    print("=== Phase 19: FDIC Summary of Deposits Ingestion ===\n")

    # Check cache
    if not CACHE_DIR.exists() or not (CACHE_DIR / "_DOWNLOAD_COMPLETE").exists():
        print("  ERROR: Download not complete. Run Phase 18 first.")
        return

    # Combine JSON pages into single file
    combined_path = CACHE_DIR / "combined.json"
    if not combined_path.exists():
        print("  Combining JSON pages...")
        all_records = []
        for p in sorted(CACHE_DIR.glob("page_*.json")):
            with open(p) as f:
                all_records.extend(json.load(f))
        print(f"    Loaded {len(all_records):,} records from "
              f"{len(list(CACHE_DIR.glob('page_*.json')))} pages")

        with open(combined_path, "w") as f:
            json.dump(all_records, f)
        print(f"    Written to {combined_path.name} "
              f"({combined_path.stat().st_size / (1024**2):.0f} MB)")
    else:
        print(f"  Using existing combined.json "
              f"({combined_path.stat().st_size / (1024**2):.0f} MB)")

    con = get_db()

    # Drop and recreate
    con.execute("DROP TABLE IF EXISTS fdic_sod")
    con.execute("""
        CREATE TABLE fdic_sod (
            fdic_cert       INTEGER,
            rssd_id         INTEGER,
            year            INTEGER,
            branch_num      INTEGER,
            uninumbr        INTEGER,
            branch_name     VARCHAR,
            address         VARCHAR,
            city            VARCHAR,
            state_code      VARCHAR,
            state_name      VARCHAR,
            zip_code        VARCHAR,
            county          VARCHAR,
            county_num      INTEGER,
            latitude        DOUBLE,
            longitude       DOUBLE,
            branch_deposits DOUBLE,
            inst_deposits   DOUBLE,
            domestic_deposits DOUBLE,
            total_assets    DOUBLE,
            hc_name         VARCHAR,
            hc_rssd_id      INTEGER,
            bank_class      VARCHAR,
            charter_type    VARCHAR,
            regulator       VARCHAR,
            source          VARCHAR DEFAULT 'fdic_sod'
        )
    """)

    # Load JSON into DuckDB
    json_path = str(combined_path).replace("\\", "/")
    print("  Loading JSON into DuckDB...")
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE sod_raw AS
        SELECT * FROM read_json('{json_path}',
            auto_detect=true,
            format='array',
            maximum_object_size=2000000000
        )
    """)

    raw_count = con.execute("SELECT COUNT(*) FROM sod_raw").fetchone()[0]
    raw_cols = [r[0] for r in con.execute("DESCRIBE sod_raw").fetchall()]
    print(f"    Loaded {raw_count:,} rows, {len(raw_cols)} columns")

    # Insert with field mapping
    con.execute("""
        INSERT INTO fdic_sod (
            fdic_cert, rssd_id, year, branch_num, uninumbr,
            branch_name, address, city, state_code, state_name,
            zip_code, county, county_num,
            latitude, longitude,
            branch_deposits, inst_deposits, domestic_deposits, total_assets,
            hc_name, hc_rssd_id, bank_class, charter_type, regulator, source
        )
        SELECT
            TRY_CAST("CERT" AS INTEGER),
            TRY_CAST("RSSDID" AS INTEGER),
            TRY_CAST("YEAR" AS INTEGER),
            TRY_CAST("BRNUM" AS INTEGER),
            TRY_CAST("UNINUMBR" AS INTEGER),
            "NAMEBR",
            "ADDRESS",
            "CITY2BR",
            "STALPBR",
            "STNAMEBR",
            "ZIPBR",
            "CNTYNAMB",
            TRY_CAST("CNTYNUMB" AS INTEGER),
            TRY_CAST("SIMS_LATITUDE" AS DOUBLE),
            TRY_CAST("SIMS_LONGITUDE" AS DOUBLE),
            TRY_CAST("DEPSUMBR" AS DOUBLE),
            TRY_CAST("DEPSUM" AS DOUBLE),
            TRY_CAST("DEPDOM" AS DOUBLE),
            TRY_CAST("ASSET" AS DOUBLE),
            "NAMEHCR",
            TRY_CAST("RSSDHCR" AS INTEGER),
            "BKCLASS",
            "CHARTER",
            "REGAGNT",
            'fdic_sod'
        FROM sod_raw
    """)

    # Summary
    count = con.execute("SELECT COUNT(*) FROM fdic_sod").fetchone()[0]
    years = con.execute("SELECT MIN(year), MAX(year) FROM fdic_sod").fetchone()
    branches = con.execute("SELECT COUNT(DISTINCT fdic_cert || '-' || COALESCE(CAST(branch_num AS VARCHAR), '0')) FROM fdic_sod").fetchone()[0]
    institutions = con.execute("SELECT COUNT(DISTINCT fdic_cert) FROM fdic_sod").fetchone()[0]
    year_count = con.execute("SELECT COUNT(DISTINCT year) FROM fdic_sod").fetchone()[0]

    # Cross-reference with institutions table
    matched = con.execute("""
        SELECT COUNT(DISTINCT f.rssd_id) FROM fdic_sod f
        WHERE f.rssd_id IS NOT NULL
          AND EXISTS (SELECT 1 FROM institutions i WHERE i.rssd_id = f.rssd_id)
    """).fetchone()[0]
    total_rssd = con.execute("""
        SELECT COUNT(DISTINCT rssd_id) FROM fdic_sod WHERE rssd_id IS NOT NULL
    """).fetchone()[0]

    print(f"\n--- Summary ---")
    print(f"  Total records: {count:,}")
    print(f"  Institutions: {institutions:,}")
    print(f"  Unique branches: {branches:,}")
    print(f"  Years: {year_count} ({years[0]} to {years[1]})")
    if total_rssd:
        print(f"  RSSD match: {matched:,} / {total_rssd:,} ({matched/total_rssd*100:.1f}%)")

    con.close()

    secs = elapsed()
    log_ingestion("19", f"FDIC SOD: {count:,} records, {institutions:,} institutions, "
                  f"{year_count} years ({years[0]}-{years[1]}). {secs:.1f}s")
    print(f"\nPhase 19 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
