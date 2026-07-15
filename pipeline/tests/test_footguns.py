"""W4 footgun-guard tests (FREENIC_COMPLETENESS_PLAN).

Asserts the two documented footguns are neutralized by
``scripts/48_footgun_guards.py`` and stay neutralized:

  robin_panel dollar-column guard
    (a) a bare ``SELECT assets FROM robin_panel`` RAISES (the uncalibrated dollar
        names assets/deposits/loans/equity no longer resolve on the public view),
    (b) the explicit ``assets_uncalibrated_real`` column exists AND is commented
        (likewise the other three renamed columns),
    (c) the clean ratio columns (leverage, deposit_ratio, nim, ...) still resolve,
        and robin_panel_base preserves the bare dollar columns + the W2 ``source`` col,
    (+) dependents robin_panel_enriched / failure_timeline still query.

  occ_historical two-vintage guard
    (d) the two typed views occ_1867_1904 / occ_clv_1863_1941 exist, are DISJOINT,
        and sum to the occ_historical base row count.

Read-only. Uses the session-scoped ``db`` fixture from conftest.py.
"""

from __future__ import annotations

import pytest

UNCALIBRATED_BARE = ["assets", "deposits", "loans", "equity"]
UNCALIBRATED_RENAMED = [
    "assets_uncalibrated_real",
    "deposits_uncalibrated_real",
    "loans_uncalibrated_real",
    "equity_uncalibrated_real",
]
CLEAN_RATIO_COLS = ["leverage", "deposit_ratio", "nim", "liquid_ratio", "loan_ratio"]


# ----- (a) bare uncalibrated dollar names no longer resolve on the view -----

@pytest.mark.parametrize("col", UNCALIBRATED_BARE)
def test_bare_uncalibrated_name_raises(db, col):
    with pytest.raises(Exception):
        db.execute(f"SELECT {col} FROM robin_panel LIMIT 1").fetchone()


def test_robin_panel_is_a_view(db):
    t = db.execute(
        "SELECT table_type FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name='robin_panel'"
    ).fetchone()
    assert t is not None and t[0] == "VIEW", "robin_panel must be the guarded VIEW"


def test_robin_panel_base_is_a_base_table(db):
    t = db.execute(
        "SELECT table_type FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name='robin_panel_base'"
    ).fetchone()
    assert t is not None and t[0] == "BASE TABLE", "robin_panel_base must be the base table"


# ----- (b) renamed uncalibrated columns exist + are commented ---------------

@pytest.mark.parametrize("col", UNCALIBRATED_RENAMED)
def test_renamed_uncalibrated_column_exists(db, col):
    n = db.execute(
        "SELECT count(*) FROM information_schema.columns "
        "WHERE table_schema='main' AND table_name='robin_panel' AND column_name=?",
        [col],
    ).fetchone()[0]
    assert n == 1, f"{col} must exist on robin_panel"
    # and be queryable
    db.execute(f"SELECT {col} FROM robin_panel LIMIT 1").fetchone()


@pytest.mark.parametrize("col", UNCALIBRATED_RENAMED)
def test_renamed_uncalibrated_column_commented(db, col):
    c = db.execute(
        "SELECT comment FROM duckdb_columns() WHERE table_name='robin_panel' AND column_name=?",
        [col],
    ).fetchone()
    assert c is not None and c[0] not in (None, ""), f"{col} missing redirect comment"
    # the comment must redirect to the calibrated source
    cmt = c[0].lower()
    assert "clean_bank_panel" in cmt or "call_report_filings" in cmt, (
        f"{col} comment must redirect to a calibrated dollar source: {c[0]!r}"
    )


def test_robin_panel_view_commented(db):
    c = db.execute(
        "SELECT comment FROM duckdb_views() WHERE view_name='robin_panel'"
    ).fetchone()
    assert c is not None and c[0] not in (None, ""), "robin_panel view missing comment"


# ----- (c) clean ratio columns still resolve; base preserves dollars+source -

@pytest.mark.parametrize("col", CLEAN_RATIO_COLS)
def test_clean_ratio_column_still_resolves(db, col):
    db.execute(f"SELECT {col} FROM robin_panel LIMIT 1").fetchone()


def test_base_table_preserves_bare_dollar_columns(db):
    cols = {
        r[0]
        for r in db.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='main' AND table_name='robin_panel_base'"
        ).fetchall()
    }
    for c in UNCALIBRATED_BARE:
        assert c in cols, f"robin_panel_base must still carry the raw {c} column"
    assert "source" in cols, "robin_panel_base must preserve the W2 `source` column"


def test_dependents_still_queryable(db):
    for v in ("robin_panel_enriched", "failure_timeline"):
        r = db.execute(f"SELECT count(*) FROM {v}").fetchone()[0]
        assert r > 0, f"dependent view {v} returned no rows after repointing"


# ----- (d) occ two-vintage views exist, disjoint, sum to base ---------------

def test_occ_views_exist(db):
    for v in ("occ_1867_1904", "occ_clv_1863_1941"):
        t = db.execute(
            "SELECT table_type FROM information_schema.tables "
            "WHERE table_schema='main' AND table_name=?",
            [v],
        ).fetchone()
        assert t is not None and t[0] == "VIEW", f"{v} must exist as a view"


def test_occ_views_disjoint_and_sum_to_base(db):
    base = db.execute("SELECT count(*) FROM occ_historical").fetchone()[0]
    n1 = db.execute("SELECT count(*) FROM occ_1867_1904").fetchone()[0]
    n2 = db.execute("SELECT count(*) FROM occ_clv_1863_1941").fetchone()[0]
    assert n1 > 0 and n2 > 0
    assert n1 + n2 == base, f"occ views {n1}+{n2} != base {base}"
    # disjoint: each view carries exactly one source value, and they differ.
    s1 = {r[0] for r in db.execute("SELECT DISTINCT source FROM occ_1867_1904").fetchall()}
    s2 = {r[0] for r in db.execute("SELECT DISTINCT source FROM occ_clv_1863_1941").fetchall()}
    assert s1 == {"occ_historical"}, f"occ_1867_1904 sources: {s1}"
    assert s2 == {"occ_historical_clv"}, f"occ_clv_1863_1941 sources: {s2}"
    assert s1.isdisjoint(s2)


def test_occ_base_table_commented(db):
    c = db.execute(
        "SELECT comment FROM duckdb_tables() WHERE schema_name='main' AND table_name='occ_historical'"
    ).fetchone()
    assert c is not None and c[0] not in (None, ""), "occ_historical missing two-vintage comment"
    assert "vintage" in c[0].lower() or "union" in c[0].lower()
