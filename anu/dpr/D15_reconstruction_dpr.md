# D15: Reconstruction layer (Luck / finhist rebuilds + reconciliation) — Data Provenance Record

## What this covers
The v1.1.0 reconstruction layer, served under `reconstruction/`:
- `luck_core_1959_1975.parquet` (601,566 rows) — Luck-era core rebuilt from
  raw public sources. Gate: **PASS**.
- `luck_equivalent_1976_2026.parquet` (2,026,104 rows) — modern-era
  Luck-equivalent rebuilt from CDR Call Reports. Pre-registered verdict:
  **FAIL** at the strictest tier (documented divergence).
- `finhist_equivalent_1863_1941.parquet` (367,312 rows) — OCC-era rebuild.
  Gate: **PASS**.
- `reconciliation_1976_2026.parquet` (40,261,405 rows),
  `reconciliation_1959_1975.parquet` (7,470,087 rows),
  `reconciliation_finhist.parquet` (2,632,440 rows) — cell-level
  reconstructed-vs-published comparisons with divergence reasons.

## Source
- **Name**: FreeNIC reconstruction module, rebuilt from the public raw
  sources of D03/D09
- **URL**: https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction
- **License**: MIT (method); rebuilt values derive from public-domain
  sources
- **Retrieved**: 2026-07-15 (release v1.1.0)

## Construction method
`pipeline/reconstruction/` is the verified engine: entity spine construction,
variable mapping (`variable_map.csv`), gmatch joining
(`run_gmatch_modern_real.py`), and the builders
(`build_luck_core.py`, `build_luck_equivalent.py`,
`build_finhist_equivalent.py`). Wrappers: phase 50 (Luck) and phase 51
(finhist). Validation (`validate_reconstruction.py`) emits the gate JSONs
and the reconciliation panels; phase 52 checks the warehouse integration
and anchor cells.

## Transformations applied
- `entity_spine`, `variable_map`, `gmatch`, `cell_reconciliation` — the
  divergence-reason taxonomy lives in `divergence_reasons.csv` and the
  human spec in `RECONSTRUCTION_SPEC.md`.

## Known issues — the honest record
- The modern-era (1976–2026) reconstruction **pre-registered FAIL**: at the
  strictest tier the public CDR sources do not reproduce the published Luck
  values exactly. This is recorded, quantified (40.3M reconciliation cells
  with reasons), and published — v1.1.0 adds the capability and its
  validation record; it does not convert the FAIL into a PASS. See
  `pipeline/reconstruction/reports/` (tri-engine V1 and adversarial V2
  reviews) for the full adjudication.

## Validation
V01: manifest row parity for all six files. In-pipeline: phase 52 gates
(3 tables == reconciliation parquets, anchor-cell checks).
