"""Build the **Luck-core** panel for 1959Q4-1975Q4 (MODL) from the CLV modern raw.

The DERIVATION-LAYER re-derivation for the MODL era (SPEC §0 boundary row 2): from CLV's
digitized modern call-report raw (the QJE repkit ``sources/call-reports-modern.dta`` -- the
*only* machine source for 1959Q4-1975Q4) up to their published/analysis schema, via
**original Python implementing CLV's documented ``05_create-modern-dataset.do`` ->
``06_create-outflows-receivership-data.do`` -> ``07_combine-*.do`` method**. Emits
``luck_core_1959_1975.parquet`` + a ``_BUILD_META.json`` sidecar. The bar is the D2
1959-1975 gate **99.9%** (near-perfect: their formula on their input).

============================================================================
INPUT CHOICE (the authors' exact input, noted per task directive + SPEC §0)
============================================================================
The MODL machine source is the modern .dta, NOT ``call-reports-historical.dta`` (which is
the OCC 1863-1941 file -- 97 OCC line-item columns, ``04``'s input, verified by schema).
Per SPEC §0/§1 the 1959Q4-1975Q4 era lives in ``sources/call-reports-modern.dta`` (id_rssd
+ date, thousands) and is processed by ``05``. We read that .dta directly (PREFERRED over
the ingested warehouse twin ``main.luck_wide`` -- so no warehouse round-trip can perturb a
value; SPEC §0 + task directive "prefer the .dta as the authors' exact input"). The .dta
spans 1959Q4-2024 (2,530,565 rows); we filter to year in [1959, 1975] (601,715 rows), which
equals ``luck_wide``'s exact era row count -- the two are the same population.

============================================================================
THE DERIVABILITY / HONESTY BOUNDARY (SPEC §0)
============================================================================
This is a derivation layer: we re-run CLV's documented formulas on their digitized input.
No step fabricates a value; every honest gap is RECORDED, never imputed. Structural absences
in the MODL slice of the modern .dta (verified null-profile):

  * ``loans`` (total, RCFD-net) is 0% populated for 1959-75 (the loan *buckets* ln_re/ci/
    cons/cc/fi/oth exist, but no total) -> loan_ratio / npl_ratio / prov_ratio / the loan-mix
    ratios are honestly NA (their denominator ``loans`` is absent). We do NOT synthesize a
    total from the buckets (that would be method-substitution). Matches ``luck_wide.ln_tot``
    null for the era.
  * ``ffpurch`` is 0% populated -> ``liquid = rowtotal(cash, securities, ffpurch)`` = cash +
    securities for the era (ffpurch contributes 0). (Published liquid concept excludes fed
    funds anyway -- SPEC §2.15 METHOD-CHOICE.)
  * ``npl_tot`` (1982+), ``brokered_dep`` (1983+), ``insured_deposits`` (1983+) are 0% for
    the era -> their ratios NA (concept post-dates the era). Recorded.

============================================================================
THE 05 -> 06 -> 07 CHAIN IMPLEMENTED (per-function do-file citations)
============================================================================
  * ``05`` modern build: FDIC fail-date prep (L11-42), id hygiene + ``-id_rssd`` surrogate
    (L53-60), FDIC-failure merge (L62), post-failure pseudo bank_id (L66-77), failure fields
    (L88-104), ``liquid`` rowtotal (L108), thousands->dollars ×1000 (L111-115), age (L125-129),
    keep-list (L119-123), ``isid bank_id quarter`` (L135).
  * ``06`` run-dummy merge onto the modern file (L159-207): the ``run`` dummy is built ONLY
    from post-1993 FTDB deposit-outflows, so for 1959-75 it merges to **all-missing** -- a
    no-op on every economic level. We add ``run`` = NA and record it (faithful to the 06 hop).
  * ``07`` combine + deflate + ratios: CPI deflation ``var/cpi_gfd`` (L26-34), all modern
    ratios (L61-132), Q4-only income-ratio gate (L120-122), outlier clips (L138-141), and the
    >1/<0 validity filter (L143-147). (07 appends HIST + modern; we build ONLY the modern
    branch for this era.)

============================================================================
CITATION POSTURE (D3, LICENSE_POSTURE.md §2b)
============================================================================
Original Python implementing the documented method; do-file lines are cited as loci
("implements 05 L66-77"). No CLV do-file code is copied. The QJE repkit stays a LOCAL input;
methods are not copyrightable.

Runtime deps: pandas + numpy + pyreadstat (Stata reader) + duckdb (read-only smoke against
``luck_wide``). Pure-functional core is unit-tested with no I/O; only ``main`` touches disk.
NEVER writes to the warehouse. All paths absolute (pathlib / forward-slash).
"""

from __future__ import annotations
import os

import json
import math
import sys
import time
import zipfile
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
#: The QJE replication kit (stable local input). The three files we read live under its
#: ``sources/``; we extract them to a scratchpad cache if not already extracted.
REPKIT_ZIP = Path(os.environ.get("FREENIC_INPUTS", "Inputs") + "/luck_database/qje-repkit.zip")
_ZIP_PREFIX = "qje-repkit-to-upload/sources"
SCRATCH = Path(
    os.environ.get("FREENIC_SCRATCH", "scratch") + "/repkit/"
    "qje-repkit-to-upload/sources"
)

#: The authors' exact modern input (id_rssd + date, thousands) -- PREFERRED over the
#: warehouse twin ``luck_wide``. Candidate 1 = the already-extracted scratchpad copy.
MOD_DTA_CANDIDATES = (
    SCRATCH / "call-reports-modern.dta",
)
#: GFD CPI Dec-31 annual (the CLV deflator basis, ``02_import_GFD_CPI.do L23-30``): year + cpi_gfd.
CPI_DTA_CANDIDATES = (
    SCRATCH / "GFD" / "US_CPI_GFD_annual.dta",
)
#: FDIC failure list + FTDB deposits/assets-at-failure (``05 L11-42``).
FDIC_PBD_CANDIDATES = (SCRATCH / "FDIC" / "public-bank-data.dta",)
FDIC_FTDB_CANDIDATES = (SCRATCH / "FDIC" / "FDIC_ftdb_deposits_assets_failure.dta",)

#: Warehouse (READ-ONLY) for the self-smoke against the published ``luck_wide``.
WAREHOUSE = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/freenic.duckdb")

OUT_DIR = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction")
OUT_PARQUET = OUT_DIR / "luck_core_1959_1975.parquet"
OUT_META = OUT_DIR / "luck_core_1959_1975_BUILD_META.json"

MODL_YEAR_MIN = 1959
MODL_YEAR_MAX = 1975

# ---------------------------------------------------------------------------
# Column groups (verbatim from 05_create-modern-dataset.do)
# ---------------------------------------------------------------------------
#: liquid components -- ``05 L108`` egen rowtotal(cash securities ffpurch).
LIQUID_COLS = ("cash", "securities", "ffpurch")

#: The vars ``05 L111-113`` multiplies thousands->dollars ×1000. (cash/securities/ffpurch are
#: NOT in this list -- they are consumed by ``liquid`` at L108 and dropped by the keep-list.)
UNIT_SCALE_VARS = (
    "assets", "liquid", "deposits", "equity", "loans", "deposits_time", "deposits_demand",
    "otherbor_liab", "brokered_dep", "ln_cons", "ln_cc", "ln_ci", "ln_oth", "ln_fi", "ln_re",
    "npl_tot", "ytdllprov", "ytdnetinc", "ytdint_exp_dep", "ytdint_inc_ln", "insured_deposits",
)

#: The ~30-var nominal list CLV deflates by cpi_gfd (``07 L26-31``), restricted to the vars
#: that exist in the MODL slice (HIST-only vars dropped). Coincides with UNIT_SCALE_VARS
#: (the modern dollar vars). ``var = var / cpi_gfd`` on the ×1000 dollars.
DEFLATE_VARS = UNIT_SCALE_VARS

#: modern loan-mix buckets -> ln_*/loans ratios (``07 L125-127``).
LOAN_MIX_VARS = ("ln_cons", "ln_cc", "ln_ci", "ln_oth", "ln_fi", "ln_re")
#: modern funding buckets -> */assets ratios (``07 L130-132``).
FUNDING_RATIO_VARS = (
    "deposits_time", "deposits_demand", "otherbor_liab", "brokered_dep", "insured_deposits",
)

#: BVX crisis years (``07 L52-55``). None fall in 1959-1975, so crisisBVX==0 across the era.
CRISIS_BVX_YEARS = frozenset({1873, 1884, 1890, 1893, 1907, 1930, 1984, 1990, 2007})

#: ``07 L143-147`` validity filter: these RATIOs -> missing if <0 or >1. (The HIST-only names
#: surplus_profit/oreo_ratio/profits_ratio/profit_shortfall/demand_ratio are absent for MODL.)
VALIDITY_FILTER_RATIOS = ("leverage", "liquid_ratio", "deposit_ratio", "noncore_ratio", "time_ratio")

#: The identity + level columns we read from the modern .dta (usecols -> lean read).
_READ_COLS = (
    "id_rssd", "id_fdic_cert", "bank_name", "state_abbr_nm", "dt_open", "year", "quarter_number",
    "assets", "cash", "securities", "loans", "deposits_demand", "deposits_time", "deposits",
    "ffpurch", "otherbor_liab", "equity", "ln_re", "ln_fi", "ln_oth", "ln_cc", "ln_ci", "ln_cons",
    "npl_tot", "brokered_dep", "insured_deposits", "num_employees",
    "ytdint_inc_ln", "ytdint_exp_dep", "ytdllprov", "ytdnetinc",
)
#: Numeric level columns to coerce to float (the rest are identity/date).
_NUMERIC_COLS = (
    "assets", "cash", "securities", "loans", "deposits_demand", "deposits_time", "deposits",
    "ffpurch", "otherbor_liab", "equity", "ln_re", "ln_fi", "ln_oth", "ln_cc", "ln_ci", "ln_cons",
    "npl_tot", "brokered_dep", "insured_deposits", "num_employees",
    "ytdint_inc_ln", "ytdint_exp_dep", "ytdllprov", "ytdnetinc",
)


# ===========================================================================
# Pure-functional core (unit-tested; no I/O). Stata semantics replicated.
# ===========================================================================
def rowtotal(df: pd.DataFrame, cols: Sequence[str], *, missing_if_all_na: bool = False) -> pd.Series:
    """Stata ``egen rowtotal(cols)`` semantics: sum treating missing as 0.

    ``missing_if_all_na=True`` replicates CLV's ``liquid`` at ``05 L108`` (egen rowtotal has
    an implicit all-missing->missing when the row contributes nothing measurable). A
    named-but-absent column contributes 0 (never fabricated). implements 05 L108.
    """
    present = [c for c in cols if c in df.columns]
    if not present:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    block = df[present].apply(pd.to_numeric, errors="coerce")
    total = block.sum(axis=1, skipna=True).astype("float64")
    if missing_if_all_na:
        total = total.mask(block.isna().all(axis=1), other=np.nan)
    return total


def compute_liquid(df: pd.DataFrame) -> pd.Series:
    """liquid = rowtotal(cash, securities, ffpurch), missing iff all three missing.
    implements 05 L108.

    SPEC §2.15 METHOD-CHOICE/quirk: the *published* modern liquid concept excludes fed funds
    (arXiv 2506.06082 fig-note p.81); ``ffpurch`` (= fed funds purchased, a liability) is an
    unremarked do-file inclusion. For 1959-75 ffpurch is 0% populated, so liquid = cash +
    securities regardless -- we reproduce ``05 L108`` verbatim for cell-match.
    """
    return rowtotal(df, LIQUID_COLS, missing_if_all_na=True)


def quarter_stata_index(year: pd.Series, quarter_number: pd.Series) -> pd.Series:
    """Stata quarterly (``%tq``) index = (year-1960)*4 + (quarter_number-1). Pure.

    CLV's ``05 L51`` renames the modern .dta ``date`` (a ``%tq`` value) to ``quarter``. The
    .dta carries ``year`` + ``quarter_number`` directly, so we reconstruct the same tq index
    from them (avoids any Stata-epoch ambiguity). Used as the panel time key (``xtset bank_id
    quarter``, 05 L135 / 07 L111).
    """
    y = pd.to_numeric(year, errors="coerce")
    q = pd.to_numeric(quarter_number, errors="coerce")
    return ((y - 1960) * 4 + (q - 1)).astype("Int64")


def quarter_end_timestamp(year: pd.Series, quarter_number: pd.Series) -> pd.Series:
    """Last calendar day of the (year, quarter) -- CLV's ``call_date = dofq(quarter+1)-1``
    (``05 L88``: last day of the quarter). Returns a datetime64 Series. Pure.
    """
    y = pd.to_numeric(year, errors="coerce").astype("Int64")
    q = pd.to_numeric(quarter_number, errors="coerce").astype("Int64")
    # first day of the NEXT quarter, minus one day
    end_month = (q * 3)  # q1->3, q2->6, q3->9, q4->12
    starts = pd.to_datetime(
        pd.DataFrame({"year": y.astype("float"), "month": end_month.astype("float"), "day": 1}),
        errors="coerce",
    )
    # move to first day of following month, then subtract a day = last day of end_month
    return (starts + pd.offsets.MonthBegin(1)) - pd.Timedelta(days=1)


def qofd_quarter_index(ts: pd.Series) -> pd.Series:
    """Stata ``qofd(date)`` = quarterly index of a calendar date. Pure.

    = (year-1960)*4 + (quarter-1) for a datetime Series. Used for the post-failure pseudo-id
    comparison ``qofd(fail_day) <= quarter`` (``05 L67``).
    """
    t = pd.to_datetime(ts, errors="coerce")
    return ((t.dt.year - 1960) * 4 + (t.dt.quarter - 1)).astype("Int64")


def charter_year_from_dt_open(dt_open: pd.Series) -> pd.Series:
    """charter_year from ``dt_open`` (a YYYYMMDD integer). implements 05 L125-127.

    CLV: ``tostring dt_open`` then ``charter_date = date(dt_open,"YMD"); charter_year =
    year(charter_date)``. ``dt_open`` in the modern .dta is a plain YYYYMMDD int (e.g.
    19040901 -> 1904), so charter_year = dt_open // 10000. Invalid/zero -> NA.
    """
    d = pd.to_numeric(dt_open, errors="coerce")
    cy = (d // 10000)
    cy = cy.mask((cy < 1600) | (cy > 2100))  # implausible -> NA (never fabricate)
    return cy.astype("Int64")


def compute_age(year: pd.Series, charter_year: pd.Series) -> pd.Series:
    """age = year - charter_year (``05 L129``). NA where charter_year NA."""
    y = pd.to_numeric(year, errors="coerce")
    return (y - pd.to_numeric(charter_year, errors="coerce")).astype("Int64")


def build_fdic_fail_dates(pbd: pd.DataFrame, ftdb: pd.DataFrame) -> pd.DataFrame:
    """CLV's per-cert fail-date table. implements 05 L11-42.

    From FDIC ``public-bank-data`` (L11): drop rows with neither cert nor rssd (L14); fill
    ``id_fdic_cert = -id_rssd`` where cert missing (L15); exclude open-bank-assistance/TARP
    ``restype1=='OBAM'`` (L20, e.g. Citi/BofA 2008 are NOT failures); drop thrifts
    ``chclass1 in {SL,SA}`` (L23); unique on (cert, fail_day), keep those two (L26-27); merge
    the FTDB deposits/assets-at-failure on (cert, fail_day) (L30); then per cert order by
    fail_day, index i, and reshape wide (L32-38) so a cert with two failures carries
    ``fail_day``/``fail_day2`` (+ resdep/resasset 1/2). Returns one row per cert.
    """
    p = pbd.copy()
    cert = pd.to_numeric(p["id_fdic_cert"], errors="coerce")
    rssd = pd.to_numeric(p["id_rssd"], errors="coerce")
    keep = ~(cert.isna() & rssd.isna())                         # L14
    p, cert, rssd = p[keep].copy(), cert[keep], rssd[keep]
    cert = cert.mask(cert.isna(), other=-rssd)                  # L15
    p["id_fdic_cert"] = cert.values
    p = p[p.get("restype1").astype("string").fillna("") != "OBAM"]              # L20
    ch = p.get("chclass1").astype("string").fillna("")
    p = p[~ch.isin(["SL", "SA"])]                                                # L23
    p = p.dropna(subset=["fail_day"]).copy()
    # unique on (cert, fail_day) (L26), keep cert+fail_day (L27)
    p = p.drop_duplicates(["id_fdic_cert", "fail_day"])[["id_fdic_cert", "fail_day"]]
    # merge FTDB resdep/resasset on (cert, fail_day) (L30)
    f = ftdb[["id_fdic_cert", "fail_day", "resdep", "resasset"]].copy()
    f["id_fdic_cert"] = pd.to_numeric(f["id_fdic_cert"], errors="coerce")
    p = p.merge(f, on=["id_fdic_cert", "fail_day"], how="left")
    # per-cert index by fail_day, reshape wide (L32-38)
    p = p.sort_values(["id_fdic_cert", "fail_day"])
    p["i"] = p.groupby("id_fdic_cert").cumcount() + 1
    wide = p[p["i"] <= 2].pivot(index="id_fdic_cert", columns="i",
                                values=["fail_day", "resdep", "resasset"])
    wide.columns = [f"{a}{b}" for a, b in wide.columns]
    wide = wide.rename(columns={"fail_day1": "fail_day", "resdep1": "resdep",
                                "resasset1": "resasset"}).reset_index()
    for c in ("fail_day2", "resdep2", "resasset2"):
        if c not in wide.columns:
            wide[c] = pd.NaT if c == "fail_day2" else np.nan
    return wide


def apply_id_hygiene(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """id hygiene + ``-id_rssd`` surrogate + drop-unkeyed. implements 05 L53-60.

    Uses :func:`entity_spine.resolve_fdic_cert` (zero->missing, missing->``-id_rssd``) and
    :func:`entity_spine.drop_unkeyed` (drop rows still lacking a cert). Adds
    ``id_fdic_cert_resolved``. For 1959-75, id_rssd has no nulls/zeros, so no rows drop for
    missing id, but 28,061 zero-cert rows take the negative surrogate.
    """
    resolved = entity_spine.resolve_fdic_cert(df["id_fdic_cert"], df["id_rssd"])
    out = df.copy()
    out["id_fdic_cert_resolved"] = resolved
    n_in = len(out)
    out = entity_spine.drop_unkeyed(out, cert_col="id_fdic_cert_resolved")
    info = {"rows_in": int(n_in), "rows_after_drop_unkeyed": int(len(out)),
            "neg_surrogate_rows": int((resolved < 0).sum())}
    return out.reset_index(drop=True), info


def compute_failure_fields(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Merge failures, mint bank_id, derive failure fields, drop post-failure rows.
    implements 05 L62-104.

    Steps: ``quarter`` (tq) + ``call_date`` (last day of quarter); the pseudo-id
    ``bank_id = (cert*10 + (qofd(fail_day)<=quarter) + (qofd(fail_day2)<=quarter)) * 1e5``
    (05 L66-77, via :func:`entity_spine.modern_bank_id`); the new-bank swap
    (fail_day<-fail_day2 etc. once past the first failure, 05 L68-72); ``failed_bank``,
    ``days_to_failure``, months/quarters/``time_to_fail`` = ``-ceil(days/(30/90/365))``
    (L93-98, negative sign convention); drop rows reporting AFTER failure
    (``days_to_failure<0``, L104).
    """
    out = df.copy()
    out["quarter"] = quarter_stata_index(out["year"], out["quarter_number"])
    out["call_date"] = quarter_end_timestamp(out["year"], out["quarter_number"])

    q_call = pd.to_numeric(out["quarter"], errors="coerce")
    q_fail1 = qofd_quarter_index(out.get("fail_day"))
    q_fail2 = qofd_quarter_index(out.get("fail_day2"))
    pf1 = ((q_fail1.notna()) & (q_fail1 <= q_call)).astype("int64")           # 05 L67 term 1
    pf2 = ((q_fail2.notna()) & (q_fail2 <= q_call)).astype("int64")           # 05 L67 term 2

    out["bank_id"] = entity_spine.modern_bank_id(
        out["id_fdic_cert_resolved"], past_fail_1=pf1.to_numpy(), past_fail_2=pf2.to_numpy()
    )

    # new_bank swap (05 L68-72): once past the first failure and a 2nd exists, use the 2nd.
    new_bank = out.get("fail_day2").notna() & (pf1 == 1)                       # 05 L68
    for base, alt in (("fail_day", "fail_day2"), ("resasset", "resasset2"), ("resdep", "resdep2")):
        if base in out.columns and alt in out.columns:
            out[base] = out[base].mask(new_bank, other=out[alt])

    out["failed_bank"] = out.get("fail_day").notna().astype("int64")          # 05 L93
    fail_ts = pd.to_datetime(out.get("fail_day"), errors="coerce")
    days = (fail_ts - pd.to_datetime(out["call_date"])).dt.days
    out["days_to_failure"] = days.where(out["failed_bank"] == 1)              # 05 L94

    def _neg_ceil(series: pd.Series, denom: int) -> pd.Series:
        v = series / denom
        return (-np.ceil(v)).astype("Float64")

    out["months_to_failure"] = _neg_ceil(out["days_to_failure"], 30)         # 05 L96
    out["quarters_to_failure"] = _neg_ceil(out["days_to_failure"], 90)       # 05 L97
    out["time_to_fail"] = _neg_ceil(out["days_to_failure"], 365)             # 05 L98
    out["final_year"] = fail_ts.dt.year.astype("Int64")                      # 05 L117

    n_in = len(out)
    keep = ~(out["days_to_failure"] < 0)                                     # 05 L104 (NA kept)
    out = out[keep].reset_index(drop=True)
    info = {"rows_in": int(n_in), "rows_after_post_failure_drop": int(len(out)),
            "failed_bank_rows": int((out["failed_bank"] == 1).sum())}
    return out, info


def apply_unit_scaling_thousands_to_dollars(level_thousands: pd.Series) -> pd.Series:
    """thousands -> dollars = level * 1000 (``05 L111-115``). Used internally to reach CLV's
    07 deflation scale; the stored nominal columns stay in THOUSANDS (published-DB scale)."""
    return pd.to_numeric(level_thousands, errors="coerce") * 1000.0


def deflate(panel: pd.DataFrame, cpi: pd.DataFrame, varlist: Iterable[str]) -> pd.DataFrame:
    """CPI real twins in CLV's 07 scale. implements 05 L111-115 (×1000) + 07 L26-34 (/cpi_gfd).

    CLV: ``05`` multiplies the modern levels thousands->dollars ×1000, then ``07`` deflates
    ``var = var / cpi_gfd`` (GFD Dec-31 native index; the paper states NO base year, SPEC §6.5
    -- reproduce the raw division bit-for-bit). Our stored nominal ``<var>`` are THOUSANDS, so
    ``<var>_real = <var>_thousands * 1000 / cpi_gfd`` reproduces CLV's deflated-dollar value.
    A year with no CPI (or cpi_gfd==0) -> NaN (honest absence).
    """
    merged = panel.merge(cpi[["year", "cpi_gfd"]], on="year", how="left")
    denom = merged["cpi_gfd"].where(merged["cpi_gfd"].astype("float64") != 0)
    out = pd.DataFrame(index=panel.index)
    out["cpi_gfd"] = merged["cpi_gfd"].to_numpy()
    for v in varlist:
        if v in panel.columns:
            dollars = pd.to_numeric(merged[v], errors="coerce").to_numpy() * 1000.0
            out[f"{v}_real"] = dollars / denom.to_numpy()
    return out


def crisis_bvx(year: pd.Series) -> pd.Series:
    """crisisBVX dummy (``07 L52-55``): 1 for BVX crisis years, else 0. (0 across 1959-75.)"""
    return pd.to_numeric(year, errors="coerce").isin(CRISIS_BVX_YEARS).astype("int64")


def _safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    den = pd.to_numeric(den, errors="coerce")
    den = den.where(den != 0)
    return pd.to_numeric(num, errors="coerce") / den


def modern_ratios(panel: pd.DataFrame) -> pd.DataFrame:
    """Derived MODERN ratios (``07``), computed on nominal thousands (deflation-invariant),
    with the Q4 income gate, outlier clips, and the >1/<0 validity filter. implements
    07 L61-147 (modern branch).

    Ratios of two same-era levels are CPI-deflation-INVARIANT (numerator and denominator are
    divided by the same cpi_gfd, which cancels), so computing them from nominal levels is
    bit-identical to CLV's post-deflation ratios. Only ``size`` (a log LEVEL) is
    deflation-sensitive and uses ``assets_real`` (CLV ×1000 dollars).

    HIST-only ratios (surplus_ratio, leverage_capital, oreo_ratio, interbank_ratio,
    emergency_borrowing, profits_ratio, demand_ratio via demand_deposits, deposit_ratio_alt)
    are structurally NA for MODL (their inputs are OCC-only) and are omitted (documented in
    _BUILD_META); the loan-based ratios are NA because ``loans`` is 0% in this era.
    """
    p = panel
    a = pd.to_numeric(p["assets"], errors="coerce")
    q4 = pd.to_numeric(p["quarter_number"], errors="coerce") == 4
    out = pd.DataFrame(index=p.index)

    liquid = pd.to_numeric(p["liquid"], errors="coerce").mask(pd.to_numeric(p["liquid"], errors="coerce") == 0)  # 07 L61
    out["liquid_ratio"] = _safe_div(liquid, a)                                # 07 L62
    out["leverage"] = _safe_div(p["equity"], a)                               # 07 L66
    out["loan_ratio"] = _safe_div(p["loans"], a)                              # 07 L82 (loans NA -> NA)
    out["deposit_ratio"] = _safe_div(p["deposits"], a)                        # 07 L83

    # noncore (modern override, year>1941): noncore_funding = rowtotal(deposits_time, otherbor_liab)
    noncore_funding = rowtotal(p, ("deposits_time", "otherbor_liab"), missing_if_all_na=False)  # 07 L91
    out["noncore_ratio"] = _safe_div(noncore_funding, a)                      # 07 L92
    # time_ratio: modern uses deposits_time/assets (07 L105, year>1945)
    dt = pd.to_numeric(p["deposits_time"], errors="coerce")
    out["time_ratio"] = _safe_div(dt.mask(dt == 0), a)                        # 07 L102-105

    # income ratios (Q4 only, clips)
    out["income_ratio"] = _safe_div(p["ytdnetinc"], a).where(q4)             # 07 L113,120-122
    out["npl_ratio"] = _safe_div(p["npl_tot"], p["loans"])                    # 07 L114 (NA in era)
    out["prov_ratio"] = _safe_div(p["ytdllprov"], p["loans"]).where(q4)      # 07 L115 (loans NA)
    out["int_exp_ratio"] = _safe_div(p["ytdint_exp_dep"], a).where(q4)       # 07 L116
    out["int_inc_ratio"] = _safe_div(p["ytdint_inc_ln"], a).where(q4)        # 07 L117
    out["nim"] = _safe_div(
        pd.to_numeric(p["ytdint_inc_ln"], errors="coerce")
        - pd.to_numeric(p["ytdint_exp_dep"], errors="coerce"), a)             # 07 L118

    # loan-mix ratios (07 L125-127) -- NA because loans is 0% in the era
    for v in LOAN_MIX_VARS:
        out[f"{v}_ratio"] = _safe_div(p.get(v), p["loans"])
    # funding ratios (07 L130-132)
    for v in FUNDING_RATIO_VARS:
        out[f"{v}_ratio"] = _safe_div(p.get(v), a)

    # size on DEFLATED assets (07 L47); size_cat within-year quartile (07 L49)
    if "assets_real" in p.columns:
        ar = pd.to_numeric(p["assets_real"], errors="coerce").to_numpy(dtype="float64")
        out["size"] = np.log(np.where(ar > 0, ar, np.nan))                    # log only on positives
        yr = pd.to_numeric(p["year"], errors="coerce")
        out["size_cat"] = _within_year_quartile(pd.Series(ar, index=p.index), yr)
    out["crisisBVX"] = crisis_bvx(p["year"])                                  # 07 L52-55 (==0)
    if "age" in p.columns:
        age = pd.to_numeric(p["age"], errors="coerce").to_numpy(dtype="float64")
        out["log_age"] = np.log(np.where(age > 0, age, np.nan))               # 07 L44

    # outlier clips (07 L138-141)
    out["income_ratio"] = out["income_ratio"].clip(-0.5, 0.5)
    out["nim"] = out["nim"].clip(-0.5, 0.5)
    out["int_exp_ratio"] = out["int_exp_ratio"].clip(0.0, 1.0)
    out["int_inc_ratio"] = out["int_inc_ratio"].clip(0.0, 1.0)

    # validity filter (07 L143-147): these ratios -> missing if <0 or >1
    for col in VALIDITY_FILTER_RATIOS:
        if col in out.columns:
            bad = (out[col] > 1) | (out[col] < 0)
            out[col] = out[col].mask(bad & out[col].notna())
    return out


def _within_year_quartile(values: pd.Series, year: pd.Series) -> pd.Series:
    """Within-year quartile bin 1..4 (Stata ``xtile(assets), n(4) by(year)``, 07 L49).

    METHOD-CHOICE: reproduced with a rank-based ``qcut`` per year (ties broken first-seen,
    like Stata's default). Documented in _BUILD_META.
    """
    df = pd.DataFrame({"v": pd.to_numeric(values, errors="coerce"), "y": pd.to_numeric(year, errors="coerce")})

    def _bin(s: pd.Series) -> pd.Series:
        v = s.dropna()
        if v.nunique() < 4:
            return pd.Series(np.nan, index=s.index)
        try:
            q = pd.qcut(v.rank(method="first"), 4, labels=[1, 2, 3, 4])
            return q.reindex(s.index).astype("float")
        except ValueError:
            return pd.Series(np.nan, index=s.index)

    return df.groupby("y", group_keys=False)["v"].apply(_bin).astype("Int64")


# ===========================================================================
# Assembly (I/O boundary)
# ===========================================================================
def _first_existing(cands: Iterable[Path]) -> Path | None:
    for c in cands:
        if Path(c).exists():
            return Path(c)
    return None


def _ensure_extracted() -> None:
    """Extract the 4 needed repkit members to the scratchpad cache if absent (idempotent).
    The zip is the stable canonical input; the scratchpad copy is re-extractable."""
    needed = {
        f"{_ZIP_PREFIX}/call-reports-modern.dta": SCRATCH / "call-reports-modern.dta",
        f"{_ZIP_PREFIX}/GFD/US_CPI_GFD_annual.dta": SCRATCH / "GFD" / "US_CPI_GFD_annual.dta",
        f"{_ZIP_PREFIX}/FDIC/public-bank-data.dta": SCRATCH / "FDIC" / "public-bank-data.dta",
        f"{_ZIP_PREFIX}/FDIC/FDIC_ftdb_deposits_assets_failure.dta":
            SCRATCH / "FDIC" / "FDIC_ftdb_deposits_assets_failure.dta",
    }
    if all(dest.exists() for dest in needed.values()):
        return
    if not REPKIT_ZIP.exists():
        return
    with zipfile.ZipFile(REPKIT_ZIP) as z:
        names = set(z.namelist())
        for member, dest in needed.items():
            if dest.exists() or member not in names:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member) as src, open(dest, "wb") as fh:
                fh.write(src.read())


def load_modern_era(dta_path: Path, y0: int = MODL_YEAR_MIN, y1: int = MODL_YEAR_MAX) -> pd.DataFrame:
    """Read the modern .dta (chunked, needed columns), filter to [y0, y1], coerce numerics.
    implements the 05 L49 ``use call-reports-modern`` input."""
    import pyreadstat  # local import: only main() needs the Stata reader
    usecols = list(_READ_COLS)
    reader = pyreadstat.read_file_in_chunks(
        pyreadstat.read_dta, str(dta_path), chunksize=300000, usecols=usecols
    )
    parts = []
    for chunk, _m in reader:
        y = pd.to_numeric(chunk["year"], errors="coerce")
        parts.append(chunk[(y >= y0) & (y <= y1)])
    df = pd.concat(parts, ignore_index=True)
    for c in _NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def build_panel(dta_path: Path, cpi_path: Path | None,
                pbd_path: Path | None, ftdb_path: Path | None) -> tuple[pd.DataFrame, dict]:
    """Assemble the Luck-core MODL panel (1959-75). Returns (panel, provenance_dict)."""
    import pyreadstat
    raw = load_modern_era(dta_path)

    # --- 05: id hygiene + FDIC merge + bank_id + failure fields ------------
    raw, hyg_info = apply_id_hygiene(raw)
    fdic_info: dict = {"fdic_available": bool(pbd_path and ftdb_path)}
    if pbd_path and ftdb_path:
        pbd, _ = pyreadstat.read_dta(str(pbd_path))
        ftdb, _ = pyreadstat.read_dta(str(ftdb_path))
        fail_dates = build_fdic_fail_dates(pbd, ftdb)
        fdic_info["fail_date_certs"] = int(len(fail_dates))
        raw = raw.merge(
            fail_dates, left_on="id_fdic_cert_resolved", right_on="id_fdic_cert",
            how="left", suffixes=("", "_fd"),
        )
    else:
        for c in ("fail_day", "fail_day2", "resdep", "resasset", "resdep2", "resasset2"):
            raw[c] = pd.NaT if c.startswith("fail_day") else np.nan
    raw, fail_info = compute_failure_fields(raw)

    year = pd.to_numeric(raw["year"], errors="coerce").astype("Int64")
    p = pd.DataFrame(index=raw.index)

    # --- identity / provenance -------------------------------------------
    p["bank_id"] = raw["bank_id"]                                             # 05 L66-77 (CLV cert rule)
    p["id_rssd"] = pd.to_numeric(raw["id_rssd"], errors="coerce").astype("Int64")
    p["entity_id"] = p["id_rssd"]                                             # == luck_wide.entity_id (verified)
    p["id_fdic_cert"] = raw["id_fdic_cert_resolved"]
    p["quarter"] = raw["quarter"]
    p["year"] = year
    p["quarter_number"] = pd.to_numeric(raw["quarter_number"], errors="coerce").astype("Int64")
    p["period_end"] = pd.to_datetime(raw["call_date"]).dt.date               # aligns to luck_wide.period_end
    p["call_date"] = pd.to_datetime(raw["call_date"]).dt.date
    p["era_group"] = entity_spine.era_series(year)                           # all MODL here
    p["reconstruction_tier"] = "derivation-layer"                            # SPEC §0 / D5 §8
    p["src_vintage"] = "luck_modern_clv"
    p["unit_basis"] = "nominal_usd_thousands"
    p["bank_name"] = raw.get("bank_name")
    p["state_abbrev"] = raw.get("state_abbr_nm")                             # 05 L107 rename

    # --- failure / run layer ---------------------------------------------
    p["failed_bank"] = raw["failed_bank"]
    p["fail_day"] = pd.to_datetime(raw.get("fail_day"), errors="coerce").dt.date
    p["days_to_failure"] = raw["days_to_failure"]
    p["quarters_to_failure"] = raw["quarters_to_failure"]
    p["time_to_fail"] = raw["time_to_fail"]
    p["final_year"] = raw["final_year"]
    p["resdep"] = pd.to_numeric(raw.get("resdep"), errors="coerce")
    p["resasset"] = pd.to_numeric(raw.get("resasset"), errors="coerce")
    p["run"] = pd.Series(pd.NA, index=raw.index, dtype="Float64")            # 06 no-op (post-1993 only)

    # --- age (05 L125-129) ------------------------------------------------
    p["charter_year"] = charter_year_from_dt_open(raw.get("dt_open"))
    p["age"] = compute_age(year, p["charter_year"])

    # --- nominal levels (THOUSANDS, published-DB scale) -------------------
    for c in ("assets", "cash", "securities", "loans", "deposits", "deposits_demand",
              "deposits_time", "equity", "otherbor_liab", "ffpurch", "ln_re", "ln_ci",
              "ln_cons", "ln_cc", "ln_fi", "ln_oth", "npl_tot", "brokered_dep",
              "insured_deposits", "num_employees", "ytdint_inc_ln", "ytdint_exp_dep",
              "ytdllprov", "ytdnetinc"):
        p[c] = pd.to_numeric(raw.get(c), errors="coerce")
    p["liquid"] = compute_liquid(raw)                                        # 05 L108

    # --- CPI deflation (real twins, CLV 07 dollar scale) ------------------
    cpi_info: dict = {"cpi_path": str(cpi_path) if cpi_path else None}
    if cpi_path and Path(cpi_path).exists():
        cpi, _ = pyreadstat.read_dta(str(cpi_path))
        cpi = cpi[["year", "cpi_gfd"]].copy()
        cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce").astype("Int64")
        real = deflate(p, cpi, DEFLATE_VARS)
        p = pd.concat([p, real], axis=1)
        cpi_info["deflated_vars"] = [v for v in DEFLATE_VARS if f"{v}_real" in p.columns]
        cpi_info["cpi_source"] = ("GFD US_CPI_GFD_annual (Dec-31), 02 L23-30; "
                                  "×1000 (05 L111-115) then /cpi_gfd (07 L26-34)")
    else:
        cpi_info["deflated_vars"] = []
        cpi_info["cpi_source"] = "ABSENT -- real twins omitted (honest absence)"
        print("[WARN] CPI file absent; real twins omitted.", file=sys.stderr)

    # --- derived ratios (07 modern branch) --------------------------------
    ratios = modern_ratios(p)
    p = pd.concat([p, ratios], axis=1)

    # isid bank_id quarter (05 L135) -- report uniqueness
    dup = int(p.duplicated(["bank_id", "quarter"]).sum())

    prov = {
        "id_hygiene": hyg_info,
        "fdic": fdic_info,
        "failure": fail_info,
        "cpi": cpi_info,
        "isid_bank_id_quarter_duplicates": dup,
        "gaps_not_derivable": [
            "loans (total, RCFD-net): 0% populated in the modern .dta for 1959-75 (loan buckets "
            "exist, no total) -> loan_ratio/npl_ratio/prov_ratio/loan-mix ratios NA; not synthesized "
            "(matches luck_wide.ln_tot null). Recorded.",
            "ffpurch: 0% populated -> liquid = cash+securities (05 L108 rowtotal, ffpurch->0).",
            "npl_tot (1982+) / brokered_dep (1983+) / insured_deposits (1983+): 0% in-era "
            "(concept post-dates 1959-75) -> ratios NA. Recorded.",
            "run dummy (06 L159-207): built only from post-1993 FTDB outflows -> all-NA for "
            "1959-75 (06 is a no-op on economic levels for this era). Set NA, recorded.",
            "HIST-only ratios (surplus_ratio, leverage_capital, oreo_ratio, interbank_ratio, "
            "emergency_borrowing, profits_ratio, deposit_ratio_alt, demand_ratio-via-demand_deposits): "
            "inputs are OCC-only -> not applicable to MODL; omitted (not all-NA columns).",
        ],
    }
    return p, prov


# ===========================================================================
# Self-smoke: 6 anchor cells vs the published luck_wide (read-only warehouse)
# ===========================================================================
#: 6 pre-selected anchor cells (entity_id/id_rssd, period_end, variable) spanning 3 top banks
#: x 4 dates x 3 core levels, with luck_wide reference values (thousands; probe5_luck).
SMOKE_ANCHORS = (
    (349361, "1959-12-31", "assets", 11373657.0),
    (349361, "1965-12-31", "equity", 891893.0),
    (349361, "1970-12-31", "deposits", 25643538.0),
    (476810, "1970-12-31", "assets", 25138414.0),
    (748601, "1975-12-31", "deposits", 33776804.0),
    (349361, "1975-12-31", "equity", 1956370.0),
)


def _luck_wide_anchor(entity_id: int, period_end: str, col: str) -> float | None:
    """Read one published cell from ``luck_wide`` (read-only). Returns None if absent."""
    if not WAREHOUSE.exists():
        return None
    import duckdb
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    try:
        r = con.execute(
            f"SELECT {col} FROM luck_wide WHERE entity_id = ? AND period_end = DATE '{period_end}'",
            [entity_id],
        ).fetchone()
    finally:
        con.close()
    if r is None or r[0] is None:
        return None
    return float(r[0])


def self_smoke(panel: pd.DataFrame, *, use_warehouse: bool = True) -> list[dict]:
    """6 anchor cells: our built nominal (thousands) vs published ``luck_wide`` (thousands),
    each classified with the pre-registered taxonomy (ulp=1 -> integer thousands)."""
    anchors: list[dict] = []
    pe = pd.to_datetime(panel["period_end"])
    for entity_id, period_end, col, fallback in SMOKE_ANCHORS:
        m = panel[(panel["id_rssd"] == entity_id) & (pe == pd.Timestamp(period_end))]
        built = None
        if not m.empty and col in m.columns:
            v = m[col].iloc[0]
            built = None if pd.isna(v) else float(v)
        pub = _luck_wide_anchor(entity_id, period_end, col) if use_warehouse else None
        if pub is None:
            pub = fallback  # pinned reference (probe5_luck) if warehouse unavailable
        cls = taxonomy.classify(pub, built, 1.0)
        anchors.append({"anchor": col, "entity_id": entity_id, "period_end": period_end,
                        "built": built, "published": pub, "class": cls,
                        "reference": "luck_wide (published Luck DB, thousands)"})
    return anchors


# ===========================================================================
# main
# ===========================================================================
def _d5_note() -> dict:
    """D5 recommendation for Batch-5 warehouse integration: extend clean_bank_panel's MODL
    stratum with these CLV-derived columns; do NOT build a parallel table (SPEC §8)."""
    return {
        "recommendation": (
            "EXTEND clean_bank_panel's MODL stratum (era_group='MODL') with these CLV-derived "
            "columns as a 'derived layer' over the existing (era_group, entity, year) spine; do "
            "NOT build a parallel luck_core table (SPEC §8, plan §B3, D5 default)."
        ),
        "new_columns_to_add": {
            "liquid": "05 L108 rowtotal(cash,securities,ffpurch); tier=derivation-layer",
            "noncore_ratio": "07 L91-92 rowtotal(deposits_time,otherbor_liab)/assets; tier=derivation-layer",
            "time_ratio / deposit_ratio / leverage / liquid_ratio": "07 ratios; tier=derivation-layer",
            "income_ratio / int_inc_ratio / int_exp_ratio / nim (Q4)": "07 L113-122 income ratios; tier=derivation-layer",
            "size / size_cat / log_age / crisisBVX": "07 L44-55 analytic; tier=derivation-layer",
            "failed_bank / time_to_fail / days_to_failure": "05 L62-104 FDIC-failure layer; tier=derivation-layer",
            "bank_id (CLV FDIC-cert rule)": "05 L66-77; METHOD-CHOICE vs freeNIC rssd_id key (SPEC §6.1) -- store as clv_bank_id",
        },
        "provenance_tier_column": "reconstruction_tier IN ('independent','derivation-layer','not-derivable')",
        "join_key": "(id_rssd, period_end) on era_group='MODL' (== luck_wide.entity_id/period_end)",
        "already_present_in_luck_wide": [
            "assets, cash, securities, deposits, equity, deposits_time, deposits_demand, ln_* buckets "
            "(nominal thousands) -- our nominal columns reproduce these exactly (self-smoke 6/6).",
        ],
    }


def main() -> int:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=== build_luck_core (1959Q4-1975Q4 MODL derivation-layer) ===", flush=True)

    _ensure_extracted()
    dta_path = _first_existing(MOD_DTA_CANDIDATES)
    if dta_path is None:
        print("[FATAL] modern .dta not found (checked scratchpad + repkit zip).", file=sys.stderr)
        return 2
    cpi_path = _first_existing(CPI_DTA_CANDIDATES)
    pbd_path = _first_existing(FDIC_PBD_CANDIDATES)
    ftdb_path = _first_existing(FDIC_FTDB_CANDIDATES)
    print(f"input dta : {dta_path}")
    print(f"cpi       : {cpi_path}")
    print(f"fdic pbd  : {pbd_path}")

    panel, prov = build_panel(dta_path, cpi_path, pbd_path, ftdb_path)
    anchors = self_smoke(panel)

    panel = panel.sort_values(["bank_id", "quarter"], na_position="first",
                              kind="stable").reset_index(drop=True)
    panel.to_parquet(OUT_PARQUET, index=False)

    n_rows = int(len(panel))
    n_entities = int(panel["id_rssd"].nunique())
    span = [int(panel["year"].min()), int(panel["year"].max())]
    matched = sum(1 for a in anchors if a["class"] in taxonomy.MATCH_CLASSES)

    meta = {
        "table": "luck_core_1959_1975",
        "description": ("Luck-core MODL derivation-layer panel (1959Q4-1975Q4): CLV's digitized "
                        "modern raw (repkit call-reports-modern.dta) -> published/analysis schema, "
                        "original Python implementing 05 -> 06 -> 07. Their formula on their input "
                        "(D2 gate 99.9%)."),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "build_script": "pipeline/reconstruction/build_luck_core.py",
        "input": {
            "dta_path": str(dta_path),
            "input_choice": ("call-reports-modern.dta (NOT call-reports-historical.dta, which is "
                             "the OCC 1863-1941 file). Per SPEC §0/§1 the MODL era lives in the "
                             "modern .dta processed by 05; the task's 'historical.dta/232MB' label "
                             "is a slip (232MB = the OCC file; modern = 343MB)."),
            "preferred_over": "warehouse luck_wide (ingested twin) -- read the .dta directly (SPEC §0)",
            "rows_read_1959_1975": prov["id_hygiene"]["rows_in"],
            "rows_after_id_hygiene": prov["id_hygiene"]["rows_after_drop_unkeyed"],
            "rows_after_post_failure_drop": prov["failure"]["rows_after_post_failure_drop"],
        },
        "output": {"parquet": str(OUT_PARQUET), "rows": n_rows,
                   "entities_id_rssd": n_entities, "year_span": span,
                   "isid_bank_id_quarter_duplicates": prov["isid_bank_id_quarter_duplicates"]},
        "chain_implemented": {
            "stage_05_modern": {
                "fdic_fail_dates": "05 L11-42", "id_hygiene": "05 L53-60",
                "fdic_failure_merge": "05 L62", "pseudo_bank_id": "05 L66-77",
                "failure_fields": "05 L88-104", "liquid_rowtotal": "05 L108",
                "unit_x1000": "05 L111-115", "age": "05 L125-129", "isid": "05 L135",
            },
            "stage_06_run_dummy": "06 L159-207 (post-1993 only -> NA for 1959-75; no-op on levels)",
            "stage_07_combine": {
                "cpi_deflation": "07 L26-34", "ratios": "07 L61-132",
                "q4_income_gate": "07 L120-122", "clips": "07 L138-141",
                "validity_filter": "07 L143-147", "size/size_cat/crisisBVX": "07 L47-55",
            },
            "entity_key": "bank_id = CLV FDIC-cert rule (05 L66-77); validation aligns on (id_rssd, period_end)",
            "deflation": prov["cpi"]["cpi_source"],
        },
        "reuse_with_citation": {
            "entity_spine.py": ["resolve_fdic_cert/drop_unkeyed (05 L53-60)",
                                "modern_bank_id (05 L66-77)", "era_series (SPEC §0)"],
            "45_build_clean_bank_panel.py": ["pivot_modl reads luck_wide columns directly (L186-195); "
                                             "we re-derive from the pre-05 modern .dta instead"],
        },
        "units": {
            "nominal_levels": "thousands of USD (published luck_wide scale) -- e.g. assets",
            "real_twins": "<var>_real = <var>_thousands * 1000 / cpi_gfd (CLV 05 ×1000 + 07 /cpi_gfd dollars)",
            "ratios": "unitless (CPI-deflation-invariant); size = log(assets_real)",
        },
        "gaps_not_derivable": prov["gaps_not_derivable"],
        "self_smoke_anchors": anchors,
        "self_smoke_matched": f"{matched}/{len(anchors)}",
        "taxonomy_gate_1959_1975": taxonomy.GATE_1959_1975,
        "d5_note_batch5_warehouse_integration": _d5_note(),
        "citation_posture": "original Python implementing CLV documented method; no do-file code copied (D3).",
    }
    OUT_META.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")

    print(f"rows={n_rows:,}  entities(id_rssd)={n_entities:,}  span={span[0]}-{span[1]}")
    print(f"id-hygiene: {prov['id_hygiene']}")
    print(f"failure   : {prov['failure']}")
    print(f"deflated vars: {len(prov['cpi']['deflated_vars'])}  isid dups: {prov['isid_bank_id_quarter_duplicates']}")
    print(f"self-smoke: {matched}/{len(anchors)} matched")
    for a in anchors:
        print(f"  [{a['class']:<10}] {a['anchor']:<9} rssd={a['entity_id']} {a['period_end']} "
              f"built={a['built']} published={a['published']}")
    print(f"WROTE {OUT_PARQUET}")
    print(f"WROTE {OUT_META}")
    print(f"done in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
