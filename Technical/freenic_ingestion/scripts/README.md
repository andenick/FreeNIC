# freenic Ingestion Scripts

## Execution Order

```
00_setup.py           Create empty database schema
01_ingest_mdrm.py     MDRM variable dictionary (87K codes)
02_ingest_attributes.py  NIC institutions, branches, relationships (217K entities)
03_ingest_crsp.py     CRSP-FRB PERMCO mapping (19K entries)
04_ingest_bhcf_txt.py    BHCF from TXT files (2000-2025, 104 files)
05_ingest_bhcf_csv.py    BHCF from CSV files (1986-1999, pre-2000)
06_verify_y9c.py      Verify Y-9C ZIP/TXT consistency (optional)
07_ingest_call_reports.py  Chicago Fed call reports (1976-2002, 146 XPT files)
08_ingest_luck.py     Luck Database call reports (1959-2025, 312M rows)
09_ingest_occ.py      OCC historical balance sheets (1867-1904, 9.8M rows)
10_build_catalog.py   Build variable catalog (9,375 variables)
11_build_views.py     Build 10 convenience views
12_export_parquet.py  Export 34 Parquet files (ZSTD, sorted)
13_validate.py        Extended validation (18 tables + G-SIB cross-check)
16_ingest_fdic_failures.py  FDIC bank failures (4,114 records, 1934-2026)
17_ingest_fdic_financials.py  FDIC SDI financials (69M rows, 1984-2025)
18_download_fdic_sod.py  Download FDIC SOD data
19_ingest_fdic_sod.py    Ingest FDIC SOD (2.7M branch records)
20_build_crosswalks.py   Variable crosswalk table (64+ entries)
23_ingest_dfast.py    DFAST stress test results (28K obs, 2013-2025)
24_ingest_pillar3.py  Pillar 3 disclosures (8K obs, 5 G-SIBs)
25_ingest_fdic_history.py  FDIC institution history (582K events)
27_ingest_fed_h8.py   FRED banking + macro series (75K obs, 15 series)
28_ingest_robin_panel.py  Failing Banks panel (2.87M obs, 1863-2024)
29_ingest_volcker_catalogs.py  Bank-identifier crosswalk, BHC hierarchy, sector groupings
30_ingest_stress_scenarios.py  Fed stress test scenario definitions (452 rows)
30_build_public_luck_panel.py  Public luck-equivalent panel builder (writes to OUTPUT_ROOT)
31_build_sdi_feature_panel.py  SDI feature panel -> fdic_sdi_features (413K rows, 1984-2025)
32_acquire_cdr_unrealized.py   FFIEC CDR Public bulk downloader (Playwright)
33_parse_cdr_unrealized.py     CDR parser -> cdr_unrealized_losses (46.9K rows, 2019-2025)
```

> **Intentional 30-prefix overlap:** the four fair-value/feature builders
> (`30_build_public_luck_panel.py`, `31`/`32`/`33`) share the `30` prefix with the
> pre-existing `30_ingest_stress_scenarios.py`. The collision is a filename-sort
> artifact only — both run independently. `fdic_sdi_features` and
> `cdr_unrealized_losses` are their FreeNIC table outputs (wired into
> 00_setup / 12_export / 13_validate / 20_crosswalks); the parquet panels are written
> under `OUTPUT_ROOT`.

## Script Number Gaps

- **14-15**: Reserved for Y-9LP (blocked by Cloudflare)
- **21-22**: Reserved for Knowledge Base integration
- **26**: Reserved for FDIC Locations API (if non-redundant with SOD)

## Path Management

All input paths are centralized in `utils.py` via the `INPUT_PATHS` dictionary.
Scripts import `INPUT_PATHS` rather than constructing paths from `INPUTS_DIR`.
Externally-sourced inputs (Failing Banks panel, bank-identifier catalogs, stress
scenarios, FFIEC CDR bulk ZIPs) are read from `Inputs/<source>/` if bundled, else
from `$DATA_ROOT/<source>/`. Derived feature panels are written to `$OUTPUT_ROOT/`.
See the project README "## Setup" and `data/MANIFEST.md`.

## Adding a New Data Source

1. Create script `NN_ingest_<source>.py` following existing patterns
2. Add table schema to `00_setup.py` (for documentation; scripts create tables directly)
3. Add new `INPUT_PATHS` entry in `utils.py` if needed
4. Add to `12_export_parquet.py` tables list
5. Add to `13_validate.py` for date/null checks
6. Update `20_build_crosswalks.py` if variables map to MDRM
7. Run `pytest tests/` to verify no regressions
