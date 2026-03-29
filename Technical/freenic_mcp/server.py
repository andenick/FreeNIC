"""freenic MCP Server — Query the unified US banking regulatory database.

Exposes 7 tools for Claude to query the 1.5B-row freenic DuckDB database:
  1. query_freenic       — Execute arbitrary read-only SQL
  2. lookup_institution   — Search institutions by name, RSSD, FDIC cert, or state
  3. get_financials       — Get financial time series for an entity
  4. search_variables     — Search the variable catalog
  5. get_hierarchy        — Get corporate parent-child tree
  6. describe_database    — Schema discovery (tables, columns, row counts)
  7. describe_table       — Detailed schema + sample data for a single table

Usage:
  python server.py
  # Or via Claude Code MCP config
"""

import json
import threading
from pathlib import Path

import duckdb
from mcp.server.fastmcp import FastMCP

DB_PATH = Path("D:/Arcanum/Projects/freenic/Outputs/freenic.duckdb")
MAX_ROWS = 1000
QUERY_TIMEOUT_SECONDS = 30

mcp = FastMCP("freenic", dependencies=["duckdb"])

# Persistent read-only connection (B3.1 quick win)
_con = duckdb.connect(str(DB_PATH), read_only=True)


def _get_con():
    return _con


def _rows_to_dicts(result):
    """Convert DuckDB result to list of dicts."""
    if result is None:
        return []
    cols = [d[0] for d in result.description]
    rows = result.fetchmany(MAX_ROWS)
    return [dict(zip(cols, [_serialize(v) for v in row])) for row in rows]


def _execute_with_timeout(con, sql, timeout=QUERY_TIMEOUT_SECONDS):
    """Execute SQL with a timeout. Interrupts query if it exceeds the limit."""
    result = [None]
    error = [None]

    def run():
        try:
            result[0] = con.execute(sql)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=run)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        con.interrupt()
        thread.join(2)
        raise TimeoutError(f"Query exceeded {timeout}s timeout limit. Add LIMIT or more specific filters.")

    if error[0]:
        raise error[0]
    return result[0]


def _serialize(val):
    """Make values JSON-safe."""
    if val is None:
        return None
    if isinstance(val, (int, float, str, bool)):
        return val
    return str(val)


@mcp.tool()
def query_freenic(sql: str) -> str:
    """Execute a read-only SQL query against the freenic banking database.

    The database contains 1.5B rows across 23 tables covering US banking
    regulatory data from 1867-2025. Returns up to 1000 rows as JSON.

    Key tables: bhcf_filings (Y-9C), call_report_filings, luck_call_reports,
    fdic_financials, fdic_sod, dfast_results, pillar3_disclosures, institutions,
    bank_failures, variable_crosswalk.

    Key views: bhcf_enriched, cross_source_financials, entity_summary,
    variable_dictionary, bank_failures_enriched, deposit_market_share,
    stress_test_summary, current_hierarchy.

    Args:
        sql: A read-only SQL query (SELECT only). DuckDB SQL dialect.
    """
    sql_stripped = sql.strip().rstrip(";")
    first_word = sql_stripped.split()[0].upper() if sql_stripped else ""
    if first_word not in ("SELECT", "WITH", "DESCRIBE", "SHOW", "EXPLAIN", "PRAGMA"):
        return json.dumps({"error": "Only read-only queries (SELECT, WITH, DESCRIBE, SHOW) are allowed."})

    con = _get_con()
    try:
        result = _execute_with_timeout(con, sql_stripped)
        rows = _rows_to_dicts(result)
        return json.dumps({"row_count": len(rows), "data": rows}, default=str)
    except TimeoutError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def lookup_institution(
    search: str,
    field: str = "name",
    limit: int = 20,
) -> str:
    """Search for banking institutions in the NIC database.

    Args:
        search: Search term (name, RSSD ID, FDIC cert number, or state code).
        field: Field to search: "name", "rssd_id", "fdic_cert", "state".
        limit: Maximum results to return (default 20).
    """
    con = _get_con()
    try:
        if field == "rssd_id":
            result = con.execute("""
                SELECT rssd_id, name_legal, entity_type, charter_type,
                       state_code, city, is_active, fdic_cert,
                       date_established, date_terminated, primary_fed_reg
                FROM institutions WHERE rssd_id = ?
            """, [int(search)])
        elif field == "fdic_cert":
            result = con.execute("""
                SELECT rssd_id, name_legal, entity_type, charter_type,
                       state_code, city, is_active, fdic_cert,
                       date_established, date_terminated, primary_fed_reg
                FROM institutions WHERE fdic_cert = ?
            """, [int(search)])
        elif field == "state":
            result = con.execute("""
                SELECT rssd_id, name_legal, entity_type, charter_type,
                       state_code, city, is_active, fdic_cert,
                       date_established, date_terminated, primary_fed_reg
                FROM institutions
                WHERE state_code = ? AND is_active = true
                ORDER BY name_legal
                LIMIT ?
            """, [search.upper(), limit])
        else:
            result = con.execute("""
                SELECT rssd_id, name_legal, entity_type, charter_type,
                       state_code, city, is_active, fdic_cert,
                       date_established, date_terminated, primary_fed_reg
                FROM institutions
                WHERE name_legal ILIKE ?
                ORDER BY is_active DESC, name_legal
                LIMIT ?
            """, [f"%{search}%", limit])

        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "institutions": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_financials(
    rssd_id: int,
    variables: str = "BHCK2170",
    start_date: str = "",
    end_date: str = "",
    source: str = "bhcf",
) -> str:
    """Get financial time series for a banking entity.

    Args:
        rssd_id: RSSD ID of the institution.
        variables: Comma-separated variable IDs (e.g., "BHCK2170,BHCK2948")
            or a concept name from the crosswalk (e.g., "total_assets").
        start_date: Optional start date filter (YYYY-MM-DD).
        end_date: Optional end date filter (YYYY-MM-DD).
        source: Data source: "bhcf", "luck", "fdic", "cross" (cross-source via crosswalk).
    """
    con = _get_con()
    try:
        var_list = [v.strip() for v in variables.split(",")]

        if source == "cross":
            where = ["rssd_id = ?"]
            params = [rssd_id]
            where.append(f"concept IN ({','.join(['?'] * len(var_list))})")
            params.extend(var_list)
            if start_date:
                where.append("period_end >= ?")
                params.append(start_date)
            if end_date:
                where.append("period_end <= ?")
                params.append(end_date)
            query = f"""
                SELECT source_table, period_end, concept, source_variable, value
                FROM cross_source_financials
                WHERE {' AND '.join(where)}
                ORDER BY concept, period_end
                LIMIT {MAX_ROWS}
            """
        elif source == "luck":
            where = ["entity_id = ?"]
            params = [rssd_id]
            where.append(f"variable_id IN ({','.join(['?'] * len(var_list))})")
            params.extend(var_list)
            if start_date:
                where.append("period_end >= ?")
                params.append(start_date)
            if end_date:
                where.append("period_end <= ?")
                params.append(end_date)
            query = f"""
                SELECT entity_id AS rssd_id, period_end, variable_id, value
                FROM luck_call_reports
                WHERE {' AND '.join(where)}
                ORDER BY variable_id, period_end
                LIMIT {MAX_ROWS}
            """
        elif source == "fdic":
            where = ["rssd_id = ?"]
            params = [rssd_id]
            where.append(f"variable_id IN ({','.join(['?'] * len(var_list))})")
            params.extend(var_list)
            if start_date:
                where.append("period_end >= ?")
                params.append(start_date)
            if end_date:
                where.append("period_end <= ?")
                params.append(end_date)
            query = f"""
                SELECT rssd_id, period_end, variable_id, value
                FROM fdic_financials
                WHERE {' AND '.join(where)}
                ORDER BY variable_id, period_end
                LIMIT {MAX_ROWS}
            """
        else:
            where = ["rssd_id = ?"]
            params = [rssd_id]
            where.append(f"variable_id IN ({','.join(['?'] * len(var_list))})")
            params.extend(var_list)
            if start_date:
                where.append("period_end >= ?")
                params.append(start_date)
            if end_date:
                where.append("period_end <= ?")
                params.append(end_date)
            query = f"""
                SELECT rssd_id, period_end, variable_id, value
                FROM bhcf_filings
                WHERE {' AND '.join(where)}
                ORDER BY variable_id, period_end
                LIMIT {MAX_ROWS}
            """

        result = con.execute(query, params)
        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "data": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_variables(
    query: str,
    limit: int = 30,
) -> str:
    """Search the variable catalog by name, description, or MDRM code.

    Also searches the crosswalk table for concept-level matches.

    Args:
        query: Search term (e.g., "total assets", "BHCK2170", "deposits").
        limit: Maximum results (default 30).
    """
    con = _get_con()
    try:
        # Search catalog
        catalog_result = con.execute("""
            SELECT variable_id, canonical_name, mnemonic, filing_types,
                   description_short, schedule, quarters_available, entities_reporting
            FROM catalog.variables
            WHERE variable_id ILIKE ?
               OR canonical_name ILIKE ?
               OR description_short ILIKE ?
               OR mnemonic ILIKE ?
            ORDER BY entities_reporting DESC NULLS LAST
            LIMIT ?
        """, [f"%{query}%"] * 4 + [limit])
        catalog_rows = _rows_to_dicts(catalog_result)

        # Search crosswalk
        xw_result = con.execute("""
            SELECT concept, source_variable, source_table, mdrm_variable,
                   match_confidence, notes
            FROM variable_crosswalk
            WHERE concept ILIKE ?
               OR source_variable ILIKE ?
               OR mdrm_variable ILIKE ?
               OR notes ILIKE ?
            ORDER BY concept, source_table
            LIMIT ?
        """, [f"%{query}%"] * 4 + [limit])
        xw_rows = _rows_to_dicts(xw_result)

        return json.dumps({
            "catalog_matches": len(catalog_rows),
            "crosswalk_matches": len(xw_rows),
            "catalog": catalog_rows,
            "crosswalk": xw_rows,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_hierarchy(
    rssd_id: int,
    direction: str = "down",
    active_only: bool = True,
) -> str:
    """Get corporate hierarchy for a banking entity.

    Args:
        rssd_id: RSSD ID of the entity.
        direction: "down" for subsidiaries, "up" for parent chain.
        active_only: If true, only show active (non-terminated) relationships.
    """
    con = _get_con()
    try:
        if direction == "up":
            where_clause = "r.rssd_offspring = ?"
            if active_only:
                where_clause += " AND (r.dt_end IS NULL OR r.dt_end > CURRENT_DATE)"
            result = con.execute(f"""
                SELECT r.rssd_parent, p.name_legal AS parent_name, p.entity_type AS parent_type,
                       r.rssd_offspring, c.name_legal AS offspring_name,
                       r.pct_equity, r.relationship_level,
                       r.dt_start, r.dt_end
                FROM relationships r
                LEFT JOIN institutions p ON r.rssd_parent = p.rssd_id
                LEFT JOIN institutions c ON r.rssd_offspring = c.rssd_id
                WHERE {where_clause}
                ORDER BY r.pct_equity DESC NULLS LAST
            """, [rssd_id])
        else:
            where_clause = "r.rssd_parent = ?"
            if active_only:
                where_clause += " AND (r.dt_end IS NULL OR r.dt_end > CURRENT_DATE)"
            result = con.execute(f"""
                SELECT r.rssd_parent, r.rssd_offspring,
                       c.name_legal AS subsidiary_name, c.entity_type AS subsidiary_type,
                       c.state_code, c.is_active,
                       r.pct_equity, r.relationship_level,
                       r.dt_start, r.dt_end
                FROM relationships r
                LEFT JOIN institutions c ON r.rssd_offspring = c.rssd_id
                WHERE {where_clause}
                ORDER BY r.pct_equity DESC NULLS LAST, c.name_legal
                LIMIT {MAX_ROWS}
            """, [rssd_id])

        rows = _rows_to_dicts(result)

        # Also get the entity itself
        entity = con.execute("""
            SELECT rssd_id, name_legal, entity_type, state_code, is_active, fdic_cert
            FROM institutions WHERE rssd_id = ?
        """, [rssd_id]).fetchone()
        entity_info = None
        if entity:
            entity_info = {
                "rssd_id": entity[0], "name": entity[1], "type": entity[2],
                "state": entity[3], "active": entity[4], "fdic_cert": entity[5],
            }

        return json.dumps({
            "entity": entity_info,
            "direction": direction,
            "relationship_count": len(rows),
            "relationships": rows,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def describe_database() -> str:
    """Get an overview of all tables and views in the freenic database.

    Returns table names, row counts, and column counts for schema discovery.
    Use this before writing queries to understand the available data.
    """
    con = _get_con()
    try:
        tables = con.execute("""
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema IN ('main', 'catalog')
            ORDER BY table_schema, table_type, table_name
        """).fetchall()

        result = []
        for schema, name, ttype in tables:
            qualified = f"{schema}.{name}" if schema != 'main' else name
            try:
                count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
            except Exception:
                count = None
            cols = con.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = ? AND table_name = ?
                ORDER BY ordinal_position
            """, [schema, name]).fetchall()
            result.append({
                "schema": schema,
                "table": name,
                "type": ttype,
                "rows": count,
                "columns": [{"name": c[0], "type": c[1]} for c in cols],
            })

        return json.dumps({"table_count": len(result), "tables": result}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get detailed schema and sample data for a specific table or view.

    Args:
        table_name: Table name (e.g., "bhcf_filings", "catalog.variables").
    """
    con = _get_con()
    try:
        # Get column info
        if '.' in table_name:
            schema, tbl = table_name.split('.', 1)
        else:
            schema, tbl = 'main', table_name

        cols = con.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
        """, [schema, tbl]).fetchall()

        if not cols:
            return json.dumps({"error": f"Table '{table_name}' not found"})

        qualified = f"{schema}.{tbl}" if schema != 'main' else tbl
        count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
        sample = _rows_to_dicts(con.execute(f"SELECT * FROM {qualified} LIMIT 5"))

        return json.dumps({
            "table": table_name,
            "row_count": count,
            "columns": [{"name": c[0], "type": c[1], "nullable": c[2]} for c in cols],
            "sample_rows": sample,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
