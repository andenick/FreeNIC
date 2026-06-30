# freenic

Python interface to the freenic US banking regulatory database. ~2.25 billion rows spanning 1863-2026, covering 217,210 institutions from 20 data sources.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import freenic

# Point to your Parquet data directory
freenic.set_data_dir("/path/to/freenic/Outputs/parquet")

# List available tables
freenic.list_tables()

# Look up an institution
freenic.lookup_institution("jpmorgan")

# Get financial time series
freenic.get_financials(1039502, "BHCK2170")  # JPMorgan total assets

# Search variables
freenic.search_variables("total assets")

# Bank failures during the 2008 crisis
freenic.get_failures(start_year=2008, end_year=2010)

# Raw SQL queries with joins
freenic.query("""
    SELECT i.name_legal, bf.closing_date, bf.total_assets
    FROM bank_failures bf
    JOIN institutions i ON bf.cert = i.fdic_cert
    WHERE bf.failure_year >= 2008
    ORDER BY bf.total_assets DESC
    LIMIT 10
""")

# Corporate hierarchy
freenic.get_hierarchy(1039502, direction="down")  # JPMorgan subsidiaries
```

## Configuration

Set the data directory via Python or environment variable:

```python
freenic.set_data_dir("/path/to/parquet")
```

```bash
export FREENIC_DATA_DIR="/path/to/parquet"
```

## Data Sources

| Source | Rows | Coverage |
|--------|------|----------|
| Chicago Fed Call Reports | 896M | 1976-2002 |
| Luck Historical Database (pre-1976 core) | 38M | 1959Q4-1975Q4 (+gap-fill) |
| BHCF Y-9C Filings | 208M | 1986-2025 |
| FDIC SDI Financials | 69M | 1984-2025 |
| OCC Historical | 9.8M | 1867-1904 |
| Failing Banks | 2.9M | 1863-2024 |
| FDIC Summary of Deposits | 2.7M | 1994-2025 |
| + 13 more sources | | |

### Engineered / cross-reference tables

| Table | Rows | Coverage |
|-------|------|----------|
| `entity_xref` — canonical RSSD identity union across all sources | 234K | all |
| `fdic_sdi_features` — FDIC-SDI engineered ratios + failure-lead flags, by (rssd_id, year) | 413K | 1984-2025 |
| `cdr_unrealized_losses` — FFIEC-CDR AFS/HTM fair-value, AOCI & brokered deposits, by (rssd_id, period_end) | 47K | 2019-2025 |

## API Reference

- `set_data_dir(path)` - Set Parquet directory path
- `query(sql, params)` - Execute SQL, returns DataFrame
- `list_tables()` - Show available tables
- `describe(table)` - Column names and types
- `lookup_institution(search, field)` - Search institutions
- `get_financials(rssd_id, variables, source)` - Financial time series
- `search_variables(term)` - Search variable catalog
- `get_hierarchy(rssd_id, direction)` - Corporate relationships
- `get_failures(start_year, end_year, state)` - Bank failure records
- `close()` - Release resources
