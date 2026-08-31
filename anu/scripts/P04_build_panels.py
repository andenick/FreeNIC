"""P04: Build the derived analysis panels.

  30_build_public_luck_panel.py  public luck-equivalent panel (OUTPUT_ROOT)
  31_build_sdi_feature_panel.py  (also in P02; idempotent)
  45_build_clean_bank_panel.py   canonical clean bank panel 1863-2026

Usage: python anu/scripts/P04_build_panels.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = [
    "30_build_public_luck_panel.py",
    "45_build_clean_bank_panel.py",
]


def main() -> int:
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        rc |= bs.run_phase(ph)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
