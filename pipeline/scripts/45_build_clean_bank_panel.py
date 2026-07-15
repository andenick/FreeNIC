"""Phase 45 -- Build the CANONICAL clean bank panel (`clean_bank_panel`).

THE UNIT-CAVEAT FIX, PROMOTED INTO FREENIC AS A FIRST-CLASS DERIVED TABLE.

finhist.com is the PRIMARY historical source; this clean panel built FROM RAW is the
PRIMARY combined historical+modern per-bank level panel. The CLV `robin_panel` is a
derived ADD-ON, never the base -- its absolute-$ columns are CPI-deflated AND uncalibrated
(see DATA_DICTIONARY.md `robin_panel` caveat). Consumers who need DOLLAR LEVELS use THIS
table; `robin_panel`'s clean ratios remain usable as an add-on.

WHAT THIS BUILDS
  Outputs/clean_bank_panel.parquet  (canonical freeNIC Outputs parquet, byte-stable)
  main.clean_bank_panel             (canonical DB table; CREATE OR REPLACE on a RW conn,
                                     exactly like 31_build_sdi_feature_panel.py)
  Outputs/parquet/clean_bank_panel.parquet  (via 12_export_parquet.py, wired in)

One row per (entity, year), three strata unioned (era x src_vintage), every absolute in
explicit nominal dollars + a CPI-deflated real twin (base 1990=100):
  HIST   1863-1941  src_vintage='occ_historical_clv'  annual    NOMINAL USD as-is
  MODL   1959-1975  src_vintage='luck_wide'           annual    THOUSANDS -> x1000
  MODC   1976-2026  src_vintage='sched_call'          annual    THOUSANDS -> x1000

PROVENANCE / VERSION PINS (carried in the sidecar Outputs/clean_bank_panel.PROVENANCE.json):
  * finhist historical-call: CLV "Failing Banks" public historical-call (finhist v2.10.0,
    2026-03-31), arXiv:2506.06082, doi:10.7910/DVN/Q22XR1; warehouse table occ_historical
    (source='occ_historical_clv'). sha256 of the source archive pinned from finhist SOURCES.csv.
  * Per-field DPR: <clv_reconstruction>/provenance/clv_panel_v2.DPR.md
    (every output column -> source table/variable_id -> formula -> units -> CLV reference;
     NOT CAPTURED is a first-class value).

REUSE: this is `code/r2_build_clv_panel.py` (Bev Testing, canonical sha d0fb7c8d) adapted to
the freeNIC ingestion-script convention (utils paths, DB-table materialization, validation
wiring). The SQL strata logic is byte-for-byte the proven R2/R4 build (CPI threads=1 +
ROUND(12) determinism fix; 1900-1933 equity/deposit COALESCE fix; 1942-1958 gap absent).

NON-NEGOTIABLES (carried from R2): read_only build connection (warehouse mtime unchanged
for the heavy joins); deterministic (threads=1 CPI block, ORDER BY, no RNG); byte-stable;
NO synthetic data (1942-1958 stays absent); NO fabrication (NOT CAPTURED where no clean
source). The ONLY write to the warehouse is the final `CREATE OR REPLACE TABLE
clean_bank_panel` on a separate RW connection (the 31_build pattern; backed up + validated
by 13_validate.py downstream).
"""

import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).parent))
from utils import DB_PATH, OUTPUTS_DIR, log_ingestion, timer

_T0 = time.time()

# ---- Paths -----------------------------------------------------------------------------
OUT = OUTPUTS_DIR / "clean_bank_panel.parquet"
PROV_OUT = OUTPUTS_DIR / "clean_bank_panel.PROVENANCE.json"
_DUCK_TMP = OUTPUTS_DIR / "_duckdb_tmp"

# External CLV-reconstruction inputs (the from-raw build's quality-flag tags + per-field DPR).
# These live in a separate reconstruction workspace, NOT in FreeNIC; the warehouse RAW tables
# are read by-reference. If the quality_flags parquet is absent (e.g. a clean checkout without
# the reconstruction workspace), the HIST quality-tag columns are emitted as NULL -- an honest
# absence, never a silent row drop (mirrors 31's _HARVEST fallback). Set the workspace via env.
_CLV_WS = Path(os.environ.get("CLV_RECONSTRUCTION_DIR", "clv_reconstruction"))
QF = _CLV_WS / "inputs" / "finhist" / "quality_flags.parquet"
DPR = _CLV_WS / "provenance" / "clv_panel_v2.DPR.md"

CPI_BASE_YEAR = 1990  # robin_panel.cpi base: cpi(1990) == 100.0 (verified)

# finhist source pin (from the reconstruction SOURCES.csv; finhist Stata package v2.10.0).
FINHIST_PIN = {
    "dataset": "CLV Failing Banks public historical-call",
    "finhist_version": "2.10.0",
    "finhist_version_date": "2026-03-31",
    "reference": "arXiv:2506.06082; doi:10.7910/DVN/Q22XR1",
    "warehouse_table": "occ_historical (source='occ_historical_clv')",
    "source_archive": "historical-call.dta.zip",
    "source_sha256": "c4d64d836d5175f1eb24c5295763a83cd7ac95f23ab48397b3572fb40c701ba1",
    "source_url": "https://f001.backblazeb2.com/file/sergio-public-data/historical-call.dta.zip",
}


def _stage(label):
    print(f"[stage +{time.time()-_T0:7.1f}s] {label}", file=sys.stderr, flush=True)


def connect_ro():
    """Read-only build connection (warehouse mtime unchanged for the heavy joins)."""
    _DUCK_TMP.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    con.execute("PRAGMA threads=4")
    con.execute("PRAGMA preserve_insertion_order=true")
    con.execute("SET default_null_order='nulls_last'")
    con.execute("SET memory_limit='10GB'")
    con.execute(f"SET temp_directory='{_DUCK_TMP.as_posix()}'")
    con.execute("PRAGMA disable_progress_bar")
    return con


def build_cpi(con):
    """Annual CPI deflator (base 1990=100). Primary = robin_panel.cpi (1870-2020); tails
    (1863-1869, 2021-2024) = robin_panel.cpi_gfd RESCALED onto the cpi base via the mean
    overlap ratio. DETERMINISM: the per-year AVG over robin_panel is computed threads=1 so
    the float reduction order is fixed, then ROUND(cpi,12). Threads restored to 4 after."""
    con.execute("PRAGMA threads=1")
    con.execute("""
    CREATE TEMP TABLE cpi_primary AS
      SELECT year, AVG(cpi) AS cpi FROM robin_panel
      WHERE cpi IS NOT NULL GROUP BY year ORDER BY year;
    CREATE TEMP TABLE cpi_gfd AS
      SELECT year, AVG(cpi_gfd) AS cpi_gfd FROM robin_panel
      WHERE cpi_gfd IS NOT NULL GROUP BY year ORDER BY year;
    """)
    scale = round(con.execute("""
      SELECT AVG(p.cpi / g.cpi_gfd)
      FROM cpi_primary p JOIN cpi_gfd g USING(year)
      WHERE p.cpi IS NOT NULL AND g.cpi_gfd IS NOT NULL AND g.cpi_gfd <> 0
    """).fetchone()[0], 12)
    con.execute(f"""
    CREATE TEMP TABLE cpi_annual AS
    WITH allyears AS (
      SELECT year FROM cpi_primary UNION SELECT year FROM cpi_gfd
    )
    SELECT y.year,
           ROUND(COALESCE(p.cpi, g.cpi_gfd * {scale}), 12)            AS cpi,
           CASE WHEN p.cpi IS NOT NULL THEN 'robin_panel.cpi'
                WHEN g.cpi_gfd IS NOT NULL THEN 'cpi_gfd_rescaled'
                ELSE NULL END                                          AS cpi_source
    FROM allyears y
    LEFT JOIN cpi_primary p USING(year)
    LEFT JOIN cpi_gfd     g USING(year)
    ORDER BY y.year
    """)
    con.execute("PRAGMA threads=4")
    rng = con.execute("SELECT MIN(year),MAX(year),COUNT(*) FROM cpi_annual WHERE cpi IS NOT NULL").fetchone()
    return scale, rng


def pivot_hist(con):
    """HIST stratum: occ_historical_clv long->wide, annual, NOMINAL USD as-is."""
    con.execute("""
    CREATE TEMP TABLE hist_raw AS
    SELECT bank_id, YEAR(report_date) AS year, report_date AS call_date, variable_id, value
    FROM occ_historical WHERE source='occ_historical_clv'
    """)
    con.execute("""
    CREATE TEMP TABLE hist_wide AS
    SELECT bank_id, year, MIN(call_date) AS call_date,
      MAX(CASE WHEN variable_id='assets'            THEN value END) AS assets,
      MAX(CASE WHEN variable_id='loans'             THEN value END) AS loans,
      MAX(CASE WHEN variable_id='deposits'          THEN value END) AS deposits,
      MAX(CASE WHEN variable_id='individual_deposits' THEN value END) AS individual_deposits,
      MAX(CASE WHEN variable_id='demand_deposits'   THEN value END) AS demand_deposits,
      MAX(CASE WHEN variable_id='time_deposits'     THEN value END) AS time_deposits,
      MAX(CASE WHEN variable_id='us_deposits'       THEN value END) AS us_deposits,
      MAX(CASE WHEN variable_id='usdo_deposits'     THEN value END) AS usdo_deposits,
      MAX(CASE WHEN variable_id='capital'           THEN value END) AS capital,
      MAX(CASE WHEN variable_id='surplus'           THEN value END) AS surplus,
      MAX(CASE WHEN variable_id='undivided_profits' THEN value END) AS undivided_profits,
      MAX(CASE WHEN variable_id='surplus_and_undivided_profits' THEN value END) AS surplus_and_undivided_profits,
      MAX(CASE WHEN variable_id='notes_nb'          THEN value END) AS notes_nb,
      MAX(CASE WHEN variable_id='securities'        THEN value END) AS securities,
      MAX(CASE WHEN variable_id='oreo_and_mortgages' THEN value END) AS oreo_and_mortgages,
      MAX(CASE WHEN variable_id='due_to_nb'         THEN value END) AS due_to_nb,
      MAX(CASE WHEN variable_id='due_to_other_nb'   THEN value END) AS due_to_other_nb,
      MAX(CASE WHEN variable_id='due_to_ra'         THEN value END) AS due_to_ra,
      MAX(CASE WHEN variable_id='due_to_sb'         THEN value END) AS due_to_sb,
      MAX(CASE WHEN variable_id='due_to_tc_and_sb'  THEN value END) AS due_to_tc_and_sb,
      MAX(CASE WHEN variable_id='due_to_banks'      THEN value END) AS due_to_banks,
      MAX(CASE WHEN variable_id='due_to_banks_and_other_liabs' THEN value END) AS due_to_banks_and_other_liabs
    FROM hist_raw GROUP BY bank_id, year
    """)


def pivot_modl(con):
    """MODERN-luck stratum: luck_wide 1959-1975, ANNUAL (Dec else latest call), THOUSANDS -> x1000."""
    con.execute("""
    CREATE TEMP TABLE modl AS
    SELECT entity_id AS rssd_id, YEAR(period_end) AS year, period_end AS call_date,
      assets, equity, deposits, time_deposits, demand_deposits,
      ln_tot AS loans, othbor_liab, ytdnetinc, npl_tot, surplus, securities
    FROM luck_wide
    WHERE YEAR(period_end) BETWEEN 1959 AND 1975 AND assets IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY entity_id, YEAR(period_end)
      ORDER BY (CASE WHEN MONTH(period_end)=12 THEN 1 ELSE 0 END) DESC,
               period_end DESC, assets DESC
    ) = 1
    """)


def pivot_modc(con):
    """MODERN-call stratum: canonical Call schedules 1976-2026, ANNUAL, THOUSANDS -> x1000.
    THE UNIT-FIX LAYER. assets=RCFD2170 (consolidated, bank-level) else RCON2170."""
    con.execute("""
    CREATE TEMP TABLE modc AS
    WITH rc_annual AS (
      SELECT rc.* FROM sched_call_rc rc
      WHERE YEAR(rc.period_end) BETWEEN 1976 AND 2026
        AND COALESCE(rc.l12_rcfd2170, rc.l12_rcon2170) IS NOT NULL
      QUALIFY ROW_NUMBER() OVER (
        PARTITION BY rc.rssd_id, YEAR(rc.period_end)
        ORDER BY (CASE WHEN MONTH(rc.period_end)=12 THEN 1 ELSE 0 END) DESC,
                 rc.period_end DESC,
                 COALESCE(rc.l12_rcfd2170, rc.l12_rcon2170) DESC
      ) = 1
    )
    SELECT
      rc.rssd_id                                              AS rssd_id,
      YEAR(rc.period_end)                                     AS year,
      rc.period_end                                           AS call_date,
      COALESCE(rc.l12_rcfd2170, rc.l12_rcon2170)              AS assets,
      rc.l27_a_rcon3210                                       AS equity,
      COALESCE(rc.l13_a_rcon2200,0) + COALESCE(rc.l13_b_rcfn2200,0) AS deposits,
      COALESCE(rcc.l12_rcfd2122, rcc.l12_rcon2122)            AS loans,
      COALESCE(rc.l16_rcfd3190, rc.l16_rcon3190)              AS othbor_liab,
      COALESCE(ri.l12_riad4340, ri.l14_riad4340)             AS ytdnetinc
    FROM rc_annual rc
    LEFT JOIN sched_call_rc_c rcc USING(rssd_id, period_end)
    LEFT JOIN sched_call_ri   ri  USING(rssd_id, period_end)
    """)


def build_panel(con):
    """Assemble the unioned long-by-row panel with ratios + nominal/real absolutes + tags.
    Returns (scale, cpi_rng). Materializes TEMP TABLE panel_final."""
    _stage("build_cpi")
    scale, cpi_rng = build_cpi(con)
    _stage("pivot_hist")
    pivot_hist(con)
    _stage("pivot_modl")
    pivot_modl(con)
    _stage("pivot_modc")
    pivot_modc(con)

    _stage("load qf")
    if QF.exists():
        con.execute(f"CREATE TEMP TABLE qf AS SELECT * FROM read_parquet('{QF.as_posix()}')")
        qf_present = True
    else:
        # Honest absence: empty qf so the LEFT JOIN yields NULL tags (never a row drop).
        con.execute("CREATE TEMP TABLE qf (bank_id BIGINT, year INT, approx_ok_bs INT, "
                    "ok_bs INT, is_filled_in INT, is_ambiguous INT, bs_merge INT)")
        qf_present = False
        print(f"[WARN] quality_flags not found at {QF}; HIST quality tags emitted as NULL "
              f"(honest absence).", file=sys.stderr)

    _stage("build panel (union)")
    con.execute("""
    CREATE TEMP TABLE panel AS
    WITH hist AS (
      SELECT
        h.bank_id::BIGINT                        AS bank_id,
        CAST(NULL AS BIGINT)                     AS rssd_id,
        h.year::INT                              AS year,
        h.call_date,
        'HIST'                                   AS era_group,
        'occ_historical_clv'                     AS src_vintage,
        'nominal_usd'                            AS unit_basis,
        (COALESCE(h.capital,0)+COALESCE(h.surplus,0)+COALESCE(h.undivided_profits,0)
          + CASE WHEN h.surplus IS NULL AND h.undivided_profits IS NULL
                 THEN COALESCE(h.surplus_and_undivided_profits,0) ELSE 0 END) AS equity_raw,
        h.assets, h.loans, h.deposits, h.individual_deposits, h.demand_deposits,
        h.time_deposits, h.us_deposits, h.usdo_deposits, h.capital, h.surplus,
        h.undivided_profits, h.surplus_and_undivided_profits, h.notes_nb, h.securities,
        h.oreo_and_mortgages,
        (COALESCE(h.individual_deposits, h.deposits, 0)
          + COALESCE(h.us_deposits,0) + COALESCE(h.usdo_deposits,0)
          + COALESCE(h.due_to_nb,0) + COALESCE(h.due_to_other_nb,0)
          + COALESCE(h.due_to_ra,0) + COALESCE(h.due_to_sb,0)
          + COALESCE(h.due_to_tc_and_sb,0)
          + COALESCE(h.due_to_banks,0) + COALESCE(h.due_to_banks_and_other_liabs,0)
        )                                         AS total_deposits_hist,
        CAST(NULL AS DOUBLE)                      AS othbor_liab,
        CAST(NULL AS DOUBLE)                      AS ytdnetinc,
        CAST(NULL AS DOUBLE)                      AS npl_tot
      FROM hist_wide h
    ),
    hist2 AS (
      SELECT *,
        equity_raw                                                       AS equity,
        CASE WHEN assets>0 THEN equity_raw/assets END                    AS leverage,
        CASE WHEN equity_raw>0 THEN
          (COALESCE(surplus,0)+COALESCE(undivided_profits, surplus_and_undivided_profits,0)
           - COALESCE(CASE WHEN surplus IS NOT NULL THEN 0 ELSE 0 END,0)) / equity_raw END AS insolvency,
        CASE WHEN assets>0 THEN
          (assets - total_deposits_hist - equity_raw - COALESCE(notes_nb,0))/assets END    AS noncore_funding,
        CASE WHEN year BETWEEN 1889 AND 1904 AND loans>0
             THEN oreo_and_mortgages/loans END                            AS npl_proxy,
        loans                                                             AS loans_clean,
        COALESCE(deposits, individual_deposits,
                 NULLIF(COALESCE(demand_deposits,0)+COALESCE(time_deposits,0)
                        +COALESCE(us_deposits,0)+COALESCE(usdo_deposits,0),0)) AS deposits_clean,
        time_deposits                                                     AS time_deposits_clean,
        demand_deposits                                                   AS demand_deposits_clean,
        securities                                                        AS securities_clean,
        notes_nb                                                          AS notes_nb_clean,
        surplus                                                           AS surplus_clean,
        undivided_profits                                                 AS undivided_profits_clean,
        CAST(NULL AS DOUBLE)                                              AS othbor_clean
      FROM hist
    ),
    modl AS (
      SELECT
        CAST(NULL AS BIGINT)        AS bank_id,
        rssd_id::BIGINT             AS rssd_id,
        year::INT                   AS year,
        call_date,
        'MODERN'                    AS era_group,
        'luck_wide'                 AS src_vintage,
        'nominal_usd'               AS unit_basis,
        assets*1000.0              AS assets,
        equity*1000.0              AS equity,
        deposits*1000.0            AS deposits_clean,
        loans*1000.0               AS loans_clean,
        time_deposits*1000.0       AS time_deposits_clean,
        demand_deposits*1000.0     AS demand_deposits_clean,
        securities*1000.0          AS securities_clean,
        surplus*1000.0             AS surplus_clean,
        othbor_liab*1000.0         AS othbor_clean,
        ytdnetinc*1000.0           AS ytdnetinc,
        npl_tot*1000.0             AS npl_tot
      FROM modl
    ),
    modl2 AS (
      SELECT *,
        CASE WHEN assets>0 THEN equity/assets END                         AS leverage,
        CASE WHEN assets>0 THEN ytdnetinc/assets END                      AS insolvency,
        CASE WHEN assets>0 THEN (COALESCE(time_deposits_clean,0)+COALESCE(othbor_clean,0))/assets END AS noncore_funding,
        CASE WHEN loans_clean>0 THEN npl_tot/loans_clean END              AS npl_proxy
      FROM modl
    ),
    modc AS (
      SELECT
        CAST(NULL AS BIGINT)        AS bank_id,
        rssd_id::BIGINT             AS rssd_id,
        year::INT                   AS year,
        call_date,
        'MODERN'                    AS era_group,
        'sched_call'                AS src_vintage,
        'nominal_usd'               AS unit_basis,
        assets*1000.0              AS assets,
        equity*1000.0              AS equity,
        deposits*1000.0            AS deposits_clean,
        loans*1000.0               AS loans_clean,
        othbor_liab*1000.0         AS othbor_clean,
        ytdnetinc*1000.0           AS ytdnetinc
      FROM modc
    ),
    modc2 AS (
      SELECT *,
        CASE WHEN assets>0 AND equity IS NOT NULL THEN equity/assets END  AS leverage,
        CASE WHEN assets>0 THEN ytdnetinc/assets END                      AS insolvency,
        CASE WHEN assets>0 THEN COALESCE(othbor_clean,0)/assets END        AS noncore_funding_partial,
        CAST(NULL AS DOUBLE) AS time_deposits_clean,
        CAST(NULL AS DOUBLE) AS demand_deposits_clean,
        CAST(NULL AS DOUBLE) AS securities_clean,
        CAST(NULL AS DOUBLE) AS surplus_clean,
        CAST(NULL AS DOUBLE) AS npl_tot,
        CAST(NULL AS DOUBLE) AS npl_proxy
      FROM modc
    )
    SELECT bank_id, rssd_id, year, call_date, era_group, src_vintage, unit_basis,
           assets        AS assets_nominal,
           equity        AS equity_nominal,
           loans_clean   AS loans_nominal,
           deposits_clean AS deposits_nominal,
           time_deposits_clean AS time_deposits_nominal,
           demand_deposits_clean AS demand_deposits_nominal,
           securities_clean AS securities_nominal,
           notes_nb_clean AS notes_nb_nominal,
           surplus_clean AS surplus_nominal,
           undivided_profits_clean AS undivided_profits_nominal,
           othbor_clean  AS othbor_liab_nominal,
           ytdnetinc     AS ytdnetinc_nominal,
           leverage, insolvency, noncore_funding, npl_proxy
    FROM hist2
    UNION ALL BY NAME
    SELECT bank_id, rssd_id, year, call_date, era_group, src_vintage, unit_basis,
           assets AS assets_nominal, equity AS equity_nominal, loans_clean AS loans_nominal,
           deposits_clean AS deposits_nominal, time_deposits_clean AS time_deposits_nominal,
           demand_deposits_clean AS demand_deposits_nominal, securities_clean AS securities_nominal,
           CAST(NULL AS DOUBLE) AS notes_nb_nominal, surplus_clean AS surplus_nominal,
           CAST(NULL AS DOUBLE) AS undivided_profits_nominal, othbor_clean AS othbor_liab_nominal,
           ytdnetinc AS ytdnetinc_nominal,
           leverage, insolvency, noncore_funding, npl_proxy
    FROM modl2
    UNION ALL BY NAME
    SELECT bank_id, rssd_id, year, call_date, era_group, src_vintage, unit_basis,
           assets AS assets_nominal, equity AS equity_nominal, loans_clean AS loans_nominal,
           deposits_clean AS deposits_nominal, time_deposits_clean AS time_deposits_nominal,
           demand_deposits_clean AS demand_deposits_nominal, securities_clean AS securities_nominal,
           CAST(NULL AS DOUBLE) AS notes_nb_nominal, surplus_clean AS surplus_nominal,
           CAST(NULL AS DOUBLE) AS undivided_profits_nominal, othbor_clean AS othbor_liab_nominal,
           ytdnetinc AS ytdnetinc_nominal,
           leverage, insolvency, noncore_funding_partial AS noncore_funding, npl_proxy
    FROM modc2
    """)

    abs_cols = ["assets", "equity", "loans", "deposits", "time_deposits", "demand_deposits",
                "securities", "notes_nb", "surplus", "undivided_profits", "othbor_liab", "ytdnetinc"]
    real_exprs = ",\n        ".join(
        f"CASE WHEN c.cpi IS NOT NULL THEN p.{a}_nominal / (c.cpi/100.0) END AS {a}_real"
        for a in abs_cols)

    _stage("build panel_cpi (cpi + real + qf join)")
    con.execute(f"""
    CREATE TEMP TABLE panel_cpi AS
    SELECT
      p.bank_id, p.rssd_id, p.year, p.call_date, p.era_group, p.src_vintage, p.unit_basis,
      CASE
        WHEN p.year < 1900 THEN 'pre-1900'
        WHEN p.year < 1934 THEN '1900-1933'
        WHEN p.year < 1942 THEN '1934-1941'
        WHEN p.year < 1976 THEN '1959-1975'
        ELSE '1976-2024'
      END                                       AS era,
      c.cpi                                      AS cpi_deflator,
      c.cpi_source,
      {CPI_BASE_YEAR}                            AS cpi_base_year,
      p.assets_nominal, p.equity_nominal, p.loans_nominal, p.deposits_nominal,
      p.time_deposits_nominal, p.demand_deposits_nominal, p.securities_nominal,
      p.notes_nb_nominal, p.surplus_nominal, p.undivided_profits_nominal,
      p.othbor_liab_nominal, p.ytdnetinc_nominal,
      {real_exprs},
      p.leverage, p.insolvency, p.noncore_funding, p.npl_proxy,
      qf.approx_ok_bs, qf.ok_bs, qf.is_filled_in, qf.is_ambiguous, qf.bs_merge,
      CASE WHEN p.era_group='HIST' THEN COALESCE(qf.ok_bs, 0) ELSE NULL END AS ok_bs_filter
    FROM panel p
    LEFT JOIN cpi_annual c ON p.year = c.year
    LEFT JOIN qf ON p.bank_id = qf.bank_id AND p.year = qf.year
    """)

    _stage("build panel_final (= panel_cpi; growth done in pandas)")
    con.execute("CREATE TEMP TABLE panel_final AS SELECT * FROM panel_cpi")
    return scale, cpi_rng, qf_present


def report_gates(con, scale, cpi_rng):
    """The headline UNIT GATE + ratio-fidelity + gap honesty. Returns dict of gate results."""
    print("=" * 78)
    print("CLEAN BANK PANEL BUILD (freeNIC canonical derived table)")
    print("=" * 78)
    print(f"CPI deflator: base {CPI_BASE_YEAR}=100; gfd->base rescale = {scale:.6f}; "
          f"coverage {cpi_rng[0]}-{cpi_rng[1]} ({cpi_rng[2]} yrs)")

    n = con.execute("SELECT COUNT(*) FROM panel_final").fetchone()[0]
    span = con.execute("SELECT MIN(year), MAX(year) FROM panel_final").fetchone()
    print(f"\nROWS={n:,}   year span {span[0]}-{span[1]}")

    print("\n=== era x src_vintage coverage ===")
    for r in con.execute("""
      SELECT era_group, src_vintage, era, COUNT(*) n,
             COUNT(DISTINCT COALESCE(bank_id, rssd_id)) entities, MIN(year) y0, MAX(year) y1
      FROM panel_final GROUP BY era_group, src_vintage, era ORDER BY y0, src_vintage
    """).fetchall():
        print(f"  {r[0]:7s} {r[1]:20s} {r[2]:11s} n={r[3]:8,d} entities={r[4]:6,d}  {r[5]}-{r[6]}")

    gap = con.execute("SELECT COUNT(*) FROM panel_final WHERE year BETWEEN 1942 AND 1958").fetchone()[0]
    gap_ok = gap == 0
    print(f"\n=== gap honesty: 1942-1958 rows = {gap}  ({'OK absent' if gap_ok else 'VIOLATION'}) ===")

    print("\n=== UNIT GATE (the headline) ===")
    jpm = con.execute("""SELECT assets_nominal FROM panel_final
      WHERE rssd_id=852218 AND call_date='2008-12-31' AND src_vintage='sched_call'""").fetchone()
    svb = con.execute("""SELECT call_date, assets_nominal FROM panel_final
      WHERE rssd_id=802866 AND src_vintage='sched_call' ORDER BY call_date DESC LIMIT 1""").fetchone()
    occ29 = con.execute("""SELECT bank_id, assets_nominal FROM panel_final
      WHERE era_group='HIST' AND year=1929 ORDER BY assets_nominal DESC NULLS LAST LIMIT 1""").fetchone()
    jpm_ok = bool(jpm) and abs(jpm[0] / 1e12 - 1.75) < 0.05
    svb_ok = bool(svb) and abs(svb[1] / 1e9 - 209) < 5
    occ_ok = bool(occ29) and abs(occ29[1] / 1e9 - 1.8) < 0.15
    print(f"  JPM 2008Q4 assets : ${jpm[0]/1e12:.4f}T   (target ~$1.75T)  {'PASS' if jpm_ok else 'CHECK'}")
    print(f"  SVB last quarter  : {svb[0]} ${svb[1]/1e9:.3f}B   (target ~$209B)  {'PASS' if svb_ok else 'CHECK'}")
    print(f"  occ 1929 largest  : bank {occ29[0]} ${occ29[1]/1e9:.4f}B   (target ~$1.8B)  {'PASS' if occ_ok else 'CHECK'}")

    return {"rows": n, "span": [span[0], span[1]], "gap_1942_1958_ok": gap_ok,
            "unit_gate": {"jpm_2008_T": jpm[0] / 1e12, "jpm_pass": jpm_ok,
                          "svb_last_B": svb[1] / 1e9, "svb_pass": svb_ok,
                          "occ_1929_B": occ29[1] / 1e9, "occ_pass": occ_ok}}


def add_growth(out_path):
    """PANDAS post-step: asset_growth_dlog3 (t vs t-3 within entity) + qcut(5). Sorts + rewrites."""
    import pandas as pd
    import numpy as np
    dfp = pd.read_parquet(out_path)
    dfp["entity_key"] = np.where(
        dfp["era_group"].eq("HIST"),
        "H" + dfp["bank_id"].astype("string"),
        "M" + dfp["src_vintage"].astype("string") + "_" + dfp["rssd_id"].astype("string"))
    la = pd.DataFrame({"entity_key": dfp["entity_key"], "year": dfp["year"],
                       "la": np.log(dfp["assets_real"].where(dfp["assets_real"] > 0))})
    prev = la[["entity_key", "year", "la"]].rename(columns={"la": "la_t3"}).copy()
    prev["year"] = prev["year"] + 3
    merged = la.merge(prev, on=["entity_key", "year"], how="left")
    dfp["asset_growth_dlog3"] = (merged["la"] - merged["la_t3"]).to_numpy()
    q = pd.Series(pd.array([pd.NA] * len(dfp), dtype="Int64"), index=dfp.index)
    for grp in ("HIST", "MODERN"):
        m = dfp["era_group"].eq(grp) & dfp["asset_growth_dlog3"].notna()
        if int(m.sum()) >= 5:
            q.loc[m] = pd.qcut(dfp.loc[m, "asset_growth_dlog3"], 5,
                               labels=[1, 2, 3, 4, 5], duplicates="drop").astype("Int64")
    dfp["asset_growth_quintile"] = q
    dfp = dfp.drop(columns=["entity_key"]).sort_values(
        ["era_group", "src_vintage", "bank_id", "rssd_id", "year", "call_date"],
        na_position="first", kind="stable").reset_index(drop=True)
    dfp.to_parquet(out_path, index=False)
    n_dlog = int(dfp["asset_growth_dlog3"].notna().sum())
    n_q = int(dfp["asset_growth_quintile"].notna().sum())
    print(f"\n=== asset_growth: dlog3 {n_dlog:,} rows; quintile {n_q:,}/{len(dfp):,} ===")
    return len(dfp)


def materialize_db_table(out_path, n_rows):
    """Promote the parquet to the CANONICAL DB table `clean_bank_panel` (RW conn, the
    31_build_sdi_feature_panel.py pattern). CREATE OR REPLACE is atomic; the read-only build
    above kept the warehouse mtime stable for the heavy joins."""
    _w = duckdb.connect(str(DB_PATH))
    _w.execute(f"CREATE OR REPLACE TABLE clean_bank_panel AS "
               f"SELECT * FROM read_parquet('{out_path.as_posix()}')")
    got = _w.execute("SELECT COUNT(*) FROM clean_bank_panel").fetchone()[0]
    _w.close()
    assert got == n_rows, f"DB table row count {got} != parquet {n_rows}"
    print(f"[write] freeNIC table main.clean_bank_panel: {got:,} rows")
    return got


def write_provenance_sidecar(out_path, gates, scale, qf_present, n_rows):
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    prov = {
        "table": "clean_bank_panel",
        "description": ("CANONICAL clean from-raw bank panel (nominal+real $ levels). "
                        "finhist-primary; robin_panel is a derived ADD-ON not the base. "
                        "THE fix for robin_panel's uncalibrated absolute-$ columns."),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "build_script": "Technical/freenic_ingestion/scripts/45_build_clean_bank_panel.py",
        "reuse_of": ("Projects/Bev Testing/Technical/clv_reconstruction/code/r2_build_clv_panel.py "
                     "(canonical clv_panel_v2 sha256 d0fb7c8d...)"),
        "rows": n_rows,
        "year_span": gates["span"],
        "cpi_base_year": CPI_BASE_YEAR,
        "cpi_gfd_rescale_factor": scale,
        "sha256": sha,
        "unit_gate": gates["unit_gate"],
        "gap_1942_1958_absent": gates["gap_1942_1958_ok"],
        "strata": {
            "HIST": "1863-1941 occ_historical (source='occ_historical_clv'), annual, nominal USD as-is",
            "MODL": "1959-1975 luck_wide, annual, thousands x1000",
            "MODC": "1976-2026 sched_call (RCFD2170/RCON2170 ...), annual, thousands x1000",
        },
        "finhist_source_pin": FINHIST_PIN,
        "per_field_DPR": str(DPR),
        "quality_flags_input": str(QF) if qf_present else "ABSENT (HIST quality tags emitted NULL)",
        "determinism": ("CPI AVG threads=1 + ROUND(cpi,12); ORDER BY on COPY + stable sort; "
                        "no RNG -> byte-stable across rebuilds"),
        "non_negotiables": ("read-only build conn; no synthetic 1942-1958; NOT CAPTURED never "
                            "zero-filled; robin_panel left intact (reframed in docs as add-on)"),
    }
    PROV_OUT.write_text(json.dumps(prov, indent=2), encoding="utf-8")
    print(f"[write] provenance sidecar {PROV_OUT}")
    return sha


def main():
    elapsed = timer()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Phase 45: Clean Bank Panel (canonical derived table) ===\n")

    con = connect_ro()
    scale, cpi_rng, qf_present = build_panel(con)

    _stage("COPY to parquet")
    con.execute(f"""
    COPY (SELECT * FROM panel_final
          ORDER BY era_group, src_vintage, COALESCE(bank_id,0), COALESCE(rssd_id,0), year, call_date)
    TO '{OUT.as_posix()}' (FORMAT PARQUET)
    """)
    gates = report_gates(con, scale, cpi_rng)
    con.close()

    n_rows = add_growth(OUT)
    materialize_db_table(OUT, n_rows)
    sha = write_provenance_sidecar(OUT, gates, scale, qf_present, n_rows)

    print(f"\nWROTE {OUT}")
    print(f"SHA256 = {sha}")

    secs = elapsed()
    log_ingestion("45", f"clean_bank_panel built: {n_rows:,} rows, span "
                        f"{gates['span'][0]}-{gates['span'][1]}; unit gate JPM "
                        f"${gates['unit_gate']['jpm_2008_T']:.3f}T / SVB "
                        f"${gates['unit_gate']['svb_last_B']:.1f}B / occ29 "
                        f"${gates['unit_gate']['occ_1929_B']:.2f}B. sha {sha[:16]}. {secs:.1f}s")
    print(f"\nPhase 45 complete in {secs:.1f}s.")
    return sha


if __name__ == "__main__":
    main()
