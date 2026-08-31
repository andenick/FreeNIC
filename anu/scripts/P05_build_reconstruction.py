"""P05: Build the reconstruction layer (Luck / finhist rebuilds).

Wraps the verified pipeline/reconstruction module:
  50_reconstruct_luck.py    Luck core 1959-1975 + luck-equivalent 1976-2026
  51_reconstruct_finhist.py finhist-equivalent 1863-1941
Cell-level reconciliation panels and gate JSONs are emitted alongside.

Note: the modern-era (1976-2026) reconstruction's pre-registered verdict is
FAIL at the strictest tier - a documented, honest divergence record, not a
hidden one. See pipeline/reconstruction/reports/ and DPR D15.

Usage: python anu/scripts/P05_build_reconstruction.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = ["50_reconstruct_luck.py", "51_reconstruct_finhist.py"]


def main() -> int:
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        rc |= bs.run_phase(ph)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
