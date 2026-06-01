"""W16 Phase 1B/1C panel materialization: build the public Luck-equivalent panel
(one row per rssd_id x period_end, validated aggregate columns) from
call_report_filings in a single conditional-aggregation scan. Era-aware recipes
in SQL. Writes data/correia/public_luck_panel.parquet."""

import duckdb
from pathlib import Path
from utils import DB_PATH

OUT = Path("D:/Arcanum/Projects/Volcker/Technical/AnuData/data/correia/"
           "public_luck_panel.parquet")
OUT_STR = str(OUT).replace("\\", "/")

# aggregate -> SQL value expression (era-aware where needed)
SEC = ("CASE WHEN period_end < DATE '1994-01-01' AND variable_id='RCFD0390' THEN value "
       "WHEN period_end >= DATE '1994-01-01' AND variable_id IN ('RCFD1754','RCFD1773') "
       "THEN value END")
FFS = ("CASE WHEN period_end < DATE '2002-01-01' AND variable_id='RCFD1350' THEN value "
       "WHEN period_end >= DATE '2002-01-01' AND variable_id='RCFDB987' THEN value END")
FFP = ("CASE WHEN period_end < DATE '2002-01-01' AND variable_id='RCFD2800' THEN value "
       "WHEN period_end >= DATE '2002-01-01' AND variable_id='RCFDB993' THEN value END")

def single(code):
    return f"CASE WHEN variable_id='{code}' THEN value END"

def multi(codes):
    inlist = ",".join(f"'{c}'" for c in codes)
    return f"CASE WHEN variable_id IN ({inlist}) THEN value END"

AGG_SQL = {
    "assets": single("RCFD2170"), "deposits": single("RCFD2200"),
    "equity": single("RCFD3210"), "cash": single("RCFD0010"),
    "ln_tot": single("RCFD2122"), "ln_re": single("RCFD1410"),
    "ln_ci": single("RCFD1766"), "ln_cons": single("RCFD1975"),
    "ln_agr": single("RCFD1590"), "demand_deposits": single("RCFD2210"),
    "domestic_dep": single("RCON2200"), "oreo": single("RCFD2150"),
    "llres": single("RCFD3123"), "surplus": single("RCFD3839"),
    "subdebt": single("RCFD3200"), "liab_tot": single("RCFD2948"),
    "securities": SEC, "time_deposits": multi(["RCON2604", "RCON6648"]),
    "npl_tot": multi(["RCFD1403", "RCFD1407"]), "ffsold": FFS, "ffpurch": FFP,
    "ytdint_inc": single("RIAD4107"), "ytdint_exp": single("RIAD4073"),
    "ytdnetinc": single("RIAD4340"), "ytdllprov": single("RIAD4230"),
}
# union of all MDRM codes referenced (for the WHERE filter)
ALL = ["RCFD2170","RCFD2200","RCFD3210","RCFD0010","RCFD2122","RCFD1410",
       "RCFD1766","RCFD1975","RCFD1590","RCFD2210","RCON2200","RCFD2150",
       "RCFD3123","RCFD3839","RCFD3200","RCFD2948","RCFD0390","RCFD1754",
       "RCFD1773","RCON2604","RCON6648","RCFD1403","RCFD1407","RCFD1350",
       "RCFDB987","RCFD2800","RCFDB993","RIAD4107","RIAD4073","RIAD4340","RIAD4230"]
inlist = ",".join(f"'{c}'" for c in ALL)

cols_sql = ",\n  ".join(f"SUM({expr}) AS {name}" for name, expr in AGG_SQL.items())
query = f"""
COPY (
  SELECT rssd_id, period_end,
  {cols_sql}
  FROM call_report_filings
  WHERE variable_id IN ({inlist})
  GROUP BY rssd_id, period_end
  ORDER BY rssd_id, period_end
) TO '{OUT_STR}' (FORMAT PARQUET, COMPRESSION ZSTD)
"""

con = duckdb.connect(str(DB_PATH), read_only=True)
print("Materializing public Luck-equivalent panel (single scan)...")
con.execute(query)
stats = duckdb.connect().execute(
    f"SELECT COUNT(*), COUNT(DISTINCT rssd_id), MIN(period_end), MAX(period_end), "
    f"COUNT(DISTINCT period_end) FROM read_parquet('{OUT_STR}')").fetchone()
size_mb = OUT.stat().st_size / (1024 ** 2)
con.close()
print(f"WROTE {OUT}")
print(f"  {stats[0]:,} rows | {stats[1]:,} entities | {stats[2]}..{stats[3]} "
      f"| {stats[4]} quarters | {size_mb:,.1f} MB")
print(f"  columns: {len(AGG_SQL)} aggregates + rssd_id + period_end")
