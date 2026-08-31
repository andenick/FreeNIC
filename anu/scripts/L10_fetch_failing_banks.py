"""L10: Failing Banks panel (Correia-Luck-Verner repackaging).

Source repository (public): https://github.com/andenick/failing-banks

The repo hosts the R analysis, conversion scripts, and documentation. The
processed CSVs ingested by phase 28 are:
  FAILING_BANKS/processed/combined_data.csv                (2.87M bank-years)
  FAILING_BANKS/processed/deposits_before_failure_historical.csv
  FAILING_BANKS/processed/deposits_before_failure_modern.csv
plus the catalog CSVs (bank_identifier_crosswalk, bhc_hierarchy,
sector_groupings) ingested by phase 29.

Regeneration path: clone the source repo and run its conversion scripts
(convert_data_simple.py) against the Correia-Luck-Verner replication files,
or obtain the processed export from the repository maintainer. The underlying
authors' historical data is public (finhist, doi:10.7910/DVN/Q22XR1).

Usage:
  python anu/scripts/L10_fetch_failing_banks.py --check
  python anu/scripts/L10_fetch_failing_banks.py clone [DEST]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

REPO_URL = "https://github.com/andenick/failing-banks"
NEEDED = [
    "failing_banks/FAILING_BANKS/processed/combined_data.csv",
    "failing_banks/FAILING_BANKS/processed/deposits_before_failure_historical.csv",
    "failing_banks/FAILING_BANKS/processed/deposits_before_failure_modern.csv",
    "catalogs/bank_identifier_crosswalk.csv",
    "catalogs/bhc_hierarchy.csv",
    "catalogs/sector_groupings.csv",
]


def main(argv: list[str]) -> int:
    if "--check" in argv:
        missing = [p for p in NEEDED if not (bs.RAW_DIR / p).exists()]
        for p in NEEDED:
            print(f"[L10] {'OK  ' if p not in missing else 'MISS'} {p}")
        if missing:
            print(f"\n[L10] {len(missing)} missing. Source: {REPO_URL}")
            return 1
        return 0
    if argv and argv[0] == "clone":
        dest = Path(argv[1]) if len(argv) > 1 else bs.RAW_DIR / "failing-banks-repo"
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"[L10] cloning {REPO_URL} -> {dest}")
        return subprocess.run(["git", "clone", REPO_URL, str(dest)]).returncode
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
