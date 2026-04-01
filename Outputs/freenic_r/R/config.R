# Package environment for state
.fn_env <- new.env(parent = emptyenv())

#' Set the path to freenic Parquet data directory
#'
#' @param path Character path to directory containing .parquet files.
#' @return Invisibly returns the normalized path.
#' @export
#' @examples
#' \dontrun{
#' freenic_set_data_dir("D:/Arcanum/Projects/freenic/Outputs/parquet")
#' }
freenic_set_data_dir <- function(path) {
  path <- normalizePath(path, mustWork = TRUE)
  .fn_env$data_dir <- path
  invisible(path)
}

#' Get the current freenic data directory
#'
#' Returns the configured path to the Parquet data directory. Checks
#' (in order): explicit `freenic_set_data_dir()` value, then the
#' `FREENIC_DATA_DIR` environment variable.
#'
#' @return Character path to the data directory.
#' @export
freenic_data_dir <- function() {
  dir <- .fn_env$data_dir
  if (is.null(dir)) {
    dir <- Sys.getenv("FREENIC_DATA_DIR", unset = NA)
    if (is.na(dir)) {
      abort(c(
        "freenic data directory not set.",
        i = "Call `freenic_set_data_dir('/path/to/parquet')`",
        i = "Or set the FREENIC_DATA_DIR environment variable."
      ))
    }
    .fn_env$data_dir <- dir
  }
  dir
}

#' Check if freenic data is available
#'
#' @return Logical. `TRUE` if the data directory is set and contains
#'   at least the `institutions.parquet` file.
#' @export
freenic_data_available <- function() {
  tryCatch({
    dir <- freenic_data_dir()
    file.exists(file.path(dir, "institutions.parquet"))
  }, error = function(e) FALSE)
}
