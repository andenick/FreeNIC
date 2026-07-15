"""FR Y-15 systemic-risk indicators tests (added W19 — B2 of the non-HDARP plan)."""


def test_y15_row_floor(db):
    n = db.execute("SELECT COUNT(*) FROM y15_systemic_indicators").fetchone()[0]
    assert n > 15_000, f"y15_systemic_indicators only {n:,} rows"


def test_y15_years_and_institutions(db):
    y = db.execute("SELECT COUNT(DISTINCT period_end) FROM y15_systemic_indicators").fetchone()[0]
    b = db.execute("SELECT COUNT(DISTINCT rssd_id) FROM y15_systemic_indicators").fetchone()[0]
    assert y >= 5, f"expected >=5 Y-15 years, got {y}"
    assert b > 30, f"expected >30 G-SIB filers, got {b}"


def test_y15_keys_nonnull(db):
    bad = db.execute("""SELECT COUNT(*) FROM y15_systemic_indicators
        WHERE rssd_id IS NULL OR period_end IS NULL OR risk_code IS NULL OR value IS NULL""").fetchone()[0]
    assert bad == 0, f"{bad} y15 rows with null keys/value"


def test_y15_codes_well_formed(db):
    bad = db.execute(r"SELECT COUNT(*) FROM (SELECT DISTINCT risk_code FROM y15_systemic_indicators "
                     r"WHERE NOT regexp_matches(risk_code, '^RISK[A-Z0-9]+$'))").fetchone()[0]
    assert bad == 0, f"{bad} malformed RISK codes"


def test_y15_grain_unique(db):
    dup = db.execute("""SELECT COUNT(*) FROM (
        SELECT rssd_id, period_end, risk_code, COUNT(*) c
        FROM y15_systemic_indicators GROUP BY 1,2,3 HAVING COUNT(*) > 1)""").fetchone()[0]
    assert dup == 0, f"{dup} duplicate (rssd,period,risk_code) grains"


def test_y15_gsibs_present(db):
    # JPMorgan (1039502) should be a Y-15 filer
    n = db.execute("SELECT COUNT(*) FROM y15_systemic_indicators WHERE rssd_id = 1039502").fetchone()[0]
    assert n > 0, "JPMorgan (1039502) missing from Y-15"
