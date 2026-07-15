"""Find H.8 disagg series that the script expects but have no cache file (timed-out ones)."""
import json
import os
from pathlib import Path

INPUTS = Path(os.environ.get("FREENIC_INPUTS", "Inputs"))
CACHE = INPUTS / "fred_h8" / "disagg"
SERIES_JSON = INPUTS / "fred_h8" / "h8_release_series.json"

series = json.loads(SERIES_JSON.read_text())
print(f"release series listed: {len(series)}")

present = {p.stem for p in CACHE.glob("*.csv")}
print(f"disagg csv present: {len(present)}")

# A valid cache file per script 27b is >20 bytes. Flag tiny/empty too.
tiny = [p.stem for p in CACHE.glob("*.csv") if p.stat().st_size <= 20]
print(f"tiny(<=20B) cache files: {len(tiny)} {tiny[:10]}")

missing = sorted(set(series) - present)
print(f"MISSING (no cache file): {len(missing)}")
for sid in missing:
    print(f"  {sid}  ::  {series[sid][:70]}")

# also include tiny ones as needing refetch
need = sorted(set(missing) | set(tiny))
(Path(__file__).parent / "_taskA_missing.json").write_text(
    json.dumps({"missing": missing, "tiny": tiny, "need": need, "titles": {s: series[s] for s in need}})
)
print(f"\nTOTAL need refetch: {len(need)}")
