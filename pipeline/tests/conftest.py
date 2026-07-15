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


# --- MCP env-debt guard ---------------------------------------------------------------
# test_mcp.py imports the freenic_mcp server module, which needs mcp>=1.0 (pydantic v2 —
# it imports pydantic.TypeAdapter). If the active interpreter pins pydantic 1.x for other
# tools, upgrading it in place has cross-project blast radius and is NOT a safe fix. The
# MCP layer carries its own env pin
# (Technical/freenic_mcp/requirements.txt: mcp>=1.0.0, duckdb>=1.1.0). Until a dedicated MCP
# venv is wired, collect test_mcp.py ONLY when the MCP stack actually imports in the ACTIVE
# interpreter; otherwise skip it. This excludes an ENVIRONMENT test (the MCP layer, not
# warehouse data) from the data gate without silencing it where the right env is present.
# Env-debt tracked in Technical/KNOWN_ISSUES.md.
collect_ignore = []
try:
    from pydantic import TypeAdapter  # noqa: F401  (present only on pydantic v2 / mcp env)
except Exception:
    collect_ignore.append("test_mcp.py")


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
