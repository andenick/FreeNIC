# FreeNIC — Open Banking Data Platform

**1.5 billion rows of US banking regulatory data from 20 sources spanning 1863–2026, unified into 34 queryable tables covering 217,210 institutions.**

---

## Why This Exists

Empirical banking research requires combining data from many regulatory sources — call reports, holding company filings, failure records, stress test results, deposit data — each in different formats with different identifiers. FreeNIC harmonizes these into a single relational schema with Python, R, and AI agent interfaces.

All data comes from public regulatory filings (FFIEC, FDIC, Federal Reserve, OCC) and freely available academic databases. No proprietary data, no paywalls.

---

## Quick Start

```bash
git clone https://github.com/andenick/FreeNIC.git
cd FreeNIC

# Python interface
cd Outputs/freenic_py
pip install -e .
```

```python
import freenic

freenic.set_data_dir("Outputs/parquet")
freenic.list_tables()
freenic.lookup_institution("jpmorgan")
freenic.get_financials(1039502, "BHCK2170")  # JPMorgan total assets
freenic.get_failures(start_year=2008, end_year=2010)
```

The Parquet data files (~5 GB) are not included in the repo and must be built from source using the ingestion pipeline. See the [Ingestion Pipeline](#ingestion-pipeline) section.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total observations | 1.5B+ |
| Institutions | 217,210 |
| Variables (MDRM) | 87,000+ |
| Tables | 34 |
| Time span | 1863–2026 |
| Data sources | 20 |

---

## Access Methods

### Python

```bash
pip install -e Outputs/freenic_py
```

```python
import freenic

freenic.set_data_dir("/path/to/parquet")
freenic.list_tables()
freenic.lookup_institution("jpmorgan")
freenic.get_financials(1039502, "BHCK2170")
freenic.get_failures(start_year=2008, end_year=2010)
freenic.query("SELECT COUNT(*) FROM institutions")
freenic.get_hierarchy(1039502, direction="down")
```

### R

```r
install.packages("Outputs/freenic_r", repos = NULL, type = "source")

library(freenic)
freenic_set_data_dir("/path/to/parquet")
df <- read_institutions()
df <- read_bank_failures()
freenic_query("SELECT COUNT(*) AS n FROM institutions")
```

### MCP Server (for AI agents)

```bash
pip install -r Technical/freenic_mcp/requirements.txt
export FREENIC_DATA_DIR="/path/to/parquet"
python Technical/freenic_mcp/server.py
```

The MCP server exposes 15 tools: `query_freenic`, `lookup_institution`, `get_financials`, `search_variables`, `get_hierarchy`, `describe_database`, `describe_table`, `get_failures`, `get_fred_series`, `lookup_rssd`, `lookup_column_id`, `show_source_descriptions`, `show_regulatory_groups`, `verify_mdrm_codes`, `verify_rssds`.

---

## Data Sources

| # | Source | Rows | Coverage | Access |
|---|--------|------|----------|--------|
| 1 | Chicago Fed Call Reports | 896M | 1976–2002 | [chicagofed.org](https://www.chicagofed.org/banking/financial-institution-reports/commercial-bank-data) |
| 2 | Luck Historical Database | 312M | 1959–2025 | [Academic request](https://www.nber.org/papers/w29557) |
| 3 | BHCF Y-9C Filings | 208M | 1986–2025 | [FFIEC CDR](https://cdr.ffiec.gov/public/ManageFacsimiles.aspx) |
| 4 | FDIC SDI Financials | 69M | 1984–2025 | [FDIC BankFind](https://banks.data.fdic.gov/) |
| 5 | OCC Historical | 9.8M | 1867–1904 | [OCC Annual Reports](https://www.occ.treas.gov/publications-and-resources/publications/annual-report/index-annual-report.html) |
| 6 | Robin Failing Banks Panel | 2.9M | 1863–2024 | Included (from [Robin](https://github.com/andenick/failing-banks)) |
| 7 | FDIC Summary of Deposits | 2.7M | 1994–2025 | [FDIC SOD](https://www7.fdic.gov/sod/) |
| 8 | FDIC Bank Failures | 4K | 1934–2025 | [FDIC BankFind API](https://banks.data.fdic.gov/api/) |
| 9 | FDIC Historical | 500K | 1934–2025 | [FDIC BankFind](https://banks.data.fdic.gov/) |
| 10 | NIC Structure Data | 36K | Current | [FFIEC NIC](https://www.ffiec.gov/NPW/) |
| 11 | CRSP-FRB Link | 14K | 1971–2024 | [NY Fed](https://www.newyorkfed.org/research/banking_research/datasets.html) |
| 12 | MDRM Variable Dictionary | 87K | Current | [Fed MDRM](https://www.federalreserve.gov/apps/mdrm/) |
| 13 | DFAST Stress Test Results | 500 | 2013–2025 | [Fed DFAST](https://www.federalreserve.gov/supervisionreg/dfast.htm) |
| 14 | Pillar 3 G-SIB Disclosure | 20K | 2020–2025 | Bank websites |
| 15 | Fed H.8 | 75K | 1973–2025 | [FRED](https://fred.stlouisfed.org/) |
| 16 | FRED Banking Series | 75K | 1954–2025 | [FRED API](https://fred.stlouisfed.org/docs/api/) |
| 17 | Stress Test Scenarios | 1K | 2024–2026 | [Fed Scenarios](https://www.federalreserve.gov/supervisionreg/stress-tests-capital-planning.htm) |
| 18 | Bank Identifier Crosswalk | 14K | Current | Derived (Robin ↔ RSSD ↔ FDIC cert) |
| 19 | BHC Hierarchy | 37K | Current | Derived (NIC structure + ownership) |
| 20 | Sector Groupings | 17K | Current | Derived (CIK → SIC → sector) |

---

## Repository Structure

```
FreeNIC/
├── README.md
├── Inputs/                         Source data files (gitignored, re-downloadable)
├── Outputs/
│   ├── parquet/                    34 Parquet tables (gitignored, ~5 GB)
│   ├── freenic_py/                 Python package (pip install -e .)
│   ├── freenic_r/                  R package (install.packages from source)
│   ├── QUICK_START.md              Connection examples, common queries
│   ├── DATA_DICTIONARY.md          Full schema reference for all 34 tables
│   ├── DATA_SOURCE_INVENTORY.md    Source provenance and ingestion details
│   └── COVERAGE_GAPS.md            Known limitations and missing data
├── Technical/
│   ├── freenic_mcp/                MCP server for AI agents
│   ├── freenic_ingestion/          30-script ingestion pipeline
│   │   ├── scripts/00-30           Numbered ingestion scripts
│   │   └── tests/                  7 test suites (integrity, schema, referential, etc.)
│   └── Knowledge_Base/             extracted from regulatory filing instructions
└── .gitignore
```

---

## Ingestion Pipeline

The ingestion pipeline transforms raw regulatory data into the unified Parquet schema. Scripts are numbered and run in order:

| Script | What it does |
|--------|-------------|
| 00 | Setup: create database schema |
| 01 | MDRM variable dictionary |
| 02 | NIC institution attributes |
| 03 | CRSP-FRB bank identifier link |
| 04–05 | BHCF Y-9C filings (TXT + CSV formats) |
| 06 | Y-9C schema verification |
| 07 | Chicago Fed call reports (1976–2002) |
| 08 | Luck Historical Database |
| 09 | OCC historical (1867–1904) |
| 10 | Build institution catalog |
| 11 | Build convenience views |
| 12 | Export to Parquet |
| 13 | Validate all tables |
| 16–19 | FDIC (failures, financials, SOD) |
| 20 | Cross-source identifier crosswalks |
| 23–25 | DFAST, Pillar 3, FDIC history |
| 27 | Fed H.8 aggregate series |
| 28–30 | Failing Banks panel, bank-identifier catalogs, stress scenarios |
| 31–33 | SDI feature panel + FFIEC CDR fair-value/unrealized-loss panel |

---

## Validation

Seven test suites verify data integrity:

| Test | What it checks |
|------|---------------|
| `test_schema.py` | Column types, table existence, expected schemas |
| `test_integrity.py` | Row counts, null rates, value ranges |
| `test_referential.py` | Foreign key relationships across tables |
| `test_cross_source.py` | Same institution across different sources matches |
| `test_freshness.py` | Data covers expected date ranges |
| `test_regression.py` | Key aggregates haven't changed unexpectedly |
| `test_mcp.py` | MCP server tool responses |

---

## Requirements

- **Python 3.11+** — ingestion, querying, MCP server
- **R 4.x** (optional) — R package only
- **DuckDB** — `pip install duckdb` (included as dependency)
- **Disk** — ~5 GB for Parquet files, ~20 GB for raw inputs during ingestion
- **APIs** — None required for querying; ingestion scripts download from public URLs

---

## Setup

Querying the published Parquet/DuckDB outputs needs no configuration. To **run the
ingestion pipeline yourself**, point it at where it should read inputs and write
derived panels via two environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATA_ROOT` | Where externally-sourced inputs not bundled under `Inputs/` are read (e.g. FFIEC CDR bulk ZIPs, the Failing Banks panel, bank-identifier catalogs, stress scenarios) | `./data` |
| `OUTPUT_ROOT` | Where derived feature panels (`*.parquet`) are written | `./outputs` |

```bash
git clone https://github.com/andenick/FreeNIC.git && cd FreeNIC
pip install -r requirements.txt
# optional: only needed to re-run ingestion
export DATA_ROOT=/path/to/your/data
export OUTPUT_ROOT=/path/to/your/outputs
```

Each ingestion script first looks for its source under `Inputs/<source>/`; if that
is absent it falls back to `$DATA_ROOT/<source>/`. See **`data/MANIFEST.md`** for the
exact files each script expects and where to download them.

### API keys — bring your own

Querying needs no keys. Some ingestion sources are public APIs that offer an optional
free key for higher rate limits:

- **FRED** (Fed H.8 / banking series): free key at
  <https://fred.stlouisfed.org/docs/api/api_key.html>; set `FRED_API_KEY`.

Copy `.env.example` to `.env` and fill in any keys you use. The FDIC BankFind, FFIEC
CDR, and Chicago Fed downloads require no key.

---

## Citation

```bibtex
@software{freenic2026,
  title = {FreeNIC: Free National Information Center — Open Banking Data Platform},
  author = {Anderson, Nicholas},
  year = {2026},
  url = {https://github.com/andenick/FreeNIC}
}
```

---

## License

MIT
