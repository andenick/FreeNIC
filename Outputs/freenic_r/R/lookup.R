#' Look up RSSD ID by name, FDIC cert, PERMCO, or RSSD
#'
#' Resolves an identifier to RSSD ID(s) with institution details.
#' Provide exactly one of the arguments.
#'
#' @param name Institution name (fuzzy match).
#' @param fdic_cert FDIC certificate number.
#' @param permco CRSP PERMCO identifier.
#' @param rssd_id RSSD ID (returns full details).
#' @param limit Maximum results for name searches.
#' @return A tibble with institution details.
#' @export
#' @examplesIf freenic_data_available()
#' lookup_rssd(name = "jpmorgan chase")
#' lookup_rssd(fdic_cert = 628)
lookup_rssd <- function(name = NULL, fdic_cert = NULL, permco = NULL,
                        rssd_id = NULL, limit = 20L) {
  check_installed("duckdb", reason = "for lookup queries")
  check_installed("DBI", reason = "for lookup queries")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  cols <- paste("rssd_id, name_legal, entity_type, state_code, city,",
                "is_active, fdic_cert, primary_fed_reg, date_established")

  if (!is.null(rssd_id)) {
    DBI::dbGetQuery(con, sprintf("SELECT %s FROM institutions WHERE rssd_id = %d", cols, as.integer(rssd_id)))
  } else if (!is.null(fdic_cert)) {
    DBI::dbGetQuery(con, sprintf("SELECT %s FROM institutions WHERE fdic_cert = %d", cols, as.integer(fdic_cert)))
  } else if (!is.null(permco)) {
    DBI::dbGetQuery(con, sprintf(
      "SELECT i.rssd_id, i.name_legal, i.entity_type, i.state_code, i.city,
              i.is_active, i.fdic_cert, i.primary_fed_reg, i.date_established,
              c.permco, c.dt_start, c.dt_end
       FROM crsp_mapping c
       JOIN institutions i ON c.rssd_id = i.rssd_id
       WHERE c.permco = %d ORDER BY c.dt_start DESC", as.integer(permco)))
  } else if (!is.null(name)) {
    DBI::dbGetQuery(con, sprintf(
      "SELECT %s FROM institutions WHERE name_legal ILIKE '%%%s%%'
       ORDER BY is_active DESC, name_legal LIMIT %d",
      cols, gsub("'", "''", name), as.integer(limit)))
  } else {
    abort("Provide at least one of: name, fdic_cert, permco, rssd_id")
  }
}

#' Search for variable/column IDs across MDRM and crosswalk
#'
#' @param search Keyword to search (matches variable_id, name, description).
#' @param source Optional filter by source table name.
#' @param limit Maximum results.
#' @return A list with two tibbles: `$catalog` (MDRM matches) and
#'   `$crosswalk` (concept-level matches).
#' @export
#' @examplesIf freenic_data_available()
#' lookup_column_id("total assets")
lookup_column_id <- function(search, source = NULL, limit = 30L) {
  check_installed("duckdb", reason = "for lookup queries")
  check_installed("DBI", reason = "for lookup queries")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  pattern <- paste0("%", gsub("'", "''", search), "%")

  catalog <- DBI::dbGetQuery(con, sprintf(
    "SELECT 'mdrm_catalog' AS match_source, variable_id, canonical_name,
            description_short, schedule, first_observed, last_observed,
            entities_reporting
     FROM catalog_variables
     WHERE variable_id ILIKE '%s' OR canonical_name ILIKE '%s'
        OR description_short ILIKE '%s'
     ORDER BY entities_reporting DESC NULLS LAST LIMIT %d",
    pattern, pattern, pattern, as.integer(limit)))

  src_filter <- if (!is.null(source)) {
    sprintf(" AND source_table = '%s'", gsub("'", "''", source))
  } else ""

  xwalk <- DBI::dbGetQuery(con, sprintf(
    "SELECT 'crosswalk' AS match_source, concept, source_variable,
            source_table, mdrm_variable, match_confidence, notes
     FROM variable_crosswalk
     WHERE (concept ILIKE '%s' OR source_variable ILIKE '%s'
        OR mdrm_variable ILIKE '%s' OR notes ILIKE '%s')%s
     ORDER BY concept LIMIT %d",
    pattern, pattern, pattern, pattern, src_filter, as.integer(limit)))

  list(catalog = catalog, crosswalk = xwalk)
}

#' Show all freenic data sources with descriptions
#'
#' @return A tibble with file_type, description, ingestion_script, file_count.
#' @export
#' @examplesIf freenic_data_available()
#' show_source_descriptions()
show_source_descriptions <- function() {
  check_installed("duckdb", reason = "for source queries")
  check_installed("DBI", reason = "for source queries")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  DBI::dbGetQuery(con,
    "SELECT file_type, description, ingestion_script, COUNT(*) AS file_count
     FROM catalog_data_sources
     GROUP BY file_type, description, ingestion_script
     ORDER BY file_type, ingestion_script")
}

#' Show full regulatory taxonomy
#'
#' Entity types, primary regulators, and BHC/FHC/SLHC indicator counts.
#'
#' @return A tibble with entity_type, primary_fed_reg, and counts.
#' @export
#' @examplesIf freenic_data_available()
#' show_regulatory_groups()
show_regulatory_groups <- function() {
  check_installed("duckdb", reason = "for regulatory queries")
  check_installed("DBI", reason = "for regulatory queries")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  DBI::dbGetQuery(con,
    "SELECT i.entity_type, i.primary_fed_reg,
            COUNT(*) AS entity_count,
            SUM(CASE WHEN i.is_active THEN 1 ELSE 0 END) AS active_count,
            SUM(CASE WHEN a.bhc_ind = 1 THEN 1 ELSE 0 END) AS bhc_count,
            SUM(CASE WHEN a.fhc_ind = 1 THEN 1 ELSE 0 END) AS fhc_count,
            SUM(CASE WHEN a.slhc_ind = 1 THEN 1 ELSE 0 END) AS slhc_count
     FROM institutions i
     LEFT JOIN institution_attributes a ON i.rssd_id = a.rssd_id
     GROUP BY i.entity_type, i.primary_fed_reg
     ORDER BY entity_count DESC")
}

#' Verify MDRM variable codes exist
#'
#' @param ... One or more MDRM variable IDs as strings.
#' @return A tibble with variable details and a `found` column.
#' @export
#' @examplesIf freenic_data_available()
#' verify_mdrm_codes("BHCK2170", "FAKE9999")
verify_mdrm_codes <- function(...) {
  codes <- c(...)
  if (length(codes) == 0) abort("Provide at least one MDRM code")

  check_installed("duckdb", reason = "for MDRM verification")
  check_installed("DBI", reason = "for MDRM verification")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  quoted <- paste(sprintf("'%s'", gsub("'", "''", codes)), collapse = ", ")
  found <- DBI::dbGetQuery(con, sprintf(
    "SELECT DISTINCT variable_id, item_name, reporting_form, start_date, end_date
     FROM mdrm WHERE variable_id IN (%s) ORDER BY variable_id", quoted))
  found$found <- TRUE

  missing_ids <- setdiff(codes, found$variable_id)
  if (length(missing_ids) > 0) {
    missing_df <- data.frame(
      variable_id = missing_ids,
      item_name = NA_character_,
      reporting_form = NA_character_,
      start_date = as.Date(NA),
      end_date = as.Date(NA),
      found = FALSE,
      stringsAsFactors = FALSE
    )
    rbind(found, missing_df)
  } else {
    found
  }
}

#' Verify RSSD IDs exist
#'
#' @param ... One or more RSSD IDs as integers.
#' @return A tibble with institution details and a `found` column.
#' @export
#' @examplesIf freenic_data_available()
#' verify_rssds(1039502, 9999999)
verify_rssds <- function(...) {
  ids <- as.integer(c(...))
  if (length(ids) == 0) abort("Provide at least one RSSD ID")

  check_installed("duckdb", reason = "for RSSD verification")
  check_installed("DBI", reason = "for RSSD verification")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  .register_parquet(con)

  id_str <- paste(ids, collapse = ", ")
  found <- DBI::dbGetQuery(con, sprintf(
    "SELECT rssd_id, name_legal, entity_type, state_code, is_active,
            fdic_cert, primary_fed_reg, date_established
     FROM institutions WHERE rssd_id IN (%s) ORDER BY rssd_id", id_str))
  found$found <- TRUE

  missing_ids <- setdiff(ids, found$rssd_id)
  if (length(missing_ids) > 0) {
    missing_df <- data.frame(
      rssd_id = missing_ids,
      name_legal = NA_character_,
      entity_type = NA_character_,
      state_code = NA_character_,
      is_active = NA,
      fdic_cert = NA_integer_,
      primary_fed_reg = NA_character_,
      date_established = as.Date(NA),
      found = FALSE,
      stringsAsFactors = FALSE
    )
    rbind(found, missing_df)
  } else {
    found
  }
}

# Internal helper to register all Parquet files as DuckDB views
.register_parquet <- function(con) {
  dir <- freenic_data_dir()
  pq_files <- list.files(dir, pattern = "\\.parquet$", full.names = TRUE)
  for (f in pq_files) {
    tbl_name <- tools::file_path_sans_ext(basename(f))
    DBI::dbExecute(con, sprintf(
      "CREATE VIEW \"%s\" AS SELECT * FROM read_parquet('%s')",
      tbl_name, gsub("\\\\", "/", f)
    ))
  }
}
