"""W16 Phase 1B/1C panel materialization: build the public Luck-equivalent panel
(one row per rssd_id x period_end, validated aggregate columns) from
call_report_filings in a single conditional-aggregation scan. Era-aware recipes
in SQL. Writes data/correia/public_luck_panel.parquet.

-----------------------------------------------------------------------------
A2 RECIPE-FIDELITY SPEC (2026-06-05; from D1 reconciliation + Luck data dictionary)
-----------------------------------------------------------------------------
D1 (Technical/coverage_analysis/d1_reconcile) showed 21/25 mapped vars reconcile >=99%
vs Luck; 4 under-reconcile due to RECIPE (not data) gaps. Corrections needed for exact
Luck parity (no underlying MDRM is missing from call_report_filings):

1. COMPLETENESS (all single-code aggregates): prefer consolidated RCFD, fall back to
   domestic-only RCON for banks that file domestic-only forms (FFIEC 034/041). Pattern:
   COALESCE(MAX(CASE WHEN variable_id='RCFD####' THEN value END),
            MAX(CASE WHEN variable_id='RCON####' THEN value END)).
   (This fills the large per-variable "luck_only" null counts from small domestic banks;
    it does not change the already->=99% agreement among both-non-null cells.)

2. securities: Luck = "Total Securities", multi-component & form-dependent across eras
   (e.g. RCON 0400+0600+0900+0950 for 1959Q4-1969Q2; later RCFD0390; post-1994
   RCFD1754+RCFD1773). Add RCON twins; the exact multi-era chain is in the Luck do-file
   3-create-variables.do.

3. time_deposits: Luck = RCON2514 ("Total Time Deposits") for 1961Q1-1984Q1; the current
   recipe RCON2604+RCON6648 is a later-era construction. Make era-aware: pre-1984 -> RCON2514.

4. ffsold / ffpurch: DEFINITIONAL mismatch. Luck "ffsold"=RCFD0276 / "ffpurch"=RCFD0278
   (PURE fed funds, 1988Q1-1997Q1), whereas this script's RCFD1350 / RCFD2800 are Luck's
   COMBINED "ffrepo_ass" / "ffrepo_liab" (fed funds + repos, 1965-2002). Either rename these
   columns to ffrepo_ass/ffrepo_liab, or switch to 0276/0278 for the pure series.

STATUS: IMPLEMENTED 2026-06-05. Items 1 (COALESCE RCFD/RCON), 3 (time_deposits era), and 4
(pure ff RCFD0276/0278) are now in AGG_SQL below and VERIFIED (coverage_analysis/d1b_reconcile.json:
24/25 vars >=99%; time_deposits 60->99.99%, ffsold/ffpurch ->100%; overall 99.70%). RESIDUAL: `securities` ~94% overall for 1976+ — EMPIRICALLY characterized 2026-06-07
(coverage_analysis/step1_securities_empirical.json): post-1994 = 99.96% (the current 1754+1773 recipe
is optimal — 5 variants tested, none better); the residual is entirely PRE-1994 = 86.81%, concentrated
in the pre-1984 FFIEC-010/011 form era. The upstream raw-MDRM construction do-file is NOT in the public
CC0 QJE repkit (Dataverse 10.7910/DVN/Q22XR1 ships only analysis code; `securities` is pre-built in the
distributed .dta). So ~94% is the public-data CEILING; no recipe change improves it. Documented, not a defect.
-----------------------------------------------------------------------------
"""

import duckdb
from utils import DB_PATH, OUTPUT_ROOT

OUT = OUTPUT_ROOT / "public_luck_panel.parquet"
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT_STR = str(OUT).replace("\\", "/")

# aggregate -> SQL value expression. IMPROVED 2026-06-05 (A2), verified vs Luck in
# coverage_analysis/d1b_reconcile.json: 24/25 vars reconcile >=99% (was 21/25).
# Pattern: prefer consolidated RCFD, fall back to domestic-only RCON (cf); era-aware
# securities & time_deposits; PURE fed-funds codes RCFD0276/0278 to match Luck's
# ffsold/ffpurch (the old RCFD1350/2800 were Luck's COMBINED ffrepo_ass/ffrepo_liab).
# period_end is a GROUP BY key, so it is usable inside the CASE.
def cf(code):  # COALESCE(consolidated RCFD, domestic-only RCON)
    return (f"COALESCE(MAX(CASE WHEN variable_id='RCFD{code}' THEN value END), "
            f"MAX(CASE WHEN variable_id='RCON{code}' THEN value END))")

def riad(code):
    return f"MAX(CASE WHEN variable_id='RIAD{code}' THEN value END)"

AGG_SQL = {
    "assets": cf("2170"), "deposits": cf("2200"), "equity": cf("3210"), "cash": cf("0010"),
    "ln_tot": cf("2122"), "ln_re": cf("1410"), "ln_ci": cf("1766"), "ln_cons": cf("1975"),
    "ln_agr": cf("1590"), "demand_deposits": cf("2210"),
    "domestic_dep": "MAX(CASE WHEN variable_id='RCON2200' THEN value END)",
    "oreo": cf("2150"), "llres": cf("3123"), "surplus": cf("3839"), "subdebt": cf("3200"),
    "liab_tot": cf("2948"),
    "securities": f"CASE WHEN period_end < DATE '1994-01-01' THEN {cf('0390')} ELSE {cf('1754')}+{cf('1773')} END",
    "time_deposits": f"CASE WHEN period_end < DATE '1984-01-01' THEN {cf('2514')} ELSE {cf('2604')}+{cf('6648')} END",
    "npl_tot": f"{cf('1403')}+{cf('1407')}",
    "ffsold": cf("0276"), "ffpurch": cf("0278"),
    "ytdint_inc": riad("4107"), "ytdint_exp": riad("4073"),
    "ytdnetinc": riad("4340"), "ytdllprov": riad("4230"),
}
# RESIDUAL: securities ~94% vs Luck for 1976+ (Luck's multi-component historical
# construction needs the Luck do-files); all other 24 aggregates reconcile >=99%.
_NUM = ["2170","2200","3210","0010","2122","1410","1766","1975","1590","2210","2150",
        "3123","3839","3200","2948","0390","1754","1773","2514","2604","6648","1403","1407","0276","0278"]
ALL = sorted(set([f"RCFD{c}" for c in _NUM] + [f"RCON{c}" for c in _NUM] +
                 ["RCON2200", "RIAD4107", "RIAD4073", "RIAD4340", "RIAD4230"]))
inlist = ",".join(f"'{c}'" for c in ALL)

# expressions are already aggregates (MAX/COALESCE) -> no outer SUM()
cols_sql = ",\n  ".join(f"{expr} AS {name}" for name, expr in AGG_SQL.items())
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
