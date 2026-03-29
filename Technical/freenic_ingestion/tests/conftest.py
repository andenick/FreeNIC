"""Shared fixtures for freenic test suite."""

import sys
from pathlib import Path

import duckdb
import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from utils import DB_PATH, OUTPUTS_DIR, INPUT_PATHS

PARQUET_DIR = OUTPUTS_DIR / "parquet"


@pytest.fixture(scope="session")
def db():
    """Session-scoped read-only DuckDB connection."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    yield con
    con.close()


@pytest.fixture(scope="session")
def parquet_dir():
    return PARQUET_DIR


@pytest.fixture(scope="session")
def input_paths():
    return INPUT_PATHS
