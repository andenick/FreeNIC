"""Phase 27b: Ingest the FULL FRED H.8 release (disaggregated by bank type).

27_ingest_fed_h8.py loads 15 aggregate series (keyless CSV). This script adds the COMPLETE
H.8 release (FRED release_id=22, ~1,938 series) — the large-domestic / small-domestic /
foreign-related / domestically-chartered breakdowns that need the FRED API key.

Key: read at runtime from the FRED_API_KEY environment variable (or a keys file pointed to by
FREENIC_KEYS_ENV); never hard-coded/committed. Observations cached per series
(Inputs/fred_h8/disagg/<id>.json) so
the run is idempotent + resumable. APPENDS to fred_series; idempotent on its own series set
(deletes only the H.8-release series_ids it manages before re-insert). NO values fabricated.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUTS_DIR

# A keys.env-style file with a `fred...=<32-char key>` line. Set via env var.
KEY_ENV = Path(os.environ.get("FREENIC_KEYS_ENV", "keys.env"))
CACHE = INPUTS_DIR / "fred_h8" / "disagg"
CACHE.mkdir(parents=True, exist_ok=True)
RELEASE_ID = 22  # H.8 Assets and Liabilities of Commercial Banks
API = "https://api.stlouisfed.org/fred"
GRAPH = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"  # keyless obs download
WORKERS = 4
FETCH_SLEEP = 0.3


def fred_key() -> str:
    # Prefer the FRED_API_KEY environment variable; fall back to a keys file.
    env_key = os.environ.get("FRED_API_KEY", "").strip()
    if env_key:
        return env_key
    if not KEY_ENV.exists():
        raise RuntimeError(
            "Set FRED_API_KEY (or point FREENIC_KEYS_ENV at a keys file); "
            f"no key file at {KEY_ENV}"
        )
    m = re.search(r'fred[^=]*=\s*"?([A-Za-z0-9]{32})', KEY_ENV.read_text(errors="replace"), re.I)
    if not m:
        raise RuntimeError(f"FRED key not found in {KEY_ENV}")
    return m.group(1)


SERIES_CACHE = INPUTS_DIR / "fred_h8" / "h8_release_series.json"


def _get(url, raw=False, attempts=6, backoff=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (freenic/1.0)"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < attempts:
                time.sleep(backoff * attempt)  # patient back-off on rate-limit ban
                continue
            raise


def enumerate_series(key):
    """All series_id -> title in the H.8 release. Cached once (h8_release_series.json) so the
    API key is hit only until the first success, then never again."""
    if SERIES_CACHE.exists() and SERIES_CACHE.stat().st_size > 100:
        return json.loads(SERIES_CACHE.read_text())
    out = {}
    offset = 0
    while True:
        j = _get(f"{API}/release/series?release_id={RELEASE_ID}&api_key={key}"
                 f"&file_type=json&limit=1000&offset={offset}")
        for s in j["seriess"]:
            out[s["id"]] = s["title"]
        offset += 1000
        if offset >= j["count"]:
            break
    SERIES_CACHE.write_text(json.dumps(out))
    return out


# Set by main() so fetch_obs can fall back to the API host when the keyless
# graph host (fred.stlouisfed.org/graph) is throttled/timing out.
_API_KEY = None


def _parse_obs_csv(text, sid):
    rows = []
    for ln in text.splitlines()[1:]:  # skip header (observation_date,<sid>)
        parts = ln.split(",")
        if len(parts) < 2:
            continue
        d, v = parts[0], parts[1]
        if v in (".", "", None):
            continue
        try:
            rows.append((d, float(v)))
        except ValueError:
            continue
    return rows


def _fetch_obs_api(sid):
    """Fallback: fetch observations from the API host (api.stlouisfed.org) with
    the key. The keyless graph host throttles/times out under load even though
    the API host stays responsive (observed 2026-06-10 for 4 H.8 series)."""
    j = _get(f"{API}/series/observations?series_id={sid}&api_key={_API_KEY}&file_type=json")
    return [(o["date"], float(o["value"]))
            for o in j.get("observations", []) if o.get("value", ".") not in (".", "")]


def fetch_obs(sid):
    """Download + cache one series' observations. Prefers the KEYLESS fredgraph.csv
    endpoint; on any transport failure falls back to the keyed API host."""
    cache = CACHE / f"{sid}.csv"
    if cache.exists() and cache.stat().st_size > 20:
        return sid, _parse_obs_csv(cache.read_text(errors="replace"), sid)
    try:
        text = _get(GRAPH.format(sid=sid), raw=True).decode("utf-8", "replace")
        rows = _parse_obs_csv(text, sid)
        cache.write_text(text)
        time.sleep(FETCH_SLEEP)
        return sid, rows
    except Exception:
        if not _API_KEY:
            raise
        rows = _fetch_obs_api(sid)  # graph host throttled -> API fallback
        # cache in the same CSV shape so the run stays resumable
        cache.write_text(f"observation_date,{sid}\n" + "\n".join(f"{d},{v}" for d, v in rows))
        time.sleep(FETCH_SLEEP)
        return sid, rows


def main():
    elapsed = timer()
    print("=== Phase 27b: full FRED H.8 release (disaggregated by bank type) ===")
    key = fred_key()
    global _API_KEY
    _API_KEY = key  # enable fetch_obs's API-host fallback for throttled graph fetches
    print("  FRED key loaded from Robin (not shown)")
    series = enumerate_series(key)
    print(f"  H.8 release series: {len(series):,}")

    # fetch observations concurrently (cached -> resumable)
    results = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch_obs, sid): sid for sid in series}
        done = 0
        for fut in as_completed(futs):
            try:
                sid, rows = fut.result()
                results[sid] = rows
            except Exception as e:
                print(f"    [warn] {futs[fut]}: {type(e).__name__} {str(e)[:50]}")
            done += 1
            if done % 300 == 0:
                print(f"    ...{done:,}/{len(series):,} series fetched")

    con = get_db()
    con.execute("""CREATE TABLE IF NOT EXISTS fred_series (
        series_id VARCHAR, observation_date DATE, value DOUBLE, series_name VARCHAR)""")
    # idempotent on this script's own series set
    ids = list(results.keys())
    con.execute("CREATE OR REPLACE TEMP TABLE _h8ids AS SELECT UNNEST(?) AS sid", [ids])
    con.execute("DELETE FROM fred_series WHERE series_id IN (SELECT sid FROM _h8ids)")
    insert = []
    for sid, rows in results.items():
        nm = series.get(sid, sid)[:250]
        for d, v in rows:
            insert.append((sid, d, v, nm))
    # bulk insert via DataFrame
    import pandas as pd
    df = pd.DataFrame(insert, columns=["series_id", "observation_date", "value", "series_name"])
    con.register("h8_df", df)
    con.execute("INSERT INTO fred_series SELECT series_id, CAST(observation_date AS DATE), value, series_name FROM h8_df")
    con.unregister("h8_df")
    con.execute("CHECKPOINT")
    tot = con.execute("SELECT COUNT(*) FROM fred_series").fetchone()[0]
    ns = con.execute("SELECT COUNT(DISTINCT series_id) FROM fred_series").fetchone()[0]
    print(f"\n  fred_series now: {tot:,} rows | {ns:,} distinct series (incl. {len(results):,} H.8 disagg)")
    # re-export parquet
    from utils import OUTPUTS_DIR
    out = (OUTPUTS_DIR / "parquet" / "fred_series.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM fred_series ORDER BY series_id, observation_date) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  parquet={pq:,} parity={'OK' if pq==tot else 'MISMATCH'}")
    con.close()
    log_ingestion("27b", f"FRED H.8 disaggregated: +{len(results):,} series; fred_series now {tot:,} rows / {ns:,} series. {elapsed():.1f}s")
    print(f"\nPhase 27b complete in {elapsed():.1f}s.")


if __name__ == "__main__":
    main()
