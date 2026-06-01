# freenic Data Dictionary

## Overview

- **Total rows**: 2,527,000,000+ (~2.53B)
- **Tables**: 37 (32 main + 5 catalog)
- **Views**: 10 convenience views
- **Variables cataloged**: 13,147
- **Cross-source crosswalk**: 76 variable mappings across 4 sources
- **Temporal coverage**: 1863-2026

> **Updated 2026-06-01 (freeNIC comprehensive update).** Call reports extended to 2025Q4
> (200 quarters, 1.912B rows) via FFIEC CDR bulk; two new tables added
> (`fdic_sdi_features`, `cdr_unrealized_losses`); `occ_historical` span now 1863-1941;
> FDIC SDI/failures/SOD/history and FRED refreshed to latest vintage.

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

### `call_report_filings` — Individual Bank Call Reports (1,912,085,025 rows)

FFIEC 031/041/051 call report data. **1976Q1–2025Q4, 200 quarters.** Pre-2012 from the
Chicago Fed bulk archive (`07`/`07b`); **2012Q1–2025Q4 from the FFIEC Central Data Repository
(CDR) bulk single-period downloads** (`07d_acquire_cdr_call_bulk.py` acquires via Playwright,
`07e_ingest_call_reports_cdr.py` melts the RCFD/RCON/RIAD schedule columns to long format and
appends idempotently). All 56 post-2011 quarters present; the long-standing post-2011 gap is
now closed.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| period_end | DATE | Quarter end date |
| schedule | VARCHAR | Call report schedule (RC, RI, RC-B, etc.) |
| variable_id | VARCHAR | FK → mdrm.variable_id (e.g., RCFD2170) |
| value | DOUBLE | Reported value |
| source_file | VARCHAR | Source file (Chicago Fed XPT pre-2012; FFIEC CDR tab-delimited bulk 2012+) |

### `luck_call_reports` — Luck Historical Database (311,809,300 rows)

Historical call report data from the Luck Database. 24,716 entities, 245 variables, 246 quarters.

| Column | Type | Description |
|--------|------|-------------|
| entity_id | INTEGER | Bank identifier (maps to institutions.rssd_id for ~38%) |
| period_end | DATE | Quarter end date |
| variable_id | VARCHAR | Variable name (Luck-specific naming, e.g., assets, deposits) |
| value | DOUBLE | Reported value |
| source | VARCHAR | Source label |

### `occ_historical` — OCC Balance Sheets 1863-1941 (17,775,763 rows)

National bank balance sheet data from the Office of the Comptroller of the Currency. Original
1867-1904 layer (9,788,940 rows, 7,109 banks, 95 variables, `source='occ'`) plus the Phase 9b
OCC-CLV finhist extension (7,986,823 rows, 14,258 banks, 66 variables, `source='occ_historical_clv'`),
together spanning **1863-11-28 to 1941-12-31**.

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

### `entity_xref` — Canonical RSSD Identity Universe (234,462 rows)

The de-duped UNION of every distinct `rssd_id` that appears in any public NIC/identity table.
Built by `20b_build_entity_xref.py` (CREATE OR REPLACE; non-destructive). **No synthesis** — every
rssd is taken verbatim from a source table; certs are mapped to rssds only via observed cert↔rssd
pairs (`institutions` ∪ `robin_crosswalk` ∪ `bank_failures_enriched`). This is the correct answer to
"is this entity a known NIC identity?" — broader than `institutions` (which under-covers historical
defunct/merged/small filers). Used by `13_validate.py` check #1 (referential) and the referential
test suite. See COVERAGE_GAPS.md §6 for before/after match rates.

Sources unioned: `institutions.rssd_id` ∪ `transformations.rssd_predecessor` ∪
`transformations.rssd_successor` ∪ `crsp_mapping.rssd_id` ∪ `robin_crosswalk.rssd_id` ∪
`robin_crosswalk.rssd_id_bhc` ∪ `bank_failures_enriched.rssd_id` ∪ `fdic_history` (via cert→rssd).
`institutions` contributes 217,210; `transformations` adds the bulk of the remaining 17,252.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | RSSD identity (PK, distinct) |
| source | VARCHAR | Pipe-delimited sorted provenance: which source table(s) contributed this rssd (e.g. `institutions\|transformations_predecessor`) |
| n_sources | INTEGER | Count of distinct source tables vouching for this rssd |

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

### `catalog.variables` — Variable Catalog (13,147 rows)

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

### `catalog.filing_coverage` — Quarterly Coverage (53,394 rows)

| Column | Type | Description |
|--------|------|-------------|
| filing_type | VARCHAR | Filing type |
| period_end | DATE | Quarter end |
| entity_count | INTEGER | Entities filing that quarter |
| variable_count | INTEGER | Variables reported |
| total_observations | INTEGER | Total non-null observations |
| pct_populated | DOUBLE | Sparsity measure |
| source_files | VARCHAR[] | Source files used |

### `catalog.entity_coverage` — Per-Entity Filing History (140,134 rows)

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| filing_type | VARCHAR | Filing type |
| first_filing | DATE | First filing date |
| last_filing | DATE | Last filing date |
| total_filings | INTEGER | Number of filings |

### `catalog.data_sources` — Provenance Tracking (689 rows)

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

### `robin_panel_enriched` (2,867,936 rows)
Robin panel joined with RSSD and FDIC cert identifiers via robin_crosswalk. All 156 Robin columns plus rssd_id, fdic_cert, name_ffiec, match_confidence, ffiec_entity_type, rssd_id_bhc. Use for linking Robin historical data to modern regulatory identifiers.

### `failure_timeline` (17 columns)
Combined failure records from Robin (failed_bank indicator) and FDIC bank_failures, matched via robin_crosswalk. Columns: bank_id, canonical_bank_name, state_abbrev, year, assets, deposits, equity, failed_bank, receivership_date, time_to_fail, bank_run_indicator, rssd_id, fdic_cert, fdic_name, fdic_closing_date, acquiring_institution, fund.

---

## Crosswalk Layer

### `variable_crosswalk` — Cross-Source Variable Mapping (76 rows)

Maps plain-language variable names from Luck, FDIC SDI, Robin, and DFAST to MDRM codes and standardized concept names.

| Column | Type | Description |
|--------|------|-------------|
| source_variable | VARCHAR | Variable name in the source table |
| source_table | VARCHAR | Source table (luck_call_reports, fdic_financials, robin_panel, dfast_results) |
| mdrm_variable | VARCHAR | Corresponding MDRM code (NULL if no direct match) |
| concept | VARCHAR | Standardized concept name (e.g., total_assets, net_income) |
| match_confidence | VARCHAR | Confidence: exact, probable, manual, derived, metadata |
| notes | VARCHAR | Description of the variable |

---

## FDIC Layer

### `bank_failures` — Failed Bank List (4,115 rows)

All FDIC-insured bank failures from 1934 to present (latest 2026-05-01), sourced from the FDIC
BankFind API. **`state_code` is now fully populated** (PSTALP from BankFind; 54 distinct states,
previously NULL).

| Column | Type | Description |
|--------|------|-------------|
| cert | INTEGER | FDIC certificate number (FK → institutions.fdic_cert) |
| bank_name | VARCHAR | Bank name at time of failure |
| city | VARCHAR | City |
| state_code | VARCHAR | State abbreviation (PSTALP; populated for all 4,115 rows) |
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

### `fdic_financials` — FDIC Statistics on Depository Institutions (69,455,560 rows)

Quarterly financial data for all FDIC-insured institutions from 1984Q1 to 2026Q1. 24,060 institutions, 58 pre-computed financial variables, 169 quarters. Long format (one row per institution/quarter/variable).

| Column | Type | Description |
|--------|------|-------------|
| fdic_cert | INTEGER | FDIC certificate number |
| rssd_id | INTEGER | FK → institutions (39.7% matched) |
| period_end | DATE | Quarter end date |
| variable_id | VARCHAR | FDIC variable name (e.g., ASSET, DEP, EQ, ROA) |
| value | DOUBLE | Reported value |
| source | VARCHAR | Data source ('fdic_sdi') |

**Key variables**: ASSET (total assets), DEP (total deposits), EQ (equity capital), NETINC (net income), INTINC (interest income), ROA (return on assets), ROE (return on equity), NIM (net interest margin), RBC1AAJ (tier 1 risk-based capital ratio)

### `fdic_sod` — FDIC Summary of Deposits (2,815,984 rows)

Branch-level deposit data from the FDIC Summary of Deposits survey. 15,505 institutions, 294,035 unique branches, 32 years (1994-2025, complete through 2025).

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

### `fdic_history` — Institution History Events (582,628 rows)

All FDIC-recorded institution history events (name changes, mergers, charter conversions, openings, closings).

| Column | Type | Description |
|--------|------|-------------|
| fdic_cert | INTEGER | FDIC certificate number |
| institution_name | VARCHAR | Institution name at time of event |
| change_code | INTEGER | Event type code |
| change_desc | VARCHAR | Event description (e.g., "Name Change", "Merger", "Failure") |
| effective_date | DATE | Event date |
| city | VARCHAR | City |
| state_code | VARCHAR | State abbreviation |
| county | VARCHAR | County name |
| class_code | VARCHAR | Charter class code |
| process_date | DATE | FDIC processing date |

### `fred_series` — FRED Banking & Macro Series (75,257 rows)

15 FRED time series providing macroeconomic context (1919-2026, latest obs 2026-05-29): bank credit, deposits, interest rates, GDP, unemployment.

| Column | Type | Description |
|--------|------|-------------|
| series_id | VARCHAR | FRED series ID (e.g., TOTBKCR, FEDFUNDS, GDP) |
| observation_date | DATE | Observation date |
| value | DOUBLE | Observed value |
| series_name | VARCHAR | Human-readable series name |

---

## CLV Feature Layer

Engineered analysis panels promoted to permanent freeNIC tables from the W16 CLV campaign
(May 2026). Both are derived **from** other freeNIC sources (FDIC SDI, FFIEC CDR) and are also
exported to parquet (sorted, ZSTD). The regenerable analysis panels (e.g. `public_luck_panel`)
remain Volcker-only and are intentionally NOT promoted here.

### `fdic_sdi_features` — FDIC-SDI Engineered Feature Panel (413,130 rows)

Bank-year engineered ratios and failure flags derived from `fdic_financials` (FDIC SDI).
**1984-2025 (annual, Q4 snapshot), 42 years, 23,065 entities.** Built by
`31_build_sdi_feature_panel.py`. Asset totals reconcile to `fdic_financials` within ~0.35%.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | INTEGER | FK → institutions |
| year | INTEGER | Observation year (Q4 snapshot) |
| assets | DOUBLE | Total assets |
| income_ratio | DOUBLE | Net income / assets ratio |
| noncore_proxy | DOUBLE | Noncore funding proxy |
| uninsured_ratio | DOUBLE | Uninsured deposits / total deposits |
| insured_ratio | DOUBLE | Insured deposits / total deposits |
| securities_ratio | DOUBLE | Securities / assets |
| equity_ratio | DOUBLE | Equity / assets |
| nim | DOUBLE | Net interest margin |
| nim_ratio | DOUBLE | Net interest margin ratio |
| roa | DOUBLE | Return on assets |
| log_age | DOUBLE | Log of institution age |
| F1_failure | DOUBLE | Failure flag, 1-year horizon |
| F3_failure | DOUBLE | Failure flag, 3-year horizon |
| F5_failure | DOUBLE | Failure flag, 5-year horizon |

### `cdr_unrealized_losses` — FFIEC CDR Unrealized-Loss Layer (46,929 rows)

AFS/HTM fair-value, AOCI, and brokered-deposit detail parsed from FFIEC CDR call-report bulk.
**2019-2025 (Q4 by year), 5,290 entities.** Built by `33_parse_cdr_unrealized.py` (CDR bulk
acquired by `32_acquire_cdr_unrealized.py`). MDRMs verified against issuer 10-Ks
(HTM fair value = RCFD1771, brokered = RCON2365). SVB 2022Q4 reconciles to its disclosed
~$15B HTM unrealized loss.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id | BIGINT | FK → institutions |
| cert | BIGINT | FDIC certificate number |
| period_end | TIMESTAMP_MS | Quarter end (Q4 by year) |
| year | BIGINT | Observation year |
| afs_amort_cost | DOUBLE | Available-for-sale amortized cost |
| afs_fair_value | DOUBLE | Available-for-sale fair value |
| htm_amort_cost | DOUBLE | Held-to-maturity amortized cost |
| htm_fair_value | DOUBLE | Held-to-maturity fair value (RCFD1771) |
| afs_unrealized_loss | DOUBLE | AFS unrealized loss (fair value − amortized cost) |
| htm_unrealized_loss | DOUBLE | HTM unrealized loss (fair value − amortized cost) |
| total_unrealized_loss | DOUBLE | AFS + HTM unrealized loss |
| aoci | DOUBLE | Accumulated other comprehensive income |
| brokered_deposits | DOUBLE | Brokered deposits (RCON2365) |
| time_dep_100_250k | DOUBLE | Time deposits $100k–$250k |
| time_dep_gt_250k | DOUBLE | Time deposits > $250k |

---

## Robin Panel Layer

### `robin_panel` — Robin Failing Banks Annual Panel (2,867,936 rows)

Annual bank-level data from the Robin Failing Banks database. 39,299 banks, 156 variables, 1863-2024. Provides the deepest historical coverage in freenic, filling the 1905-1958 gap at annual granularity.

| Column | Type | Description |
|--------|------|-------------|
| bank_id | DOUBLE | Robin bank identifier |
| canonical_bank_name | VARCHAR | Standardized bank name |
| city_name | VARCHAR | City |
| state_abbrev | VARCHAR | State abbreviation |
| year | BIGINT | Observation year |
| charter | VARCHAR | Charter type |
| assets | DOUBLE | Total assets |
| deposits | DOUBLE | Total deposits |
| loans | DOUBLE | Total loans |
| equity | DOUBLE | Total equity |
| capital | VARCHAR | Capital |
| surplus | VARCHAR | Surplus |
| liquid | DOUBLE | Liquid assets |
| oreo | VARCHAR | Other real estate owned |
| failed_bank | BIGINT | Failure indicator (1 = failed) |
| time_to_fail | DOUBLE | Years until failure |
| call_date | DATE | Call report date |
| ... | ... | 139 additional financial, macro, and risk variables |

### `robin_deposits_historical` — Pre-FDIC Deposit Dynamics (2,961 rows)

Deposit and asset data at suspension for pre-FDIC failed banks. Includes receivership outcomes (collections, dividends, offsets).

| Column | Type | Description |
|--------|------|-------------|
| failure_id | BIGINT | Failure event identifier |
| charter | DOUBLE | Charter type |
| deposits_at_suspension | DOUBLE | Deposits at time of suspension |
| assets_at_suspension | DOUBLE | Assets at time of suspension |
| simplified_cause_of_failure | VARCHAR | Cause of failure |
| collected_from_assets | DOUBLE | Amount collected from asset liquidation |
| dividends | DOUBLE | Dividends paid to depositors |
| ... | ... | 71 additional receivership and recovery columns |

### `robin_deposits_modern` — Modern Deposit Dynamics (547 rows)

Deposit dynamics for modern (post-FDIC) bank failures. Includes bank run indicators, brokered deposits, and funding structure.

| Column | Type | Description |
|--------|------|-------------|
| bank_id | DOUBLE | Robin bank identifier |
| year | BIGINT | Year |
| quarter | DATE | Quarter date |
| assets | DOUBLE | Total assets |
| deposits | DOUBLE | Total deposits |
| failed_bank | BIGINT | Failure indicator |
| deposits_time | DOUBLE | Time deposits |
| deposits_demand | DOUBLE | Demand deposits |
| brokered_dep | DOUBLE | Brokered deposits |
| otherbor_liab | DOUBLE | Other borrowed liabilities |
| ... | ... | 37 additional funding and risk columns |

### `robin_crosswalk` — Robin ↔ RSSD/FDIC Mapping (14,286 rows)

Maps Robin bank_id to FFIEC RSSD IDs and FDIC certificate numbers. 6.5% match rate to institutions table (expected — most Robin IDs are pre-NIC historical banks).

| Column | Type | Description |
|--------|------|-------------|
| bank_id_robin | INTEGER | Robin bank identifier |
| charter_robin | INTEGER | Robin charter number |
| rssd_id | INTEGER | FK → institutions (NULL if no match) |
| fdic_cert | INTEGER | FDIC certificate number |
| canonical_name_robin | VARCHAR | Robin bank name |
| name_ffiec | VARCHAR | FFIEC institution name |
| match_method | VARCHAR | How match was determined |
| match_confidence | DOUBLE | Match confidence score |
| robin_year_min | INTEGER | First year in Robin data |
| robin_year_max | INTEGER | Last year in Robin data |
| entity_type | VARCHAR | FFIEC entity type |
| is_bhc | BOOLEAN | Bank holding company flag |
| failed | INTEGER | Failure flag |
| rssd_id_bhc | INTEGER | Parent BHC RSSD ID |

---

## BHC & Sector Layer

### `bhc_ownership` — BHC Ownership Hierarchy (36,668 rows)

Parent-child ownership relationships for bank holding companies. Includes equity percentages and hierarchy levels.

| Column | Type | Description |
|--------|------|-------------|
| rssd_id_bhc | INTEGER | Parent BHC RSSD ID |
| rssd_id_bank | INTEGER | Subsidiary bank RSSD ID |
| fdic_cert | INTEGER | FDIC certificate number |
| hierarchy_level | INTEGER | Level in ownership tree |
| relationship_type | VARCHAR | Relationship type |
| pct_equity | DOUBLE | Equity ownership percentage |
| nm_lgl | VARCHAR | Legal name |
| nm_short | VARCHAR | Short name |
| city | VARCHAR | City |
| state_abbr | VARCHAR | State abbreviation |
| entity_type | VARCHAR | Entity type code |
| is_bhc | BOOLEAN | BHC indicator |
| is_primary_bank | BOOLEAN | Primary bank indicator |
| status | VARCHAR | Active/Inactive status |

### `sector_groupings` — CIK→SIC→Sector Classifications (16,548 rows)

Maps SEC CIK identifiers to SIC codes and sector groups. Useful for classifying BHCs by industry sector.

| Column | Type | Description |
|--------|------|-------------|
| cik | VARCHAR | SEC CIK identifier |
| ticker | VARCHAR | Stock ticker |
| company_name | VARCHAR | Company name |
| sic_code | DOUBLE | SIC industry code |
| sector_group | VARCHAR | Sector classification |

---

## Stress Testing & Disclosure Layer

### `stress_scenarios_domestic` — Fed Domestic Stress Scenarios (226 rows)

Federal Reserve stress test domestic macroeconomic scenario definitions. Quarterly projections for GDP, unemployment, rates, house prices, etc.

| Column | Type | Description |
|--------|------|-------------|
| Scenario Name | VARCHAR | Scenario (Baseline, Adverse, Severely Adverse) |
| Date | VARCHAR | Projection quarter |
| Real GDP growth | DOUBLE | Real GDP growth rate (%) |
| Unemployment rate | DOUBLE | Unemployment rate (%) |
| CPI inflation rate | DOUBLE | CPI inflation rate (%) |
| 3-month Treasury rate | DOUBLE | 3-month T-bill rate (%) |
| 10-year Treasury yield | DOUBLE | 10-year Treasury yield (%) |
| BBB corporate yield | DOUBLE | BBB corporate bond yield (%) |
| Mortgage rate | DOUBLE | 30-year mortgage rate (%) |
| House Price Index (Level) | DOUBLE | HPI level index |
| ... | ... | 8 additional domestic macro variables |

### `stress_scenarios_international` — Fed International Stress Scenarios (226 rows)

Federal Reserve stress test international macroeconomic scenario definitions.

| Column | Type | Description |
|--------|------|-------------|
| Scenario Name | VARCHAR | Scenario (Baseline, Adverse, Severely Adverse) |
| Date | VARCHAR | Projection quarter |
| Euro area real GDP growth | DOUBLE | Euro area GDP growth (%) |
| Euro area inflation | DOUBLE | Euro area CPI (%) |
| Euro area bilateral dollar exchange rate (USD/euro) | DOUBLE | USD/EUR exchange rate |
| Japan real GDP growth | DOUBLE | Japan GDP growth (%) |
| U.K. real GDP growth | DOUBLE | UK GDP growth (%) |
| ... | ... | 7 additional international variables |

---

## Stress Testing & Disclosure Layer (continued)

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
