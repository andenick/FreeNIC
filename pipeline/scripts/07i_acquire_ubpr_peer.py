"""Phase 7i: Acquire FFIEC CDR Public bulk UBPR **Rank** and **Stats** (peer percentiles) via
Playwright. These are "Four Periods" products (one ZIP per YEAR = 4 quarters), distinct from the
date-based Single-Period UBPR (07g). XBRL format (per-bank XML in the ZIP); TSV crashes headless.
Cloned from 07g_acquire_ubpr.py. NO values fabricated. Public (no auth):
https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx

Usage:
  python 07i_acquire_ubpr_peer.py rank 2024            # one product, one year (probe)
  python 07i_acquire_ubpr_peer.py stats 2024 2023      # one product, several years
  python 07i_acquire_ubpr_peer.py both                 # both products, all 25 offered years
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from utils import INPUT_PATHS  # noqa: E402

URL = "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx"
DD = "select[name='ctl00$MainContentHolder$DatesDropDownList']"
PRODUCTS = {
    "rank": "PerformanceReportingSeriesRank",
    "stats": "PerformanceReportingSeriesStats",
}
BULK_DIR = INPUT_PATHS["cdr_call_bulk"].parent  # Inputs/


def raw_dir(prod_key: str) -> Path:
    d = BULK_DIR / f"ubpr_{prod_key}_bulk"
    d.mkdir(parents=True, exist_ok=True)
    return d


def select_product(pg, product_value: str) -> None:
    pg.select_option("select#ListBox1, select[name='ctl00$MainContentHolder$ListBox1']",
                     value=product_value)
    pg.wait_for_timeout(2800)
    pg.wait_for_selector(DD, timeout=20000)


def read_year_map(pg) -> dict:
    """Four-Periods dropdown options are bare years ('2024'); map year -> internal postback value."""
    opts = pg.eval_on_selector_all(
        DD + " option", "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
    pm = {}
    for o in opts:
        t = o["t"].strip()
        if t.isdigit() and len(t) == 4:
            pm[t] = o["v"]
    return pm


def download_year(pg, internal_value: str, prod_key: str, year: str) -> int:
    pg.select_option(DD, value=internal_value)
    pg.wait_for_timeout(1800)
    with pg.expect_download(timeout=180000) as dlinfo:
        try:
            pg.click("a#Download_0, input#Download_0, "
                     "[name='ctl00$MainContentHolder$TabStrip1$Download_0']", timeout=8000)
        except Exception:
            pg.get_by_text("Download", exact=False).first.click(timeout=8000)
    dest = raw_dir(prod_key) / f"ubpr_{prod_key}_{year}.zip"
    dlinfo.value.save_as(str(dest))
    return dest.stat().st_size


def acquire(prod_keys, years_wanted):
    got, failed = [], []
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=[
            "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
            "--js-flags=--max-old-space-size=4096"])
        ctx = br.new_context(accept_downloads=True)
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        pg.goto(URL, wait_until="networkidle")
        for pk in prod_keys:
            select_product(pg, PRODUCTS[pk])
            pm = read_year_map(pg)
            years = years_wanted or sorted(pm)
            years = [y for y in years if y in pm]
            # skip already-downloaded
            years = [y for y in years
                     if not (raw_dir(pk) / f"ubpr_{pk}_{y}.zip").exists()
                     or (raw_dir(pk) / f"ubpr_{pk}_{y}.zip").stat().st_size < 1000]
            print(f"[plan] {pk}: {len(years)} year(s) of {len(pm)} offered -> {raw_dir(pk)}")
            for y in years:
                ok = False
                for _ in (1, 2, 3):
                    try:
                        sz = download_year(pg, pm[y], pk, y)
                        if sz > 1000:
                            print(f"[ok] {pk} {y}: {sz:,} bytes")
                            got.append((pk, y, sz)); ok = True; break
                    except Exception as e:
                        print(f"[retry] {pk} {y}: {type(e).__name__}: {str(e)[:80]}")
                        try:
                            pg.goto(URL, wait_until="networkidle")
                            select_product(pg, PRODUCTS[pk])
                            pm = read_year_map(pg)
                        except Exception:
                            pass
                    time.sleep(3)
                if not ok:
                    failed.append((pk, y))
                time.sleep(1)
        br.close()
    print(f"\n[summary] downloaded {len(got)}; failed {len(failed)}")
    if failed:
        print("  failed:", failed)
    return got, failed


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "both":
        prod_keys, years = ["rank", "stats"], [a for a in args[1:] if a.isdigit()]
    elif args[0] in PRODUCTS:
        prod_keys, years = [args[0]], [a for a in args[1:] if a.isdigit()]
    else:
        print(f"unknown product '{args[0]}' (use rank|stats|both)")
        return 1
    got, failed = acquire(prod_keys, years)
    return 0 if got else 2


if __name__ == "__main__":
    sys.exit(main())
