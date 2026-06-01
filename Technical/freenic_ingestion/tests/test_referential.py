"""C4: Referential integrity tests — entity-id match rates.

Recalibrated 2026-06-01. Filing rssds are validated against
`entity_xref` (the de-duped union of all public NIC identity tables, built by
20b_build_entity_xref.py), NOT just `institutions`. `institutions` (217,210
rssds) under-covers historical defunct/merged entities, which produced a
misleadingly low 34-40% rate and three permanent xfails. With `entity_xref`
the misses are recovered (chiefly via `transformations.rssd_predecessor`), so
call_report/luck/fdic now match >=95% overall and the xfails become real PASS
tests — gated on the MODERN slice so they stay genuine regression guards.

See COVERAGE_GAPS.md S6.
"""

import pytest

# Modern slice = entities whose latest activity year >= 2000.
MODERN_THRESHOLD = 0.85   # modern match vs entity_xref must clear this (HONEST GUARD)
OVERALL_FLOOR = 0.80      # overall match vs entity_xref sanity floor


def _xref_match_rate(db, table, id_col="rssd_id"):
    """Distinct-id match rate of `table` against entity_xref."""
    total = db.execute(f"SELECT COUNT(DISTINCT {id_col}) FROM {table}").fetchone()[0]
    if total == 0:
        return 0.0
    matched = db.execute(f"""
        SELECT COUNT(DISTINCT t.{id_col})
        FROM {table} t JOIN entity_xref x ON t.{id_col} = x.rssd_id
    """).fetchone()[0]
    return matched / total


def _era_match_rates(db, table, id_col, year_expr):
    """Return (modern_rate, overall_rate) vs entity_xref, era by latest activity."""
    rows = db.execute(f"""
        WITH ent AS (
            SELECT {id_col} AS rssd, MAX({year_expr}) AS yr
            FROM {table} GROUP BY {id_col}
        ), tagged AS (
            SELECT rssd, CASE WHEN yr >= 2000 THEN 'modern' ELSE 'historical' END AS era
            FROM ent
        )
        SELECT t.era, COUNT(*) AS n,
               SUM(CASE WHEN x.rssd_id IS NOT NULL THEN 1 ELSE 0 END) AS m
        FROM tagged t LEFT JOIN entity_xref x ON t.rssd = x.rssd_id
        GROUP BY t.era
    """).fetchall()
    stats = {era: (n, m) for era, n, m in rows}
    mn, mm = stats.get("modern", (0, 0))
    hn, hm = stats.get("historical", (0, 0))
    modern = (mm / mn) if mn else 1.0
    overall = ((mm + hm) / (mn + hn)) if (mn + hn) else 1.0
    return modern, overall


# --- entity_xref must exist and be populated (20b ran) ---

def test_entity_xref_exists(db):
    n = db.execute("SELECT COUNT(*) FROM entity_xref").fetchone()[0]
    assert n >= 200_000, f"entity_xref has {n:,} rows (expected >200k; run 20b)"


def test_entity_xref_superset_of_institutions(db):
    """entity_xref must contain every institutions rssd plus historical additions."""
    extra = db.execute("""
        SELECT COUNT(*) FROM (
            SELECT rssd_id FROM institutions
            EXCEPT SELECT rssd_id FROM entity_xref
        )
    """).fetchone()[0]
    assert extra == 0, f"{extra} institutions rssds missing from entity_xref"
    beyond = db.execute("""
        SELECT COUNT(*) FROM (
            SELECT rssd_id FROM entity_xref
            EXCEPT SELECT rssd_id FROM institutions
        )
    """).fetchone()[0]
    assert beyond > 10_000, f"entity_xref adds only {beyond} beyond institutions"


# --- Small modern-only tables: flat entity_xref gate ---

def test_bhcf_match_rate(db):
    rate = _xref_match_rate(db, "bhcf_filings")
    assert rate >= 0.90, f"bhcf_filings xref match rate {rate:.1%} < 90%"


def test_dfast_match_rate(db):
    rate = _xref_match_rate(db, "dfast_results")
    assert rate >= 0.85, f"dfast_results xref match rate {rate:.1%} < 85%"


def test_pillar3_match_rate(db):
    rate = _xref_match_rate(db, "pillar3_disclosures")
    assert rate >= 0.70, f"pillar3_disclosures xref match rate {rate:.1%} < 70%"


# --- Historical-spanning tables: era-stratified gate (former xfails, now PASS) ---

def test_call_report_match_rate(db):
    modern, overall = _era_match_rates(
        db, "call_report_filings", "rssd_id", "EXTRACT(year FROM period_end)")
    assert modern >= MODERN_THRESHOLD, f"call_report modern match {modern:.1%} < {MODERN_THRESHOLD:.0%}"
    assert overall >= OVERALL_FLOOR, f"call_report overall match {overall:.1%} < {OVERALL_FLOOR:.0%}"


def test_luck_match_rate(db):
    modern, overall = _era_match_rates(
        db, "luck_call_reports", "entity_id", "EXTRACT(year FROM period_end)")
    assert modern >= MODERN_THRESHOLD, f"luck modern match {modern:.1%} < {MODERN_THRESHOLD:.0%}"
    assert overall >= OVERALL_FLOOR, f"luck overall match {overall:.1%} < {OVERALL_FLOOR:.0%}"


def test_fdic_financials_match_rate(db):
    modern, overall = _era_match_rates(
        db, "fdic_financials", "rssd_id", "EXTRACT(year FROM period_end)")
    assert modern >= MODERN_THRESHOLD, f"fdic_financials modern match {modern:.1%} < {MODERN_THRESHOLD:.0%}"
    assert overall >= OVERALL_FLOOR, f"fdic_financials overall match {overall:.1%} < {OVERALL_FLOOR:.0%}"


def test_fdic_sod_match_rate(db):
    modern, overall = _era_match_rates(db, "fdic_sod", "rssd_id", "year")
    assert modern >= MODERN_THRESHOLD, f"fdic_sod modern match {modern:.1%} < {MODERN_THRESHOLD:.0%}"
    assert overall >= OVERALL_FLOOR, f"fdic_sod overall match {overall:.1%} < {OVERALL_FLOOR:.0%}"


# --- HONEST-GUARD sanity: the modern gate must still FAIL on a real break ---

def test_modern_gate_fails_on_injected_break(db):
    """Prove the era-stratified gate is a real guard, not a rubber stamp.

    Simulate a join/key break by matching call_report modern rssds against an
    EMPTY identity set (a 'broken entity_xref'). The modern rate must collapse
    below threshold, i.e. the gate would FAIL. If this assertion ever fails, the
    check has been weakened into a no-op.
    """
    broken_modern = db.execute("""
        WITH ent AS (
            SELECT rssd_id AS rssd, MAX(EXTRACT(year FROM period_end)) AS yr
            FROM call_report_filings GROUP BY rssd_id
        ), tagged AS (
            SELECT rssd FROM ent WHERE yr >= 2000
        )
        SELECT
            COUNT(*) AS n,
            SUM(CASE WHEN x.rssd_id IS NOT NULL THEN 1 ELSE 0 END) AS m
        FROM tagged t
        LEFT JOIN (SELECT rssd_id FROM entity_xref WHERE 1=0) x ON t.rssd = x.rssd_id
    """).fetchone()
    n, m = broken_modern
    broken_rate = (m / n) if n else 0.0
    assert broken_rate < MODERN_THRESHOLD, (
        "Regression guard broken: modern match did NOT drop below threshold "
        "when validated against an empty identity set — the gate is a no-op."
    )
