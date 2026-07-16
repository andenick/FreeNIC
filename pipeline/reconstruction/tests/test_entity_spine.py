"""Tests for the era-aware entity spine (RECONSTRUCTION_SPEC.md §6.1).

Fast, fixture-based, no warehouse. Covers the correctness-critical edge cases the
adversarial review (Part V) is expected to attack: receivership version bumps, the
missing-cert `-id_rssd` rule, post-failure pseudo-ids, and era-boundary non-join
(range disjointness).
"""

import numpy as np
import pandas as pd
import pytest

from pipeline.reconstruction import entity_spine as es


# ------------------------------------------------------- HIST version / entity id
def test_hist_version_receivership_restart_bumps_transient_version():
    # bank 500 runs 1900-1902; end_date changes at 1902 -> the TRANSIENT 04 version-id
    # bumps to 2 (04 L14-18). Per the G-SPEC correction this id is dropped downstream;
    # the delivered panel pools the bank under charter 500 (see hist_panel_key test).
    df = pd.DataFrame({
        "bank_id": [500, 500, 500],
        "year": [1900, 1901, 1902],
        "end_date": ["1901-12-31", "1901-12-31", "1935-06-30"],
    })
    v = es.hist_version(df)
    assert list(v) == [1, 1, 2]
    ids = es.hist_entity_id(df["bank_id"], v)
    assert list(ids) == [5001, 5001, 5002]


def test_hist_panel_key_pools_under_charter():
    # G-SPEC: the persistent HIST key is the charter; a re-entering bank stays one entity.
    key = es.hist_panel_key(pd.Series([500, 500, 500]))
    assert list(key) == [500, 500, 500]


def test_hist_version_preserves_original_row_order():
    # shuffled input; version must align back to df.index, not the sorted order
    df = pd.DataFrame({
        "bank_id": [7, 7, 7],
        "year": [1912, 1910, 1911],
        "end_date": ["c", "a", "a"],
    })
    v = es.hist_version(df)
    # year 1910 -> v1, 1911 -> v1 (same end_date 'a'), 1912 -> v2 ('c')
    assert v.loc[0] == 2   # the 1912/'c' row
    assert v.loc[1] == 1   # the 1910/'a' row
    assert v.loc[2] == 1   # the 1911/'a' row


def test_hist_entity_id_scalar():
    assert es.hist_entity_id(500, 2) == 5002


# ------------------------------------------------------- MODERN cert resolution
def test_resolve_fdic_cert_missing_filled_with_negative_rssd():
    # zero cert -> missing -> -rssd; genuinely-missing cert -> -rssd; real cert kept.
    # SPEC §6.1 / 05 L54-59.
    df = pd.DataFrame({
        "id_fdic_cert": [1234.0, 0.0, np.nan],
        "id_rssd": [9999.0, 8888.0, 7777.0],
    })
    out = es.resolve_fdic_cert(df["id_fdic_cert"], df["id_rssd"])
    assert list(out) == [1234, -8888, -7777]


def test_drop_unkeyed_removes_rows_with_no_cert_and_no_rssd():
    df = pd.DataFrame({
        "id_fdic_cert": [1234.0, np.nan],
        "id_rssd": [9999.0, np.nan],   # second row: no cert, no rssd -> unkeyable
    })
    df["id_fdic_cert_resolved"] = es.resolve_fdic_cert(df["id_fdic_cert"], df["id_rssd"])
    kept = es.drop_unkeyed(df)
    assert len(kept) == 1
    assert kept["id_fdic_cert_resolved"].iloc[0] == 1234


# ------------------------------------------------------- MODERN failure pseudo-id
def test_modern_bank_id_scale_and_failure_bump():
    # no failure yet: (1234*10 + 0 + 0) * 1e5
    assert es.modern_bank_id(1234, 0, 0) == 12340 * 100_000
    # after first failure event: id bumps -> distinct entity
    assert es.modern_bank_id(1234, 1, 0) == 12341 * 100_000
    # rare double-failure: both flags set
    assert es.modern_bank_id(1234, 1, 1) == 12342 * 100_000


def test_modern_bank_id_vectorised():
    cert = pd.Series([1234, 5678], dtype="Int64")
    out = es.modern_bank_id(cert, 0, 0)
    assert list(out) == [12340 * 100_000, 56780 * 100_000]


# ------------------------------------------------------- MODC rssd-native
def test_modc_rssd_key_is_rssd():
    out = es.modc_rssd_key(pd.Series([111, 222]), pd.Series(["2000-12-31", "2001-12-31"]))
    assert list(out) == [111, 222]


# ------------------------------------------------------- freeNIC unified key
def test_freenic_entity_key_hist_vs_modern():
    era = pd.Series([es.HIST, es.MODC])
    out = es.freenic_entity_key(era, bank_id=pd.Series([500, 0]),
                                rssd_id=pd.Series([0, 9999]),
                                src_vintage=pd.Series(["", "jan2026"]))
    assert out.iloc[0] == "H500"
    assert out.iloc[1] == "Mjan2026_9999"


# ------------------------------------------------------- era classification
@pytest.mark.parametrize("year,era", [
    (1863, es.HIST), (1941, es.HIST),
    (1942, es.GAP), (1958, es.GAP),
    (1959, es.MODL), (1975, es.MODL),
    (1976, es.MODC), (2026, es.MODC),
])
def test_era_of_year_boundaries(year, era):
    assert es.era_of_year(year) == era


def test_era_series_vectorised_including_gap():
    s = es.era_series([1900, 1950, 1970, 2000])
    assert list(s) == [es.HIST, es.GAP, es.MODL, es.MODC]


# ------------------------------------------------------- append-not-join invariant
def test_assert_eras_disjoint_passes_for_valid_ranges():
    hist = pd.Series([5001, 5002, 999_990])                 # positive, < 1e6
    modern = pd.Series([12340 * 100_000, 56780 * 100_000])  # >= 1e6, scaled
    es.assert_eras_disjoint(hist, modern)                   # should not raise


def test_assert_eras_disjoint_accepts_negative_surrogate_modern_id():
    # G-SPEC: a cert-missing bank -> negative bank_id (-id_rssd surrogate), |id| >= 1e6.
    hist = pd.Series([5001])
    modern = pd.Series([-88880 * 100_000])                  # negative, |id| = 8.888e9
    es.assert_eras_disjoint(hist, modern)                   # legitimate, must not raise


def test_assert_eras_disjoint_flags_unscaled_modern_id():
    # a modern id that skipped the *1e5 scaling collides with charter space -> raise
    hist = pd.Series([5001])
    modern = pd.Series([50])                                # |id| < 1e6
    with pytest.raises(AssertionError, match="below modern floor"):
        es.assert_eras_disjoint(hist, modern)


def test_assert_eras_disjoint_flags_hist_id_at_modern_scale():
    hist = pd.Series([2_000_000])                           # a HIST id reaching modern scale
    modern = pd.Series([12340 * 100_000])
    with pytest.raises(AssertionError, match="reaching modern scale"):
        es.assert_eras_disjoint(hist, modern)


# ------------------------------------------------------- alignment key
def test_alignment_key_returns_natural_key_columns():
    df = pd.DataFrame({"id_rssd": [1, 2], "period_end": ["2000-12-31", "2001-12-31"],
                       "assets": [10, 20]})
    out = es.alignment_key(df)
    assert list(out.columns) == ["id_rssd", "period_end"]
    assert len(out) == 2


def test_alignment_key_raises_when_column_absent():
    df = pd.DataFrame({"id_rssd": [1], "assets": [10]})   # no period_end
    with pytest.raises(KeyError, match="period_end"):
        es.alignment_key(df)
