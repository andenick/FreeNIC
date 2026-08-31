"""L03: BHCF (FR Y-9C) bulk files + MDRM dictionary + Chicago Fed historical XPT.

Three inputs with three different acquisition stories (honest, no silent fallback):

1. BHCF TXT (2000-2025), caret-delimited - public bulk from FFIEC:
     https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx  (BHCF product)
   Expected under: anu/data/raw/ffiec_bulk_bhcf/BHCF*.txt
2. BHCF pre-2000 CSV vintage (1986-1999) - historical FFIEC/FRB distribution:
   place the CSVs under anu/data/raw/bhcf_csv_pre2000/
3. MDRM_CSV.csv - the Fed Micro Data Reference Manual, distributed with the
   FFIEC bulk products:
     https://www.federalreserve.gov/apps/mdrm/
   Expected at: anu/data/raw/ffiec_bulk_bhcf/MDRM_CSV.csv
4. Chicago Fed Commercial Bank Data XPT vintages (1976-2002 call reports) -
   a licensed/subscription FRB Chicago distribution:
     https://www.chicagofed.org/banking/financial-institution-reports-commercial-bank-data
   Expected under: anu/data/raw/chicago_fed_call_reports/call*-zip/

The repo does NOT redistribute any of these raw files. Reproducers with
public access run steps 1-3 keyless; step 4 requires the Chicago Fed product
(the public keyless era starts 2001+ at FFIEC CDR, and 1959-1975 is covered by
the public Luck/finhist files - see L06 and DPR D03).

Usage:
  python anu/scripts/L03_fetch_bhcf_mdrm.py --check
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

CHECKS = [
    ("ffiec_bulk_bhcf/BHCF*.txt (2000+ TXT vintage)", "ffiec_bulk_bhcf",
     "BHCF*.txt"),
    ("ffiec_bulk_bhcf/MDRM_CSV.csv", "ffiec_bulk_bhcf", "MDRM_CSV.csv"),
    ("bhcf_csv_pre2000/*.csv (1986-1999 vintage)", "bhcf_csv_pre2000", "*.csv"),
    ("chicago_fed_call_reports/call*-zip/ (1976-2002, licensed)",
     "chicago_fed_call_reports", "*"),
]


def main(argv: list[str]) -> int:
    missing = 0
    for label, sub, pat in CHECKS:
        d = bs.RAW_DIR / sub
        hits = list(d.glob(pat)) if d.is_dir() else []
        n = len(hits)
        print(f"[L03] {'OK  ' if n else 'MISS'} {label}: {n} file(s)")
        missing += 0 if n else 1
    if missing:
        print(
            f"\n[L03] {missing} input group(s) missing. Acquisition points:\n"
            "  BHCF TXT + MDRM (public):  https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx\n"
            "  MDRM (canonical):          https://www.federalreserve.gov/apps/mdrm/\n"
            "  Pre-2000 BHCF CSV vintage: FFIEC/FRB historical distribution (see D05)\n"
            "  Chicago Fed 1976-2002:     https://www.chicagofed.org/banking/financial-institution-reports-commercial-bank-data\n"
            "  (licensed product; public keyless Call Reports start 2001+ at CDR)")
        return 1
    print("[L03] all BHCF/MDRM/Chicago-Fed inputs present. "
          "Ingest with P02 (phases 01/04/05/07).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
