"""Phase 28: Ingest the Failing Banks annual panel dataset.

Source: the public Failing Banks database
(https://github.com/andenick/failing-banks), FAILING_BANKS/ directory.

- combined_data.csv: 2,867,936 bank-year observations, 156 variables, 1863-2024
- deposits_before_failure_historical.csv: 2,961 pre-FDIC era deposit dynamics
- deposits_before_failure_modern.csv: 547 modern era deposit dynamics with run indicator

This is an annual panel of ALL US banks (failed + surviving) with financial data,
failure indicators, macro context, and computed ratios. Partially fills the 1905-1958 gap
in freenic's temporal coverage.

Place the FAILING_BANKS CSVs under either:
  - Inputs/failing_banks/   (bundled with the project), or
  - $DATA_ROOT/failing_banks/   (external source root; see README "## Setup")
See data/MANIFEST.md for download details.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUTS_DIR, DATA_ROOT

# Prefer the project-bundled checkout; fall back to DATA_ROOT.
_BUNDLED = INPUTS_DIR / "failing_banks" / "FAILING_BANKS"
_EXTERNAL = DATA_ROOT / "failing_banks" / "FAILING_BANKS"

if _BUNDLED.exists() and any(_BUNDLED.iterdir()):
    FAILING_BANKS = _BUNDLED
else:
    FAILING_BANKS = _EXTERNAL
    if not (_EXTERNAL.exists() and any(_EXTERNAL.iterdir())):
        print(f"[WARN] Failing Banks data not found at {_BUNDLED} or {_EXTERNAL}")
        print("[WARN] Download from https://github.com/andenick/failing-banks (see data/MANIFEST.md)")


def ingest_panel(con):
    """Ingest the main Failing Banks combined panel using DuckDB CSV reader."""
    csv_path = str(FAILING_BANKS / "combined_data.csv").replace("\\", "/")

    con.execute("DROP TABLE IF EXISTS robin_panel")
    con.execute(f"""
        CREATE TABLE robin_panel AS
        SELECT * FROM read_csv_auto('{csv_path}',
            header=true,
            sample_size=10000,
            ignore_errors=true
        )
    """)

    count = con.execute("SELECT COUNT(*) FROM robin_panel").fetchone()[0]
    cols = len(con.execute("SELECT * FROM robin_panel LIMIT 0").description)
    years = con.execute("SELECT MIN(year), MAX(year) FROM robin_panel").fetchone()
    banks = con.execute("SELECT COUNT(DISTINCT bank_id) FROM robin_panel").fetchone()[0]
    failed = con.execute("SELECT COUNT(DISTINCT bank_id) FROM robin_panel WHERE failed_bank = 1").fetchone()[0]

    print(f"  robin_panel: {count:,} rows, {cols} columns")
    print(f"  Coverage: {years[0]}-{years[1]}, {banks:,} banks ({failed:,} failed)")
    return count


def ingest_deposits(con):
    """Ingest deposit behavior data (historical + modern)."""
    total = 0

    for name, table in [
        ("deposits_before_failure_historical.csv", "robin_deposits_historical"),
        ("deposits_before_failure_modern.csv", "robin_deposits_modern"),
    ]:
        csv_path = str(FAILING_BANKS / name).replace("\\", "/")
        con.execute(f"DROP TABLE IF EXISTS {table}")
        con.execute(f"""
            CREATE TABLE {table} AS
            SELECT * FROM read_csv_auto('{csv_path}', header=true)
        """)
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count:,} rows")
        total += count

    return total


def main():
    elapsed = timer()
    print("=== Phase 28: Robin Failing Banks Panel ===\n")

    con = get_db()

    panel_count = ingest_panel(con)
    deposits_count = ingest_deposits(con)

    con.close()

    total = panel_count + deposits_count
    secs = elapsed()
    print(f"\n  Total: {total:,} rows across 3 tables")
    log_ingestion("28", f"Robin panel: {panel_count:,} + deposits: {deposits_count:,}. {secs:.1f}s")
    print(f"\nPhase 28 complete in {secs:.1f}s")


if __name__ == "__main__":
    main()
