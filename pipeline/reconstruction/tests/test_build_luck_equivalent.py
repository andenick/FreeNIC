"""Tests for build_luck_equivalent's procedural layer (era splices, rowtotal, ratio
constructions, deflation, crisisBVX, size_cat).

Fast, pure, fixture-based, NO warehouse (the heavy SQL scan is not exercised here). These
functions ARE the builder's production derived layer, so testing them tests the real code
path. Spec loci are in the tested functions' docstrings (SPEC §2-§4 / §6.5).
"""

import numpy as np
import pandas as pd
import pytest

from pipeline.reconstruction import build_luck_equivalent as b


# --------------------------------------------------------------------------- rowtotal
def test_rowtotal_sums_treating_nan_as_zero():
    a = pd.Series([1.0, 2.0, np.nan])
    c = pd.Series([10.0, np.nan, np.nan])
    out = b.rowtotal([a, c])
    assert out.tolist()[:2] == [11.0, 2.0]


def test_rowtotal_all_nan_is_nan():
    # egen rowtotal: missing IFF every input missing (05 L108 semantics)
    a = pd.Series([np.nan, 5.0])
    c = pd.Series([np.nan, 1.0])
    out = b.rowtotal([a, c])
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 6.0


# --------------------------------------------------------------------------- plus / coalesce
def test_plus_propagates_nan():
    # plain '+' (30_build securities/time_deposits/npl) is NULL-propagating
    a = pd.Series([1.0, 2.0])
    c = pd.Series([np.nan, 3.0])
    out = b.plus(a, c)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 5.0


def test_coalesce_first_non_nan():
    a = pd.Series([np.nan, 2.0, np.nan])
    c = pd.Series([9.0, 8.0, np.nan])
    out = b.coalesce(a, c)
    assert out.iloc[0] == 9.0   # a null -> fall to c
    assert out.iloc[1] == 2.0   # a present -> keep a
    assert np.isnan(out.iloc[2])


# --------------------------------------------------------------------------- era_pick
def test_era_pick_half_open_windows():
    # securities: <1994Q1 -> arm0; >=1994Q1 -> arm1  (SPEC §2.6)
    period = pd.Series(pd.to_datetime(["1993-12-31", "1994-03-31", "2020-03-31"]))
    arm0 = pd.Series([10.0, 10.0, 10.0])
    arm1 = pd.Series([20.0, 20.0, 20.0])
    out = b.era_pick(period, [(None, b.B_SECURITIES, arm0), (b.B_SECURITIES, None, arm1)])
    assert out.tolist() == [10.0, 20.0, 20.0]


def test_era_pick_three_arm_time_deposits_boundaries():
    # boundaries 1984Q1 and 2010Q1 (SPEC §2.5 dict :28-30), [lo,hi) convention
    period = pd.Series(pd.to_datetime(["1983-12-31", "1984-03-31", "2009-12-31", "2010-03-31"]))
    a0 = pd.Series([1.0] * 4)
    a1 = pd.Series([2.0] * 4)
    a2 = pd.Series([3.0] * 4)
    out = b.era_pick(period, [
        (None, b.B_TIMEDEP_1, a0),
        (b.B_TIMEDEP_1, b.B_TIMEDEP_2, a1),
        (b.B_TIMEDEP_2, None, a2),
    ])
    assert out.tolist() == [1.0, 2.0, 2.0, 3.0]


def test_era_pick_uncovered_row_is_nan():
    period = pd.Series(pd.to_datetime(["2000-03-31"]))
    arm = pd.Series([5.0])
    # arm window ends 1994 -> 2000 uncovered -> NaN (honest gap, no fabrication)
    out = b.era_pick(period, [(None, b.B_SECURITIES, arm)])
    assert np.isnan(out.iloc[0])


# --------------------------------------------------------------------------- ratio
def test_ratio_basic():
    out = b.ratio(pd.Series([50.0]), pd.Series([100.0]))
    assert out.iloc[0] == 0.5


def test_ratio_zero_denominator_is_nan():
    out = b.ratio(pd.Series([50.0]), pd.Series([0.0]))
    assert np.isnan(out.iloc[0])


def test_ratio_validity_filter_sets_missing_outside_band():
    # 07 L134-147: "clip to [0,1]" == set missing if >1 or <0 (NOT winsorize)
    out = b.ratio(pd.Series([150.0, -10.0, 50.0]), pd.Series([100.0, 100.0, 100.0]),
                  lo=0.0, hi=1.0)
    assert np.isnan(out.iloc[0])   # 1.5 > 1 -> missing
    assert np.isnan(out.iloc[1])   # -0.1 < 0 -> missing
    assert out.iloc[2] == 0.5      # in band -> kept


def test_ratio_income_band_minus_half_to_half():
    out = b.ratio(pd.Series([60.0, -60.0, 10.0]), pd.Series([100.0, 100.0, 100.0]),
                  lo=-0.5, hi=0.5)
    assert np.isnan(out.iloc[0])   # 0.6 > 0.5
    assert np.isnan(out.iloc[1])   # -0.6 < -0.5
    assert out.iloc[2] == 0.1


def test_ratio_drop_zero_numerator():
    # 07 L61/L102/L107: liquid/time/demand set missing if the level is 0 first
    out = b.ratio(pd.Series([0.0, 30.0]), pd.Series([100.0, 100.0]), drop_zero_num=True)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 0.3


def test_ratio_q4_keep_mask():
    # income ratios are Q4-only (07 L120-122)
    is_q4 = pd.Series([True, False])
    out = b.ratio(pd.Series([10.0, 10.0]), pd.Series([100.0, 100.0]), keep_mask=is_q4)
    assert out.iloc[0] == 0.1
    assert np.isnan(out.iloc[1])


# --------------------------------------------------------------------------- crisis_bvx
def test_crisis_bvx_modern_years():
    y = pd.Series([1983, 1984, 1990, 1991, 2007, 2008])
    out = b.crisis_bvx(y)
    assert out.tolist() == [0, 1, 1, 0, 1, 0]


# --------------------------------------------------------------------------- size_quartile
def test_size_quartile_within_year():
    # 8 banks in one year -> two per quartile 1..4 (07 L49 xtile by year)
    assets = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    year = pd.Series([2000] * 8)
    out = b.size_quartile(assets, year)
    assert out.tolist() == [1, 1, 2, 2, 3, 3, 4, 4]


def test_size_quartile_deflation_invariant():
    # a within-year constant deflator does not change ranks -> quartiles identical
    assets = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    year = pd.Series([2000] * 8)
    nominal = b.size_quartile(assets, year)
    real = b.size_quartile(assets / 2.37, year)  # divide by a constant CPI
    assert nominal.tolist() == real.tolist()


def test_size_quartile_interleaved_years_stay_aligned():
    # rows are NOT grouped by year -> the per-year quartile must land back on the SAME row
    # (regression: groupby.apply concatenates in group order; result must be reindexed).
    assets = pd.Series([1.0, 100.0, 2.0, 200.0, 3.0, 300.0, 4.0, 400.0])
    year = pd.Series([2000, 2001, 2000, 2001, 2000, 2001, 2000, 2001])
    out = b.size_quartile(assets, year)
    # within 2000: assets 1,2,3,4 -> quartiles 1,2,3,4 at positions 0,2,4,6
    assert out.iloc[0] == 1 and out.iloc[2] == 2 and out.iloc[4] == 3 and out.iloc[6] == 4
    # within 2001: assets 100,200,300,400 -> quartiles 1,2,3,4 at positions 1,3,5,7
    assert out.iloc[1] == 1 and out.iloc[3] == 2 and out.iloc[5] == 3 and out.iloc[7] == 4


def test_size_quartile_nan_assets_are_na():
    assets = pd.Series([np.nan, np.nan])
    year = pd.Series([2000, 2000])
    out = b.size_quartile(assets, year)
    assert out.isna().all()


# --------------------------------------------------------------------------- deflate
def test_deflate_divides_by_cpi():
    out = b.deflate(pd.Series([237.0]), pd.Series([2.37]))
    assert out.iloc[0] == pytest.approx(100.0)


def test_deflate_zero_cpi_is_nan():
    out = b.deflate(pd.Series([100.0]), pd.Series([0.0]))
    assert np.isnan(out.iloc[0])


# --------------------------------------------------------------------------- integration (tiny)
def test_build_derived_on_synthetic_building_blocks():
    """_build_derived on a 2-row synthetic building-block frame (no warehouse)."""
    cols = {}
    for c in b.CF_CODES:
        cols[f"cf_{c}"] = [np.nan, np.nan]
    for c in b.RCON_ONLY:
        cols[f"rcon_{c}"] = [np.nan, np.nan]
    for c in b.RCFN_ONLY:
        cols[f"rcfn_{c}"] = [np.nan, np.nan]
    for c in b.RIAD_CODES:
        cols[f"riad_{c}"] = [np.nan, np.nan]
    bb = pd.DataFrame(cols)
    bb.insert(0, "period_end", pd.to_datetime(["2008-12-31", "2020-12-31"]))
    bb.insert(0, "rssd_id", [111, 222])
    # populate a coherent post-1994 large-bank-ish row 0
    bb.loc[0, "cf_2170"] = 1000.0   # assets
    bb.loc[0, "cf_2200"] = 600.0    # deposits
    bb.loc[0, "cf_3210"] = 90.0     # equity
    bb.loc[0, "cf_2122"] = 500.0    # ln_tot
    bb.loc[0, "cf_1754"] = 100.0    # securities HTM
    bb.loc[0, "cf_1773"] = 50.0     # securities AFS
    bb.loc[0, "cf_3839"] = 40.0     # surplus (post-1990 arm)
    bb.loc[0, "cf_2604"] = 120.0    # time dep component
    bb.loc[0, "cf_6648"] = 30.0
    bb.loc[0, "cf_0010"] = 70.0     # cash

    out = b._build_derived(bb)
    r0 = out.iloc[0]
    assert r0["assets"] == 1000.0
    assert r0["securities"] == 150.0                 # 100+50 (post-1994 arm)
    assert r0["surplus"] == 40.0                     # post-1990 arm -> 3839
    assert r0["time_deposits"] == 150.0              # 2008 -> 2604+6648
    assert r0["cash"] == 70.0                        # cf_0010 present
    assert r0["leverage"] == pytest.approx(0.09)     # 90/1000
    assert r0["loan_ratio"] == pytest.approx(0.5)    # 500/1000
    assert r0["deposit_ratio"] == pytest.approx(0.6) # 600/1000
    assert r0["crisisBVX"] == 0                       # 2008 not a crisis year
    assert r0["era"] == "MODC"


def test_built_and_gapped_cover_scoped_modc():
    """Map-driven coverage: no scoped MODC variable is silently omitted."""
    cov = b._coverage_report()
    assert cov["uncovered_variables"] == [], cov["uncovered_variables"]


# ------------------------------------------------- SPEC §10 modern-era remediation arms
def _bb_row(period, **codes):
    """One building-block row (all codes NaN except the named cf_* ones)."""
    cols = {}
    for c in b.CF_CODES:
        cols[f"cf_{c}"] = [np.nan]
    for c in b.RCON_ONLY:
        cols[f"rcon_{c}"] = [np.nan]
    for c in b.RCFN_ONLY:
        cols[f"rcfn_{c}"] = [np.nan]
    for c in b.RIAD_CODES:
        cols[f"riad_{c}"] = [np.nan]
    bb = pd.DataFrame(cols)
    bb.insert(0, "period_end", pd.to_datetime([period]))
    bb.insert(0, "rssd_id", [1])
    for k, v in codes.items():
        bb.loc[0, k] = v
    return bb


def test_ffpurch_era_split_pure_arms():
    # §10.1: pre-1997 cf(0278); 1997Q1-2001Q4 NULL (no pure arm); 2002+ cf(B993).
    assert b._build_derived(_bb_row("1994-12-31", cf_0278=42.0)).iloc[0]["ffpurch"] == 42.0
    assert np.isnan(b._build_derived(_bb_row("1999-06-30", cf_0278=1.0, cf_B993=2.0)).iloc[0]["ffpurch"])
    assert b._build_derived(_bb_row("2010-12-31", cf_B993=77.0)).iloc[0]["ffpurch"] == 77.0
    # ffsold symmetric: 2002+ cf(B987)
    assert b._build_derived(_bb_row("2010-12-31", cf_B987=55.0)).iloc[0]["ffsold"] == 55.0


def test_otherbor_liab_pre1994_arm():
    # §10.2: pre-1994 rowtotal(2850,2910) (NaN iff both null); 1994+ cf(3190) unchanged.
    r = b._build_derived(_bb_row("1985-06-30", cf_2850=100.0, cf_2910=25.0)).iloc[0]
    assert r["otherbor_liab"] == 125.0
    # only one component present -> rowtotal keeps coverage (treats missing as 0)
    assert b._build_derived(_bb_row("1985-06-30", cf_2850=100.0)).iloc[0]["otherbor_liab"] == 100.0
    # 1994+ still uses 3190 (pre-1994 arm not applied)
    assert b._build_derived(_bb_row("2005-03-31", cf_3190=300.0)).iloc[0]["otherbor_liab"] == 300.0


def test_ln_cons_post2011_successor_arm():
    # §10.3: through 2011Q4 cf(1975); 2012Q1+ rowtotal(B538,B539,K137,K207).
    assert b._build_derived(_bb_row("2011-12-31", cf_1975=900.0)).iloc[0]["ln_cons"] == 900.0
    r = b._build_derived(_bb_row("2015-06-30", cf_B538=10.0, cf_B539=20.0, cf_K137=30.0, cf_K207=40.0)).iloc[0]
    assert r["ln_cons"] == 100.0
    # post-2011 cf(1975) is ignored (retired); the successor is authoritative
    assert np.isnan(b._build_derived(_bb_row("2015-06-30", cf_1975=999.0)).iloc[0]["ln_cons"])
