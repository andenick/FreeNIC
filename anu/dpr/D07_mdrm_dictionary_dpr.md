# D07: MDRM variable dictionary — Data Provenance Record

## What this covers
`mdrm` — the Federal Reserve Micro Data Reference Manual as ingested here:
87,351 reporting-item definitions (codes, titles, descriptions) that key
every Call Report / Y-9C variable in the warehouse.

## Source
- **Name**: Federal Reserve MDRM (CSV distribution via FFIEC bulk products)
- **URL**: https://www.federalreserve.gov/apps/mdrm/
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-01-26 (release v1.1.0, vintage 2026Q1)
- **Format**: CSV (`MDRM_CSV.csv`) with a "PUBLIC" header line, quoted
  fields, HTML entities in descriptions

## Construction method
Phase 01 parses the CSV (header line handled, HTML entities cleaned) into
the `mdrm` table. One row per MDRM item.

## Transformations applied
- `csv_clean` — text cleaning only; no content changes.

## Known issues
- The MDRM evolves with reporting-form revisions; the snapshot is pinned to
  the release vintage.

## Validation
V01: manifest row parity (87,351 rows).
