# Internal helper to read a Parquet table
.read_table <- function(table_name, columns = NULL) {
  check_installed("arrow", reason = "to read freenic Parquet files")
  path <- file.path(freenic_data_dir(), paste0(table_name, ".parquet"))
  if (!file.exists(path)) {
    abort(paste("Parquet file not found:", path))
  }
  if (!is.null(columns)) {
    check_installed("dplyr", reason = "for column selection")
    arrow::read_parquet(path, col_select = dplyr::all_of(columns))
  } else {
    arrow::read_parquet(path)
  }
}

# --- Reference Tables ---

#' Read the MDRM variable dictionary
#'
#' FFIEC Master Data Reference Manual. 87,351 variable codes with
#' descriptions, reporting forms, and date ranges.
#'
#' @param columns Character vector of column names to select (NULL = all).
#' @return A tibble.
#' @export
#' @examplesIf freenic_data_available()
#' read_mdrm() |> head()
read_mdrm <- function(columns = NULL) .read_table("mdrm", columns)

#' Read the reporting forms table
#'
#' Distinct regulatory form types (180 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_reporting_forms <- function(columns = NULL) .read_table("reporting_forms", columns)

# --- Entity Tables ---

#' Read the institutions table
#'
#' All bank holding companies, banks, and financial institutions
#' from NIC. 217,210 rows including 59,824 active entities.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
#' @examplesIf freenic_data_available()
#' read_institutions() |> head()
read_institutions <- function(columns = NULL) .read_table("institutions", columns)

#' Read institution attributes
#'
#' Time-varying regulatory status indicators (217,210 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_institution_attributes <- function(columns = NULL) .read_table("institution_attributes", columns)

#' Read branch locations
#'
#' 173,250 branch locations with open/close dates.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_branches <- function(columns = NULL) .read_table("branches", columns)

#' Read parent-child ownership relationships
#'
#' 286,223 corporate hierarchy relationships with equity percentages.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_relationships <- function(columns = NULL) .read_table("relationships", columns)

#' Read mergers and acquisitions
#'
#' 58,935 transformation records (mergers, acquisitions, charter changes).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_transformations <- function(columns = NULL) .read_table("transformations", columns)

#' Read CRSP-FRB link mapping
#'
#' Maps CRSP PERMCO stock identifiers to RSSD IDs (18,908 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_crsp_mapping <- function(columns = NULL) .read_table("crsp_mapping", columns)

# --- Filing Tables (Long Format) ---

#' Read BHC financial filings (Y-9C)
#'
#' 208 million rows of bank holding company financial data, 1986-2025.
#' Long format: one row per entity/period/variable.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_bhcf_filings <- function(columns = NULL) .read_table("bhcf_filings", columns)

#' Read individual bank call reports
#'
#' 896 million rows from Chicago Fed, 1976-2002.
#' Long format: one row per entity/period/variable.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_call_report_filings <- function(columns = NULL) .read_table("call_report_filings", columns)

#' Read Luck Historical Database
#'
#' 312 million rows of historical call report data, 1959-2025.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_luck_call_reports <- function(columns = NULL) .read_table("luck_call_reports", columns)

#' Read OCC historical balance sheets
#'
#' National bank balance sheets 1867-1904 (9.8 million rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_occ_historical <- function(columns = NULL) .read_table("occ_historical", columns)

#' Read filing metadata
#'
#' Filing coverage summary (259 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_filing_metadata <- function(columns = NULL) .read_table("filing_metadata", columns)

# --- FDIC Tables ---

#' Read bank failures
#'
#' All FDIC-insured bank failures 1934-2026 (4,114 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
#' @examplesIf freenic_data_available()
#' read_bank_failures() |> head()
read_bank_failures <- function(columns = NULL) .read_table("bank_failures", columns)

#' Read FDIC SDI quarterly financials
#'
#' 69 million rows of individual bank financials, 1984-2025.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_fdic_financials <- function(columns = NULL) .read_table("fdic_financials", columns)

#' Read FDIC Summary of Deposits
#'
#' Branch-level deposit data, 1994-2025 (2.7 million rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_fdic_sod <- function(columns = NULL) .read_table("fdic_sod", columns)

#' Read FDIC institution history events
#'
#' 581,588 events (name changes, mergers, failures, etc.).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_fdic_history <- function(columns = NULL) .read_table("fdic_history", columns)

# --- Stress Testing & Disclosure ---

#' Read DFAST stress test results
#'
#' Federal Reserve stress test results 2013-2025 (28,231 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_dfast_results <- function(columns = NULL) .read_table("dfast_results", columns)

#' Read Pillar 3 G-SIB disclosures
#'
#' Basel III Pillar 3 disclosures for 5 G-SIBs (7,952 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_pillar3_disclosures <- function(columns = NULL) .read_table("pillar3_disclosures", columns)

#' Read domestic stress test scenarios
#'
#' Fed domestic macroeconomic scenario definitions (226 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_stress_scenarios_domestic <- function(columns = NULL) .read_table("stress_scenarios_domestic", columns)

#' Read international stress test scenarios
#'
#' Fed international macroeconomic scenario definitions (226 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_stress_scenarios_international <- function(columns = NULL) .read_table("stress_scenarios_international", columns)

# --- Robin Panel ---

#' Read Robin Failing Banks annual panel
#'
#' 2.87 million rows of annual bank-level data, 1863-2024.
#' 39,299 banks, 156 variables.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_robin_panel <- function(columns = NULL) .read_table("robin_panel", columns)

#' Read Robin pre-FDIC deposit dynamics
#'
#' Deposit and asset data at suspension for pre-FDIC failed banks (2,961 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_robin_deposits_historical <- function(columns = NULL) .read_table("robin_deposits_historical", columns)

#' Read Robin modern deposit dynamics
#'
#' Deposit dynamics for post-FDIC bank failures (547 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_robin_deposits_modern <- function(columns = NULL) .read_table("robin_deposits_modern", columns)

#' Read Robin to RSSD/FDIC crosswalk
#'
#' Maps Robin bank_id to RSSD and FDIC cert identifiers (14,286 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_robin_crosswalk <- function(columns = NULL) .read_table("robin_crosswalk", columns)

# --- Other Reference Tables ---

#' Read cross-source variable crosswalk
#'
#' Maps variable names across Luck, FDIC SDI, Robin, and DFAST
#' to standardized concepts (76 entries).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_variable_crosswalk <- function(columns = NULL) .read_table("variable_crosswalk", columns)

#' Read FRED banking and macro series
#'
#' 15 FRED time series (75,037 rows), 1954-2025.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_fred_series <- function(columns = NULL) .read_table("fred_series", columns)

#' Read BHC ownership hierarchy
#'
#' Parent-child ownership for bank holding companies (36,668 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_bhc_ownership <- function(columns = NULL) .read_table("bhc_ownership", columns)

#' Read sector groupings
#'
#' CIK to SIC to sector classifications (16,548 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_sector_groupings <- function(columns = NULL) .read_table("sector_groupings", columns)

# --- Catalog Tables ---

#' Read the variable catalog
#'
#' 9,375 unique variables with metadata from all filing types.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_catalog_variables <- function(columns = NULL) .read_table("catalog_variables", columns)

#' Read quarterly filing coverage
#'
#' Entity and variable counts per quarter per filing type.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_catalog_filing_coverage <- function(columns = NULL) .read_table("catalog_filing_coverage", columns)

#' Read per-entity filing history
#'
#' Per-entity filing coverage across all sources (140,134 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_catalog_entity_coverage <- function(columns = NULL) .read_table("catalog_entity_coverage", columns)

#' Read variable lifecycle tracking
#'
#' When each variable first/last appeared (9,375 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_catalog_schema_evolution <- function(columns = NULL) .read_table("catalog_schema_evolution", columns)

#' Read data provenance tracking
#'
#' Source files and ingestion metadata (589 rows).
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_catalog_data_sources <- function(columns = NULL) .read_table("catalog_data_sources", columns)

# --- Engineered / Cross-Reference Tables ---

#' Read the canonical entity cross-reference
#'
#' Canonical union of all known RSSD identities across every source
#' (institutions, transformations pred/succ, CRSP, FDIC history, Robin
#' crosswalk, enriched bank failures). 234,462 rows. Columns: rssd_id,
#' source (pipe-delimited provenance), n_sources.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_entity_xref <- function(columns = NULL) .read_table("entity_xref", columns)

#' Read the FDIC-SDI feature panel
#'
#' FDIC-SDI engineered financial ratios plus failure-lead flags, by
#' (rssd_id, year) for 1984-2025 Q4. 413,130 rows. Columns include assets,
#' income_ratio, noncore_proxy, uninsured_ratio, insured_ratio,
#' securities_ratio, equity_ratio, nim, nim_ratio, roa, log_age, and the
#' F1/F3/F5 failure-lead flags.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_fdic_sdi_features <- function(columns = NULL) .read_table("fdic_sdi_features", columns)

#' Read FFIEC-CDR unrealized losses
#'
#' FFIEC Call Report Data fair-value, AOCI, and brokered-deposit measures
#' by (rssd_id, period_end) for 2019-2025. 46,929 rows. Columns include
#' cert, afs_amort_cost, afs_fair_value, htm_amort_cost, htm_fair_value,
#' afs_unrealized_loss, htm_unrealized_loss, total_unrealized_loss, aoci,
#' brokered_deposits, time_dep_100_250k, and time_dep_gt_250k.
#'
#' @inheritParams read_mdrm
#' @return A tibble.
#' @export
read_cdr_unrealized_losses <- function(columns = NULL) .read_table("cdr_unrealized_losses", columns)
