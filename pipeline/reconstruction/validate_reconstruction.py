"""``validate_reconstruction.py`` — the reconstruction validation harness.

"The perfect reverse engineer" made operational (plan §B2). Given a *published* Luck /
finhist panel and a *built* (reconstructed) panel for one era, this harness aligns them
on the spec's validation key, classifies every overlapping cell into the pre-registered
divergence taxonomy (RECONSTRUCTION_SPEC.md §7), and emits an honest coverage matrix, a
cell-level reconciliation parquet, a human report, and a machine gate result.

Design invariants (campaign non-negotiables)
--------------------------------------------
* **No tunable thresholds live here.** Every number that decides a class or a gate is a
  constant in :mod:`pipeline.reconstruction.taxonomy` (the pre-registration). This module
  calls :func:`taxonomy.classify` / :func:`taxonomy.passes_gate` and reads
  :data:`taxonomy.MATCH_CLASSES` / :data:`taxonomy.UNEXPLAINED_FLOOR`; it introduces no
  numeric policy of its own. The only data-derived quantity computed here,
  :func:`units_last_digit`, is a base-10 place value of the *published* value (structural,
  not a knob).
* **First-match precedence (SPEC §7).** A cell is classed
  ``EXACT -> ROUNDING -> TOLERANCE -> VINTAGE -> METHOD-CHOICE -> NOT-DERIVABLE -> UNEXPLAINED``,
  first satisfied class wins. The three arithmetic matches (EXACT/ROUNDING/TOLERANCE) are
  decided *first* by :func:`taxonomy.classify`; only a cell that fails all three may take a
  documented class, and only if a **pre-registered reason key** exists for it in
  ``divergence_reasons.csv``. A non-arithmetic divergence with no registered reason is
  **UNEXPLAINED** — never silently relabelled VINTAGE.
* **Reason-registry discipline.** Every VINTAGE / METHOD-CHOICE / NOT-DERIVABLE assignment
  cites a ``reason_id`` from the registry. The registry is the only channel for those three
  classes; there is no in-code path to mint them.
* **Alignment-key mismatches are coverage gaps, not matches.** A key present in one panel
  only produces cells with one side missing -> UNEXPLAINED (unless pre-registered
  NOT-DERIVABLE). They count against the gate; they are never scored as agreement.
* **Deterministic output.** All emitted rows/tables are sorted by (key..., variable); JSON
  keys are sorted; no wall-clock timestamps enter the artifacts.

Citation posture (D3): original code implementing the plan §B2 harness spec; it reproduces
no CLV do-file code. Runtime deps: pandas (+ pyarrow for parquet). No warehouse access.
"""

from __future__ import annotations
import os

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from pipeline.reconstruction import entity_spine as es
from pipeline.reconstruction import taxonomy as tx
from pipeline.reconstruction import variable_map as vm

CAMPAIGN = "FREENIC11_RECONSTRUCTION_20260715"

# --------------------------------------------------------------------------- eras
#: Era token (CLI ``--era`` value) -> taxonomy era-group (SPEC §7 / entity_spine).
ERA_GROUP = {
    "1976_2026": es.MODC,   # independent Fed-direct re-derivation
    "1959_1975": es.MODL,   # derivation layer (their .dta -> published schema)
    "finhist": es.HIST,     # 1863-1941 derivation layer
}
ERA_TOKENS = tuple(ERA_GROUP)  # fixed, deterministic order

#: Per-era cell-level validation key (SPEC §6.1). Modern eras align on the natural key
#: ``(id_rssd, period_end)`` (present in both the CLV .dta and call_report_filings);
#: finhist aligns on the persistent HIST charter key ``hist_panel_key`` (= bank_id) x year
#: (the delivered HIST panel keys on bank_id; 07 ``xtset bank_id quarter``).
ERA_KEY = {
    "1976_2026": list(es.ALIGNMENT_KEY),   # ("id_rssd", "period_end")
    "1959_1975": list(es.ALIGNMENT_KEY),   # ("id_rssd", "period_end")
    "finhist": ["bank_id", "year"],
}

#: The honest derivability-boundary paragraph per era (RECONSTRUCTION_SPEC.md §0), emitted
#: verbatim in each report so a claim can never outrun the boundary.
BOUNDARY = {
    "1976_2026": (
        "1976-2026 is a TRUE independent re-derivation from Fed-direct raw MDRM "
        "(`call_report_filings`, Chicago Fed + FFIEC CDR). The `securities` series carries "
        "a documented ~94% public-data ceiling pre-1994 (the raw-MDRM build lives in the "
        "un-shipped `3-create-variables.do`); those cells are pre-registered NOT-DERIVABLE, "
        "reported honestly and never imputed (SPEC §0, §2.6)."
    ),
    "1959_1975": (
        "1959Q4-1975Q4 is a DERIVATION-LAYER reconstruction: their digitized `.dta` is the "
        "only machine source, and our open code re-runs their documented 04/05/07 method. "
        "Because we run their formula on their input, near-perfect agreement is the bar "
        "(gate 99.9%). No step fabricates a value (SPEC §0)."
    ),
    "finhist": (
        "1863-1941 (finhist) is a DERIVATION-LAYER reconstruction from `historical-call.dta` "
        "(their OCC OCR) to the published derivation. The OCR itself is NOT-DERIVABLE "
        "(physical archives); 1942-1958 is a genuine gap, kept absent, never synthetically "
        "filled (SPEC §0)."
    ),
}

#: Shipped copy of the reason registry (repo-self-contained; canonical twin lives in the
#: spec dir, mirroring the variable_map SHIPPED/SPEC arrangement).
_HERE = Path(__file__).resolve().parent
SHIPPED_REASONS = _HERE / "divergence_reasons.csv"
SPEC_REASONS = Path(
    os.environ.get("FREENIC_TECHNICAL", "Technical") + "/reconstruction_spec/divergence_reasons.csv"
)

#: Registry column contract. The 8th column ``predicate`` (SPEC §10.4, added 2026-07-15) is blank
#: for the period-window rows and carries a predicate token (e.g. ``ZERO_VS_NULL``) for
#: value-shape rows that apply across all variables via :data:`_PREDICATES`.
_REASON_COLUMNS = (
    "reason_id", "variable", "era", "klass", "period_start", "period_end", "reason", "cite",
    "predicate",
)
#: Documented-class precedence within the registry (SPEC §7 order).
_REGISTERED_ORDER = (tx.VINTAGE, tx.METHOD_CHOICE, tx.NOT_DERIVABLE)

#: Wildcard variable token: a registry row with ``variable == "*"`` applies to EVERY scoped variable.
_WILDCARD_VARIABLE = "*"

#: Registry predicate tokens (SPEC §10.4). A predicate row matches a cell on the SHAPE of its two
#: values rather than a (variable, period) window. ``""`` == no predicate (the classic period-window
#: row). ``ZERO_VS_NULL`` == exactly one side is the float 0.0 and the other side is absent (NULL/NaN),
#: symmetric in both sidednesses — the CLV dense-zero-fill vs FreeNIC sparse-MDRM-NULL encoding fork.
_PREDICATES = ("", "ZERO_VS_NULL")


def _zero_vs_null_mask(pub, blt) -> np.ndarray:
    """Boolean mask for the ``ZERO_VS_NULL`` predicate (SPEC §10.4), symmetric + value-only.

    True where exactly one side is the float ``0.0`` and the other side is absent (NaN):
    ``(published == 0.0 AND built is NULL) OR (built == 0.0 AND published is NULL)``. Coerces both
    sides to float64 with NaN for missing — the same missing-semantics as :func:`taxonomy.classify`.
    Never true for a two-sided cell (both present) — those keep their numeric verdict.
    """
    p = pd.to_numeric(pd.Series(pub), errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    b = pd.to_numeric(pd.Series(blt), errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    p_missing, b_missing = np.isnan(p), np.isnan(b)
    return ((p == 0.0) & b_missing) | ((b == 0.0) & p_missing)


# =========================================================================== ULP
def units_last_digit(published) -> float:
    """Place value of the published value's least-significant displayed digit (its ULP).

    ROUNDING (SPEC §7) is ``|delta| <= 0.5 * units-of-last-digit``; the ULP is a property of
    how the *published* reference is expressed, so it is derived from that value's decimal
    form — deterministically, with no tunable constant. An integer-valued number (any
    magnitude, e.g. dollars) has its last digit in the units place -> ULP 1.0; a value shown
    to k decimals -> ULP ``10**-k`` (e.g. 1.23 -> 0.01).

    Missing/non-finite published -> 1.0 (irrelevant: a missing side is handled by the
    missing-branch of :func:`taxonomy.classify` before ULP is consulted).
    """
    if published is None:
        return 1.0
    try:
        if pd.isna(published):
            return 1.0
    except (TypeError, ValueError):
        pass
    d = Decimal(str(float(published))).normalize()
    exp = d.as_tuple().exponent
    if exp >= 0:            # integer-valued (incl. trailing-zero magnitudes) -> units place
        return 1.0
    return float(Decimal(1).scaleb(exp))   # 10**exp, e.g. -2 -> 0.01


def units_last_digit_vec(published) -> np.ndarray:
    """Vectorised :func:`units_last_digit` over a whole column.

    Elementwise-identical to :func:`units_last_digit` by construction: it evaluates the
    scalar function on the **distinct** published values only, then maps the results back —
    the ULP is a structural place-value, so distinct values share a ULP and there is no
    logic drift. This exists because the G-MATCH runs are tens of millions of cells and a
    per-cell ``Decimal`` round-trip is the cost; the arithmetic is unchanged.

    Returns a ``float64`` ndarray of ULPs (1.0 for missing/non-finite, matching the scalar).
    """
    vals = pd.to_numeric(pd.Series(published), errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    out = np.ones(vals.shape[0], dtype="float64")
    finite = np.isfinite(vals)
    if not finite.any():
        return out
    uniq, inv = np.unique(vals[finite], return_inverse=True)
    ulp_uniq = np.fromiter((units_last_digit(float(u)) for u in uniq), dtype="float64", count=uniq.shape[0])
    out[finite] = ulp_uniq[inv]
    return out


# =============================================================== reason registry
def load_reasons(path: Optional[Path | str] = None, *, validate: bool = True) -> pd.DataFrame:
    """Load the pre-registered divergence-reason registry (``divergence_reasons.csv``).

    Default: the shipped copy. Every row pins a documented class
    (VINTAGE / METHOD-CHOICE / NOT-DERIVABLE) to a (variable, era[, period-window]) case with
    a stable ``reason_id`` and a spec cite — the only channel by which a cell may leave the
    UNEXPLAINED bucket without an arithmetic match.
    """
    csv_path = Path(path) if path is not None else SHIPPED_REASONS
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    if validate:
        validate_reasons(df)
    return df


def validate_reasons(df: pd.DataFrame) -> None:
    """Validate the registry schema + value contract. Raises ValueError.

    Checks: exact column set/order; non-empty ``reason_id``/``variable``/``era``; unique
    ``reason_id``; ``klass`` in the three REGISTERED_CLASSES; ``era`` in the era tokens or
    ``combined``. This is the gate that keeps a stray or mis-classed reason out.
    """
    cols = tuple(df.columns)
    if cols != _REASON_COLUMNS:
        raise ValueError(
            f"divergence_reasons columns mismatch.\n  expected: {_REASON_COLUMNS}\n  got:      {cols}"
        )
    for col in ("reason_id", "variable", "era", "klass"):
        blank = df[col].astype(str).str.strip().eq("")
        if blank.any():
            raise ValueError(f"{blank.sum()} registry row(s) have empty '{col}'")
    dups = df["reason_id"][df["reason_id"].duplicated()].tolist()
    if dups:
        raise ValueError(f"duplicate reason_id(s): {sorted(set(dups))}")
    bad_klass = set(df["klass"].unique()) - set(tx.REGISTERED_CLASSES)
    if bad_klass:
        raise ValueError(
            f"registry klass must be one of {sorted(tx.REGISTERED_CLASSES)}; found {sorted(bad_klass)}"
        )
    allowed_era = set(ERA_TOKENS) | {"combined"}
    bad_era = set(df["era"].unique()) - allowed_era
    if bad_era:
        raise ValueError(f"registry era must be in {sorted(allowed_era)}; found {sorted(bad_era)}")
    bad_pred = set(df["predicate"].unique()) - set(_PREDICATES)
    if bad_pred:
        raise ValueError(f"registry predicate must be in {sorted(_PREDICATES)}; found {sorted(bad_pred)}")
    # A predicate row applies by value-shape across all variables -> it MUST use the wildcard variable
    # (and carries no period window; the predicate is its whole scope). Guard both invariants.
    pred_rows = df[df["predicate"].astype(str).str.strip() != ""]
    bad_wild = pred_rows[pred_rows["variable"] != _WILDCARD_VARIABLE]
    if not bad_wild.empty:
        raise ValueError(
            f"predicate row(s) must use variable '{_WILDCARD_VARIABLE}': "
            f"{bad_wild['reason_id'].tolist()}"
        )


def _parse_bound(bound: str, era: str):
    """Parse a registry period bound into the era's period type (date | year int)."""
    if bound is None or str(bound).strip() == "":
        return None
    if era == "finhist":
        return int(str(bound).strip())
    return pd.Timestamp(str(bound).strip())


def _period_value(raw, era):
    """Normalize a cell's period value to the era's comparable type (Timestamp | int)."""
    if era == "finhist":
        return int(raw)
    return pd.Timestamp(raw)


def reasons_for_era(reasons: pd.DataFrame, era: str) -> pd.DataFrame:
    """Registry rows applicable to ``era`` (its own token OR ``combined``), sorted so the first
    matching row wins deterministically.

    Ordering (SPEC §7 + §10.4): **specific variable-window rows first, wildcard/predicate rows last**
    (``_wild`` sort key), then SPEC §7 documented-class precedence (VINTAGE→METHOD-CHOICE→NOT-DERIVABLE),
    then variable, then reason_id. Applying the ``MC_ZEROFILL_ENCODING`` wildcard predicate LAST is what
    keeps a more-specific pre-registered boundary (e.g. securities-pre-1994 NOT-DERIVABLE) winning over
    the generic 0-vs-NULL class for a cell that satisfies both.
    """
    sub = reasons[reasons["era"].isin([era, "combined"])].copy()
    order = {k: i for i, k in enumerate(_REGISTERED_ORDER)}
    sub["_ord"] = sub["klass"].map(order)
    sub["_wild"] = ((sub["variable"] == _WILDCARD_VARIABLE)
                    | (sub["predicate"].astype(str).str.strip() != "")).astype(int)
    return sub.sort_values(["_wild", "_ord", "variable", "reason_id"]).reset_index(drop=True)


def match_reason(era_reasons: pd.DataFrame, variable: str, period, era: str,
                 published=None, built=None):
    """First registered (klass, reason_id) whose scope covers this cell.

    A row's scope is EITHER a ``(variable, period-window)`` window (blank ``predicate``) OR a
    value-shape ``predicate`` (SPEC §10.4). ``variable == "*"`` is a wildcard matching every variable.
    Period window is ``[period_start, period_end)`` (start inclusive, end exclusive); a blank bound is
    unbounded. Predicate rows consult ``published``/``built`` (the two cell values). Rows are consulted
    in :func:`reasons_for_era` order (specific first, wildcard/predicate last). Returns ``(None, None)``
    when no reason is registered — the cell then stays UNEXPLAINED (SPEC §7: no post-hoc relabelling).
    """
    cand = era_reasons[(era_reasons["variable"] == variable)
                       | (era_reasons["variable"] == _WILDCARD_VARIABLE)]
    if cand.empty:
        return None, None
    pval = None if period is None or (isinstance(period, float) and pd.isna(period)) else _period_value(period, era)
    for row in cand.itertuples(index=False):
        predicate = str(getattr(row, "predicate", "")).strip()
        if predicate:
            if predicate == "ZERO_VS_NULL":
                if _zero_vs_null_mask([published], [built])[0]:
                    return row.klass, row.reason_id
            continue  # predicate not satisfied -> this row does not cover the cell
        start = _parse_bound(row.period_start, era)
        end = _parse_bound(row.period_end, era)
        if (start is not None or end is not None) and pval is None:
            continue  # a period-scoped reason cannot cover a cell with no period
        if start is not None and pval < start:
            continue
        if end is not None and pval >= end:
            continue
        return row.klass, row.reason_id
    return None, None


# ================================================================= panel + align
def load_panel(path: Path | str) -> pd.DataFrame:
    """Load a panel from parquet (published or built)."""
    return pd.read_parquet(Path(path))


def _normalize_keys(df: pd.DataFrame, era: str) -> pd.DataFrame:
    """Validate the era's key columns are present and normalize their dtypes for a clean
    align. Modern eras route through :func:`entity_spine.alignment_key` (raises if a key
    column is absent); finhist normalizes the charter via :func:`entity_spine.hist_panel_key`.
    """
    df = df.copy()
    key = ERA_KEY[era]
    if era == "finhist":
        missing = [c for c in key if c not in df.columns]
        if missing:
            raise KeyError(f"finhist key column(s) absent: {missing}; have {list(df.columns)}")
        df["bank_id"] = es.hist_panel_key(df["bank_id"])
        df["year"] = df["year"].astype("Int64")
    else:
        es.alignment_key(df)  # validation side-effect: raises KeyError on a missing key col
        df["id_rssd"] = df["id_rssd"].astype("Int64")
        df["period_end"] = pd.to_datetime(df["period_end"])
    return df


def align_cells(published: pd.DataFrame, built: pd.DataFrame, era: str,
                scoped_vars: set) -> pd.DataFrame:
    """Long-form (key..., variable, published, built) frame over the scoped-variable cell
    universe = {cells where published or built is present}.

    An outer merge on ``key + variable`` makes a key or a variable present in only one panel
    surface as a one-sided cell (missing on the other side) — the honest coverage-gap
    representation. Cells absent from both panels never enter the frame.
    """
    key = ERA_KEY[era]
    pub = _normalize_keys(published, era)
    blt = _normalize_keys(built, era)

    pub_vars = [c for c in pub.columns if c not in key and c in scoped_vars]
    blt_vars = [c for c in blt.columns if c not in key and c in scoped_vars]

    pub_long = pub.melt(id_vars=key, value_vars=pub_vars,
                        var_name="variable", value_name="published")
    blt_long = blt.melt(id_vars=key, value_vars=blt_vars,
                        var_name="variable", value_name="built")

    merged = pub_long.merge(blt_long, on=key + ["variable"], how="outer")
    # drop cells absent from BOTH panels (neither published nor built present)
    merged = merged[~(merged["published"].isna() & merged["built"].isna())].copy()
    return merged.sort_values(key + ["variable"]).reset_index(drop=True)


def classify_frame(cells: pd.DataFrame, era: str, reasons: pd.DataFrame) -> pd.DataFrame:
    """Add ``class`` + ``reason_id`` to the aligned cell frame (SPEC §7 first-match precedence).

    Per cell: the arithmetic verdict from :func:`taxonomy.classify_vec` decides EXACT/ROUNDING/
    TOLERANCE first; only a non-match cell consults the registry for a documented class; a
    non-match cell with no registered reason is UNEXPLAINED.

    Vectorised (plan Batch-4 handoff): the arithmetic verdict is one
    :func:`taxonomy.classify_vec` call over the whole column (identical to the per-cell
    :func:`taxonomy.classify` — proven on a 100k-cell sample in the test suite), and the
    registry is applied by iterating the **tiny** era-reason table (a handful of rows) with
    vectorised masks in the exact SPEC §7 first-match order, NOT by looping over the tens of
    millions of cells. No classification policy changes.
    """
    era_reasons = reasons_for_era(reasons, era)
    key = ERA_KEY[era]
    period_col = key[1]

    n = len(cells)
    pub = cells["published"]
    blt = cells["built"]
    ulp = units_last_digit_vec(pub)
    classes = tx.classify_vec(pub, blt, ulp)               # arithmetic verdict (no registration)
    reason_ids = np.array([""] * n, dtype=object)

    # Only non-arithmetic-match cells (== UNEXPLAINED here) may take a documented class, and
    # only via a pre-registered reason key. First-match precedence: era_reasons is already
    # sorted (variable, SPEC-§7 class order, reason_id); assign only where not yet assigned.
    open_mask = ~np.isin(classes, list(tx.MATCH_CLASSES))  # non-match cells (arithmetic wins first)
    if open_mask.any() and not era_reasons.empty:
        variables = cells["variable"].to_numpy(dtype=object)
        zvn = _zero_vs_null_mask(pub, blt)                 # SPEC §10.4 predicate mask (value-shape)
        if era == "finhist":
            period_num = pd.to_numeric(cells[period_col], errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
            period_has = np.isfinite(period_num)
        else:
            period_ts = pd.to_datetime(cells[period_col], errors="coerce")
            period_has = period_ts.notna().to_numpy()
        for row in era_reasons.itertuples(index=False):
            predicate = str(getattr(row, "predicate", "")).strip()
            # variable scope: exact match OR the wildcard '*' (SPEC §10.4 applies to all variables)
            var_m = (variables == row.variable)
            if row.variable == _WILDCARD_VARIABLE:
                var_m = np.ones(n, dtype=bool)
            m = open_mask & (reason_ids == "") & var_m
            if not m.any():
                continue
            if predicate:
                # value-shape predicate row (no period window). Only ZERO_VS_NULL is defined.
                if predicate == "ZERO_VS_NULL":
                    m = m & zvn
                else:  # pragma: no cover - guarded by validate_reasons
                    continue
            else:
                start = _parse_bound(row.period_start, era)
                end = _parse_bound(row.period_end, era)
                if start is not None or end is not None:
                    # a period-scoped reason cannot cover a cell with no period (mirrors match_reason)
                    m = m & period_has
                    if era == "finhist":
                        if start is not None:
                            m = m & (period_num >= float(int(start)))
                        if end is not None:
                            m = m & (period_num < float(int(end)))
                    else:
                        if start is not None:
                            m = m & (period_ts >= start).to_numpy()
                        if end is not None:
                            m = m & (period_ts < end).to_numpy()
            if m.any():
                classes[m] = row.klass                     # == tx.classify(..., registered_class=klass)
                reason_ids[m] = row.reason_id

    out = cells.copy()
    out["class"] = classes
    out["reason_id"] = reason_ids
    return out


# ================================================================= coverage/gate
def coverage_matrix(classified: pd.DataFrame) -> pd.DataFrame:
    """Per-variable coverage matrix: published / attempted / per-class / matched counts.

    * ``published`` — cells with a published (reference) value present.
    * ``attempted`` — cells with a built value present (a coverage measure, not a match).
    * one column per taxonomy class + ``matched`` (EXACT+ROUNDING+TOLERANCE).
    Sorted by variable; a ``TOTAL`` row is appended.
    """
    rows = []
    for variable, grp in classified.groupby("variable", sort=True):
        counts = grp["class"].value_counts().to_dict()
        row = {"variable": variable,
               "published": int(grp["published"].notna().sum()),
               "attempted": int(grp["built"].notna().sum())}
        for c in tx.ALL_CLASSES:
            row[c] = int(counts.get(c, 0))
        row["matched"] = sum(int(counts.get(c, 0)) for c in tx.MATCH_CLASSES)
        rows.append(row)
    cov = pd.DataFrame(rows).sort_values("variable").reset_index(drop=True)
    total = {"variable": "TOTAL",
             "published": int(cov["published"].sum()) if not cov.empty else 0,
             "attempted": int(cov["attempted"].sum()) if not cov.empty else 0}
    for c in tx.ALL_CLASSES:
        total[c] = int(cov[c].sum()) if not cov.empty else 0
    total["matched"] = int(cov["matched"].sum()) if not cov.empty else 0
    cov = pd.concat([cov, pd.DataFrame([total])], ignore_index=True)
    return cov


def gate_result(classified: pd.DataFrame, era: str) -> dict:
    """Compute the D2 gate verdict + shares for an era from the classified cells.

    The verdict is :func:`taxonomy.passes_gate` (NOT-DERIVABLE excluded from the
    denominator; matched share >= era threshold AND unexplained share <= floor). Shares are
    reported on the same derivable denominator.
    """
    era_group = ERA_GROUP[era]
    class_counts = {c: int((classified["class"] == c).sum()) for c in tx.ALL_CLASSES}
    total = sum(class_counts.values())
    not_deriv = class_counts[tx.NOT_DERIVABLE]
    derivable = total - not_deriv
    matched = sum(class_counts[c] for c in tx.MATCH_CLASSES)
    unexplained = class_counts[tx.UNEXPLAINED]
    match_share = (matched / derivable) if derivable > 0 else 0.0
    unexplained_share = (unexplained / derivable) if derivable > 0 else 0.0
    verdict = tx.passes_gate(class_counts, era_group)
    return {
        "campaign": CAMPAIGN,
        "era": era,
        "era_group": era_group,
        "validation_key": ERA_KEY[era],
        "gate_threshold": tx.gate_for_era(era_group),
        "unexplained_floor": tx.UNEXPLAINED_FLOOR,
        "class_counts": class_counts,
        "total_cells": total,
        "derivable_cells": derivable,
        "not_derivable_cells": not_deriv,
        "matched_cells": matched,
        "match_share": match_share,
        "unexplained_cells": unexplained,
        "unexplained_share": unexplained_share,
        "published_cells": int(classified["published"].notna().sum()),
        "attempted_cells": int(classified["built"].notna().sum()),
        "verdict": "PASS" if verdict else "FAIL",
    }


# ======================================================================= reports
def _fmt_pct(x: float) -> str:
    return f"{x * 100:.4f}%"


def render_report(era: str, cov: pd.DataFrame, gate: dict) -> str:
    """Render RECONSTRUCTION_REPORT_<era>.md (coverage matrix + gate verdict + boundary)."""
    era_group = gate["era_group"]
    lines: list[str] = []
    lines.append(f"# Reconstruction validation report — era `{era}` ({era_group})")
    lines.append("")
    lines.append(f"**Campaign:** {CAMPAIGN}  ")
    lines.append(f"**Validation key:** `{tuple(gate['validation_key'])}`  ")
    lines.append(
        f"**Pre-registered gate (SPEC §7 / D2):** matched share "
        f"(EXACT+ROUNDING+TOLERANCE) >= {_fmt_pct(gate['gate_threshold'])} "
        f"AND UNEXPLAINED share <= {_fmt_pct(gate['unexplained_floor'])} "
        f"(NOT-DERIVABLE excluded from the denominator)."
    )
    lines.append("")

    # --- coverage matrix
    lines.append("## Coverage matrix (per scoped variable)")
    lines.append("")
    cols = (["variable", "published", "attempted", "matched"]
            + list(tx.ALL_CLASSES))
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    lines.append(header)
    lines.append(sep)
    # iterrows (not itertuples): class labels contain hyphens (METHOD-CHOICE / NOT-DERIVABLE)
    # which are not valid Python identifiers and would be mangled by itertuples.
    for _, row in cov.iterrows():
        d = row.to_dict()
        lines.append("| " + " | ".join(str(d[c]) for c in cols) + " |")
    lines.append("")

    # --- verdict
    lines.append("## D2 gate verdict")
    lines.append("")
    lines.append(f"- Cells (total / derivable / NOT-DERIVABLE): "
                 f"{gate['total_cells']} / {gate['derivable_cells']} / {gate['not_derivable_cells']}")
    lines.append(f"- Matched (EXACT+ROUNDING+TOLERANCE): {gate['matched_cells']} "
                 f"= **{_fmt_pct(gate['match_share'])}** of derivable "
                 f"(gate {_fmt_pct(gate['gate_threshold'])})")
    lines.append(f"- UNEXPLAINED: {gate['unexplained_cells']} "
                 f"= **{_fmt_pct(gate['unexplained_share'])}** of derivable "
                 f"(floor {_fmt_pct(gate['unexplained_floor'])})")
    lines.append(f"- **VERDICT: {gate['verdict']}**")
    lines.append("")

    # --- honest boundary
    lines.append("## Honest derivability boundary")
    lines.append("")
    lines.append(BOUNDARY[era])
    lines.append("")
    if gate["unexplained_cells"] > 0 and gate["verdict"] == "FAIL":
        lines.append(
            "> Every UNEXPLAINED cell above the floor blocks G-MATCH. Investigate each: "
            "reclassify with a pre-registered reason key, or report it honestly and hold the "
            "claim. No UNEXPLAINED cell is silently absorbed into a documented class (SPEC §7)."
        )
        lines.append("")
    return "\n".join(lines)


def write_outputs(classified: pd.DataFrame, era: str, out_dir: Path) -> dict:
    """Write reconciliation_<era>.parquet, RECONSTRUCTION_REPORT_<era>.md, gate_result_<era>.json.

    Returns the gate dict. Reconciliation columns: key..., variable, published, built, class,
    reason_id — deterministically sorted by (key..., variable).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    key = ERA_KEY[era]
    recon = classified.loc[:, key + ["variable", "published", "built", "class", "reason_id"]]
    recon = recon.sort_values(key + ["variable"]).reset_index(drop=True)
    recon.to_parquet(out_dir / f"reconciliation_{era}.parquet", index=False)

    cov = coverage_matrix(classified)
    gate = gate_result(classified, era)
    (out_dir / f"RECONSTRUCTION_REPORT_{era}.md").write_text(
        render_report(era, cov, gate), encoding="utf-8")
    (out_dir / f"gate_result_{era}.json").write_text(
        json.dumps(gate, indent=2, sort_keys=True), encoding="utf-8")
    return gate


def run_era(era: str, published: Path, built: Path, out_dir: Path,
            reasons_path: Optional[Path] = None,
            variable_map_path: Optional[Path] = None) -> dict:
    """Full single-era harness: load -> align -> classify -> emit. Returns the gate dict."""
    if era not in ERA_GROUP:
        raise ValueError(f"unknown era {era!r}; expected one of {list(ERA_GROUP)}")
    vmap = vm.load_variable_map(variable_map_path)
    scoped_vars = set(vm.scoped(vmap)["variable"])
    reasons = load_reasons(reasons_path)

    pub = load_panel(published)
    blt = load_panel(built)
    cells = align_cells(pub, blt, era, scoped_vars)
    classified = classify_frame(cells, era, reasons)
    return write_outputs(classified, era, out_dir)


# ======================================================================= combine
def combine_reports(out_dir: Path) -> str:
    """Roll the three per-era gate_result_<era>.json in ``out_dir`` into RECONSTRUCTION_REPORT.md.

    Eras are emitted in the fixed :data:`ERA_TOKENS` order. Missing era files are reported as
    absent (never silently treated as passing).
    """
    lines: list[str] = ["# Reconstruction validation report (combined)", "",
                        f"**Campaign:** {CAMPAIGN}", ""]
    lines.append("| era | era_group | key | matched | match_share | unexplained_share | verdict |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    all_pass = True
    for era in ERA_TOKENS:
        gpath = out_dir / f"gate_result_{era}.json"
        if not gpath.exists():
            lines.append(f"| {era} | {ERA_GROUP[era]} | — | — | — | — | **ABSENT** |")
            all_pass = False
            continue
        g = json.loads(gpath.read_text(encoding="utf-8"))
        lines.append(
            f"| {era} | {g['era_group']} | `{tuple(g['validation_key'])}` | "
            f"{g['matched_cells']} | {_fmt_pct(g['match_share'])} | "
            f"{_fmt_pct(g['unexplained_share'])} | **{g['verdict']}** |"
        )
        all_pass = all_pass and g["verdict"] == "PASS"
    lines.append("")
    lines.append(f"## Overall: {'ALL ERAS PASS' if all_pass else 'NOT ALL ERAS PASS'}")
    lines.append("")
    for era in ERA_TOKENS:
        lines.append(f"### {era} boundary")
        lines.append("")
        lines.append(BOUNDARY[era])
        lines.append("")
    report = "\n".join(lines)
    (out_dir / "RECONSTRUCTION_REPORT.md").write_text(report, encoding="utf-8")
    return report


# =========================================================================== CLI
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="validate_reconstruction.py",
        description="Validate a reconstructed Luck/finhist panel against the published panel "
                    "(the perfect reverse engineer). Pre-registered taxonomy; no tunable knobs.",
    )
    p.add_argument("--era", choices=list(ERA_GROUP),
                   help="reconstruction era to validate")
    p.add_argument("--published", type=Path, help="path to the published panel (parquet)")
    p.add_argument("--built", type=Path, help="path to the built/reconstructed panel (parquet)")
    p.add_argument("--out", type=Path, required=True, help="output directory")
    p.add_argument("--reasons", type=Path, default=None,
                   help="override the divergence-reasons registry CSV (default: shipped copy)")
    p.add_argument("--variable-map", type=Path, default=None,
                   help="override the variable_map CSV (default: shipped copy)")
    p.add_argument("--combine", action="store_true",
                   help="roll existing per-era gate_result_*.json in --out into RECONSTRUCTION_REPORT.md")
    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.combine:
        combine_reports(args.out)
        print(f"[validate_reconstruction] combined report -> {args.out / 'RECONSTRUCTION_REPORT.md'}")
        return 0
    missing = [n for n in ("era", "published", "built")
               if getattr(args, n if n != "era" else "era") is None]
    if missing:
        build_parser().error("--era, --published and --built are required (or use --combine)")
    gate = run_era(args.era, args.published, args.built, args.out,
                   reasons_path=args.reasons, variable_map_path=args.variable_map)
    print(f"[validate_reconstruction] era={gate['era']} verdict={gate['verdict']} "
          f"match_share={_fmt_pct(gate['match_share'])} -> {args.out}")
    return 0 if gate["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
