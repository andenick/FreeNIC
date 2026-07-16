"""Fixture-based tests for the Luck-core (MODL 1959-75) procedural core.

Every reconstructed field / ratio / deflation / failure function is tested against a
hand-computed expectation on a tiny synthetic frame that exercises the Stata semantics
(``egen rowtotal`` missing, tq index, qofd, ×1000+deflate, Q4 income gate, clips, validity
filter). These prove the DERIVATION is faithful to ``05``/``06``/``07``; the .dta read,
FDIC merge, parquet write, and warehouse smoke are integration-only (exercised by main()).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.reconstruction import build_luck_core as bl


# --------------------------------------------------------------------------- liquid (05 L108)
def test_liquid_rowtotal_ffpurch_missing_is_cash_plus_securities():
    df = pd.DataFrame({"cash": [10.0, np.nan], "securities": [5.0, 7.0], "ffpurch": [np.nan, np.nan]})
    out = bl.compute_liquid(df)
    assert out.iloc[0] == 15.0          # 10 + 5 + 0(ffpurch NaN)
    assert out.iloc[1] == 7.0           # NaN + 7 + 0


def test_liquid_missing_iff_all_three_missing():
    df = pd.DataFrame({"cash": [np.nan], "securities": [np.nan], "ffpurch": [np.nan]})
    assert np.isnan(bl.compute_liquid(df).iloc[0])


# --------------------------------------------------------------------------- quarter/date math
def test_quarter_stata_index():
    yr = pd.Series([1960, 1959, 1970, 1975])
    qn = pd.Series([1, 4, 4, 4])
    out = bl.quarter_stata_index(yr, qn)
    assert out.tolist() == [0, -1, 43, 63]      # 1960q1=0; 1959q4=-1; 1970q4=(10*4)+3=43; 1975q4=63


def test_quarter_end_timestamp_last_day_of_quarter():
    out = bl.quarter_end_timestamp(pd.Series([1970, 1970, 1972]), pd.Series([4, 2, 1]))
    assert out.iloc[0] == pd.Timestamp("1970-12-31")
    assert out.iloc[1] == pd.Timestamp("1970-06-30")
    assert out.iloc[2] == pd.Timestamp("1972-03-31")   # leap-year Q1 still ends 03-31


def test_qofd_quarter_index():
    ts = pd.Series(pd.to_datetime(["1960-01-15", "1970-12-31", "1985-05-01"]))
    assert bl.qofd_quarter_index(ts).tolist() == [0, 43, 101]  # 1985q2 = (25*4)+1 = 101


# --------------------------------------------------------------------------- age (05 L125-129)
def test_charter_year_from_dt_open_and_age():
    dt = pd.Series([19040901, 19551231, 0, 18630101])
    cy = bl.charter_year_from_dt_open(dt)
    assert cy.tolist()[:2] == [1904, 1955]
    assert pd.isna(cy.iloc[2])                          # 0 -> implausible -> NA
    age = bl.compute_age(pd.Series([1970, 1970, 1970, 1970]), cy)
    assert age.tolist()[:2] == [66, 15]
    assert pd.isna(age.iloc[2])


# --------------------------------------------------------------------------- deflation (05 L111-115 + 07 L26-34)
def test_deflate_x1000_then_divide_cpi():
    panel = pd.DataFrame({"year": pd.array([1970, 1975], dtype="Int64"),
                          "assets": [100.0, 200.0]})       # thousands
    cpi = pd.DataFrame({"year": pd.array([1970, 1975], dtype="Int64"), "cpi_gfd": [39.8, 55.5]})
    out = bl.deflate(panel, cpi, ["assets"])
    # real = thousands * 1000 / cpi_gfd (CLV dollar scale)
    assert out["assets_real"].iloc[0] == pytest.approx(100.0 * 1000 / 39.8)
    assert out["assets_real"].iloc[1] == pytest.approx(200.0 * 1000 / 55.5)


def test_deflate_missing_year_and_zero_cpi_are_nan():
    panel = pd.DataFrame({"year": pd.array([1970, 1800], dtype="Int64"), "assets": [100.0, 5.0]})
    cpi = pd.DataFrame({"year": pd.array([1970], dtype="Int64"), "cpi_gfd": [0.0]})
    out = bl.deflate(panel, cpi, ["assets"])
    assert np.isnan(out["assets_real"].iloc[0])           # cpi 0 -> NaN not inf
    assert np.isnan(out["assets_real"].iloc[1])           # 1800 absent -> NaN


# --------------------------------------------------------------------------- crisisBVX (07 L52-55)
def test_crisis_bvx_zero_across_modl():
    assert bl.crisis_bvx(pd.Series([1959, 1965, 1970, 1975])).tolist() == [0, 0, 0, 0]
    assert bl.crisis_bvx(pd.Series([1907, 1984])).tolist() == [1, 1]


# --------------------------------------------------------------------------- ratios (07)
def _ratio_frame(**over) -> pd.DataFrame:
    base = dict(assets=100.0, equity=8.0, deposits=85.0, loans=np.nan, liquid=30.0,
                deposits_time=40.0, deposits_demand=20.0, otherbor_liab=5.0,
                ytdnetinc=2.0, ytdint_inc_ln=6.0, ytdint_exp_dep=3.0, ytdllprov=1.0,
                npl_tot=np.nan, brokered_dep=np.nan, insured_deposits=np.nan,
                ln_cons=1.0, ln_cc=1.0, ln_ci=1.0, ln_oth=1.0, ln_fi=1.0, ln_re=1.0,
                quarter_number=4, year=1970, assets_real=100000.0, age=20.0)
    base.update(over)
    return pd.DataFrame([base])


def test_ratios_core_and_noncore_and_liquid():
    out = bl.modern_ratios(_ratio_frame())
    assert out["leverage"].iloc[0] == pytest.approx(8.0 / 100.0)
    assert out["deposit_ratio"].iloc[0] == pytest.approx(85.0 / 100.0)
    assert out["liquid_ratio"].iloc[0] == pytest.approx(30.0 / 100.0)
    # noncore_funding = deposits_time + otherbor_liab = 45 -> /assets
    assert out["noncore_ratio"].iloc[0] == pytest.approx(45.0 / 100.0)
    assert out["time_ratio"].iloc[0] == pytest.approx(40.0 / 100.0)


def test_ratios_loans_absent_makes_loan_ratios_na():
    out = bl.modern_ratios(_ratio_frame())              # loans is NaN
    for col in ("loan_ratio", "npl_ratio", "prov_ratio",
                "ln_cons_ratio", "ln_ci_ratio", "ln_re_ratio"):
        assert np.isnan(out[col].iloc[0]), col


def test_income_ratios_q4_gate_and_clip():
    q2 = bl.modern_ratios(_ratio_frame(quarter_number=2))
    assert np.isnan(q2["income_ratio"].iloc[0])          # non-Q4 -> NA (07 L120-122)
    assert np.isnan(q2["int_inc_ratio"].iloc[0])
    # nim = (6-3)/100 = 0.03 (nim is NOT Q4-gated in 07); clip keeps it
    assert q2["nim"].iloc[0] == pytest.approx(0.03)
    # clip: huge income -> 0.5
    big = bl.modern_ratios(_ratio_frame(ytdnetinc=999.0))
    assert big["income_ratio"].iloc[0] == 0.5            # clip(-0.5,0.5) (07 L138)


def test_validity_filter_blanks_out_of_range_leverage():
    out = bl.modern_ratios(_ratio_frame(equity=250.0))   # leverage = 2.5 > 1
    assert np.isnan(out["leverage"].iloc[0])             # 07 L143-147
    # negative equity -> leverage < 0 -> blanked too
    neg = bl.modern_ratios(_ratio_frame(equity=-5.0))
    assert np.isnan(neg["leverage"].iloc[0])


def test_size_uses_deflated_assets():
    out = bl.modern_ratios(_ratio_frame(assets_real=100000.0))
    assert out["size"].iloc[0] == pytest.approx(np.log(100000.0))
    assert out["log_age"].iloc[0] == pytest.approx(np.log(20.0))


# --------------------------------------------------------------------------- within-year quartile (07 L49)
def test_within_year_quartile_bins():
    vals = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    yr = pd.Series([1970] * 8)
    out = bl._within_year_quartile(vals, yr)
    assert out.min() == 1 and out.max() == 4
    assert out.iloc[0] == 1 and out.iloc[-1] == 4


# --------------------------------------------------------------------------- FDIC fail-dates reshape (05 L11-42)
def test_build_fdic_fail_dates_reshape_and_exclusions():
    pbd = pd.DataFrame({
        # a genuinely MISSING cert (NaN) with rssd 55 -> -id_rssd surrogate (05 L15, mi() only)
        "id_fdic_cert": [100.0, 100.0, 200.0, np.nan, 300.0, 400.0],
        "id_rssd":      [11.0,  11.0,  22.0,  55.0,   33.0,  44.0],
        "fail_day": pd.to_datetime(["1988-02-01", "1991-05-01", "1985-03-01",
                                    "1990-01-01", "1989-01-01", "1987-01-01"]),
        "restype1": ["", "", "", "", "OBAM", ""],           # 300 excluded (TARP)
        "chclass1": ["NM", "NM", "NM", "NM", "NM", "SL"],   # 400 excluded (thrift)
    })
    ftdb = pd.DataFrame({"id_fdic_cert": [100.0, 200.0], "fail_day": pd.to_datetime(["1988-02-01", "1985-03-01"]),
                         "resdep": [9.0, 8.0], "resasset": [90.0, 80.0]})
    out = bl.build_fdic_fail_dates(pbd, ftdb)
    row100 = out[out["id_fdic_cert"] == 100.0].iloc[0]
    assert row100["fail_day"] == pd.Timestamp("1988-02-01")     # first failure
    assert row100["fail_day2"] == pd.Timestamp("1991-05-01")    # second -> wide col
    assert row100["resdep"] == 9.0
    # zero-cert row (rssd 55) -> negative surrogate -55 present
    assert (-55.0) in set(out["id_fdic_cert"])
    # OBAM (300) and thrift (400) excluded
    assert 300.0 not in set(out["id_fdic_cert"])
    assert 400.0 not in set(out["id_fdic_cert"])
