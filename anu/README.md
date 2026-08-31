# FreeNIC Anu Replication Package

The Anu-framework replication layer for the FreeNIC US banking data
warehouse: **67 served data tables across 22 source families** (4.97 billion
rows, 1782–2026), organized by **table family** rather than by individual
series — the warehouse serves millions of series, so the unit of replication
is the served table.

This package **provides the pipeline, not the data**: how to fetch every
public raw source, how the canonical 74-phase pipeline builds the warehouse,
and how the output is validated against the served release. The data itself
(13.9 GiB of Parquet) is served from https://data.freenic.org and is
deliberately not committed.

```
anu/
  series_registry.json    canonical data contract: 67 tables, sources, rows
  scripts/
    L01-L10_fetch_*.py    loaders: fetch/acquire raw data per source family
    P01-P06_*.py          processors: ingest -> catalog -> panels -> export
    V01_validate.py       validator: registry <-> release-manifest parity
    make_registry.py      regenerate series_registry.json from the manifest
  dpr/                    15 Data Provenance Records (D01-D15, per family)
  data/                   gitignored; produced by the scripts
    raw/ processed/ outputs/
  requirements.txt
  Makefile
```

## Quick start

```bash
pip install -r anu/requirements.txt

# Validate this package against the LIVE served release (no download):
python anu/scripts/V01_validate.py --remote

# Or fully offline:
python anu/scripts/V01_validate.py --local
```

## Reproduce the warehouse

```bash
python anu/scripts/L01_fetch_fdic.py         # keyless FDIC APIs (public)
python anu/scripts/L05_fetch_fred.py         # keyless FRED CSVs (public)
python anu/scripts/L02_fetch_ffiec_cdr.py call 20260631   # CDR bulk (public)
python anu/scripts/L03_fetch_bhcf_mdrm.py --check        # + licensed inputs
python anu/scripts/L06_fetch_occ_luck.py --check          # + published files
python anu/scripts/P01_ingest_dictionary.py
python anu/scripts/P02_ingest_sources.py     # all ingest phases (idempotent)
python anu/scripts/P03_build_catalogs.py
python anu/scripts/P04_build_panels.py
python anu/scripts/P05_build_reconstruction.py
python anu/scripts/P06_export_release.py
python anu/scripts/V01_validate.py --local --warehouse anu/data/outputs/freenic.duckdb
```

Or `make fetch construct validate` from `anu/`.

## API keys

| Source | Key needed | Where |
|---|---|---|
| Everything except the FRED full H.8 tier | **none** | — |
| FRED full H.8 release (~1,938 series, phase 27b) | free key | set `FRED_API_KEY` — https://fred.stlouisfed.org/docs/api/api_key.html |

## Honest access notes (see the DPRs)

- **Chicago Fed Commercial Bank Data (1976–2002 Call Report XPT vintage)**:
  a licensed FRB Chicago distribution — not a keyless download. Public
  keyless Call Reports start 2001+ at FFIEC CDR; 1959–1975 is covered by the
  public Luck/finhist files. See `dpr/D03`.
- **Pillar 3 disclosures**: hand-collected from five G-SIBs' published
  disclosure documents — no bulk source exists. See `dpr/D12`.
- **Luck / finhist / OCC digitizations**: public research distributions
  (FRBNY, Harvard Dataverse, finhist.com). See `dpr/D09`.
- **Failing Banks panel**: processed CSVs regenerate from the public
  `failing-banks` repository's conversion scripts. See `dpr/D10`.
- The modern-era reconstruction's pre-registered FAIL is documented, not
  hidden. See `dpr/D15`.

## Relation to the repo pipeline

The canonical construction code is `pipeline/scripts/` (74 phases) plus
`pipeline/reconstruction/`; this package wraps it (`_bootstrap.run_phase`),
organizes it by Anu loader/processor/validator stages, documents provenance
(DPRs), and enforces the data contract (`series_registry.json` + V01). The
quarterly refresh protocol stays in `pipeline/REFRESH.md`; the release
packaging stays in `release-tools/`.

License: code MIT; the data compilation CC-BY-4.0 — see the repo `LICENSE`
and `DATA_LICENSE.md`.
