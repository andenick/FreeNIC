"""V0.2 (browser route) — drive the FFIEC CDR Public bulk-download Telerik AJAX flow with
Playwright (headless Chromium) to fetch Call Reports Single Period, tab-delimited, for
target quarters. The requests-only route failed (Telerik RadAjax partial postbacks are not
single-shot replicable). NO values are fabricated; if the browser flow fails the script
exits non-zero and the report documents the manual procedure.

Public source (NO auth): https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx
Product: 'Call Reports -- Single Period' ; Format: 'Tab Delimited'.
Saves each period's ZIP to data/correia/_cdr_raw/.
"""
import sys
import time
from playwright.sync_api import sync_playwright
from utils import DATA_ROOT

URL = "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx"
RAW = DATA_ROOT / "cdr_raw"
RAW.mkdir(parents=True, exist_ok=True)

# target reporting periods (YYYYMMDD) — Q4 2019..2024 + latest available 2025 quarters
TARGET_YEARS = {"2019", "2020", "2021", "2022", "2023", "2024", "2025"}

got = []
with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    ctx = br.new_context(accept_downloads=True)
    pg = ctx.new_page()
    pg.set_default_timeout(45000)
    pg.goto(URL, wait_until="networkidle")
    print("[nav] loaded bulk page")

    # 1. select product
    pg.select_option("select#ListBox1, select[name='ctl00$MainContentHolder$ListBox1']",
                     value="ReportingSeriesSinglePeriod")
    pg.wait_for_timeout(2500)  # let Telerik AJAX repopulate the dates dropdown
    print("[step] product=Call Reports Single Period selected")

    # 2. enumerate reporting periods now in DatesDropDownList
    dd = "select[name='ctl00$MainContentHolder$DatesDropDownList']"
    pg.wait_for_selector(dd, timeout=20000)
    opts = pg.eval_on_selector_all(
        dd + " option",
        "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
    # option text is the date label (e.g. '12/31/2022'); value is an internal id.
    import re as _re
    def to_ymd(t):
        m = _re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
        if m:
            return f"{m.group(3)}{int(m.group(1)):02d}{int(m.group(2)):02d}"
        m = _re.search(r"(\d{4})[-/]?(\d{2})[-/]?(\d{2})", t)
        return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else None
    period_map = {}  # ymd -> internal value
    for o in opts:
        ymd = to_ymd(o["t"])
        if ymd:
            period_map[ymd] = o["v"]
    print(f"[step] reporting periods available: {len(period_map)} -> "
          f"{sorted(period_map)[-8:]}")
    if not period_map:
        print(f"[BLOCKED] could not parse period dates. sample opts: {opts[:5]}")
        br.close(); sys.exit(2)

    want = sorted([ymd for ymd in period_map
                   if ymd[:4] in TARGET_YEARS and (ymd.endswith("1231") or ymd[:4] == "2025")],
                  reverse=True)
    if "20221231" in period_map and "20221231" not in want:
        want.append("20221231")
    print(f"[target] {want}")

    # 3. select tab-delimited format if a FormatType control exists
    try:
        pg.check("input[value='TabDelimited'], input#FormatType_0", timeout=4000)
        print("[step] format=TabDelimited")
    except Exception:
        # FormatType may be radios with different ids; try by label text
        try:
            pg.get_by_text("Tab Delimited", exact=False).first.click(timeout=4000)
            print("[step] format=Tab Delimited (by label)")
        except Exception as e:
            print(f"[warn] could not set format explicitly ({str(e)[:60]}); using default")

    # 4. per target period: select + download
    for per in want:
        try:
            pg.select_option(dd, value=period_map[per])
            pg.wait_for_timeout(1500)
            with pg.expect_download(timeout=90000) as dlinfo:
                # the Download button
                try:
                    pg.click("a#Download_0, input#Download_0, "
                             "[name='ctl00$MainContentHolder$TabStrip1$Download_0']",
                             timeout=8000)
                except Exception:
                    pg.get_by_text("Download", exact=False).first.click(timeout=8000)
            dl = dlinfo.value
            dest = RAW / f"call_single_{per}.zip"
            dl.save_as(str(dest))
            sz = dest.stat().st_size
            print(f"[download] {per}: {sz:,} bytes -> {dest.name}")
            if sz > 1000:
                got.append((per, sz))
        except Exception as e:
            print(f"[download] {per}: FAILED {type(e).__name__}: {str(e)[:90]}")
        time.sleep(1)

    br.close()

print(f"\n[summary] downloaded {len(got)} period ZIP(s): {got}")
if not got:
    print("[BLOCKED] browser flow reached the page but produced no ZIPs.")
    sys.exit(2)
