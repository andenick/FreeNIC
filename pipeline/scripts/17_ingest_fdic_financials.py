"""Phase 17: Ingest FDIC SDI Financials (1984Q1-2025Q4).

Source: FDIC BankFind API (api.fdic.gov/banks/financials)
Pre-downloaded to: Inputs/fdic_financials/ (168 JSON pages, 1.67M records)

Strategy: Concatenate cached JSON pages into one file, load via DuckDB
native JSON reader, then SQL UNPIVOT to long format. Much faster than
Python executemany.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

CACHE_DIR = INPUT_PATHS['fdic_financials']

# Variable columns to unpivot (numeric financial fields)
VAR_COLS = [
    "ASSET", "DEP", "EQ", "EQTOT", "LIAB", "LNLSNET", "SC",
    "CHBAL", "FREPO", "TRADE", "INTAN", "ORE", "NFAA", "AOA",
    "DEPDOM", "DEPFOR", "DEPINS", "DEPUNINS", "COREDEP",
    "NETINC", "INTINC", "EINTEXP", "NONII", "NONIX", "NOIJ", "PTAXNETINC",
    "ITAX", "ELNATR",
    "RBC1AAJ", "RBCRWAJ", "ROA", "ROE", "NIM", "NIMY", "ERNASTR",
    "EEFFR", "LNLSDEPR", "ROEINJR", "NETINBM", "ROAPTX",
    "P3ASSET", "P9ASSET", "P3LTOT", "P9LTOT", "LNRESNCR", "NTLNLS",
    "NCLNLSR", "LNATRESR",
    "NUMEMP", "OFFDOM", "OFFFOR", "BKPREM",
    "SZLNRES", "SZLNCI", "SZLNCON", "SZLNCRCD", "SZLNHEL", "SZLNAUTO", "SZLNOTH",
]


def main():
    elapsed = timer()
    print("=== Phase 17: FDIC SDI Financials Ingestion ===\n")

    # Check cache
    if not CACHE_DIR.exists() or not (CACHE_DIR / "_DOWNLOAD_COMPLETE").exists():
        print("  ERROR: Download not complete. Run download phase first.")
        return

    # Concatenate JSON pages into single NDJSON file
    combined_path = CACHE_DIR / "combined.json"
    if not combined_path.exists():
        print("  Combining JSON pages...")
        all_records = []
        for p in sorted(CACHE_DIR.glob("page_*.json")):
            with open(p) as f:
                all_records.extend(json.load(f))
        print(f"    Loaded {len(all_records):,} records from {len(list(CACHE_DIR.glob('page_*.json')))} pages")

        with open(combined_path, "w") as f:
            json.dump(all_records, f)
        print(f"    Written to {combined_path.name} ({combined_path.stat().st_size / (1024**2):.0f} MB)")
    else:
        print(f"  Using existing combined.json ({combined_path.stat().st_size / (1024**2):.0f} MB)")

    con = get_db()

    # Drop existing table
    con.execute("DROP TABLE IF EXISTS fdic_financials")

    # Load JSON into a wide temp table
    json_path = str(combined_path).replace("\\", "/")
    print("  Loading JSON into DuckDB...")
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE fdic_wide AS
        SELECT * FROM read_json('{json_path}',
            auto_detect=true,
            format='array',
            maximum_object_size=2000000000
        )
    """)
    wide_count = con.execute("SELECT COUNT(*) FROM fdic_wide").fetchone()[0]
    wide_cols = [r[0] for r in con.execute("DESCRIBE fdic_wide").fetchall()]
    print(f"    Loaded {wide_count:,} rows, {len(wide_cols)} columns")

    # Create target table
    con.execute("""
        CREATE TABLE fdic_financials (
            fdic_cert INTEGER,
            rssd_id INTEGER,
            period_end DATE,
            variable_id VARCHAR,
            value DOUBLE,
            source VARCHAR DEFAULT 'fdic_sdi'
        )
    """)

    # Determine which VAR_COLS actually exist in the data
    existing_vars = [v for v in VAR_COLS if v in wide_cols]
    print(f"  Variable columns found: {len(existing_vars)} of {len(VAR_COLS)}")

    # UNPIVOT in batches of 20 columns to avoid query complexity limits
    batch_size = 20
    total_inserted = 0

    for i in range(0, len(existing_vars), batch_size):
        batch = existing_vars[i:i + batch_size]

        selects = []
        for col in batch:
            selects.append(f"""
                SELECT
                    TRY_CAST("CERT" AS INTEGER) AS fdic_cert,
                    TRY_CAST("RSSDID" AS INTEGER) AS rssd_id,
                    MAKE_DATE(
                        CAST(LEFT(CAST("REPDTE" AS VARCHAR), 4) AS INTEGER),
                        CAST(SUBSTR(CAST("REPDTE" AS VARCHAR), 5, 2) AS INTEGER),
                        CAST(RIGHT(CAST("REPDTE" AS VARCHAR), 2) AS INTEGER)
                    ) AS period_end,
                    '{col}' AS variable_id,
                    TRY_CAST("{col}" AS DOUBLE) AS value,
                    'fdic_sdi' AS source
                FROM fdic_wide
                WHERE TRY_CAST("{col}" AS DOUBLE) IS NOT NULL
                  AND TRY_CAST("{col}" AS DOUBLE) != 0
            """)

        union_sql = "\nUNION ALL\n".join(selects)
        con.execute(f"INSERT INTO fdic_financials {union_sql}")

        batch_count = con.execute("SELECT COUNT(*) FROM fdic_financials").fetchone()[0]
        inserted = batch_count - total_inserted
        total_inserted = batch_count
        print(f"    Batch {i // batch_size + 1}: cols {i+1}-{min(i+batch_size, len(existing_vars))}, "
              f"+{inserted:,} obs (total: {total_inserted:,})")

    # Summary
    count = con.execute("SELECT COUNT(*) FROM fdic_financials").fetchone()[0]
    entities = con.execute("SELECT COUNT(DISTINCT fdic_cert) FROM fdic_financials").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM fdic_financials").fetchone()[0]
    date_range = con.execute("SELECT MIN(period_end), MAX(period_end) FROM fdic_financials").fetchone()
    quarters = con.execute("SELECT COUNT(DISTINCT period_end) FROM fdic_financials").fetchone()[0]

    matched = con.execute("""
        SELECT COUNT(DISTINCT f.rssd_id) FROM fdic_financials f
        WHERE f.rssd_id IS NOT NULL
          AND EXISTS (SELECT 1 FROM institutions i WHERE i.rssd_id = f.rssd_id)
    """).fetchone()[0]
    total_rssd = con.execute("""
        SELECT COUNT(DISTINCT rssd_id) FROM fdic_financials WHERE rssd_id IS NOT NULL
    """).fetchone()[0]

    print(f"\n--- Summary ---")
    print(f"  Total observations: {count:,}")
    print(f"  Institutions: {entities:,}")
    print(f"  Variables: {variables}")
    print(f"  Quarters: {quarters}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")
    if total_rssd:
        print(f"  RSSD match: {matched:,} / {total_rssd:,} ({matched/total_rssd*100:.1f}%)")

    con.close()

    secs = elapsed()
    log_ingestion("17", f"FDIC Financials: {count:,} obs, {entities:,} institutions, "
                  f"{variables} vars, {quarters} quarters, {date_range[0]} to {date_range[1]}. {secs:.1f}s")
    print(f"\nPhase 17 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
