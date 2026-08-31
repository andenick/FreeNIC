# D02: FDIC Summary of Deposits (SOD) — Data Provenance Record

## What this covers
Branch-level deposit records from the FDIC's annual Summary of Deposits
survey, 1994–2025. Table: `fdic_sod` (2,815,984 rows).

## Source
- **Name**: FDIC BankFind Suite API — SOD endpoint
- **URL**: https://banks.data.fdic.gov/api/sod
- **License**: US federal government work (public domain)
- **Retrieved**: 2025-10-31 (2025 survey; release v1.1.0, vintage 2026Q1)
- **Format**: JSON (paginated, limit=10000)
- **API key**: none required

## Construction method
1. Phase 18 downloads all pages (cached as `fdic_sod/page_NNNN.json`).
2. Phase 19 flattens the pages to one row per branch-year record.

## Transformations applied
- `paginated_download`, `json_flatten` — verbatim values, no imputation.

## Known issues
- Annual survey cadence: the served table ends at the latest published
  survey year (2025).

## Validation
V01: manifest row parity for `fdic_sod.parquet`.
