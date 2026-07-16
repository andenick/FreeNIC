"""Loader + validator for the machine-readable reconstruction spec (``variable_map.csv``).

``variable_map.csv`` is the machine twin of RECONSTRUCTION_SPEC.md: one row per
(variable, era) with its source, formula id, do-file citation, confidence, and v1.1
scope flag. This module loads it, validates its schema, and exposes the scoped view the
builders consume.

SHIPPED COPY / SYNC NOTE
------------------------
The canonical, working copy of this CSV lives in the spec dir::

    Technical/reconstruction_spec/variable_map.csv

A copy is shipped **inside this module** (``pipeline/reconstruction/variable_map.csv``)
so the open-source repo is self-contained. Until v1.1.0 ships, the spec-dir copy is
canonical (the R2 author + G-SPEC adversarial checker edit it there); this shipped copy
must be re-synced from it before release. :func:`assert_in_sync` performs that check.
Keep them byte-identical; do not hand-edit the shipped copy.

Citation posture (D3): original code; the CSV's own ``dofile_cite`` column carries the
per-formula do-file loci — no CLV code is reproduced.

Runtime deps: pandas only. No warehouse access.
"""

from __future__ import annotations
import os

from pathlib import Path
from typing import Optional

import pandas as pd

#: This module's directory.
_HERE = Path(__file__).resolve().parent

#: The shipped copy (canonical for the repo/release).
SHIPPED_CSV = _HERE / "variable_map.csv"

#: The working canonical copy in the spec dir (authoritative until v1.1.0 ships).
SPEC_CSV = Path(
    os.environ.get("FREENIC_TECHNICAL", "Technical") + "/reconstruction_spec/variable_map.csv"
)

#: Required columns, in order (the CSV header contract). SPEC §R2 / §9.
REQUIRED_COLUMNS = (
    "variable",       # luck variable / concept name
    "era",            # era window this row applies to (e.g. 1976-2026, 1863-1941, combined)
    "source_kind",    # how the value is obtained (see SOURCE_KINDS)
    "source_ref",     # the concrete source (MDRM recipe / .dta column / occ item / formula)
    "formula_id",     # stable id for the formula (e.g. F_assets_mod)
    "dofile_cite",    # do-file locus / dictionary row / builder cite (the citation, D3)
    "confidence",     # exact | probable | inferred (see CONFIDENCE_CLASSES)
    "scope_v11",      # TRUE = in v1.1 core-first scope; FALSE = deferred to v1.2
)

#: The confidence classes the spec uses (RECONSTRUCTION_SPEC.md §9 / §R2 precedence).
#: 'inferred' means NOT literally in a cited source — labelled, never presented as verbatim.
CONFIDENCE_CLASSES = frozenset({"exact", "probable", "inferred"})

#: The source_kind vocabulary observed/allowed in the map (RECONSTRUCTION_SPEC.md §1-§6).
SOURCE_KINDS = frozenset({
    "mdrm_fed_direct",    # 1976+ Fed-direct MDRM recipe (cf(...) etc.)
    "dta_column",         # read directly from the CLV .dta (MODL 1959-75)
    "occ_line_item",      # HIST OCC historical line item
    "reconstructed_agg",  # HIST egen-rowtotal reconstruction (04)
    "derived_ratio",      # 07 derived ratio on the combined+deflated panel
    "entity_rule",        # panel-construction rule (spine/failure/dedup/filter)
    "deflator",           # CPI deflator treatment
    "not_derivable",      # outside the boundary (SPEC §0)
})


def load_variable_map(path: Optional[Path | str] = None, *, validate: bool = True) -> pd.DataFrame:
    """Load the variable map CSV into a DataFrame.

    Parameters
    ----------
    path:
        CSV to load. Default: the module's :data:`SHIPPED_CSV`. Pass :data:`SPEC_CSV`
        to load the working canonical copy.
    validate:
        Run :func:`validate_schema` after loading (default True).

    Returns
    -------
    DataFrame with exactly :data:`REQUIRED_COLUMNS` (string dtype; ``scope_v11`` kept as
    the raw 'TRUE'/'FALSE' string — use :func:`scoped` for the boolean filter). The CSV
    is parsed with the stdlib CSV rules (quoted commas inside ``dofile_cite`` are
    honoured), NOT naive splitting.
    """
    csv_path = Path(path) if path is not None else SHIPPED_CSV
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    if validate:
        validate_schema(df)
    return df


def validate_schema(df: pd.DataFrame) -> None:
    """Validate the loaded map against the column + value contract. Raises ValueError.

    Checks: exact column set/order; non-empty ``variable``/``era``/``formula_id``;
    ``confidence`` in :data:`CONFIDENCE_CLASSES`; ``source_kind`` in :data:`SOURCE_KINDS`;
    ``scope_v11`` in {TRUE, FALSE}. This is the schema gate the builders rely on.
    """
    cols = tuple(df.columns)
    if cols != REQUIRED_COLUMNS:
        raise ValueError(
            f"variable_map columns mismatch.\n  expected: {REQUIRED_COLUMNS}\n  got:      {cols}"
        )
    for col in ("variable", "era", "formula_id"):
        blank = df[col].astype(str).str.strip().eq("")
        if blank.any():
            raise ValueError(f"{blank.sum()} row(s) have empty '{col}' (rows {list(df.index[blank])})")

    bad_conf = set(df["confidence"].unique()) - CONFIDENCE_CLASSES
    if bad_conf:
        raise ValueError(f"unknown confidence class(es): {sorted(bad_conf)}; allowed {sorted(CONFIDENCE_CLASSES)}")

    bad_kind = set(df["source_kind"].unique()) - SOURCE_KINDS
    if bad_kind:
        raise ValueError(f"unknown source_kind(s): {sorted(bad_kind)}; allowed {sorted(SOURCE_KINDS)}")

    bad_scope = set(df["scope_v11"].unique()) - {"TRUE", "FALSE"}
    if bad_scope:
        raise ValueError(f"scope_v11 must be TRUE/FALSE; found {sorted(bad_scope)}")


def scoped(df: pd.DataFrame, *, in_scope: bool = True) -> pd.DataFrame:
    """Filter to the v1.1 scope (``scope_v11 == 'TRUE'`` by default). SPEC §D1 core-first."""
    want = "TRUE" if in_scope else "FALSE"
    return df[df["scope_v11"] == want].copy()


def confidence_counts(df: pd.DataFrame) -> dict:
    """Return a {confidence_class: count} dict (honest exact/probable/inferred ledger). SPEC §9."""
    return df["confidence"].value_counts().to_dict()


def assert_in_sync(shipped: Path = SHIPPED_CSV, spec: Path = SPEC_CSV) -> None:
    """Assert the shipped copy is byte-identical to the spec-dir canonical copy.

    Until v1.1.0 ships, the spec-dir copy is authoritative; call this before release
    (and in the release gate) to catch a stale shipped copy. Raises AssertionError with
    a byte-count diagnostic; if the spec copy is absent (e.g. running from a clean repo
    clone with no workspace), it is a no-op with no error.
    """
    if not Path(spec).exists():
        return  # spec dir not present (clean clone) — nothing to reconcile against
    a = Path(shipped).read_bytes()
    b = Path(spec).read_bytes()
    if a != b:
        raise AssertionError(
            f"shipped variable_map.csv ({len(a)} bytes) != spec-dir canonical "
            f"({len(b)} bytes); re-sync {shipped} from {spec} before release"
        )
