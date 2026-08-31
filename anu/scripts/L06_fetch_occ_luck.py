"""L06: OCC historical + Luck historical database + finhist inputs.

The historical backbone inputs. None has a single keyless bulk URL; each is a
published research distribution, documented honestly (see DPR D09):

1. Luck historical call reports (balance sheets + income statements, Stata
   DTA) - Correia-Luck-Verner public dataset (FRBNY distribution):
     https://www.newyorkfed.org/research/banking_research/datasets.html
   Expected: anu/data/raw/luck_database/call-reports-*.dta
2. OCC historical TSV (digitized OCC Annual Report condition statements,
   1863-1941, distributed in the Luck database files):
     https://www.occ.gov/about/what-we-do/hist-publications/hist-publications-index.html
   Expected: anu/data/raw/luck_database/occ_historical/
3. finhist historical-call (CLV public vintage, Stata DTA):
     https://finhist.com  /  Harvard Dataverse doi:10.7910/DVN/Q22XR1
   Expected: anu/data/raw/clv_historical_call/historical-call.dta

Usage:
  python anu/scripts/L06_fetch_occ_luck.py --check
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

CHECKS = [
    ("luck_database/call-reports-*.dta (Luck call reports)",
     "luck_database", "call-reports-*.dta"),
    ("luck_database/occ_historical/ (OCC historical TSV + docs)",
     "luck_database/occ_historical", "*"),
    ("clv_historical_call/historical-call.dta (finhist)",
     "clv_historical_call", "historical-call.dta"),
]


def main(argv: list[str]) -> int:
    missing = 0
    for label, sub, pat in CHECKS:
        d = bs.RAW_DIR / sub
        hits = [h for h in d.glob(pat) if h.is_file()] if d.is_dir() else []
        n = len(hits)
        print(f"[L06] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    if missing:
        print(
            f"\n[L06] {missing} input group(s) missing. Acquisition points:\n"
            "  Luck DTA:     https://www.newyorkfed.org/research/banking_research/datasets.html\n"
            "  OCC digitized: https://www.occ.gov/about/what-we-do/hist-publications/hist-publications-index.html\n"
            "  finhist DTA:  https://finhist.com (Harvard Dataverse doi:10.7910/DVN/Q22XR1)\n"
            "  (also distributed inside the Luck database files; see DPR D09)")
        return 1
    print("[L06] historical backbone inputs present. "
          "Ingest with P02 (phases 08/08b/09/09b).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
