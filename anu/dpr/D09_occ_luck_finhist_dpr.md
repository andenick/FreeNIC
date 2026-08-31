# D09: OCC Annual Reports + Luck historical database + finhist — Data Provenance Record

## What this covers
The pre-1976 historical backbone of the warehouse:
- `occ_historical` (17.8M rows) — digitized OCC Annual Report national-bank
  condition statements, 1863–1941.
- `occ_historical_clv` (8.0M rows) — the Correia-Luck-Verner public
  "finhist" vintage of the same OCC source, full span, penny-exact verified
  against the TSV vintage.
- `luck_call_reports` (37.8M rows) — the Luck historical call-report core,
  1959Q4–1975Q4 (deduplicated from the 311.8M-row raw source).

## Source
| Input | Publisher / access | URL |
|---|---|---|
| `call-reports-{balance-sheets,income-statements}-Jan2026.dta` | Correia-Luck-Verner public dataset (FRBNY distribution; authors' replication files) — **public** | https://www.newyorkfed.org/research/banking_research/datasets.html |
| `occ-balance-sheets-tsv` + YAML label maps + report dates | digitized OCC Annual Reports, distributed inside the Luck historical database files — **public with the database** | https://www.occ.gov/about/what-we-do/hist-publications/hist-publications-index.html |
| `historical-call.dta` | finhist — Correia-Luck-Verner historical call reports, Harvard Dataverse — **public, CC BY 4.0** | https://doi.org/10.7910/DVN/Q22XR1 (https://finhist.com) |

- **Retrieved**: 2026-03-11 (release v1.1.0, vintage 2026Q1)
- **Format**: Stata DTA; TSV + YAML documentation

## Construction method
1. Phase 08 loads the Luck DTA files (id_rssd + quarter-start dates);
   quarter-start dates are converted to quarter-end keys. Phase 08b then
   deduplicates to the 1959Q4–1975Q4 core plus Fed-absent gap-fill
   (311.8M → 37.8M rows).
2. Phase 09 loads the OCC TSV (111K rows × 116 cols) with DuckDB's native
   reader, unpivots wide-to-long, maps variable names via the YAML label
   files, and maps years to actual report dates via `report_dates.tsv`.
3. Phase 09b loads the finhist DTA wide, as the CLV-published schema,
   alongside the TSV vintage (Wave-15A verification: penny-exact value
   match, identical bank_id scheme, matching report dates).

## Transformations applied
- `dta_load`, `tsv_load`, `wide_to_long`, `label_map`, `date_map`,
  `quarter_end_conversion`, `dedup_core`. Era units preserved as digitized
  (see the YAML label maps for definitions).

## Known issues
- The Luck DTA source spans 1959–2023; the served table is the slimmed core.
- These are bulk historical files with no single keyless URL — the loader
  (`L06`) gates on their presence and points at the publisher URLs above.

## Validation
V01: manifest row parity for all three tables; in-pipeline, phase 13 runs
date/null checks and the reconstruction layer (D15) reconciles the finhist
vintage cell-by-cell.
