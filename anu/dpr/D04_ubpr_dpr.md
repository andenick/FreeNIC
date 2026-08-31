# D04: FFIEC UBPR (ratios, peer statistics, ranks) + unrealized-losses layer — Data Provenance Record

## What this covers
The Uniform Bank Performance Report family: per-institution ratios
(`ubpr_ratios`, 1.25B rows), peer-group percentile statistics
(`ubpr_peer_stats`, 22.1M), per-bank peer ranks (`ubpr_peer_rank`, 250M),
and the focused AFS/HTM unrealized-losses layer (`cdr_unrealized_losses`,
46.9K).

## Source
- **Name**: FFIEC Central Data Repository public bulk downloads
- **URL**: https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx
  - UBPR Ratio — Single Period (tab-delimited ZIP per quarter)
  - UBPR Rank / Peer Stats — Four Periods (XBRL ZIP per year)
  - Call Report schedules (RC-B/RC/RC-E) for the unrealized-losses layer
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-03-31 (release v1.1.0, vintage 2026Q1)
- **Format**: tab-delimited ZIPs; XBRL (per-bank XML) ZIPs
- **API key**: none; the download UI is a Telerik RadAjax flow driven by the
  canonical acquirers (07g/07i/32) with Playwright

## Construction method
1. Phase 07g acquires per-quarter UBPR ZIPs; phase 39 ingests them long.
2. Phase 07i acquires per-year Rank/Stats XBRL ZIPs; phase 42 parses and
   ingests both products.
3. Phase 32 acquires the Call Report bulk schedules; phase 33 parses
   RC-B/RC/RC-E line items into the unrealized-losses layer.

## Transformations applied
- `zip_extract`, `wide_to_long`, `xbrl_parse`, `schedule_parse` — verbatim
  published values.

## Known issues
- UBPR coverage starts 2002Q4 in the served table.
- The unrealized-losses layer covers 2019Q4–2025Q4.

## Validation
V01: manifest row parity for all four tables.
