"""L07: NCUA 5300 credit-union call report bulk ZIPs.

Public quarterly bulk downloads (no auth):
  https://www.ncua.gov/analysis/credit-union-corporate-call-report-data

Expected under: anu/data/raw/ncua_5300/ (quarterly ZIPs + FOICU directory)

Usage:
  python anu/scripts/L07_fetch_ncua.py --check

Note: the download page links per-quarter ZIPs; the canonical pipeline ingests
whatever is placed under the raw dir (loaders are idempotent per period).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402


def main(argv: list[str]) -> int:
    d = bs.RAW_DIR / "ncua_5300"
    zips = list(d.glob("*.zip")) if d.is_dir() else []
    print(f"[L07] ncu_5300 bulk ZIPs: {len(zips)} file(s)")
    if not zips:
        print("[L07] MISS. Download quarterly ZIPs from:\n"
              "  https://www.ncua.gov/analysis/credit-union-corporate-call-report-data\n"
              "  place them in anu/data/raw/ncua_5300/")
        return 1
    print("[L07] present. Ingest with P02 (phase 26).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
