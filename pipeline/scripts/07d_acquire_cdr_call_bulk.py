"""Phase 7d: Acquire FFIEC CDR Public bulk Call Reports -- Single Period (tab-delimited
ZIP per reporting period) via Playwright, generalized from 32_acquire_cdr_unrealized.py.

Drives cdr.ffiec.gov Bulk Data -> 'Call Reports -- Single Period' -> Tab Delimited,
iterating reporting periods 2012Q1..2025Q4 (the post-2011 gap in call_report_filings).
One ZIP per period saved to Inputs/cdr_call_bulk/call_single_<YYYYMMDD>.zip.

NO values fabricated. The Telerik RadAjax partial-postback flow is driven in a real
headless Chromium (the requests-only route is not single-shot replicable). Robust to
the AJAX repopulation with retries; if a period download fails it is logged and skipped
(the companion loader 07e is idempotent so a future run resumes).

Public source (NO auth): https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx
Usage:
  python 07d_acquire_cdr_call_bulk.py                 # all 2012Q1..2025Q4 not yet on disk
  python 07d_acquire_cdr_call_bulk.py 20221231        # one specific period (probe)
  python 07d_acquire_cdr_call_bulk.py 2012 2013       # whole years
"""
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from utils import INPUT_PATHS  # noqa: E402

URL = "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx"
RAW = INPUT_PATHS['cdr_call_bulk']
RAW.mkdir(parents=True, exist_ok=True)

DD = "select[name='ctl00$MainContentHolder$DatesDropDownList']"
PRODUCT = "ReportingSeriesSinglePeriod"  # 'Call Reports -- Single Period'

# All quarter-ends 2012Q1..2025Q4 (the gap to close).
QENDS = []
for yr in range(2012, 2026):
    for mmdd in ("0331", "0630", "0930", "1231"):
        QENDS.append(f"{yr}{mmdd}")


def to_ymd(text: str) -> str | None:
    """'12/31/2022' or '2022-12-31' -> '20221231'."""
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        return f"{m.group(3)}{int(m.group(1)):02d}{int(m.group(2)):02d}"
    m = re.search(r"(\d{4})[-/]?(\d{2})[-/]?(\d{2})", text)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else None


def select_product_and_format(pg) -> None:
    pg.select_option(
        "select#ListBox1, select[name='ctl00$MainContentHolder$ListBox1']",
        value=PRODUCT,
    )
    pg.wait_for_timeout(2800)  # Telerik AJAX repopulates the dates dropdown
    pg.wait_for_selector(DD, timeout=20000)
    # Tab-delimited radio
    try:
        pg.check("input[value='TabDelimited'], input#FormatType_0", timeout=4000)
    except Exception:
        try:
            pg.get_by_text("Tab Delimited", exact=False).first.click(timeout=4000)
        except Exception as e:
            print(f"[warn] could not set Tab Delimited explicitly ({str(e)[:60]}); default")


def read_period_map(pg) -> dict:
    opts = pg.eval_on_selector_all(
        DD + " option",
        "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))",
    )
    pm = {}
    for o in opts:
        ymd = to_ymd(o["t"])
        if ymd:
            pm[ymd] = o["v"]
    return pm


def download_period(pg, internal_value: str, ymd: str) -> int:
    """Select the period, click Download, save ZIP. Returns bytes (0 on fail)."""
    pg.select_option(DD, value=internal_value)
    pg.wait_for_timeout(1800)
    with pg.expect_download(timeout=180000) as dlinfo:
        try:
            pg.click(
                "a#Download_0, input#Download_0, "
                "[name='ctl00$MainContentHolder$TabStrip1$Download_0']",
                timeout=8000,
            )
        except Exception:
            pg.get_by_text("Download", exact=False).first.click(timeout=8000)
    dl = dlinfo.value
    dest = RAW / f"call_single_{ymd}.zip"
    dl.save_as(str(dest))
    return dest.stat().st_size


def main() -> int:
    args = sys.argv[1:]
    if args:
        want = []
        for a in args:
            if len(a) == 8 and a.isdigit():
                want.append(a)
            elif len(a) == 4 and a.isdigit():  # whole year
                want += [q for q in QENDS if q[:4] == a]
        targets = sorted(set(want))
    else:
        targets = list(QENDS)

    # Skip ZIPs already on disk (idempotent acquisition).
    targets = [
        q for q in targets
        if not (RAW / f"call_single_{q}.zip").exists()
        or (RAW / f"call_single_{q}.zip").stat().st_size < 1000
    ]
    print(f"[plan] {len(targets)} period(s) to fetch -> {RAW}")
    if not targets:
        print("[done] nothing to fetch (all present).")
        return 0

    got, failed = [], []
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(accept_downloads=True)
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        pg.goto(URL, wait_until="networkidle")
        select_product_and_format(pg)
        pm = read_period_map(pg)
        print(f"[periods] {len(pm)} available on CDR; "
              f"newest -> {sorted(pm)[-6:]}")

        for ymd in targets:
            if ymd not in pm:
                print(f"[skip] {ymd}: not offered by CDR (unavailable)")
                failed.append((ymd, "not_offered"))
                continue
            ok = False
            for attempt in (1, 2, 3):
                try:
                    sz = download_period(pg, pm[ymd], ymd)
                    if sz > 1000:
                        print(f"[ok] {ymd}: {sz:,} bytes (attempt {attempt})")
                        got.append((ymd, sz))
                        ok = True
                        break
                    print(f"[retry] {ymd}: {sz} bytes too small (attempt {attempt})")
                except Exception as e:
                    print(f"[retry] {ymd}: {type(e).__name__}: {str(e)[:80]} "
                          f"(attempt {attempt})")
                    # re-establish page state on transient failure
                    try:
                        pg.goto(URL, wait_until="networkidle")
                        select_product_and_format(pg)
                        pm = read_period_map(pg)
                    except Exception:
                        pass
                time.sleep(3)
            if not ok:
                failed.append((ymd, "download_failed"))
            time.sleep(1)
        br.close()

    print(f"\n[summary] downloaded {len(got)} ZIP(s); failed {len(failed)}")
    if failed:
        print("  failed:", failed)
    return 0 if got else 2


if __name__ == "__main__":
    sys.exit(main())
