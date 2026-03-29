"""Phase 25: Ingest FDIC Institution History (mergers, name changes, closings).

Source: FDIC BankFind API (api.fdic.gov/banks/history)
~581K records covering charter conversions, name changes, branch openings/closings.
No authentication required. Pagination: limit=10000, offset=N.
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, INPUTS_DIR

CACHE_DIR = INPUTS_DIR / "fdic_history"
BASE_URL = "https://api.fdic.gov/banks/history"

FIELDS = ",".join([
    "CERT", "INSTNAME", "CHANGECODE", "CHANGECODE_DESC",
    "EFFDATE", "PCITY", "PSTALP", "CNTYNAME",
    "CLASS", "PROCDATE", "REGAGNT2",
])

PAGE_SIZE = 10000
MAX_OFFSET = 2_000_000


def download_all():
    """Download all FDIC history records with pagination."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    marker = CACHE_DIR / "_DOWNLOAD_COMPLETE"

    if marker.exists():
        print("  Download already complete (marker found)")
        return

    offset = 0
    total_records = 0
    all_data = []

    while offset < MAX_OFFSET:
        url = f"{BASE_URL}?fields={FIELDS}&limit={PAGE_SIZE}&offset={offset}&sort_by=EFFDATE&sort_order=DESC"
        page_file = CACHE_DIR / f"page_{offset:07d}.json"

        if page_file.exists():
            with open(page_file, "r") as f:
                page = json.load(f)
        else:
            print(f"  Downloading offset {offset}...")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "freenic/1.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    page = json.loads(resp.read().decode())
            except Exception as e:
                print(f"  ERROR at offset {offset}: {e}")
                break

            with open(page_file, "w") as f:
                json.dump(page, f)
            time.sleep(0.5)

        records = page.get("data", [])
        if not records:
            break

        total_count = page.get("totals", {}).get("count", 0)
        all_data.extend(records)
        total_records += len(records)
        print(f"    offset={offset}: {len(records)} records (total so far: {total_records}/{total_count})")

        if len(records) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    # Write combined file
    combined_path = CACHE_DIR / "combined.json"
    with open(combined_path, "w") as f:
        json.dump(all_data, f)
    print(f"  Combined: {total_records} records -> {combined_path}")

    marker.write_text(f"Downloaded {total_records} records")
    return total_records


def ingest(con):
    """Ingest FDIC history into DuckDB using native JSON reader (fast)."""
    con.execute("DROP TABLE IF EXISTS fdic_history")
    combined_path = str(CACHE_DIR / "combined.json").replace("\\", "/")

    # Use DuckDB native JSON reader with auto-detect for nested struct
    con.execute(f"""
        CREATE TABLE fdic_history AS
        SELECT
            CAST(data.CERT AS INTEGER) AS fdic_cert,
            data.INSTNAME AS institution_name,
            CAST(data.CHANGECODE AS INTEGER) AS change_code,
            data.CHANGECODE_DESC AS change_desc,
            CASE WHEN data.EFFDATE IS NOT NULL
                 THEN CAST(LEFT(data.EFFDATE, 10) AS DATE)
                 ELSE NULL END AS effective_date,
            data.PCITY AS city,
            data.PSTALP AS state_code,
            data.CNTYNAME AS county,
            data.CLASS AS class_code,
            CASE WHEN data.PROCDATE IS NOT NULL
                 THEN CAST(LEFT(data.PROCDATE, 10) AS DATE)
                 ELSE NULL END AS process_date
        FROM read_json_auto('{combined_path}', format='array')
    """)

    count = con.execute("SELECT COUNT(*) FROM fdic_history").fetchone()[0]
    return count


def main():
    elapsed = timer()
    print("=== Phase 25: FDIC Institution History ===\n")

    total_downloaded = download_all()

    con = get_db()
    count = ingest(con)
    con.close()

    secs = elapsed()
    print(f"\n  Ingested: {count:,} history records")
    log_ingestion("25", f"FDIC history: {count:,} records. {secs:.1f}s")
    print(f"\nPhase 25 complete in {secs:.1f}s")


if __name__ == "__main__":
    main()
