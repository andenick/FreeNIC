"""Phase 18: Download FDIC Summary of Deposits (SOD) data.

Source: FDIC BankFind API (banks.data.fdic.gov/api/sod)
Output: Inputs/fdic_sod/page_NNNN.json (paginated cache)

2,823,000 branch-level deposit records (1994-present).
No authentication required. Pagination: limit=10000, offset=N.
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import INPUT_PATHS, log_ingestion, timer

CACHE_DIR = INPUT_PATHS['fdic_sod']
BASE_URL = "https://banks.data.fdic.gov/api/sod"

# Fields to download (branch-level deposit data + identifiers)
FIELDS = ",".join([
    "CERT", "RSSDID", "YEAR", "BRNUM", "UNINUMBR",
    "NAMEBR", "ADDRESS", "CITY2BR", "STALPBR", "STNAMEBR",
    "ZIPBR", "CNTYNAMB", "CNTYNUMB",
    "SIMS_LATITUDE", "SIMS_LONGITUDE",
    "DEPSUMBR",  # Branch deposits
    "DEPSUM",    # Institution total deposits
    "DEPDOM",    # Domestic deposits
    "ASSET",     # Total assets
    "NAMEHCR", "RSSDHCR",  # Holding company info
    "BKCLASS", "CHARTER", "REGAGNT",  # Regulatory info
])

PAGE_SIZE = 10000


def download_page(offset, fields=FIELDS):
    """Download a single page from the FDIC SOD API."""
    url = f"{BASE_URL}?limit={PAGE_SIZE}&offset={offset}&fields={fields}&sort_by=YEAR&sort_order=ASC"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "freenic-research/1.0")

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data


def main():
    elapsed = timer()
    print("=== Phase 18: Download FDIC Summary of Deposits ===\n")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Check if already complete
    sentinel = CACHE_DIR / "_DOWNLOAD_COMPLETE"
    if sentinel.exists():
        page_files = sorted(CACHE_DIR.glob("page_*.json"))
        print(f"  Download already complete ({len(page_files)} pages cached).")
        return

    # Get total count (retry on transient 429/5xx — FDIC rate-limits bursts)
    print("  Probing API for total record count...")
    probe = None
    for attempt in range(8):
        try:
            probe = download_page(0)
            break
        except Exception as e:
            print(f"  probe retry {attempt}: {str(e)[:70]}")
            time.sleep(20)
    if probe is None:
        print("  FATAL: probe failed after retries.")
        return
    total = probe["meta"]["total"]
    print(f"  Total records: {total:,}")

    # Save first page
    page_path = CACHE_DIR / "page_0000.json"
    records = [r["data"] for r in probe["data"]]
    with open(page_path, "w") as f:
        json.dump(records, f)
    print(f"  Page 0000: {len(records)} records")

    # Download remaining pages
    total_downloaded = len(records)
    page_num = 1

    while total_downloaded < total:
        offset = page_num * PAGE_SIZE
        page_path = CACHE_DIR / f"page_{page_num:04d}.json"

        # Skip if already cached
        if page_path.exists():
            with open(page_path) as f:
                cached = json.load(f)
            total_downloaded += len(cached)
            page_num += 1
            continue

        # Robust per-page retry with exponential backoff — FDIC rate-limits
        # bursts hard (HTTP 429). Transient errors must not abort the run.
        records = None
        for attempt in range(10):
            try:
                data = download_page(offset)
                records = [r["data"] for r in data["data"]]
                break
            except Exception as e:
                wait = min(60, 5 * (2 ** attempt))
                print(f"  page {page_num:04d} attempt {attempt} failed ({str(e)[:60]}); "
                      f"backoff {wait}s")
                time.sleep(wait)
        if records is None:
            print(f"  STOP: page {page_num} unrecoverable after retries; "
                  f"leaving cache for resume (no sentinel).")
            break

        if not records:
            print(f"  Page {page_num:04d}: empty response, stopping.")
            break

        with open(page_path, "w") as f:
            json.dump(records, f)
        total_downloaded += len(records)
        print(f"  Page {page_num:04d}: {len(records)} records "
              f"(total: {total_downloaded:,} / {total:,})")

        page_num += 1
        # Steady pause to stay under FDIC's rate cap.
        time.sleep(1.0)

    # Only mark complete if we actually pulled everything (no false "complete"
    # on a rate-limited partial — re-running resumes from cached pages).
    if total_downloaded >= total:
        sentinel.write_text(f"Downloaded {total_downloaded:,} records in {page_num} pages\n")
        print(f"  Download COMPLETE: {total_downloaded:,}/{total:,} records.")
    else:
        print(f"  PARTIAL: {total_downloaded:,}/{total:,} records cached. "
              f"Re-run to resume; sentinel NOT written.")

    secs = elapsed()
    log_ingestion("18", f"FDIC SOD Download: {total_downloaded:,} records, {page_num} pages. {secs:.1f}s")
    print(f"\nPhase 18 complete: {total_downloaded:,} records in {secs:.1f}s.")


if __name__ == "__main__":
    main()
