"""W3 fresh-user acceptance test (FREENIC_COMPLETENESS_PLAN DoD #8).

Asserts the warehouse is self-describing:
  (a) main.freenic_manifest exists and covers every base table (+ views),
  (b) the key fact tables carry non-NULL table + column comments,
  (c) Outputs/UNITS.md exists,
and demonstrates that a naive user can resolve the two DoD tasks with CORRECT UNITS using
only the manifest + clean_bank_panel + fdic_financials (no tribal MDRM/thousands knowledge):
  1. "total assets for a bank over time"  -> clean_bank_panel (whole USD, /1e12 for $T)
  2. "net income for all banks in a year"  -> fdic_financials (USD thousands, /1e6 for $B)

Read-only. Uses the session-scoped `db` fixture from conftest.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import OUTPUTS_DIR  # noqa: E402

# Fact/reference tables that must be self-describing (table + key-column comments).
KEY_FACT_TABLES = [
    "call_report_filings",
    "bhcf_filings",
    "fdic_financials",
    "ubpr_ratios",
    "ncua_5300",
    "luck_call_reports",
    "occ_historical",
    "clean_bank_panel",
    "institutions",
    "id_crosswalk",
    "entity_xref",
]

# JPMorgan Chase Bank NA — stable identifiers used in the worked tasks.
JPM_RSSD = 852218


# ----- (a) manifest exists + covers all base tables ------------------------

def test_manifest_exists(db):
    n = db.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name='freenic_manifest'"
    ).fetchone()[0]
    assert n == 1, "main.freenic_manifest must exist (run scripts/47_self_describing.py)"


def test_manifest_columns(db):
    cols = {
        c[0]
        for c in db.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name='freenic_manifest'"
        ).fetchall()
    }
    expected = {
        "name", "kind", "schema", "purpose", "grain", "units",
        "code_column", "canonical_or_derived", "use_instead", "row_count", "period_span",
    }
    assert expected <= cols, f"manifest missing columns: {expected - cols}"


def test_manifest_covers_all_base_tables(db):
    missing = db.execute(
        """
        SELECT t.table_name
        FROM information_schema.tables t
        WHERE t.table_type = 'BASE TABLE'
          AND t.table_name <> 'freenic_manifest'
          AND t.table_name NOT IN (SELECT name FROM main.freenic_manifest)
        """
    ).fetchall()
    assert missing == [], f"base tables absent from manifest: {missing}"


def test_manifest_covers_views(db):
    missing = db.execute(
        """
        SELECT v.view_name
        FROM duckdb_views() v
        WHERE v.internal = false
          AND v.view_name NOT IN (SELECT name FROM main.freenic_manifest)
        """
    ).fetchall()
    assert missing == [], f"views absent from manifest: {missing}"


def test_manifest_rowcounts_match_live(db):
    # The manifest's row_count for a sampled set must equal the live count (regenerable/fresh).
    for name in ("fdic_financials", "clean_bank_panel", "institutions"):
        live = db.execute(f"SELECT count(*) FROM main.{name}").fetchone()[0]
        man = db.execute(
            "SELECT row_count FROM main.freenic_manifest WHERE name = ?", [name]
        ).fetchone()[0]
        assert man == live, f"{name}: manifest row_count {man} != live {live}"


# ----- (b) key fact tables have non-NULL table + column comments -----------

@pytest.mark.parametrize("tbl", KEY_FACT_TABLES)
def test_key_table_has_comment(db, tbl):
    c = db.execute(
        "SELECT comment FROM duckdb_tables() WHERE schema_name='main' AND table_name=?",
        [tbl],
    ).fetchone()
    assert c is not None and c[0] not in (None, ""), f"{tbl} missing table comment"


@pytest.mark.parametrize(
    "tbl,col",
    [
        ("call_report_filings", "value"),
        ("call_report_filings", "variable_id"),
        ("fdic_financials", "value"),
        ("ubpr_ratios", "ubpr_code"),
        ("ncua_5300", "value"),
        ("ncua_5300", "account_code"),
        ("occ_historical", "value"),
        ("clean_bank_panel", "assets_nominal"),
    ],
)
def test_key_column_has_comment(db, tbl, col):
    c = db.execute(
        "SELECT comment FROM duckdb_columns() WHERE table_name=? AND column_name=?",
        [tbl, col],
    ).fetchone()
    assert c is not None and c[0] not in (None, ""), f"{tbl}.{col} missing column comment"


def test_units_mentioned_in_comments(db):
    # The value-column comments must actually state units (thousands / whole dollars).
    cmt = db.execute(
        "SELECT comment FROM duckdb_columns() WHERE table_name='call_report_filings' AND column_name='value'"
    ).fetchone()[0].upper()
    assert "THOUSAND" in cmt
    cmt2 = db.execute(
        "SELECT comment FROM duckdb_columns() WHERE table_name='clean_bank_panel' AND column_name='assets_nominal'"
    ).fetchone()[0].upper()
    assert "WHOLE USD" in cmt2 or "WHOLE DOLLAR" in cmt2


# ----- (c) UNITS.md exists -------------------------------------------------

def test_units_doc_exists():
    p = OUTPUTS_DIR / "UNITS.md"
    assert p.exists(), "Outputs/UNITS.md must exist"
    txt = p.read_text(encoding="utf-8")
    assert "USD thousands" in txt and "whole dollar" in txt.lower()


# ----- DoD #8: the two fresh-user tasks resolve WITH CORRECT UNITS ---------
# A naive user uses only the manifest to pick the table+units, then queries.

def _manifest_units(db, name: str) -> str:
    return db.execute(
        "SELECT units FROM main.freenic_manifest WHERE name = ?", [name]
    ).fetchone()[0]


def test_task1_total_assets_over_time_correct_units(db):
    """Task 1: total assets for a bank over time, via clean_bank_panel (whole USD)."""
    # The manifest tells the naive user clean_bank_panel is whole-USD nominal.
    units = _manifest_units(db, "clean_bank_panel")
    assert "whole" in units.lower(), f"manifest units must flag whole dollars: {units!r}"

    rows = db.execute(
        """
        SELECT year, assets_nominal/1e12 AS assets_trillions
        FROM clean_bank_panel
        WHERE rssd_id = ? AND assets_nominal IS NOT NULL
        ORDER BY year DESC
        """,
        [JPM_RSSD],
    ).fetchall()
    assert len(rows) > 5, "expected a multi-year JPMorgan series"
    latest_year, latest_t = rows[0]
    # JPMorgan total assets are in the multi-$T range in recent years; with the CORRECT
    # whole-dollar divisor (/1e12) this lands in ~1-5 $T. The /1e9 trap would give ~thousands.
    assert 1.0 < latest_t < 6.0, (
        f"JPM {latest_year} assets={latest_t} $T is out of range -> wrong units divisor"
    )


def test_task2_net_income_all_banks_year_correct_units(db):
    """Task 2: net income for all banks in a year, via fdic_financials (USD thousands)."""
    units = _manifest_units(db, "fdic_financials")
    assert "thousand" in units.lower(), f"manifest units must flag thousands: {units!r}"

    # Aggregate 2024 net income across all FDIC-insured banks, in $ BILLIONS (thousands → /1e6).
    total_b = db.execute(
        """
        SELECT SUM(value)/1e6 AS net_income_billions
        FROM fdic_financials
        WHERE variable_id = 'NETINC' AND period_end = DATE '2024-12-31'
        """
    ).fetchone()[0]
    assert total_b is not None
    # US banking-system annual net income is on the order of low-hundreds of $B.
    assert 50.0 < total_b < 500.0, (
        f"2024 aggregate net income {total_b} $B is out of range -> wrong units divisor"
    )

    # And the per-bank top entry should be a sane single-bank figure (a few $B-$50B).
    top = db.execute(
        """
        SELECT value/1e6 AS net_income_billions
        FROM fdic_financials
        WHERE variable_id = 'NETINC' AND period_end = DATE '2024-12-31'
        ORDER BY value DESC LIMIT 1
        """
    ).fetchone()[0]
    assert 1.0 < top < 80.0, f"top-bank 2024 net income {top} $B out of range -> wrong units"
