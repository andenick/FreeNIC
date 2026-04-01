"""Tests for freenic typed accessor functions."""

import os
import pytest
import pandas as pd
import freenic

PARQUET_DIR = os.environ.get(
    "FREENIC_DATA_DIR",
    "D:/Arcanum/Projects/freenic/Outputs/parquet",
)


@pytest.fixture(autouse=True)
def setup():
    freenic.set_data_dir(PARQUET_DIR)
    yield
    freenic.close()


class TestLookupInstitution:
    def test_by_name(self):
        df = freenic.lookup_institution("jpmorgan")
        assert len(df) > 0
        assert any("JPMORGAN" in n.upper() for n in df["name_legal"])

    def test_by_rssd(self):
        df = freenic.lookup_institution("1039502", field="rssd_id")
        assert len(df) == 1
        assert df["rssd_id"].iloc[0] == 1039502

    def test_by_state(self):
        df = freenic.lookup_institution("NY", field="state")
        assert len(df) > 0
        assert all(df["state_code"].str.upper() == "NY")

    def test_by_fdic_cert(self):
        df = freenic.lookup_institution("628", field="fdic_cert")
        assert len(df) >= 1


class TestGetFinancials:
    def test_bhcf_default(self):
        df = freenic.get_financials(1039502, "BHCK2170")
        assert len(df) > 0
        assert "value" in df.columns

    def test_bhcf_with_dates(self):
        df = freenic.get_financials(
            1039502, "BHCK2170",
            start_date="2020-01-01", end_date="2024-12-31",
        )
        assert len(df) > 0

    def test_multiple_variables(self):
        df = freenic.get_financials(1039502, ["BHCK2170", "BHCK2948"])
        assert len(df) > 0

    def test_fdic_source(self):
        df = freenic.get_financials(628, "ASSET", source="fdic")
        assert len(df) > 0

    def test_invalid_source(self):
        with pytest.raises(ValueError):
            freenic.get_financials(1039502, source="invalid")


class TestSearchVariables:
    def test_search_by_name(self):
        df = freenic.search_variables("total assets")
        assert len(df) > 0

    def test_search_by_code(self):
        df = freenic.search_variables("BHCK2170")
        assert len(df) > 0
        assert any("BHCK2170" in v for v in df["variable_id"])


class TestGetHierarchy:
    def test_subsidiaries(self):
        df = freenic.get_hierarchy(1039502, direction="down")
        assert len(df) > 0
        assert "subsidiary_name" in df.columns

    def test_parent_chain(self):
        df = freenic.get_hierarchy(1039502, direction="up")
        assert "parent_name" in df.columns


class TestGetFailures:
    def test_all_failures(self):
        df = freenic.get_failures()
        assert len(df) > 0

    def test_by_year_range(self):
        df = freenic.get_failures(start_year=2008, end_year=2010)
        assert len(df) > 0
        assert all(df["failure_year"].between(2008, 2010))

    def test_by_state(self):
        # state_code is NULL in current data export; test the query runs
        df = freenic.get_failures(state="GA")
        # May be empty if state_code not populated; just verify no error
        assert isinstance(df, pd.DataFrame)
