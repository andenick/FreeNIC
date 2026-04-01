skip_if_not(freenic_data_available(), "freenic data not available")

test_that("read_institutions returns tibble with expected columns", {
  df <- read_institutions()
  expect_s3_class(df, "tbl_df")
  expect_true("rssd_id" %in% names(df))
  expect_true("name_legal" %in% names(df))
  expect_gt(nrow(df), 200000)
})

test_that("read_institutions with column selection", {
  df <- read_institutions(columns = c("rssd_id", "name_legal"))
  expect_equal(ncol(df), 2)
  expect_true(all(c("rssd_id", "name_legal") %in% names(df)))
})

test_that("read_bank_failures returns data", {
  df <- read_bank_failures()
  expect_s3_class(df, "tbl_df")
  expect_gt(nrow(df), 4000)
})

test_that("read_mdrm returns data", {
  df <- read_mdrm()
  expect_gt(nrow(df), 80000)
})

test_that("read_variable_crosswalk returns data", {
  df <- read_variable_crosswalk()
  expect_gt(nrow(df), 70)
})

test_that("read_catalog_variables returns data", {
  df <- read_catalog_variables()
  expect_gt(nrow(df), 9000)
})

test_that("freenic_query runs SQL", {
  skip_if_not_installed("duckdb")
  skip_if_not_installed("DBI")
  df <- freenic_query("SELECT COUNT(*) AS n FROM institutions")
  expect_gt(df$n, 200000)
})

test_that("freenic_query can join tables", {
  skip_if_not_installed("duckdb")
  skip_if_not_installed("DBI")
  df <- freenic_query("
    SELECT i.name_legal, bf.closing_date
    FROM bank_failures bf
    JOIN institutions i ON bf.cert = i.fdic_cert
    LIMIT 5
  ")
  expect_equal(nrow(df), 5)
  expect_true("name_legal" %in% names(df))
})
