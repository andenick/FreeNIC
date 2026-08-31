"""P06: Export the public Parquet release + slice.

  12_export_parquet.py         base-table Parquet exports (ZSTD, sorted)
  12b_export_call_report_filings.py
  17_export_dict_parquet.py    dictionary Parquets
  15_generate_schedule_views.py + 16_coverage_audit.py  views/coverage (PASS gate)

The served release (root + reconstruction/ + SHA256SUMS + manifest) is then
staged by release-tools/ (build_slice.py, make_freenic_counts.py) per
release-tools/README.md and site/DATA_SERVING.md.

Usage: python anu/scripts/P06_export_release.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = [
    "12_export_parquet.py",
    "12b_export_call_report_filings.py",
    "17_export_dict_parquet.py",
    "15_generate_schedule_views.py",
    "16_coverage_audit.py",
]


def main() -> int:
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        rc |= bs.run_phase(ph)
    if rc == 0:
        print("\n[P06] export phases green. Stage the served release with "
              "release-tools/build_slice.py + make_freenic_counts.py, then "
              "validate with anu/scripts/V01_validate.py --remote.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
