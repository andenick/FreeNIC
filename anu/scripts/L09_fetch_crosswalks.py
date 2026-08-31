"""L09: Market crosswalks - CRSP-FRB link, SEC EDGAR CIK, CFPB HMDA, GLEIF LEI.

1. CRSP-FRB PERMCO mapping CSVs - public NY Fed distribution:
     https://www.newyorkfed.org/research/banking_research/datasets.html
   Expected: anu/data/raw/crsp_frb_link/*.csv
2. SEC EDGAR CIK crosswalk - built live from public structured APIs by the
   canonical phase script:
     https://data.sec.gov/           -> delegates to 34_ingest_sec_edgar.py
3. CFPB HMDA institution-year summary - built live from the public Data
   Browser API:
     https://ffiec.cfpb.gov/data-browser/ -> delegates to 35_ingest_hmda.py
4. GLEIF Level-1 golden copy (US/ACTIVE) - public, CC BY 4.0:
     https://www.gleif.org/en/lei-data/gleif-golden-copy
   Expected: golden-copy CSV under anu/data/raw/gleif/

Usage:
  python anu/scripts/L09_fetch_crosswalks.py --check
  python anu/scripts/L09_fetch_crosswalks.py sec
  python anu/scripts/L09_fetch_crosswalks.py hmda
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402


def check() -> int:
    groups = [
        ("crsp_frb_link CSVs", "crsp_frb_link", "*.csv"),
        ("gleif golden copy", "gleif", "*.csv"),
        ("hmda API cache", "hmda", "*.json"),
    ]
    missing = 0
    for label, sub, pat in groups:
        d = bs.RAW_DIR / sub
        n = len(list(d.glob(pat))) if d.is_dir() else 0
        print(f"[L09] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    if missing:
        print("\n[L09] acquisition points:\n"
              "  CRSP-FRB: https://www.newyorkfed.org/research/banking_research/datasets.html\n"
              "  GLEIF:    https://www.gleif.org/en/lei-data/gleif-golden-copy\n"
              "  SEC/HMDA: run `sec` / `hmda` (live public API builds)")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    if not argv:
        print(__doc__)
        return 2
    bs.ensure_dirs()
    what = argv[0]
    if what == "sec":
        return bs.run_phase("34_ingest_sec_edgar.py")
    if what == "hmda":
        return bs.run_phase("35_ingest_hmda.py")
    print(f"[L09] unknown target {what}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
