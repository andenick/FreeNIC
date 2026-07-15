"""Phase 7h: Acquire FR Y-15 (systemic-risk / G-SIB indicators) snapshot CSVs.

Source: FFIEC NIC "FR Y-15 Snapshots" (https://www.ffiec.gov/npw/FinancialReport/FRY15Reports).
The page listing is Cloudflare-JS-gated (headless blocked) so we use a HEADED browser to pass
the challenge and read the per-year static-CSV hrefs; the CSV static assets themselves are NOT
gated and download directly. Saves '<reportdate> Snapshot All.csv' + 'Indicators.csv' per year
to Inputs/y15_bulk/. NO values fabricated.

(FR Y-9LP has NO bulk product on NPW — FDD serves only BHCF/Y-9C — so it cannot be acquired as a
dataset; only per-institution filings exist. Not fetched here.)
"""
import sys
import urllib.parse
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120 Safari/537.36")

sys.path.insert(0, str(Path(__file__).parent))
from utils import INPUT_PATHS  # noqa: E402

URL = "https://www.ffiec.gov/npw/FinancialReport/FRY15Reports"
BASE = "https://www.ffiec.gov"
OUT = INPUT_PATHS['cdr_call_bulk'].parent / "y15_bulk"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    print(f"=== Phase 7h: FR Y-15 snapshots -> {OUT} ===")
    got = 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(accept_downloads=True)
        pg = ctx.new_page()
        pg.goto(URL, timeout=70000, wait_until="domcontentloaded")
        for _ in range(7):
            pg.wait_for_timeout(4000)
            if "just a moment" not in pg.title().lower():
                break
        if "just a moment" in pg.title().lower():
            print("  [error] Cloudflare not passed (headed). Aborting.")
            b.close(); return
        hrefs = pg.eval_on_selector_all(
            "a", "els=>els.map(e=>e.getAttribute('href')||'').filter(h=>/Y15SnapShot/i.test(h) && /\\.csv$/i.test(h))")
        hrefs = sorted(set(hrefs))
        print(f"  {len(hrefs)} Y-15 snapshot CSV links found")
        for h in hrefs:
            url = h if h.startswith("http") else BASE + h
            fname = urllib.parse.unquote(h.split("/")[-1]).replace(" ", "_")
            dest = OUT / fname
            if dest.exists() and dest.stat().st_size > 1000:
                print(f"  [skip] {fname} (present)")
                continue
            # the static CSVs are NOT JS-gated -> plain requests with a browser UA + referer works
            # (ctx.request.get returns 403; the page visit above was only to discover the URLs).
            try:
                rr = requests.get(url, headers={"User-Agent": _UA, "Referer": URL}, timeout=60)
                if rr.status_code == 200 and len(rr.content) > 1000:
                    dest.write_bytes(rr.content)
                    print(f"  [ok] {fname}: {dest.stat().st_size:,} bytes")
                    got += 1
                else:
                    print(f"  [warn] {fname}: HTTP {rr.status_code} ({len(rr.content)} bytes)")
            except Exception as e:
                print(f"  [warn] {fname}: {type(e).__name__} {str(e)[:60]}")
        b.close()
    print(f"\n  downloaded {got} Y-15 CSV(s).")


if __name__ == "__main__":
    main()
