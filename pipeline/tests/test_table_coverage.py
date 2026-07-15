"""Universal per-table coverage tests (Q6, Definitive Build, added 2026-06-08).

Guarantees the test matrix has NO holes: EVERY base table (main + catalog) is covered by
  - schema   : exists with >=1 column
  - integrity: non-empty (>0 rows) — the standing guard against silent truncation
               (the 2026-06 luck_call_reports->0 incident would fail here)
  - parity   : db row count == its exported parquet row count (promotes the 7-table
               coverage_analysis/integrity_check.py to an ALL-table pytest gate)
Plus grain-uniqueness for the long-form fact tables (a registered grain must be unique).

Tables are enumerated live at import so a newly-added table is automatically covered.
"""
import sys
from pathlib import Path

import duckdb
import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from utils import DB_PATH, OUTPUTS_DIR  # noqa: E402

PARQUET = OUTPUTS_DIR / "parquet"

# Enumerate base tables once at collection time.
_con = duckdb.connect(str(DB_PATH), read_only=True)
_MAIN = [r[0] for r in _con.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='main' "
    "AND table_type='BASE TABLE' ORDER BY 1").fetchall()]
_CAT = [r[0] for r in _con.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='catalog' "
    "AND table_type='BASE TABLE' ORDER BY 1").fetchall()]
_con.close()

# (schema, table, parquet_stem)
ALL_TABLES = ([("main", t, t) for t in _MAIN]
              + [("catalog", t, f"catalog_{t}") for t in _CAT])

# NOTE: grain-uniqueness is intentionally NOT re-implemented here. The authoritative,
# tolerance-aware grain tests live in test_uniqueness.py / test_ubpr.py / test_y15.py with the
# TRUE grains (e.g. call_report/ncua key on `schedule` too) and documented legacy tolerances
# (fdic_financials ~4,917 pre-existing dups; call_report 1980-82 Chicago-Fed artifacts). This
# module covers the universal holes only: schema, non-empty, and db==parquet parity for EVERY table.

_ids = [f"{s}.{t}" for s, t, _ in ALL_TABLES]


@pytest.mark.parametrize("schema,table,pqstem", ALL_TABLES, ids=_ids)
def test_table_has_columns(schema, table, pqstem, db):
    ncols = db.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema=? AND table_name=?", [schema, table]).fetchone()[0]
    assert ncols >= 1, f"{schema}.{table} has no columns"


@pytest.mark.parametrize("schema,table,pqstem", ALL_TABLES, ids=_ids)
def test_table_nonempty(schema, table, pqstem, db):
    """Every base table is non-empty — standing guard against silent truncation."""
    n = db.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
    assert n > 0, f"{schema}.{table} is EMPTY (possible truncation — check integrity_check + parquet)"


@pytest.mark.parametrize("schema,table,pqstem", ALL_TABLES, ids=_ids)
def test_table_parquet_parity(schema, table, pqstem, db):
    """db row count == exported parquet row count for every table that has a parquet."""
    pqf = PARQUET / f"{pqstem}.parquet"
    if not pqf.is_file():
        pytest.skip(f"no parquet for {schema}.{table}")
    dbn = db.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
    pqn = db.execute("SELECT COUNT(*) FROM read_parquet(?)", [pqf.as_posix()]).fetchone()[0]
    assert dbn == pqn, f"{schema}.{table}: db={dbn:,} != parquet={pqn:,} (re-export)"
