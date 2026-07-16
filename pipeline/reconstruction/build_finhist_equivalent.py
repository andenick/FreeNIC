"""Build the **finhist-equivalent** panel for 1863-1941 from the OCC historical raw.

The DERIVATION-LAYER re-derivation for the finhist / HIST era (SPEC §0 boundary row 3):
from finhist's digitized OCC balance sheets (``historical-call.dta``, 370,977 x 82 -- the
authors' OCR output) up to their published derived schema, via **original Python
implementing CLV's documented ``04_create-historical-dataset.do`` method**. Emits
``finhist_equivalent_1863_1941.parquet`` + a ``_BUILD_META.json`` sidecar.

============================================================================
THE NOT-DERIVABLE BOUNDARY (the honesty contract for this module -- SPEC §0)
============================================================================
The **OCR itself is NOT-DERIVABLE** -- the microfilm->digits step reads physical OCC
archives (finhist's ``1/2/3-*.do`` import + manual QC, never shipped; CONSTRUCTION_NOTES
§4). This module re-derives ONLY the *derivation layer* on top of that raw: the reconstructed
aggregates, the deposits-override rule, the CPI deflation, and the persistent HIST entity
key. No step ever fabricates a value; every honest gap is RECORDED, never imputed (SPEC §0,
python-data-quality "No Silent Fallbacks").

Two further boundaries are forced by THIS input file (the *public* finhist
``historical-call.dta`` carries balance sheets only -- it does NOT carry the columns
``04`` merges from the OCC-receiverships panel):

  * **Failure / receivership layer NOT-DERIVABLE here** -- ``end_date``,
    ``end_has_receivership``, ``in_vl``, ``receivership_date``, ``days_to_failure`` are
    absent, so ``04 L10-54`` (receiver-restart versioning, ``failed_bank``,
    ``time_to_fail``, the ``in_vl`` / ``days_to_failure<=0`` drops) cannot run from this
    file. That layer belongs to ``06_create-outflows-receivership-data.do`` +
    ``occ-receiverships/receiverships_panel.dta`` (a separate merge). Only the
    ``bs_merge==1`` drop (``04 L40``) is derivable (``bs_merge`` IS in the file). Recorded
    as a gap; the transient ``04 L18`` version id is dropped downstream anyway (G-SPEC,
    entity_spine.hist_version) so its absence has no effect on the delivered charter key.
  * **age / log_age NOT-DERIVABLE here** -- ``04 L129-130`` needs ``charter_date``
    (absent; only the ``charter`` number is present). Recorded as a gap.

============================================================================
CITATION POSTURE (D3, LICENSE_POSTURE.md §2b)
============================================================================
Original Python implementing the documented method; do-file lines are cited as loci
("implements 04 L84-85"). No CLV do-file code is copied. The QJE repkit stays a local
input; methods are not copyrightable.

============================================================================
REUSE-WITH-CITATION (D5 extend-not-parallel doctrine)
============================================================================
Where ``45_build_clean_bank_panel.py`` (the existing kindred freeNIC builder) already
implements a spec rule for the HIST stratum, this module reproduces the SAME arithmetic
and cites it -- e.g. the equity rowtotal / COALESCE-guard (``45_build build_panel
L267-269``), the ``pivot_hist`` long->wide line-item set (``45_build L146-179``). The
divergence is documented per-cell (METHOD-CHOICE): ``45_build`` groups by
``(bank_id, year)`` (MAX per line item) whereas CLV's ``04`` is **row-wise**; this module
follows CLV's row-wise derivation and records the choice.

Runtime deps: pandas + pyreadstat (Stata reader) + numpy. Pure-functional core (the
``reconstruct_* / override_* / hist_ratios / deflate`` functions are unit-tested with no
I/O); only ``main`` touches disk. NEVER writes to the warehouse. All paths absolute.
"""

from __future__ import annotations
import os

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pipeline.reconstruction import entity_spine, taxonomy  # noqa: E402

# ---------------------------------------------------------------------------
# Paths (all absolute; pathlib / forward-slash per filepath-safety rule)
# ---------------------------------------------------------------------------
#: The authors' exact raw OCR output -- PREFERRED input over the warehouse twin
#: ``occ_historical`` (source='occ_historical_clv'), which is its ingested long-format
#: copy. We read the .dta directly so no warehouse round-trip can perturb a value
#: (SPEC §0; task directive "prefer the .dta, note the choice").
DTA_PATH = Path(os.environ.get("FREENIC_INPUTS", "Inputs") + "/clv_historical_call/historical-call.dta")

#: GFD CPI (Dec-31 annual), the CLV deflator basis (``02_import_GFD_CPI.do L23-30``).
#: Extracted read-only from the QJE repkit to the campaign scratchpad; carries columns
#: ``year`` + ``cpi_gfd``. If absent, real twins are emitted NULL (honest absence).
CPI_PATH_CANDIDATES = (
    Path(os.environ.get("FREENIC_INPUTS", "Inputs") + "/luck_database/GFD/US_CPI_GFD_annual.dta"),
    Path(os.environ.get("FREENIC_SCRATCH", "scratch") + "/US_CPI_GFD_annual.dta"),
)

OUT_DIR = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction")
OUT_PARQUET = OUT_DIR / "finhist_equivalent_1863_1941.parquet"
OUT_META = OUT_DIR / "finhist_equivalent_1863_1941_BUILD_META.json"

HIST_YEAR_MIN = 1863
HIST_YEAR_MAX = 1941

# ---------------------------------------------------------------------------
# Column groups (verbatim from 04_create-historical-dataset.do)
# ---------------------------------------------------------------------------
#: interbank components -- ``04 L68`` (NB: due_to_ra is NOT in CLV's list).
INTERBANK_COLS = (
    "due_to_nb", "due_to_other_nb", "due_to_sb", "due_to_tc_and_sb",
    "due_to_banks", "due_to_banks_and_other_liabs",
)
#: liquid components (15) -- ``04 L72-74``.
LIQUID_COLS = (
    "bills_nb", "bills_sb", "checks_and_other", "currency", "legal_tender", "specie",
    "due_from_nb", "due_from_ra", "due_from_other_nb", "due_from_other_nb_and_sb",
    "due_from_sb", "bonds_dep", "bonds_hand", "cash_exchange_and_reserve", "cash_and_exchange",
)
#: liquid override components for 1905-1935 -- ``04 L80-81``.
LIQUID_OVERRIDE_COLS = ("cash_and_exchange", "frb_reserve", "cash_exchange_and_reserve")
#: equity components -- ``04 L84-85``.
EQUITY_COLS = ("capital", "surplus", "undivided_profits", "surplus_and_undivided_profits")
#: total_deposits components -- ``04 L98``.
TOTAL_DEPOSITS_COLS = (
    "us_deposits", "usdo_deposits", "individual_deposits",
    "demand_deposits", "time_deposits", "deposits",
)

#: The exact set of raw columns this build reads (usecols -> fast Stata read).
_IDENTITY_COLS = (
    "bank_id", "charter", "year", "bank_name", "call_date", "state_abbrev", "city_name",
    "is_filled_in", "is_ambiguous", "bs_merge", "ok_bs", "approx_ok_bs",
)
_PASSTHRU_COLS = (
    "assets", "loans", "securities", "securities_other", "securities_usgov",
    "oreo_and_mortgages", "capital", "surplus", "undivided_profits",
    "surplus_and_undivided_profits", "notes_nb", "bills_payable", "rediscounts",
    "deposits", "us_deposits", "usdo_deposits", "individual_deposits",
    "demand_deposits", "time_deposits", "lawful_money", "bonds_circ", "frb_reserve",
)


def _needed_columns() -> list[str]:
    cols: list[str] = []
    for grp in (_IDENTITY_COLS, _PASSTHRU_COLS, INTERBANK_COLS, LIQUID_COLS):
        for c in grp:
            if c not in cols:
                cols.append(c)
    return cols


#: The ~30-var nominal list CLV deflates by cpi_gfd (``07 L26-31``), restricted to the
#: columns that exist in the HIST era (modern-only vars dropped). ``var = var / cpi_gfd``.
DEFLATE_VARS = (
    "assets", "deposits", "loans", "interbank", "liquid", "oreo", "equity", "emergency",
    "capital", "bonds_circ", "rediscounts", "bills_payable", "undivided_profits",
    "surplus", "securities_other", "demand_deposits", "time_deposits", "notes_nb",
    "surplus_profit", "res_funding", "total_deposits",
)

#: BVX crisis years (``07 L52-55``) -- HIST-relevant subset lives in 1863-1941.
CRISIS_BVX_YEARS = frozenset({1873, 1884, 1890, 1893, 1907, 1930, 1984, 1990, 2007})

#: 07's validity filter (``07 L143-147``): these RATIOs -> missing if <0 or >1. NB: CLV's
#: list also names the LEVEL ``surplus_profit``; that blanking only makes sense on the
#: deflated *combined* panel (``07``) and would destroy the standalone level here, so it is
#: reproduced downstream in build_clv_analysis_panel, NOT applied to the level in this
#: finhist-level builder (documented in _BUILD_META).
VALIDITY_FILTER_RATIOS = (
    "leverage", "liquid_ratio", "oreo_ratio", "deposit_ratio", "noncore_ratio",
    "time_ratio", "profits_ratio", "profit_shortfall", "demand_ratio",
)


# ===========================================================================
# Pure-functional core (unit-tested; no I/O). Stata egen semantics replicated.
# ===========================================================================
def rowtotal(df: pd.DataFrame, cols: Sequence[str], *, missing_if_all_na: bool = False) -> pd.Series:
    """Stata ``egen rowtotal(cols)`` semantics: sum treating missing as 0.

    Default (``missing_if_all_na=False``) matches bare ``egen rowtotal`` -- an all-missing
    row returns **0** (used for interbank ``04 L68`` and total_deposits ``04 L98``, which
    have no follow-up missing mask). ``missing_if_all_na=True`` replicates the explicit
    ``replace X = . if <all components missing>`` lines CLV adds for liquid (L76-78),
    equity (L85), surplus_profit (L88) and emergency (L95).

    Only columns present in ``df`` are summed; a named-but-absent component contributes 0
    (Stata would error, but a robust reproduction records the absence upstream and does not
    fabricate). SPEC §2.
    """
    present = [c for c in cols if c in df.columns]
    if not present:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    block = df[present].apply(pd.to_numeric, errors="coerce")
    total = block.sum(axis=1, skipna=True).astype("float64")
    if missing_if_all_na:
        all_na = block.isna().all(axis=1)
        total = total.mask(all_na, other=np.nan)
    return total


def reconstruct_interbank(df: pd.DataFrame) -> pd.Series:
    """interbank = rowtotal(6 due_to_* items). ``04 L68`` (no missing mask -> 0 if all NA).

    Footnote-9 caveat (``04 L63-67``): 1905-1920 pools unsecured interbank funding WITH
    other liabilities in one line item, so the measure over-states for those years -- a
    documented data property, carried as-is (SPEC §2.13). implements 04 L68.
    """
    return rowtotal(df, INTERBANK_COLS, missing_if_all_na=False)


def reconstruct_liquid(df: pd.DataFrame, year: pd.Series) -> pd.Series:
    """liquid assets, with the 1905-1935 override. implements 04 L72-82.

    Base = rowtotal(15 cash/specie/due-from items), set missing iff ALL 15 missing
    (``04 L76-78``); then for ``inrange(year,1905,1935)`` OVERRIDDEN to
    ``rowtotal(cash_and_exchange, frb_reserve, cash_exchange_and_reserve)`` (``04 L80-81``).
    """
    base = rowtotal(df, LIQUID_COLS, missing_if_all_na=True)
    override = rowtotal(df, LIQUID_OVERRIDE_COLS, missing_if_all_na=False)
    y = pd.to_numeric(year, errors="coerce")
    in_window = y.between(1905, 1935)
    return base.mask(in_window, other=override)


def reconstruct_equity(df: pd.DataFrame) -> pd.Series:
    """equity = rowtotal(capital, surplus, undivided_profits, surplus_and_undivided_profits),
    missing iff all four missing. implements 04 L84-85.

    REUSE-WITH-CITATION: ``45_build build_panel L267-269`` builds the same equity with a
    COALESCE guard that only adds ``surplus_and_undivided_profits`` when both ``surplus``
    and ``undivided_profits`` are NULL (the 1900-1933 double-count fix). This function
    reproduces CLV's UNCONDITIONAL egen rowtotal (``04``); the guard is a documented
    METHOD-CHOICE that differs ONLY in the overlap years where the combined item duplicates
    the split items (SPEC §2.11). See :func:`reconstruct_equity_freenic_guard`.
    """
    return rowtotal(df, EQUITY_COLS, missing_if_all_na=True)


def reconstruct_equity_freenic_guard(df: pd.DataFrame) -> pd.Series:
    """freeNIC METHOD-CHOICE equity: capital + surplus + undivided_profits, adding
    surplus_and_undivided_profits ONLY when both surplus and undivided_profits are NULL.

    Reproduces ``45_build build_panel L267-269`` (the 1900-1933 equity COALESCE fix). Used
    only to CROSS-CHECK the anchor cells against the materialized ``clean_bank_panel``
    (SPEC §2.11 METHOD-CHOICE). Not the primary output column.
    """
    cap = pd.to_numeric(df.get("capital"), errors="coerce")
    sur = pd.to_numeric(df.get("surplus"), errors="coerce")
    und = pd.to_numeric(df.get("undivided_profits"), errors="coerce")
    sau = pd.to_numeric(df.get("surplus_and_undivided_profits"), errors="coerce")
    both_split_na = sur.isna() & und.isna()
    guard = sau.where(both_split_na, other=0.0).fillna(0.0)
    eq = cap.fillna(0.0) + sur.fillna(0.0) + und.fillna(0.0) + guard
    all_na = cap.isna() & sur.isna() & und.isna() & sau.isna()
    return eq.mask(all_na, other=np.nan)


def reconstruct_surplus_profit(df: pd.DataFrame, year: pd.Series) -> pd.Series:
    """surplus_profit = rowtotal(surplus, undivided_profits), missing iff both missing;
    REPLACED by surplus_and_undivided_profits for 1918-28 and 1905-07. implements 04 L87-90.
    """
    sp = rowtotal(df, ("surplus", "undivided_profits"), missing_if_all_na=True)
    sau = pd.to_numeric(df.get("surplus_and_undivided_profits"), errors="coerce")
    y = pd.to_numeric(year, errors="coerce")
    repl = y.between(1918, 1928) | y.between(1905, 1907)
    return sp.mask(repl, other=sau)


def reconstruct_emergency(df: pd.DataFrame) -> pd.Series:
    """emergency = rowtotal(bills_payable, rediscounts), missing iff both missing.
    implements 04 L94-95 ("after 1929 both reported as one; take the sum throughout").
    """
    return rowtotal(df, ("bills_payable", "rediscounts"), missing_if_all_na=True)


def reconstruct_total_deposits(df: pd.DataFrame) -> pd.Series:
    """total_deposits = rowtotal(us, usdo, individual, demand, time, deposits). implements
    04 L98. NB: uses the RAW ``deposits`` column (computed BEFORE the override at L100-106)
    and has NO missing mask (0 when all six missing).
    """
    return rowtotal(df, TOTAL_DEPOSITS_COLS, missing_if_all_na=False)


def override_deposits(df: pd.DataFrame, year: pd.Series) -> pd.Series:
    """deposits era-override. implements 04 L100-106.

      * 1915-1928: deposits = (demand_deposits + time_deposits), set MISSING iff both
        components missing, then MISSING if that sum == 0.
      * 1905-1914: deposits = individual_deposits.
      * otherwise (<1905 or >=1929): the RAW ``deposits`` column, unchanged.
    """
    raw = pd.to_numeric(df.get("deposits"), errors="coerce")
    dem = pd.to_numeric(df.get("demand_deposits"), errors="coerce")
    tim = pd.to_numeric(df.get("time_deposits"), errors="coerce")
    ind = pd.to_numeric(df.get("individual_deposits"), errors="coerce")
    y = pd.to_numeric(year, errors="coerce")

    dt_sum = dem.fillna(0.0) + tim.fillna(0.0)           # egen rowtotal(demand time)
    dt_sum = dt_sum.mask(dem.isna() & tim.isna(), other=np.nan)  # . if both missing (L101)

    out = raw.copy()
    w1928 = y.between(1915, 1928)
    out = out.mask(w1928, other=dt_sum)                  # L102
    out = out.mask(w1928 & (out == 0), other=np.nan)     # L103: . if 0 in 1915-28
    w1914 = y.between(1905, 1914)
    out = out.mask(w1914, other=ind)                     # L106
    return out


def approximate_bonds_circ(df: pd.DataFrame) -> pd.Series:
    """bonds_circ approximation. implements 04 L111-112.

    = raw bonds_circ; where missing and lawful_money present -> lawful_money; where still
    missing -> securities_usgov ("bonds to secure circulation").
    """
    bc = pd.to_numeric(df.get("bonds_circ"), errors="coerce")
    lm = pd.to_numeric(df.get("lawful_money"), errors="coerce")
    su = pd.to_numeric(df.get("securities_usgov"), errors="coerce")
    out = bc.copy()
    out = out.mask(bc.isna() & lm.notna(), other=lm)     # L111
    out = out.mask(out.isna(), other=su)                 # L112 (bonds_circ still missing)
    return out


def reconstruct_res_funding(
    df: pd.DataFrame, equity: pd.Series, total_deposits: pd.Series, interbank: pd.Series
) -> pd.Series:
    """res_funding = assets - rowtotal(equity, total_deposits, interbank, notes_nb),
    floored at 0. implements 04 L116-122.

    ``capital_deposits_notes`` set missing iff ``capital & notes_nb & deposits & interbank``
    all missing (CLV's mask uses the RAW capital/deposits, a documented quirk -- SPEC
    §2.18). REUSE-WITH-CITATION: ``45_build build_panel L294`` expresses the same residual
    as a ratio ``noncore_funding``.
    """
    assets = pd.to_numeric(df.get("assets"), errors="coerce")
    notes_nb = pd.to_numeric(df.get("notes_nb"), errors="coerce")
    cdn = (equity.fillna(0.0) + total_deposits.fillna(0.0)
           + interbank.fillna(0.0) + notes_nb.fillna(0.0))
    cap = pd.to_numeric(df.get("capital"), errors="coerce")
    dep = pd.to_numeric(df.get("deposits"), errors="coerce")
    mask_all_na = cap.isna() & notes_nb.isna() & dep.isna() & interbank.isna()
    cdn = cdn.mask(mask_all_na, other=np.nan)
    res = assets - cdn
    return res.mask(res < 0, other=0.0)                  # floor at 0 (L121)


def crisis_bvx(year: pd.Series) -> pd.Series:
    """crisisBVX dummy (``07 L52-55``): 1 for BVX crisis years, else 0."""
    y = pd.to_numeric(year, errors="coerce")
    return y.isin(CRISIS_BVX_YEARS).astype("int64")


def hist_ratios(panel: pd.DataFrame) -> pd.DataFrame:
    """Derived HIST ratios (``07``), computed on nominal levels.

    Ratios of two same-era levels are CPI-deflation-INVARIANT (``07`` deflates numerator and
    denominator by the same ``cpi_gfd``, which cancels), so computing them from nominal
    levels is bit-identical to CLV's post-deflation ratios -- documented in _BUILD_META.
    Only ``size`` (a log LEVEL) is deflation-sensitive and uses ``assets_real``.

    Reproduces the ``07`` clips/validity filter for the HIST-applicable ratios
    (``07 L138-147``). implements 07 L61-108, L138-147.
    """
    p = panel
    a = p["assets"]

    def _safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
        den = den.where(den != 0)
        return num / den

    out = pd.DataFrame(index=p.index)
    liquid = p["liquid"].mask(p["liquid"] == 0)                           # 07 L61
    out["liquid_ratio"] = _safe_div(liquid, a)                           # 07 L62
    out["leverage"] = _safe_div(p["equity"], a)                          # 07 L66
    out["leverage_capital"] = _safe_div(p["capital"], a)                 # 07 L68
    out["surplus_ratio"] = _safe_div(p["surplus_profit"], p["equity"])   # 07 L71
    out["equity_shortfall"] = (out["surplus_ratio"] <= 0.25).astype("float64")  # 07 L73
    out["profits_ratio"] = _safe_div(p["undivided_profits"], p["equity"])  # 07 L74
    out["profit_shortfall"] = (out["profits_ratio"] < 0.01).astype("float64")  # 07 L75
    out["oreo_ratio"] = _safe_div(p["oreo"], p["loans"] + p["oreo"])     # 07 L79
    out["loan_ratio"] = _safe_div(p["loans"], a)                         # 07 L82
    out["deposit_ratio"] = _safe_div(p["deposits"], a)                   # 07 L83
    out["deposit_ratio_alt"] = _safe_div(p["total_deposits"], a)         # 07 L84
    out["noncore_ratio"] = _safe_div(p["res_funding"], a)               # 07 L88 (year<=1941: res_funding form)
    emergency_borrowing = _safe_div(p["emergency"], a)                   # 07 L96
    y = pd.to_numeric(p["year"], errors="coerce")
    out["emergency_borrowing"] = emergency_borrowing.mask(y.between(1905, 1928))  # 07 L97
    out["interbank_ratio"] = _safe_div(p["interbank"], a)               # 07 L100
    time_ratio = _safe_div(p["time_deposits"], a)                        # 07 L102
    out["time_ratio"] = time_ratio.mask(p["time_deposits"] == 0)         # 07 L104
    demand_ratio = _safe_div(p["demand_deposits"], a)                    # 07 L107
    out["demand_ratio"] = demand_ratio.mask(p["demand_deposits"] == 0)   # 07 L108
    if "assets_real" in p.columns:
        ar = p["assets_real"].where(p["assets_real"] > 0)
        out["size"] = np.log(ar)                                         # 07 L47 (deflated assets)
    out["crisisBVX"] = crisis_bvx(p["year"])                             # 07 L52-55

    # 07 L143-147 validity filter: these ratios -> missing if <0 or >1.
    for col in VALIDITY_FILTER_RATIOS:
        if col in out.columns:
            bad = (out[col] > 1) | (out[col] < 0)
            out[col] = out[col].mask(bad & out[col].notna())
    return out


def deflate(panel: pd.DataFrame, cpi: pd.DataFrame, varlist: Iterable[str]) -> pd.DataFrame:
    """CPI real twins: ``var_real = var / cpi_gfd`` per year. implements 07 L25-34 + 02.

    ``cpi`` carries columns ``year`` + ``cpi_gfd`` (GFD Dec-31 annual, ``02 L23-30``). The
    paper states NO base year -- it deflates by the GFD-native index directly (SPEC §6.5,
    G-SPEC); we reproduce the raw ``/cpi_gfd`` division bit-for-bit. A year with no CPI (or
    cpi_gfd==0) yields NaN (honest absence, never fabricated).
    """
    merged = panel.merge(cpi[["year", "cpi_gfd"]], on="year", how="left")
    denom = merged["cpi_gfd"].where(merged["cpi_gfd"].astype("float64") != 0)
    out = pd.DataFrame(index=panel.index)
    out["cpi_gfd"] = merged["cpi_gfd"].to_numpy()
    for v in varlist:
        if v in panel.columns:
            out[f"{v}_real"] = (merged[v].to_numpy() / denom.to_numpy())
    return out


# ===========================================================================
# Assembly (I/O boundary)
# ===========================================================================
def _resolve_cpi_path() -> Path | None:
    for c in CPI_PATH_CANDIDATES:
        if c.exists():
            return c
    return None


def load_raw(dta_path: Path = DTA_PATH) -> pd.DataFrame:
    """Read the finhist raw balance sheets (PREFERRED over the warehouse twin), needed
    columns only. Restricts to the HIST window 1863-1941 (SPEC §0)."""
    import pyreadstat  # local import: only main() needs the Stata reader

    usecols = [c for c in _needed_columns()]
    df, _meta = pyreadstat.read_dta(str(dta_path), usecols=usecols)
    y = pd.to_numeric(df["year"], errors="coerce")
    df = df[y.between(HIST_YEAR_MIN, HIST_YEAR_MAX)].reset_index(drop=True)
    return df


def apply_dedup(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """The DERIVABLE dedup drop from ``04``: drop ``bs_merge==1`` (``04 L40``, "years where
    we couldn't find any call report"). The ``in_vl==1`` (L39) and ``days_to_failure<=0``
    (L54) drops are NOT-DERIVABLE from this file (columns absent) -> recorded, not applied.
    """
    info = {"rows_in": int(len(df))}
    if "bs_merge" in df.columns:
        bs = pd.to_numeric(df["bs_merge"], errors="coerce")
        dropped = int((bs == 1).sum())
        df = df[bs != 1].reset_index(drop=True)
        info["bs_merge_dropped"] = dropped
    else:
        info["bs_merge_dropped"] = None
    info["rows_out"] = int(len(df))
    info["not_derivable_drops"] = [
        "in_vl==1 (04 L39) -- in_vl column absent from public historical-call.dta",
        "days_to_failure<=0 (04 L54) -- receivership_date/call_date failure merge absent",
    ]
    return df, info


def build_panel(dta_path: Path = DTA_PATH, cpi_path: Path | None = None) -> tuple[pd.DataFrame, dict]:
    """Assemble the finhist-equivalent panel. Returns (panel, provenance_dict)."""
    raw = load_raw(dta_path)
    raw, dedup_info = apply_dedup(raw)

    year = pd.to_numeric(raw["year"], errors="coerce").astype("Int64")
    p = pd.DataFrame(index=raw.index)

    # --- identity / provenance columns -----------------------------------
    p["bank_id"] = pd.to_numeric(raw["bank_id"], errors="coerce").astype("Int64")
    p["charter"] = raw.get("charter")
    p["hist_panel_key"] = entity_spine.hist_panel_key(p["bank_id"])   # charter-pooled key
    p["year"] = year
    p["era_group"] = entity_spine.era_series(year)                    # all HIST here
    p["call_date"] = raw.get("call_date")
    p["bank_name"] = raw.get("bank_name")
    p["state_abbrev"] = raw.get("state_abbrev")
    p["city_name"] = raw.get("city_name")
    p["reconstruction_tier"] = "derivation-layer"                    # SPEC §0 / D5 §8
    p["src_vintage"] = "occ_historical_clv"
    p["unit_basis"] = "nominal_usd"
    for q in ("is_filled_in", "is_ambiguous", "bs_merge", "ok_bs", "approx_ok_bs"):
        if q in raw.columns:
            p[q] = raw[q]

    # --- pass-through OCC line items (occ_line_item) ----------------------
    p["assets"] = pd.to_numeric(raw.get("assets"), errors="coerce")
    p["loans"] = pd.to_numeric(raw.get("loans"), errors="coerce")           # ln_tot / loans
    p["securities"] = pd.to_numeric(raw.get("securities"), errors="coerce")
    p["securities_other"] = pd.to_numeric(raw.get("securities_other"), errors="coerce")
    p["oreo"] = pd.to_numeric(raw.get("oreo_and_mortgages"), errors="coerce")  # 04 L61 rename
    p["capital"] = pd.to_numeric(raw.get("capital"), errors="coerce")
    p["surplus"] = pd.to_numeric(raw.get("surplus"), errors="coerce")
    p["undivided_profits"] = pd.to_numeric(raw.get("undivided_profits"), errors="coerce")
    p["notes_nb"] = pd.to_numeric(raw.get("notes_nb"), errors="coerce")
    p["bills_payable"] = pd.to_numeric(raw.get("bills_payable"), errors="coerce")
    p["rediscounts"] = pd.to_numeric(raw.get("rediscounts"), errors="coerce")
    p["demand_deposits"] = pd.to_numeric(raw.get("demand_deposits"), errors="coerce")
    p["time_deposits"] = pd.to_numeric(raw.get("time_deposits"), errors="coerce")

    # --- reconstructed aggregates (order matters: 04 computes total_deposits
    #     from RAW deposits BEFORE the override; res_funding last) ----------
    p["interbank"] = reconstruct_interbank(raw)                       # 04 L68
    p["liquid"] = reconstruct_liquid(raw, raw["year"])               # 04 L72-82
    p["equity"] = reconstruct_equity(raw)                            # 04 L84-85
    p["surplus_profit"] = reconstruct_surplus_profit(raw, raw["year"])  # 04 L87-90
    p["emergency"] = reconstruct_emergency(raw)                      # 04 L94-95
    p["total_deposits"] = reconstruct_total_deposits(raw)           # 04 L98 (raw deposits)
    p["deposits"] = override_deposits(raw, raw["year"])            # 04 L100-106
    p["bonds_circ"] = approximate_bonds_circ(raw)                   # 04 L111-112
    p["res_funding"] = reconstruct_res_funding(                      # 04 L116-122
        raw, p["equity"], p["total_deposits"], p["interbank"])

    # --- CPI deflation (real twins) --------------------------------------
    cpi_path = cpi_path or _resolve_cpi_path()
    cpi_info: dict = {"cpi_path": str(cpi_path) if cpi_path else None}
    if cpi_path and Path(cpi_path).exists():
        import pyreadstat
        cpi, _ = pyreadstat.read_dta(str(cpi_path))
        cpi = cpi[["year", "cpi_gfd"]].copy()
        cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce").astype("Int64")
        real = deflate(p, cpi, DEFLATE_VARS)
        p = pd.concat([p, real], axis=1)
        cpi_info["deflated_vars"] = [v for v in DEFLATE_VARS if v in p.columns]
        cpi_info["cpi_source"] = "GFD US_CPI_GFD_annual (Dec-31), 02 L23-30; var/cpi_gfd (07 L26-34)"
    else:
        cpi_info["deflated_vars"] = []
        cpi_info["cpi_source"] = "ABSENT -- real twins omitted (honest absence)"
        print("[WARN] CPI file absent; real twins omitted.", file=sys.stderr)

    # --- derived ratios (07) ---------------------------------------------
    ratios = hist_ratios(p)
    p = pd.concat([p, ratios], axis=1)

    prov = {
        "dedup": dedup_info,
        "cpi": cpi_info,
        "gaps_not_derivable": [
            "OCR digitization (microfilm->digits) -- physical OCC archives, finhist 1/2/3-*.do (SPEC §0)",
            "age / log_age (04 L129-130) -- charter_date absent from public historical-call.dta",
            "failure layer: failed_bank / time_to_fail / receivership_date / transient version-id "
            "(04 L10-54) -- end_date/end_has_receivership/in_vl absent; belongs to 06 + occ-receiverships",
        ],
    }
    return p, prov


# ===========================================================================
# Self-smoke: 6 anchor cells vs the best available published-equivalent reference
# ===========================================================================
def _clean_panel_anchor(bank_id: int, year: int, col: str) -> float | None:
    """Look up a HIST cell in the materialized ``clean_bank_panel.parquet`` (freeNIC's
    already-shipped finhist-equivalent HIST stratum, built from the SAME occ_historical).
    The CLV *built* hist output (``$temp/call-reports-historical.dta``) is a Stata temp and
    is NOT shipped in the repkit, so this materialized panel is the closest published-grade
    reference for the pass-throughs + the equity rowtotal."""
    cbp = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/clean_bank_panel.parquet")
    if not cbp.exists():
        return None
    df = pd.read_parquet(cbp, columns=["bank_id", "year", "era_group", col])
    m = df[(df["era_group"] == "HIST") & (df["bank_id"] == bank_id) & (df["year"] == year)]
    if m.empty:
        return None
    return float(m[col].iloc[0])


def self_smoke(panel: pd.DataFrame) -> list[dict]:
    """6 anchor cells, each classified with the pre-registered taxonomy.

    Anchors 1-4 (assets, loans, securities, notes_nb): raw pass-throughs -> cross-checked
    against ``clean_bank_panel`` *_nominal (== the raw occ_historical value). Anchor 5
    (equity): our unconditional rowtotal vs clean_bank_panel's COALESCE-guard equity_nominal
    (EXACT in clean years where surplus_and_undivided_profits is null; METHOD-CHOICE in the
    1900-1933 overlap). Anchor 6 (res_funding): internal-consistency -- the reconstructed
    residual recomputed from the panel's own levels must match the stored column.
    """
    bank_id, year = 1461, 1929   # occ 1929 largest bank (unit-gate anchor)
    row = panel[(panel["bank_id"] == bank_id) & (panel["year"] == year)]
    anchors: list[dict] = []

    def _add(name, built, published, ulp, ref):
        cls = taxonomy.classify(published, built, ulp)
        anchors.append({"anchor": name, "bank_id": bank_id, "year": year,
                        "built": None if built is None else float(built),
                        "published": None if published is None else float(published),
                        "class": cls, "reference": ref})

    if row.empty:
        anchors.append({"anchor": "ROW_PRESENT", "bank_id": bank_id, "year": year,
                        "built": None, "published": None, "class": taxonomy.UNEXPLAINED,
                        "reference": "anchor bank-year missing from build"})
        return anchors

    r = row.iloc[0]
    for name, built_col, cbp_col in (
        ("assets", "assets", "assets_nominal"),
        ("loans", "loans", "loans_nominal"),
        ("notes_nb", "notes_nb", "notes_nb_nominal"),
        ("equity", "equity", "equity_nominal"),
    ):
        built = r[built_col]
        built = None if pd.isna(built) else float(built)
        pub = _clean_panel_anchor(bank_id, year, cbp_col)
        ref = f"clean_bank_panel.{cbp_col} (freeNIC HIST stratum, 45_build)"
        _add(name, built, pub, 1.0, ref)

    # securities: the anchor bank-year (1461/1929) reports no unified 'securities' line, so
    # use a securities-PRESENT cell (bank 1, 1889 = $554,359.54) for a non-trivial pass-through.
    s_bid, s_yr = 1, 1889
    s_row = panel[(panel["bank_id"] == s_bid) & (panel["year"] == s_yr)]
    s_built = None if s_row.empty or pd.isna(s_row["securities"].iloc[0]) else float(s_row["securities"].iloc[0])
    s_pub = _clean_panel_anchor(s_bid, s_yr, "securities_nominal")
    anchors.append({"anchor": "securities", "bank_id": s_bid, "year": s_yr,
                    "built": s_built, "published": None if s_pub is None else float(s_pub),
                    "class": taxonomy.classify(s_pub, s_built, 1.0),
                    "reference": "clean_bank_panel.securities_nominal (freeNIC HIST stratum, 45_build)"})

    # Anchor 6: res_funding internal consistency (assets - (eq+totdep+ib+notes), floor 0).
    eq = 0.0 if pd.isna(r["equity"]) else float(r["equity"])
    td = 0.0 if pd.isna(r["total_deposits"]) else float(r["total_deposits"])
    ib = 0.0 if pd.isna(r["interbank"]) else float(r["interbank"])
    nn = 0.0 if pd.isna(r["notes_nb"]) else float(r["notes_nb"])
    assets = float(r["assets"])
    recomputed = max(assets - (eq + td + ib + nn), 0.0)
    built_rf = None if pd.isna(r["res_funding"]) else float(r["res_funding"])
    _add("res_funding", built_rf, recomputed, 1.0,
         "internal: assets-(equity+total_deposits+interbank+notes_nb), floor 0 (04 L116-122)")
    return anchors


# ===========================================================================
# main
# ===========================================================================
def _d5_note() -> dict:
    """The D5 recommendation for Batch-5 warehouse integration (consumed by the
    warehouse-integration agent). Extend clean_bank_panel's HIST stratum; do NOT build a
    parallel table (SPEC §8)."""
    return {
        "recommendation": (
            "EXTEND clean_bank_panel's HIST stratum with these CLV-derived columns as a "
            "'derived layer' over the existing (era_group, entity, year) spine; do NOT build "
            "a parallel finhist_equivalent table (SPEC §8, plan §B3, D5 default)."
        ),
        "new_columns_to_add": {
            "interbank": "reconstructed_agg (04 L68); tier=derivation-layer",
            "liquid": "reconstructed_agg (04 L72-82); tier=derivation-layer",
            "emergency": "reconstructed_agg (04 L94-95); tier=derivation-layer",
            "surplus_profit": "reconstructed_agg (04 L87-90); tier=derivation-layer",
            "total_deposits": "reconstructed_agg (04 L98); tier=derivation-layer "
                              "(NB CLV form differs from clean_bank_panel.total_deposits_hist METHOD-CHOICE)",
            "deposits (CLV override)": "reconstructed_agg (04 L100-106); tier=derivation-layer "
                                       "(distinct from clean_bank_panel.deposits_clean COALESCE form METHOD-CHOICE)",
            "bonds_circ": "reconstructed_agg (04 L111-112); tier=derivation-layer",
            "res_funding": "reconstructed_agg (04 L116-122); tier=derivation-layer "
                           "(clean_bank_panel carries the ratio noncore_funding L294; add the LEVEL)",
            "surplus_ratio / profits_ratio / emergency_borrowing / interbank_ratio / "
            "deposit_ratio_alt / leverage_capital": "derived_ratio (07); tier=derivation-layer",
        },
        "provenance_tier_column": "reconstruction_tier IN ('independent','derivation-layer','not-derivable')",
        "join_key": "(bank_id, year) on era_group='HIST' -- charter-pooled hist_panel_key",
        "already_present_in_clean_bank_panel": [
            "assets_nominal, loans_nominal, securities_nominal, notes_nb_nominal, equity_nominal "
            "(equity via COALESCE-guard METHOD-CHOICE vs CLV unconditional rowtotal -- reconcile in overlap years)",
        ],
    }


def main() -> int:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=== build_finhist_equivalent (1863-1941 derivation-layer) ===", flush=True)

    panel, prov = build_panel()
    anchors = self_smoke(panel)

    panel = panel.sort_values(["bank_id", "year", "call_date"], na_position="first",
                              kind="stable").reset_index(drop=True)
    panel.to_parquet(OUT_PARQUET, index=False)

    n_rows = int(len(panel))
    n_entities = int(panel["bank_id"].nunique())
    span = [int(panel["year"].min()), int(panel["year"].max())]
    matched = sum(1 for a in anchors if a["class"] in taxonomy.MATCH_CLASSES)

    meta = {
        "table": "finhist_equivalent_1863_1941",
        "description": ("finhist / OCC-historical derivation-layer panel (1863-1941): the "
                        "authors' digitized raw -> CLV's published derived schema, original "
                        "Python implementing 04_create-historical-dataset.do. OCR is NOT-DERIVABLE."),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "build_script": "pipeline/reconstruction/build_finhist_equivalent.py",
        "input": {
            "dta_path": str(DTA_PATH),
            "preferred_over": "warehouse occ_historical (source='occ_historical_clv') -- read .dta directly",
            "rows_read_1863_1941": prov["dedup"]["rows_in"],
            "rows_after_bs_merge_drop": prov["dedup"]["rows_out"],
        },
        "output": {"parquet": str(OUT_PARQUET), "rows": n_rows,
                   "entities_bank_id": n_entities, "year_span": span},
        "chain_implemented": {
            "pass_through_occ_line_items": ["assets", "loans", "securities", "securities_other",
                                            "oreo(04 L61)", "capital", "surplus", "undivided_profits",
                                            "notes_nb", "bills_payable", "rediscounts",
                                            "demand_deposits", "time_deposits"],
            "reconstructed_aggregates": {
                "interbank": "04 L68", "liquid": "04 L72-82", "equity": "04 L84-85",
                "surplus_profit": "04 L87-90", "emergency": "04 L94-95",
                "total_deposits": "04 L98", "deposits_override": "04 L100-106",
                "bonds_circ": "04 L111-112", "res_funding": "04 L116-122",
            },
            "derived_ratios": "07 L61-108 + clips/validity filter L138-147 "
                              "(computed on nominal levels; ratios are CPI-deflation-invariant)",
            "deflation": prov["cpi"]["cpi_source"],
            "entity_key": "hist_panel_key = bank_id (charter-pooled; version transient/dropped, G-SPEC)",
        },
        "reuse_with_citation": {
            "45_build_clean_bank_panel.py": [
                "equity rowtotal/COALESCE-guard L267-269 (reproduced as METHOD-CHOICE cross-check)",
                "pivot_hist line-item set L146-179 (same OCC variable_ids)",
                "res_funding residual as ratio noncore_funding L294",
            ],
            "note": "CLV 04 is ROW-WISE; clean_bank_panel groups by (bank_id,year) MAX -- METHOD-CHOICE, documented.",
        },
        "gaps_not_derivable": prov["gaps_not_derivable"],
        "documented_07_behavior_not_applied_here": (
            "07 L143 lists the LEVEL surplus_profit in the >1/<0 validity filter; that "
            "blanking only makes sense on the deflated combined panel and would destroy the "
            "standalone level -- reproduced downstream in build_clv_analysis_panel, not here."
        ),
        "self_smoke_anchors": anchors,
        "self_smoke_matched": f"{matched}/{len(anchors)}",
        "taxonomy_gate_finhist": taxonomy.GATE_FINHIST,
        "d5_note_batch5_warehouse_integration": _d5_note(),
        "citation_posture": "original Python implementing CLV documented method; no do-file code copied (D3).",
    }
    OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"rows={n_rows:,}  entities={n_entities:,}  span={span[0]}-{span[1]}")
    print(f"bs_merge dropped: {prov['dedup']['bs_merge_dropped']}")
    print(f"deflated vars: {len(prov['cpi']['deflated_vars'])}")
    print(f"self-smoke: {matched}/{len(anchors)} matched")
    for a in anchors:
        print(f"  [{a['class']:<12}] {a['anchor']:<12} built={a['built']} published={a['published']}")
    print(f"WROTE {OUT_PARQUET}")
    print(f"WROTE {OUT_META}")
    print(f"done in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
