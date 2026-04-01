"""Typed accessor functions for common freenic queries."""

from __future__ import annotations

import pandas as pd

from freenic._core import query


def lookup_institution(
    search: str,
    field: str = "name",
    limit: int = 20,
) -> pd.DataFrame:
    """Search for institutions by name, RSSD ID, FDIC cert, or state.

    Args:
        search: Search term.
        field: One of "name", "rssd_id", "fdic_cert", "state".
        limit: Maximum results to return.

    Returns:
        DataFrame of matching institutions.
    """
    if field == "rssd_id":
        return query(
            "SELECT rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, date_established, primary_fed_reg "
            "FROM institutions WHERE rssd_id = ? LIMIT ?",
            [int(search), limit],
        )
    elif field == "fdic_cert":
        return query(
            "SELECT rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, date_established, primary_fed_reg "
            "FROM institutions WHERE fdic_cert = ? LIMIT ?",
            [int(search), limit],
        )
    elif field == "state":
        return query(
            "SELECT rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, date_established, primary_fed_reg "
            "FROM institutions WHERE UPPER(state_code) = UPPER(?) "
            "ORDER BY is_active DESC, name_legal LIMIT ?",
            [search, limit],
        )
    else:
        return query(
            "SELECT rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, date_established, primary_fed_reg "
            "FROM institutions WHERE name_legal ILIKE ? "
            "ORDER BY is_active DESC, name_legal LIMIT ?",
            [f"%{search}%", limit],
        )


def get_financials(
    rssd_id: int,
    variables: list[str] | str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    source: str = "bhcf",
) -> pd.DataFrame:
    """Get financial time series for an institution.

    Args:
        rssd_id: RSSD identifier.
        variables: Variable ID(s) to filter. String or list of strings.
        start_date: Start date filter (YYYY-MM-DD).
        end_date: End date filter (YYYY-MM-DD).
        source: Data source - "bhcf", "luck", "fdic", or "cross".

    Returns:
        DataFrame with financial data.
    """
    if isinstance(variables, str):
        variables = [variables]

    if source == "cross":
        conditions = ["rssd_id = ?"]
        params: list = [rssd_id]
        if variables:
            placeholders = ", ".join(["?"] * len(variables))
            conditions.append(f"concept IN ({placeholders})")
            params.extend(variables)
        if start_date:
            conditions.append("period_end >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("period_end <= ?")
            params.append(end_date)
        where = " AND ".join(conditions)
        return query(
            f"SELECT * FROM cross_source_financials "
            f"WHERE {where} ORDER BY period_end DESC",
            params,
        )

    table_map = {
        "bhcf": ("bhcf_filings", "rssd_id", "period_end"),
        "luck": ("luck_call_reports", "entity_id", "period_end"),
        "fdic": ("fdic_financials", "fdic_cert", "period_end"),
    }
    if source not in table_map:
        raise ValueError(f"Unknown source '{source}'. Use: bhcf, luck, fdic, cross")

    table, id_col, date_col = table_map[source]
    conditions = [f"{id_col} = ?"]
    params = [rssd_id]

    if variables:
        placeholders = ", ".join(["?"] * len(variables))
        conditions.append(f"variable_id IN ({placeholders})")
        params.extend(variables)
    if start_date:
        conditions.append(f"{date_col} >= ?")
        params.append(start_date)
    if end_date:
        conditions.append(f"{date_col} <= ?")
        params.append(end_date)

    where = " AND ".join(conditions)
    return query(
        f"SELECT * FROM {table} WHERE {where} ORDER BY {date_col} DESC",
        params,
    )


def search_variables(search_term: str, limit: int = 30) -> pd.DataFrame:
    """Search the variable catalog by name, description, or code.

    Args:
        search_term: Keyword to search for.
        limit: Maximum results.

    Returns:
        DataFrame of matching variables from catalog and crosswalk.
    """
    pattern = f"%{search_term}%"
    return query(
        "SELECT variable_id, canonical_name, description_short, "
        "first_observed, last_observed, entities_reporting "
        "FROM catalog_variables "
        "WHERE variable_id ILIKE ? OR canonical_name ILIKE ? "
        "OR description_short ILIKE ? "
        "ORDER BY entities_reporting DESC NULLS LAST "
        "LIMIT ?",
        [pattern, pattern, pattern, limit],
    )


def get_hierarchy(
    rssd_id: int,
    direction: str = "down",
    active_only: bool = True,
) -> pd.DataFrame:
    """Get corporate parent-child relationships for an entity.

    Args:
        rssd_id: RSSD identifier.
        direction: "down" for subsidiaries, "up" for parent chain.
        active_only: If True, only current relationships.

    Returns:
        DataFrame of related entities.
    """
    date_filter = " AND r.dt_end IS NULL" if active_only else ""

    if direction == "up":
        return query(
            f"SELECT r.rssd_parent, p.name_legal AS parent_name, "
            f"r.rssd_offspring, c.name_legal AS subsidiary_name, "
            f"r.pct_equity, r.dt_start, r.dt_end "
            f"FROM relationships r "
            f"JOIN institutions p ON r.rssd_parent = p.rssd_id "
            f"JOIN institutions c ON r.rssd_offspring = c.rssd_id "
            f"WHERE r.rssd_offspring = ?{date_filter} "
            f"ORDER BY r.pct_equity DESC NULLS LAST",
            [rssd_id],
        )
    else:
        return query(
            f"SELECT r.rssd_parent, p.name_legal AS parent_name, "
            f"r.rssd_offspring, c.name_legal AS subsidiary_name, "
            f"r.pct_equity, r.dt_start, r.dt_end "
            f"FROM relationships r "
            f"JOIN institutions p ON r.rssd_parent = p.rssd_id "
            f"JOIN institutions c ON r.rssd_offspring = c.rssd_id "
            f"WHERE r.rssd_parent = ?{date_filter} "
            f"ORDER BY r.pct_equity DESC NULLS LAST",
            [rssd_id],
        )


def get_failures(
    start_year: int | None = None,
    end_year: int | None = None,
    state: str | None = None,
    limit: int = 100,
) -> pd.DataFrame:
    """Get bank failure records.

    Args:
        start_year: Filter failures from this year.
        end_year: Filter failures through this year.
        state: Filter by state abbreviation.
        limit: Maximum results.

    Returns:
        DataFrame of bank failures.
    """
    conditions = []
    params: list = []

    if start_year is not None:
        conditions.append("failure_year >= ?")
        params.append(start_year)
    if end_year is not None:
        conditions.append("failure_year <= ?")
        params.append(end_year)
    if state is not None:
        conditions.append("UPPER(state_code) = UPPER(?)")
        params.append(state)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)

    return query(
        f"SELECT cert, bank_name, city, state_code, closing_date, "
        f"failure_year, total_assets, total_deposits, estimated_loss, "
        f"acquiring_institution, resolution_type "
        f"FROM bank_failures {where} "
        f"ORDER BY closing_date DESC LIMIT ?",
        params,
    )


def lookup_rssd(
    name: str | None = None,
    fdic_cert: int | None = None,
    permco: int | None = None,
    rssd_id: int | None = None,
    limit: int = 20,
) -> pd.DataFrame:
    """Resolve an identifier to RSSD ID(s) with institution details.

    Provide exactly one of name, fdic_cert, permco, or rssd_id.

    Args:
        name: Institution name (fuzzy ILIKE match).
        fdic_cert: FDIC certificate number (exact match).
        permco: CRSP PERMCO identifier (exact match via crsp_mapping).
        rssd_id: RSSD ID (exact match, returns full details).
        limit: Maximum results for name searches.

    Returns:
        DataFrame with rssd_id, name_legal, entity_type, state_code, city,
        is_active, fdic_cert, primary_fed_reg, date_established.
    """
    cols = ("rssd_id, name_legal, entity_type, state_code, city, "
            "is_active, fdic_cert, primary_fed_reg, date_established")

    if rssd_id is not None:
        return query(f"SELECT {cols} FROM institutions WHERE rssd_id = ?", [rssd_id])
    elif fdic_cert is not None:
        return query(f"SELECT {cols} FROM institutions WHERE fdic_cert = ?", [fdic_cert])
    elif permco is not None:
        return query(
            f"SELECT i.rssd_id, i.name_legal, i.entity_type, i.state_code, "
            f"i.city, i.is_active, i.fdic_cert, i.primary_fed_reg, "
            f"i.date_established, c.permco, c.dt_start, c.dt_end "
            f"FROM crsp_mapping c "
            f"JOIN institutions i ON c.rssd_id = i.rssd_id "
            f"WHERE c.permco = ? "
            f"ORDER BY c.dt_start DESC",
            [permco],
        )
    elif name is not None:
        return query(
            f"SELECT {cols} FROM institutions "
            f"WHERE name_legal ILIKE ? "
            f"ORDER BY is_active DESC, name_legal LIMIT ?",
            [f"%{name}%", limit],
        )
    else:
        raise ValueError("Provide at least one of: name, fdic_cert, permco, rssd_id")


def lookup_column_id(
    search: str,
    source: str | None = None,
    limit: int = 30,
) -> pd.DataFrame:
    """Search for variable/column IDs across MDRM and the variable crosswalk.

    Args:
        search: Keyword to search (matches variable_id, name, description).
        source: Optional filter by source table (e.g., "luck_call_reports").
        limit: Maximum results.

    Returns:
        DataFrame with variable_id, canonical_name/concept, source info.
    """
    pattern = f"%{search}%"

    # Search MDRM/catalog
    catalog_df = query(
        "SELECT variable_id, canonical_name, description_short, "
        "schedule, first_observed, last_observed, entities_reporting "
        "FROM catalog_variables "
        "WHERE variable_id ILIKE ? OR canonical_name ILIKE ? "
        "OR description_short ILIKE ? "
        "ORDER BY entities_reporting DESC NULLS LAST "
        "LIMIT ?",
        [pattern, pattern, pattern, limit],
    )
    catalog_df.insert(0, "match_source", "mdrm_catalog")

    # Search crosswalk
    xw_conditions = [
        "(concept ILIKE ? OR source_variable ILIKE ? "
        "OR mdrm_variable ILIKE ? OR notes ILIKE ?)"
    ]
    xw_params: list = [pattern, pattern, pattern, pattern]
    if source is not None:
        xw_conditions.append("source_table = ?")
        xw_params.append(source)
    xw_params.append(limit)

    xw_df = query(
        f"SELECT concept, source_variable, source_table, "
        f"mdrm_variable, match_confidence, notes "
        f"FROM variable_crosswalk "
        f"WHERE {' AND '.join(xw_conditions)} "
        f"ORDER BY concept LIMIT ?",
        xw_params,
    )
    xw_df.insert(0, "match_source", "crosswalk")

    return pd.concat([catalog_df, xw_df], ignore_index=True)


def show_source_descriptions() -> pd.DataFrame:
    """Show all freenic data sources with descriptions, file types, and scripts.

    Returns:
        DataFrame with one row per distinct source type: file_type,
        description, ingestion_script, file_count.
    """
    return query(
        "SELECT file_type, description, ingestion_script, "
        "COUNT(*) AS file_count "
        "FROM catalog_data_sources "
        "GROUP BY file_type, description, ingestion_script "
        "ORDER BY file_type, ingestion_script"
    )


def show_regulatory_groups() -> pd.DataFrame:
    """Show full regulatory taxonomy: entity types, regulators, and BHC/FHC/SLHC status.

    Returns:
        DataFrame with entity_type, primary_fed_reg, counts, and
        BHC/FHC/SLHC indicator totals.
    """
    return query("""
        SELECT
            i.entity_type,
            i.primary_fed_reg,
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


def verify_mdrm_codes(*codes: str) -> pd.DataFrame:
    """Verify that MDRM variable codes exist and return their metadata.

    Args:
        *codes: One or more variable IDs (e.g., "BHCK2170", "RCFD2170").

    Returns:
        DataFrame with variable_id, item_name, reporting_form, start_date,
        end_date, and a 'found' boolean. Missing codes appear with found=False.

    Example:
        >>> freenic.verify_mdrm_codes("BHCK2170", "FAKE9999", "RCFD2170")
    """
    code_list = list(codes)
    if not code_list:
        raise ValueError("Provide at least one MDRM code to verify")

    placeholders = ", ".join(["?"] * len(code_list))
    found_df = query(
        f"SELECT DISTINCT variable_id, item_name, reporting_form, "
        f"start_date, end_date "
        f"FROM mdrm WHERE variable_id IN ({placeholders}) "
        f"ORDER BY variable_id",
        code_list,
    )
    found_df["found"] = True

    # Identify missing codes
    found_ids = set(found_df["variable_id"].tolist())
    missing = [c for c in code_list if c not in found_ids]
    if missing:
        missing_df = pd.DataFrame({
            "variable_id": missing,
            "item_name": None,
            "reporting_form": None,
            "start_date": None,
            "end_date": None,
            "found": False,
        })
        return pd.concat([found_df, missing_df], ignore_index=True)

    return found_df


def verify_rssds(*rssd_ids: int) -> pd.DataFrame:
    """Verify that RSSD IDs exist and return institution details.

    Args:
        *rssd_ids: One or more RSSD identifiers.

    Returns:
        DataFrame with rssd_id, name_legal, entity_type, state_code,
        is_active, and a 'found' boolean. Missing IDs appear with found=False.

    Example:
        >>> freenic.verify_rssds(1039502, 9999999, 1073757)
    """
    id_list = list(rssd_ids)
    if not id_list:
        raise ValueError("Provide at least one RSSD ID to verify")

    placeholders = ", ".join(["?"] * len(id_list))
    found_df = query(
        f"SELECT rssd_id, name_legal, entity_type, state_code, "
        f"is_active, fdic_cert, primary_fed_reg, date_established "
        f"FROM institutions WHERE rssd_id IN ({placeholders}) "
        f"ORDER BY rssd_id",
        id_list,
    )
    found_df["found"] = True

    # Identify missing IDs
    found_ids = set(found_df["rssd_id"].tolist())
    missing = [r for r in id_list if r not in found_ids]
    if missing:
        missing_df = pd.DataFrame({
            "rssd_id": missing,
            "name_legal": None,
            "entity_type": None,
            "state_code": None,
            "is_active": None,
            "fdic_cert": None,
            "primary_fed_reg": None,
            "date_established": None,
            "found": False,
        })
        return pd.concat([found_df, missing_df], ignore_index=True)

    return found_df
