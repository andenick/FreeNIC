"""Phase 9: Ingest OCC Historical data (1867-present).

Sources: Inputs/2026.03.11 Luck Database/occ_historical/
  - occ-balance-sheets-tsv (TSV file, 111K rows x 116 cols, primary)
  - documentation/asset_labels.yaml, liability_labels.yaml (variable name mappings)
  - documentation/report_dates.tsv (date mapping: year -> actual report date)

Uses DuckDB native TSV reader for speed, then SQL UNPIVOT for wide-to-long conversion.
"""

import csv
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

OCC_DIR = INPUT_PATHS['occ']


def load_labels():
    """Load asset and liability labels from YAML files."""
    labels = {}
    doc_dir = OCC_DIR / "documentation"

    for yaml_file in doc_dir.glob("*_labels.yaml"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        labels[key] = val[0]  # Use first variant
                    else:
                        labels[key] = str(val)

    return labels


def load_report_dates():
    """Load report_dates.tsv mapping year -> date."""
    date_map = {}
    dates_file = OCC_DIR / "documentation" / "report_dates.tsv"
    if dates_file.exists():
        with open(dates_file, "r") as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                year = int(row['year'])
                month = int(row['report_month'])
                day = int(row['report_day'])
                date_map[year] = f"{year}-{month:02d}-{day:02d}"
    return date_map


def main():
    elapsed = timer()
    print("=== Phase 9: OCC Historical Ingestion ===")

    # Load label mappings
    labels = load_labels()
    print(f"Loaded {len(labels)} variable labels")

    # Load date mapping
    date_map = load_report_dates()
    print(f"Loaded {len(date_map)} report dates ({min(date_map)} to {max(date_map)})")

    # Find TSV file
    tsv_path = OCC_DIR / "occ-balance-sheets-tsv"
    if not tsv_path.is_file():
        print(f"  ERROR: TSV file not found at {tsv_path}")
        return

    con = get_db()
    con.execute("DELETE FROM occ_historical")

    # Load TSV with DuckDB native reader
    tsv_str = str(tsv_path).replace('\\', '/')
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE occ_raw AS
        SELECT * FROM read_csv('{tsv_str}', delim='\t', header=true, all_varchar=true)
    """)

    row_count = con.execute("SELECT COUNT(*) FROM occ_raw").fetchone()[0]
    cols = [r[0] for r in con.execute("DESCRIBE occ_raw").fetchall()]
    print(f"  Loaded {row_count:,} rows, {len(cols)} columns")

    # Identify non-numeric metadata columns to exclude from unpivot
    skip_cols = {'bank_id', 'original_bank_id', 'bank_name', 'state_id', 'state_abbrev',
                 'city_name', 'year', 'lat', 'lon', 'president_id', 'president_name',
                 'cashier_id', 'cashier_name', 'page', 'table'}

    var_cols = [c for c in cols if c not in skip_cols]
    print(f"  Variable columns: {len(var_cols)}")

    # Build report_dates temp table for join
    con.execute("CREATE OR REPLACE TEMP TABLE report_dates (year INTEGER, report_date VARCHAR)")
    for year, date_str in date_map.items():
        con.execute("INSERT INTO report_dates VALUES (?, ?)", (year, date_str))

    # Unpivot using UNION ALL in batches of 50 columns
    batch_size = 50
    total_inserted = 0

    for i in range(0, len(var_cols), batch_size):
        batch = var_cols[i:i + batch_size]
        selects = []
        for col in batch:
            selects.append(f"""
                SELECT
                    CAST(bank_id AS INTEGER) AS bank_id,
                    COALESCE(rd.report_date, CAST(o.year AS VARCHAR) || '-12-31') AS report_date,
                    '{col}' AS variable_id,
                    TRY_CAST(o."{col}" AS DOUBLE) AS value,
                    'occ_historical' AS source
                FROM occ_raw o
                LEFT JOIN report_dates rd ON CAST(o.year AS INTEGER) = rd.year
                WHERE TRY_CAST(o."{col}" AS DOUBLE) IS NOT NULL
            """)

        union_sql = "\nUNION ALL\n".join(selects)
        con.execute(f"""
            INSERT INTO occ_historical (bank_id, report_date, variable_id, value, source)
            {union_sql}
        """)

        batch_count = con.execute("SELECT COUNT(*) FROM occ_historical").fetchone()[0]
        inserted = batch_count - total_inserted
        total_inserted = batch_count
        print(f"    Batch {i // batch_size + 1}: cols {i+1}-{min(i+batch_size, len(var_cols))}, "
              f"+{inserted:,} obs (total: {total_inserted:,})")

    # Summary
    count = con.execute("SELECT COUNT(*) FROM occ_historical").fetchone()[0]
    banks = con.execute("SELECT COUNT(DISTINCT bank_id) FROM occ_historical").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM occ_historical").fetchone()[0]
    date_range = con.execute("SELECT MIN(report_date), MAX(report_date) FROM occ_historical").fetchone()

    print(f"\n--- Summary ---")
    print(f"  Total observations: {count:,}")
    print(f"  Unique banks: {banks:,}")
    print(f"  Unique variables: {variables:,}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")

    con.close()

    secs = elapsed()
    log_ingestion("9", f"OCC Historical: {count:,} observations, {banks:,} banks, {variables:,} variables. {secs:.1f}s")
    print(f"\nPhase 9 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
