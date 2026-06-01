"""V0.1 — Build the modern SDI feature panel 1984-2025 (Q4) for the W16 V2 banking-failure
work. One row per (rssd_id, year), Q4 only, from public FDIC SDI (fdic_financials).

Columns:
  assets          = ASSET                                  ($ thousands, SDI raw)
  income_ratio    = NETINC/ASSET           clip [-0.5, 0.5]
  noncore_proxy   = (DEP-COREDEP)/ASSET    clip [0, 1]      (PROXY: corr ~0.34 vs the
                    exact call-report noncore_ratio — documented approximation, WS4.1)
  uninsured_ratio = DEPUNINS/ASSET         clip [0, 1]
  insured_ratio   = DEPINS/ASSET           clip [0, 1]
  securities_ratio= SC/ASSET               clip [0, 1]
  equity_ratio    = EQ/ASSET               clip [0, 1]
  nim             = NIM   (SDI raw)        -- NOTE: SDI 'NIM' is net interest INCOME in
                    $ thousands (INTINC-EINTEXP), NOT the percentage margin. Stored raw;
                    nim_ratio = NIM/ASSET added for convenience.
  nim_ratio       = NIM/ASSET              clip [-0.2, 0.2]
  roa             = ROA   (SDI raw)        -- percentage (median ~1.04), stored as-is.
  log_age         = log(year - charter_year), charter_year from luck_call_reports dt_open
  F1_failure      = 1 if quarters_to_failure in [-4,-1]
  F3_failure      = 1 if quarters_to_failure in [-12,-1]
  F5_failure      = 1 if quarters_to_failure in [-20,-1]

Failure construction (per spec): quarters_to_failure = -ceil((fail_day-period_end).days/90);
DROP observations after failure (days_to_failure < 0). Failures sourced from public FDIC
bank_failures via cert->rssd crosswalk (fdic_financials u institutions u bank_failures_enriched).

Validation: row/entity counts; reconcile total ASSET vs FDIC SDI aggregate per year;
confirm SVB/Signature/First Republic present for 2021-2022 with F1=1.
"""

import numpy as np
import pandas as pd
import duckdb
from utils import DB_PATH, OUTPUT_ROOT

OUT = OUTPUT_ROOT / "sdi_feature_panel.parquet"
OUT.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH), read_only=True)

# --- 1. SDI Q4 fields per (rssd, year) -------------------------------------------------
sdi = con.execute("""
  SELECT rssd_id,
    CAST(EXTRACT(year FROM period_end) AS INTEGER) AS year,
    period_end,
    SUM(CASE WHEN variable_id='ASSET'    THEN value END) AS asset,
    SUM(CASE WHEN variable_id='NETINC'   THEN value END) AS netinc,
    SUM(CASE WHEN variable_id='DEP'      THEN value END) AS dep,
    SUM(CASE WHEN variable_id='COREDEP'  THEN value END) AS coredep,
    SUM(CASE WHEN variable_id='DEPUNINS' THEN value END) AS depunins,
    SUM(CASE WHEN variable_id='DEPINS'   THEN value END) AS depins,
    SUM(CASE WHEN variable_id='SC'       THEN value END) AS sc,
    SUM(CASE WHEN variable_id='EQ'       THEN value END) AS eq,
    SUM(CASE WHEN variable_id='NIM'      THEN value END) AS nim,
    SUM(CASE WHEN variable_id='ROA'      THEN value END) AS roa
  FROM fdic_financials
  WHERE variable_id IN ('ASSET','NETINC','DEP','COREDEP','DEPUNINS','DEPINS','SC','EQ','NIM','ROA')
    AND EXTRACT(month FROM period_end)=12
    AND rssd_id IS NOT NULL
  GROUP BY rssd_id, period_end
""").fetchdf()
print(f"[load] SDI Q4 rows: {len(sdi):,}  rssd: {sdi.rssd_id.nunique():,}  "
      f"years {int(sdi.year.min())}-{int(sdi.year.max())}")

# --- 2. charter year -> log_age --------------------------------------------------------
dto = con.execute("""
  SELECT entity_id AS rssd_id, MIN(value) AS dt_open
  FROM luck_call_reports WHERE variable_id='dt_open' AND value>0
  GROUP BY entity_id
""").fetchdf()
dto["charter_year"] = pd.to_numeric(dto["dt_open"] // 10000, errors="coerce")

# --- 3. failures: cert -> rssd, earliest closing_date ---------------------------------
fail = con.execute("""
  WITH x AS (
    SELECT DISTINCT fdic_cert AS cert, rssd_id FROM fdic_financials
      WHERE fdic_cert IS NOT NULL AND rssd_id IS NOT NULL
    UNION SELECT fdic_cert, rssd_id FROM institutions
      WHERE fdic_cert IS NOT NULL AND rssd_id IS NOT NULL
    UNION SELECT cert, rssd_id FROM bank_failures_enriched
      WHERE cert IS NOT NULL AND rssd_id IS NOT NULL),
   f AS (SELECT cert, MIN(closing_date) AS fail_day FROM bank_failures
         WHERE cert IS NOT NULL GROUP BY cert)
  SELECT x.rssd_id, MIN(f.fail_day) AS fail_day
  FROM f JOIN x ON f.cert=x.cert GROUP BY x.rssd_id
""").fetchdf()
print(f"[load] failures mapped to rssd (raw): {len(fail):,}")

# Crosswalk hazard: cert<->rssd reuse means a failed small cert can share an rssd lineage
# with a SURVIVING giant (e.g. cert 3510 -> rssd 480228 = Bank of America). Such a spurious
# fail_day would wrongly drop the survivor's post-2009 obs. Guard: only honor a fail_day for
# an rssd if that rssd has NO SDI Q4 filing more than 2 quarters (180d) AFTER fail_day. A
# genuinely failed bank stops filing; a survivor that keeps filing is a mismapping -> discard.
lastfile = con.execute("""
  SELECT rssd_id, MAX(period_end) AS last_period
  FROM fdic_financials WHERE EXTRACT(month FROM period_end)=12 AND rssd_id IS NOT NULL
  GROUP BY rssd_id
""").fetchdf()
fail = fail.merge(lastfile, on="rssd_id", how="left")
_fd = pd.to_datetime(fail.fail_day); _lp = pd.to_datetime(fail.last_period)
spurious = (_lp - _fd).dt.days > 180
print(f"[guard] dropping {int(spurious.sum())} spurious fail-day mappings "
      f"(survivor still filing >180d after fail_day): "
      f"{sorted(fail.loc[spurious,'rssd_id'].astype(int).tolist())[:8]}...")
fail = fail.loc[~spurious, ["rssd_id", "fail_day"]].reset_index(drop=True)
print(f"[load] failures mapped to rssd (guarded): {len(fail):,}")

# crisis banks for validation
crisis = con.execute("""
  SELECT bfe.cert, bfe.bank_name, COALESCE(bfe.rssd_id, ff.rssd_id) AS rssd_id
  FROM bank_failures_enriched bfe
  LEFT JOIN (SELECT DISTINCT fdic_cert, rssd_id FROM fdic_financials WHERE rssd_id IS NOT NULL) ff
    ON bfe.cert=ff.fdic_cert
  WHERE bfe.cert IN (24735,57053,59017)
""").fetchdf()

# FDIC SDI aggregate ASSET per year (Q4) for reconciliation
agg = con.execute("""
  SELECT CAST(EXTRACT(year FROM period_end) AS INTEGER) AS year,
         SUM(value) AS total_asset, COUNT(DISTINCT rssd_id) AS n_rssd
  FROM fdic_financials
  WHERE variable_id='ASSET' AND EXTRACT(month FROM period_end)=12 AND rssd_id IS NOT NULL
  GROUP BY 1 ORDER BY 1
""").fetchdf()
con.close()

# --- 4. assemble ----------------------------------------------------------------------
df = sdi.merge(dto[["rssd_id", "charter_year"]], on="rssd_id", how="left") \
        .merge(fail, on="rssd_id", how="left")

df["charter_year"] = pd.to_numeric(df["charter_year"], errors="coerce")
df["log_age"] = np.log((df["year"] - df["charter_year"]).where(lambda s: s > 0))

pe = pd.to_datetime(df.period_end)
fd = pd.to_datetime(df.fail_day)
df["days_to_failure"] = (fd - pe).dt.days
# DROP observations AFTER failure
df = df[df.days_to_failure.isna() | (df.days_to_failure >= 0)].copy()

qtf = -np.ceil(df.days_to_failure / 90)  # quarters_to_failure (negative = before failure)
df["F1_failure"] = ((qtf >= -4)  & (qtf <= -1)).astype(float)
df["F3_failure"] = ((qtf >= -12) & (qtf <= -1)).astype(float)
df["F5_failure"] = ((qtf >= -20) & (qtf <= -1)).astype(float)

# --- 5. ratios (formula fidelity + documented clips) ----------------------------------
df["assets"]           = df.asset
df["income_ratio"]     = (df.netinc / df.asset).clip(-0.5, 0.5)
df["noncore_proxy"]    = ((df.dep - df.coredep) / df.asset).where(lambda s: (s >= 0) & (s <= 1))
df["uninsured_ratio"]  = (df.depunins / df.asset).where(lambda s: (s >= 0) & (s <= 1))
df["insured_ratio"]    = (df.depins   / df.asset).where(lambda s: (s >= 0) & (s <= 1))
df["securities_ratio"] = (df.sc       / df.asset).where(lambda s: (s >= 0) & (s <= 1))
df["equity_ratio"]     = (df["eq"]    / df.asset).where(lambda s: (s >= 0) & (s <= 1))
df["nim_ratio"]        = (df.nim      / df.asset).clip(-0.2, 0.2)   # SDI NIM is $-valued NII
# nim, roa kept as SDI raw

cols = ["rssd_id", "year", "assets", "income_ratio", "noncore_proxy", "uninsured_ratio",
        "insured_ratio", "securities_ratio", "equity_ratio", "nim", "nim_ratio", "roa",
        "log_age", "F1_failure", "F3_failure", "F5_failure"]
panel = df[df.asset > 0][cols].reset_index(drop=True)

panel.to_parquet(OUT, index=False)
print(f"\n[write] {OUT}")
print(f"[write] rows: {len(panel):,}  rssd: {panel.rssd_id.nunique():,}  "
      f"years {int(panel.year.min())}-{int(panel.year.max())}")

# WS1 (2026-05-31): persist as the CANONICAL freeNIC table `fdic_sdi_features`
# (read-write connection; the Volcker parquet above is kept for CLV consumers).
from utils import log_ingestion  # noqa: E402
_w = duckdb.connect(str(DB_PATH))
_w.register("panel_df", panel)
_w.execute("CREATE OR REPLACE TABLE fdic_sdi_features AS SELECT * FROM panel_df")
_w.unregister("panel_df")
_w.close()
log_ingestion("31", f"fdic_sdi_features table built: {len(panel):,} rows, "
                    f"{panel.rssd_id.nunique():,} entities, "
                    f"{int(panel.year.min())}-{int(panel.year.max())} (Q4, FDIC SDI features).")
print(f"[write] freeNIC table fdic_sdi_features: {len(panel):,} rows")

# --- 6. VALIDATION --------------------------------------------------------------------
print("\n========== VALIDATION ==========")
print(f"F1=1: {int(panel.F1_failure.sum()):,}  F3=1: {int(panel.F3_failure.sum()):,}  "
      f"F5=1: {int(panel.F5_failure.sum()):,}")
print("\nColumn non-null fraction:")
for c in cols[2:]:
    print(f"  {c:18} non-null={panel[c].notna().mean():.3f}  "
          f"min={panel[c].min():.4g} med={panel[c].median():.4g} max={panel[c].max():.4g}")

# reconcile ASSET totals vs FDIC SDI per-year aggregate (panel keeps asset>0 only)
rec = panel.groupby("year").agg(panel_asset=("assets", "sum"),
                                panel_n=("rssd_id", "nunique")).reset_index()
rec = rec.merge(agg, on="year", how="left")
rec["asset_diff_pct"] = (rec.panel_asset - rec.total_asset) / rec.total_asset * 100
print("\nASSET reconciliation vs FDIC SDI aggregate (sample years):")
for y in [1984, 1990, 2000, 2008, 2011, 2020, 2022, 2025]:
    r = rec[rec.year == y]
    if len(r):
        r = r.iloc[0]
        print(f"  {y}: panel ${r.panel_asset/1e9:,.2f}T ({int(r.panel_n):,} banks) vs "
              f"SDI ${r.total_asset/1e9:,.2f}T ({int(r.n_rssd):,})  diff={r.asset_diff_pct:+.3f}%")
print(f"\nMax |asset diff| across all years: {rec.asset_diff_pct.abs().max():.4f}%")

# crisis banks present 2021-2022 with F1=1?
print("\nCrisis-bank check (2021-2022):")
for _, c in crisis.iterrows():
    sub = panel[(panel.rssd_id == c.rssd_id) & (panel.year.isin([2021, 2022]))]
    if len(sub):
        for _, r in sub.sort_values("year").iterrows():
            print(f"  {c.bank_name[:24]:24} rssd={int(c.rssd_id)} y{int(r.year)}: "
                  f"assets=${r.assets/1e6:.1f}B unins={r.uninsured_ratio:.3f} "
                  f"F1={int(r.F1_failure)} F3={int(r.F3_failure)} F5={int(r.F5_failure)}")
    else:
        print(f"  {c.bank_name[:24]:24} rssd={c.rssd_id}: NOT in panel 2021-2022")
print("================================")
