test_that("freenic_set_data_dir validates path", {
  expect_error(
    freenic_set_data_dir("/nonexistent/path"),
    "cannot be normalized"
  )
})

test_that("freenic_data_dir errors when not set", {
  .fn_env <- freenic:::.fn_env
  old <- .fn_env$data_dir
  .fn_env$data_dir <- NULL
  withr::local_envvar(FREENIC_DATA_DIR = NA)
  expect_error(freenic_data_dir(), "not set")
  .fn_env$data_dir <- old
})
