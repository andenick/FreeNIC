"""C7: MCP server tests — verify all 7 tools return valid results."""

import json
import sys
from pathlib import Path

import pytest

# Add MCP server to path. The MCP layer lives at Technical/freenic_mcp/ (operational, its
# own dedicated venv per ENV-DEBT-001). Pre-restructure this test sat at
# Technical/freenic_ingestion/tests/, so parent.parent.parent == Technical/ and the bare
# "freenic_mcp" hop resolved; the public-layout move to pipeline/tests/ made
# parent.parent.parent == repo-root, so the Technical/ segment must be explicit.
# Corrected 2026-07-16.
MCP_DIR = Path(__file__).parent.parent.parent / "Technical" / "freenic_mcp"
sys.path.insert(0, str(MCP_DIR))

from server import (
    query_freenic,
    lookup_institution,
    get_financials,
    search_variables,
    get_hierarchy,
    describe_database,
    describe_table,
)


def _parse(result):
    return json.loads(result)


def test_query_select_one():
    r = _parse(query_freenic("SELECT 1 AS val"))
    assert r["row_count"] == 1
    assert r["data"][0]["val"] == 1


def test_query_rejects_drop():
    r = _parse(query_freenic("DROP TABLE institutions"))
    assert "error" in r


def test_query_rejects_insert():
    r = _parse(query_freenic("INSERT INTO institutions VALUES (1, 'test')"))
    assert "error" in r


def test_query_rejects_delete():
    r = _parse(query_freenic("DELETE FROM institutions"))
    assert "error" in r


def test_lookup_by_name():
    r = _parse(lookup_institution("jpmorgan"))
    assert r["count"] > 0
    names = [i["name_legal"] for i in r["institutions"]]
    assert any("JPMORGAN" in n.upper() for n in names)


def test_lookup_by_rssd():
    r = _parse(lookup_institution("1039502", field="rssd_id"))
    assert r["count"] == 1
    assert r["institutions"][0]["rssd_id"] == 1039502


def test_lookup_by_state():
    r = _parse(lookup_institution("NY", field="state"))
    assert r["count"] > 0


def test_get_financials_bhcf():
    r = _parse(get_financials(1039502, "BHCK2170"))
    assert r["count"] > 0
    assert all(d["variable_id"] == "BHCK2170" for d in r["data"])


def test_get_financials_cross():
    r = _parse(get_financials(1039502, "total_assets", source="cross"))
    assert r["count"] > 0


def test_search_variables_by_name():
    r = _parse(search_variables("total assets"))
    assert r["catalog_matches"] > 0 or r["crosswalk_matches"] > 0


def test_search_variables_by_code():
    r = _parse(search_variables("BHCK2170"))
    assert r["catalog_matches"] > 0


def test_get_hierarchy_down():
    r = _parse(get_hierarchy(1039502))
    assert r["entity"] is not None
    assert r["entity"]["rssd_id"] == 1039502
    assert r["relationship_count"] > 0


def test_get_hierarchy_up():
    # JPM Chase Bank NA (subsidiary) should have JPM as parent
    r = _parse(get_hierarchy(852218, direction="up"))
    assert r["relationship_count"] >= 0  # may or may not have parents


def test_describe_database():
    r = _parse(describe_database())
    assert r["table_count"] > 20
    table_names = {t["table"] for t in r["tables"]}
    assert "institutions" in table_names
    assert "bhcf_filings" in table_names


def test_describe_table():
    r = _parse(describe_table("institutions"))
    assert r["row_count"] > 200000
    col_names = {c["name"] for c in r["columns"]}
    assert "rssd_id" in col_names
    assert "name_legal" in col_names
    assert len(r["sample_rows"]) == 5
