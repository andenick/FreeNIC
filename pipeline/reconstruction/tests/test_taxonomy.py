"""Tests for the pre-registered divergence taxonomy (RECONSTRUCTION_SPEC.md §7).

Fast, pure, no warehouse. Emphasis on the exact boundary values (0.5 ULP, 1e-4 relative)
because the whole point of §7 is that the thresholds are pre-registered and inclusive.
"""

import math

import numpy as np
import pytest

from pipeline.reconstruction import taxonomy as tx


# --------------------------------------------------------------------------- EXACT
def test_exact_equal_ints():
    assert tx.classify(100, 100, 1) == tx.EXACT


def test_exact_type_normalized_int_vs_float():
    # "bit-identical after type normalization" — 5 == 5.0
    assert tx.classify(5, 5.0, 1) == tx.EXACT


def test_exact_both_missing():
    assert tx.classify(None, None, 1) == tx.EXACT
    assert tx.classify(float("nan"), float("nan"), 1) == tx.EXACT


# --------------------------------------------------------------------------- ROUNDING
def test_rounding_within_half_ulp():
    # ULP=1 -> band 0.5; delta 0.3 -> ROUNDING
    assert tx.classify(100.0, 100.3, 1) == tx.ROUNDING


def test_rounding_exactly_half_ulp_is_inclusive():
    # boundary: |delta| == 0.5 * ULP must classify as ROUNDING (<= is inclusive)
    assert tx.classify(100.0, 100.5, 1) == tx.ROUNDING
    assert tx.classify(100.0, 99.5, 1) == tx.ROUNDING


def test_rounding_scaled_ulp_two_decimals():
    # value shown to 2 dp -> ULP 0.01 -> band 0.005. Use representable deltas either side
    # of the band (0.005 itself is not a representable double at this scale).
    assert tx.classify(1.230, 1.234, 0.01) == tx.ROUNDING       # 0.004 < band -> ROUNDING
    assert tx.classify(1.230, 1.236, 0.01) != tx.ROUNDING       # 0.006 > band -> not ROUNDING


def test_just_over_half_ulp_is_not_rounding():
    # delta 0.5001 with ULP 1 -> not ROUNDING; also outside 1e-4 rel -> UNEXPLAINED
    assert tx.classify(100.0, 100.5001, 1) == tx.UNEXPLAINED


# --------------------------------------------------------------------------- TOLERANCE
def test_tolerance_exactly_1e4_relative_is_inclusive():
    # published 1_000_000; rel 1e-4 -> abs 100; ULP tiny so ROUNDING can't catch it
    assert tx.classify(1_000_000.0, 1_000_100.0, 0.0001) == tx.TOLERANCE


def test_tolerance_just_over_1e4_is_unexplained():
    assert tx.classify(1_000_000.0, 1_000_101.0, 0.0001) == tx.UNEXPLAINED


def test_tolerance_below_band():
    assert tx.classify(1_000_000.0, 1_000_050.0, 0.0001) == tx.TOLERANCE


# --------------------------------------------------------------------------- UNEXPLAINED
def test_unexplained_large_gap():
    assert tx.classify(100.0, 200.0, 1) == tx.UNEXPLAINED


def test_unexplained_one_side_missing():
    assert tx.classify(100.0, None, 1) == tx.UNEXPLAINED
    assert tx.classify(None, 100.0, 1) == tx.UNEXPLAINED


def test_published_zero_does_not_divide():
    # pub==0 guards the relative test; nonzero built -> UNEXPLAINED (not a crash)
    assert tx.classify(0.0, 5.0, 0.0001) == tx.UNEXPLAINED
    # pub==0, built==0 -> EXACT
    assert tx.classify(0.0, 0.0, 1) == tx.EXACT


# --------------------------------------------------------------------- registered classes
@pytest.mark.parametrize("rc", [tx.VINTAGE, tx.METHOD_CHOICE, tx.NOT_DERIVABLE])
def test_registered_class_wins_over_numbers(rc):
    # even a perfect numeric match yields the pre-registered documented class
    assert tx.classify(100, 100, 1, registered_class=rc) == rc
    # and a huge numeric gap still yields the registered class (never UNEXPLAINED)
    assert tx.classify(100, 999, 1, registered_class=rc) == rc


def test_non_registered_override_is_ignored():
    # passing a bogus / non-documented class falls through to the numeric verdict
    assert tx.classify(100, 100, 1, registered_class="EXACT") == tx.EXACT
    assert tx.classify(100, 200, 1, registered_class="whatever") == tx.UNEXPLAINED


# --------------------------------------------------------------------------- constants
def test_d2_constants_are_pinned():
    assert tx.ROUNDING_ULP_FACTOR == 0.5
    assert tx.TOLERANCE_REL == 1e-4
    assert tx.GATE_1976_2026 == 0.995
    assert tx.GATE_1959_1975 == 0.999
    assert tx.GATE_FINHIST == 0.995
    assert tx.UNEXPLAINED_FLOOR == 0.001
    assert tx.MATCH_CLASSES == frozenset({tx.EXACT, tx.ROUNDING, tx.TOLERANCE})


# --------------------------------------------------------------------------- gates
def test_gate_for_era():
    assert tx.gate_for_era("MODC") == 0.995
    assert tx.gate_for_era("MODL") == 0.999
    assert tx.gate_for_era("HIST") == 0.995
    with pytest.raises(KeyError):
        tx.gate_for_era("BOGUS")


def test_passes_gate_matched_share_and_unexplained_floor():
    # 999 matched / 1 unexplained out of 1000 derivable -> 99.9% matched, 0.1% unexplained
    counts = {tx.EXACT: 999, tx.UNEXPLAINED: 1}
    assert tx.passes_gate(counts, "MODC") is True          # 99.9% >= 99.5%, 0.1% <= 0.1%
    # push unexplained just over the floor -> block
    counts = {tx.EXACT: 998, tx.UNEXPLAINED: 2}
    assert tx.passes_gate(counts, "MODC") is False         # 0.2% > 0.1% floor


def test_passes_gate_excludes_not_derivable_from_denominator():
    # 500 NOT-DERIVABLE cells are outside the boundary -> not in the denominator
    counts = {tx.EXACT: 500, tx.NOT_DERIVABLE: 500}
    assert tx.passes_gate(counts, "MODC") is True          # 500/500 derivable matched


# ------------------------------------------------ vectorised classify equivalence
def test_classify_vec_matches_scalar_100k():
    """The whole point of classify_vec: it MUST be elementwise-identical to the scalar
    classify over a large adversarial random sample, else the big-run classification has
    drifted from the pre-registered §7 policy. 100k cells spanning every branch:
    both-missing, one-side-missing, EXACT, ROUNDING at/around 0.5 ULP, TOLERANCE at/around
    1e-4 relative, large gaps, pub==0, varied ULPs, and the registered-class channel.
    """
    rng = np.random.default_rng(20260715)
    n = 100_000

    # published: a spread of magnitudes + integers/fractionals + some missing + some zeros
    base = rng.uniform(-5, 8, n)
    pub = np.sign(rng.standard_normal(n)) * (10.0 ** base)
    decimals = rng.integers(0, 4, n)                                # varied displayed precision -> varied ULP
    for k in range(4):                                             # np.round takes a scalar 'decimals'
        sel = decimals == k
        pub[sel] = np.round(pub[sel], k)
    pub[rng.random(n) < 0.05] = 0.0                                 # some exact zeros (guards rel div)
    pub[rng.random(n) < 0.08] = np.nan                              # some missing published

    # built: mostly a perturbation of published so all arithmetic bands are exercised
    kind = rng.integers(0, 5, n)
    built = pub.copy()
    # kind 0: exact (leave as pub); kind 1: tiny (<=0.5 ULP-ish); kind 2: ~1e-4 rel;
    # kind 3: large gap; kind 4: built missing
    built[kind == 1] = pub[kind == 1] + rng.uniform(-0.5, 0.5, (kind == 1).sum())
    built[kind == 2] = pub[kind == 2] * (1.0 + rng.uniform(-2e-4, 2e-4, (kind == 2).sum()))
    built[kind == 3] = pub[kind == 3] * rng.uniform(1.5, 4.0, (kind == 3).sum()) + 1.0
    built[kind == 4] = np.nan
    built[rng.random(n) < 0.05] = np.nan                           # extra independent missing

    # ULP: mix of the structurally-derived value and some explicit/NaN ULPs
    from pipeline.reconstruction.validate_reconstruction import units_last_digit_vec
    ulp = units_last_digit_vec(pub)
    explicit = rng.random(n) < 0.15
    ulp[explicit] = rng.choice([1.0, 0.1, 0.01, 0.001, np.nan], explicit.sum())

    # registered_class channel: mostly None, some documented classes, some bogus
    reg = np.array([None] * n, dtype=object)
    pick = rng.random(n)
    reg[pick < 0.04] = tx.VINTAGE
    reg[(pick >= 0.04) & (pick < 0.08)] = tx.METHOD_CHOICE
    reg[(pick >= 0.08) & (pick < 0.12)] = tx.NOT_DERIVABLE
    reg[(pick >= 0.12) & (pick < 0.15)] = "BOGUS"                  # ignored -> numeric verdict

    # --- without registration
    vec = tx.classify_vec(pub, built, ulp)
    scal = np.array([tx.classify(p, b, u) for p, b, u in zip(pub, built, ulp)], dtype=object)
    mismatch = np.where(vec != scal)[0]
    assert mismatch.size == 0, (
        f"{mismatch.size} classify_vec/scalar mismatches (no reg); "
        f"first: i={mismatch[:5]} pub={pub[mismatch[:5]]} built={built[mismatch[:5]]}"
    )

    # --- with the registered-class channel
    vec_r = tx.classify_vec(pub, built, ulp, registered_class=reg)
    scal_r = np.array(
        [tx.classify(p, b, u, registered_class=r) for p, b, u, r in zip(pub, built, ulp, reg)],
        dtype=object,
    )
    mismatch_r = np.where(vec_r != scal_r)[0]
    assert mismatch_r.size == 0, f"{mismatch_r.size} classify_vec/scalar mismatches (with reg)"
