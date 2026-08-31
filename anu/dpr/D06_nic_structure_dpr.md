# D06: FFIEC NIC structure data + FR Y-15 — Data Provenance Record

## What this covers
The entity dimension of the warehouse from the FFIEC National Information
Center: `institutions` and `institution_attributes` (217K entities, active +
closed), `branches` (173K), `relationships` (286K), `transformations`
(58.9K), `nic_entity_identifiers` (103K — the authoritative Fed
multi-regulator identifier crosswalk), `nic_attributes_ext` (220K —
geography/charter extension), and FR Y-15 systemic indicators
`y15_systemic_indicators` (22.5K, 2020Q4–2024Q4).

## Source
- **Name**: FFIEC National Information Center data downloads
- **URL**: https://www.ffiec.gov/npw/FinancialReport/DataDownload
  (CSV_ATTRIBUTES_ACTIVE/CLOSED/BRANCHES, CSV_RELATIONSHIPS,
  CSV_TRANSFORMATIONS — 74-column vintage);
  FR Y-15 snapshots: https://www.ffiec.gov/npw/FinancialReport/FRY15Reports
- **License**: US federal government work (public domain)
- **Retrieved**: 2026-05-29 (Y-15: 2025-12-31; release v1.1.0)
- **Format**: CSV (attribute files); CSV snapshots (Y-15)
- **API key**: none. Note: the Y-15 *listing page* is JS-gated — the
  canonical acquirer (07h) drives a headed browser; the static CSV assets
  themselves download directly.

## Construction method
1. Phase 02 loads the attribute CSVs (DuckDB native reader), unioning
   ACTIVE + CLOSED.
2. Phase 37 harvests the identifier columns into the canonical crosswalk.
3. Phase 37b harvests the remaining high-value columns (geography, charter
   codes) additively.
4. Phase 07h acquires the Y-15 snapshot CSVs; phase 41 ingests them.

## Transformations applied
- `csv_load`, `active_closed_union`, `column_harvest` — verbatim values.

## Known issues
- FR Y-9LP has **no bulk product** and is intentionally absent.
- Attribute sets are current snapshots plus closed-entity history; the
  1782 start date in coverage reflects the earliest charter dates carried
  in the history tables, not NIC's own launch.

## Validation
V01: manifest row parity for all eight tables.
