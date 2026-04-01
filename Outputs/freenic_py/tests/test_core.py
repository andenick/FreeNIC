"""Tests for freenic core functionality."""

import os
import pytest
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


def test_set_data_dir_invalid():
    with pytest.raises(FileNotFoundError):
        freenic.set_data_dir("/nonexistent/path")


def test_list_tables():
    df = freenic.list_tables()
    assert len(df) == 34
    assert "institutions" in df["table"].values
    assert "bhcf_filings" in df["table"].values
    assert df["available"].all()


def test_describe():
    df = freenic.describe("institutions")
    col_names = df["column_name"].tolist()
    assert "rssd_id" in col_names
    assert "name_legal" in col_names


def test_query_simple():
    df = freenic.query("SELECT COUNT(*) AS n FROM institutions")
    assert df["n"].iloc[0] > 200_000


def test_query_with_params():
    df = freenic.query(
        "SELECT rssd_id, name_legal FROM institutions WHERE rssd_id = ?",
        [1039502],
    )
    assert len(df) == 1
    assert "JPMORGAN" in df["name_legal"].iloc[0].upper()


def test_query_bank_failures():
    df = freenic.query("SELECT COUNT(*) AS n FROM bank_failures")
    assert df["n"].iloc[0] >= 4_000


def test_query_catalog():
    df = freenic.query("SELECT COUNT(*) AS n FROM catalog_variables")
    assert df["n"].iloc[0] >= 9_000


def test_query_join():
    df = freenic.query("""
        SELECT i.name_legal, bf.closing_date, bf.total_assets
        FROM bank_failures bf
        JOIN institutions i ON bf.cert = i.fdic_cert
        WHERE bf.failure_year = 2008
        ORDER BY bf.total_assets DESC NULLS LAST
        LIMIT 5
    """)
    assert len(df) > 0
    assert "name_legal" in df.columns
