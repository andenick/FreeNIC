# FreeNIC Quarterly Refresh Protocol

FreeNIC tracks the FFIEC reporting calendar. Each quarter's Call/UBPR/FDIC-SDI/BHCF/NCUA
data is published on a lag and folded into the warehouse with the ingestion scripts in
`pipeline/scripts/`. This document is the operator checklist; the machine-readable ledger of
what has and has not been done per quarter lives in `pipeline/REFRESH_STATE.json`.

## When a new quarter is ready

- A quarter (period-end `YYYY-03-31`, `-06-30`, `-09-30`, `-12-31`) publishes **~75 days
  after quarter-end**. Do not start earlier — the FFIEC CDR bulk service will not yet offer it.
- **Lag rule.** Call / UBPR / FDIC-SDI lead. **FR Y-9C / BHCF (`bhcf_filings`) trails ~1
  quarter.** Acquire whatever is published, mark the trailing product `pending` in
  `REFRESH_STATE.json`, and collect it the following cycle.

## Steps (run from `pipeline/scripts/`)

Pass the **8-digit** period-end date (e.g. `20260630`), never a bare year.

1. **Acquire.** `python 07d_acquire_cdr_call_bulk.py 20260630` and
   `python 07g_acquire_ubpr.py 20260630`.
2. **Ingest.** `07e_ingest_call_reports_cdr.py`, `39_ingest_ubpr.py`, plus the per-source
   loaders for any other product published this quarter (FDIC, NCUA, H.8, etc.). Loaders are
   idempotent — they skip already-loaded periods.
3. **Validate.** `13_validate.py` (the read-only gate) must be green, then `pytest tests/ -q`.
4. **Export parity.** Re-export the changed Parquet tables and refresh `SHA256SUMS.txt` /
   `PROVENANCE.csv`. Every served Parquet's row count must equal its warehouse source table's.
5. **Dictionary.** Run the `bank-data-dictionary` quarterly refresh (`--dry-run` first, then
   the real run) so the taxonomy cycle advances to the new period; re-pin FreeNIC's `dict`
   tables to the new dictionary release.
6. **Views + coverage.** `14 → 15 → 16 → 17`; `16_coverage_audit.py` must print `PASS`.
7. **Republish (operator-gated).** Rebuild the served slice with
   `release-tools/build_slice.py`, regenerate the counts/manifest with
   `release-tools/make_freenic_counts.py`, and sync the parquet release + site per
   `site/DATA_SERVING.md`.
8. **Close out.** Flip the quarter's stages to `done` in `REFRESH_STATE.json`.

## Expected volumes (2026Q1 precedent)

- New Call ZIP ~5 MB; new UBPR ZIP ~100 MB.
- Call adds ~3.2M rows to `call_report_filings` (one new quarter).
- Re-exporting the billion-row tables to Parquet is slow (budget ~1.5 h for a large add).
- The dictionary side is append-only/idempotent — usually a handful of taxonomy edits.

## Configuration

The ingestion scripts read their build-host locations from environment variables so the
pipeline is host-agnostic:

| Variable | Purpose | Default |
|---|---|---|
| `FREENIC_OUTPUTS` | warehouse export dir (`parquet/`, `SHA256SUMS.txt`, `PROVENANCE.csv`) | `Outputs` |
| `FREENIC_INPUTS` | raw acquisition cache | `Inputs` |
| `FREENIC_WAREHOUSE` | warehouse DuckDB file | `$FREENIC_OUTPUTS/freenic.duckdb` |
| `FREENIC_SITE_DIR` | runnable site app (for `build_slice`/`build_content`) | `../site` |
| `BANK_DATA_DICTIONARY_REPO` | local checkout of the public `bank-data-dictionary` | — |
| `FRED_API_KEY` | FRED API key for the H.8 disaggregated release (phase 27b) | — |

## Roadmap items (not blockers for a quarter's core ingest)

- **FR Y-9LP / Y-9SP** parent-only reports — FreeNIC 1.1.
- The `freenic_t` tentative tier — excluded from 1.0.0 (roadmap).
