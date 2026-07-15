# FreeNIC Changelog

## v1.0.0 — 2026-07-14

FreeNIC's first semantic **v1.0.0** public release.

### Served release
- **61 files**: 60 base-table Parquet exports + the 163-year (1863–2026)
  bank-aggregate spine (`long_bank_aggregates_1863_2026.parquet`).
- Built from **warehouse build 1.4**, data vintage **2026Q1**.
- Every served Parquet's row count equals its warehouse source table's row
  count (G2 row-parity gate: 61/61 mapped files match).

### Lineage
- **Draft era** — internal warehouse construction; pre-public parquet snapshots.
- **50 tables** — first broad parquet export set.
- **61 files (2026-07-14)** — scope settled at 60 base tables + the spine, served
  on data.freenic.org.
- **v1.0.0** — this release: artifacts (release_manifest.json, SHA256SUMS.txt,
  codebook/, data_dictionary.csv, croissant.jsonld, CITATION.cff, LICENSE)
  regenerated deterministically from warehouse build 1.4 (2026Q1).

### Scope decisions
- `freenic_t` tentative tier is **excluded** from v1.0.0 (roadmap item; D1).
- Public **v1.0.0** is the version string everywhere; the underlying warehouse
  build (1.4) is recorded here in the changelog only (D2).

### Data license
- Compilation under **CC-BY-4.0** (E-3 provisional); code under MIT. Upstream
  per-source terms and required citations: DATA_LICENSE.md + PROVENANCE.csv.
