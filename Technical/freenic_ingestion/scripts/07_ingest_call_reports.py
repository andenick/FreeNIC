"""Phase 7: Ingest Chicago Fed Call Reports (SAS XPT files) into call_report_filings.

Sources: 146 directories in Inputs/2026.03.11 Chicago Fed Call Reports/call*-zip/
Each contains a .xpt SAS transport file with one quarter of call report data.
Format: DATE (YYYYMMDD float), ENTITY (RSSD ID), then 2800+ variable columns.
"""

import re
import sys
import time
import gc
import numpy as np
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

CALL_DIR = INPUT_PATHS['call_reports']


def parse_schedule_from_name(dirname):
    """Extract schedule code from directory name like call0003-zip -> 0003."""
    match = re.match(r'call(\d{4})', dirname)
    return match.group(1) if match else dirname


def date_float_to_str(date_val):
    """Convert 20000331.0 -> '2000-03-31'."""
    if date_val is None or np.isnan(date_val):
        return None
    d = str(int(date_val))
    if len(d) == 8:
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return None


def ingest_one_xpt(con, xpt_path, schedule):
    """Read one XPT file and insert unpivoted data into call_report_filings."""
    import pyreadstat

    filename = xpt_path.name

    # Read the XPT file
    try:
        df, meta = pyreadstat.read_xport(str(xpt_path))
    except Exception as e:
        print(f"    ERROR reading {filename}: {e}")
        return 0

    if df.empty:
        return 0

    # Get period from DATE column
    if 'DATE' in df.columns:
        period_val = df['DATE'].dropna().iloc[0] if not df['DATE'].dropna().empty else None
        period_end = date_float_to_str(period_val)
    else:
        period_end = None

    if not period_end:
        print(f"    WARNING: No DATE column or value in {filename}")
        return 0

    # Identify variable columns (exclude DATE, ENTITY, CALL8786 which is a flag)
    skip_cols = {'DATE', 'ENTITY', 'CALL8786'}
    var_cols = [c for c in df.columns if c not in skip_cols]

    # Melt to long format using pandas (faster than SQL for this)
    entity_col = 'ENTITY'
    if entity_col not in df.columns:
        print(f"    WARNING: No ENTITY column in {filename}")
        return 0

    # Filter to only numeric columns (exclude text/string columns)
    numeric_var_cols = []
    for c in var_cols:
        if df[c].dtype in ('float64', 'float32', 'int64', 'int32'):
            numeric_var_cols.append(c)

    if not numeric_var_cols:
        print(f"    WARNING: No numeric variable columns in {filename}")
        return 0

    var_cols = numeric_var_cols

    # Convert to long format, drop NaN
    df_long = df[[entity_col] + var_cols].melt(
        id_vars=[entity_col],
        var_name='variable_id',
        value_name='value'
    ).dropna(subset=['value'])

    # Add metadata columns
    df_long['rssd_id'] = df_long[entity_col].astype(int)
    df_long['period_end'] = period_end
    df_long['schedule'] = schedule
    df_long['source_file'] = filename

    # Select and reorder
    df_insert = df_long[['rssd_id', 'period_end', 'schedule', 'variable_id', 'value', 'source_file']]

    # Insert into DuckDB
    con.execute("""
        INSERT INTO call_report_filings (rssd_id, period_end, schedule, variable_id, value, source_file)
        SELECT * FROM df_insert
    """)

    count = len(df_insert)

    # Record metadata
    n_entities = df_long['rssd_id'].nunique()
    n_vars = df_long['variable_id'].nunique()
    con.execute("""
        INSERT OR REPLACE INTO filing_metadata
        (filing_type, period_end, source_file, entity_count, variable_count, ingestion_ts)
        VALUES ('CALL', ?, ?, ?, ?, ?)
    """, (period_end, filename, n_entities, n_vars, datetime.now()))

    # Free memory
    del df, df_long, df_insert
    gc.collect()

    return count


def main():
    elapsed = timer()
    print("=== Phase 7: Chicago Fed Call Reports Ingestion ===")

    con = get_db()
    con.execute("DELETE FROM call_report_filings")

    # Find all XPT directories
    xpt_dirs = sorted([d for d in CALL_DIR.iterdir()
                       if d.is_dir() and d.name.startswith('call') and d.name.endswith('-zip')])
    print(f"Found {len(xpt_dirs)} call report directories")

    # Also check for non-zip directories and standalone files
    all_dirs = sorted([d for d in CALL_DIR.iterdir() if d.is_dir()])
    xpt_files_direct = sorted(CALL_DIR.glob("*.xpt"))

    if len(all_dirs) > len(xpt_dirs):
        extra = [d.name for d in all_dirs if d not in xpt_dirs]
        if extra:
            print(f"  Also found non-zip dirs: {extra[:5]}...")

    total_rows = 0
    total_files = len(xpt_dirs)
    start_time = time.time()

    for i, xpt_dir in enumerate(xpt_dirs):
        # Find XPT file inside directory
        xpt_files = list(xpt_dir.glob("*.xpt"))
        if not xpt_files:
            print(f"  [{i+1}/{total_files}] {xpt_dir.name}: No XPT file found, skipping")
            continue

        xpt_path = xpt_files[0]
        schedule = parse_schedule_from_name(xpt_dir.name)

        file_start = time.time()
        count = ingest_one_xpt(con, xpt_path, schedule)
        file_time = time.time() - file_start
        total_rows += count

        # Estimate remaining time
        elapsed_so_far = time.time() - start_time
        rate = (i + 1) / elapsed_so_far if elapsed_so_far > 0 else 1
        remaining = (total_files - i - 1) / rate if rate > 0 else 0

        print(f"  [{i+1}/{total_files}] {xpt_dir.name} (schedule {schedule}): "
              f"{count:,} obs ({file_time:.1f}s) "
              f"[total: {total_rows:,}, ETA: {remaining/60:.0f}m]")

    # Summary
    print(f"\n--- Summary ---")
    total = con.execute("SELECT COUNT(*) FROM call_report_filings").fetchone()[0]
    entities = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM call_report_filings").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM call_report_filings").fetchone()[0]
    quarters = con.execute("SELECT COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()[0]
    schedules = con.execute("SELECT COUNT(DISTINCT schedule) FROM call_report_filings").fetchone()[0]
    date_range = con.execute("SELECT MIN(period_end), MAX(period_end) FROM call_report_filings").fetchone()

    print(f"  Total observations: {total:,}")
    print(f"  Unique entities: {entities:,}")
    print(f"  Unique variables: {variables:,}")
    print(f"  Quarters covered: {quarters}")
    print(f"  Schedules: {schedules}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")

    con.close()

    secs = elapsed()
    log_ingestion("7", f"Call Reports: {total:,} observations, {entities:,} entities, {variables:,} variables, {quarters} quarters, {schedules} schedules. {secs:.1f}s")
    print(f"\nPhase 7 complete in {secs:.1f}s ({secs/60:.1f} minutes).")


if __name__ == "__main__":
    main()
