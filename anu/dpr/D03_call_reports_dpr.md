# D03: Consolidated Call Reports 1976–2026 — Data Provenance Record

## What this covers
The single largest table in the warehouse: `call_report_filings` — 1.92
billion `(institution, quarter, MDRM item)` observations spanning fifty
years of regulatory balance-sheet and income-statement filings.

## Source
Three vintages, harmonized to one long table:

| Span | Vintage | Acquisition | Access |
|---|---|---|---|
| 1976–2002 | Chicago Fed Commercial Bank Data (146 quarterly SAS XPT files, 2,800+ variables) | licensed FRB Chicago distribution | **restricted** — institutional/subscription product |
| 2012–2026 | FFIEC CDR public bulk — Call Reports Single Period (tab-delimited ZIP per quarter) | https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx | public, no auth (JS-driven bulk UI) |
| gap quarters | CDR bulk recovery pass | same | public |

- **License**: US federal government work (public domain) for the FFIEC/Fed
  data; the Chicago Fed historical product ships under its own distribution
  license.
- **Retrieved**: 2026-03-31 (release v1.1.0, data vintage 2026Q1)
- **Format**: SAS XPT (1976–2002); tab-delimited ZIPs (CDR)

## Construction method
1. Phase 07 reads each XPT with pyreadstat/DuckDB and unpivots the wide
   quarterly files to `(rssd, date, item, value)`; DATE floats
   (`YYYYMMDD`) are normalized and quarter-end keys derived.
2. Phase 07d acquires CDR ZIPs per period (Playwright drives the public
   bulk-download flow; no values are fabricated — see the script header).
3. Phase 07e ingests the CDR ZIPs; phase 07f recovers any missing quarters
   from CDR.
4. All tracks land in the same long schema keyed by
   `(rssd_id, period_end, mdrm_item)`.

## Transformations applied
- `xpt_read`, `zip_extract`, `wide_to_long` (≈2,800 columns → long),
  `period_keyed_merge` across vintages. No recomputation of source values.

## Known issues — honest reproduction ladder
- **The 1976–2002 XPT vintage is NOT a keyless public download.** A
  reproducer without the Chicago Fed product can still assemble:
  1959–1975 from the public Luck/finhist files (D09), 2001+ from FFIEC CDR
  bulk, and the `luck_call_reports`/`occ_historical_clv` public vintages.
  The 1976–2002 span as ingested here is the licensed distribution.
- Units vary by MDRM item (USD thousands for `$` items, counts, ratios);
  per-item definitions are in the `mdrm` table.

## Validation
V01: manifest row parity (1,917,025,977 rows) and warehouse COUNT(*) parity;
`catalog_filing_coverage` carries per-period coverage; phase 13's validation
gate runs date/null checks on the table in-pipeline.
