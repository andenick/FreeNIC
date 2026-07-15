"""Phase 5: Ingest BHCF CSV files for pre-2000 data (1986Q3-1999Q4).

Sources: bhcf*.csv files in Inputs/2026.03.11 BHCF and MDRM Inputs/
Format: Comma-delimited CSV, lowercase column names, rssd9999=period, rssd9001=entity.
Naming: bhcfYYMM.csv where YY=year (86-99), MM=month (03,06,09,12).
Only ingest pre-2000 files — 2000+ already covered by Phase 4.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

BHCF_CSV_DIR = INPUT_PATHS['bhcf_csv']

# Same RSSD metadata exclusions
RSSD_PREFIXES = {'rssd', 'RSSD'}


def parse_period_from_csv_name(filename):
    """Parse period from bhcf8609.csv -> 1986-09-30, bhcf0003.csv -> 2000-03-31."""
    match = re.match(r'bhcf(\d{2})(\d{2})\.csv', filename, re.IGNORECASE)
    if not match:
        return None
    yy = int(match.group(1))
    mm = int(match.group(2))
    year = 1900 + yy if yy >= 86 else 2000 + yy

    # Last day of the month
    if mm == 3:
        day = 31
    elif mm == 6:
        day = 30
    elif mm == 9:
        day = 30
    elif mm == 12:
        day = 31
    else:
        day = 28
    return f"{year}-{mm:02d}-{day:02d}"


def is_pre_2000(filename):
    """Check if a BHCF CSV is pre-2000."""
    match = re.match(r'bhcf(\d{2})\d{2}\.csv', filename, re.IGNORECASE)
    if not match:
        return False
    yy = int(match.group(1))
    return yy >= 86  # 86-99 are 1986-1999


def ingest_one_csv(con, filepath):
    """Ingest a single BHCF CSV file using DuckDB native reader."""
    filename = filepath.name
    period_end = parse_period_from_csv_name(filename)
    if not period_end:
        return 0

    escaped_path = str(filepath).replace("\\", "/")

    try:
        # Read the CSV with DuckDB
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE bhcf_csv_raw AS
            SELECT * FROM read_csv('{escaped_path}',
                header=true, auto_detect=true, sample_size=-1,
                ignore_errors=true, all_varchar=true)
        """)
    except Exception as e:
        print(f"  ERROR reading {filename}: {e}")
        return 0

    # Get column names
    cols = [desc[0] for desc in con.execute("SELECT * FROM bhcf_csv_raw LIMIT 0").description]

    # Find RSSD ID column
    rssd_col = None
    for c in cols:
        if c.lower() == 'rssd9001':
            rssd_col = c
            break
    if not rssd_col:
        rssd_col = cols[1] if len(cols) > 1 else cols[0]

    # Variable columns (exclude rssd* and text*)
    var_cols = []
    for c in cols:
        lower = c.lower()
        if lower.startswith('rssd') or lower.startswith('text'):
            continue
        var_cols.append(c)

    # Unpivot in batches
    batch_size = 200
    for i in range(0, len(var_cols), batch_size):
        batch = var_cols[i:i + batch_size]

        selects = []
        for vc in batch:
            var_id = vc.upper()  # Normalize to uppercase
            selects.append(f"""
                SELECT
                    TRY_CAST("{rssd_col}" AS INTEGER) as rssd_id,
                    '{period_end}'::DATE as period_end,
                    '{var_id}' as variable_id,
                    TRY_CAST("{vc}" AS DOUBLE) as value,
                    '{filename}' as source_file
                FROM bhcf_csv_raw
                WHERE "{vc}" IS NOT NULL
                    AND TRIM("{vc}") != ''
                    AND TRY_CAST("{vc}" AS DOUBLE) IS NOT NULL
                    AND TRY_CAST("{rssd_col}" AS INTEGER) IS NOT NULL
            """)

        if selects:
            union_query = " UNION ALL ".join(selects)
            try:
                con.execute(f"""
                    INSERT INTO bhcf_filings (rssd_id, period_end, variable_id, value, source_file)
                    {union_query}
                """)
            except Exception as e:
                print(f"  ERROR in batch for {filename}: {e}")

    count = con.execute(f"""
        SELECT COUNT(*) FROM bhcf_filings
        WHERE period_end = '{period_end}' AND source_file = '{filename}'
    """).fetchone()[0]

    con.execute("DROP TABLE IF EXISTS bhcf_csv_raw")
    return count


def main():
    elapsed = timer()
    print("=== Phase 5: BHCF CSV Pre-2000 Ingestion ===")

    con = get_db()

    # Find pre-2000 CSV files only
    all_csvs = sorted(BHCF_CSV_DIR.glob("bhcf*.csv"))
    pre2000_csvs = [f for f in all_csvs if is_pre_2000(f.name)]
    print(f"Found {len(all_csvs)} total BHCF CSVs, {len(pre2000_csvs)} are pre-2000")

    total_rows = 0
    for i, filepath in enumerate(pre2000_csvs):
        period = parse_period_from_csv_name(filepath.name)
        count = ingest_one_csv(con, filepath)
        total_rows += count
        print(f"  [{i+1}/{len(pre2000_csvs)}] {filepath.name} ({period}): {count:,} obs (total: {total_rows:,})")

        # Record filing metadata
        if count > 0:
            entities = con.execute(f"""
                SELECT COUNT(DISTINCT rssd_id) FROM bhcf_filings
                WHERE period_end = '{period}' AND source_file = '{filepath.name}'
            """).fetchone()[0]
            variables = con.execute(f"""
                SELECT COUNT(DISTINCT variable_id) FROM bhcf_filings
                WHERE period_end = '{period}' AND source_file = '{filepath.name}'
            """).fetchone()[0]
            con.execute("""
                INSERT OR REPLACE INTO filing_metadata
                (filing_type, period_end, source_file, entity_count, variable_count, ingestion_ts)
                VALUES ('BHCF', ?, ?, ?, ?, ?)
            """, (period, filepath.name, entities, variables, datetime.now()))

    # Summary
    print(f"\n--- Summary ---")
    total = con.execute("SELECT COUNT(*) FROM bhcf_filings").fetchone()[0]
    entities = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM bhcf_filings").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM bhcf_filings").fetchone()[0]
    quarters = con.execute("SELECT COUNT(DISTINCT period_end) FROM bhcf_filings").fetchone()[0]
    date_range = con.execute("SELECT MIN(period_end), MAX(period_end) FROM bhcf_filings").fetchone()

    print(f"  Total BHCF observations (all time): {total:,}")
    print(f"  Unique entities: {entities:,}")
    print(f"  Unique variables: {variables:,}")
    print(f"  Quarters covered: {quarters}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")
    print(f"  Pre-2000 added: {total_rows:,}")

    con.close()

    secs = elapsed()
    log_ingestion("5", f"BHCF CSV pre-2000: {total_rows:,} observations from {len(pre2000_csvs)} files. Grand total: {total:,}. {secs:.1f}s")
    print(f"\nPhase 5 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
