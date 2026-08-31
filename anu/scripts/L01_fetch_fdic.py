"""L01: Fetch FDIC BankFind Suite data (failures, financials, history, SOD).

All four endpoints are public, keyless JSON APIs:
  failures   https://api.fdic.gov/banks/failures          -> fdic_failures_api.json
  financials https://api.fdic.gov/banks/financials        -> fdic_financials/page_NNNN.json
  history    https://api.fdic.gov/banks/history           -> fdic_history/page_NNNN.json
  sod        https://banks.data.fdic.gov/api/sod          -> fdic_sod/page_NNNN.json

Usage:
  python anu/scripts/L01_fetch_fdic.py            # fetch all four
  python anu/scripts/L01_fetch_fdic.py failures   # fetch one
  python anu/scripts/L01_fetch_fdic.py --check    # verify caches exist, no download

Volumes: financials is the heavy one (~168 pages x 10k records, 1.67M rows).
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

UA = {"User-Agent": "freenic-anu-replication/1.0"}

ENDPOINTS = {
    "failures": {
        "url": "https://api.fdic.gov/banks/failures",
        "dest": "fdic_failures_api.json", "single": True,
    },
    "financials": {
        "url": "https://api.fdic.gov/banks/financials",
        "dest": "fdic_financials", "single": False,
    },
    "history": {
        "url": "https://api.fdic.gov/banks/history",
        "dest": "fdic_history", "single": False,
    },
    "sod": {
        "url": "https://banks.data.fdic.gov/api/sod",
        "dest": "fdic_sod", "single": False,
    },
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def fetch_single(url: str, dest: Path) -> int:
    data = get_json(f"{url}?limit=10000")
    total = data.get("totals", {}).get("count", len(data.get("data", [])))
    dest.write_text(json.dumps(data), encoding="utf-8")
    print(f"[L01] {dest.name}: {total} records")
    return total


def fetch_paginated(url: str, dest_dir: Path, max_pages: int | None = None) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    page = 0
    got = 0
    while True:
        offset = page * 10000
        q = urllib.parse.urlencode({"limit": 10000, "offset": offset})
        data = get_json(f"{url}?{q}")
        rows = data.get("data", [])
        if not rows:
            break
        out = dest_dir / f"page_{page:04d}.json"
        out.write_text(json.dumps(data), encoding="utf-8")
        got += len(rows)
        print(f"[L01] {dest_dir.name}/page_{page:04d}.json: {len(rows)} records "
              f"(cumulative {got})")
        page += 1
        if max_pages and page >= max_pages:
            break
        if len(rows) < 10000:
            break
    return got


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    argv = [a for a in argv if not a.startswith("--")]
    targets = argv or list(ENDPOINTS)
    bs.ensure_dirs()
    failures = 0
    for t in targets:
        if t not in ENDPOINTS:
            print(f"[L01] unknown target {t}", file=sys.stderr)
            return 2
        ep = ENDPOINTS[t]
        if ep["single"]:
            dest = bs.RAW_DIR / ep["dest"]
        else:
            dest = bs.RAW_DIR / ep["dest"]
        if check_only:
            ok = (dest.exists() if ep["single"]
                  else dest.is_dir() and any(dest.glob("page_*.json")))
            print(f"[L01] {'OK  ' if ok else 'MISS'} {ep['dest']}")
            failures += 0 if ok else 1
            continue
        if ep["single"]:
            fetch_single(ep["url"], dest)
        else:
            n = fetch_paginated(ep["url"], dest)
            print(f"[L01] {t}: {n} records -> anu/data/raw/{ep['dest']}/")
    if check_only:
        print(f"[L01] check: {failures} missing")
        return 1 if failures else 0
    print("[L01] done. Ingest with P02 (phases 16/17/18+19/25).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
