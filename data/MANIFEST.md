# Data Manifest — FreeNIC inputs

FreeNIC is built entirely from **public US banking regulatory data**. The published
Parquet/DuckDB outputs are self-contained — you only need the files below if you want
to **re-run the ingestion pipeline** yourself.

Each ingestion script first looks for its source under `Inputs/<source>/`. If that is
absent, it falls back to `$DATA_ROOT/<source>/` (see the README "## Setup"). Place the
files under whichever root you prefer.

## Required inputs by ingestion phase

| Phase script | Source dir (under `Inputs/` or `$DATA_ROOT/`) | Files | Public source |
|---|---|---|---|
| 01 | `ffiec_bulk_bhcf/` | `MDRM_CSV.csv` + BHCF TXT | [Fed MDRM](https://www.federalreserve.gov/apps/mdrm/) · [FFIEC CDR](https://cdr.ffiec.gov/public/) |
| 02 | `nic_attributes/` | NIC institution attribute CSVs | [FFIEC NIC](https://www.ffiec.gov/NPW/) |
| 03 | `crsp_frb_link/` | CRSP-FRB PERMCO link | [NY Fed datasets](https://www.newyorkfed.org/research/banking_research/datasets.html) |
| 04–05 | `ffiec_bulk_bhcf/`, `bhcf_csv_pre2000/` | Y-9C TXT/CSV | [FFIEC CDR](https://cdr.ffiec.gov/public/) |
| 07 | `chicago_fed_call_reports/` | call report XPT | [Chicago Fed](https://www.chicagofed.org/banking/financial-institution-reports/commercial-bank-data) |
| 07d/07e | `cdr_call_bulk/` | FFIEC CDR Single-Period bulk ZIPs | [FFIEC CDR bulk](https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx) |
| 08 | `luck_database/` | Luck Historical Database | [NBER w29557](https://www.nber.org/papers/w29557) (academic request) |
| 09 | `luck_database/occ_historical/`, `clv_historical_call/` | OCC historical balance sheets | [OCC Annual Reports](https://www.occ.treas.gov/publications-and-resources/publications/annual-report/index-annual-report.html) |
| 16–19 | `fdic_failures_api.json`, `fdic_financials/`, `fdic_sod/`, `fdic_history/` | FDIC SDI/failures/SOD/history | [FDIC BankFind](https://banks.data.fdic.gov/) |
| 23 | `dfast/` | DFAST stress-test results | [Fed DFAST](https://www.federalreserve.gov/supervisionreg/dfast.htm) |
| 24 | `filing_instructions/` | Pillar 3 disclosure PDFs/CSVs | Bank investor-relations pages |
| 27 | `fred_h8/` (auto-downloaded) | FRED H.8 + macro series | [FRED](https://fred.stlouisfed.org/) (keyless CSV) |
| 28 | `failing_banks/FAILING_BANKS/` | `combined_data.csv`, `deposits_before_failure_{historical,modern}.csv` | [Failing Banks DB](https://github.com/andenick/failing-banks) |
| 29 | `catalogs/` | `bank_identifier_crosswalk.csv`, `bhc_hierarchy.csv`, `sector_groupings.csv` | Derived (NIC structure + Failing Banks ↔ RSSD ↔ FDIC cert) |
| 30 (stress) | `stress_scenarios/` | `2026_Proposed_*_{Domestic,International}.csv` | [Fed supervisory scenarios](https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm) |
| 32 | `cdr_raw/` (auto-downloaded) | FFIEC CDR Single-Period ZIPs | [FFIEC CDR bulk](https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx) |

## Derived outputs

Phases 30–33 write feature panels (`public_luck_panel.parquet`,
`sdi_feature_panel.parquet`, `cdr_unrealized_2019_2025.parquet`) to `$OUTPUT_ROOT/`
and register `fdic_sdi_features` / `cdr_unrealized_losses` tables in the DuckDB.

## Notes

- All sources are public. The Luck Historical Database requires a free academic data
  request; everything else is openly downloadable.
- No API key is required for any current download path.
- Raw inputs are large (~tens of GB) and are intentionally **not** committed; download
  them yourself from the links above.
