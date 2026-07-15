"""Provenance & dedup-invariant tests (added 2026-06-05).

Enforces the public-reproducibility claim:
  1. Outputs/PROVENANCE.csv exists, parses, and has the expected schema.
  2. Every key published table has >=1 provenance row.
  3. Provenance tiers are from the controlled vocabulary.
  4. DEDUP INVARIANT — no retained luck_call_reports 1976+ cell is also present in
     call_report_filings (proves the Luck slim stayed clean and never silently re-bloats).
"""
import csv
from pathlib import Path

import pytest

import sys
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import OUTPUTS_DIR  # noqa: E402

PROVENANCE = OUTPUTS_DIR / "PROVENANCE.csv"
EXEMPTIONS = OUTPUTS_DIR / "PROVENANCE_EXEMPTIONS.csv"

EXPECTED_COLS = {"table", "era", "provenance_tier", "provider", "download_url",
                 "self_serve", "citation_required", "notes"}
VALID_TIERS = {"T1", "T2", "T3", "T3.5", "T4", "derived"}

# Key published tables that MUST carry a provenance row.
REQUIRED_TABLES = {
    "call_report_filings", "luck_call_reports", "bhcf_filings", "occ_historical",
    "fdic_financials", "fdic_sod", "bank_failures", "dfast_results",
    "cdr_unrealized_losses", "institutions", "mdrm", "fred_series",
    "fdic_sdi_features", "entity_xref",
}


def _rows():
    with open(PROVENANCE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _exempt_tables():
    """Tables with a documented table-level provenance exemption (single-source
    pure-reference or multi-source-derived tables where a constant row-level
    `source` column adds no value). Empty set if the file is absent."""
    if not EXEMPTIONS.is_file():
        return set()
    with open(EXEMPTIONS, newline="", encoding="utf-8") as f:
        return {r["table"].strip() for r in csv.DictReader(f)}


def test_provenance_file_exists_and_schema():
    assert PROVENANCE.is_file(), f"missing {PROVENANCE}"
    rows = _rows()
    assert rows, "PROVENANCE.csv has no rows"
    assert set(rows[0].keys()) == EXPECTED_COLS, f"unexpected columns: {set(rows[0].keys())}"


def test_required_tables_have_provenance():
    covered = {r["table"] for r in _rows()}
    missing = REQUIRED_TABLES - covered
    assert not missing, f"tables without a PROVENANCE.csv row: {sorted(missing)}"


def test_tiers_are_valid():
    bad = {r["provenance_tier"] for r in _rows()} - VALID_TIERS
    assert not bad, f"invalid provenance tiers: {bad}"


# physical-table -> provenance-csv key, where the two legitimately differ
# robin_panel_base is the W4-guard rename of robin_panel; PROVENANCE.csv stays keyed
# on the public name robin_panel (the guarded view consumers see).
_PROV_ALIASES = {"occ_historical_clv": "occ_historical",
                 "robin_panel_base": "robin_panel"}


def test_every_base_table_has_provenance(db):
    """Definitive-build Q1 invariant (W2-strengthened): the union of the tables
    documented in Outputs/PROVENANCE.csv and Outputs/PROVENANCE_EXEMPTIONS.csv
    covers EVERY base table in the warehouse (views exempt — they inherit from
    base tables). A new un-provenanced table fails here until its source is
    documented in one of those two files."""
    covered = {r["table"] for r in _rows()} | _exempt_tables()
    base_tables = [r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_type='BASE TABLE'"
    ).fetchall()]
    missing = [t for t in base_tables
               if _PROV_ALIASES.get(t, t) not in covered and t not in covered]
    assert not missing, (
        "base tables without a PROVENANCE.csv or PROVENANCE_EXEMPTIONS.csv row: "
        f"{sorted(missing)}")


def test_provenance_union_equals_base_tables(db):
    """W2 acceptance gate: (PROVENANCE.csv tables) ∪ (PROVENANCE_EXEMPTIONS.csv
    tables) == live base tables — exact, not hand-waved.

    Forward: every base table is documented (subsumes the test above).
    Reverse: every documented table that names a *base table* must be real, and
    every exemption must correspond to a live base table (no orphan claims).
    Views and dictionary tables documented in PROVENANCE.csv are tolerated; they
    are not base tables and intentionally not asserted here."""
    prov_tables = {r["table"] for r in _rows()}
    exempt = _exempt_tables()
    base_tables = {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_type='BASE TABLE'"
    ).fetchall()}
    # all live names that PROVENANCE.csv may legitimately reference
    all_tables = base_tables | {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall()} | set(_PROV_ALIASES)

    # Forward — full base-table coverage by the union.
    covered = prov_tables | exempt
    uncovered = {t for t in base_tables
                 if _PROV_ALIASES.get(t, t) not in covered and t not in covered}
    assert not uncovered, f"base tables not in PROVENANCE.csv ∪ EXEMPTIONS.csv: {sorted(uncovered)}"

    # Reverse — every exemption names a live base table (no stale exemptions).
    orphan_exempt = exempt - base_tables
    assert not orphan_exempt, f"exemptions for non-existent base tables: {sorted(orphan_exempt)}"

    # Reverse — no exemption silently double-counts a table that is also in PROVENANCE.csv
    # for a *different* purpose: that's fine (PROVENANCE.csv is table-level, exemptions are
    # the row-level dimension), so we only assert exemptions are a subset of documented tables.
    assert exempt <= (prov_tables | base_tables), (
        f"exemptions reference tables absent from both PROVENANCE.csv and the DB: "
        f"{sorted(exempt - (prov_tables | base_tables))}")


def test_dedup_invariant_luck_post1976_not_in_call_report(db):
    """No retained Luck 1976+ cell may duplicate call_report_filings coverage.
    If this fails, the Luck slim regressed (1976+ redundant rows re-entered)."""
    redundant = db.execute("""
        SELECT COUNT(*) FROM luck_call_reports L
        WHERE L.period_end >= DATE '1976-01-01'
          AND EXISTS (
              SELECT 1 FROM call_report_filings C
              WHERE C.rssd_id = L.entity_id AND C.period_end = L.period_end
          )
    """).fetchone()[0]
    assert redundant == 0, (
        f"{redundant} retained Luck 1976+ rows are also in call_report_filings "
        f"(slim regressed — re-run 08b_slim_luck.py)")


def test_luck_min_date_is_1959(db):
    """The retained Luck core still starts 1959Q4 (pre-1976 window intact)."""
    mn = db.execute("SELECT MIN(period_end) FROM luck_call_reports").fetchone()[0]
    assert str(mn) == "1959-12-31", f"Luck min date {mn} != 1959-12-31"
