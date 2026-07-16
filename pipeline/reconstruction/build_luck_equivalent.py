"""build_luck_equivalent — the TRUE independent 1976Q1-2026Q1 re-derivation.

Builds the Luck-schema call-report panel (one row per ``rssd_id x period_end``) **purely
from Fed-direct raw MDRM** in the read-only FreeNIC warehouse
(``main.call_report_filings``: Chicago Fed pre-2012 + FFIEC CDR 2012+), for the D1
(``scope_v11``) MODC scope. This is the "independent tier" of the reconstruction (SPEC §0
row 1 / §5): no CLV ``.dta`` value is read — every cell is re-derived from raw MDRM items
via the ``variable_map.csv`` recipes.

ARCHITECTURE (why two layers)
-----------------------------
1. **Heavy SQL layer (mechanical, map-code-driven).** A single conditional-aggregation
   scan of ``call_report_filings`` (the ``30_build_public_luck_panel.py`` pattern) extracts
   the raw *building blocks* — one ``MAX``/``cf`` per MDRM code the scoped variables need —
   keyed ``rssd_id x period_end``. This is the ~1.7B-row scan; target < 30 min.
2. **Procedural layer (pure Python, pytested).** The genuinely procedural rules — era
   splices, the ``rowtotal`` reconstructions (liquid), the ratio constructions with their
   ``07`` clips, ``crisisBVX``, ``size_cat`` — are applied in pandas over the small
   (~2.1M-row) aggregated frame by the importable helpers in this module. Because the
   builder USES those helpers as its production path, the pytest fixtures exercise the
   *actual* code (no SQL/Python twin drift). The CPI deflation helper (:func:`deflate`) is
   provided + tested as the procedural contract but is applied downstream in the combine
   step (real levels are gapped here — see ``_BUILD_META.gaps``); all §4 ratios are
   deflation-invariant and ARE built.

FORMULA SOURCE = ``variable_map.csv`` (loaded/validated via :mod:`variable_map`). The MDRM
recipes below are the machine twin of that CSV; each is tagged with its ``formula_id`` and
the spec locus. Where a formula **differs from** ``30_build_public_luck_panel.py`` it is
flagged ``DIVERGENCE(30_build)`` with the spec row that authorizes the change (all are
coverage EXTENSIONS, never fabrication).

Citation posture (D3): original Python implementing CLV's documented methodology; do-file
loci are cited ("implements 05 L108", "07 L66"); no CLV code is reproduced. The warehouse
connection is **READ-ONLY** (asserted). No fabrication: a scoped variable that cannot be
built from raw per the spec is OMITTED and recorded in ``_BUILD_META.gaps`` — never
approximated.

Run (stage-resumable; per the workspace >10-min stage-resume rule):
  PYTHONIOENCODING=utf-8 python -m pipeline.reconstruction.build_luck_equivalent --stage scan
    # heavy: one DuckDB COPY per period chunk -> _bb_luck_equivalent_<lo>_<hi>.parquet;
    # already-written chunks are SKIPPED, so a killed run resumes where it stopped.
  PYTHONIOENCODING=utf-8 python -m pipeline.reconstruction.build_luck_equivalent --stage derive
    # fast: reads the chunk parquets, applies the derived layer, writes the final
    # parquet + _BUILD_META.json + the 6-anchor smoke.
  (--stage all runs both.)

Runtime deps: duckdb + pandas (+ numpy/pyarrow via pandas). Warehouse READ-ONLY.
"""

from __future__ import annotations
import os

import json
import time
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional, Sequence

import duckdb
import numpy as np
import pandas as pd

try:  # allow both ``python -m pipeline.reconstruction.build_luck_equivalent`` and direct run
    from . import variable_map as vm
except ImportError:  # pragma: no cover - direct-script fallback
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from pipeline.reconstruction import variable_map as vm  # type: ignore

# ---------------------------------------------------------------------------
# Paths (forward-slash, per .claude/rules/filepath-safety.md). Warehouse READ-ONLY.
# ---------------------------------------------------------------------------
WAREHOUSE = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/freenic.duckdb")
PUBLIC_LUCK_PANEL = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/public_luck_panel.parquet")
OUT_DIR = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction")
OUT_PARQUET = OUT_DIR / "luck_equivalent_1976_2026.parquet"
OUT_META = OUT_DIR / "luck_equivalent_1976_2026_BUILD_META.json"

#: MODC era window (SPEC §0 / §5). Inclusive of both quarter-ends. call_report_filings
#: itself spans exactly 1976-03-31 .. 2026-03-31 (verified from the manifest).
MODC_LO = date(1976, 3, 31)
MODC_HI = date(2026, 3, 31)

#: Scan chunks (inclusive period_end windows). Each chunk is one DuckDB COPY -> parquet;
#: completed chunks are skipped on re-run (stage-resume). Sized so each scan stays well
#: inside a 10-minute foreground call.
SCAN_CHUNKS = [
    (date(1976, 1, 1), date(1985, 12, 31)),
    (date(1986, 1, 1), date(1995, 12, 31)),
    (date(1996, 1, 1), date(2005, 12, 31)),
    (date(2006, 1, 1), date(2015, 12, 31)),
    (date(2016, 1, 1), date(2026, 12, 31)),
]


def _chunk_path(lo: date, hi: date) -> Path:
    return OUT_DIR / f"_bb_luck_equivalent_{lo.year}_{hi.year}.parquet"

# ---------------------------------------------------------------------------
# Era-boundary constants (SPEC §2 / §3 dictionary rows + Table C.1). Shared by the
# production splices and the pytest fixtures — one source of truth for each boundary.
# ---------------------------------------------------------------------------
B_SECURITIES = pd.Timestamp("1994-03-31")   # SPEC §2.6 / Table C.1: RCFD1754+1773 from 1994Q1
B_TIMEDEP_1 = pd.Timestamp("1984-03-31")    # SPEC §2.5 dict :28-30: 2514 -> 2604+6648 at 1984Q1
B_TIMEDEP_2 = pd.Timestamp("2010-03-31")    # SPEC §2.5 dict :30: -> J473+J474+6648 at 2010Q1
B_LNCI = pd.Timestamp("1984-03-31")         # SPEC §2.8 dict :89-91: 1600 -> 1766 at 1984Q1
B_LNCC = pd.Timestamp("2001-03-31")         # SPEC §2.8 Table C.1: RCON2008 -> B538 at 2001Q1
B_LNFI_1 = pd.Timestamp("1984-03-31")       # SPEC §2.8 Table C.1: 1495 -> component sum at 1984Q1
B_LNFI_2 = pd.Timestamp("2001-03-31")       # SPEC §2.8 Table C.1: sum -> B531+B534+B535 at 2001Q1
B_SURPLUS = pd.Timestamp("1990-03-31")      # SPEC §2.12 dict :64-65: 3240 -> 3839 at 1990Q1
B_INTEXPDEP = pd.Timestamp("2017-03-31")    # SPEC §3 dict :259-262: -> 4508+0093+HK03+HK04+4172 at 2017Q1
B_INSURED = pd.Timestamp("2006-06-30")      # SPEC §2.19 dict :95-96: 2702 -> F049+F045 at 2006Q2
# --- SPEC §10 modern-era remediation boundaries (2026-07-15) ---
B_FF_PURE_END = pd.Timestamp("1997-03-31")  # SPEC §10.1 dict :34,:17: pure ff 0278/0276 end 1996Q4 (arm [·,1997Q1))
B_FF_PURE_POST = pd.Timestamp("2002-03-31") # SPEC §10.1 dict :35,:18: pure ff post arm B993/B987 from 2002Q1
B_OTHERBOR = pd.Timestamp("1994-03-31")     # SPEC §10.2 dict :39-44: otherbor 2850+2910 -> 3190 at 1994Q1
B_LNCONS = pd.Timestamp("2012-03-31")       # SPEC §10.3 dict :92 + 2011 identity: 1975 retired 2011Q4 -> RC-C item-6 successor
B_LNRE = pd.Timestamp("2012-03-31")         # SPEC §10.6 dict :70 + 2007-2011 identity: RCON1410 aggregate retired 2011Q4 -> RC-C Part I component sum

#: BVX crisis-year dummy set (SPEC §4 / 07 L52-55).
CRISIS_YEARS = frozenset({1873, 1884, 1890, 1893, 1907, 1930, 1984, 1990, 2007})

# ===========================================================================
# BUILDING-BLOCK CODE REGISTRIES (mechanical; the SQL scan extracts these).
# Each code is referenced by one or more variable_map formulas (cited at use site).
# ===========================================================================
#: cf(code) = COALESCE(MAX RCFD, MAX RCON) building blocks (consolidated->domestic fallback,
#: SPEC §2 notation; ``30_build def cf``). Every code here has an RCFD and/or RCON twin.
CF_CODES = [
    "2170", "2200", "2210", "1410", "1975", "1590", "2150", "3123", "3210",
    "3200", "2948", "3190", "0276", "0278", "2122", "2123",           # single-code levels
    "0010", "0081", "0071",                                            # cash arms (§2.7)
    "0390", "1754", "1773",                                            # securities arms (§2.6)
    "2514", "2604", "6648",                                            # time_deposits arms (§2.5)
    "1600", "1766", "1763", "1764",                                    # ln_ci arms (§2.8)
    "3240", "3839",                                                    # surplus arms (§2.12)
    "1403", "1407",                                                    # npl_tot (§3)
    "B993", "B987",                                                    # ffpurch/ffsold post-2002 pure arms (§10.1 dict :35,:18)
    "2850", "2910", "2332", "2333", "A547", "A548",                    # otherbor_liab era chain (§10.2 dict :39-44)
    "B538", "B539", "K137", "K207",                                    # ln_cons post-2011 RC-C item-6 successor (§10.3)
    "1415", "1420", "1460", "1480", "1797", "5367", "5368",            # ln_re post-2011 RC-C Part I successor (§10.6)
    "F158", "F159", "F160", "F161",                                    # ln_re construction/nonfarm-nonres F-item arms (§10.6)
]
#: RCON-only building blocks (domestic-office series the recipe names explicitly).
RCON_ONLY = [
    "2200",                                                            # domestic_dep (§2.3)
    "2365",                                                            # brokered_dep (§2.19)
    "2702", "F049", "F045",                                            # insured_deposits (§2.19)
    "2008", "B538",                                                    # ln_cc (Table C.1)
    "1495", "1505", "1510", "1517", "1756", "1757", "B531", "B534", "B535",  # ln_fi (Table C.1)
    "J473", "J474",                                                    # time_deposits post-2010 (§2.5)
]
#: RCFN-only building blocks (foreign-office series).
RCFN_ONLY = ["2200"]                                                   # foreign_dep (§2.3)
#: RIAD income building blocks (income items are RIAD-only — no RCFD/RCON twin exists).
RIAD_CODES = [
    "4340", "4107", "4073", "4010", "4230", "4150",                    # net inc / int inc / int exp / int-inc-loans / llprov / employees
    "4170", "4174", "4176", "4172", "4508", "0093", "HK03", "HK04",    # ytdint_exp_dep era chain (§3)
]


def _colname(prefix: str, code: str) -> str:
    return f"{prefix}_{code}"


def _agg_sql() -> tuple[str, list[str]]:
    """Return (aggregate-columns SQL, WHERE inlist codes). Mechanical, single-scan.

    Emits one aggregate column per building block: ``cf_<c>`` = COALESCE(MAX RCFD,MAX RCON);
    ``rcon_<c>`` = MAX RCON; ``rcfn_<c>`` = MAX RCFN; ``riad_<c>`` = MAX RIAD. Implements the
    ``30_build`` conditional-aggregation pattern (``30_build def cf`` / ``AGG_SQL``).
    """
    cols: list[str] = []
    ids: set[str] = set()
    for c in CF_CODES:
        cols.append(
            f"COALESCE(MAX(CASE WHEN variable_id='RCFD{c}' THEN value END), "
            f"MAX(CASE WHEN variable_id='RCON{c}' THEN value END)) AS {_colname('cf', c)}"
        )
        ids.add(f"RCFD{c}")
        ids.add(f"RCON{c}")
    for c in RCON_ONLY:
        cols.append(f"MAX(CASE WHEN variable_id='RCON{c}' THEN value END) AS {_colname('rcon', c)}")
        ids.add(f"RCON{c}")
    for c in RCFN_ONLY:
        cols.append(f"MAX(CASE WHEN variable_id='RCFN{c}' THEN value END) AS {_colname('rcfn', c)}")
        ids.add(f"RCFN{c}")
    for c in RIAD_CODES:
        cols.append(f"MAX(CASE WHEN variable_id='RIAD{c}' THEN value END) AS {_colname('riad', c)}")
        ids.add(f"RIAD{c}")
    return ",\n  ".join(cols), sorted(ids)


# ===========================================================================
# PROCEDURAL HELPERS (pure Python, pytested; the builder's production derived layer).
# All operate on / return pandas float64 Series (NaN == absent). SPEC §2-§4 loci cited.
# ===========================================================================
def rowtotal(cols: Sequence[pd.Series]) -> pd.Series:
    """Stata ``egen rowtotal`` semantics: sum treating NaN as 0, **NaN iff ALL inputs NaN**.

    Used for the reconstructed aggregates that CLV builds with ``egen rowtotal`` (e.g.
    modern ``liquid`` = rowtotal(cash, securities, ffpurch), ``05 L108``; the ln_fi
    component sums, Table C.1). Distinct from a plain ``a+b`` (NULL-propagating), which the
    spec/30_build uses for securities & time_deposits arms — see :func:`plus`.
    """
    if not cols:
        raise ValueError("rowtotal needs at least one column")
    frame = pd.concat([pd.Series(c, dtype="float64").reset_index(drop=True) for c in cols], axis=1)
    total = frame.sum(axis=1, skipna=True)                 # NaN treated as 0
    all_na = frame.isna().all(axis=1)                      # missing iff every input missing
    total[all_na] = np.nan
    idx = cols[0].index if isinstance(cols[0], pd.Series) else None
    return pd.Series(total.to_numpy(), index=idx, dtype="float64")


def plus(*cols: pd.Series) -> pd.Series:
    """NULL-propagating sum (``a+b`` SQL semantics): NaN if ANY input NaN.

    Reproduces ``30_build``'s ``{cf(a)}+{cf(b)}`` for securities (``1754+1773``),
    time_deposits (``2604+6648``), and npl_tot (``1403+1407``) so those cells match the
    validated ``public_luck_panel`` bit-for-bit (SPEC §2.5/§2.6/§3).
    """
    out = pd.Series(cols[0], dtype="float64").copy()
    for c in cols[1:]:
        out = out + pd.Series(c, dtype="float64").values
    return out


def coalesce(*cols: pd.Series) -> pd.Series:
    """First non-NaN across columns, elementwise (SQL COALESCE)."""
    out = pd.Series(cols[0], dtype="float64").copy()
    for c in cols[1:]:
        out = out.where(out.notna(), pd.Series(c, dtype="float64").values)
    return out


def era_pick(period: pd.Series, arms: Sequence[tuple[Optional[pd.Timestamp], Optional[pd.Timestamp], pd.Series]]) -> pd.Series:
    """Era-splice: for each row pick the value of the arm whose ``[lo, hi)`` covers ``period``.

    ``arms`` is an ordered list of ``(lo, hi, value_series)``; ``lo=None`` == open below,
    ``hi=None`` == open above; the window is **[lo, hi)** (lo inclusive, hi exclusive),
    matching the dictionary's ``19840331 <= dt < 20100331`` convention (SPEC §2). Rows
    covered by no arm get NaN. This is the generic engine behind securities / time_deposits
    / ln_ci / ln_cc / ln_fi / surplus / ytdint_exp_dep (each cites its dict rows at the call
    site in :func:`_build_derived`).
    """
    per = pd.to_datetime(pd.Series(period).values)
    out = pd.Series(np.nan, index=pd.Series(period).index, dtype="float64")
    for lo, hi, val in arms:
        mask = np.ones(len(per), dtype=bool)
        if lo is not None:
            mask &= per >= np.datetime64(lo)
        if hi is not None:
            mask &= per < np.datetime64(hi)
        vals = pd.Series(val, dtype="float64").to_numpy()
        out_vals = out.to_numpy()
        out_vals[mask] = vals[mask]
        out = pd.Series(out_vals, index=out.index, dtype="float64")
    return out


def ratio(
    num: pd.Series,
    den: pd.Series,
    *,
    lo: Optional[float] = None,
    hi: Optional[float] = None,
    drop_zero_num: bool = False,
    keep_mask: Optional[pd.Series] = None,
) -> pd.Series:
    """Derived ratio ``num/den`` with the ``07`` validity/clip + Q4 masking rules (SPEC §4).

    * ``drop_zero_num`` — set the numerator missing when it is 0 first (``07 L61`` liquid,
      ``07 L102`` time_deposits, ``07 L107`` demand_deposits: ``replace x=. if x==0``).
    * ``lo``/``hi`` — "clip to [lo,hi]" means **set missing outside the band**, exactly as
      ``07 L134-147`` does (``replace r=. if r>hi | r<lo``) — NOT winsorize. The validity
      filter (leverage, liquid/oreo/deposit/noncore/time/demand ratios) is ``lo=0, hi=1``;
      income_ratio & nim are ``lo=-0.5, hi=0.5``; int_exp/int_inc ratios are ``lo=0, hi=1``.
    * ``keep_mask`` — keep the ratio only where True (else NaN); used for the Q4-only income
      ratios (``07 L120-122``: missing when ``quarter_number != 4``).

    Division by 0 or NaN denominator -> NaN.
    """
    n = pd.Series(num, dtype="float64").copy()
    d = pd.Series(den, dtype="float64").to_numpy()
    if drop_zero_num:
        n = n.mask(n == 0.0, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = n.to_numpy() / d
    r = np.where((d == 0.0) | np.isnan(d), np.nan, r)
    out = pd.Series(r, index=n.index, dtype="float64")
    if keep_mask is not None:
        out = out.where(pd.Series(keep_mask).to_numpy().astype(bool), np.nan)
    if lo is not None:
        out = out.mask(out < lo, np.nan)
    if hi is not None:
        out = out.mask(out > hi, np.nan)
    return out


def crisis_bvx(year: pd.Series) -> pd.Series:
    """BVX crisis dummy: 1 for year in {1873,1884,1890,1893,1907,1930,1984,1990,2007} (07 L52-55)."""
    y = pd.Series(year).astype("Int64")
    return y.isin(CRISIS_YEARS).astype("int8")


def size_quartile(assets: pd.Series, year: pd.Series) -> pd.Series:
    """Within-year asset quartile 1..4 (``07 L49`` ``xtile(assets,4) by(year)``).

    Approximates Stata ``xtile`` with a rank-based 4-quantile cut per year. **Deflation
    note:** CLV computes this on CPI-*deflated* assets, but the deflator is constant within
    a year, so within-year ranks (hence quartiles) are identical on nominal assets — this
    column is therefore deflation-invariant and correct without the CPI merge (SPEC §6.5).
    Rows with NaN assets get ``<NA>``.
    """
    df = pd.DataFrame({"a": pd.Series(assets, dtype="float64").values,
                       "y": pd.Series(year).astype("Int64").values})

    def _q(g: pd.Series) -> pd.Series:
        valid = g.dropna()
        if valid.empty:
            return pd.Series(pd.NA, index=g.index, dtype="Int64")
        try:
            q = pd.qcut(valid.rank(method="first"), 4, labels=[1, 2, 3, 4])
            return q.astype("Int64").reindex(g.index)
        except ValueError:  # too few distinct values for 4 bins
            return pd.Series(pd.NA, index=g.index, dtype="Int64")

    res = df.groupby("y", group_keys=False)["a"].apply(_q)
    res = res.reindex(df.index)   # restore original row order (apply concatenates in group order)
    return pd.Series(res.values, index=pd.Series(assets).index, dtype="Int64")


def deflate(nominal: pd.Series, cpi: pd.Series) -> pd.Series:
    """CPI deflation, CLV's raw-division treatment: ``real = nominal / cpi`` (SPEC §6.5).

    CLV deflate ``var = var / cpi_gfd`` (``07 L32-34``) with GFD's native Dec-31 annual CPI
    index and **no base year** (paper p.81). Provided + tested here as the procedural
    contract; **not applied in this builder** — the MODC output is nominal (matching the
    published ``luck_wide``/``public_luck_panel``), and CLV applies deflation only after the
    HIST+MODERN append in the combine step. Real levels are therefore gapped here (see
    ``_BUILD_META.gaps``); the §4 ratios are deflation-invariant and ARE built.
    """
    n = pd.Series(nominal, dtype="float64")
    c = pd.Series(cpi, dtype="float64").to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = n.to_numpy() / c
    r = np.where((c == 0.0) | np.isnan(c), np.nan, r)
    return pd.Series(r, index=n.index, dtype="float64")


# ===========================================================================
# The derived layer: assemble Luck-schema variables from the building blocks.
# Each variable cites its formula_id (variable_map.csv) + spec locus. DIVERGENCE(30_build)
# tags mark the spec-authorized coverage extensions over 30_build_public_luck_panel.py.
# ===========================================================================
def _build_derived(bb: pd.DataFrame) -> pd.DataFrame:
    """Given the building-block frame (rssd_id, period_end, cf_*/rcon_*/rcfn_*/riad_*),
    return the Luck-schema output frame. Pure over pandas — the tested production path."""
    period = bb["period_end"]
    year = pd.to_datetime(period).dt.year.astype("Int64")
    quarter = pd.to_datetime(period).dt.quarter.astype("Int64")

    out = pd.DataFrame({"rssd_id": bb["rssd_id"].values, "period_end": period.values})
    out["year"] = year.values
    out["quarter"] = quarter.values
    out["era"] = "MODC"

    def cf(c: str) -> pd.Series: return bb[_colname("cf", c)]
    def rcon(c: str) -> pd.Series: return bb[_colname("rcon", c)]
    def rcfn(c: str) -> pd.Series: return bb[_colname("rcfn", c)]
    def riad(c: str) -> pd.Series: return bb[_colname("riad", c)]

    # --- Part A balance-sheet levels (mechanical cf) -----------------------
    out["assets"] = cf("2170").values                 # F_assets_mod  §2.1  cf(2170)
    out["deposits"] = cf("2200").values               # F_dep_mod     §2.2  cf(2200)
    out["domestic_dep"] = rcon("2200").values         # F_domdep      §2.3  MAX(RCON2200)
    out["foreign_dep"] = rcfn("2200").values          # F_fordep      §2.3  RCFN2200
    out["demand_deposits"] = cf("2210").values        # F_demdep_mod  §2.4  cf(2210)
    out["ln_tot"] = cf("2122").values                 # F_lntot_mod   §2.8  cf(2122) net
    out["ln_tot_gross"] = plus(cf("2122"), cf("2123")).values  # F_lntotg_mod §2.8 (scope_v11=FALSE; mechanical, built)
    # ln_re — ERA-SPLIT (SPEC §10.6). cf(1410) through 2011Q4; the RCON1410 domestic aggregate
    # is RETIRED after 2011Q4 (only ~121 big FFIEC-031 filers still report RCFD1410), so cf(1410)
    # collapses. From 2012Q1 the RC-C Part I component sum reconstructs the total, fork-aware:
    # construction = rowtotal(F158,F159) else cf(1415); nonfarm-nonres = rowtotal(F160,F161) else
    # cf(1480); 1-4 family = rowtotal(1797,5367,5368); + farmland cf(1420) + multifamily cf(1460).
    # Prefer the still-filed cf(1410) where present (keeps the matched big-bank cells unchanged).
    # Identity-validated: reproduces CLV PUBLISHED ln_re for 290,234/290,322 post-2011 pub-only
    # cells (99.97% EXACT). F_lnre (dict :70,:493 + 2007-2011 identity + published match).
    re_constr = coalesce(rowtotal([cf("F158"), cf("F159")]), cf("1415"))
    re_nonfarm = coalesce(rowtotal([cf("F160"), cf("F161")]), cf("1480"))
    re_14fam = rowtotal([cf("1797"), cf("5367"), cf("5368")])
    re_comp = rowtotal([re_constr, cf("1420"), cf("1460"), re_14fam, re_nonfarm])
    out["ln_re"] = era_pick(period, [
        (None, B_LNRE, cf("1410")),
        (B_LNRE, None, coalesce(cf("1410"), re_comp)),
    ]).values
    # ln_cons — ERA-SPLIT (SPEC §10.3). cf(1975) through 2011Q4 (RCFD/RCON1975 retired after 2011Q4);
    # from 2012Q1 the FFIEC RC-C item-6 successor rowtotal(B538,B539,K137,K207) — identity-validated:
    # == cf(1975) EXACTLY for all 27,408 2011 bank-quarters. F_lncons (dict :92,:566 + 2011 probe).
    out["ln_cons"] = era_pick(period, [
        (None, B_LNCONS, cf("1975")),
        (B_LNCONS, None, rowtotal([cf("B538"), cf("B539"), cf("K137"), cf("K207")])),
    ]).values
    out["ln_agr"] = cf("1590").values                 # F_lnagr       §2.8  cf(1590)
    out["oreo"] = cf("2150").values                   # F_oreo_mod    §2.10 cf(2150)
    out["llres"] = cf("3123").values                  # F_llres       §2.9  cf(3123); pre-1976 3120 arm inapplicable (panel starts 1976Q1)
    out["equity"] = cf("3210").values                 # F_eq_mod      §2.11 cf(3210)
    out["subdebt"] = cf("3200").values                # F_subdebt     §2.19 cf(3200)
    out["liab_tot"] = cf("2948").values               # F_liabtot     §2.19 cf(2948)
    out["brokered_dep"] = rcon("2365").values         # F_broker      §2.19 RCON2365

    # otherbor_liab — ERA-SPLIT (SPEC §10.2 dict :39-44). DIVERGENCE(30_build/pre-remediation):
    # was cf(3190) only (NULL pre-1994); ADD pre-1994 arm rowtotal(cf 2850, cf 2910). Keep cf(3190)
    # for 1994Q1+ unchanged (currently matched; maturity chain only 93.4% reproduces 3190). F_othbor_mod.
    out["otherbor_liab"] = era_pick(period, [
        (None, B_OTHERBOR, rowtotal([cf("2850"), cf("2910")])),
        (B_OTHERBOR, None, cf("3190")),
    ]).values

    # ffsold / ffpurch — PURE fed funds, ERA-SPLIT (SPEC §10.1 dict :34/:35, :17/:18). Pure arm 0276/0278
    # ends 1996Q4; post-2002 pure arm = RCON B987 (ffsold) / RCON B993 (ffpurch), cf-coalesced with the
    # 2002-2011 RCFD twin. The 1997Q1-2001Q4 window has no pure arm -> NULL (honest; combined ffrepo covers
    # it but is a different concept). NB: the campaign brief's "RCONB987 for ffpurch" was ffsold's code;
    # ffpurch post-2002 = B993 (dict :35). F_ffsold / F_ffpurch.
    out["ffsold"] = era_pick(period, [
        (None, B_FF_PURE_END, cf("0276")),
        (B_FF_PURE_POST, None, cf("B987")),
    ]).values
    out["ffpurch"] = era_pick(period, [
        (None, B_FF_PURE_END, cf("0278")),
        (B_FF_PURE_POST, None, cf("B993")),
    ]).values
    out["npl_tot"] = plus(cf("1403"), cf("1407")).values  # F_npl      §3    cf(1403)+cf(1407), 1982+

    # cash — DIVERGENCE(30_build): 30_build uses cf(0010) only; SPEC §2.7 dict :1-2 adds the
    # post-1984 RCFD0081+RCFD0071 arm. Implemented as a *fallback* (COALESCE) so validated
    # cf(0010) cells are unchanged (0010 = 0081+0071 by construction) and coverage is only
    # ADDED where 0010 is null. F_cash.
    out["cash"] = coalesce(cf("0010"), plus(cf("0081"), cf("0071"))).values

    # securities — ERA-SPLIT (SPEC §2.6 / Table C.1). <1994Q1: cf(0390); else cf(1754)+cf(1773).
    # Plain '+' (NULL-propagating) matches 30_build bit-for-bit. F_sec_mod. ~94% pre-1994 ceiling.
    out["securities"] = era_pick(period, [
        (None, B_SECURITIES, cf("0390")),
        (B_SECURITIES, None, plus(cf("1754"), cf("1773"))),
    ]).values

    # time_deposits — ERA-SPLIT 3-arm (SPEC §2.5 dict :28-30). DIVERGENCE(30_build): 30_build
    # stops at cf(2604)+cf(6648); SPEC adds the post-2010 J473+J474+6648 arm (RCON2604 ends
    # 2011, so the 2-arm recipe under-reports 2011+). F_timedep_mod.
    out["time_deposits"] = era_pick(period, [
        (None, B_TIMEDEP_1, cf("2514")),
        (B_TIMEDEP_1, B_TIMEDEP_2, plus(cf("2604"), cf("6648"))),
        (B_TIMEDEP_2, None, plus(rcon("J473"), rcon("J474"), cf("6648"))),
    ]).values

    # ln_ci — ERA-SPLIT (SPEC §2.8 dict :89-91). DIVERGENCE(30_build): 30_build uses cf(1766)
    # only; SPEC adds pre-1984 RCFD1600 arm + the 1763+1764 fallback when 1766 null. F_lnci.
    out["ln_ci"] = era_pick(period, [
        (None, B_LNCI, cf("1600")),
        (B_LNCI, None, coalesce(cf("1766"), plus(cf("1763"), cf("1764")))),
    ]).values

    # surplus — ERA-SPLIT (SPEC §2.12 dict :64-65). DIVERGENCE(30_build): 30_build uses
    # cf(3839) only (null pre-1990); SPEC adds pre-1990 RCFD3240 arm -> extends 1976-1990. F_surp_mod.
    out["surplus"] = era_pick(period, [
        (None, B_SURPLUS, cf("3240")),
        (B_SURPLUS, None, cf("3839")),
    ]).values

    # ln_cc — Table C.1 (SPEC §2.8), RCON: <2001Q1 RCON2008 else RCONB538. NEW (not in 30_build). F_lncc.
    out["ln_cc"] = era_pick(period, [
        (None, B_LNCC, rcon("2008")),
        (B_LNCC, None, rcon("B538")),
    ]).values

    # ln_fi — Table C.1 (SPEC §2.8), RCON, 3-arm. <1984Q1 RCON1495; 1984Q1..2001Q1
    # rowtotal(1505,1510,1517,1756,1757); >=2001Q1 rowtotal(B531,B534,B535). NEW. F_lnfi.
    lnfi_mid = rowtotal([rcon("1505"), rcon("1510"), rcon("1517"), rcon("1756"), rcon("1757")])
    lnfi_new = rowtotal([rcon("B531"), rcon("B534"), rcon("B535")])
    out["ln_fi"] = era_pick(period, [
        (None, B_LNFI_1, rcon("1495")),
        (B_LNFI_1, B_LNFI_2, lnfi_mid),
        (B_LNFI_2, None, lnfi_new),
    ]).values

    # insured_deposits — ERA-SPLIT (SPEC §2.19 dict :95-96), RCON. <2006Q2 RCON2702 (Q2-only
    # 1983-1990) else RCONF049+RCONF045. NEW. F_insured.
    out["insured_deposits"] = era_pick(period, [
        (None, B_INSURED, rcon("2702")),
        (B_INSURED, None, plus(rcon("F049"), rcon("F045"))),
    ]).values

    # liquid — reconstructed_agg, modern (SPEC §2.15 / 05 L108): rowtotal(cash, securities,
    # ffpurch). ffpurch (cf 0278) exists only 1988-1996, so outside that window liquid =
    # cash+securities (rowtotal treats the missing ffpurch as 0). Published concept (p.81)
    # excludes fed funds -> ffpurch is a documented do-file quirk; reproduced verbatim. F_liquid_mod.
    out["liquid"] = rowtotal([out["cash"], out["securities"], out["ffpurch"]]).values

    # --- Part B income levels (YTD; RIAD-only) -----------------------------
    out["ytdnetinc"] = riad("4340").values            # F_netinc   §3  RIAD4340
    out["ytdint_inc"] = riad("4107").values           # F_intinc   §3  RIAD4107
    out["ytdint_exp"] = riad("4073").values           # F_intexp   §3  RIAD4073
    out["ytdint_inc_ln"] = riad("4010").values        # F_intincln §3  RIAD4010 (1969+; whole MODC era)
    out["ytdllprov"] = riad("4230").values            # F_llprov   §3  RIAD4230
    out["num_employees"] = riad("4150").values        # F_numemp   §3  RIAD4150 (Table C.1 p.112)

    # ytdint_exp_dep — ERA-CHAIN (SPEC §3 dict :259-262). pre-2017: COALESCE(RIAD4170,
    # rowtotal(4174,4176,4172)); 2017+: rowtotal(4508,0093,HK03,HK04,4172). Note: 4170 ends
    # 2011 and 4174/4176 end 1996/1986, so 2012Q1-2016Q4 has no dict arm -> gapped honestly
    # (recorded in _BUILD_META.gaps). F_intexpdep.
    iedep_pre = coalesce(riad("4170"), rowtotal([riad("4174"), riad("4176"), riad("4172")]))
    iedep_new = rowtotal([riad("4508"), riad("0093"), riad("HK03"), riad("HK04"), riad("4172")])
    out["ytdint_exp_dep"] = era_pick(period, [
        (None, B_INTEXPDEP, iedep_pre),
        (B_INTEXPDEP, None, iedep_new),
    ]).values

    # --- Part C derived ratios (07, on the nominal panel; deflation-invariant) ----
    a = out["assets"]
    is_q4 = out["quarter"].eq(4)
    out["leverage"] = ratio(out["equity"], a, lo=0.0, hi=1.0).values            # R_leverage 07 L66
    out["loan_ratio"] = ratio(out["ln_tot"], a).values                         # R_loanratio 07 L82 (no clip)
    out["deposit_ratio"] = ratio(out["deposits"], a, lo=0.0, hi=1.0).values    # R_depratio 07 L83
    out["oreo_ratio"] = ratio(out["oreo"], plus(out["ln_tot"], out["oreo"]), lo=0.0, hi=1.0).values  # R_oreoratio 07 L79
    out["liquid_ratio"] = ratio(out["liquid"], a, lo=0.0, hi=1.0, drop_zero_num=True).values  # R_liqratio 07 L61-62
    out["time_ratio"] = ratio(out["time_deposits"], a, lo=0.0, hi=1.0, drop_zero_num=True).values  # R_timeratio 07 L102-105
    out["demand_ratio"] = ratio(out["demand_deposits"], a, lo=0.0, hi=1.0, drop_zero_num=True).values  # R_demratio 07 L107
    # noncore_ratio — modern arm (year>1941): (deposits_time + otherbor_liab)/assets (07 L88-92).
    noncore_funding = rowtotal([out["time_deposits"], out["otherbor_liab"]])
    out["noncore_ratio"] = ratio(noncore_funding, a, lo=0.0, hi=1.0).values     # R_noncore
    out["npl_ratio"] = ratio(out["npl_tot"], out["ln_tot"]).values             # R_nplratio 07 L114 (no clip)
    out["income_ratio"] = ratio(out["ytdnetinc"], a, lo=-0.5, hi=0.5, keep_mask=is_q4).values  # R_incratio 07 L113,138 Q4
    out["prov_ratio"] = ratio(out["ytdllprov"], out["ln_tot"], keep_mask=is_q4).values  # R_provratio 07 L115 Q4
    out["int_exp_ratio"] = ratio(out["ytdint_exp_dep"], a, lo=0.0, hi=1.0, keep_mask=is_q4).values  # R_intexpr 07 L116,140 Q4
    out["int_inc_ratio"] = ratio(out["ytdint_inc_ln"], a, lo=0.0, hi=1.0, keep_mask=is_q4).values   # R_intincr 07 L117,141 Q4
    nim_num = out["ytdint_inc_ln"].astype("float64") - out["ytdint_exp_dep"].astype("float64")
    out["nim"] = ratio(nim_num, a, lo=-0.5, hi=0.5).values                     # R_nim 07 L118,139

    # --- Panel-derived (deflation-invariant / year-based) ------------------
    out["size_cat"] = size_quartile(out["assets"], out["year"]).values         # R_sizecat 07 L49
    out["crisisBVX"] = crisis_bvx(out["year"]).values                          # R_crisis 07 L52-55

    return out


# ===========================================================================
# Map-driven coverage: what the scope requires vs what we build vs honest gaps.
# ===========================================================================
#: Output variables this builder produces (the columns of _build_derived, excluding keys).
BUILT_VARS = [
    "assets", "deposits", "domestic_dep", "foreign_dep", "demand_deposits", "time_deposits",
    "securities", "cash", "ln_tot", "ln_tot_gross", "ln_re", "ln_ci", "ln_cons", "ln_agr",
    "ln_cc", "ln_fi", "oreo", "llres", "equity", "surplus", "subdebt", "liab_tot",
    "otherbor_liab", "ffsold", "ffpurch", "brokered_dep", "insured_deposits", "npl_tot",
    "liquid", "ytdnetinc", "ytdint_inc", "ytdint_exp", "ytdint_inc_ln", "ytdint_exp_dep",
    "ytdllprov", "num_employees",
    "leverage", "loan_ratio", "deposit_ratio", "oreo_ratio", "liquid_ratio", "time_ratio",
    "demand_ratio", "noncore_ratio", "npl_ratio", "income_ratio", "prov_ratio",
    "int_exp_ratio", "int_inc_ratio", "nim", "size_cat", "crisisBVX",
]

#: Scoped MODC variables intentionally NOT built from raw, with the honest reason (SPEC §0
#: no-fabrication contract). Keyed variable -> reason. These are recorded in _BUILD_META.gaps.
GAP_VARS = {
    "ln_oth": "No published Table C.1 recipe (SPEC §2.8 F_lnoth): 'Other Loans' is a CLV "
              ".dta residual column, not an MDRM sum — cannot derive from raw without "
              "fabrication. Omitted.",
    "size": "log(deflated assets) (07 L47). Requires CPI (GFD cpi_gfd) deflation, a "
            "07-combine step applied AFTER the HIST+MODERN append; the GFD CPI CSV is not in "
            "the warehouse. Nominal levels are built; all §4 ratios are deflation-invariant; "
            "size_cat (rank-invariant) IS built. Real 'size' deferred to the combine layer.",
    "log_age": "log(year - charter_year) (07 L44). Requires the bank establishment/charter "
               "year, which is NOT in call_report_filings (needs a NIC/institution_attributes "
               "merge). Out of the pure-raw MODC scope; deferred.",
    "cpi_deflator": "CLV cpi_gfd (GFD US CPI, SPEC §6.5). External GFD CSV not in the "
                    "warehouse; a 07-combine step. deflate() is provided+tested as the "
                    "contract but not applied here (nominal output).",
    "leverage_capital": "capital/assets (07 L68). 'capital' is a HIST OCC paid-in-capital "
                        "line item (SPEC §2.12); no 1976+ MDRM counterpart. HIST-only.",
    "surplus_ratio": "surplus_profit/equity (07 L71). surplus_profit is a HIST reconstruction "
                     "(SPEC §2.12); no modern counterpart. HIST-only.",
    "profit_shortfall": "undivided_profits/equity threshold (07 L74-75). undivided_profits is "
                        "a HIST OCC line item (SPEC §2.12); HIST-only.",
    "emergency_borrowing": "emergency/assets (07 L96). 'emergency' = HIST bills_payable+"
                           "rediscounts reconstruction (SPEC §2.16); HIST-only.",
    "interbank_ratio": "interbank/assets (07 L100). 'interbank' is a HIST reconstruction "
                       "(SPEC §2.13); folded into deposits post-1976. HIST-only.",
    "ytdint_exp_dep[2012-2016]": "Coverage gap within a built var: the dict recipe (SPEC §3 "
                                 ":259-262) has no full arm for 2012Q1-2016Q4 (RIAD4170 ends "
                                 "2011; 4174/4176 end 1996/1986; the HK03/HK04 arm starts "
                                 "2017). Those quarters are NaN except the small foreign-"
                                 "office-filer subset whose RIAD4172 component (alive through "
                                 "2026) survives the alt-arm rowtotal (~1.8k bank-quarters, an "
                                 "honest partial per rowtotal semantics, NOT an approximation); "
                                 "nim & int_exp_ratio inherit the gap for 2012-2016 Q4.",
}


def _coverage_report() -> dict:
    """Cross-check BUILT_VARS + GAP_VARS against the scoped MODC variable_map. Map-driven."""
    df = vm.load_variable_map(vm.SPEC_CSV if vm.SPEC_CSV.exists() else vm.SHIPPED_CSV)
    sc = vm.scoped(df)  # scope_v11 == TRUE
    # MODC-relevant rows: era touching 1976+ (contains '1976' or '1969' or '1959-2026') or
    # 'combined' derived ratios; exclude pure entity_rule/not_derivable/deflator rows and the
    # dta-only / hist-only eras — those are handled as construction rules or gaps.
    modc = sc[
        sc["era"].str.contains("1976|1969|1959-2026|combined", regex=True)
        & (sc["source_kind"] != "entity_rule")
    ]
    required = sorted(set(modc["variable"]))
    built = set(BUILT_VARS)
    gapped = set(k.split("[")[0] for k in GAP_VARS)
    covered = built | gapped
    uncovered = sorted(v for v in required if v not in covered)
    return {
        "scoped_modc_variables": required,
        "n_required": len(required),
        "n_built": len(built),
        "n_gapped_concepts": len(gapped),
        "uncovered_variables": uncovered,  # must be empty (no silent omission)
    }


# ===========================================================================
# Warehouse table versions (from the manifest) for provenance.
# ===========================================================================
def _warehouse_versions(con: duckdb.DuckDBPyConnection) -> dict:
    try:
        rows = con.execute(
            "SELECT name, row_count, period_span FROM main.freenic_manifest "
            "WHERE name IN ('call_report_filings')"
        ).fetchall()
        return {r[0]: {"row_count": r[1], "period_span": r[2]} for r in rows}
    except Exception as e:  # pragma: no cover
        return {"error": str(e)}


# ===========================================================================
# Self-smoke: 6 anchor cells vs the validated public_luck_panel (rssd-keyed).
# ===========================================================================
def _smoke(con: duckdb.DuckDBPyConnection, out_df: pd.DataFrame) -> dict:
    """Informal 6-anchor smoke vs public_luck_panel.parquet (SPEC §5; the harness does the
    formal G-MATCH next batch). Anchors are post-1994 large-bank cells where the spec
    extensions do NOT alter the value, so they should match the validated panel exactly."""
    anchors = [
        (852218, "2008-12-31", "assets"),      # JPMorgan Chase Bank NA — unit gate ~$1.75T (SPEC §2.1)
        (852218, "2008-12-31", "deposits"),
        (480228, "2008-12-31", "equity"),      # Bank of America NA
        (480228, "2008-12-31", "ln_tot"),
        (476810, "2008-12-31", "securities"),  # Citibank NA
        (852218, "2008-12-31", "time_deposits"),
    ]
    results = []
    for rssd, pe, var in anchors:
        ref = con.execute(
            f"SELECT {var} FROM read_parquet('{PUBLIC_LUCK_PANEL.as_posix()}') "
            f"WHERE rssd_id={rssd} AND period_end=DATE '{pe}'"
        ).fetchone()
        ref_v = float(ref[0]) if ref and ref[0] is not None else None
        m = out_df[(out_df["rssd_id"] == rssd) & (out_df["period_end"].astype(str).str[:10] == pe)]
        built_v = float(m[var].iloc[0]) if len(m) and pd.notna(m[var].iloc[0]) else None
        if ref_v is None or built_v is None:
            match = (ref_v is None and built_v is None)
            rel = None
        else:
            rel = abs(built_v - ref_v) / abs(ref_v) if ref_v != 0 else abs(built_v - ref_v)
            match = rel <= 1e-9
        results.append({"rssd_id": rssd, "period_end": pe, "var": var,
                        "reference": ref_v, "built": built_v,
                        "rel_delta": rel, "match": bool(match)})
    n_match = sum(1 for r in results if r["match"])
    return {"n_anchors": len(results), "n_match": n_match, "anchors": results}


# ===========================================================================
# stages
# ===========================================================================
def _connect_readonly() -> duckdb.DuckDBPyConnection:
    """READ-ONLY warehouse connection (asserted — the non-negotiable)."""
    assert WAREHOUSE.exists(), f"warehouse not found: {WAREHOUSE}"
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    ro = con.execute("SELECT current_setting('access_mode')").fetchone()[0]
    assert str(ro).upper().startswith("READ"), f"warehouse not opened read-only: {ro}"
    return con


def stage_scan() -> float:
    """Heavy stage: one conditional-aggregation COPY per period chunk (30_build single-pass
    pattern — DuckDB streams straight to parquet, no pandas). Completed chunks are SKIPPED,
    so a killed run resumes. Returns scan seconds (this invocation)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    agg_cols, inlist = _agg_sql()
    ids_sql = ",".join(f"'{c}'" for c in inlist)
    t_scan = time.time()
    con = _connect_readonly()
    for lo, hi in SCAN_CHUNKS:
        dest = _chunk_path(lo, hi)
        if dest.exists():
            print(f"[scan] SKIP {dest.name} (already written)", flush=True)
            continue
        tmp = dest.with_suffix(".parquet.tmp")   # write-then-rename: no half-written chunk survives
        t_c = time.time()
        print(f"[scan] chunk {lo.year}-{hi.year}: COPY ... ({len(inlist)} MDRM ids)", flush=True)
        con.execute(f"""
            COPY (
              SELECT rssd_id, period_end,
                {agg_cols}
              FROM call_report_filings
              WHERE period_end BETWEEN DATE '{max(lo, MODC_LO)}' AND DATE '{min(hi, MODC_HI)}'
                AND variable_id IN ({ids_sql})
              GROUP BY rssd_id, period_end
            ) TO '{tmp.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        tmp.replace(dest)
        print(f"[scan] chunk {lo.year}-{hi.year} DONE in {time.time()-t_c:,.1f}s -> {dest.name}",
              flush=True)
    con.close()
    secs = time.time() - t_scan
    print(f"[scan] all chunks present ({len(SCAN_CHUNKS)}) in {secs:,.1f}s", flush=True)
    return secs


def stage_derive(scan_secs: float = float("nan")) -> None:
    """Fast stage: read the chunk parquets, apply the derived layer, write the final
    parquet + _BUILD_META.json + the 6-anchor smoke."""
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Coverage cross-check FIRST (fails loud on any silent omission).
    cov = _coverage_report()
    assert not cov["uncovered_variables"], (
        f"scoped MODC variables neither built nor gapped: {cov['uncovered_variables']}"
    )

    missing = [(_chunk_path(lo, hi)) for lo, hi in SCAN_CHUNKS if not _chunk_path(lo, hi).exists()]
    assert not missing, f"scan chunks missing (run --stage scan first): {[m.name for m in missing]}"

    print("[derive] loading building-block chunks ...", flush=True)
    bb = pd.concat(
        [pd.read_parquet(_chunk_path(lo, hi)) for lo, hi in SCAN_CHUNKS],
        ignore_index=True,
    )
    print(f"[derive] {len(bb):,} bank-quarters loaded; building derived layer ...", flush=True)

    out_df = _build_derived(bb)
    out_df = out_df.sort_values(["rssd_id", "period_end"]).reset_index(drop=True)
    out_df.to_parquet(OUT_PARQUET, engine="pyarrow", compression="zstd", index=False)
    print(f"[derive] parquet written; running smoke ...", flush=True)

    con = _connect_readonly()
    smoke = _smoke(con, out_df)
    versions = _warehouse_versions(con)
    con.close()

    _, inlist = _agg_sql()
    runtime = time.time() - t0
    n_rows = len(out_df)
    n_entities = int(out_df["rssd_id"].nunique())
    n_quarters = int(out_df["period_end"].nunique())
    q_lo = str(pd.to_datetime(out_df["period_end"]).min().date())
    q_hi = str(pd.to_datetime(out_df["period_end"]).max().date())

    meta = {
        "deliverable": "luck_equivalent_1976_2026",
        "campaign": "FREENIC11_RECONSTRUCTION_20260715",
        "builder": "pipeline/reconstruction/build_luck_equivalent.py",
        "description": "TRUE independent Luck-schema re-derivation 1976Q1-2026Q1 from "
                       "Fed-direct raw MDRM (call_report_filings), MODC / scope_v11.",
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "warehouse": str(WAREHOUSE),
        "warehouse_read_only": True,
        "warehouse_table_versions": versions,
        "rows": n_rows,
        "entities": n_entities,
        "quarters": n_quarters,
        "period_range": [q_lo, q_hi],
        "scan_seconds": (round(scan_secs, 1) if scan_secs == scan_secs else
                         "resumed (see per-chunk [scan] log lines)"),
        "derive_runtime_seconds": round(runtime, 1),
        "n_building_block_mdrm_ids": len(inlist),
        "variables_built": BUILT_VARS,
        "n_variables_built": len(BUILT_VARS),
        "coverage": cov,
        "gaps": GAP_VARS,
        "divergences_from_30_build": {
            "cash": "added post-1984 RCFD0081+RCFD0071 fallback (COALESCE) — SPEC §2.7 F_cash "
                    "(coverage-only; 0010 cells unchanged).",
            "time_deposits": "added post-2010 J473+J474+6648 arm — SPEC §2.5 F_timedep_mod "
                             "(30_build stops at 2604+6648, under-reports 2011+).",
            "ln_ci": "added pre-1984 RCFD1600 arm + 1763+1764 fallback — SPEC §2.8 F_lnci.",
            "surplus": "added pre-1990 RCFD3240 arm — SPEC §2.12 F_surp_mod (extends 1976-1990).",
            "ffpurch": "SPEC §10.1: added post-2002 pure arm cf(B993) (dict :35); pure 0278 ends "
                       "1996Q4, 1997-2001 has no pure arm (NULL). Corrects brief's 'B987' (=ffsold).",
            "ffsold": "SPEC §10.1: added post-2002 pure arm cf(B987) (dict :18); symmetric with ffpurch.",
            "otherbor_liab": "SPEC §10.2: added pre-1994 arm rowtotal(cf 2850, cf 2910) (dict :39-40); "
                             "cf(3190) kept for 1994Q1+ (unchanged, matched).",
            "ln_cons": "SPEC §10.3: added post-2011 RC-C item-6 successor rowtotal(cf B538,B539,K137,K207) "
                       "(dict :92,:566); == cf(1975) exactly for all 27,408 2011 bank-quarters (identity).",
            "ln_re": "SPEC §10.6: added post-2011 RC-C Part I component-sum successor (fork-aware "
                     "F158+F159|1415 construction, F160+F161|1480 nonfarm-nonres, 1797+5367+5368 "
                     "1-4family, +1420 farmland +1460 multifamily), preferring still-filed cf(1410); "
                     "RCON1410 aggregate retired 2011Q4. Reproduces PUBLISHED ln_re for 99.97% of "
                     "post-2011 pub-only cells (dict :70,:493 + 2007-2011 identity).",
            "new_variables_not_in_30_build": [
                "foreign_dep", "otherbor_liab", "brokered_dep", "insured_deposits", "ln_cc",
                "ln_fi", "ln_tot_gross", "ln_re(as-is)", "num_employees", "ytdint_inc_ln",
                "ytdint_exp_dep", "liquid", "all §4 derived ratios", "size_cat", "crisisBVX",
            ],
        },
        "self_smoke_vs_public_luck_panel": smoke,
        "units": "USD thousands (dollar items, matches call_report_filings + luck_wide); "
                 "ratios dimensionless; income items are YTD.",
        "no_fabrication_contract": "Variables not derivable from raw per spec are omitted and "
                                   "listed in 'gaps' — never approximated (SPEC §0).",
        "output_parquet": str(OUT_PARQUET),
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)

    print(f"[build_luck_equivalent] WROTE {OUT_PARQUET}")
    print(f"  {n_rows:,} rows | {n_entities:,} entities | {n_quarters} quarters "
          f"| {q_lo}..{q_hi}")
    print(f"  {len(BUILT_VARS)} variables built; smoke {smoke['n_match']}/{smoke['n_anchors']} "
          f"anchors match; runtime {runtime:,.1f}s")
    print(f"[build_luck_equivalent] META {OUT_META}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--stage", choices=["scan", "derive", "all"], default="all")
    args = p.parse_args(argv)
    scan_secs = float("nan")
    if args.stage in ("scan", "all"):
        scan_secs = stage_scan()
    if args.stage in ("derive", "all"):
        stage_derive(scan_secs)


if __name__ == "__main__":
    main()
