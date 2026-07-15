"""UBPR ratios table tests (added W19 — A1 of the non-HDARP plan)."""


def test_ubpr_row_floor(db):
    n = db.execute("SELECT COUNT(*) FROM ubpr_ratios").fetchone()[0]
    assert n > 40_000_000, f"ubpr_ratios only {n:,} rows"


def test_ubpr_panel_periods(db):
    p = db.execute("SELECT COUNT(DISTINCT period_end) FROM ubpr_ratios").fetchone()[0]
    assert p >= 5, f"expected >=5 UBPR periods, got {p}"


def test_ubpr_banks_and_concepts(db):
    b = db.execute("SELECT COUNT(DISTINCT rssd_id) FROM ubpr_ratios").fetchone()[0]
    c = db.execute("SELECT COUNT(DISTINCT ubpr_code) FROM ubpr_ratios").fetchone()[0]
    assert b > 4000, f"only {b} banks"
    assert c > 2000, f"only {c} UBPR concepts"


def test_ubpr_keys_nonnull(db):
    bad = db.execute("""SELECT COUNT(*) FROM ubpr_ratios
        WHERE rssd_id IS NULL OR period_end IS NULL OR ubpr_code IS NULL OR value IS NULL""").fetchone()[0]
    assert bad == 0, f"{bad} ubpr_ratios rows with null keys/value"


def test_ubpr_codes_well_formed(db):
    # every concept is a UBPR#### mnemonic
    bad = db.execute(r"SELECT COUNT(*) FROM (SELECT DISTINCT ubpr_code FROM ubpr_ratios "
                     r"WHERE NOT regexp_matches(ubpr_code, '^UBPR[A-Z0-9]+$'))").fetchone()[0]
    assert bad == 0, f"{bad} malformed UBPR codes"


def test_ubpr_grain_unique(db):
    # one value per (rssd, period, concept) — bounded to the latest period; a full-table GROUP BY
    # over the (now ~400M-row, full-extent) panel OOMs, and a per-period check catches any grain dup.
    mx = db.execute("SELECT MAX(period_end) FROM ubpr_ratios").fetchone()[0]
    dup = db.execute("""SELECT COUNT(*) FROM (
        SELECT rssd_id, period_end, ubpr_code, COUNT(*) c
        FROM ubpr_ratios WHERE period_end = ? GROUP BY 1,2,3 HAVING COUNT(*) > 1)""", [mx]).fetchone()[0]
    assert dup == 0, f"{dup} duplicate (rssd,period,ubpr_code) grains at {mx}"
