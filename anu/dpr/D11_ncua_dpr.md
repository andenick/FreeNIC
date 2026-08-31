# D11: NCUA credit-union call reports — Data Provenance Record

## What this covers
- `ncua_5300` (1,180,127,221 rows) — Form 5300 credit-union call reports,
  1994Q1–2025Q4, parsed to long `(CU, quarter, account)` observations.
- `ncua_cu_directory` (851,288 rows) — credit-union directory records.

## Source
- **Name**: NCUA credit union call report data (quarterly bulk ZIPs)
- **URL**: https://www.ncua.gov/analysis/credit-union-corporate-call-report-data
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-04-30 (release v1.1.0, vintage 2026Q1)
- **Format**: ZIP (per-quarter bulk) + FOICU directory
- **API key**: none

## Construction method
Phase 26 parses the quarterly bulk ZIPs to long format and loads the
directory layer, exporting both tables' Parquets directly.

## Transformations applied
- `zip_extract`, `wide_to_long` — verbatim reported values.

## Known issues
- **Scope expansion, separate universe**: NCUA regulates credit unions — a
  DISTINCT institution universe keyed by NCUA CU_NUMBER, not RSSD or FDIC
  cert (FOICU carries an RSSD column where one exists). These tables are
  additive and must NOT be unioned with bank tables on identifier columns.
- The second-largest table in the warehouse after Call Reports — the bulk
  ZIPs are multi-hundred-MB downloads.

## Validation
V01: manifest row parity for both tables.
