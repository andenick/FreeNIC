"""UBPR peer-layer tests (A5, Definitive Build, added 2026-06-09).

ubpr_peer_stats = official FFIEC UBPR Stats (peer-group percentile benchmarks). Grain must be unique
(reporting_period x peer_group x ubpr_code); reporting_period non-null; quarter-end dates only.
(ubpr_peer_rank — per-bank percentiles — is a separate deferred table; its tests are added when it lands.)
"""


def test_ubpr_peer_stats_grain_unique(db):
    tot = db.execute("SELECT COUNT(*) FROM ubpr_peer_stats").fetchone()[0]
    dist = db.execute(
        "SELECT COUNT(*) FROM (SELECT 1 FROM ubpr_peer_stats "
        "GROUP BY reporting_period, peer_group, ubpr_code)").fetchone()[0]
    assert tot == dist, f"ubpr_peer_stats: {tot - dist} duplicate (period,peer_group,code) keys"


def test_ubpr_peer_stats_no_null_period(db):
    nulls = db.execute(
        "SELECT COUNT(*) - COUNT(reporting_period) FROM ubpr_peer_stats").fetchone()[0]
    assert nulls == 0, f"ubpr_peer_stats has {nulls} null reporting_period"


def test_ubpr_peer_rank_grain_unique_recent(db):
    """ubpr_peer_rank grain (period,rssd,peer_group,code) unique — bounded to the latest period
    (full 250M-row GROUP BY is too slow for the routine suite; a per-period check catches dups)."""
    mx = db.execute("SELECT MAX(reporting_period) FROM ubpr_peer_rank").fetchone()[0]
    dups = db.execute("""
        SELECT COUNT(*) FROM (
            SELECT reporting_period, rssd_id, peer_group, ubpr_code FROM ubpr_peer_rank
            WHERE reporting_period = ? GROUP BY 1,2,3,4 HAVING COUNT(*) > 1)
    """, [mx]).fetchone()[0]
    assert dups == 0, f"ubpr_peer_rank: {dups} duplicate grain keys at {mx}"


def test_ubpr_peer_rank_values_are_percentiles(db):
    """Rank values are percentiles in [0,100] (bounded sample)."""
    bad = db.execute("""
        SELECT COUNT(*) FROM (SELECT value FROM ubpr_peer_rank
            WHERE reporting_period = (SELECT MAX(reporting_period) FROM ubpr_peer_rank) LIMIT 500000)
        WHERE value < 0 OR value > 100
    """).fetchone()[0]
    assert bad == 0, f"ubpr_peer_rank has {bad} out-of-range percentile values in the sample"


def test_ubpr_peer_stats_quarter_ends(db):
    """All reporting_period values are quarter-end dates."""
    bad = db.execute("""
        SELECT COUNT(*) FROM (SELECT DISTINCT reporting_period FROM ubpr_peer_stats)
        WHERE (month(reporting_period), day(reporting_period))
              NOT IN ((3,31),(6,30),(9,30),(12,31))
    """).fetchone()[0]
    assert bad == 0, f"ubpr_peer_stats has {bad} non-quarter-end reporting_period values"
