"""Phase 3: Ingest CRSP PERMCO-to-RSSD mapping files.

Sources: 16 CSV files in Inputs/2026.03.11 CRSP/
Format: CSV with optional 'notice' column and copyright row.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

CRSP_DIR = INPUT_PATHS['crsp']


def parse_crsp_date(val):
    """Parse CRSP date (YYYYMMDD integer) to YYYY-MM-DD string."""
    if not val:
        return None
    s = str(val).strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return None


def main():
    elapsed = timer()
    print("=== Phase 3: CRSP Mapping Ingestion ===")

    con = get_db()
    con.execute("DELETE FROM crsp_mapping")

    csv_files = sorted(CRSP_DIR.glob("crsp_*.csv"))
    print(f"Found {len(csv_files)} CRSP files")

    total_rows = 0
    for csv_path in csv_files:
        print(f"\n  Processing {csv_path.name}...")
        rows = []

        with open(csv_path, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                # Skip notice/copyright rows
                if not name or "PERMCO" in name or "CRSP" in name:
                    continue

                permco = row.get("permco", "").strip()
                entity = row.get("entity", "").strip()
                if not permco or not entity:
                    continue

                try:
                    permco_int = int(permco)
                    rssd_int = int(entity)
                except ValueError:
                    continue

                rows.append((
                    permco_int,
                    rssd_int,
                    name,
                    (row.get("inst_type") or "").strip(),
                    parse_crsp_date(row.get("dt_start")),
                    parse_crsp_date(row.get("dt_end")),
                    csv_path.name,
                ))

        if rows:
            con.executemany("""
                INSERT INTO crsp_mapping
                (permco, rssd_id, name, inst_type, dt_start, dt_end, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)

        print(f"    {len(rows):,} records")
        total_rows += len(rows)

    # Summary
    print(f"\n--- Summary ---")
    print(f"  Total CRSP records: {total_rows:,}")

    unique_permcos = con.execute("SELECT COUNT(DISTINCT permco) FROM crsp_mapping").fetchone()[0]
    unique_rssds = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM crsp_mapping").fetchone()[0]
    print(f"  Unique PERMCOs: {unique_permcos:,}")
    print(f"  Unique RSSD IDs: {unique_rssds:,}")

    print(f"\n  Institution types:")
    types = con.execute("""
        SELECT inst_type, COUNT(*) as cnt
        FROM crsp_mapping
        GROUP BY inst_type
        ORDER BY cnt DESC
    """).fetchall()
    for t, c in types:
        print(f"    {t}: {c:,}")

    con.close()

    secs = elapsed()
    log_ingestion("3", f"CRSP: {total_rows:,} records from {len(csv_files)} files, {unique_permcos:,} PERMCOs, {unique_rssds:,} RSSDs. {secs:.1f}s")
    print(f"\nPhase 3 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
