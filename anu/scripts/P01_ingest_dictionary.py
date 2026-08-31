"""P01: Ingest the variable dictionary layer.

Runs the canonical dictionary phases in order:
  01_ingest_mdrm.py            MDRM codes -> mdrm
  14_import_dictionary.py      pinned bank-data-dictionary -> dict_* tables
  44_build_variable_dictionary.py  harmonized variable dictionary

Usage: python anu/scripts/P01_ingest_dictionary.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = ["01_ingest_mdrm.py", "14_import_dictionary.py",
          "44_build_variable_dictionary.py"]


def main() -> int:
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        rc |= bs.run_phase(ph)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
