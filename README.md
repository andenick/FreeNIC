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
| [`pipeline/`](pipeline/) | The ingestion + validation suite that builds the warehouse: `scripts/` (phase scripts, incl. `13_validate.py`, `47_self_describing.py`, `49_coverage_matrix.py`, and the `50–52_*` reconstruction wrappers), the verified [`reconstruction/`](pipeline/reconstruction/) module (rebuild Luck/finhist from raw + cell-by-cell validation — see below), the `tests/` pytest suite, `requirements.txt`, and the quarterly refresh protocol (`REFRESH.md` + `REFRESH_STATE.json`). |
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

## Reconstructing Luck / finhist from raw (v1.1.0)

FreeNIC **v1.1.0** adds a first-class, open-source, **verified reconstruction** capability: it
rebuilds the Correia–Luck–Verner ("CLV") "Failing Banks" call-report panel ("Luck") and the OCC
historical panel ("finhist") **from raw FreeNIC data**, then proves the result against the
published datasets **cell-by-cell** — the "perfect reverse engineer." The module lives in
[`pipeline/reconstruction/`](pipeline/reconstruction/); its human spec is
[`RECONSTRUCTION_SPEC.md`](pipeline/reconstruction/RECONSTRUCTION_SPEC.md), its machine twin is
`variable_map.csv`, and the full validation record (combined + per-era reports, gate JSONs, the
tri-engine anchor, and the independent adversarial review) is in
[`pipeline/reconstruction/reports/`](pipeline/reconstruction/reports/).

### The derivability boundary (the honesty contract)

Not every era can be reconstructed the same way. The module states — and enforces — exactly
what "from raw" can mean in each era, and never fabricates a value outside that boundary:

| Era | What "from raw" means here | Basis |
|---|---|---|
| **1976–2026** (MODC) | **TRUE independent re-derivation** — the Luck-schema panel is built from Fed-direct raw MDRM (Chicago Fed + FFIEC CDR call-report filings) and matched against the published values | raw MDRM call-report filings |
| **1959Q4–1975Q4** (MODL) | **Derivation-layer** re-derivation — an original open-source implementation of CLV's documented 04/05/07 method run on their digitized `.dta` (the only machine source for this era) | their source `.dta` + their do-file *method* (never their code) |
| **1863–1941** (finhist, HIST) | **Derivation-layer** — `historical-call.dta` (their OCR digitization) → the published derivation; the OCR itself is **NOT-DERIVABLE** (physical archives) | finhist `.dta` + OCC label docs |

Cells outside the boundary are classed **NOT-DERIVABLE** and never imputed; the genuine
1942–1958 gap is kept absent, never synthetically filled.

### The honest verdicts

The harness runs a pre-registered cell-match gate per era (SPEC §7 / D2: matched share ≥ the
era threshold **AND** UNEXPLAINED share ≤ 0.1000%, with NOT-DERIVABLE excluded from the
denominator). The verdicts are reported exactly as they came out — **including the failure**:

| Era | Alignment key | Matched share | Pre-registered gate | Verdict |
|---|---|---|---|---|
| **1959Q4–1975Q4** | `(id_rssd, period_end)` | **99.9753%** | ≥ 99.9% | **PASS** |
| **1863–1941 (finhist)** | `(bank_id, year)` | **99.7061%** | ≥ 99.5% | **PASS** |
| **1976–2026** | `(id_rssd, period_end)` | **96.4338%** | ≥ 99.5% | **FAIL** |

**The 1976–2026 independent tier FAILs its pre-registered gate, and we say so plainly.** Our
sparse Fed-direct panel and CLV's dense harmonized panel differ materially in coverage and
encoding, and METHOD-CHOICE cells (including the zero-fill encoding fork) stay in the
denominator so they cannot lift the score. Stated as supplementary metrics (clearly **not** the
gate): value fidelity **where both panels report a value and the cell is inside the
derivability boundary is 99.90%** (38,469,955 of 38,508,758), and the **two-sided
value-divergence rate is just 0.0972% of derivable** (cells where both panels report a value and
disagree). The claim that the rebuild reproduces CLV's published modern panel *cell-for-cell* is
**NOT supported and is held**; the claim that it reproduces the values *where both panels report*
is supported by those supplementary metrics.

The two PASS eras are honest **same-source derivation-layer** reproductions — their `.dta` is
the only machine source, so near-perfect agreement is the deliberate bar — not independent
corroboration; the independent tier is 1976–2026. An independent **adversarial re-review**
([`reports/V2_ADVERSARIAL_20260715.md`](pipeline/reconstruction/reports/V2_ADVERSARIAL_20260715.md))
reproduced every headline number bit-for-bit, confirmed zero two-sided divergence in the PASS
eras, and found no fabricated or masked cell.

### Tri-engine anchor — does the economics survive the swap?

Beyond cell-matching, a **tri-engine anchor** replaces CLV's regressors, cell-for-cell, with our
independently reconstructed ones and re-runs the QJE "Failing Banks" AUC horse race through the
unmodified STUDY_11 engine (verified Stata ≡ R ≡ Python to 4 dp). Verdict:
**ANCHORED-with-explained-deltas** — the historical and 1959–75 legs reproduce every AUC to
Δ ≤ 0.0002 (the 1959–75 regressors are bit-identical to CLV's), and the only material deltas
(modern, ≤ 0.007) trace entirely to the *independent Fed-direct* sourcing of `noncore_ratio` — a
pre-registered METHOD-CHOICE, not an error. The horse-race ordering and the dominant negative
position-making interaction are preserved
([`reports/V1_TRI_ENGINE_20260715.md`](pipeline/reconstruction/reports/V1_TRI_ENGINE_20260715.md)).

### How to run

```bash
cd pipeline
pip install -r requirements.txt        # duckdb + pandas
# Build-host input/output locations are read from env vars (repo-relative defaults):
#   FREENIC_OUTPUTS (default: Outputs)   FREENIC_INPUTS (default: Inputs)
#   FREENIC_TECHNICAL / FREENIC_SCRATCH  — see pipeline/reconstruction/README.md

# Reconstruct + load the panels into the warehouse (thin wrappers over the module):
python scripts/50_reconstruct_luck.py --rebuild        # MODC 1976–2026 + MODL 1959–1975
python scripts/51_reconstruct_finhist.py --rebuild     # HIST 1863–1941
python scripts/52_validate_reconstruction.py           # the cell-by-cell gate -> reports/

# Module unit tests (fast, fixture-based, no warehouse):
pytest reconstruction/tests -q
```

### Data provenance, citation & licensing

The reconstruction derives from the "Failing Banks" project by Sergio Correia, Stephan Luck, and
Emil Verner. The Harvard Dataverse deposit `doi:10.7910/DVN/Q22XR1` is **CC0 1.0**; the modern
call-report content is redistributed under the **New York Fed Terms of Use** (attribution +
keep-source-URL + **share-alike** + no-endorsement, on that slice only) — the NY-Fed-derived
slice is **not relicensed** under more restrictive terms, our reconstructions are labeled as ours
and are **not attributed to the New York Fed**, the accuracy disclaimer is carried through, and no
OUP/QJE article text is redistributed (cite only). Every module is **original Python implementing
CLV's documented methodology** with per-function citations to their do-file loci; **their do-files
are never redistributed** (D3). Ship this block verbatim in every README / codebook / data
package / site footer (full posture: [`LICENSE_POSTURE.md`](pipeline/reconstruction/LICENSE_POSTURE.md)):

```text
DATA PROVENANCE & CITATIONS
---------------------------
This release reconstructs and redistributes data from the "Failing Banks" project by
Sergio Correia, Stephan Luck, and Emil Verner. Please cite:

Paper (methodology / dataset of record):
  Correia, Sergio, Stephan Luck, and Emil Verner. "Failing Banks." The Quarterly Journal of
  Economics 141, no. 1 (2026): 147-204. https://doi.org/10.1093/qje/qjaf044

Replication data (Harvard Dataverse, CC0 1.0):
  Correia, Sergio; Luck, Stephan; Verner, Emil, 2026, "Replication Data for: 'Failing Banks'",
  https://doi.org/10.7910/DVN/Q22XR1, Harvard Dataverse, V1.1. Licensed CC0 1.0.

Historical OCC call reports (1867-1904 subset), where used:
  Carlson, Mark, Sergio Correia, and Stephan Luck. 2022. "The Effects of Banking Competition on
  Growth and Financial Stability: Evidence from the National Banking Era." Journal of Political
  Economy 130 (2): 462-520.

Historical data portal:
  finhist.com - Historical Financial Data Project (Correia, Luck, Verner). https://finhist.com

Modern call reports (1959Q4-2025):
  Federal Reserve Bank of New York, "Balance Sheets and Income Statements of Commercial Banks:
  1959 through 2025." https://www.newyorkfed.org/research/banking_research/balance-sheets-income-statements
  Content from the New York Fed is used under the New York Fed Terms of Use
  (https://www.newyorkfed.org/privacy/termsofuse):
  "(c) [year] Federal Reserve Bank of New York. Content from the New York Fed subject to the
  Terms of Use at newyorkfed.org." No guarantee is made about the accuracy of the data; the
  New York Fed does not endorse this reconstruction, and derivative works herein are not
  attributed to the New York Fed.

LICENSES: Dataverse deposit doi:10.7910/DVN/Q22XR1 = CC0 1.0. NY Fed modern call-report content =
NY Fed Terms of Use (attribution + share-alike; not relicensed here). Our original code and
reconstruction outputs are the campaign's own contribution and do not redistribute the authors' code.
```

(Replace `[year]` with the retrieval year for the NY Fed slice, e.g. 2026.)

## Citation

If you use FreeNIC, please cite it — see [`CITATION.cff`](release-tools/release_v1.0.0/CITATION.cff):

> Anderson, Nicholas. *FreeNIC: Free National Information Center* (v1.0.0), 2026.
> https://github.com/andenick/FreeNIC · https://data.freenic.org

Individual upstream sources carry their own terms and required citations; most are US
Government / regulatory public-domain works, a few academic sources require citation. See
`release-tools/release_v1.0.0/LICENSE` and the per-table provenance for details.
