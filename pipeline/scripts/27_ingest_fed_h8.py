"""Phase 27: Ingest Fed H.8 aggregate banking statistics from FRED.

Source: FRED API (no key required for CSV download)
Covers weekly aggregate banking data since 1973: total bank credit,
total loans, total securities, total deposits by bank type.

Downloads CSVs directly from FRED for each series.
"""

import csv
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUTS_DIR

CACHE_DIR = INPUTS_DIR / "fred_h8"

# FRED series available via CSV download (H8B* series need API key, excluded)
H8_SERIES = {
    # Bank credit and loans
    "TOTBKCR": "Total bank credit, all commercial banks",
    "BUSLOANS": "Commercial and industrial loans, all commercial banks",
    "CONSUMER": "Consumer loans, all commercial banks",
    "REALLN": "Real estate loans, all commercial banks",
    "TOTLL": "Total loans and leases, all commercial banks",
    # Deposits
    "DPSACBW027SBOG": "Deposits, all commercial banks (weekly)",
    # Rates
    "FEDFUNDS": "Federal funds effective rate",
    "DPRIME": "Bank prime loan rate",
    "MORTGAGE30US": "30-year fixed-rate mortgage average",
    "T10Y2Y": "10-Year Treasury minus 2-Year (yield curve)",
    "DFF": "Federal funds rate (daily)",
    # Macro context
    "GDPC1": "Real GDP (quarterly)",
    "UNRATE": "Unemployment rate",
    "CPIAUCSL": "Consumer Price Index",
    "INDPRO": "Industrial Production Index",
}

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def download_series():
    """Download all FRED series as CSVs."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    marker = CACHE_DIR / "_DOWNLOAD_COMPLETE"

    if marker.exists():
        print("  Download already complete (marker found)")
        return

    downloaded = 0
    for series_id in H8_SERIES:
        csv_path = CACHE_DIR / f"{series_id}.csv"
        if csv_path.exists() and csv_path.stat().st_size > 50:
            downloaded += 1
            continue

        url = FRED_CSV_URL.format(series_id=series_id)
        print(f"  Downloading {series_id}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (freenic/1.0)"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            csv_path.write_bytes(data)
            downloaded += 1
            time.sleep(1.0)  # Generous rate limit for FRED
        except Exception as e:
            print(f"    WARN: {series_id} failed: {e}")

    print(f"  Downloaded {downloaded}/{len(H8_SERIES)} series")
    marker.write_text(f"Downloaded {downloaded} series")


def ingest(con):
    """Load FRED CSVs into fed_h8 and fred_macro tables."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS fred_series (
            series_id       VARCHAR,
            observation_date DATE,
            value           DOUBLE,
            series_name     VARCHAR
        )
    """)
    con.execute("DELETE FROM fred_series")

    total_rows = 0
    for series_id, name in H8_SERIES.items():
        csv_path = CACHE_DIR / f"{series_id}.csv"
        if not csv_path.exists():
            continue

        rows = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.get("observation_date", "") or row.get("DATE", "")
                val_str = row.get(series_id, "")
                if not date_str or val_str == "." or not val_str:
                    continue
                try:
                    val = float(val_str)
                    rows.append((series_id, date_str, val, name))
                except ValueError:
                    continue

        if rows:
            con.executemany(
                "INSERT INTO fred_series VALUES (?, ?, ?, ?)", rows
            )
            total_rows += len(rows)
            print(f"  {series_id}: {len(rows):,} observations")

    count = con.execute("SELECT COUNT(*) FROM fred_series").fetchone()[0]
    return count


def main():
    elapsed = timer()
    print("=== Phase 27: Fed H.8 + FRED Macro Series ===\n")

    download_series()

    con = get_db()
    count = ingest(con)
    con.close()

    secs = elapsed()
    print(f"\n  Ingested: {count:,} observations across {len(H8_SERIES)} series")
    log_ingestion("27", f"FRED series: {count:,} obs from {len(H8_SERIES)} series. {secs:.1f}s")
    print(f"\nPhase 27 complete in {secs:.1f}s")


if __name__ == "__main__":
    main()
