# FreeNIC — Free National Information Center

**FreeNIC** is a research-grade, openly published US banking data warehouse. It harmonizes
the major public regulatory data sources — FFIEC Call Reports & UBPR, FDIC (BankFind, SDI,
Summary of Deposits, historical), the Federal Reserve (FR Y-9C/BHCF, H.8, FRED), OCC, NCUA,
SEC EDGAR, and derived academic panels — into a single, provenance-tracked warehouse with a
harmonized variable dictionary, then exports a clean, citable public release.

- **Warehouse:** 58 base tables · **4.97 billion rows** (4,965,894,572) · coverage span **1782–2026**
  across 21 source families (warehouse build 1.4, data vintage 2026Q1).
- **Public release (v1.0.0):** **61 files / 13.2 GiB** — 60 base-table Parquet exports plus the
  163-year (1863–2026) bank-aggregate spine `long_bank_aggregates_1863_2026.parquet`. Every
  served Parquet's row count equals its warehouse source table's (row-parity gate: 61/61).
- **Explorer site:** [freenic.org](https://freenic.org) · **Data host:** [data.freenic.org](https://data.freenic.org)

Code is MIT; the data compilation is CC-BY-4.0 (E-3 provisional — see [LICENSE](LICENSE) and
`release-tools/release_v1.0.0/LICENSE`).

## Query the data over HTTP (no download)

Every released Parquet file is served with HTTP byte-range support, so DuckDB's `httpfs`
extension can query it in place — you fetch only the bytes your query touches.

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

# Example 1 — every US bank failure on record (FDIC + historical), 1863–2026:
print(con.execute("""
    SELECT failure_year, COUNT(*) AS n_failures, SUM(total_assets) AS assets
    FROM 'https://data.freenic.org/bank_failures.parquet'
    WHERE failure_year IS NOT NULL
    GROUP BY failure_year ORDER BY failure_year DESC LIMIT 10
""").fetchdf())

# Example 2 — the 163-year replicated bank-aggregate spine (num banks / assets / deposits / loans):
print(con.execute("""
    SELECT year, metric, value, definition
    FROM 'https://data.freenic.org/long_bank_aggregates_1863_2026.parquet'
    WHERE metric = 'num_banks' AND definition = 'primary'
    ORDER BY year DESC LIMIT 10
""").fetchdf())
```

The same works from the R `duckdb`/`arrow` packages and from the command line
(`duckdb -c "SELECT ... FROM 'https://data.freenic.org/<file>.parquet'"`). The complete
per-file catalog (name, bytes, sha256, rows, provenance, URL) is in
[`release-tools/release_v1.0.0/release_manifest.json`](release-tools/release_v1.0.0/release_manifest.json).

## Repository layout

This is one repository with three top-level parts:

| Directory | What it holds |
|---|---|
| [`pipeline/`](pipeline/) | The ingestion + validation suite that builds the warehouse: `scripts/` (71 phase scripts, incl. `13_validate.py`, `47_self_describing.py`, `49_coverage_matrix.py`), the `tests/` pytest suite, `requirements.txt`, and the quarterly refresh protocol (`REFRESH.md` + `REFRESH_STATE.json`). |
| [`site/`](site/) | The `freenic.org` explorer application (FastAPI + Jinja): both the data explorer and the variable-dictionary explorer, the counts mechanism, templates, static assets, the curated slice serving, `Dockerfile`/compose, and `DATA_SERVING.md` (self-hosting the httpfs data host). |
| [`release-tools/`](release-tools/) | Release-packaging tools (`build_slice.py`, `build_content.py`, `make_freenic_counts.py`) and the v1.0.0 release metadata (`release_v1.0.0/`: manifest, changelog, citation, license, codebook, croissant, checksums). |

Large data artifacts (the warehouse DuckDB, the full Parquet release, the curated
`freenic_slice.duckdb`, zips) are **not** committed — they are served from
[data.freenic.org](https://data.freenic.org) and cataloged in `release_manifest.json`.

## Build the warehouse (pipeline)

```bash
cd pipeline
pip install -r requirements.txt
# The scripts read build-host locations from env vars (see pipeline/REFRESH.md):
#   FREENIC_OUTPUTS, FREENIC_INPUTS, FREENIC_WAREHOUSE, FRED_API_KEY, ...
python scripts/00_setup.py           # then run the numbered phases in order
python scripts/13_validate.py        # the read-only validation gate
pytest tests/ -q
```

## Run the explorer site

```bash
cd site
pip install -r app/requirements.txt
# The app needs the curated slice at app/data/freenic_slice.duckdb — build it with
# release-tools/build_slice.py (see release-tools/README.md), or run against the hosted data.
uvicorn app.main:app --reload         # or: docker compose up
```

## Quarterly refresh

FFIEC publishes each reporting quarter ~75 days after quarter-end. The refresh protocol
(acquire → ingest → validate → dictionary → views/coverage → republish) is documented in
[`pipeline/REFRESH.md`](pipeline/REFRESH.md); per-quarter progress is tracked in
[`pipeline/REFRESH_STATE.json`](pipeline/REFRESH_STATE.json).

## Citation

If you use FreeNIC, please cite it — see [`CITATION.cff`](release-tools/release_v1.0.0/CITATION.cff):

> Anderson, Nicholas. *FreeNIC: Free National Information Center* (v1.0.0), 2026.
> https://github.com/andenick/FreeNIC · https://data.freenic.org

Individual upstream sources carry their own terms and required citations; most are US
Government / regulatory public-domain works, a few academic sources require citation. See
`release-tools/release_v1.0.0/LICENSE` and the per-table provenance for details.
