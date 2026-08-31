"""L05: Fetch FRED banking + macro series (keyless tier).

Mirrors pipeline/scripts/27_ingest_fed_h8.py exactly: 15 aggregate series
(H.8 bank credit/loans/deposits, key rates, macro context) via the keyless
fredgraph.csv endpoint.

The FULL disaggregated H.8 release (~1,938 series by bank size/type, phases
27b) needs a free FRED API key: set FRED_API_KEY and run P02 phase 27b.

Usage:
  python anu/scripts/L05_fetch_fred.py           # fetch all 15 keyless CSVs
  python anu/scripts/L05_fetch_fred.py --check
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# Same set, order, and labels as pipeline/scripts/27_ingest_fed_h8.py.
H8_SERIES = {
    "TOTBKCR": "Total bank credit, all commercial banks",
    "BUSLOANS": "Commercial and industrial loans, all commercial banks",
    "CONSUMER": "Consumer loans, all commercial banks",
    "REALLN": "Real estate loans, all commercial banks",
    "TOTLL": "Total loans and leases, all commercial banks",
    "DPSACBW027SBOG": "Deposits, all commercial banks (weekly)",
    "FEDFUNDS": "Federal funds effective rate",
    "DPRIME": "Bank prime loan rate",
    "MORTGAGE30US": "30-year fixed-rate mortgage average",
    "T10Y2Y": "10-Year Treasury minus 2-Year (yield curve)",
    "DFF": "Federal funds rate (daily)",
    "GDPC1": "Real GDP (quarterly)",
    "UNRATE": "Unemployment rate",
    "CPIAUCSL": "Consumer Price Index",
    "INDPRO": "Industrial Production Index",
}


def fetch(dest_dir: Path) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for sid, label in H8_SERIES.items():
        out = dest_dir / f"{sid}.csv"
        req = urllib.request.Request(CSV_URL.format(series_id=sid),
                                     headers={"User-Agent": "freenic-anu/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            out.write_bytes(body)
            ok += 1
            print(f"[L05] {sid}.csv  ({label}) - {len(body):,} bytes")
        except Exception as exc:  # noqa: BLE001
            print(f"[L05] FAIL {sid}: {exc}", file=sys.stderr)
    return ok


def main(argv: list[str]) -> int:
    dest = bs.RAW_DIR / "fred_h8"
    if "--check" in argv:
        missing = [s for s in H8_SERIES if not (dest / f"{s}.csv").exists()]
        for s in H8_SERIES:
            ok = (dest / f"{s}.csv").exists()
            print(f"[L05] {'OK  ' if ok else 'MISS'} {s}")
        print(f"[L05] check: {len(missing)} missing")
        return 1 if missing else 0
    bs.ensure_dirs()
    n = fetch(dest)
    print(f"[L05] {n}/{len(H8_SERIES)} series -> anu/data/raw/fred_h8/. "
          "Ingest with P02 (phase 27). For the full H.8 release set FRED_API_KEY "
          "and run P02 phase 27b.")
    return 0 if n == len(H8_SERIES) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
