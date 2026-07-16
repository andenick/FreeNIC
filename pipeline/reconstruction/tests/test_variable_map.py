"""Tests for the variable_map loader/validator (RECONSTRUCTION_SPEC.md §R2 / §9).

Fast, no warehouse. Uses the shipped CSV plus small in-memory frames for the
negative-path schema checks.
"""

import pandas as pd
import pytest

from pipeline.reconstruction import variable_map as vm


def test_shipped_csv_loads_and_validates():
    df = vm.load_variable_map()            # defaults to the shipped copy, validate=True
    assert len(df) > 0
    assert tuple(df.columns) == vm.REQUIRED_COLUMNS


def test_quoted_commas_parsed_not_split():
    # dofile_cite carries embedded commas inside quotes; the stdlib parser must keep the
    # 8-column contract (naive comma-splitting would explode these rows).
    df = vm.load_variable_map()
    assert tuple(df.columns) == vm.REQUIRED_COLUMNS
    assert df.shape[1] == 8


def test_confidence_and_scope_domains_hold_on_shipped():
    df = vm.load_variable_map()
    assert set(df["confidence"].unique()) <= vm.CONFIDENCE_CLASSES
    assert set(df["source_kind"].unique()) <= vm.SOURCE_KINDS
    assert set(df["scope_v11"].unique()) <= {"TRUE", "FALSE"}


def test_scoped_filter():
    df = vm.load_variable_map()
    in_scope = vm.scoped(df)
    out_scope = vm.scoped(df, in_scope=False)
    assert (in_scope["scope_v11"] == "TRUE").all()
    assert (out_scope["scope_v11"] == "FALSE").all()
    assert len(in_scope) + len(out_scope) == len(df)
    assert len(in_scope) > 0    # core-first scope is non-empty (SPEC §D1)


def test_confidence_counts_has_expected_classes():
    counts = vm.confidence_counts(vm.load_variable_map())
    assert "exact" in counts
    assert counts["exact"] > 0


# --------------------------------------------------------------- schema negatives
def _good_frame():
    return pd.DataFrame([{
        "variable": "assets", "era": "1976-2026", "source_kind": "mdrm_fed_direct",
        "source_ref": "cf(RCFD2170)", "formula_id": "F_assets_mod",
        "dofile_cite": "30_build AGG_SQL", "confidence": "exact", "scope_v11": "TRUE",
    }])


def test_validate_schema_accepts_good_frame():
    vm.validate_schema(_good_frame())   # no raise


def test_validate_schema_rejects_missing_column():
    df = _good_frame().drop(columns=["confidence"])
    with pytest.raises(ValueError, match="columns mismatch"):
        vm.validate_schema(df)


def test_validate_schema_rejects_bad_confidence():
    df = _good_frame()
    df.loc[0, "confidence"] = "very-sure"
    with pytest.raises(ValueError, match="confidence"):
        vm.validate_schema(df)


def test_validate_schema_rejects_bad_source_kind():
    df = _good_frame()
    df.loc[0, "source_kind"] = "vibes"
    with pytest.raises(ValueError, match="source_kind"):
        vm.validate_schema(df)


def test_validate_schema_rejects_bad_scope():
    df = _good_frame()
    df.loc[0, "scope_v11"] = "maybe"
    with pytest.raises(ValueError, match="scope_v11"):
        vm.validate_schema(df)


def test_validate_schema_rejects_empty_variable():
    df = _good_frame()
    df.loc[0, "variable"] = "  "
    with pytest.raises(ValueError, match="empty 'variable'"):
        vm.validate_schema(df)


# --------------------------------------------------------------- sync check
def test_shipped_copy_in_sync_with_spec():
    # spec-dir copy is the working canonical until v1.1.0 ships; shipped copy must match.
    # no-op (passes) if the spec dir isn't present (clean clone).
    vm.assert_in_sync()
