"""C4: Referential integrity tests — entity ID match rates against institutions."""

import pytest


def _match_rate(db, table, id_col="rssd_id"):
    total = db.execute(f"SELECT COUNT(DISTINCT {id_col}) FROM {table}").fetchone()[0]
    if total == 0:
        return 0.0
    matched = db.execute(f"""
        SELECT COUNT(DISTINCT t.{id_col})
        FROM {table} t
        JOIN institutions i ON t.{id_col} = i.rssd_id
    """).fetchone()[0]
    return matched / total


def test_bhcf_match_rate(db):
    rate = _match_rate(db, "bhcf_filings")
    assert rate >= 0.90, f"bhcf_filings match rate {rate:.1%} < 90%"


def test_dfast_match_rate(db):
    rate = _match_rate(db, "dfast_results")
    assert rate >= 0.85, f"dfast_results match rate {rate:.1%} < 85%"


def test_pillar3_match_rate(db):
    rate = _match_rate(db, "pillar3_disclosures")
    assert rate >= 0.70, f"pillar3_disclosures match rate {rate:.1%} < 70%"


@pytest.mark.xfail(reason="Historical banks predate NIC database")
def test_call_report_match_rate(db):
    rate = _match_rate(db, "call_report_filings")
    assert rate >= 0.50, f"call_report_filings match rate {rate:.1%} < 50%"


@pytest.mark.xfail(reason="Historical banks predate NIC database")
def test_luck_match_rate(db):
    rate = _match_rate(db, "luck_call_reports", id_col="entity_id")
    assert rate >= 0.50, f"luck_call_reports match rate {rate:.1%} < 50%"


@pytest.mark.xfail(reason="FDIC uses cert IDs, not RSSD IDs for most banks")
def test_fdic_financials_match_rate(db):
    rate = _match_rate(db, "fdic_financials")
    assert rate >= 0.50, f"fdic_financials match rate {rate:.1%} < 50%"
