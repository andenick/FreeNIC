"""Pre-registered divergence taxonomy for the Luck / finhist reconstruction.

Implements the classifier defined in RECONSTRUCTION_SPEC.md **section 7**
("PRE-REGISTERED DIVERGENCE TAXONOMY + THRESHOLDS"), itself copied verbatim from
the campaign plan (FREENIC_11_RECONSTRUCTION_PLAN_20260715.md, §R3 + §D2).

The whole point of this module is that the thresholds are **registered BEFORE any
validation code runs, as hard CONSTANTS with the plan's D2 values** — there are no
tunable knobs, so the validation harness (build_reconstruction / validate_reconstruction)
cannot be quietly tuned to make a match rate clear a gate. Change a constant here and
you are changing the pre-registration, which is a visible, reviewable act.

Spec anchor (for the Batch-3 mechanical refresh after the adversarial checker lands):
    RECONSTRUCTION_SPEC.md §7  (taxonomy table + match gates)

Citation posture (D3): original code. No CLV do-file is reproduced; §7 is a plan-level
taxonomy, not a do-file, so there is no per-do-file locus to cite here.

Runtime deps: pandas only (for the vectorised helper). The scalar ``classify`` is pure
Python. No warehouse access.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# The seven classes (RECONSTRUCTION_SPEC.md §7 taxonomy table, verbatim names).
# Exactly one class is assigned to every overlapping published<->built cell.
# ---------------------------------------------------------------------------
EXACT = "EXACT"                 # built == published, bit-identical after type normalization
ROUNDING = "ROUNDING"           # |delta| <= 0.5 units-of-last-digit
TOLERANCE = "TOLERANCE"         # |relative delta| <= 1e-4
VINTAGE = "VINTAGE"             # Dec-2025 snapshot vs our quarter refreshes / FFIEC bulk-vintage; documented per case
METHOD_CHOICE = "METHOD-CHOICE"  # documented fork (code vs docs vs crosswalk / freeNIC alt); cite both loci
NOT_DERIVABLE = "NOT-DERIVABLE"  # outside the derivability boundary (SPEC §0); reported honestly, never imputed
UNEXPLAINED = "UNEXPLAINED"     # survives none of the above -> COUNTS AGAINST THE GATE

#: All classes, in the §7 table order.
ALL_CLASSES = (
    EXACT,
    ROUNDING,
    TOLERANCE,
    VINTAGE,
    METHOD_CHOICE,
    NOT_DERIVABLE,
    UNEXPLAINED,
)

#: Classes that count as a "match" for the gate (SPEC §7 "Match gates":
#: "EXACT+ROUNDING+TOLERANCE"). VINTAGE / METHOD-CHOICE / NOT-DERIVABLE are
#: documented-but-not-matched; UNEXPLAINED is a failure.
MATCH_CLASSES = frozenset({EXACT, ROUNDING, TOLERANCE})

#: The pre-registered, documented-divergence classes. A cell can only carry one of
#: these if it was pre-registered per-case in the spec / variable_map (they are NOT
#: inferable from the numbers alone — see §7). ``classify`` accepts such a
#: pre-registration and honours it over any numeric verdict.
REGISTERED_CLASSES = frozenset({VINTAGE, METHOD_CHOICE, NOT_DERIVABLE})

# ---------------------------------------------------------------------------
# Numeric thresholds — D2 values, HARD CONSTANTS (no runtime knobs). SPEC §7.
# ---------------------------------------------------------------------------
#: ROUNDING band, as a fraction of the caller-supplied units-of-last-digit (ULP).
#: SPEC §7: ROUNDING iff ``|delta| <= 0.5 * units_of_last_digit`` (<= is inclusive).
ROUNDING_ULP_FACTOR = 0.5

#: TOLERANCE band on the relative delta. SPEC §7: ``|relative delta| <= 1e-4`` (inclusive).
TOLERANCE_REL = 1e-4

# ---------------------------------------------------------------------------
# Match GATES — plan §B2 / §D2 defaults, pre-registered. SPEC §7 "Match gates".
# Keyed by the three reconstruction eras. (EXACT+ROUNDING+TOLERANCE) share must
# meet-or-exceed the threshold AND UNEXPLAINED share must not exceed the floor.
# ---------------------------------------------------------------------------
GATE_1976_2026 = 0.995   # independent Fed-direct re-derivation
GATE_1959_1975 = 0.999   # derivation layer: their formula on their input -> near-perfect
GATE_FINHIST = 0.995     # 1863-1941 derivation layer
UNEXPLAINED_FLOOR = 0.001  # any UNEXPLAINED share above this blocks G-MATCH (>0.1%)

#: Era key -> match-share threshold, for the harness (Batch 4). Era keys match the
#: entity_spine era groups.
GATE_BY_ERA = {
    "MODC": GATE_1976_2026,   # 1976-2026
    "MODL": GATE_1959_1975,   # 1959Q4-1975Q4
    "HIST": GATE_FINHIST,     # 1863-1941 finhist
}


def _is_missing(x) -> bool:
    """True for None / NaN. (pandas NA also lands here via != self or math.isnan.)"""
    if x is None:
        return True
    try:
        return bool(math.isnan(x))
    except (TypeError, ValueError):
        # non-float (e.g. pandas.NA) — compare to self
        return x != x


def classify(
    published,
    built,
    units_last_digit: float,
    registered_class: Optional[str] = None,
) -> str:
    """Classify one published<->built cell into exactly one taxonomy class.

    Implements RECONSTRUCTION_SPEC.md **§7** verbatim. The three positional
    arguments are the whole numeric contract; ``registered_class`` is the optional
    per-cell pre-registration channel for the three documented-divergence classes
    (VINTAGE / METHOD-CHOICE / NOT-DERIVABLE), which by §7 are NOT inferable from the
    numbers and must be carried from the spec / variable_map.

    Parameters
    ----------
    published, built:
        The reference (their published) value and our rebuilt value. ``None``/NaN
        means "cell absent". Both-absent -> EXACT; exactly-one-absent -> UNEXPLAINED
        (a coverage miss the gate must see), unless pre-registered NOT-DERIVABLE.
    units_last_digit:
        The magnitude of the published value's last significant digit (its ULP).
        e.g. integers displayed to the dollar -> ``1``; a value shown to 2 dp -> ``0.01``.
        The ROUNDING band is ``ROUNDING_ULP_FACTOR * units_last_digit``.
    registered_class:
        If one of REGISTERED_CLASSES, it wins outright (the cell was pre-registered
        as a documented divergence). Any other value is ignored. Passing ``None``
        (the default) runs the pure numeric classifier — so the documented
        ``classify(published, built, units_last_digit)`` 3-arg signature is exact.

    Returns
    -------
    One of :data:`ALL_CLASSES`.
    """
    # Pre-registered documented divergence (SPEC §7 VINTAGE/METHOD-CHOICE/NOT-DERIVABLE)
    # is not a numeric verdict; if the spec pinned it, honour it.
    if registered_class in REGISTERED_CLASSES:
        return registered_class

    pub_missing = _is_missing(published)
    blt_missing = _is_missing(built)
    if pub_missing and blt_missing:
        return EXACT           # both absent -> agree
    if pub_missing or blt_missing:
        return UNEXPLAINED     # coverage asymmetry the gate must count

    pub = float(published)
    blt = float(built)

    # EXACT: bit-identical after type normalization (SPEC §7).
    if pub == blt:
        return EXACT

    delta = abs(blt - pub)

    # ROUNDING: |delta| <= 0.5 ULP (inclusive). SPEC §7.
    if units_last_digit is not None and not _is_missing(units_last_digit):
        if delta <= ROUNDING_ULP_FACTOR * float(units_last_digit):
            return ROUNDING

    # TOLERANCE: |relative delta| <= 1e-4 (inclusive). SPEC §7.
    # Relative to the published (reference) magnitude; guard the pub==0 case.
    if pub != 0.0 and (delta / abs(pub)) <= TOLERANCE_REL:
        return TOLERANCE

    return UNEXPLAINED


def classify_vec(
    published,
    built,
    units_last_digit,
    registered_class=None,
) -> np.ndarray:
    """Vectorised twin of :func:`classify` (RECONSTRUCTION_SPEC.md §7), for whole columns.

    Elementwise-identical to calling :func:`classify` cell-by-cell over the same inputs —
    this is a pure numpy/pandas rewrite over the **same D2 CONSTANTS**
    (:data:`ROUNDING_ULP_FACTOR`, :data:`TOLERANCE_REL`, :data:`REGISTERED_CLASSES`,
    :data:`MATCH_CLASSES`), so there is **zero logic drift**: the harness proves the
    identity on a 100k-cell random sample (``test_classify_vec_matches_scalar``). Added
    because the G-MATCH runs are ~60M (MODL) + ~29M (finhist) cells and a per-cell Python
    call is the bottleneck; the classification policy is unchanged.

    Parameters
    ----------
    published, built:
        Array-likes (numpy array / pandas Series / list) of the reference and rebuilt
        values. Coerced to ``float64`` with NaN for missing (None / NaN / pandas NA), which
        is exactly how :func:`_is_missing` treats a missing side.
    units_last_digit:
        Array-like (or scalar, broadcast) of per-cell ULP values. A NaN ULP disables the
        ROUNDING branch for that cell, matching the scalar's ``not _is_missing(...)`` guard.
    registered_class:
        Optional array-like (or scalar, broadcast) of pre-registration strings. Where the
        value is one of :data:`REGISTERED_CLASSES` the cell takes that class outright (the
        documented-divergence channel); any other value (incl. ``None``/NaN) is ignored and
        the cell runs the numeric classifier — exactly the scalar contract. Pass ``None``
        (default) to run the pure numeric classifier over every cell.

    Returns
    -------
    ``np.ndarray`` (dtype object) of class strings, one per input cell, drawn from
    :data:`ALL_CLASSES`.
    """
    pub = pd.to_numeric(pd.Series(published), errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    blt = pd.to_numeric(pd.Series(built), errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    n = pub.shape[0]

    ulp = np.asarray(units_last_digit, dtype="float64")
    if ulp.ndim == 0:
        ulp = np.full(n, float(ulp))

    out = np.empty(n, dtype=object)
    decided = np.zeros(n, dtype=bool)

    # (0) Pre-registered documented divergence wins outright (SPEC §7); mirrors the scalar's
    #     ``if registered_class in REGISTERED_CLASSES`` short-circuit, elementwise.
    if registered_class is not None:
        rc = np.asarray(registered_class, dtype=object)
        if rc.ndim == 0:
            rc = np.full(n, rc.item(), dtype=object)
        reg_mask = np.zeros(n, dtype=bool)
        for k in REGISTERED_CLASSES:
            reg_mask |= (rc == k)
        if reg_mask.any():
            out[reg_mask] = rc[reg_mask]
            decided |= reg_mask

    pub_missing = np.isnan(pub)
    blt_missing = np.isnan(blt)

    # (1) both absent -> EXACT
    m = (~decided) & pub_missing & blt_missing
    out[m] = EXACT
    decided |= m

    # (2) exactly one absent -> UNEXPLAINED (coverage asymmetry the gate must count)
    m = (~decided) & (pub_missing ^ blt_missing)
    out[m] = UNEXPLAINED
    decided |= m

    present = ~pub_missing & ~blt_missing

    # (3) EXACT: bit-identical after type normalization
    m = (~decided) & present & (pub == blt)
    out[m] = EXACT
    decided |= m

    delta = np.abs(blt - pub)

    # (4) ROUNDING: |delta| <= 0.5 * ULP (inclusive); NaN ULP disables the branch
    ulp_ok = ~np.isnan(ulp)
    m = (~decided) & present & ulp_ok & (delta <= ROUNDING_ULP_FACTOR * ulp)
    out[m] = ROUNDING
    decided |= m

    # (5) TOLERANCE: |relative delta| <= 1e-4 (inclusive); guard pub == 0
    nonzero = present & (pub != 0.0)
    rel = np.full(n, np.inf)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel[nonzero] = delta[nonzero] / np.abs(pub[nonzero])
    m = (~decided) & nonzero & (rel <= TOLERANCE_REL)
    out[m] = TOLERANCE
    decided |= m

    # (6) everything left -> UNEXPLAINED
    out[~decided] = UNEXPLAINED
    return out


def gate_for_era(era_group: str) -> float:
    """Match-share threshold for an era group (SPEC §7 match gates). See GATE_BY_ERA."""
    try:
        return GATE_BY_ERA[era_group]
    except KeyError:
        raise KeyError(
            f"unknown era_group {era_group!r}; expected one of {sorted(GATE_BY_ERA)}"
        )


def passes_gate(class_counts: dict, era_group: str) -> bool:
    """Evaluate G-MATCH for an era from a class -> count mapping (SPEC §7).

    A gate passes iff the matched share (EXACT+ROUNDING+TOLERANCE) meets-or-exceeds
    :func:`gate_for_era` AND the UNEXPLAINED share does not exceed
    :data:`UNEXPLAINED_FLOOR`. NOT-DERIVABLE cells are outside the boundary and are
    excluded from the denominator (they were never claimable).
    """
    total = sum(class_counts.get(c, 0) for c in ALL_CLASSES)
    derivable = total - class_counts.get(NOT_DERIVABLE, 0)
    if derivable <= 0:
        return False
    matched = sum(class_counts.get(c, 0) for c in MATCH_CLASSES)
    unexplained = class_counts.get(UNEXPLAINED, 0)
    match_share = matched / derivable
    unexplained_share = unexplained / derivable
    return match_share >= gate_for_era(era_group) and unexplained_share <= UNEXPLAINED_FLOOR
