"""Phase 8: Ingest Luck Database call reports (balance sheets + income statements).

Sources: call-reports-balance-sheets-Jan2026.dta, call-reports-income-statements-Jan2026.dta
Format: Stata DTA with id_rssd and date (datetime64, quarter-start dates like 1986-01-01).
We convert quarter-start dates to quarter-end dates (e.g., 1986-01-01 -> 1986-03-31).
"""

import sys
import gc
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

LUCK_DIR = INPUT_PATHS['luck']


def quarter_start_to_end(dt):
    """Convert quarter-start date to quarter-end date.

    Jan 1 -> Mar 31 (Q1), Apr 1 -> Jun 30 (Q2),
    Jul 1 -> Sep 30 (Q3), Oct 1 -> Dec 31 (Q4).
    """
    if pd.isna(dt):
        return None
    month = dt.month
    year = dt.year
    quarter_ends = {1: "03-31", 4: "06-30", 7: "09-30", 10: "12-31"}
    end = quarter_ends.get(month)
    if end:
        return f"{year}-{end}"
    # Fallback: use pandas quarter end
    return str((dt + pd.offsets.QuarterEnd(0)).date())


def ingest_dta(con, dta_path, source_label):
    """Ingest a Stata DTA file into luck_call_reports in long format."""
    print(f"  Reading {dta_path.name} ({dta_path.stat().st_size / (1024**3):.1f} GB)...")

    chunk_size = 500000
    total_rows = 0
    chunk_num = 0

    reader = pd.read_stata(str(dta_path), chunksize=chunk_size)

    for chunk in reader:
        chunk_num += 1

        # Identify columns
        id_col = 'id_rssd' if 'id_rssd' in chunk.columns else chunk.columns[0]
        date_col = 'date' if 'date' in chunk.columns else chunk.columns[1]

        # Variable columns (everything except id and date)
        var_cols = [c for c in chunk.columns if c not in (id_col, date_col)
                    and chunk[c].dtype in ('float64', 'float32', 'int64', 'int32')]

        # Melt to long format
        df_long = chunk[[id_col, date_col] + var_cols].melt(
            id_vars=[id_col, date_col],
            var_name='variable_id',
            value_name='value'
        ).dropna(subset=['value'])

        if df_long.empty:
            continue

        # Convert quarter-start datetime to quarter-end date string
        df_long['period_end'] = df_long[date_col].apply(quarter_start_to_end)
        df_long['entity_id'] = df_long[id_col].astype(int)
        df_long['source'] = source_label

        df_insert = df_long[['entity_id', 'period_end', 'variable_id', 'value', 'source']]

        con.execute("""
            INSERT INTO luck_call_reports (entity_id, period_end, variable_id, value, source)
            SELECT * FROM df_insert
        """)

        total_rows += len(df_insert)

        if chunk_num % 5 == 0:
            print(f"    Chunk {chunk_num}: {total_rows:,} total rows...")
            gc.collect()

    print(f"    {source_label}: {total_rows:,} observations")
    return total_rows


def main():
    elapsed = timer()
    print("=== Phase 8: Luck Database Ingestion ===")

    con = get_db()
    con.execute("DELETE FROM luck_call_reports")

    total = 0

    # Balance sheets
    bs_dir = LUCK_DIR / "call-reports-balance-sheets-Jan2026"
    bs_files = list(bs_dir.glob("*.dta"))
    if bs_files:
        total += ingest_dta(con, bs_files[0], "luck_balance_sheet")

    # Income statements
    is_dir = LUCK_DIR / "call-reports-income-statements-Jan2026"
    is_files = list(is_dir.glob("*.dta"))
    if is_files:
        total += ingest_dta(con, is_files[0], "luck_income_statement")

    # Summary
    print(f"\n--- Summary ---")
    count = con.execute("SELECT COUNT(*) FROM luck_call_reports").fetchone()[0]
    entities = con.execute("SELECT COUNT(DISTINCT entity_id) FROM luck_call_reports").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM luck_call_reports").fetchone()[0]
    quarters = con.execute("SELECT COUNT(DISTINCT period_end) FROM luck_call_reports").fetchone()[0]
    date_range = con.execute("SELECT MIN(period_end), MAX(period_end) FROM luck_call_reports").fetchone()

    print(f"  Total observations: {count:,}")
    print(f"  Unique entities: {entities:,}")
    print(f"  Unique variables: {variables:,}")
    print(f"  Quarters covered: {quarters}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")

    con.close()

    secs = elapsed()
    log_ingestion("8", f"Luck Database: {count:,} observations, {entities:,} entities, {variables:,} variables, {quarters} quarters. {secs:.1f}s")
    print(f"\nPhase 8 complete in {secs:.1f}s ({secs/60:.1f} minutes).")


if __name__ == "__main__":
    main()
