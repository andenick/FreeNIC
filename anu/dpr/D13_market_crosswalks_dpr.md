# D13: Market crosswalks (CRSP-FRB, SEC EDGAR, HMDA, GLEIF) — Data Provenance Record

## What this covers
- `crsp_mapping` (18,908 rows) — PERMCO↔RSSD linking table (1971–2024).
- `sec_cik_crosswalk` (371 rows) — SEC CIK identity for bank/BHC filers.
- `hmda_summary` (208,302 rows) — CFPB HMDA institution×year mortgage
  summary, keyed by LEI at (lei, activity_year, loan_purpose).
- `id_crosswalk` (103,037 rows) — the unified identifier crosswalk, LEI
  gap-filled from GLEIF (see D14 for the derived-family view).

## Source
| Table | Source | URL | Access |
|---|---|---|---|
| crsp_mapping | NY Fed CRSP-FRB link table | https://www.newyorkfed.org/research/banking_research/datasets.html | public |
| sec_cik_crosswalk | SEC EDGAR structured data (submissions + XBRL frames) | https://data.sec.gov/ | public API |
| hmda_summary | CFPB HMDA Data Browser API | https://ffiec.cfpb.gov/data-browser/ | public API |
| id_crosswalk (LEI fill) | GLEIF Level-1 golden copy (US/ACTIVE) | https://www.gleif.org/en/lei-data/gleif-golden-copy | public, CC BY 4.0 |

- **Retrieved**: CRSP 2026-03-11; SEC/HMDA/GLEIF 2026-06-30 (release v1.1.0)
- **Format**: CSV (CRSP, GLEIF); JSON API (SEC, HMDA)

## Construction method
- Phase 03 loads the 16 CRSP mapping CSVs (notice/copyright rows dropped).
- Phase 34 queries data.sec.gov (SIC-filtered submissions + XBRL frames) to
  build the CIK crosswalk. NOTE: www.sec.gov is Akamai-blocked for bulk
  robots; data.sec.gov structured endpoints work.
- Phase 35 pulls filers + per-LEI loan-purpose aggregations from the HMDA
  Data Browser API — a SUMMARY, transcribed verbatim, not the full LAR.
- Phase 36b fills missing LEIs in `id_crosswalk` via unambiguous
  normalized-name match against GLEIF US/ACTIVE (source-tagged `gleif`;
  existing NIC/HMDA LEIs never overwritten).

## Transformations applied
- `csv_load`, `api_query`, `sic_filter`, `api_aggregation`,
  `name_match_fill` (deterministic normalization shared with the NIC side to
  prevent drift).

## Known issues
- **CRSP ships the link table only** — CRSP market data itself is
  proprietary and is NOT in FreeNIC.
- HMDA summary covers 2022–2023 and is adjacent to (not part of) the
  call-report core.
- SEC crosswalk is identity + a coarse size hint, not financials.

## Validation
V01: manifest row parity for all tables.
