"""L04: FFIEC NIC structure data + FR Y-15 snapshots.

1. NIC institution attributes (active/closed/branches/relationships/
   transformations CSVs) - public download page:
     https://www.ffiec.gov/npw/FinancialReport/DataDownload
   Expected under: anu/data/raw/nic_attributes/
   and NIC_Structure CSVs under: anu/data/raw/NIC_Structure/

2. FR Y-15 systemic-indicator snapshots - the listing page is JS-gated
   (Cloudflare), so the canonical acquirer drives a HEADED browser; the
   static CSV assets themselves download directly:
     https://www.ffiec.gov/npw/FinancialReport/FRY15Reports
   Delegates to pipeline/scripts/07h_acquire_y15.py.

Usage:
  python anu/scripts/L04_fetch_nic.py --check
  python anu/scripts/L04_fetch_nic.py y15
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402


def check() -> int:
    groups = [
        ("nic_attributes (CSV_ATTRIBUTES_* etc.)", "nic_attributes", "*.csv"),
        ("NIC_Structure", "NIC_Structure", "*.csv"),
        ("y15_bulk (FR Y-15 snapshots)", "y15_bulk", "*.csv"),
    ]
    missing = 0
    for label, sub, pat in groups:
        d = bs.RAW_DIR / sub
        n = len(list(d.glob(pat))) if d.is_dir() else 0
        print(f"[L04] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    if missing:
        print(
            "\n[L04] acquisition points:\n"
            "  NIC attributes: https://www.ffiec.gov/npw/FinancialReport/DataDownload\n"
            "  FR Y-15:        https://www.ffiec.gov/npw/FinancialReport/FRY15Reports\n"
            "                 (listing JS-gated; run `y15` to drive the headed-browser acquirer)")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    if not argv or argv[0] != "y15":
        print(__doc__)
        return 2
    bs.ensure_dirs()
    return bs.run_phase("07h_acquire_y15.py")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
