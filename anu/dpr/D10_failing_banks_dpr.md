# D10: Failing Banks panel (Correia-Luck-Verner repackaging) — Data Provenance Record

## What this covers
- `robin_panel_base` (2,867,936 rows) — annual panel of ALL US banks (failed
  + surviving), 1863–2024: 156 variables of financial data, failure
  indicators, macro context, computed ratios. Partially fills the 1905–1958
  coverage gap.
- `robin_deposits_historical` (2,961 rows) — pre-FDIC-era deposit dynamics.
- `robin_deposits_modern` (547 rows) — modern-era deposit run-up with run
  indicators.
- `robin_crosswalk` (14,287), `bhc_ownership` (36,668), `sector_groupings`
  (16,548) — identifier and structure catalogs from the same database.

## Source
- **Name**: Failing Banks database — the Correia-Luck-Verner panel
  repackaged in the public `failing-banks` repository
- **URL**: https://github.com/andenick/failing-banks
- **License**: MIT (the repository); the underlying authors' historical data
  is public (finhist, doi:10.7910/DVN/Q22XR1)
- **Retrieved**: 2026-05-19 (panel export v3.3; release v1.1.0)
- **Format**: CSV (`FAILING_BANKS/processed/*.csv`, catalog CSVs)
- **API key**: none

## Construction method
Phase 28 loads the three processed CSVs verbatim (no recomputation).
Phase 29 loads the identifier / BHC-hierarchy / sector catalogs.

## Transformations applied
- `csv_load` only — the panel's own construction (variable definitions,
  ratios, failure flags) is documented in the source repository.

## Known issues
- The processed CSVs are generated artifacts of the source repository: a
  regenerator clones `failing-banks` and runs its conversion scripts
  (`convert_data_simple.py`) against the CLV replication files, or obtains
  the processed export from the repository maintainer. Loader `L10` gates on
  the files and documents this path.
- Panel values are as published by the source database — FreeNIC does not
  recalibrate them (the from-raw alternative is `clean_bank_panel`, D14).

## Validation
V01: manifest row parity for all six tables.
