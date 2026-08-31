"""L08: Supervisory sources - DFAST results, stress scenarios, Pillar 3.

1. DFAST results CSVs (2013-2025 cumulative file) - public:
     https://www.federalreserve.gov/supervisionreg/dfast-archive.htm
   Expected: anu/data/raw/dfast/public_results_DFAST_*.csv
2. Supervisory stress scenario definitions - public CSVs:
     https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm
   Expected: anu/data/raw/stress_scenarios/*.csv
3. G-SIB Pillar 3 disclosures - HAND-COLLECTED from five banks' investor
   relations pages (JPM, BAC, WFC, C, MS). No bulk source exists; the
   disclosure documents are public but transcription is manual (DPR D12):
     https://www.bis.org/bcbs/pillar3.htm (framework)
   Expected: transcribed CSVs (see pipeline/scripts/24_ingest_pillar3.py)

Usage:
  python anu/scripts/L08_fetch_supervisory.py --check
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

CHECKS = [
    ("dfast results CSVs", "dfast", "*DFAST*.csv"),
    ("stress_scenarios CSVs", "stress_scenarios", "*.csv"),
    ("pillar3 transcribed CSVs (manual layer)", "pillar3", "*.csv"),
]


def main(argv: list[str]) -> int:
    missing = 0
    for label, sub, pat in CHECKS:
        d = bs.RAW_DIR / sub
        n = len(list(d.glob(pat))) if d.is_dir() else 0
        print(f"[L08] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    if missing:
        print(
            f"\n[L08] {missing} group(s) missing. Acquisition points:\n"
            "  DFAST:     https://www.federalreserve.gov/supervisionreg/dfast-archive.htm\n"
            "  Scenarios: https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm\n"
            "  Pillar 3:  bank IR pages (manual transcription; no bulk source - D12)")
        return 1
    print("[L08] supervisory inputs present. Ingest with P02 (phases 23/24/30).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
