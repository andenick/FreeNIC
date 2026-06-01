"""freenic MCP Server — Query the unified US banking regulatory database.

Exposes 15 tools for Claude to query the 1.5B-row freenic DuckDB database:
  1. query_freenic           — Execute arbitrary read-only SQL
  2. lookup_institution      — Search institutions by name, RSSD, FDIC cert, or state
  3. get_financials          — Get financial time series (bhcf, luck, fdic, robin, cross)
  4. search_variables        — Search the variable catalog
  5. get_hierarchy           — Get corporate parent-child tree
  6. describe_database       — Schema discovery (tables, columns, row counts)
  7. describe_table          — Detailed schema + sample data for a single table
  8. get_failures            — Bank failure records with filtering
  9. get_fred_series         — FRED macro/banking time series
 10. lookup_rssd             — Resolve name/FDIC cert/PERMCO to RSSD ID
 11. lookup_column_id        — Search variable IDs across MDRM + crosswalk
 12. show_source_descriptions — List all data sources with metadata
 13. show_regulatory_groups  — Full regulatory taxonomy (entity types, regulators, BHC/FHC/SLHC)
 14. verify_mdrm_codes       — Check if MDRM codes exist, return metadata
 15. verify_rssds            — Check if RSSD IDs exist, return institution details

Usage:
  # Set data location via environment variable:
  export FREENIC_DATA_DIR="/path/to/parquet"   # Parquet directory (preferred)
  export FREENIC_DB_PATH="/path/to/freenic.duckdb"  # Or DuckDB file directly

  python server.py
  # Or via Claude Code MCP config:
  # claude mcp add freenic -- python server.py
"""

import json
import os
import threading
from pathlib import Path

import duckdb
from mcp.server.fastmcp import FastMCP

_PARQUET_TABLES = [
    "mdrm", "reporting_forms", "institutions", "institution_attributes",
    "branches", "relationships", "transformations", "crsp_mapping",
    "bhcf_filings", "call_report_filings", "luck_call_reports",
    "occ_historical", "filing_metadata", "bank_failures", "fdic_financials",
    "fdic_sod", "dfast_results", "pillar3_disclosures", "variable_crosswalk",
    "fdic_history", "fred_series", "robin_panel", "robin_deposits_historical",
    "robin_deposits_modern", "robin_crosswalk", "bhc_ownership",
    "sector_groupings", "stress_scenarios_domestic",
    "stress_scenarios_international", "catalog_variables",
    "catalog_filing_coverage", "catalog_entity_coverage",
    "catalog_schema_evolution", "catalog_data_sources",
    "entity_xref", "fdic_sdi_features", "cdr_unrealized_losses",
]

MAX_ROWS = 1000
QUERY_TIMEOUT_SECONDS = 30

mcp = FastMCP("freenic", dependencies=["duckdb"])


def _resolve_connection() -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection from env vars or defaults.

    Resolution order:
      1. FREENIC_DATA_DIR — directory of .parquet files (creates in-memory DB with views)
      2. FREENIC_DB_PATH  — path to a .duckdb file (opens read-only)
      3. Default fallback to ./Outputs/freenic.duckdb (relative to repo root)
    """
    data_dir = os.environ.get("FREENIC_DATA_DIR")
    if data_dir:
        p = Path(data_dir)
        if not p.is_dir():
            raise FileNotFoundError(f"FREENIC_DATA_DIR not found: {data_dir}")
        con = duckdb.connect(":memory:")
        for table in _PARQUET_TABLES:
            pq = p / f"{table}.parquet"
            if pq.exists():
                con.execute(
                    f'CREATE VIEW "{table}" AS '
                    f"SELECT * FROM read_parquet('{pq.as_posix()}')"
                )
        return con

    db_path = os.environ.get("FREENIC_DB_PATH")
    if not db_path:
        db_path = str(Path(__file__).resolve().parent.parent.parent / "Outputs" / "freenic.duckdb")
    p = Path(db_path)
    if not p.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}. "
            "Set FREENIC_DATA_DIR to a parquet directory or "
            "FREENIC_DB_PATH to a .duckdb file."
        )
    return duckdb.connect(str(p), read_only=True)


_con = _resolve_connection()


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

    The database contains 1.5B rows across 37 tables covering US banking
    regulatory data from 1863-2026. Returns up to 1000 rows as JSON.

    Key tables: bhcf_filings (Y-9C), call_report_filings, luck_call_reports,
    fdic_financials, fdic_sod, dfast_results, pillar3_disclosures, institutions,
    bank_failures, variable_crosswalk, robin_panel, fred_series, fdic_history,
    bhc_ownership, stress_scenarios_domestic, stress_scenarios_international.

    Engineered/cross-reference tables: entity_xref (canonical RSSD identity
    union across all sources, 234K rows), fdic_sdi_features (FDIC-SDI engineered
    ratios + F1/F3/F5 failure-lead flags by (rssd_id, year), 1984-2025, 413K
    rows), cdr_unrealized_losses (FFIEC-CDR AFS/HTM fair-value, AOCI & brokered
    deposits by (rssd_id, period_end), 2019-2025, 47K rows).

    Key views: bhcf_enriched, cross_source_financials, entity_summary,
    variable_dictionary, bank_failures_enriched, deposit_market_share,
    stress_test_summary, current_hierarchy, robin_panel_enriched, failure_timeline.

    Args:
        sql: A read-only SQL query (SELECT only). DuckDB SQL dialect.
    """
    sql_stripped = sql.strip().rstrip(";")
    first_word = sql_stripped.split()[0].upper() if sql_stripped else ""
    if first_word not in ("SELECT", "WITH", "DESCRIBE", "SHOW", "EXPLAIN", "PRAGMA", "SUMMARIZE"):
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
        source: Data source: "bhcf", "luck", "fdic", "robin", "cross" (cross-source via crosswalk).
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
        elif source == "robin":
            # Robin panel is wide-format; select requested columns directly
            where = []
            params = []
            # Try to match via crosswalk first
            where.append("rc.rssd_id = ?")
            params.append(rssd_id)
            if start_date:
                where.append("rp.year >= ?")
                params.append(int(start_date[:4]))
            if end_date:
                where.append("rp.year <= ?")
                params.append(int(end_date[:4]))
            # Select common Robin columns
            query = f"""
                SELECT rp.year, rp.canonical_bank_name, rp.assets, rp.deposits,
                       rp.loans, rp.equity, rp.failed_bank, rp.time_to_fail,
                       rc.rssd_id, rc.fdic_cert
                FROM robin_panel rp
                JOIN robin_crosswalk rc ON CAST(rp.bank_id AS BIGINT) = CAST(rc.bank_id_robin AS BIGINT)
                WHERE {' AND '.join(where)}
                ORDER BY rp.year DESC
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


@mcp.tool()
def get_failures(
    start_year: int = 0,
    end_year: int = 9999,
    state: str = "",
    limit: int = 100,
) -> str:
    """Get bank failure records from the FDIC failed banks list (1934-2026).

    Args:
        start_year: Filter failures from this year (default: no filter).
        end_year: Filter failures through this year (default: no filter).
        state: Filter by state abbreviation (e.g., "GA"). Empty = all states.
        limit: Maximum results (default 100).
    """
    con = _get_con()
    try:
        conditions = []
        params = []

        if start_year > 0:
            conditions.append("failure_year >= ?")
            params.append(start_year)
        if end_year < 9999:
            conditions.append("failure_year <= ?")
            params.append(end_year)
        if state:
            conditions.append("UPPER(state_code) = UPPER(?)")
            params.append(state)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        result = con.execute(f"""
            SELECT cert, bank_name, city, state_code, closing_date,
                   failure_year, total_assets, total_deposits, estimated_loss,
                   acquiring_institution, resolution_type
            FROM bank_failures {where}
            ORDER BY closing_date DESC
            LIMIT ?
        """, params)
        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "data": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_fred_series(
    series_id: str = "",
    start_date: str = "",
    end_date: str = "",
    limit: int = 500,
) -> str:
    """Get FRED banking and macroeconomic time series data.

    Available series: FEDFUNDS, TOTBKCR, DPCREDIT, GDP, UNRATE, CPIAUCSL,
    GS10, GS2, TB3MS, BOGZ1FL073164003Q, USREC, DPRIME, MORTGAGE30US,
    BOGZ1FL153064005Q, INDPRO.

    Args:
        series_id: FRED series ID (e.g., "FEDFUNDS"). Empty = list all series.
        start_date: Optional start date (YYYY-MM-DD).
        end_date: Optional end date (YYYY-MM-DD).
        limit: Maximum results (default 500).
    """
    con = _get_con()
    try:
        if not series_id:
            result = con.execute("""
                SELECT series_id, series_name,
                       MIN(observation_date) AS first_date,
                       MAX(observation_date) AS last_date,
                       COUNT(*) AS observations
                FROM fred_series
                GROUP BY series_id, series_name
                ORDER BY series_id
            """)
            rows = _rows_to_dicts(result)
            return json.dumps({"count": len(rows), "series": rows}, default=str)

        conditions = ["series_id = ?"]
        params = [series_id.upper()]
        if start_date:
            conditions.append("observation_date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("observation_date <= ?")
            params.append(end_date)
        params.append(limit)

        result = con.execute(f"""
            SELECT series_id, series_name, observation_date, value
            FROM fred_series
            WHERE {' AND '.join(conditions)}
            ORDER BY observation_date DESC
            LIMIT ?
        """, params)
        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "data": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def lookup_rssd(
    name: str = "",
    fdic_cert: int = 0,
    permco: int = 0,
    rssd_id: int = 0,
    limit: int = 20,
) -> str:
    """Resolve an identifier to RSSD ID(s) with institution details.

    Provide exactly one non-zero argument.

    Args:
        name: Institution name (fuzzy ILIKE match).
        fdic_cert: FDIC certificate number.
        permco: CRSP PERMCO identifier.
        rssd_id: RSSD ID (returns full details).
        limit: Maximum results for name searches.
    """
    con = _get_con()
    cols = ("rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, primary_fed_reg, date_established")
    try:
        if rssd_id:
            result = con.execute(f"SELECT {cols} FROM institutions WHERE rssd_id = ?", [rssd_id])
        elif fdic_cert:
            result = con.execute(f"SELECT {cols} FROM institutions WHERE fdic_cert = ?", [fdic_cert])
        elif permco:
            result = con.execute(
                f"SELECT i.rssd_id, i.name_legal, i.entity_type, i.state_code, "
                f"i.city, i.is_active, i.fdic_cert, i.primary_fed_reg, "
                f"i.date_established, c.permco, c.dt_start, c.dt_end "
                f"FROM crsp_mapping c "
                f"JOIN institutions i ON c.rssd_id = i.rssd_id "
                f"WHERE c.permco = ? ORDER BY c.dt_start DESC", [permco])
        elif name:
            result = con.execute(
                f"SELECT {cols} FROM institutions "
                f"WHERE name_legal ILIKE ? "
                f"ORDER BY is_active DESC, name_legal LIMIT ?",
                [f"%{name}%", limit])
        else:
            return json.dumps({"error": "Provide at least one of: name, fdic_cert, permco, rssd_id"})

        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "data": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def lookup_column_id(
    search: str,
    source: str = "",
    limit: int = 30,
) -> str:
    """Search for variable/column IDs across MDRM catalog and crosswalk.

    Args:
        search: Keyword to search (matches variable_id, name, description, concept).
        source: Optional filter by source table (e.g., "luck_call_reports").
        limit: Maximum results per section.
    """
    con = _get_con()
    try:
        pattern = f"%{search}%"

        # Catalog
        catalog_result = con.execute("""
            SELECT variable_id, canonical_name, description_short,
                   schedule, first_observed, last_observed, entities_reporting
            FROM catalog.variables
            WHERE variable_id ILIKE ? OR canonical_name ILIKE ?
               OR description_short ILIKE ?
            ORDER BY entities_reporting DESC NULLS LAST LIMIT ?
        """, [pattern] * 3 + [limit])
        catalog_rows = _rows_to_dicts(catalog_result)

        # Crosswalk
        xw_where = ["(concept ILIKE ? OR source_variable ILIKE ? OR mdrm_variable ILIKE ? OR notes ILIKE ?)"]
        xw_params = [pattern] * 4
        if source:
            xw_where.append("source_table = ?")
            xw_params.append(source)
        xw_params.append(limit)

        xw_result = con.execute(f"""
            SELECT concept, source_variable, source_table, mdrm_variable,
                   match_confidence, notes
            FROM variable_crosswalk
            WHERE {' AND '.join(xw_where)}
            ORDER BY concept LIMIT ?
        """, xw_params)
        xw_rows = _rows_to_dicts(xw_result)

        return json.dumps({
            "catalog_matches": len(catalog_rows),
            "crosswalk_matches": len(xw_rows),
            "catalog": catalog_rows,
            "crosswalk": xw_rows,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# Curated descriptions for engineered / cross-reference tables that are
# derived in post-processing rather than ingested as raw source files, so
# they do not appear in the catalog.data_sources provenance table.
_ENGINEERED_TABLES = [
    {
        "table": "entity_xref",
        "description": "Canonical union of all known RSSD identities across every "
                       "source (institutions, transformations pred/succ, CRSP, FDIC "
                       "history, Robin crosswalk, enriched bank failures). Columns: "
                       "rssd_id, source (pipe-delimited provenance), n_sources.",
        "rows": 234462,
        "coverage": "all sources",
        "build_script": "scripts/20b_build_entity_xref.py",
    },
    {
        "table": "fdic_sdi_features",
        "description": "FDIC-SDI engineered financial ratios + F1/F3/F5 failure-lead "
                       "flags by (rssd_id, year). Cols: assets, income_ratio, "
                       "noncore_proxy, uninsured_ratio, insured_ratio, securities_ratio, "
                       "equity_ratio, nim, nim_ratio, roa, log_age, F1/F3/F5_failure.",
        "rows": 413130,
        "coverage": "1984-2025 Q4",
        "build_script": "scripts/31_build_sdi_feature_panel.py",
    },
    {
        "table": "cdr_unrealized_losses",
        "description": "FFIEC-CDR fair-value/AOCI/brokered-deposit measures by "
                       "(rssd_id, period_end). Cols: cert, afs/htm amort_cost & "
                       "fair_value, afs/htm/total_unrealized_loss, aoci, "
                       "brokered_deposits, time_dep_100_250k, time_dep_gt_250k.",
        "rows": 46929,
        "coverage": "2019-2025",
        "build_script": "scripts/32, scripts/33",
    },
]


@mcp.tool()
def show_source_descriptions() -> str:
    """Show all freenic data sources with descriptions, file types, and ingestion scripts.

    Also lists engineered/cross-reference tables (entity_xref, fdic_sdi_features,
    cdr_unrealized_losses) that are derived in post-processing and therefore not
    tracked in the raw-source provenance catalog.
    """
    con = _get_con()
    try:
        result = con.execute("""
            SELECT file_type, description, ingestion_script, COUNT(*) AS file_count
            FROM catalog.data_sources
            GROUP BY file_type, description, ingestion_script
            ORDER BY file_type, ingestion_script
        """)
        rows = _rows_to_dicts(result)
        return json.dumps({
            "count": len(rows),
            "sources": rows,
            "engineered_tables": _ENGINEERED_TABLES,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def show_regulatory_groups() -> str:
    """Show full regulatory taxonomy: entity types, regulators, and BHC/FHC/SLHC counts."""
    con = _get_con()
    try:
        result = con.execute("""
            SELECT i.entity_type, i.primary_fed_reg,
                   COUNT(*) AS entity_count,
                   SUM(CASE WHEN i.is_active THEN 1 ELSE 0 END) AS active_count,
                   SUM(CASE WHEN a.bhc_ind = 1 THEN 1 ELSE 0 END) AS bhc_count,
                   SUM(CASE WHEN a.fhc_ind = 1 THEN 1 ELSE 0 END) AS fhc_count,
                   SUM(CASE WHEN a.slhc_ind = 1 THEN 1 ELSE 0 END) AS slhc_count
            FROM institutions i
            LEFT JOIN institution_attributes a ON i.rssd_id = a.rssd_id
            GROUP BY i.entity_type, i.primary_fed_reg
            ORDER BY entity_count DESC
        """)
        rows = _rows_to_dicts(result)
        return json.dumps({"count": len(rows), "groups": rows}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def verify_mdrm_codes(codes: str) -> str:
    """Verify that MDRM variable codes exist and return their metadata.

    Args:
        codes: Comma-separated MDRM codes (e.g., "BHCK2170,FAKE9999,RCFD2170").
    """
    con = _get_con()
    try:
        code_list = [c.strip() for c in codes.split(",")]
        placeholders = ",".join(["?"] * len(code_list))
        result = con.execute(
            f"SELECT DISTINCT variable_id, item_name, reporting_form, start_date, end_date "
            f"FROM mdrm WHERE variable_id IN ({placeholders}) ORDER BY variable_id",
            code_list,
        )
        found_rows = _rows_to_dicts(result)
        found_ids = {r["variable_id"] for r in found_rows}

        for row in found_rows:
            row["found"] = True

        missing = [c for c in code_list if c not in found_ids]
        missing_rows = [{"variable_id": c, "item_name": None, "reporting_form": None,
                         "start_date": None, "end_date": None, "found": False} for c in missing]

        all_rows = found_rows + missing_rows
        return json.dumps({
            "total": len(code_list),
            "found": len(found_rows),
            "missing": len(missing),
            "data": all_rows,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def verify_rssds(rssd_ids: str) -> str:
    """Verify that RSSD IDs exist and return institution details.

    Args:
        rssd_ids: Comma-separated RSSD IDs (e.g., "1039502,9999999,1073757").
    """
    con = _get_con()
    try:
        id_list = [int(r.strip()) for r in rssd_ids.split(",")]
        placeholders = ",".join(["?"] * len(id_list))
        result = con.execute(
            f"SELECT rssd_id, name_legal, entity_type, state_code, is_active, "
            f"fdic_cert, primary_fed_reg, date_established "
            f"FROM institutions WHERE rssd_id IN ({placeholders}) ORDER BY rssd_id",
            id_list,
        )
        found_rows = _rows_to_dicts(result)
        found_ids = {r["rssd_id"] for r in found_rows}

        for row in found_rows:
            row["found"] = True

        missing = [r for r in id_list if r not in found_ids]
        missing_rows = [{"rssd_id": r, "name_legal": None, "entity_type": None,
                         "state_code": None, "is_active": None, "fdic_cert": None,
                         "primary_fed_reg": None, "date_established": None,
                         "found": False} for r in missing]

        all_rows = found_rows + missing_rows
        return json.dumps({
            "total": len(id_list),
            "found": len(found_rows),
            "missing": len(missing),
            "data": all_rows,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
