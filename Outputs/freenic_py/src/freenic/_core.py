"""Core engine: Parquet discovery, DuckDB-on-Parquet connection, query interface."""

import os
import threading
from pathlib import Path

import duckdb
import pandas as pd

from freenic._tables import TABLES, TABLE_DESCRIPTIONS

_lock = threading.Lock()
_con = None
_data_dir = None


def set_data_dir(path: str) -> None:
    """Set the path to the freenic Parquet directory.

    Args:
        path: Directory containing freenic .parquet files.
    """
    global _data_dir, _con
    p = Path(path)
    if not p.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")
    with _lock:
        _data_dir = str(p)
        if _con is not None:
            _con.close()
            _con = None


def _get_data_dir() -> str:
    global _data_dir
    if _data_dir is None:
        env = os.environ.get("FREENIC_DATA_DIR")
        if env:
            _data_dir = env
    if _data_dir is None:
        raise RuntimeError(
            "freenic data directory not set. "
            "Call freenic.set_data_dir('/path/to/parquet') "
            "or set the FREENIC_DATA_DIR environment variable."
        )
    return _data_dir


def _get_con() -> duckdb.DuckDBPyConnection:
    """Get or create in-memory DuckDB with Parquet views registered."""
    global _con
    with _lock:
        if _con is not None:
            return _con
        data_dir = _get_data_dir()
        con = duckdb.connect(":memory:")
        for table in TABLES:
            pq_path = Path(data_dir) / f"{table}.parquet"
            if pq_path.exists():
                con.execute(
                    f"CREATE VIEW \"{table}\" AS "
                    f"SELECT * FROM read_parquet('{pq_path.as_posix()}')"
                )
        _con = con
        return _con


def query(sql: str, params: list | dict | None = None) -> pd.DataFrame:
    """Execute SQL against freenic Parquet-backed views.

    Args:
        sql: SQL query string.
        params: Optional query parameters (list for positional, dict for named).

    Returns:
        Query results as a pandas DataFrame.

    Example:
        >>> freenic.query("SELECT * FROM institutions WHERE rssd_id = ?", [1039502])
    """
    con = _get_con()
    if params is not None:
        return con.execute(sql, params).df()
    return con.execute(sql).df()


def list_tables() -> pd.DataFrame:
    """List all available freenic tables with descriptions.

    Returns:
        DataFrame with columns: table, description, available.
    """
    data_dir = _get_data_dir()
    rows = []
    for table in TABLES:
        pq_path = Path(data_dir) / f"{table}.parquet"
        rows.append({
            "table": table,
            "description": TABLE_DESCRIPTIONS.get(table, ""),
            "available": pq_path.exists(),
        })
    return pd.DataFrame(rows)


def describe(table_name: str) -> pd.DataFrame:
    """Get column names and types for a table.

    Args:
        table_name: Name of the table to describe.

    Returns:
        DataFrame with columns: column_name, column_type.
    """
    con = _get_con()
    return con.execute(f'DESCRIBE "{table_name}"').df()


def close() -> None:
    """Close the DuckDB connection and release resources."""
    global _con
    with _lock:
        if _con is not None:
            _con.close()
            _con = None
