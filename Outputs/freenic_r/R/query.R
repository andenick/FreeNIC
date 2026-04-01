#' Execute SQL against freenic Parquet files via DuckDB
#'
#' Creates a temporary in-memory DuckDB connection and registers all
#' Parquet files as views. Useful for joins and complex queries that
#' span multiple tables.
#'
#' @param sql Character SQL query.
#' @return A tibble with query results.
#' @export
#' @examplesIf freenic_data_available()
#' freenic_query("SELECT COUNT(*) AS n FROM institutions")
freenic_query <- function(sql) {
  check_installed("duckdb", reason = "to run SQL queries")
  check_installed("DBI", reason = "to run SQL queries")

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = ":memory:")
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  dir <- freenic_data_dir()
  pq_files <- list.files(dir, pattern = "\\.parquet$", full.names = TRUE)
  for (f in pq_files) {
    tbl_name <- tools::file_path_sans_ext(basename(f))
    DBI::dbExecute(con, sprintf(
      "CREATE VIEW \"%s\" AS SELECT * FROM read_parquet('%s')",
      tbl_name, gsub("\\\\", "/", f)
    ))
  }

  DBI::dbGetQuery(con, sql)
}
