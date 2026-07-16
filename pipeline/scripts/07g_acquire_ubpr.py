"""Phase 7g: Acquire FFIEC CDR Public bulk UBPR Ratios -- Single Period (tab-delimited
ZIP per reporting period) via Playwright. Cloned from 07d_acquire_cdr_call_bulk.py.

Drives cdr.ffiec.gov Bulk Data -> 'UBPR Ratio -- Single Period' -> Tab Delimited,
iterating reporting periods. One ZIP per period -> Inputs/ubpr_bulk/ubpr_single_<YYYYMMDD>.zip.
NO values fabricated. Public source (NO auth): https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx

Usage:
  python 07g_acquire_ubpr.py 20241231     # one period (probe)
  python 07g_acquire_ubpr.py 2015 2016    # whole years
  python 07g_acquire_ubpr.py              # default scope 2015Q1..2025Q4 not on disk
"""
import sys
import time
import datetime as _dt
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from utils import INPUT_PATHS  # noqa: E402

URL = "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx"
RAW = INPUT_PATHS['cdr_call_bulk'].parent / "ubpr_bulk"
RAW.mkdir(parents=True, exist_ok=True)

DD = "select[name='ctl00$MainContentHolder$DatesDropDownList']"
PRODUCT = "PerformanceReportingSeriesSinglePeriod"  # 'UBPR Ratio -- Single Period'
# The TSV single-period payload crashes headless Chromium (renderer OOM); XBRL (default,
# per-bank XML files in the ZIP) downloads reliably and is parsed by 39_ingest_ubpr.py.
USE_TSV = False

# 2026-06-09 (A1, Definitive Build): widened from range(2015,2026) to range(2002,2027) for the
# full-extent back-history pull. 2026-07-15 (C5): upper bound is now PROGRAMMATIC (current UTC year
# + 2, floor 2035) so year-args keep resolving for future cycles instead of silently capping at a
# hardcoded upper year -- the same class of bug that bit 07d at 2026. Start stays 2002 (full history).
_QSTART_YEAR = 2002
_QEND_YEAR = max(2035, _dt.date.today().year + 2)
_QMMDD = ("0331", "0630", "0930", "1231")
_VALID_MMDD = set(_QMMDD)
QENDS = [f"{yr}{mmdd}" for yr in range(_QSTART_YEAR, _QEND_YEAR + 1) for mmdd in _QMMDD]


def parse_targets(args):
    """Resolve CLI args -> sorted list of YYYYMMDD quarter-ends, or ABORT loudly.

    Guards (each ERRORS via sys.exit -- never a silent no-op):
      * 8-digit YYYYMMDD whose MMDD is NOT a quarter-end (e.g. 20260615) -> error.
      * 4-digit year outside the producible QENDS range -> error.
      * any other token (e.g. '2026Q2', 'Q2', 3/5/6-digit) -> error.
      * args resolving to zero target periods -> error.
    No args -> full QENDS default scope (self-extending).
    """
    if not args:
        return list(QENDS)
    want = []
    for a in args:
        if len(a) == 8 and a.isdigit():
            if a[4:] not in _VALID_MMDD:
                sys.exit(
                    f"[error] '{a}': not a quarter-end date. MMDD must be one of "
                    f"{sorted(_VALID_MMDD)} (got '{a[4:]}'). Pass an 8-digit "
                    f"YYYYMMDD quarter-end, e.g. 20260630."
                )
            want.append(a)
        elif len(a) == 4 and a.isdigit():
            yr_q = [q for q in QENDS if q[:4] == a]
            if not yr_q:
                sys.exit(
                    f"[error] year '{a}': outside the producible range "
                    f"{_QSTART_YEAR}..{_QEND_YEAR}. Extend QENDS or pass an 8-digit "
                    f"YYYYMMDD. (Refusing to fetch nothing silently.)"
                )
            want += yr_q
        else:
            sys.exit(
                f"[error] '{a}': not a valid period argument. Pass an 8-digit YYYYMMDD "
                f"quarter-end (e.g. 20260630) or a 4-digit year (e.g. 2026)."
            )
    targets = sorted(set(want))
    if not targets:
        sys.exit(
            "[error] arguments produced zero target periods -- refusing to run "
            "(would silently fetch nothing). Check your arguments."
        )
    return targets


def to_ymd(text: str) -> str | None:
    import re
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        return f"{m.group(3)}{int(m.group(1)):02d}{int(m.group(2)):02d}"
    m = re.search(r"(\d{4})[-/]?(\d{2})[-/]?(\d{2})", text)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else None


def select_product_and_format(pg) -> None:
    pg.select_option("select#ListBox1, select[name='ctl00$MainContentHolder$ListBox1']", value=PRODUCT)
    pg.wait_for_timeout(2800)
    pg.wait_for_selector(DD, timeout=20000)
    if USE_TSV:
        try:
            pg.check("input#TSVRadioButton", force=True, timeout=5000)
        except Exception:
            pass
        pg.wait_for_timeout(1500)
        print(f"[format] TSV checked = {pg.is_checked('input#TSVRadioButton')}")
    else:
        print("[format] XBRL (default; per-bank XML in ZIP) — TSV crashes headless renderer")


def read_period_map(pg) -> dict:
    opts = pg.eval_on_selector_all(
        DD + " option", "els => els.map(e => ({v:e.value, t:e.textContent.trim()}))")
    pm = {}
    for o in opts:
        ymd = to_ymd(o["t"])
        if ymd:
            pm[ymd] = o["v"]
    return pm


def download_period(pg, internal_value: str, ymd: str) -> int:
    pg.select_option(DD, value=internal_value)
    pg.wait_for_timeout(1800)
    with pg.expect_download(timeout=180000) as dlinfo:
        try:
            pg.click("a#Download_0, input#Download_0, "
                     "[name='ctl00$MainContentHolder$TabStrip1$Download_0']", timeout=8000)
        except Exception:
            pg.get_by_text("Download", exact=False).first.click(timeout=8000)
    dest = RAW / f"ubpr_single_{ymd}.zip"
    dlinfo.value.save_as(str(dest))
    return dest.stat().st_size


def main() -> int:
    targets = parse_targets(sys.argv[1:])  # validates args; ABORTS on bad/empty input
    targets = [q for q in targets if not (RAW / f"ubpr_single_{q}.zip").exists()
               or (RAW / f"ubpr_single_{q}.zip").stat().st_size < 1000]
    print(f"[plan] {len(targets)} UBPR period(s) -> {RAW}")
    if not targets:
        print("[done] nothing to fetch.")
        return 0

    got, failed = [], []
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=[
            "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
            "--js-flags=--max-old-space-size=4096"])
        ctx = br.new_context(accept_downloads=True)
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        pg.goto(URL, wait_until="networkidle")
        select_product_and_format(pg)
        pm = read_period_map(pg)
        print(f"[periods] {len(pm)} UBPR periods on CDR; newest -> {sorted(pm)[-6:]}")
        for ymd in targets:
            if ymd not in pm:
                print(f"[skip] {ymd}: not offered")
                failed.append((ymd, "not_offered"))
                continue
            ok = False
            for attempt in (1, 2, 3):
                try:
                    sz = download_period(pg, pm[ymd], ymd)
                    if sz > 1000:
                        print(f"[ok] {ymd}: {sz:,} bytes")
                        got.append((ymd, sz)); ok = True; break
                    print(f"[retry] {ymd}: {sz} bytes too small")
                except Exception as e:
                    print(f"[retry] {ymd}: {type(e).__name__}: {str(e)[:80]}")
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
    print(f"\n[summary] downloaded {len(got)}; failed {len(failed)}")
    if failed:
        print("  failed:", failed)
    return 0 if got else 2


if __name__ == "__main__":
    sys.exit(main())
