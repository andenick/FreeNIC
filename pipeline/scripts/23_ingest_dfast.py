"""Phase 23: Ingest DFAST Stress Test Results (2013-2025).

Source: Inputs/dfast/public_results_DFAST_2025.csv (cumulative file from Federal Reserve)
Target: dfast_results table

Contains capital ratios, loan losses, revenue, and income projections under stress scenarios
for 22-43 large BHCs per year, 14 annual exercises (DFAST 2013 through 2025 Stress Test).
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

DFAST_DIR = INPUT_PATHS['dfast']

# Columns to unpivot as stress test variables (skip identifiers and names)
SKIP_COLS = {
    "exercise_name", "dt_exercise_quarter", "id_rssd",
    "disclosure_legal_name", "scenario_id", "scenario_name",
}

# Variable descriptions for key metrics
VAR_DESCRIPTIONS = {
    "common_equity_tier1_actual_rat": "CET1 Ratio (Actual)",
    "common_equity_tier1_end_rat": "CET1 Ratio (End of Horizon)",
    "common_equity_tier1_min_rat": "CET1 Ratio (Minimum)",
    "tier1_capital_actual_rat": "Tier 1 Capital Ratio (Actual)",
    "tier1_capital_min_rat": "Tier 1 Capital Ratio (Minimum)",
    "total_capital_actual_rat": "Total Capital Ratio (Actual)",
    "total_capital_min_rat": "Total Capital Ratio (Minimum)",
    "tier1_leverage_actual_rat": "Tier 1 Leverage Ratio (Actual)",
    "tier1_leverage_min_rat": "Tier 1 Leverage Ratio (Minimum)",
    "supp_leverage_actual_rat": "Supplementary Leverage Ratio (Actual)",
    "supp_leverage_min_rat": "Supplementary Leverage Ratio (Minimum)",
    "loss_total_loan_amt": "Total Loan Losses ($B)",
    "loss_total_loan_rate": "Total Loan Loss Rate (%)",
    "revenue_preprovision_net_amt": "Pre-Provision Net Revenue ($B)",
    "income_pretax_net_amt": "Pre-Tax Net Income ($B)",
}


def parse_exercise_year(exercise_name):
    """Extract year from exercise name like 'DFAST 2013' or '2025 Stress Test'."""
    match = re.search(r'(\d{4})', exercise_name)
    return int(match.group(1)) if match else None


def main():
    elapsed = timer()
    print("=== Phase 23: DFAST Stress Test Results Ingestion ===\n")

    # Use the cumulative 2025 file (contains all years 2013-2025)
    csv_path = DFAST_DIR / "public_results_DFAST_2025.csv"
    if not csv_path.exists():
        print(f"  ERROR: {csv_path} not found")
        return

    con = get_db()

    # Create table
    con.execute("DROP TABLE IF EXISTS dfast_results")
    con.execute("""
        CREATE TABLE dfast_results (
            rssd_id         INTEGER,
            bank_name       VARCHAR,
            year            INTEGER,
            exercise_name   VARCHAR,
            scenario        VARCHAR,
            variable_id     VARCHAR,
            value           DOUBLE,
            source          VARCHAR DEFAULT 'dfast'
        )
    """)

    # Read and unpivot
    total_rows = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        var_cols = [c for c in reader.fieldnames if c not in SKIP_COLS]

        batch = []
        for row in reader:
            rssd_id = row.get("id_rssd", "").strip()
            if not rssd_id:
                continue  # Skip aggregate rows
            try:
                rssd_id = int(rssd_id)
            except ValueError:
                continue

            bank_name = row.get("disclosure_legal_name", "").strip()
            exercise = row.get("exercise_name", "").strip()
            year = parse_exercise_year(exercise)
            scenario = row.get("scenario_name", "").strip()

            for vc in var_cols:
                val = row.get(vc, "").strip()
                if not val or val in ("", "N/A", "n/a"):
                    continue
                try:
                    value = float(val)
                except ValueError:
                    continue

                batch.append((rssd_id, bank_name, year, exercise,
                             scenario, vc, value, "dfast"))
                total_rows += 1

                if len(batch) >= 10000:
                    con.executemany("""
                        INSERT INTO dfast_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    batch = []

        if batch:
            con.executemany("""
                INSERT INTO dfast_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)

    # Summary
    count = con.execute("SELECT COUNT(*) FROM dfast_results").fetchone()[0]
    banks = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM dfast_results").fetchone()[0]
    years = con.execute("SELECT COUNT(DISTINCT year) FROM dfast_results").fetchone()[0]
    scenarios = con.execute("SELECT COUNT(DISTINCT scenario) FROM dfast_results").fetchone()[0]
    variables = con.execute("SELECT COUNT(DISTINCT variable_id) FROM dfast_results").fetchone()[0]
    year_range = con.execute("SELECT MIN(year), MAX(year) FROM dfast_results").fetchone()

    # Cross-reference with institutions
    matched = con.execute("""
        SELECT COUNT(DISTINCT d.rssd_id) FROM dfast_results d
        WHERE EXISTS (SELECT 1 FROM institutions i WHERE i.rssd_id = d.rssd_id)
    """).fetchone()[0]

    print(f"\n--- Summary ---")
    print(f"  Total observations: {count:,}")
    print(f"  Banks: {banks}")
    print(f"  Years: {years} ({year_range[0]} to {year_range[1]})")
    print(f"  Scenarios: {scenarios}")
    print(f"  Variables: {variables}")
    print(f"  Matched to institutions: {matched} / {banks} ({matched/banks*100:.0f}%)")

    con.close()

    secs = elapsed()
    log_ingestion("23", f"DFAST: {count:,} obs, {banks} banks, {years} years "
                  f"({year_range[0]}-{year_range[1]}), {variables} variables. {secs:.1f}s")
    print(f"\nPhase 23 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
