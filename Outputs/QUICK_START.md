# freenic Quick Start Guide

## What is freenic?

A unified DuckDB database of all publicly available US banking regulatory data — 1.50 billion observations spanning 1863-2026. Covers 217,210 institutions, 9,375 variables, 140,134 entity-filing combinations across 10 filing types, 24,056 FDIC-insured banks with quarterly financials, 294,035 bank branches with deposit data, 43 stress-tested BHCs, 5 G-SIB Pillar 3 disclosures, 4,114 bank failures since 1934, the Robin Failing Banks panel (39,299 banks, 1863-2024), and FRED macroeconomic context series.

## Connect

### Python

```python
import duckdb

con = duckdb.connect("freenic.duckdb", read_only=True)

# Or query Parquet files directly (no DuckDB install needed):
df = duckdb.read_parquet("parquet/institutions.parquet").df()
```

### R

```r
library(duckdb)

con <- dbConnect(duckdb(), "freenic.duckdb", read_only = TRUE)

# Or read Parquet:
library(arrow)
df <- read_parquet("parquet/institutions.parquet")
```

## MCP Server (Claude Integration)

freenic includes an MCP server for querying the database directly from Claude Code conversations.

**Setup** (already registered if you ran `/readystart freenic`):
```bash
claude mcp add freenic -- python "D:/Arcanum/Projects/freenic/Technical/freenic_mcp/server.py"
```

**Available tools**:
- `query_freenic(sql)` — Execute read-only SQL, returns up to 1000 rows as JSON
- `lookup_institution(search, field)` — Search by name, RSSD ID, FDIC cert, or state
- `get_financials(rssd_id, variables, start_date, end_date, source)` — Time series data
- `search_variables(query)` — Search catalog and crosswalk by keyword
- `get_hierarchy(rssd_id, direction)` — Corporate parent-child tree

## Cross-Source Queries

The `variable_crosswalk` table maps variables across sources to standardized concept names, enabling unified queries via the `cross_source_financials` view:

```sql
-- Total assets for JPMorgan across ALL sources
SELECT source_table, period_end, value / 1e6 AS trillions
FROM cross_source_financials
WHERE rssd_id = 1039502 AND concept = 'total_assets'
ORDER BY period_end DESC
LIMIT 10;

-- Compare net income across BHCF and FDIC SDI
SELECT source_table, period_end, value / 1e3 AS millions
FROM cross_source_financials
WHERE rssd_id = 1073757 AND concept = 'net_income'
  AND period_end >= '2024-01-01'
ORDER BY period_end DESC, source_table;

-- List all available concept names
SELECT DISTINCT concept, COUNT(DISTINCT source_table) AS sources
FROM variable_crosswalk
WHERE concept NOT IN ('fdic_cert', 'occ_charter', 'state_code')
GROUP BY concept ORDER BY sources DESC;
```

## Common Queries

### Look up an institution

```sql
SELECT rssd_id, name_legal, entity_type, state_code, is_active
FROM institutions
WHERE name_legal ILIKE '%jpmorgan%';
```

### Get total assets for a bank holding company

```sql
-- BHCK2170 = Total consolidated assets
SELECT period_end, value / 1000 AS total_assets_billions
FROM bhcf_filings
WHERE rssd_id = 1039502          -- JPMorgan Chase
  AND variable_id = 'BHCK2170'
ORDER BY period_end DESC
LIMIT 8;
```

### Find a variable by name

```sql
SELECT variable_id, canonical_name, description_short,
       first_observed, last_observed, entities_reporting
FROM catalog.variables
WHERE canonical_name ILIKE '%total assets%'
ORDER BY entities_reporting DESC;
```

### Get the corporate hierarchy for an entity

```sql
SELECT r.rssd_parent, p.name_legal AS parent_name,
       r.rssd_offspring, c.name_legal AS subsidiary_name,
       r.pct_equity, r.dt_start, r.dt_end
FROM relationships r
JOIN institutions p ON r.rssd_parent = p.rssd_id
JOIN institutions c ON r.rssd_offspring = c.rssd_id
WHERE r.rssd_parent = 1039502    -- JPMorgan Chase
  AND r.dt_end IS NULL;          -- current relationships only
```

### Cross-source query: compare BHCF and Luck data

```sql
SELECT b.period_end, b.variable_id,
       b.value AS bhcf_value,
       l.value AS luck_value
FROM bhcf_filings b
JOIN luck_call_reports l
    ON b.rssd_id = l.entity_id
    AND b.period_end = l.period_end
    AND b.variable_id = l.variable_id
WHERE b.rssd_id = 1039502
ORDER BY b.period_end DESC
LIMIT 20;
```

### Get call report data for individual banks

```sql
-- RCFD2170 = Total assets (call reports)
SELECT rssd_id, period_end, value / 1000 AS total_assets_billions
FROM call_report_filings
WHERE variable_id = 'RCFD2170'
  AND period_end = '2002-03-31'
ORDER BY value DESC
LIMIT 10;
```

### Historical data back to 1867

```sql
SELECT bank_id, report_date, variable_id, value
FROM occ_historical
WHERE variable_id = 'assets'
  AND report_date = '1867-10-07'
ORDER BY value DESC
LIMIT 10;
```

### Map bank to stock (CRSP PERMCO)

```sql
SELECT c.permco, c.rssd_id, c.name, i.name_legal,
       c.dt_start, c.dt_end
FROM crsp_mapping c
JOIN institutions i ON c.rssd_id = i.rssd_id
WHERE c.permco = 47896;  -- JPMorgan Chase PERMCO
```

### Mergers and acquisitions

```sql
SELECT t.rssd_predecessor, p.name_legal AS acquired,
       t.rssd_successor, s.name_legal AS acquirer,
       t.dt_trans
FROM transformations t
JOIN institutions p ON t.rssd_predecessor = p.rssd_id
JOIN institutions s ON t.rssd_successor = s.rssd_id
WHERE t.rssd_successor = 1039502
ORDER BY t.dt_trans DESC;
```

## Convenience Views

| View | Description |
|------|-------------|
| `bhcf_enriched` | BHCF filings joined with institution names and MDRM variable descriptions |
| `current_hierarchy` | Active parent-child relationships only |
| `entity_summary` | Per-entity summary with filing counts and date ranges |
| `variable_dictionary` | Variables with MDRM descriptions and coverage stats |
| `bank_failures_enriched` | Failures joined with institution details (RSSD, entity type, regulator) |
| `deposit_market_share` | Per-institution annual deposit market share by state and county |
| `stress_test_summary` | DFAST Severely Adverse scenario results only |
| `cross_source_financials` | Unified financial data across BHCF/Luck/FDIC via variable crosswalk |
| `robin_panel_enriched` | Robin panel + RSSD/FDIC cert linkage via crosswalk |
| `failure_timeline` | Combined Robin + FDIC failures with cross-database matching |

```sql
-- Use views for enriched queries without manual joins:
SELECT * FROM bhcf_enriched
WHERE rssd_id = 1039502 AND variable_id = 'BHCK2170'
ORDER BY period_end DESC LIMIT 5;
```

### Bank failures since 1934

```sql
SELECT bf.closing_date, bf.bank_name, bf.city, bf.state_code,
       bf.total_assets, bf.acquiring_institution
FROM bank_failures bf
WHERE bf.failure_year >= 2008 AND bf.failure_year <= 2010
ORDER BY bf.total_assets DESC NULLS LAST
LIMIT 10;
```

### FDIC individual bank financials (1984-2025)

```sql
-- Total assets for an FDIC-insured bank by FDIC cert number
SELECT period_end, value / 1000 AS total_assets_billions
FROM fdic_financials
WHERE fdic_cert = 628  -- JPMorgan Chase Bank NA
  AND variable_id = 'ASSET'
ORDER BY period_end DESC
LIMIT 8;
```

### Compare holding company vs bank subsidiary

```sql
-- JPMorgan Chase: holding company (BHCF) vs lead bank (FDIC)
SELECT b.period_end,
       b.value / 1000 AS bhc_assets_B,
       f.value / 1000 AS bank_assets_B
FROM bhcf_filings b
JOIN fdic_financials f
    ON b.period_end = f.period_end
    AND f.fdic_cert = 628
WHERE b.rssd_id = 1039502
  AND b.variable_id = 'BHCK2170'
  AND f.variable_id = 'ASSET'
ORDER BY b.period_end DESC
LIMIT 8;
```

### Branch-level deposits and market share

```sql
-- Top 10 banks by deposit market share in New York County, 2024
SELECT s.fdic_cert, i.name_legal, s.branch_deposits / 1000 AS deposits_M,
       COUNT(*) AS branches
FROM fdic_sod s
LEFT JOIN institutions i ON i.fdic_cert = s.fdic_cert
WHERE s.county = 'New York' AND s.state_code = 'NY' AND s.year = 2024
GROUP BY s.fdic_cert, i.name_legal, s.branch_deposits
ORDER BY deposits_M DESC
LIMIT 10;
```

### DFAST stress test results

```sql
-- CET1 minimum ratios under Severely Adverse for 2025 exercise
SELECT bank_name, value AS cet1_min_ratio
FROM dfast_results
WHERE year = 2025
  AND scenario = 'Severely Adverse'
  AND variable_id = 'common_equity_tier1_min_rat'
ORDER BY value;
```

### Pillar 3 capital disclosures

```sql
-- CET1 ratio across G-SIBs
SELECT bank_name, period_end, value
FROM pillar3_disclosures
WHERE variable_id ILIKE '%CET1%ratio%'
  AND disclosure_type = 'ratios'
ORDER BY bank_name, period_end;
```

### Deposit market share view

```sql
-- Counties where a single bank holds >50% market share (2024)
SELECT state_code, county, name_legal, market_share, deposits
FROM deposit_market_share
WHERE year = 2024 AND market_share > 0.5
ORDER BY deposits DESC
LIMIT 20;
```

## Data Sources

| Table | Rows | Source | Coverage |
|-------|------|--------|----------|
| call_report_filings | 896.3M | Chicago Fed XPT files | 1976Q1-2002Q2 |
| luck_call_reports | 311.8M | Luck Historical Database (Stata DTA) | 1959Q4-2025Q4 |
| bhcf_filings | 208.1M | FFIEC Bulk Downloads + BHCF CSV | 1986Q3-2025Q4 |
| fdic_financials | 69.3M | FDIC BankFind API (SDI) | 1984Q1-2025Q4 |
| occ_historical | 9.8M | OCC Balance Sheets (TSV) | 1867-1904 |
| robin_panel | 2.87M | Robin Failing Banks Database | 1863-2024 |
| fdic_sod | 2.7M | FDIC BankFind API (SOD) | 1994-2025 |
| fdic_history | 582K | FDIC History API | all dates |
| fred_series | 75K | FRED (15 banking + macro series) | 1954-2025 |
| bhc_ownership | 36.7K | Volcker BHC hierarchy catalog | current |
| dfast_results | 28K | Federal Reserve DFAST CSV | 2013-2025 |
| sector_groupings | 16.5K | SEC CIK→SIC→sector | current |
| robin_crosswalk | 14.3K | Robin↔RSSD/FDIC cert mapping | reference |
| pillar3_disclosures | 8K | HDARP-extracted Pillar 3 CSVs | 2024Q1-2025Q3 |
| bank_failures | 4.1K | FDIC Failed Banks API | 1934-2026 |
| robin_deposits_* | 3.5K | Robin deposit dynamics | historical+modern |
| stress_scenarios_* | 452 | Fed stress test definitions | 2026 |
| institutions | 217K | NIC Active + Closed Attributes | current |
| mdrm | 87K | FFIEC Master Data Reference Manual | reference |
| crsp_mapping | 19K | CRSP-FRB Link (16 vintages) | 1959-2025 |

## Additional Queries

### Robin historical bank data (1863-2024)

```sql
-- Bank-level assets for all banks in 1929 (Great Depression onset)
SELECT canonical_bank_name, state_abbrev, assets, deposits, failed_bank
FROM robin_panel
WHERE year = 1929
ORDER BY assets DESC NULLS LAST
LIMIT 20;

-- Banks that failed with run indicators
SELECT canonical_bank_name, year, assets, time_to_fail
FROM robin_panel
WHERE failed_bank = 1 AND year BETWEEN 1930 AND 1933
ORDER BY assets DESC NULLS LAST
LIMIT 20;
```

### FRED macro context

```sql
-- Federal funds rate over time
SELECT observation_date, value AS fed_funds_rate
FROM fred_series
WHERE series_id = 'FEDFUNDS'
ORDER BY observation_date DESC
LIMIT 20;
```

### FDIC institution history

```sql
-- All mergers in 2023
SELECT institution_name, change_desc, effective_date, city, state_code
FROM fdic_history
WHERE change_desc ILIKE '%merger%' AND YEAR(effective_date) = 2023
ORDER BY effective_date;
```

### BHC ownership hierarchy

```sql
-- All subsidiaries of JPMorgan Chase
SELECT rssd_id_bank, nm_lgl, entity_type, pct_equity, hierarchy_level
FROM bhc_ownership
WHERE rssd_id_bhc = 1039502
ORDER BY hierarchy_level, nm_lgl;
```

### Stress test scenario definitions

```sql
-- Severely Adverse unemployment projections
SELECT "Date", "Unemployment rate", "Real GDP growth"
FROM stress_scenarios_domestic
WHERE "Scenario Name" = 'Severely Adverse'
ORDER BY "Date";
```

### Failure timeline (cross-database)

```sql
-- Failures with both Robin and FDIC data
SELECT canonical_bank_name, year, assets, fdic_name, fdic_closing_date, acquiring_institution
FROM failure_timeline
WHERE fdic_cert IS NOT NULL
ORDER BY assets DESC NULLS LAST
LIMIT 20;
```

## File Layout

```
Outputs/
  freenic.duckdb          # 9.2 GB — the complete database
  parquet/                 # ~5.0 GB — per-table Parquet exports (34 files)
    institutions.parquet
    bhcf_filings.parquet
    call_report_filings.parquet
    luck_call_reports.parquet
    fdic_financials.parquet
    fdic_sod.parquet
    fdic_history.parquet
    fred_series.parquet
    robin_panel.parquet
    robin_deposits_historical.parquet
    robin_deposits_modern.parquet
    robin_crosswalk.parquet
    bhc_ownership.parquet
    sector_groupings.parquet
    stress_scenarios_domestic.parquet
    stress_scenarios_international.parquet
    dfast_results.parquet
    pillar3_disclosures.parquet
    occ_historical.parquet
    variable_crosswalk.parquet
    ... and 14 more (reference, catalog, etc.)
  QUICK_START.md           # this file
  DATA_DICTIONARY.md       # full schema reference
  DATA_SOURCE_INVENTORY.md # all 20 ingested sources
  COVERAGE_GAPS.md         # known data gaps and limitations
```
