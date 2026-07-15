"""Fetch the timed-out H.8 disagg series to the same cache the ingest reads.
Cache: Inputs/fred_h8/disagg/<sid>.csv via keyless fredgraph.csv endpoint.
Robust against 504 gateway timeouts: per-series retry ladder with backoff."""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

INPUTS = Path(os.environ.get("FREENIC_INPUTS", "Inputs"))
CACHE = INPUTS / "fred_h8" / "disagg"
GRAPH = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
BACKOFFS = [3, 8, 15, 25, 40, 60, 90]  # seconds between attempts on 504/timeout

need = json.loads((Path(__file__).parent / "_taskA_missing.json").read_text())["need"]
print(f"to fetch: {need}", flush=True)


def fetch_one(sid):
    dest = CACHE / f"{sid}.csv"
    for attempt, wait in enumerate([0] + BACKOFFS):
        if wait:
            time.sleep(wait)
        req = urllib.request.Request(GRAPH.format(sid=sid), headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            text = data.decode("utf-8", "replace")
            lines = text.splitlines()
            ndata = sum(1 for ln in lines[1:] if "," in ln and ln.split(",")[1] not in (".", ""))
            if len(data) <= 20 or ndata == 0:
                print(f"  WARN {sid}: too small/empty ({len(data)}B,{ndata}rows) attempt{attempt+1}", flush=True)
                continue
            dest.write_bytes(data)
            print(f"  OK {sid}: {len(data):,}B, {ndata:,} obs, header={lines[0]!r} (attempt {attempt+1})", flush=True)
            return True
        except urllib.error.HTTPError as e:
            print(f"  .. {sid} attempt{attempt+1}: HTTP {e.code} (retry)", flush=True)
        except Exception as e:
            print(f"  .. {sid} attempt{attempt+1}: {type(e).__name__} {str(e)[:60]} (retry)", flush=True)
    print(f"  FAIL {sid}: exhausted retries", flush=True)
    return False


for sid in need:
    fetch_one(sid)
    time.sleep(1.0)

series = json.loads((INPUTS / "fred_h8" / "h8_release_series.json").read_text())
present = {p.stem for p in CACHE.glob("*.csv")}
missing_after = sorted(set(series) - present)
print(f"\nrelease={len(series)} present={len(present)} still_missing={len(missing_after)} {missing_after}", flush=True)
