# freenic Data Dictionary

## Overview

- **Total rows**: 1,499,110,463
- **Tables**: 24 (19 main + 5 catalog)
- **Views**: 8 convenience views
- **Variables cataloged**: 9,375 (84.6% matched to MDRM)
- **Cross-source crosswalk**: 64 variable mappings across 3 sources
- **Temporal coverage**: 1867-2025

---

## Reference Layer

### `mdrm` — Master Data Reference Manual (87,351 rows)

The FFIEC variable dictionary. Maps every regulatory variable code to its human-readable name, description, and reporting context.

| Column | Type | Description |
|--------|------|-------------|
| mnemonic | VARCHAR | Variable prefix (BHCK, BHCP, RCFD, RCON, RIAD, etc.) |
| item_code | VARCHAR | Numeric item code |
| variable_id | VARCHAR | Full ID = mnemonic + item_code (e.g., BHCK2170) |
| item_name | VARCHAR | Human-readable variable name |
| start_date | DATE | First reporting period |
| end_date | DATE | Last reporting period (NULL if still active) |
| confidentiality | VARCHAR | Confidentiality classification |
| item_type | VARCHAR | Data type (numeric, character, date) |
| reporting_form | VARCHAR | Source form (FR Y-9C, FFIEC 031, etc.) |
| description | VARCHAR | Full text description |
| series_glossary | VARCHAR | Glossary reference |

### `reporting_forms` — Distinct Form Types (180 rows)

| Column | Type | Description |
|--------|------|-------------|
| form_code | VARCHAR | Form identifier |
| form_name | VARCHAR | Full form name |
| filing_type | VARCHAR | Filing type category |

---

## Entity Layer

### `institutions` — Master Entity Table (217,210 rows)

All bank holding companies, banks, and financial institutions from the NIC database. 59,824 active + 157,386 closed/merged.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | **Primary key.** Federal Reserve RSSD identifier |
| name_legal | VARCHAR | Legal name |
| name_short | VARCHAR | Short name |
| entity_type | VARCHAR | Entity type code (FHD, BHC, SMB, NMB, etc.) |
| charter_type | INTEGER | Charter type code |
| charter_auth | INTEGER | Chartering authority |
| city | VARCHAR | Headquarters city |
| state_code | VARCHAR | State abbreviation |
| country | VARCHAR | Country code |
| fdic_cert | INTEGER | FDIC certificate number |
| date_established | DATE | Date established |
| date_terminated | DATE | Date terminated (NULL if active) |
| primary_fed_reg | VARCHAR | Primary federal regulator |
| is_active | BOOLEAN | Currently active flag |
| source_file | VARCHAR | Source data file |

### `institution_attributes` — Time-Varying Attributes (217,210 rows)

Regulatory status indicators with effective date ranges.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| dt_start | VARCHAR | Effective start date |
| dt_end | VARCHAR | Effective end date |
| bhc_ind | INTEGER | Bank holding company indicator |
| fhc_ind | INTEGER | Financial holding company indicator |
| slhc_ind | INTEGER | Savings & loan holding company indicator |
| broad_reg_cd | INTEGER | Broad regulatory code |
| insur_pri_cd | INTEGER | Primary insurance code |
| mbr_frs_ind | INTEGER | Federal Reserve member indicator |
| mbr_fhlbs_ind | INTEGER | Federal Home Loan Bank member indicator |
| sec_rptg_status | INTEGER | SEC reporting status |
| bank_cnt | INTEGER | Number of controlled banks |
| source | VARCHAR | Source file |

### `branches` — Branch Locations (173,250 rows)

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | Branch RSSD ID |
| head_office_rssd | INTEGER | FK → institutions (parent) |
| dt_start | VARCHAR | Branch open date |
| dt_end | VARCHAR | Branch close date |
| branch_name | VARCHAR | Branch name |
| city | VARCHAR | City |
| state_code | VARCHAR | State |
| country | VARCHAR | Country |
| entity_type | VARCHAR | Entity type |

### `relationships` — Parent-Child Ownership (286,223 rows)

Corporate hierarchy. Use `current_hierarchy` view for active-only.

| Column | Type | Description |
|--------|------|-------------|
| rssd_parent | INTEGER | FK → institutions (parent entity) |
| rssd_offspring | INTEGER | FK → institutions (subsidiary) |
| dt_start | DATE | Relationship start date |
| dt_end | DATE | Relationship end date (NULL if current) |
| relationship_level | INTEGER | Hierarchy level |
| control_ind | INTEGER | Control indicator |
| equity_ind | INTEGER | Equity investment indicator |
| pct_equity | DOUBLE | Equity ownership percentage |
| pct_other | DOUBLE | Other ownership percentage |

### `transformations` — Mergers & Acquisitions (58,935 rows)

| Column | Type | Description |
|--------|------|-------------|
| rssd_predecessor | INTEGER | FK → institutions (acquired entity) |
| rssd_successor | INTEGER | FK → institutions (acquiring entity) |
| dt_trans | DATE | Transaction date |
| transform_code | INTEGER | Transformation type code |
| acct_method | INTEGER | Accounting method code |

---

## Filing Layer (Long Format)

All filing tables use **long format**: one row per entity/period/variable observation.

### `bhcf_filings` — Bank Holding Company Financial Data (208,147,772 rows)

FR Y-9C and related BHC financial data. 13,668 entities, 3,208 variables, 158 quarters.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| period_end | DATE | Quarter end date (YYYY-MM-DD) |
| variable_id | VARCHAR | FK → mdrm.variable_id (e.g., BHCK2170) |
| value | DOUBLE | Reported value |
| source_file | VARCHAR | Source data file |

**Key variables**: BHCK2170 (total assets), BHCK2948 (total equity capital), BHCK4340 (net income), BHCK4074 (total interest income)

### `call_report_filings` — Individual Bank Call Reports (896,251,036 rows)

FFIEC 031/041/051 call report data from Chicago Fed. 22,185 entities, 4,473 variables, 101 quarters.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| period_end | DATE | Quarter end date |
| schedule | VARCHAR | Call report schedule (RC, RI, RC-B, etc.) |
| variable_id | VARCHAR | FK → mdrm.variable_id (e.g., RCFD2170) |
| value | DOUBLE | Reported value |
| source_file | VARCHAR | Source XPT file |

### `luck_call_reports` — Luck Historical Database (311,809,300 rows)

Historical call report data from the Luck Database. 24,716 entities, 245 variables, 246 quarters.

| Column | Type | Description |
|--------|------|-------------|
| entity_id | INTEGER | Bank identifier (maps to institutions.rssd_id for ~38%) |
| period_end | DATE | Quarter end date |
| variable_id | VARCHAR | Variable name (Luck-specific naming, e.g., assets, deposits) |
| value | DOUBLE | Reported value |
| source | VARCHAR | Source label |

### `occ_historical` — OCC Balance Sheets 1867-1904 (9,788,940 rows)

National bank balance sheet data from the Office of the Comptroller of the Currency. 7,109 banks, 95 variables.

| Column | Type | Description |
|--------|------|-------------|
| bank_id | INTEGER | OCC bank identifier |
| report_date | DATE | Report date |
| variable_id | VARCHAR | Variable name (e.g., assets, deposits, securities) |
| value | DOUBLE | Reported value |
| source | VARCHAR | Source label |

---

## Crosswalk Layer

### `crsp_mapping` — CRSP-FRB Link (18,908 rows)

Maps CRSP stock identifiers (PERMCO) to Federal Reserve RSSD IDs. Compiled from 16 CRSP vintage files.

| Column | Type | Description |
|--------|------|-------------|
| permco | INTEGER | CRSP permanent company identifier |
| rssd_id | INTEGER | FK → institutions |
| name | VARCHAR | Company name (from CRSP) |
| inst_type | VARCHAR | Institution type |
| dt_start | DATE | Link start date |
| dt_end | DATE | Link end date |
| source_file | VARCHAR | CRSP vintage file |

### `filing_metadata` — Filing Coverage Summary (259 rows)

| Column | Type | Description |
|--------|------|-------------|
| filing_type | VARCHAR | Filing type (bhcf, call_report, luck, occ) |
| period_end | DATE | Quarter/period |
| source_file | VARCHAR | Source file |
| entity_count | INTEGER | Number of reporting entities |
| variable_count | INTEGER | Number of variables reported |
| ingestion_ts | TIMESTAMP | When data was ingested |

---

## Catalog Schema (`catalog.*`)

### `catalog.variables` — Variable Catalog (9,375 rows)

Every unique variable observed across all filing types.

| Column | Type | Description |
|--------|------|-------------|
| variable_id | VARCHAR | Unique variable identifier |
| mnemonic | VARCHAR | MDRM mnemonic (NULL if unmatched) |
| item_code | VARCHAR | MDRM item code |
| canonical_name | VARCHAR | Human-readable name |
| filing_types | VARCHAR[] | Array of filing types containing this variable |
| first_observed | DATE | Earliest observation |
| last_observed | DATE | Latest observation |
| quarters_available | INTEGER | Number of quarters with data |
| entities_reporting | INTEGER | Number of entities reporting this variable |
| pct_non_null | DOUBLE | Population rate |
| confidentiality | VARCHAR | MDRM confidentiality flag |
| description_short | VARCHAR | Truncated description (200 chars) |
| description_full | VARCHAR | Full MDRM description |
| schedule | VARCHAR | Reporting schedule |

### `catalog.filing_coverage` — Quarterly Coverage (724 rows)

| Column | Type | Description |
|--------|------|-------------|
| filing_type | VARCHAR | Filing type |
| period_end | DATE | Quarter end |
| entity_count | INTEGER | Entities filing that quarter |
| variable_count | INTEGER | Variables reported |
| total_observations | INTEGER | Total non-null observations |
| pct_populated | DOUBLE | Sparsity measure |
| source_files | VARCHAR[] | Source files used |

### `catalog.entity_coverage` — Per-Entity Filing History (91,782 rows)

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| filing_type | VARCHAR | Filing type |
| first_filing | DATE | First filing date |
| last_filing | DATE | Last filing date |
| total_filings | INTEGER | Number of filings |

### `catalog.data_sources` — Provenance Tracking (581 rows)

| Column | Type | Description |
|--------|------|-------------|
| source_id | VARCHAR | Unique source identifier |
| file_path | VARCHAR | Original file path |
| file_type | VARCHAR | File format (CSV, TXT, XPT, DTA, TSV) |
| file_size_bytes | BIGINT | File size |
| row_count | INTEGER | Rows ingested |
| column_count | INTEGER | Columns in source |
| date_range | VARCHAR | Temporal coverage |
| description | VARCHAR | Source description |
| ingestion_ts | TIMESTAMP | Ingestion timestamp |
| ingestion_script | VARCHAR | Script that ingested this source |
| checksum_sha256 | VARCHAR | File checksum |

### `catalog.schema_evolution` — Variable Lifecycle (9,375 rows)

| Column | Type | Description |
|--------|------|-------------|
| variable_id | VARCHAR | Variable identifier |
| first_quarter | DATE | First quarter variable appears |
| last_quarter | DATE | Last quarter variable appears |
| quarters_present | INTEGER | Total quarters present |

---

## Convenience Views

### `bhcf_enriched`
BHCF filings joined with institution names and MDRM variable descriptions. Use this instead of manual joins for enriched analysis.

### `current_hierarchy`
Active parent-child relationships only (dt_end IS NULL). Includes institution names for both parent and subsidiary.

### `entity_summary`
Per-entity summary with filing counts, date ranges, and coverage metrics.

### `variable_dictionary`
Variables with full MDRM descriptions and coverage statistics. Use for data discovery.

### `bank_failures_enriched` (4,119 rows)
Bank failures joined with institution details (RSSD ID, entity type, primary federal regulator).

### `deposit_market_share` (822,652 rows)
Per-institution annual deposit market share by state and county, computed from FDIC Summary of Deposits.

### `stress_test_summary` (18,581 rows)
DFAST results filtered to Severely Adverse scenario only — the binding constraint for regulatory capital planning.

### `cross_source_financials` (118,462,126 rows)
Unified financial data across BHCF, Luck, and FDIC SDI via the variable crosswalk. Enables concept-level queries (e.g., "total_assets") that automatically span all sources. Columns: rssd_id, institution_name, period_end, concept, source_variable, source_table, value.

---

## Crosswalk Layer

### `variable_crosswalk` — Cross-Source Variable Mapping (64 rows)

Maps plain-language variable names from Luck, FDIC SDI, and DFAST to MDRM codes and standardized concept names.

| Column | Type | Description |
|--------|------|-------------|
| source_variable | VARCHAR | Variable name in the source table |
| source_table | VARCHAR | Source table (luck_call_reports, fdic_financials, dfast_results) |
| mdrm_variable | VARCHAR | Corresponding MDRM code (NULL if no direct match) |
| concept | VARCHAR | Standardized concept name (e.g., total_assets, net_income) |
| match_confidence | VARCHAR | Confidence: exact, probable, manual, derived, metadata |
| notes | VARCHAR | Description of the variable |

---

## FDIC Layer

### `bank_failures` — Failed Bank List (4,114 rows)

All FDIC-insured bank failures from 1934 to present, sourced from the FDIC BankFind API.

| Column | Type | Description |
|--------|------|-------------|
| cert | INTEGER | FDIC certificate number (FK → institutions.fdic_cert) |
| bank_name | VARCHAR | Bank name at time of failure |
| city | VARCHAR | City |
| state_code | VARCHAR | State abbreviation |
| closing_date | DATE | Date the bank was closed |
| failure_year | INTEGER | Year of failure |
| acquiring_institution | VARCHAR | Name of acquiring institution |
| acquiring_city | VARCHAR | Acquirer city |
| acquiring_state | VARCHAR | Acquirer state |
| fund | INTEGER | FDIC fund identifier |
| total_deposits | DOUBLE | Total deposits at failure (thousands) |
| total_assets | DOUBLE | Total assets at failure (thousands) |
| estimated_loss | DOUBLE | Estimated loss to FDIC (thousands) |
| resolution_type | VARCHAR | Resolution method |
| charter_class | VARCHAR | Charter class at failure |
| source | VARCHAR | Data source ('fdic_api') |

### `fdic_financials` — FDIC Statistics on Depository Institutions (69,272,714 rows)

Quarterly financial data for all FDIC-insured institutions from 1984-2025. 24,056 institutions, 58 pre-computed financial variables, 168 quarters. Long format (one row per institution/quarter/variable).

| Column | Type | Description |
|--------|------|-------------|
| fdic_cert | INTEGER | FDIC certificate number |
| rssd_id | INTEGER | FK → institutions (39.7% matched) |
| period_end | DATE | Quarter end date |
| variable_id | VARCHAR | FDIC variable name (e.g., ASSET, DEP, EQ, ROA) |
| value | DOUBLE | Reported value |
| source | VARCHAR | Data source ('fdic_sdi') |

**Key variables**: ASSET (total assets), DEP (total deposits), EQ (equity capital), NETINC (net income), INTINC (interest income), ROA (return on assets), ROE (return on equity), NIM (net interest margin), RBC1AAJ (tier 1 risk-based capital ratio)

### `fdic_sod` — FDIC Summary of Deposits (2,740,878 rows)

Branch-level deposit data from the FDIC Summary of Deposits survey. 15,505 institutions, 294,035 unique branches, 32 years (1994-2025).

| Column | Type | Description |
|--------|------|-------------|
| fdic_cert | INTEGER | FDIC certificate number (FK → institutions.fdic_cert) |
| rssd_id | INTEGER | Federal Reserve RSSD ID |
| year | INTEGER | Survey year |
| branch_num | INTEGER | FDIC branch number |
| uninumbr | INTEGER | Unique branch identifier |
| branch_name | VARCHAR | Branch name |
| address | VARCHAR | Street address |
| city | VARCHAR | City |
| state_code | VARCHAR | State abbreviation |
| state_name | VARCHAR | Full state name |
| zip_code | VARCHAR | ZIP code |
| county | VARCHAR | County name |
| county_num | INTEGER | FIPS county number |
| latitude | DOUBLE | Branch latitude |
| longitude | DOUBLE | Branch longitude |
| branch_deposits | DOUBLE | Branch deposits (thousands) |
| inst_deposits | DOUBLE | Total institution deposits (thousands) |
| domestic_deposits | DOUBLE | Domestic deposits (thousands) |
| total_assets | DOUBLE | Institution total assets (thousands) |
| hc_name | VARCHAR | Holding company name |
| hc_rssd_id | INTEGER | Holding company RSSD ID |
| bank_class | VARCHAR | Bank class code |
| charter_type | VARCHAR | Charter type |
| regulator | VARCHAR | Primary federal regulator |
| source | VARCHAR | Data source ('fdic_sod') |

---

## Stress Testing & Disclosure Layer

### `dfast_results` — DFAST Stress Test Results (28,231 rows)

Federal Reserve Dodd-Frank Act Stress Test results. 43 banks, 13 years (2013-2025), 3 scenarios, 56 variables.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| bank_name | VARCHAR | Bank name (as disclosed) |
| year | INTEGER | Exercise year |
| exercise_name | VARCHAR | Exercise name (e.g., "DFAST 2025") |
| scenario | VARCHAR | Scenario (Baseline, Adverse, Severely Adverse) |
| variable_id | VARCHAR | Variable name (e.g., common_equity_tier1_min_rat) |
| value | DOUBLE | Projected/actual value |
| source | VARCHAR | Data source ('dfast') |

**Key variables**: `common_equity_tier1_min_rat` (CET1 minimum ratio), `tier1_capital_min_rat` (Tier 1 minimum), `loss_total_loan_amt` (total loan losses $B), `revenue_preprovision_net_amt` (PPNR $B)

### `pillar3_disclosures` — G-SIB Pillar 3 Disclosures (7,952 rows)

Quarterly Basel III Pillar 3 regulatory disclosures for 5 G-SIBs (JPM, BAC, C, WFC, MS). Parsed from HDARP-extracted CSV tables.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| bank_name | VARCHAR | Bank name |
| period_end | DATE | Quarter end date |
| disclosure_type | VARCHAR | Category: capital, rwa, ratios, slr, tlac, credit_risk, market_risk, operational_risk, other |
| table_name | VARCHAR | Source table title |
| variable_id | VARCHAR | Row label from disclosure table |
| value | DOUBLE | Reported value |
| unit | VARCHAR | Unit: millions, percent |
| source_file | VARCHAR | Source CSV file name |

---

## Variable Naming Conventions

| Prefix | Meaning | Source |
|--------|---------|--------|
| BHCK | BHC Consolidated (domestic + foreign) | FR Y-9C |
| BHCP | BHC Parent Only | FR Y-9C |
| RCFD | Call Report (domestic + foreign offices) | FFIEC 031 |
| RCON | Call Report (domestic offices only) | FFIEC 041 |
| RIAD | Call Report Income/Expense (annualized) | FFIEC 031/041 |
| (no prefix) | Luck Database uses plain names (assets, deposits, etc.) | Luck DB |

## Entity Type Codes

| Code | Description |
|------|-------------|
| FHD | Financial Holding Company (Domestic) |
| BHC | Bank Holding Company |
| SMB | State Member Bank |
| NMB | National Member Bank |
| SSB | State Savings Bank |
| SLA | Savings & Loan Association |
| IHC | Intermediate Holding Company |
