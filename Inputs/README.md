# freenic Inputs

Read-only source data for the freenic banking regulatory database. Do not modify files here.

## Directory Structure

| Directory | Contents | Script |
|-----------|----------|--------|
| `ffiec_bulk_bhcf/` | BHCF caret-delimited TXT files (FR Y-9C 2000-2025) + MDRM dictionary | 01, 04 |
| `bhcf_csv_pre2000/` | BHCF CSV files (1986Q3-1999Q4) + alternate MDRM version | 05 |
| `nic_attributes/` | NIC institution/relationship/transformation CSV files | 02 |
| `chicago_fed_call_reports/` | SAS XPT transport files (call reports 1976-2002) | 07 |
| `crsp_frb_link/` | CRSP-FRB link CSV vintages (16 files, 2008-2024) | 03 |
| `luck_database/` | Luck Database Stata DTA + OCC historical TSV (1867-2025) | 08, 09 |
| `dfast/` | Federal Reserve DFAST stress test CSV (2013-2025) | 23 |
| `fdic_financials/` | FDIC SDI financials JSON (1984-2025) | 17 |
| `fdic_sod/` | FDIC Summary of Deposits JSON (1994-2025) | 18, 19 |
| `fdic_history/` | FDIC institution history JSON (all dates) | 25 |
| `fred_h8/` | FRED banking + macro CSV series (1954-2025) | 27 |
| `filing_instructions/` | GS filings + filing instruction PDFs | — |
| `fdic_failures_api.json` | FDIC bank failures JSON (1934-2026) | 16 |

## Conventions

- All paths are defined centrally in `Technical/freenic_ingestion/scripts/utils.py` via `INPUT_PATHS`
- Directories renamed from date-prefixed names to descriptive names in Session 7
- FDIC API data cached as paginated JSON; `_DOWNLOAD_COMPLETE` marker indicates full download
- `combined.json` files aggregate page files for ingestion
