"""Phase 4: Ingest BHCF caret-delimited TXT files into bhcf_filings (wide-to-long).

Sources: 104 BHCF*.txt files in Inputs/2026.01 FFIEC Bulk Downloads/
Format: Caret (^) delimited, header row with variable codes, 446-2116 data rows.
Strategy: Read each file with DuckDB, unpivot all variable columns to long format.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

BHCF_DIR = INPUT_PATHS['bhcf_txt']

# RSSD metadata columns to exclude from unpivot (not financial variables)
RSSD_META_COLS = {
    'RSSD9001', 'RSSD9999', 'RSSD9007', 'RSSD9008', 'RSSD9132',
    'RSSD9032', 'RSSD9146', 'RSSD9045',
    # Also exclude text/identifier columns that appear at end of rows
    'RSSD9425', 'RSSD9044', 'RSSD9421', 'RSSD9048', 'RSSD9130',
    'RSSD9014', 'RSSD9031', 'RSSD9005', 'RSSD9150', 'RSSD9170',
    'RSSD9101', 'RSSD9052', 'RSSD9053', 'RSSD9955', 'RSSD9950',
    'RSSD9046', 'RSSD9016', 'RSSD9054', 'RSSD9059', 'RSSD9138',
    'RSSD9060', 'RSSD9579', 'RSSD9042', 'RSSD9161', 'RSSD9050',
    'RSSD9039', 'RSSD9055', 'RSSD9375', 'RSSD6191', 'RSSD9037',
    'RSSD9038', 'RSSD9424', 'RSSD9049', 'RSSD9422', 'RSSD9320',
    'RSSD9017', 'RSSD9010', 'RSSD9047', 'RSSD9030', 'RSSD9192',
    'RSSD9061', 'RSSD9056', 'RSSD9198', 'RSSD9216', 'RSSD9200',
    'RSSD9210', 'RSSD9213', 'RSSD9028', 'RSSD9029', 'RSSD4087',
    'RSSD9220',
}


def parse_period_from_filename(filename):
    """Extract period_end date from filename like BHCF20240930.txt -> 2024-09-30."""
    match = re.search(r'BHCF(\d{8})', filename)
    if match:
        d = match.group(1)
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return None


def ingest_one_file(con, filepath):
    """Ingest a single BHCF file: read wide, unpivot to long, insert into bhcf_filings."""
    filename = filepath.name
    period_end = parse_period_from_filename(filename)
    if not period_end:
        print(f"  SKIP: Cannot parse date from {filename}")
        return 0

    # Read the header to get column names
    with open(filepath, "r", encoding="latin-1") as f:
        header_line = f.readline().strip()
    columns = header_line.split("^")

    # Identify the RSSD ID column (usually RSSD9001) and variable columns
    rssd_col = None
    for c in columns:
        if c.upper() == 'RSSD9001':
            rssd_col = c
            break
    if not rssd_col:
        rssd_col = columns[0]

    # Identify variable columns (exclude RSSD metadata and TEXT* columns)
    var_cols = []
    for c in columns:
        upper = c.upper()
        if upper in RSSD_META_COLS:
            continue
        if upper.startswith('RSSD'):
            continue
        # Skip text columns (like TEXTC703 which contain string descriptions)
        if upper.startswith('TEXT'):
            continue
        var_cols.append(c)

    # Load the file into a temp table using DuckDB
    escaped_path = str(filepath).replace("\\", "/")
    try:
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE bhcf_raw AS
            SELECT * FROM read_csv('{escaped_path}',
                delim='^', header=true, auto_detect=true,
                sample_size=-1, ignore_errors=true,
                all_varchar=true)
        """)
    except Exception as e:
        print(f"  ERROR reading {filename}: {e}")
        return 0

    raw_count = con.execute("SELECT COUNT(*) FROM bhcf_raw").fetchone()[0]

    # Build UNPIVOT query
    # We need to cast each variable column to DOUBLE, skipping empty/non-numeric
    # Use UNION ALL approach for efficiency
    batch_size = 200  # Process columns in batches to avoid query size limits
    total_inserted = 0

    for i in range(0, len(var_cols), batch_size):
        batch = var_cols[i:i + batch_size]

        # Build UNION ALL of SELECT statements for each variable
        selects = []
        for vc in batch:
            # Quote column name to handle special chars
            selects.append(f"""
                SELECT
                    TRY_CAST("{rssd_col}" AS INTEGER) as rssd_id,
                    '{period_end}'::DATE as period_end,
                    '{vc}' as variable_id,
                    TRY_CAST("{vc}" AS DOUBLE) as value,
                    '{filename}' as source_file
                FROM bhcf_raw
                WHERE "{vc}" IS NOT NULL
                    AND TRIM("{vc}") != ''
                    AND TRY_CAST("{vc}" AS DOUBLE) IS NOT NULL
                    AND TRY_CAST("{rssd_col}" AS INTEGER) IS NOT NULL
            """)

        if not selects:
            continue

        union_query = " UNION ALL ".join(selects)

        try:
            con.execute(f"""
                INSERT INTO bhcf_filings (rssd_id, period_end, variable_id, value, source_file)
                {union_query}
            """)
        except Exception as e:
            print(f"  ERROR in batch {i//batch_size}: {e}")

    # Get count for this period
    count = con.execute(f"""
        SELECT COUNT(*) FROM bhcf_filings WHERE period_end = '{period_end}'
    """).fetchone()[0]

    con.execute("DROP TABLE IF EXISTS bhcf_raw")
    return count


def main():
    elapsed = timer()
    print("=== Phase 4: BHCF TXT Ingestion (wide-to-long) ===")

    con = get_db()

    # Clear existing BHCF data
    con.execute("DELETE FROM bhcf_filings")

    # Find all BHCF files
    bhcf_files = sorted(BHCF_DIR.glob("BHCF*.txt"))
    # Filter out non-data files (like README)
    bhcf_files = [f for f in bhcf_files if re.match(r'BHCF\d{8}\.txt', f.name)]
    print(f"Found {len(bhcf_files)} BHCF files")

    total_rows = 0
    for i, filepath in enumerate(bhcf_files):
        period = parse_period_from_filename(filepath.name)
        count = ingest_one_file(con, filepath)
        total_rows += count
        print(f"  [{i+1}/{len(bhcf_files)}] {filepath.name}: {count:,} observations (running total: {total_rows:,})")

        # Record filing metadata
        entities = con.execute(f"""
            SELECT COUNT(DISTINCT rssd_id) FROM bhcf_filings WHERE period_end = '{period}'
        """).fetchone()[0]
        variables = con.execute(f"""
            SELECT COUNT(DISTINCT variable_id) FROM bhcf_filings WHERE period_end = '{period}'
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

    print(f"  Total observations: {total:,}")
    print(f"  Unique entities: {entities:,}")
    print(f"  Unique variables: {variables:,}")
    print(f"  Quarters covered: {quarters}")

    date_range = con.execute("SELECT MIN(period_end), MAX(period_end) FROM bhcf_filings").fetchone()
    print(f"  Date range: {date_range[0]} to {date_range[1]}")

    con.close()

    secs = elapsed()
    log_ingestion("4", f"BHCF TXT: {total:,} observations, {entities:,} entities, {variables:,} variables, {quarters} quarters. {secs:.1f}s")
    print(f"\nPhase 4 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
