# D01: FDIC BankFind Suite (failures, financials, history) — Data Provenance Record

## What this covers
The FDIC-served layer of FreeNIC: every failed bank (1934–2026), quarterly
SDI financials for every FDIC-insured institution (1984–2026), and the full
institution event history (1782–2026). Tables: `bank_failures` (4,115 rows),
`fdic_financials` (69.5M), `fdic_history` (582K).

## Source
- **Name**: FDIC BankFind Suite API (Statistics on Depository Institutions)
- **URL**: https://api.fdic.gov/banks/failures · /financials · /history
  (SOD endpoint under https://banks.data.fdic.gov/api/sod — see D02)
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-05-27 (failures, history); 2026-04-30 (financials) —
  release v1.1.0, data vintage 2026Q1
- **Format**: JSON (paginated, limit=10000, offset pagination)
- **API key**: none required

## Construction method
1. Fetcher (`anu/scripts/L01_fetch_fdic.py`) pulls each endpoint with
   offset pagination into `anu/data/raw/` (failures as one JSON; financials
   and history as page caches).
2. Phase 16 flattens the failures JSON to one row per failure event.
3. Phase 17 concatenates the financials pages, loads them with DuckDB's
   native JSON reader, and SQL-unpivots the wide institution-quarter records
   to long `(cert, period, variable, value)`.
4. Phase 25 flattens the history JSON to one row per event.

## Transformations applied
- `json_flatten` (failures, history): nested API records → flat rows.
- `json_concat` + `wide_to_long` (financials): 168 pages → single long table.
- No filtering, no imputation, no unit conversion — verbatim API values.

## Known issues
- The API is live: a re-fetch after the 2026Q1 vintage returns newer counts
  (the vintage released in v1.1.0 froze 4,115 failures; the live API grows).
- SDI variable units vary per item; consult the FDIC SDI codebook per
  variable (the warehouse carries variable names verbatim).

## Validation
V01 checks: table present in release manifest with exact row parity;
bank_failures spot check (failure years within 1934–2026, count > 0).
