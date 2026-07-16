"""FreeNIC reconstruction module — Luck / finhist from-raw construction, verified.

This package produces Luck-equivalent and finhist-equivalent panels **from raw FreeNIC
data** and proves equivalence against the published datasets cell-by-cell (the "perfect
reverse engineer"). It ships as part of ``andenick/FreeNIC`` v1.1.0.

See ``README.md`` (this directory) for the derivability-boundary table, the D3 citation
posture, and the mandatory data-provenance citation block. The human spec is
``RECONSTRUCTION_SPEC.md`` (working copy in
``Technical/reconstruction_spec/``); its machine twin is
``variable_map.csv`` (shipped alongside this package).

Citation posture (D3, LICENSE_POSTURE.md §2b): every module here is **original Python
implementing CLV's documented methodology**, with per-function citations to their
do-file loci (e.g. "implements 05 L66-77"). No CLV do-file code is reproduced.

Batch-1 scaffold (this batch) provides the shared foundations the era builders reuse:

  * :mod:`variable_map`  — load/validate the machine-readable spec, scope filter.
  * :mod:`entity_spine`  — era-aware entity keys (HIST OCC charter+version; MODL
    FDIC-cert + ``-id_rssd`` fallback; MODC RSSD-native), append-not-join invariant,
    and the ``(id_rssd, period_end)`` validation alignment key.
  * :mod:`taxonomy`      — the pre-registered divergence classifier
    (EXACT/ROUNDING/TOLERANCE/VINTAGE/METHOD-CHOICE/NOT-DERIVABLE/UNEXPLAINED) with the
    D2 thresholds as hard constants.

The era builders (build_luck_equivalent / build_luck_core / build_finhist_equivalent),
the combined analysis panel, and the validation harness (validate_reconstruction) land
in later batches and import these foundations.

No module in this package writes to the warehouse. All functions are pure over pandas
DataFrames / DuckDB relations.
"""

from __future__ import annotations

from . import entity_spine, taxonomy, variable_map

__all__ = ["entity_spine", "taxonomy", "variable_map"]

__version__ = "1.1.0"
