"""P03: Build catalogs, crosswalks, provenance, self-description, coverage.

Runs after P02, once the raw sources are ingested:
  10_build_catalog.py       variable catalog
  20_build_crosswalks.py    cross-vintage variable crosswalk
  20b_build_entity_xref.py  entity cross-reference
  36_build_id_crosswalk.py  unified identifier crosswalk
  46_provenance_finalize.py provenance records
  47_self_describing.py     warehouse self-manifest
  48_footgun_guards.py      integrity guards
  49_coverage_matrix.py     coverage catalogs

Usage: python anu/scripts/P03_build_catalogs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = [
    "10_build_catalog.py",
    "20_build_crosswalks.py",
    "20b_build_entity_xref.py",
    "36_build_id_crosswalk.py",
    "46_provenance_finalize.py",
    "47_self_describing.py",
    "48_footgun_guards.py",
    "49_coverage_matrix.py",
]


def main() -> int:
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        rc |= bs.run_phase(ph)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
