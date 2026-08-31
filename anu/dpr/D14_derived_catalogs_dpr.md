# D14: Derived panels, dictionary, and warehouse catalogs — Data Provenance Record

## What this covers
The FreeNIC-built layer: `clean_bank_panel`, `long_bank_aggregates_1863_2026`,
`entity_xref`, `id_crosswalk`, the 7 `dict_*` tables, the 6 `catalog_*`
tables, `freenic_manifest`, `filing_metadata`, `reporting_forms`,
`variable_crosswalk`, `fdic_sdi_features`, and `sector_groupings`.

## Source
- **Name**: FreeNIC derived (from the public sources in D01–D13); the
  dictionary tier re-pins the public `bank-data-dictionary`
- **URL**: https://github.com/andenick/FreeNIC (build) ·
  https://github.com/andenick/bank-data-dictionary (dictionary)
- **License**: MIT (FreeNIC build artifacts; compiled from public-domain
  sources)
- **Retrieved**: 2026-07-15 (release v1.1.0 build)

## Construction method
- **clean_bank_panel** (phase 45): from-raw rebuild over three strata —
  `occ_historical_clv` (1863–1941), Luck (1959–1975), scheduled Call Report
  items (1976–2026) — with nominal AND real (1990=100) USD levels.
  Deterministic/byte-stable; unit-gate verified against published anchors
  (JPM-2008 $1.7462T, SVB $209.0B, OCC-1929 $1.80B). Basis: finhist
  historical-call v2.10.0 (arXiv:2506.06082).
- **long_bank_aggregates** (staged by `release-tools/build_slice.py`): the
  163-year year×metric spine (810 rows) over OCC condition statements, FDIC
  HSOB, and modern Call Report aggregates, with definition toggles,
  source-series provenance, and junction flags at the 1896/1914/1934 regime
  joins.
- **dict_*** (phases 14/44): the pinned bank-data-dictionary release —
  schedule line-items, UBPR concepts, the variable→view access map, edit
  history, relationships.
- **catalog_*** (phases 10/46/47/49): self-describing warehouse catalogs —
  data-source registry, entity/filing coverage, schema evolution, variable
  lineage.
- **fdic_sdi_features** (phase 31): deterministic SQL feature build over
  `fdic_financials` (ratios, NIM/ROA, log age, F1/F3/F5 forward failure
  flags).
- **entity_xref / id_crosswalk** (phases 20b/36): cross-source entity
  resolution and identifier unification (GLEIF fill per D13).

## Transformations applied
- `real_deflation_1990_100`, `strata_union`, `unit_gate`,
  `aggregation`, `regime_join_annotation`, `entity_resolution`,
  `merge`, `catalog_build` — all deterministic; no synthetic values.

## Known issues
- `clean_bank_panel` is the recommended from-raw panel; the Failing Banks
  panel (D10) is the as-published alternative with uncalibrated absolute-$
  in some eras.
- Derived tables regenerate exactly; their upstream vintages govern their
  coverage.

## Validation
V01: manifest row parity; spot checks on `clean_bank_panel` (1863–2026 span,
non-empty) and `long_bank_aggregates` (810 rows, 1863–2026, no non-positive
`num_banks`).
