"""Uniqueness / dedup integrity invariants (Step 7, added 2026-06-06).

Enforces the natural grain of each table is unique, with documented tolerances for two
PRE-EXISTING legacy artifacts (not introduced by recent work):
  - call_report_filings: 3,798 dup-keys / 7,596 rows, ALL in 1980-1982 (legacy Chicago Fed
    layer); the modern/CDR/cdrgap layers are clean. We assert the cdrgap recovery added no dups.
  - fdic_financials: 4,917 pre-existing dup rows (tolerance-bounded).
  - occ_historical intentionally keeps two penny-matched vintages (occ + occ_historical_clv);
    their overlap (~4.23M cells) is by design, documented in COVERAGE_GAPS, NOT a dup bug.
Big-table full dup-scans (call_report 1.9B, bhcf 208M) are avoided in the routine suite for
speed; bhcf is verified unique, call_report's clean layers are guarded via the cdrgap subset.
"""
import pytest

# table -> natural-grain key; must be EXACTLY unique (0 dups)
EXACT_UNIQUE = {
    "luck_call_reports":  "entity_id, period_end, variable_id",
    "ncua_5300":          "cu_number, period_end, schedule, account_code",
    "ncua_cu_directory":  "cu_number, period_end",
    "hmda_summary":       "lei, activity_year, loan_purpose",
    "sec_cik_crosswalk":  "cik",
    "fdic_sdi_features":  "rssd_id, year",
}


@pytest.mark.parametrize("table,key", EXACT_UNIQUE.items())
def test_grain_unique(db, table, key):
    tot = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    dist = db.execute(f"SELECT COUNT(*) FROM (SELECT 1 FROM {table} GROUP BY {key})").fetchone()[0]
    assert tot == dist, f"{table}: {tot - dist} duplicate {key} keys (expected 0)"


def test_pillar3_no_exact_duplicate_rows(db):
    """pillar3_disclosures must have no all-columns-identical rows (deduped 2026-06-06)."""
    tot = db.execute("SELECT COUNT(*) FROM pillar3_disclosures").fetchone()[0]
    dist = db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT * FROM pillar3_disclosures)").fetchone()[0]
    assert tot == dist, f"pillar3_disclosures has {tot - dist} exact-duplicate rows"


def test_call_report_cdrgap_recovery_unique(db):
    """The A3 trust-company recovery (source_file cdrgap_*) must add no duplicate grain keys."""
    dups = db.execute("""
        SELECT COALESCE(SUM(c - 1), 0) FROM (
            SELECT COUNT(*) c FROM call_report_filings
            WHERE source_file LIKE 'cdrgap%'
            GROUP BY rssd_id, period_end, schedule, variable_id HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dups == 0, f"cdrgap recovery introduced {dups} duplicate rows"


def test_call_report_no_modern_dups(db):
    """Modern call reports (>=2012, the CDR era) must be dup-free; legacy 1980-82 dups are
    a documented pre-existing Chicago-Fed artifact and excluded here."""
    dups = db.execute("""
        SELECT COALESCE(SUM(c - 1), 0) FROM (
            SELECT COUNT(*) c FROM call_report_filings
            WHERE period_end >= DATE '2012-01-01'
            GROUP BY rssd_id, period_end, schedule, variable_id HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dups == 0, f"{dups} duplicate rows in modern (>=2012) call reports"


def test_fdic_financials_dups_within_tolerance(db):
    """fdic_financials carries ~4,917 pre-existing dup rows; guard against material growth."""
    tot = db.execute("SELECT COUNT(*) FROM fdic_financials").fetchone()[0]
    dist = db.execute(
        "SELECT COUNT(*) FROM (SELECT 1 FROM fdic_financials GROUP BY rssd_id, period_end, variable_id)"
    ).fetchone()[0]
    dups = tot - dist
    assert dups < 6000, f"fdic_financials dup rows {dups} exceeded tolerance (pre-existing ~4,917)"
