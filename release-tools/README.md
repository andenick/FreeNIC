# FreeNIC release tools

Build-host tooling that turns the warehouse into the public release + the served explorer
slice, plus the frozen v1.0.0 release metadata.

## Scripts

| Script | What it does |
|---|---|
| `build_slice.py` | Exports a small, **real** curated slice (`freenic_slice.duckdb`, < 100 MB) from the warehouse Parquet exports for the explorer app, then bakes the content layer via `build_content.py`. |
| `build_content.py` | Merges the reviewed dictionary explanations into `app/data/explanations.json` and bakes the per-schedule CSVs into the site's static tree. |
| `make_freenic_counts.py` | The single source of truth for every on-page count: regenerates `app/data/freenic_counts.json` and `release_manifest.json` from the served Parquet set + the built slice. Nothing is hand-typed. **Note:** the copy committed here is the **v1.0.0-vintage** tool — its `_served_files()` enumerates the served root only (60 base tables + the spine = 61) and does not yet walk the v1.1.0 `reconstruction/` layer, so re-running it as committed reproduces the 61-file v1.0.0 manifest, not the 67-file v1.1.0 one. The v1.1.0 manifest published at `data.freenic.org` is authoritative; treat `release_manifest.json` / `SHA256SUMS.txt` on the host as the source of truth for file counts. |

### Configuration (env vars)

These scripts run on the build host and locate everything by environment variable, so no
absolute paths are baked in:

| Variable | Purpose | Default |
|---|---|---|
| `FREENIC_OUTPUTS` | warehouse export dir (`parquet/`, `SHA256SUMS.txt`, `PROVENANCE.csv`, the spine) | `Outputs` |
| `FREENIC_PARQUET_DIR` | per-table Parquet export dir | `$FREENIC_OUTPUTS/parquet` |
| `FREENIC_WAREHOUSE` | warehouse DuckDB file (holds the `dict` taxonomy schema) | `$FREENIC_OUTPUTS/freenic.duckdb` |
| `FREENIC_SITE_DIR` | the runnable site app the slice/content/counts are written into | `../site` |

```bash
# from release-tools/, with the warehouse export dir available:
export FREENIC_OUTPUTS=/path/to/freenic/Outputs
python build_slice.py            # -> ../site/app/data/freenic_slice.duckdb (+ content, CSVs)
python make_freenic_counts.py    # -> ../site/app/data/{freenic_counts,release_manifest}.json
```

## `release_v1.0.0/` — frozen release metadata

The **small** metadata files for the v1.0.0 release are committed here:

- `release_manifest.json` — per-file catalog (name, bytes, sha256, rows, provenance, URL).
- `CHANGELOG.md`, `CITATION.cff`, `LICENSE` (data CC-BY-4.0), `CODEBOOK.md`, `croissant.jsonld`,
  `SHA256SUMS.txt`.

The **large** release payload is **not** committed — it is served, and referenced from the
manifest / checksums:

- The **67 Parquet files, 13.9 GiB** (14,955,118,561 bytes) of the v1.1.0 release: **61 at the
  served root** — 60 base tables + the 163-year spine — at `https://data.freenic.org/<file>.parquet`,
  plus the **6-file reconstruction layer** at `https://data.freenic.org/reconstruction/<file>.parquet`.
  (`SHA256SUMS.txt` carries **75** entries: those 67 parquet plus 8 reconstruction reports/gate JSONs —
  checksum coverage, not the file count.)
- The full per-variable `data_dictionary.csv` and the `codebook/` CSVs (large) accompany the
  hosted release rather than the repo.

Verify a downloaded release against `SHA256SUMS.txt` (`sha256sum -c SHA256SUMS.txt`).
