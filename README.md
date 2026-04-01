# FreeNIC

**Free National Information Center** — an open banking data research platform integrating 1.5 billion rows of US regulatory data from 20 sources spanning 1863–2026.

## Overview

FreeNIC unifies data from FFIEC, FDIC, Federal Reserve, OCC, CRSP, and academic sources into 34 Parquet tables covering 217,210 institutions. Three access interfaces are provided: a Python package, an R package, and an MCP server for AI agents.

| Metric | Value |
|--------|-------|
| Total observations | 1.5B+ |
| Institutions | 217,210 |
| Variables (MDRM) | 87,000+ |
| Tables | 34 |
| Time span | 1863–2026 |
| Data sources | 20 |

## Access Methods

### Python

```bash
cd Outputs/freenic_py
pip install -e .
```

```python
import freenic

freenic.set_data_dir("/path/to/parquet")
freenic.list_tables()
freenic.lookup_institution("jpmorgan")
freenic.get_financials(1039502, "BHCK2170")
freenic.get_failures(start_year=2008, end_year=2010)
```

### R

```r
# Install from local source
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

# Set data directory
export FREENIC_DATA_DIR="/path/to/parquet"

# Run the server
python Technical/freenic_mcp/server.py

# Or add to Claude Code:
claude mcp add freenic -- python Technical/freenic_mcp/server.py
```

The MCP server exposes 15 tools: `query_freenic`, `lookup_institution`, `get_financials`, `search_variables`, `get_hierarchy`, `describe_database`, `describe_table`, `get_failures`, `get_fred_series`, `lookup_rssd`, `lookup_column_id`, `show_source_descriptions`, `show_regulatory_groups`, `verify_mdrm_codes`, `verify_rssds`.

## Configuration

All three interfaces read from a directory of Parquet files. Set the path via:

```bash
export FREENIC_DATA_DIR="/path/to/Outputs/parquet"
```

Or configure in code (Python: `freenic.set_data_dir(...)`, R: `freenic_set_data_dir(...)`).

The MCP server also supports connecting to a pre-built DuckDB file via `FREENIC_DB_PATH`.

## Data Sources

| Source | Rows | Coverage |
|--------|------|----------|
| Chicago Fed Call Reports | 896M | 1976–2002 |
| Luck Historical Database | 312M | 1959–2025 |
| BHCF Y-9C Filings | 208M | 1986–2025 |
| FDIC SDI Financials | 69M | 1984–2025 |
| Robin Failing Banks Panel | 2.9M | 1863–2024 |
| FDIC Summary of Deposits | 2.7M | 1994–2025 |
| OCC Historical | 9.8M | 1867–1904 |
| FRED Banking Series | 75K | 1954–2025 |
| + 12 more sources | | |

## Repository Structure

```
Inputs/          Source data files (gitignored, re-downloadable)
Outputs/
  parquet/       34 Parquet tables (gitignored, ~5 GB, built by ingestion pipeline)
  freenic_py/    Python package (pip install -e .)
  freenic_r/     R package (install.packages from source)
Technical/
  freenic_mcp/   MCP server for AI agents
  freenic_ingestion/  Ingestion pipeline scripts
  Knowledge_Base/     HDARP-processed regulatory filing instructions
```

## Documentation

- [QUICK_START.md](Outputs/QUICK_START.md) — Connection examples, common queries, convenience views
- [DATA_DICTIONARY.md](Outputs/DATA_DICTIONARY.md) — Full schema reference for all 34 tables
- [DATA_SOURCE_INVENTORY.md](Outputs/DATA_SOURCE_INVENTORY.md) — Source provenance and ingestion details
- [COVERAGE_GAPS.md](Outputs/COVERAGE_GAPS.md) — Known limitations and missing data

## License

MIT
