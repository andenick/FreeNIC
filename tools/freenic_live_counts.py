"""Authoritative live-count probe for the freenic warehouse.

Connects READ-ONLY to the live DuckDB warehouse and emits the single source of
truth for every count quoted in freenic's docs (README, DATA_DICTIONARY,
QUICK_START, DATA_SOURCE_INVENTORY, release notes). The companion gate
``check_doc_counts.py`` parses the doc-stated numbers back out and asserts they
match this JSON, so doc drift cannot recur (W1.4 of FREENIC_COMPLETENESS_PLAN).

Emits:
  - base-table count (+ schema breakdown main/catalog/dict)
  - view count
  - total rows = SUM(COUNT(*)) over base tables in main + catalog + dict
  - max period_end across tables carrying a period_end column
  - parquet-file count under Outputs/parquet/
  - ingestion-script count (pipeline/scripts/*.py)
  - test-file count (pipeline/tests/test_*.py)

Prints the JSON to stdout AND writes Technical/coverage_analysis/live_counts.json.

WAREHOUSE IS READ-ONLY. This script never writes to the DB or the parquet dir.

Usage:
    python tools/freenic_live_counts.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

# --- resolve DB_PATH from the pipeline's own utils, falling back to the default ---
# Canonical code locations moved under pipeline/ in the v1.0.0 public-layout restructure
# (was Technical/freenic_ingestion/scripts + .../tests, now superseded). Repointed to the
# tracked pipeline/ homes 2026-07-16 so the "single source of truth" probe counts the live
# shipped pipeline, not the superseded pre-restructure dirs.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "pipeline" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from utils import DB_PATH as _DB_PATH  # type: ignore
    DB_PATH = Path(_DB_PATH)
except Exception:
    DB_PATH = PROJECT_ROOT / "Outputs" / "freenic.duckdb"

PARQUET_DIR = PROJECT_ROOT / "Outputs" / "parquet"
TESTS_DIR = PROJECT_ROOT / "pipeline" / "tests"
COVERAGE_DIR = PROJECT_ROOT / "Technical" / "coverage_analysis"
OUT_JSON = COVERAGE_DIR / "live_counts.json"

# Schemas that hold base data tables (excludes information_schema / pg_catalog / temp).
DATA_SCHEMAS = ("main", "catalog", "dict")


def _base_tables(con, schema: str) -> list[str]:
    return [
        r[0]
        for r in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = ? AND table_type = 'BASE TABLE' "
            "ORDER BY table_name",
            [schema],
        ).fetchall()
    ]


def _views(con, schema: str) -> list[str]:
    return [
        r[0]
        for r in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = ? AND table_type = 'VIEW' "
            "ORDER BY table_name",
            [schema],
        ).fetchall()
    ]


def _has_column(con, schema: str, table: str, column: str) -> bool:
    n = con.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = ? AND table_name = ? AND column_name = ?",
        [schema, table, column],
    ).fetchone()[0]
    return n > 0


def collect() -> dict:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        schema_base_tables = {s: _base_tables(con, s) for s in DATA_SCHEMAS}
        schema_views = {s: _views(con, s) for s in DATA_SCHEMAS}

        base_table_counts = {s: len(t) for s, t in schema_base_tables.items()}
        base_table_total = sum(base_table_counts.values())
        view_counts = {s: len(v) for s, v in schema_views.items()}
        view_total = sum(view_counts.values())

        # Total rows = SUM over base tables in all data schemas.
        total_rows = 0
        per_table_rows: dict[str, int] = {}
        for schema, tables in schema_base_tables.items():
            for t in tables:
                n = con.execute(f'SELECT COUNT(*) FROM "{schema}"."{t}"').fetchone()[0]
                per_table_rows[f"{schema}.{t}"] = n
                total_rows += n

        # max period_end across base tables that carry a period_end column.
        max_period_end = None
        for schema, tables in schema_base_tables.items():
            for t in tables:
                if _has_column(con, schema, t, "period_end"):
                    r = con.execute(
                        f'SELECT MAX(period_end) FROM "{schema}"."{t}"'
                    ).fetchone()[0]
                    if r is not None:
                        rs = str(r)
                        if max_period_end is None or rs > max_period_end:
                            max_period_end = rs

        # Top-10 largest base tables (for human-readable doc notes).
        largest = sorted(per_table_rows.items(), key=lambda kv: kv[1], reverse=True)[:10]
    finally:
        con.close()

    parquet_count = len(sorted(PARQUET_DIR.glob("*.parquet"))) if PARQUET_DIR.is_dir() else 0
    script_count = len(sorted(SCRIPTS_DIR.glob("*.py"))) if SCRIPTS_DIR.is_dir() else 0
    test_count = len(sorted(TESTS_DIR.glob("test_*.py"))) if TESTS_DIR.is_dir() else 0

    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "db_path": str(DB_PATH),
        "base_tables_total": base_table_total,
        "base_tables_by_schema": base_table_counts,
        "views_total": view_total,
        "views_by_schema": view_counts,
        "total_rows": total_rows,
        "max_period_end": max_period_end,
        "parquet_files": parquet_count,
        "ingestion_scripts": script_count,
        "test_files": test_count,
        "largest_tables": [{"table": k, "rows": v} for k, v in largest],
    }


def main() -> None:
    counts = collect()
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))
    print(f"\nwrote {OUT_JSON}", file=sys.stderr)


if __name__ == "__main__":
    main()
