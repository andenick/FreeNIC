"""L02: Acquire FFIEC CDR public bulk products (Call Reports, UBPR, unrealized losses).

The FFIEC Central Data Repository serves public bulk ZIPs (no auth):
  https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx
  - Call Reports -- Single Period (tab-delimited ZIP per quarter)
  - UBPR Ratio -- Single Period (tab-delimited ZIP per quarter)
  - UBPR Rank / Peer Stats -- Four Periods (XBRL ZIP per year)
  - BHCF (FR Y-9C) bulk files

The download UI is a Telerik RadAjax partial-postback flow, so the canonical
acquisition scripts drive it with Playwright. This loader delegates to them:

  07d_acquire_cdr_call_bulk.py 20260630   -> cdr_call_bulk/call_single_*.zip
  07g_acquire_ubpr.py 20260630           -> ubpr_bulk/ubpr_single_*.zip
  07i_acquire_ubpr_peer.py rank 2025     -> ubpr_rank_bulk/  ubpr_stats_bulk/
  32_acquire_cdr_unrealized.py           -> cdr_raw/

Usage:
  python anu/scripts/L02_fetch_ffiec_cdr.py --check
  python anu/scripts/L02_fetch_ffiec_cdr.py call 20260630
  python anu/scripts/L02_fetch_ffiec_cdr.py ubpr 20260630
  python anu/scripts/L02_fetch_ffiec_cdr.py peer rank 2025
  python anu/scripts/L02_fetch_ffiec_cdr.py peer stats 2024 2025
  python anu/scripts/L02_fetch_ffiec_cdr.py unrealized

Prereq: playwright + `playwright install chromium` (see anu/requirements.txt).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402


def check() -> int:
    targets = [
        ("cdr_call_bulk", "cdr_call_bulk", "call_single_*.zip"),
        ("ubpr_bulk", "ubpr_bulk", "ubpr_single_*.zip"),
        ("ubpr_rank", "ubpr_rank_bulk", "*.zip"),
        ("ubpr_stats", "ubpr_stats_bulk", "*.zip"),
        ("cdr_raw (unrealized)", "cdr_raw", "*.zip"),
    ]
    missing = 0
    for label, sub, pat in targets:
        d = bs.RAW_DIR / sub
        n = len(list(d.glob(pat))) if d.is_dir() else 0
        print(f"[L02] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    print(f"[L02] check: {missing} missing")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    if not argv:
        print(__doc__)
        return 2
    bs.ensure_dirs()
    what, rest = argv[0], argv[1:]
    if what == "call":
        return bs.run_phase("07d_acquire_cdr_call_bulk.py", *rest)
    if what == "ubpr":
        return bs.run_phase("07g_acquire_ubpr.py", *rest)
    if what == "peer":
        return bs.run_phase("07i_acquire_ubpr_peer.py", *rest)
    if what == "unrealized":
        return bs.run_phase("32_acquire_cdr_unrealized.py", *rest)
    print(f"[L02] unknown product {what}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
