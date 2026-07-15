"""W16 task #2 — scrounger diagnosis of the missing/unreadable XPT quarters.
Read-only: identify which 1976Q1-2011Q4 quarters are absent from the DB, locate
their callYYMM XPT, and attempt to read each (utf-8 -> latin1 -> header probe).
Classify per the Scrounger Standard: RECOVERABLE / DUPLICATE / QUARANTINE."""

import re
from pathlib import Path
import duckdb
import pyreadstat
from utils import DB_PATH, INPUT_PATHS

CALL_DIR = INPUT_PATHS["call_reports"]
QEND = {"03": "31", "06": "30", "09": "30", "12": "31"}

def period_from_dirname(name):
    m = re.match(r"call(\d{2})(\d{2})", name)
    if not m:
        return None
    yy, mm = m.group(1), m.group(2)
    if mm not in QEND:
        return None
    yy_i = int(yy)
    year = 2000 + yy_i if yy_i <= 30 else 1900 + yy_i
    return f"{year}-{mm}-{QEND[mm]}"

con = duckdb.connect(str(DB_PATH), read_only=True)
loaded = {str(r[0]) for r in con.execute(
    "SELECT DISTINCT period_end FROM call_report_filings").fetchall()}
con.close()

expected = [f"{y}-{mm}-{QEND[mm]}" for y in range(1976, 2012) for mm in ("03","06","09","12")]
missing = sorted(set(expected) - loaded)
print(f"Loaded quarters: {len(loaded)} | expected 1976Q1-2011Q4: {len(expected)} "
      f"| MISSING: {len(missing)}")
print(f"Missing quarters: {missing}\n")

# Map dirs to periods; find dirs covering missing quarters
dirs = sorted(d for d in CALL_DIR.iterdir()
              if d.is_dir() and d.name.startswith("call") and d.name.endswith("-zip"))
by_period = {}
for d in dirs:
    pe = period_from_dirname(d.name)
    by_period.setdefault(pe, []).append(d)

print("=== Diagnosing dirs for each MISSING quarter ===")
recoverable, quarantine, nodir = [], [], []
for pe in missing:
    ds = by_period.get(pe, [])
    if not ds:
        nodir.append(pe)
        print(f"\n{pe}: NO callYYMM dir on disk (genuinely absent source)")
        continue
    for d in ds:
        xpts = list(d.glob("*.xpt"))
        if not xpts:
            print(f"\n{pe} [{d.name}]: no .xpt in dir")
            quarantine.append((pe, d.name, "no xpt file"))
            continue
        xp = xpts[0]
        size_mb = xp.stat().st_size / (1024**2)
        status = None
        for enc in (None, "LATIN1"):
            try:
                kw = {"encoding": enc} if enc else {}
                df, meta = pyreadstat.read_xport(str(xp), **kw)
                status = f"READABLE enc={enc or 'utf8'}: {len(df):,} rows, {len(df.columns)} cols"
                recoverable.append((pe, d.name, xp.name, enc, len(df), len(df.columns)))
                break
            except Exception as e:
                status = f"FAIL enc={enc or 'utf8'}: {type(e).__name__}: {str(e)[:90]}"
        print(f"\n{pe} [{d.name}] {xp.name} ({size_mb:.1f} MB): {status}")

print("\n=== Scrounger classification ===")
print(f"  RECOVERABLE (readable, was wrongly skipped): {len(recoverable)}")
for r in recoverable:
    print(f"    {r[0]} {r[2]} enc={r[3] or 'utf8'} -> {r[4]:,} rows x {r[5]} cols")
print(f"  NO SOURCE DIR (quarter never downloaded): {len(nodir)} -> {nodir}")
print(f"  QUARANTINE (dir present, unreadable): {len(quarantine)} -> {quarantine}")
