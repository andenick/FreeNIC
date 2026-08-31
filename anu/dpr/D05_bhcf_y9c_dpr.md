# D05: BHCF / FR Y-9C (bank holding company financials) — Data Provenance Record

## What this covers
FR Y-9C consolidated financial statements for bank holding companies:
`bhcf_filings`, 208M `(BHC, quarter, item)` observations, 1986Q3–2025Q4.

## Source
- **Name**: FFIEC bulk data — FR Y-9C (BHCF)
- **URL**: https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx (BHCF
  product); reporting page https://www.ffiec.gov/npw/FinancialReport/ReturnY9C
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-01-26 (release v1.1.0, vintage 2026Q1)
- **Format**: caret-delimited TXT (2000–2025, 104 files); CSV (pre-2000
  vintage, 1986–1999)
- **API key**: none

## Construction method
1. Phase 04 reads each caret-delimited TXT with DuckDB and unpivots the
   variable-code columns to long format.
2. Phase 05 ingests the pre-2000 CSV vintage into the same long schema.

## Transformations applied
- `delimited_read`, `wide_to_long` — verbatim values.

## Known issues
- BHCF is the **trailing product** in the quarterly refresh (~1 quarter
  behind Call Reports); the served table ends 2025Q4.
- The pre-2000 CSV vintage is a historical FFIEC/FRB distribution — place
  the files under `anu/data/raw/bhcf_csv_pre2000/` (see L03).

## Validation
V01: manifest row parity (208,147,772 rows); phase 06's TXT/ZIP consistency
check runs in-pipeline.
