"""Tests for the reconstruction validation harness (plan §B2, RECONSTRUCTION_SPEC.md §7).

Synthetic fixtures only — the real builder outputs are NOT consumed this batch. The
fixtures prove the correctness-critical guarantees the campaign pins:

  * arithmetic class boundaries (EXACT / ROUNDING at 0.5 ULP / TOLERANCE at 1e-4);
  * an UNEXPLAINED divergence with no registered reason lands UNEXPLAINED, never VINTAGE;
  * a pre-registered reason key moves a non-arithmetic divergence to its documented class;
  * gate math: a fixture that PASSES 99.5% and one that FAILS;
  * alignment-key mismatches are counted as coverage gaps (UNEXPLAINED), not matches;
  * the ULP derivation matches taxonomy.classify's arithmetic contract;
  * deterministic output ordering; combined-report mode.

All artifacts land in a pytest tmp dir. No warehouse, no network.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from pipeline.reconstruction import taxonomy as tx
from pipeline.reconstruction import validate_reconstruction as vr


# =========================================================== ULP derivation
def test_units_last_digit_integer_valued_is_one():
    assert vr.units_last_digit(1_750_000.0) == 1.0     # integer magnitude, trailing zeros
    assert vr.units_last_digit(5.0) == 1.0
    assert vr.units_last_digit(0.0) == 1.0
    assert vr.units_last_digit(-42.0) == 1.0


def test_units_last_digit_fractional():
    assert vr.units_last_digit(1.23) == pytest.approx(0.01)
    assert vr.units_last_digit(100.5) == pytest.approx(0.1)
    assert vr.units_last_digit(0.001) == pytest.approx(0.001)


def test_units_last_digit_missing_defaults_one():
    assert vr.units_last_digit(None) == 1.0
    assert vr.units_last_digit(float("nan")) == 1.0


# =========================================================== registry loading
def test_shipped_reasons_load_and_validate():
    r = vr.load_reasons()  # shipped copy
    # the three seed cases the task names must be present
    ids = set(r["reason_id"])
    assert {"MC_LIQUID_FFPURCH", "ND_SECURITIES_PRE1994", "VINTAGE_TIMEDEP_PRE1994"} <= ids
    # every registry klass is a documented (non-arithmetic) class
    assert set(r["klass"]) <= set(tx.REGISTERED_CLASSES)


def test_shipped_reasons_byte_identical_to_spec_copy():
    a = vr.SHIPPED_REASONS.read_bytes()
    b = vr.SPEC_REASONS.read_bytes()
    assert a == b, "shipped divergence_reasons.csv must equal the spec-dir canonical copy"


def test_validate_reasons_rejects_arithmetic_klass(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "reason_id,variable,era,klass,period_start,period_end,reason,cite,predicate\n"
        "X1,assets,1976_2026,EXACT,,,not a documented class,cite,\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="klass must be"):
        vr.load_reasons(bad)


def test_validate_reasons_rejects_duplicate_id(tmp_path):
    bad = tmp_path / "dup.csv"
    bad.write_text(
        "reason_id,variable,era,klass,period_start,period_end,reason,cite,predicate\n"
        "D1,assets,1976_2026,VINTAGE,,,a,c,\n"
        "D1,equity,finhist,METHOD-CHOICE,,,b,c,\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate reason_id"):
        vr.load_reasons(bad)


# =========================================================== reason matching
def test_match_reason_period_window_pre1994():
    reasons = vr.load_reasons()
    era_r = vr.reasons_for_era(reasons, "1976_2026")
    # securities pre-1994 -> NOT-DERIVABLE (period_end bound 1994-01-01, exclusive upper)
    klass, rid = vr.match_reason(era_r, "securities", pd.Timestamp("1990-12-31"), "1976_2026")
    assert klass == tx.NOT_DERIVABLE and rid == "ND_SECURITIES_PRE1994"
    # securities in 1994+ has no registered reason -> no documented class
    klass2, rid2 = vr.match_reason(era_r, "securities", pd.Timestamp("2000-12-31"), "1976_2026")
    assert klass2 is None and rid2 is None


def test_match_reason_unbounded_method_choice():
    reasons = vr.load_reasons()
    era_r = vr.reasons_for_era(reasons, "1976_2026")
    klass, rid = vr.match_reason(era_r, "liquid", pd.Timestamp("2005-12-31"), "1976_2026")
    assert klass == tx.METHOD_CHOICE and rid == "MC_LIQUID_FFPURCH"


def test_match_reason_combined_era_row_applies_to_finhist():
    reasons = vr.load_reasons()
    era_r = vr.reasons_for_era(reasons, "finhist")
    # cpi_deflator registered with era='combined' -> applies to finhist too
    klass, rid = vr.match_reason(era_r, "cpi_deflator", 1900, "finhist")
    assert klass == tx.METHOD_CHOICE and rid == "MC_CPI_BASE"


# =========================================================== helpers for panels
def _modc_panel(rows, cols):
    """Build a modern (id_rssd, period_end) panel DataFrame from row dicts."""
    df = pd.DataFrame(rows)
    df["id_rssd"] = df["id_rssd"].astype("Int64")
    df["period_end"] = pd.to_datetime(df["period_end"])
    return df[["id_rssd", "period_end"] + cols]


# =========================================================== end-to-end: classes
def test_arithmetic_boundaries_end_to_end(tmp_path):
    # assets scoped var; craft EXACT, ROUNDING(0.5 ULP), TOLERANCE(1e-4), UNEXPLAINED cells.
    pub = _modc_panel([
        {"id_rssd": 1, "period_end": "2000-12-31", "assets": 100.0},        # EXACT
        {"id_rssd": 2, "period_end": "2000-12-31", "assets": 100.0},        # ROUNDING (+0.5)
        {"id_rssd": 3, "period_end": "2000-12-31", "assets": 1_000_000.0},  # TOLERANCE (+100 == 1e-4)
        {"id_rssd": 4, "period_end": "2000-12-31", "assets": 100.0},        # UNEXPLAINED
    ], ["assets"])
    blt = _modc_panel([
        {"id_rssd": 1, "period_end": "2000-12-31", "assets": 100.0},
        {"id_rssd": 2, "period_end": "2000-12-31", "assets": 100.5},
        {"id_rssd": 3, "period_end": "2000-12-31", "assets": 1_000_100.0},
        {"id_rssd": 4, "period_end": "2000-12-31", "assets": 250.0},
    ], ["assets"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "pub", pub), _w(tmp_path, "blt", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    by_rssd = dict(zip(recon["id_rssd"].astype(int), recon["class"]))
    assert by_rssd[1] == tx.EXACT
    assert by_rssd[2] == tx.ROUNDING
    assert by_rssd[3] == tx.TOLERANCE
    assert by_rssd[4] == tx.UNEXPLAINED
    # 3 matched of 4 derivable -> 75% -> FAIL the 99.5% gate; 25% unexplained > floor
    assert gate["matched_cells"] == 3
    assert gate["verdict"] == "FAIL"


def test_unregistered_nonarithmetic_divergence_is_unexplained_not_vintage(tmp_path):
    # securities in 2000 (post-1994, no registered reason) with a large divergence.
    # It must be UNEXPLAINED, NEVER silently VINTAGE/NOT-DERIVABLE.
    pub = _modc_panel([{"id_rssd": 9, "period_end": "2000-12-31", "securities": 500.0}], ["securities"])
    blt = _modc_panel([{"id_rssd": 9, "period_end": "2000-12-31", "securities": 900.0}], ["securities"])
    vr.run_era("1976_2026", _w(tmp_path, "pub", pub), _w(tmp_path, "blt", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    assert recon.loc[0, "class"] == tx.UNEXPLAINED
    assert recon.loc[0, "reason_id"] == ""


def test_registered_reason_moves_divergence_to_documented_class(tmp_path):
    # Same securities divergence but PRE-1994 -> pre-registered NOT-DERIVABLE (excluded from gate);
    # a pre-1994 time_deposits divergence -> pre-registered VINTAGE.
    pub = _modc_panel([
        {"id_rssd": 9, "period_end": "1990-12-31", "securities": 500.0, "time_deposits": 50.0},
    ], ["securities", "time_deposits"])
    blt = _modc_panel([
        {"id_rssd": 9, "period_end": "1990-12-31", "securities": 900.0, "time_deposits": 80.0},
    ], ["securities", "time_deposits"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "pub", pub), _w(tmp_path, "blt", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet").set_index("variable")
    assert recon.loc["securities", "class"] == tx.NOT_DERIVABLE
    assert recon.loc["securities", "reason_id"] == "ND_SECURITIES_PRE1994"
    assert recon.loc["time_deposits", "class"] == tx.VINTAGE
    assert recon.loc["time_deposits", "reason_id"] == "VINTAGE_TIMEDEP_PRE1994"
    # NOT-DERIVABLE excluded from denominator: derivable = 1 (only time_deposits VINTAGE),
    # matched = 0 -> FAIL, but not_derivable is not counted against the denominator.
    assert gate["not_derivable_cells"] == 1
    assert gate["derivable_cells"] == 1


def test_registered_reason_does_not_override_arithmetic_match(tmp_path):
    # SPEC §7 first-match precedence: a pre-1994 securities cell that MATCHES exactly is EXACT,
    # NOT NOT-DERIVABLE (the arithmetic match wins over the registered documented class).
    pub = _modc_panel([{"id_rssd": 9, "period_end": "1990-12-31", "securities": 500.0}], ["securities"])
    blt = _modc_panel([{"id_rssd": 9, "period_end": "1990-12-31", "securities": 500.0}], ["securities"])
    vr.run_era("1976_2026", _w(tmp_path, "pub", pub), _w(tmp_path, "blt", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    assert recon.loc[0, "class"] == tx.EXACT
    assert recon.loc[0, "reason_id"] == ""


# =========================================================== gate math
def test_gate_passes_at_995(tmp_path):
    # 199 EXACT + 1 TOLERANCE-miss-that-is-unexplained? No: build 200 cells, 199 exact,
    # 1 ROUNDING -> matched 200/200 = 100% pass. Then a 1000-cell case at exactly 99.5%.
    rows_pub, rows_blt = [], []
    for i in range(1000):
        rows_pub.append({"id_rssd": i, "period_end": "2000-12-31", "assets": 1000.0})
        # 995 EXACT, 5 divergent-but-registered? No — to pass we need matched>=99.5% AND
        # unexplained<=0.1%. Make 999 EXACT + 1 registered METHOD-CHOICE (liquid) so
        # unexplained=0. Use assets EXACT for 999, and 1 UNEXPLAINED would break floor.
        rows_blt.append({"id_rssd": i, "period_end": "2000-12-31", "assets": 1000.0})
    pub = _modc_panel(rows_pub, ["assets"])
    blt = _modc_panel(rows_blt, ["assets"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "pubp", pub), _w(tmp_path, "bltp", blt), tmp_path)
    assert gate["match_share"] == 1.0
    assert gate["verdict"] == "PASS"


def test_gate_fails_just_below_threshold(tmp_path):
    # 1000 cells: 994 EXACT + 6 UNEXPLAINED -> 99.4% matched (< 99.5) AND 0.6% unexplained
    # (> 0.1% floor) -> FAIL on both counts.
    rows_pub, rows_blt = [], []
    for i in range(1000):
        v_pub = 1000.0
        v_blt = 1000.0 if i >= 6 else 5000.0   # first 6 diverge hugely -> UNEXPLAINED
        rows_pub.append({"id_rssd": i, "period_end": "2000-12-31", "assets": v_pub})
        rows_blt.append({"id_rssd": i, "period_end": "2000-12-31", "assets": v_blt})
    pub = _modc_panel(rows_pub, ["assets"])
    blt = _modc_panel(rows_blt, ["assets"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "pubf", pub), _w(tmp_path, "bltf", blt), tmp_path)
    assert gate["matched_cells"] == 994
    assert gate["unexplained_cells"] == 6
    assert gate["match_share"] == pytest.approx(0.994)
    assert gate["verdict"] == "FAIL"


# =========================================================== coverage gaps
def test_alignment_key_mismatch_counts_as_coverage_gap_not_match(tmp_path):
    # published has an entity (rssd 2) the built panel never produced -> the built side is
    # missing -> UNEXPLAINED (a coverage gap), NOT counted as a match.
    pub = _modc_panel([
        {"id_rssd": 1, "period_end": "2000-12-31", "assets": 100.0},
        {"id_rssd": 2, "period_end": "2000-12-31", "assets": 200.0},   # built lacks rssd 2
    ], ["assets"])
    blt = _modc_panel([
        {"id_rssd": 1, "period_end": "2000-12-31", "assets": 100.0},
    ], ["assets"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "pubg", pub), _w(tmp_path, "bltg", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet").set_index("id_rssd")
    assert recon.loc[1, "class"] == tx.EXACT
    assert recon.loc[2, "class"] == tx.UNEXPLAINED   # coverage gap, not a match
    # published counts 2 cells; attempted (built present) counts only 1
    assert gate["published_cells"] == 2
    assert gate["attempted_cells"] == 1
    assert gate["matched_cells"] == 1


# =========================================================== finhist key
def test_finhist_aligns_on_charter_year_key(tmp_path):
    pub = pd.DataFrame({
        "bank_id": pd.array([500, 501], dtype="Int64"),
        "year": pd.array([1900, 1900], dtype="Int64"),
        "equity": [10.0, 20.0],
    })
    blt = pd.DataFrame({
        "bank_id": pd.array([500, 501], dtype="Int64"),
        "year": pd.array([1900, 1900], dtype="Int64"),
        "equity": [10.0, 25.0],   # 501 diverges; equity has a finhist METHOD-CHOICE reason
    })
    vr.run_era("finhist", _w(tmp_path, "hpub", pub), _w(tmp_path, "hblt", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_finhist.parquet")
    assert list(recon.columns[:2]) == ["bank_id", "year"]
    by_bank = dict(zip(recon["bank_id"].astype(int), zip(recon["class"], recon["reason_id"])))
    assert by_bank[500][0] == tx.EXACT
    # 501 diverges and equity/finhist carries MC_EQUITY_ROWTOTAL -> METHOD-CHOICE
    assert by_bank[501][0] == tx.METHOD_CHOICE
    assert by_bank[501][1] == "MC_EQUITY_ROWTOTAL"


# =========================================================== determinism
def test_deterministic_reconciliation_ordering(tmp_path):
    pub = _modc_panel([
        {"id_rssd": 3, "period_end": "2000-12-31", "assets": 1.0, "deposits": 2.0},
        {"id_rssd": 1, "period_end": "2000-12-31", "assets": 1.0, "deposits": 2.0},
        {"id_rssd": 2, "period_end": "2000-12-31", "assets": 1.0, "deposits": 2.0},
    ], ["assets", "deposits"])
    blt = pub.copy()
    vr.run_era("1976_2026", _w(tmp_path, "pubd", pub), _w(tmp_path, "bltd", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    # sorted by (id_rssd, period_end, variable)
    assert list(recon["id_rssd"].astype(int)) == [1, 1, 2, 2, 3, 3]
    # within each rssd, variable is alphabetical (assets < deposits)
    assert list(recon["variable"].head(2)) == ["assets", "deposits"]


# =========================================================== combined mode
def test_combined_report_rolls_three_eras(tmp_path):
    # write minimal gate_result_<era>.json for all three eras, then combine.
    for era in vr.ERA_TOKENS:
        g = {
            "campaign": vr.CAMPAIGN, "era": era, "era_group": vr.ERA_GROUP[era],
            "validation_key": vr.ERA_KEY[era], "matched_cells": 10,
            "match_share": 1.0, "unexplained_share": 0.0, "verdict": "PASS",
        }
        (tmp_path / f"gate_result_{era}.json").write_text(json.dumps(g), encoding="utf-8")
    report = vr.combine_reports(tmp_path)
    assert (tmp_path / "RECONSTRUCTION_REPORT.md").exists()
    assert "ALL ERAS PASS" in report
    for era in vr.ERA_TOKENS:
        assert era in report


def test_combined_report_flags_absent_era(tmp_path):
    # only one era present -> the others are ABSENT (never silently passing)
    era = vr.ERA_TOKENS[0]
    g = {"campaign": vr.CAMPAIGN, "era": era, "era_group": vr.ERA_GROUP[era],
         "validation_key": vr.ERA_KEY[era], "matched_cells": 1,
         "match_share": 1.0, "unexplained_share": 0.0, "verdict": "PASS"}
    (tmp_path / f"gate_result_{era}.json").write_text(json.dumps(g), encoding="utf-8")
    report = vr.combine_reports(tmp_path)
    assert "ABSENT" in report
    assert "NOT ALL ERAS PASS" in report


# =========================================================== outputs exist
def test_all_artifacts_written(tmp_path):
    pub = _modc_panel([{"id_rssd": 1, "period_end": "2000-12-31", "assets": 1.0}], ["assets"])
    blt = pub.copy()
    vr.run_era("1976_2026", _w(tmp_path, "pube", pub), _w(tmp_path, "blte", blt), tmp_path)
    assert (tmp_path / "reconciliation_1976_2026.parquet").exists()
    assert (tmp_path / "RECONSTRUCTION_REPORT_1976_2026.md").exists()
    gpath = tmp_path / "gate_result_1976_2026.json"
    assert gpath.exists()
    g = json.loads(gpath.read_text(encoding="utf-8"))
    # gate json keys are sorted (deterministic)
    assert list(g.keys()) == sorted(g.keys())
    # the report carries the honest boundary paragraph
    md = (tmp_path / "RECONSTRUCTION_REPORT_1976_2026.md").read_text(encoding="utf-8")
    assert "derivability boundary" in md.lower()


# =========================================================== SPEC §10.4 zero-vs-null predicate
def _modc_panel_nullable(rows, cols):
    """Like _modc_panel but preserves NaN value cells (no dtype coercion that would drop them)."""
    df = pd.DataFrame(rows)
    df["id_rssd"] = df["id_rssd"].astype("Int64")
    df["period_end"] = pd.to_datetime(df["period_end"])
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
    return df[["id_rssd", "period_end"] + cols]


def test_zero_vs_null_mask_symmetric_value_only():
    # unit test of the predicate itself: exactly-one-side-zero, other-side-NULL, both directions.
    import numpy as np
    pub = [0.0, float("nan"), 0.0, 100.0, 5.0]
    blt = [float("nan"), 0.0, 0.0, float("nan"), 6.0]
    m = vr._zero_vs_null_mask(pub, blt)
    # (0/null)=T, (null/0)=T, (0/0 both present)=F, (100/null nonzero)=F, (5/6 two-sided)=F
    assert list(m) == [True, True, False, False, False]


def test_zero_vs_null_predicate_both_sidednesses_method_choice(tmp_path):
    # pub=0.0 / blt=NULL AND pub=NULL / blt=0.0 -> METHOD-CHOICE MC_ZEROFILL_ENCODING (symmetric).
    pub = _modc_panel_nullable([
        {"id_rssd": 1, "period_end": "2005-12-31", "assets": 0.0},          # pub 0 / blt null
        {"id_rssd": 2, "period_end": "2005-12-31", "assets": float("nan")},  # pub null / blt 0
    ], ["assets"])
    blt = _modc_panel_nullable([
        {"id_rssd": 1, "period_end": "2005-12-31", "assets": float("nan")},
        {"id_rssd": 2, "period_end": "2005-12-31", "assets": 0.0},
    ], ["assets"])
    vr.run_era("1976_2026", _w(tmp_path, "zp", pub), _w(tmp_path, "zb", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet").set_index("id_rssd")
    assert recon.loc[1, "class"] == tx.METHOD_CHOICE and recon.loc[1, "reason_id"] == "MC_ZEROFILL_ENCODING"
    assert recon.loc[2, "class"] == tx.METHOD_CHOICE and recon.loc[2, "reason_id"] == "MC_ZEROFILL_ENCODING"


def test_zero_vs_null_does_not_touch_two_sided_or_nonzero_onesided(tmp_path):
    # two-sided (0 vs 5) and nonzero-one-sided (100 vs null) stay UNEXPLAINED — predicate is value-shaped.
    pub = _modc_panel_nullable([
        {"id_rssd": 3, "period_end": "2005-12-31", "assets": 0.0},           # two-sided 0 vs 5
        {"id_rssd": 4, "period_end": "2005-12-31", "assets": 100.0},         # nonzero one-sided
    ], ["assets"])
    blt = _modc_panel_nullable([
        {"id_rssd": 3, "period_end": "2005-12-31", "assets": 5.0},
        {"id_rssd": 4, "period_end": "2005-12-31", "assets": float("nan")},
    ], ["assets"])
    vr.run_era("1976_2026", _w(tmp_path, "zp2", pub), _w(tmp_path, "zb2", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet").set_index("id_rssd")
    assert recon.loc[3, "class"] == tx.UNEXPLAINED and recon.loc[3, "reason_id"] == ""
    assert recon.loc[4, "class"] == tx.UNEXPLAINED and recon.loc[4, "reason_id"] == ""


def test_zero_vs_null_wildcard_applies_to_any_variable(tmp_path):
    # the wildcard row must fire on a variable with NO specific reason (otherbor_liab, post-retirement).
    pub = _modc_panel_nullable([{"id_rssd": 7, "period_end": "1985-12-31", "otherbor_liab": 0.0}], ["otherbor_liab"])
    blt = _modc_panel_nullable([{"id_rssd": 7, "period_end": "1985-12-31", "otherbor_liab": float("nan")}], ["otherbor_liab"])
    vr.run_era("1976_2026", _w(tmp_path, "zw", pub), _w(tmp_path, "zwb", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    assert recon.loc[0, "class"] == tx.METHOD_CHOICE and recon.loc[0, "reason_id"] == "MC_ZEROFILL_ENCODING"


def test_zero_vs_null_yields_to_more_specific_not_derivable(tmp_path):
    # a securities PRE-1994 cell that is also 0-vs-NULL must stay NOT-DERIVABLE (specific boundary wins;
    # the wildcard predicate is applied LAST). This is the last-precedence guarantee (SPEC §10.4).
    pub = _modc_panel_nullable([{"id_rssd": 8, "period_end": "1990-12-31", "securities": 0.0}], ["securities"])
    blt = _modc_panel_nullable([{"id_rssd": 8, "period_end": "1990-12-31", "securities": float("nan")}], ["securities"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "zn", pub), _w(tmp_path, "znb", blt), tmp_path)
    recon = pd.read_parquet(tmp_path / "reconciliation_1976_2026.parquet")
    assert recon.loc[0, "class"] == tx.NOT_DERIVABLE and recon.loc[0, "reason_id"] == "ND_SECURITIES_PRE1994"
    assert gate["not_derivable_cells"] == 1 and gate["derivable_cells"] == 0


def test_zero_vs_null_stays_in_denominator_not_a_match(tmp_path):
    # 990 EXACT + 10 zero-vs-null(MC), 0 UNEXPLAINED. matched=990, METHOD-CHOICE=10, derivable=1000.
    # match_share = 990/1000 = 99.0% -> FAIL (< 99.5). This is the honesty invariant: were the MC cells
    # (wrongly) counted as matches -> 100% PASS; were they (wrongly) dropped from the denominator ->
    # 990/990 = 100% PASS. Keeping them in-denominator-not-match gives the honest 99.0% FAIL.
    rows_pub, rows_blt = [], []
    for i in range(990):
        rows_pub.append({"id_rssd": i, "period_end": "2005-12-31", "assets": 1000.0})
        rows_blt.append({"id_rssd": i, "period_end": "2005-12-31", "assets": 1000.0})
    for i in range(990, 1000):
        rows_pub.append({"id_rssd": i, "period_end": "2005-12-31", "assets": 0.0})
        rows_blt.append({"id_rssd": i, "period_end": "2005-12-31", "assets": float("nan")})
    pub = _modc_panel_nullable(rows_pub, ["assets"])
    blt = _modc_panel_nullable(rows_blt, ["assets"])
    gate = vr.run_era("1976_2026", _w(tmp_path, "zd", pub), _w(tmp_path, "zdb", blt), tmp_path)
    assert gate["matched_cells"] == 990
    assert gate["class_counts"]["METHOD-CHOICE"] == 10
    assert gate["derivable_cells"] == 1000              # MC stays in the denominator (not dropped)
    assert gate["match_share"] == pytest.approx(0.990)  # MC not counted as a match
    assert gate["verdict"] == "FAIL"


def test_match_reason_zero_vs_null_scalar():
    reasons = vr.load_reasons()
    era_r = vr.reasons_for_era(reasons, "1976_2026")
    # scalar predicate path: any variable, one side 0.0 / other None
    k, rid = vr.match_reason(era_r, "ln_cons", pd.Timestamp("2015-12-31"), "1976_2026",
                             published=0.0, built=None)
    assert k == tx.METHOD_CHOICE and rid == "MC_ZEROFILL_ENCODING"
    # two-sided -> no predicate match
    k2, rid2 = vr.match_reason(era_r, "ln_cons", pd.Timestamp("2015-12-31"), "1976_2026",
                               published=5.0, built=6.0)
    assert k2 is None and rid2 is None


def test_validate_reasons_rejects_unknown_predicate(tmp_path):
    bad = tmp_path / "badpred.csv"
    bad.write_text(
        "reason_id,variable,era,klass,period_start,period_end,reason,cite,predicate\n"
        "P1,*,1976_2026,METHOD-CHOICE,,,r,c,BOGUS_PREDICATE\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="predicate must be"):
        vr.load_reasons(bad)


def test_validate_reasons_predicate_row_requires_wildcard(tmp_path):
    bad = tmp_path / "predvar.csv"
    bad.write_text(
        "reason_id,variable,era,klass,period_start,period_end,reason,cite,predicate\n"
        "P2,assets,1976_2026,METHOD-CHOICE,,,r,c,ZERO_VS_NULL\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="must use variable"):
        vr.load_reasons(bad)


def test_shipped_registry_has_zerofill_and_retired_interim_rows():
    r = vr.load_reasons()
    ids = set(r["reason_id"])
    assert "MC_ZEROFILL_ENCODING" in ids
    # the three interim coverage-fork rows are RETIRED (SPEC §10.5)
    assert {"MC_FFPURCH_PUREARM_MOD", "MC_OTHERBOR_PRE1994_MOD", "MC_LNCONS_POST2011_MOD"}.isdisjoint(ids)
    z = r[r["reason_id"] == "MC_ZEROFILL_ENCODING"].iloc[0]
    assert z["variable"] == "*" and z["predicate"] == "ZERO_VS_NULL" and z["klass"] == "METHOD-CHOICE"


# --------------------------------------------------------------------------- util
def _w(tmp_path, name, df):
    """Write a fixture panel to parquet under tmp_path; return the path."""
    p = tmp_path / f"{name}.parquet"
    df.to_parquet(p, index=False)
    return p
