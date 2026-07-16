"""Fixture-based tests for the finhist-equivalent procedural core (no warehouse, no .dta).

Every reconstructed aggregate / override / ratio / deflation function is tested against a
hand-computed expectation on a tiny synthetic frame that exercises the era windows and the
Stata ``egen rowtotal`` missing semantics. These prove the DERIVATION is faithful to
``04``/``07``; the .dta read and parquet write are integration-only (exercised by main()).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.reconstruction import build_finhist_equivalent as bf


# --------------------------------------------------------------------------- rowtotal
def test_rowtotal_missing_as_zero_and_all_na_zero_by_default():
    df = pd.DataFrame({"a": [1.0, np.nan, np.nan], "b": [2.0, 5.0, np.nan]})
    out = bf.rowtotal(df, ["a", "b"])
    assert out.tolist() == [3.0, 5.0, 0.0]          # all-NA -> 0 (bare egen rowtotal)


def test_rowtotal_missing_if_all_na_flag():
    df = pd.DataFrame({"a": [1.0, np.nan], "b": [2.0, np.nan]})
    out = bf.rowtotal(df, ["a", "b"], missing_if_all_na=True)
    assert out.iloc[0] == 3.0
    assert np.isnan(out.iloc[1])                     # all-NA -> missing


def test_rowtotal_absent_column_contributes_zero_not_error():
    df = pd.DataFrame({"a": [4.0, 1.0]})
    out = bf.rowtotal(df, ["a", "does_not_exist"])
    assert out.tolist() == [4.0, 1.0]


# --------------------------------------------------------------------------- interbank (04 L68)
def test_interbank_rowtotal_no_missing_mask():
    df = pd.DataFrame({c: [1.0] for c in bf.INTERBANK_COLS})
    assert bf.reconstruct_interbank(df).iloc[0] == float(len(bf.INTERBANK_COLS))
    empty = pd.DataFrame({c: [np.nan] for c in bf.INTERBANK_COLS})
    assert bf.reconstruct_interbank(empty).iloc[0] == 0.0   # 04 L68 has no missing mask


# --------------------------------------------------------------------------- liquid (04 L72-82)
def test_liquid_override_window_1905_1935():
    base = {c: 0.0 for c in bf.LIQUID_COLS}
    base.update({"bills_nb": 10.0})                 # base rowtotal = 10
    base.update({"cash_and_exchange": 3.0, "frb_reserve": 4.0, "cash_exchange_and_reserve": 5.0})
    df = pd.DataFrame([{**base, "year": 1900}, {**base, "year": 1910}, {**base, "year": 1940}])
    out = bf.reconstruct_liquid(df, df["year"])
    # 1900 & 1940 -> base (cash_and_exchange 3 + cash_exchange_and_reserve 5 + bills_nb 10 = 18)
    assert out.iloc[0] == 18.0
    assert out.iloc[2] == 18.0
    # 1910 -> override = 3+4+5 = 12
    assert out.iloc[1] == 12.0


def test_liquid_missing_iff_all_components_missing():
    row = {c: np.nan for c in set(bf.LIQUID_COLS) | set(bf.LIQUID_OVERRIDE_COLS)}
    df = pd.DataFrame([{**row, "year": 1900}])
    assert np.isnan(bf.reconstruct_liquid(df, df["year"]).iloc[0])


# --------------------------------------------------------------------------- equity (04 L84-85)
def test_equity_unconditional_rowtotal_vs_freenic_guard():
    # overlap-year style row: both split items present AND the combined item present.
    df = pd.DataFrame([{
        "capital": 100.0, "surplus": 20.0, "undivided_profits": 5.0,
        "surplus_and_undivided_profits": 25.0,
    }])
    # CLV unconditional: 100+20+5+25 = 150 (double-counts the combined item)
    assert bf.reconstruct_equity(df).iloc[0] == 150.0
    # freeNIC guard: adds combined only when both split are NULL -> here 100+20+5 = 125
    assert bf.reconstruct_equity_freenic_guard(df).iloc[0] == 125.0


def test_equity_clean_year_both_methods_agree():
    df = pd.DataFrame([{
        "capital": 100.0, "surplus": 20.0, "undivided_profits": 5.0,
        "surplus_and_undivided_profits": np.nan,
    }])
    assert bf.reconstruct_equity(df).iloc[0] == 125.0
    assert bf.reconstruct_equity_freenic_guard(df).iloc[0] == 125.0


def test_equity_missing_iff_all_four_missing():
    df = pd.DataFrame([{c: np.nan for c in bf.EQUITY_COLS}])
    assert np.isnan(bf.reconstruct_equity(df).iloc[0])
    assert np.isnan(bf.reconstruct_equity_freenic_guard(df).iloc[0])


# --------------------------------------------------------------------------- surplus_profit (04 L87-90)
def test_surplus_profit_era_replacement():
    df = pd.DataFrame([
        {"surplus": 3.0, "undivided_profits": 4.0, "surplus_and_undivided_profits": 99.0, "year": 1900},
        {"surplus": 3.0, "undivided_profits": 4.0, "surplus_and_undivided_profits": 99.0, "year": 1920},
        {"surplus": 3.0, "undivided_profits": 4.0, "surplus_and_undivided_profits": 99.0, "year": 1906},
    ])
    out = bf.reconstruct_surplus_profit(df, df["year"])
    assert out.iloc[0] == 7.0     # 1900: rowtotal
    assert out.iloc[1] == 99.0    # 1920 in [1918,1928] -> combined item
    assert out.iloc[2] == 99.0    # 1906 in [1905,1907] -> combined item


# --------------------------------------------------------------------------- total_deposits + override
def test_total_deposits_uses_raw_deposits_no_mask():
    df = pd.DataFrame([{"us_deposits": 1.0, "usdo_deposits": 2.0, "individual_deposits": 3.0,
                        "demand_deposits": 4.0, "time_deposits": 5.0, "deposits": 6.0}])
    assert bf.reconstruct_total_deposits(df).iloc[0] == 21.0


def test_override_deposits_windows():
    df = pd.DataFrame([
        {"deposits": 500.0, "demand_deposits": 10.0, "time_deposits": 20.0, "individual_deposits": 99.0, "year": 1890},
        {"deposits": 500.0, "demand_deposits": 10.0, "time_deposits": 20.0, "individual_deposits": 99.0, "year": 1920},
        {"deposits": 500.0, "demand_deposits": 10.0, "time_deposits": 20.0, "individual_deposits": 99.0, "year": 1910},
        {"deposits": 500.0, "demand_deposits": np.nan, "time_deposits": np.nan, "individual_deposits": 99.0, "year": 1920},
    ])
    out = bf.override_deposits(df, df["year"])
    assert out.iloc[0] == 500.0   # <1905 -> raw
    assert out.iloc[1] == 30.0    # 1915-28 -> demand+time
    assert out.iloc[2] == 99.0    # 1905-14 -> individual_deposits
    assert np.isnan(out.iloc[3])  # 1915-28 both components missing -> missing


def test_override_deposits_zero_in_window_becomes_missing():
    df = pd.DataFrame([{"deposits": 500.0, "demand_deposits": 0.0, "time_deposits": 0.0,
                        "individual_deposits": 1.0, "year": 1920}])
    # demand+time both present (0) -> sum 0 -> then blanked (04 L103)
    assert np.isnan(bf.override_deposits(df, df["year"]).iloc[0])


# --------------------------------------------------------------------------- bonds_circ (04 L111-112)
def test_bonds_circ_approximation_chain():
    df = pd.DataFrame([
        {"bonds_circ": 7.0, "lawful_money": 1.0, "securities_usgov": 2.0},   # keep raw
        {"bonds_circ": np.nan, "lawful_money": 1.0, "securities_usgov": 2.0},  # -> lawful_money
        {"bonds_circ": np.nan, "lawful_money": np.nan, "securities_usgov": 2.0},  # -> securities_usgov
    ])
    out = bf.approximate_bonds_circ(df)
    assert out.tolist() == [7.0, 1.0, 2.0]


# --------------------------------------------------------------------------- res_funding (04 L116-122)
def test_res_funding_floor_and_mask():
    df = pd.DataFrame([
        {"assets": 1000.0, "capital": 100.0, "deposits": 50.0, "notes_nb": 10.0},   # positive residual
        {"assets": 100.0, "capital": 100.0, "deposits": 50.0, "notes_nb": 10.0},    # negative -> floored 0
    ])
    equity = pd.Series([200.0, 200.0])
    total_deposits = pd.Series([300.0, 300.0])
    interbank = pd.Series([50.0, 50.0])
    out = bf.reconstruct_res_funding(df, equity, total_deposits, interbank)
    # row0: 1000 - (200+300+50+10) = 440
    assert out.iloc[0] == 440.0
    # row1: 100 - 560 = -460 -> floored to 0
    assert out.iloc[1] == 0.0


def test_res_funding_missing_when_mask_components_all_na():
    df = pd.DataFrame([{"assets": 1000.0, "capital": np.nan, "deposits": np.nan, "notes_nb": np.nan}])
    equity = pd.Series([np.nan]); total_deposits = pd.Series([np.nan])
    interbank = pd.Series([np.nan])
    out = bf.reconstruct_res_funding(df, equity, total_deposits, interbank)
    assert np.isnan(out.iloc[0])   # capital&notes_nb&deposits&interbank all NA -> cdn NA -> res NA


# --------------------------------------------------------------------------- crisis / ratios / deflate
def test_crisis_bvx():
    out = bf.crisis_bvx(pd.Series([1873, 1900, 1907, 1930, 1941]))
    assert out.tolist() == [1, 0, 1, 1, 0]


def test_hist_ratios_validity_filter_blanks_out_of_range():
    panel = pd.DataFrame([{
        "assets": 100.0, "equity": 250.0, "capital": 10.0, "surplus_profit": 5.0,
        "undivided_profits": 1.0, "oreo": 2.0, "loans": 48.0, "deposits": 60.0,
        "total_deposits": 70.0, "res_funding": 20.0, "emergency": 3.0, "interbank": 4.0,
        "time_deposits": 5.0, "demand_deposits": 6.0, "liquid": 30.0, "year": 1900,
    }])
    out = bf.hist_ratios(panel)
    # leverage = 250/100 = 2.5 > 1 -> blanked by validity filter (07 L143-147)
    assert np.isnan(out["leverage"].iloc[0])
    # loan_ratio = 48/100 = 0.48 -> kept (loan_ratio NOT in the validity list, and in-range anyway)
    assert out["loan_ratio"].iloc[0] == pytest.approx(0.48)
    # emergency_borrowing kept at 1900 (only blanked 1905-1928)
    assert out["emergency_borrowing"].iloc[0] == pytest.approx(0.03)


def test_hist_ratios_deflation_invariance_property():
    # ratio of two levels == ratio after dividing both by the same cpi_gfd.
    panel = pd.DataFrame([{"assets": 200.0, "equity": 50.0, "capital": 10.0,
                           "surplus_profit": 5.0, "undivided_profits": 2.0, "oreo": 1.0,
                           "loans": 80.0, "deposits": 90.0, "total_deposits": 95.0,
                           "res_funding": 20.0, "emergency": 3.0, "interbank": 4.0,
                           "time_deposits": 10.0, "demand_deposits": 12.0, "liquid": 40.0,
                           "year": 1899}])
    out = bf.hist_ratios(panel)
    assert out["leverage"].iloc[0] == pytest.approx(50.0 / 200.0)
    assert out["deposit_ratio"].iloc[0] == pytest.approx(90.0 / 200.0)


def test_emergency_borrowing_blanked_1905_1928():
    panel = pd.DataFrame([
        {"assets": 100.0, "emergency": 5.0, "equity": 1.0, "capital": 1.0, "surplus_profit": 1.0,
         "undivided_profits": 1.0, "oreo": 1.0, "loans": 1.0, "deposits": 1.0, "total_deposits": 1.0,
         "res_funding": 1.0, "interbank": 1.0, "time_deposits": 1.0, "demand_deposits": 1.0,
         "liquid": 1.0, "year": 1910},
    ])
    out = bf.hist_ratios(panel)
    assert np.isnan(out["emergency_borrowing"].iloc[0])   # 07 L97


def test_deflate_divides_by_cpi_gfd_and_handles_missing_year():
    panel = pd.DataFrame({"year": pd.array([1929, 1800], dtype="Int64"),
                          "assets": [1720.0, 100.0], "loans": [860.0, 50.0]})
    cpi = pd.DataFrame({"year": pd.array([1929], dtype="Int64"), "cpi_gfd": [17.2]})
    out = bf.deflate(panel, cpi, ["assets", "loans"])
    assert out["assets_real"].iloc[0] == pytest.approx(1720.0 / 17.2)
    assert np.isnan(out["assets_real"].iloc[1])   # 1800 not in cpi -> honest NaN


def test_deflate_zero_cpi_is_nan_not_inf():
    panel = pd.DataFrame({"year": pd.array([1900], dtype="Int64"), "assets": [100.0]})
    cpi = pd.DataFrame({"year": pd.array([1900], dtype="Int64"), "cpi_gfd": [0.0]})
    out = bf.deflate(panel, cpi, ["assets"])
    assert np.isnan(out["assets_real"].iloc[0])
