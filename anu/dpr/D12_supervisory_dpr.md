# D12: Supervisory stress data (DFAST, scenarios, Pillar 3) — Data Provenance Record

## What this covers
- `dfast_results` (28,231 rows) — Dodd-Frank Act Stress Test results,
  2013–2025: capital ratios, loan losses, revenue/income projections under
  stress for the 22–43 largest BHCs per exercise.
- `stress_scenarios` / `_domestic` / `_international` (200/226/226 rows) —
  supervisory scenario definitions (historic actuals, baseline, severely
  adverse macro paths).
- `pillar3_disclosures` (8,653 rows) — Basel III Pillar 3 disclosures
  (capital, RWA, ratios, SLR, TLAC) for 5 G-SIBs, 2024Q1–2025Q3.

## Source
| Table | Source | URL | Access |
|---|---|---|---|
| dfast_results | Federal Reserve DFAST published results | https://www.federalreserve.gov/supervisionreg/dfast-archive.htm | public CSV |
| stress_scenarios* | Federal Reserve supervisory scenarios | https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm | public CSV |
| pillar3_disclosures | G-SIB investor-relations Pillar 3 documents (JPM, BAC, WFC, C, MS) | per-bank IR pages; framework at https://www.bis.org/bcbs/pillar3.htm | **manual** |

- **License**: US federal government work (public domain) for the Fed
  tables; bank disclosures are public documents © their publishers.
- **Retrieved**: DFAST 2025-06-30; scenarios 2025-02-28; Pillar 3
  2025-11-30 (release v1.1.0)
- **Format**: CSV (Fed); PDF/pages transcribed to CSV (Pillar 3)

## Construction method
- Phase 23 loads the cumulative DFAST results CSV.
- Phase 30 harmonizes the six published scenario CSVs into one table plus
  the domestic/international blocks.
- Phase 24 parses the transcribed Pillar 3 CSVs.

## Transformations applied
- `csv_load`, `harmonize` (scenarios); `manual_transcription` +
  `csv_parse` (Pillar 3).

## Known issues — the honest one
- **Pillar 3 is a hand-collected layer.** There is no bulk download for
  bank Pillar 3 disclosures; the values were transcribed from the five
  banks' published disclosure documents into CSVs before ingestion. A
  regenerator re-collects them from the banks' IR pages (the framework
  reference above) — the transcription step is manual by nature, and the
  CSVs' provenance is recorded in the pipeline.

## Validation
V01: manifest row parity for all five tables.
