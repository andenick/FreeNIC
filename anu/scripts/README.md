# Reproducing FreeNIC Data — anu/ scripts

Anu-stage drivers over the canonical pipeline (`pipeline/scripts/`). Run
from the repo root unless noted. All scripts use relative paths and default
their outputs to `anu/data/` (override with `FREENIC_INPUTS` /
`FREENIC_OUTPUTS` / `FREENIC_WAREHOUSE`).

## Loaders (L##) — fetch / acquire raw data

| Script | Family | Access |
|---|---|---|
| `L01_fetch_fdic.py [failures\|financials\|history\|sod]` | FDIC BankFind Suite | public, keyless (live fetch) |
| `L02_fetch_ffiec_cdr.py call\|ubpr\|peer\|unrealized [args]` | FFIEC CDR bulk (Call, UBPR, unrealized) | public, browser-driven (delegates to 07d/07g/07i/32) |
| `L03_fetch_bhcf_mdrm.py --check` | BHCF/Y-9C bulk + MDRM + Chicago Fed XPT | public bulk + licensed historical vintage (D03/D05) |
| `L04_fetch_nic.py y15` | NIC attributes + FR Y-15 | public download page; Y-15 listing JS-gated (headed browser) |
| `L05_fetch_fred.py` | FRED H.8 + macro (15 keyless series) | public, keyless (live fetch) |
| `L06_fetch_occ_luck.py --check` | Luck DTA + OCC TSV + finhist | public research distributions (D09) |
| `L07_fetch_ncua.py --check` | NCUA 5300 | public quarterly bulk |
| `L08_fetch_supervisory.py --check` | DFAST + scenarios + Pillar 3 | public CSVs; Pillar 3 manual (D12) |
| `L09_fetch_crosswalks.py sec\|hmda` | CRSP-FRB, SEC, HMDA, GLEIF | public (D13) |
| `L10_fetch_failing_banks.py clone` | Failing Banks panel | public repo + conversion scripts (D10) |

Every loader accepts `--check` to verify input presence without downloading;
missing bulk inputs print the exact acquisition URL and exit non-zero (no
silent fallbacks).

## Processors (P##) — build the warehouse

| Script | Phases run | Produces |
|---|---|---|
| `P01_ingest_dictionary.py` | 01, 14, 44 | mdrm, dict_*, variable dictionary |
| `P02_ingest_sources.py [phase-tokens]` | 02–42 (34 ingest phases) | all source tables |
| `P03_build_catalogs.py` | 10, 20, 20b, 36, 46, 47, 48, 49 | catalogs, crosswalks, self-manifest |
| `P04_build_panels.py` | 30b, 45 | public luck panel, clean_bank_panel |
| `P05_build_reconstruction.py` | 50, 51 | reconstruction layer + reconciliations |
| `P06_export_release.py` | 12, 12b, 17, 15, 16 | Parquet exports, views, coverage audit |

Ingest phases are idempotent (already-loaded periods are skipped), so P02
can be re-run after each quarterly acquisition (`L02 call 20260631` etc.)
per `pipeline/REFRESH.md`.

## Validator (V01)

`python anu/scripts/V01_validate.py [--remote|--local] [--warehouse DB]`

- **A** registry structure: 67 entries, required fields, unique ids, every
  referenced construction script exists
- **B** registry ↔ release manifest bijection with exact row parity
  (`--remote` checks against https://data.freenic.org/release_manifest.json;
  `--local` against the committed v1.0.0 manifest + reconstruction counts)
- **C** local warehouse COUNT(*) parity when a warehouse file is present
- **D** served-data spot checks over DuckDB `httpfs` (failures span,
  163-year aggregate spine sanity, clean panel span)

Exits non-zero on any failure.

## Registry maintenance

`python anu/scripts/make_registry.py --remote` regenerates
`series_registry.json` by merging the curated family/source metadata with
the authoritative release manifest's row counts and tiers. Run it after a
quarterly refresh and commit the diff alongside the new release manifest.
