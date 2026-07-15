"""Variable-dictionary completeness tests (Q3, Definitive Build, added 2026-06-08).

Enforces that every code used in a namespaced fact table (UBPR / RISK / FS220) is registered in the
variable dictionary — catalog.namespace_variables (built by 44_build_variable_dictionary.py) or
catalog.variables (MDRM). Registration is the hard invariant; description coverage is reported by
13_validate but not asserted here (some derived NCUA FS220 accounts have no published AcctDesc entry).
"""
import pytest

NAMESPACES = [
    ("UBPR", "ubpr_ratios", "ubpr_code"),
    ("RISK", "y15_systemic_indicators", "risk_code"),
    ("FS220", "ncua_5300", "account_code"),
]


def test_namespace_variables_table_exists(db):
    n = db.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='catalog' AND table_name='namespace_variables'").fetchone()[0]
    assert n == 1, "catalog.namespace_variables missing — run 44_build_variable_dictionary.py"


@pytest.mark.parametrize("ns,table,col", NAMESPACES)
def test_no_orphan_codes(ns, table, col, db):
    """Every distinct code in the fact table is registered in the dictionary (no orphans)."""
    orphan = db.execute(f"""
        WITH codes AS (SELECT DISTINCT {col} AS c FROM {table})
        SELECT COUNT(*) FROM codes c
        LEFT JOIN catalog.namespace_variables nv ON c.c = nv.variable_id
        LEFT JOIN catalog.variables v ON c.c = v.variable_id
        WHERE nv.variable_id IS NULL AND v.variable_id IS NULL
    """).fetchone()[0]
    assert orphan == 0, f"{ns}: {orphan} {table}.{col} codes not registered in the dictionary"


def test_namespace_variables_no_duplicate_ids_per_namespace(db):
    """variable_id is unique within a namespace (one dictionary row per code)."""
    dups = db.execute("""
        SELECT COUNT(*) FROM (
            SELECT namespace, variable_id FROM catalog.namespace_variables
            GROUP BY namespace, variable_id HAVING COUNT(*) > 1)
    """).fetchone()[0]
    assert dups == 0, f"{dups} duplicate (namespace, variable_id) rows in catalog.namespace_variables"
