"""Phase 30: Ingest Fed stress test scenario definitions.

Source: Set VOLCKER_DATA_DIR env var, or defaults to ../../../Projects/Volcker
Original location: Volcker project Inputs/Data/2026_Proposed_*.csv
6 CSV files covering domestic + international scenarios:
- Historic (actual macro data)
- Baseline (Fed projection)
- Severely Adverse (stress scenario)

Creates two tables (different column structures):
- stress_scenarios_domestic (18 cols: GDP, unemployment, rates, HPI, VIX, etc.)
- stress_scenarios_international (14 cols: Euro area, Asia, Japan, UK)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer

import os
_volcker_root = Path(os.environ.get("VOLCKER_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent.parent.parent / "Volcker")))
VOLCKER_DATA = _volcker_root / "Inputs" / "Data"

DOMESTIC = [
    "2026_Proposed_Historic_Domestic.csv",
    "2026_Proposed_Supervisory_Baseline_Domestic.csv",
    "2026_Proposed_Supervisory_Severely_Adverse_Domestic.csv",
]

INTERNATIONAL = [
    "2026_Proposed_Historic_International.csv",
    "2026_Proposed_Supervisory_Baseline_International.csv",
    "2026_Proposed_Supervisory_Severely_Adverse_International.csv",
]


def ingest_group(con, table_name, files):
    """Ingest a group of scenario files with identical schemas."""
    con.execute(f"DROP TABLE IF EXISTS {table_name}")

    first = True
    for fname in files:
        fpath = VOLCKER_DATA / fname
        if not fpath.exists():
            print(f"  WARNING: {fname} not found, skipping")
            continue

        csv_path = str(fpath).replace("\\", "/")

        if first:
            con.execute(f"""
                CREATE TABLE {table_name} AS
                SELECT * FROM read_csv_auto('{csv_path}', header=true)
            """)
            first = False
        else:
            con.execute(f"""
                INSERT INTO {table_name}
                SELECT * FROM read_csv_auto('{csv_path}', header=true)
            """)

        count = con.execute(f"""
            SELECT COUNT(*) FROM read_csv_auto('{csv_path}', header=true)
        """).fetchone()[0]
        print(f"  {fname}: {count} rows")

    total = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return total


def main():
    elapsed = timer()
    print("=== Phase 30: Stress Test Scenarios ===\n")

    con = get_db()

    print("  --- Domestic ---")
    dom_count = ingest_group(con, "stress_scenarios_domestic", DOMESTIC)
    print(f"  Total domestic: {dom_count:,} rows\n")

    print("  --- International ---")
    intl_count = ingest_group(con, "stress_scenarios_international", INTERNATIONAL)
    print(f"  Total international: {intl_count:,} rows")

    con.close()

    total = dom_count + intl_count
    secs = elapsed()
    print(f"\n  Total: {total:,} rows across 2 tables")
    log_ingestion("30", f"Stress scenarios: domestic={dom_count:,}, intl={intl_count:,}. {secs:.1f}s")
    print(f"\nPhase 30 complete in {secs:.1f}s")


if __name__ == "__main__":
    main()
