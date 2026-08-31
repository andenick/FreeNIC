# D08: FRED banking & macro series (H.8 + context) — Data Provenance Record

## What this covers
`fred_series` — 1.35M observations of Federal Reserve H.8 aggregate banking
statistics (bank credit, loans by type, securities, deposits), key policy
and market rates, and macro context (real GDP, unemployment, CPI, industrial
production).

## Source
Two tiers:
1. **Keyless tier** (15 aggregate series): `fredgraph.csv` per series —
   https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}
2. **Full H.8 release** (~1,938 series, disaggregated by bank size/type —
   large-domestic / small-domestic / foreign-related / domestically
   chartered): FRED API release 22 — https://api.stlouisfed.org/fred
   (free API key required: https://fred.stlouisfed.org/docs/api/api_key.html)

- **License**: US federal government work (public domain)
- **Retrieved**: 2026-05-31 (release v1.1.0, vintage 2026Q1)
- **Format**: CSV (keyless tier); JSON (API tier, cached per series)

## Construction method
1. Phase 27 downloads the 15 keyless CSVs (loader `L05` mirrors this
   exactly) and loads them into one long table.
2. Phase 27b pages the full H.8 release through the API (key read from the
   `FRED_API_KEY` environment variable — never committed), caching each
   series' observations so the run is idempotent and resumable, and appends
   to the same long table.

## Transformations applied
- `csv_download`, `api_pagination`, `append_long` — values verbatim from
  FRED; no seasonal adjustment or unit conversion applied by FreeNIC.

## Known issues
- Units and frequency vary by series (`USD billions`, `percent`, `index`;
  weekly/monthly/quarterly/daily). The per-series metadata lives in the
  table itself — there is deliberately no single forced unit.
- The full H.8 tier does not regenerate without an API key (free).

## Validation
V01: manifest row parity (1,345,207 rows).
