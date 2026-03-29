"""Phase 16: Ingest FDIC Failed Banks data (1934-present).

Source: FDIC BankFind API (api.fdic.gov/banks/failures)
Downloaded to: Inputs/fdic_failures_api.json (4,114 records)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS


def main():
    elapsed = timer()
    print("=== Phase 16: FDIC Failed Banks Ingestion ===\n")

    json_path = INPUT_PATHS['fdic_failures']
    if not json_path.exists():
        print(f"  ERROR: {json_path} not found")
        return

    with open(json_path, "r") as f:
        failures = json.load(f)
    print(f"  Loaded {len(failures):,} failure records")

    con = get_db()

    # Create table
    con.execute("DROP TABLE IF EXISTS bank_failures")
    con.execute("""
        CREATE TABLE bank_failures (
            cert INTEGER,
            bank_name VARCHAR,
            city VARCHAR,
            state_code VARCHAR,
            closing_date DATE,
            failure_year INTEGER,
            acquiring_institution VARCHAR,
            acquiring_city VARCHAR,
            acquiring_state VARCHAR,
            fund INTEGER,
            total_deposits DOUBLE,
            total_assets DOUBLE,
            estimated_loss DOUBLE,
            resolution_type VARCHAR,
            charter_class VARCHAR,
            source VARCHAR DEFAULT 'fdic_api'
        )
    """)

    # Parse and insert
    rows = []
    parse_errors = 0
    for rec in failures:
        # Parse date
        date_str = rec.get("FAILDATE")
        closing_date = None
        if date_str:
            try:
                from datetime import datetime
                closing_date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                parse_errors += 1

        cert = rec.get("CERT")
        if cert:
            try:
                cert = int(cert)
            except (ValueError, TypeError):
                cert = None

        rows.append((
            cert,
            rec.get("NAME"),
            rec.get("CITY"),
            rec.get("STALP"),
            closing_date,
            rec.get("FAILYR"),
            rec.get("BIDNAME"),
            rec.get("BIDCITY"),
            rec.get("BIDSTATE"),
            rec.get("FUND"),
            rec.get("QBFDEP"),
            rec.get("QBFASSET"),
            rec.get("COST"),
            rec.get("RESTYPE1"),
            rec.get("CHCLASS1"),
            'fdic_api'
        ))

    con.executemany("""
        INSERT INTO bank_failures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    # Summary
    count = con.execute("SELECT COUNT(*) FROM bank_failures").fetchone()[0]
    date_range = con.execute("SELECT MIN(closing_date), MAX(closing_date) FROM bank_failures").fetchone()
    states = con.execute("SELECT COUNT(DISTINCT state_code) FROM bank_failures").fetchone()[0]
    with_cert = con.execute("SELECT COUNT(*) FROM bank_failures WHERE cert IS NOT NULL").fetchone()[0]

    # Cross-reference with institutions table
    matched = con.execute("""
        SELECT COUNT(DISTINCT bf.cert) FROM bank_failures bf
        WHERE EXISTS (SELECT 1 FROM institutions i WHERE i.fdic_cert = bf.cert)
    """).fetchone()[0]

    print(f"\n--- Summary ---")
    print(f"  Total failures: {count:,}")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")
    print(f"  States: {states}")
    print(f"  With FDIC cert: {with_cert:,}")
    print(f"  Matched to institutions table: {matched:,} ({matched/with_cert*100:.1f}%)" if with_cert else "")
    print(f"  Parse errors: {parse_errors}")

    con.close()

    secs = elapsed()
    log_ingestion("16", f"FDIC Failed Banks: {count:,} failures, {date_range[0]} to {date_range[1]}. {secs:.1f}s")
    print(f"\nPhase 16 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
