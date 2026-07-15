"""Cross-source value reconciliation (Step 8, added 2026-06-07).

Independent bank-level sources must agree on total assets. Full-history reconciliation
(coverage_analysis/step8_reconcile.json): call_report (RCFD/RCON2170) vs FDIC SDI (ASSET) =
**99.875%** within 0.1% across 1,487,666 bank-quarters, 0 sign flips. The routine test below is
bounded to 2024Q4 for speed.

Note (documented, NOT a failure): bhcf (BHCK2170) is HOLDING-COMPANY consolidated and keyed by the
HC rssd, so it does NOT reconcile to bank-level call_report/FDIC (only 55 same-rssd overlaps, ~35-45%
median diff) — different entity scope by design, not a data error.
"""


def test_call_report_vs_fdic_assets_reconcile_2024q4(db):
    """Bank total assets agree across call_report and FDIC SDI for 2024Q4 (>=99% within 0.1%)."""
    both, ok = db.execute("""
        WITH cr AS (
            SELECT rssd_id, COALESCE(
                       MAX(CASE WHEN variable_id='RCFD2170' THEN value END),
                       MAX(CASE WHEN variable_id='RCON2170' THEN value END)) a
            FROM call_report_filings
            WHERE period_end = DATE '2024-12-31' AND variable_id IN ('RCFD2170','RCON2170')
            GROUP BY rssd_id),
        fd AS (
            SELECT rssd_id, MAX(value) a FROM fdic_financials
            WHERE period_end = DATE '2024-12-31' AND variable_id='ASSET' GROUP BY rssd_id)
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE abs(cr.a - fd.a) <= GREATEST(1.0, 0.001*abs(fd.a)))
        FROM cr JOIN fd USING (rssd_id)
        WHERE cr.a IS NOT NULL AND fd.a IS NOT NULL
    """).fetchone()
    assert both > 1000, f"too few overlapping banks in 2024Q4 ({both})"
    rate = ok / both
    assert rate >= 0.99, f"call_report vs FDIC total-assets agreement {rate:.2%} < 99% (2024Q4)"


def test_call_report_vs_fdic_deposits_reconcile_2024q4(db):
    """Bank total deposits agree across call_report and FDIC SDI for 2024Q4 (>=99% within 0.1%)."""
    both, ok = db.execute("""
        WITH cr AS (
            SELECT rssd_id, COALESCE(
                       MAX(CASE WHEN variable_id='RCFD2200' THEN value END),
                       MAX(CASE WHEN variable_id='RCON2200' THEN value END)) a
            FROM call_report_filings
            WHERE period_end = DATE '2024-12-31' AND variable_id IN ('RCFD2200','RCON2200')
            GROUP BY rssd_id),
        fd AS (
            SELECT rssd_id, MAX(value) a FROM fdic_financials
            WHERE period_end = DATE '2024-12-31' AND variable_id='DEP' GROUP BY rssd_id)
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE abs(cr.a - fd.a) <= GREATEST(1.0, 0.001*abs(fd.a)))
        FROM cr JOIN fd USING (rssd_id)
        WHERE cr.a IS NOT NULL AND fd.a IS NOT NULL
    """).fetchone()
    assert both > 1000, f"too few overlapping banks in 2024Q4 ({both})"
    rate = ok / both
    assert rate >= 0.99, f"call_report vs FDIC total-deposits agreement {rate:.2%} < 99% (2024Q4)"


def test_reconciliation_report_headline_thresholds():
    """The published RECONCILIATION.md/.json headline agreements must hold (regression guard
    on the public trust report). Regenerate with coverage_analysis/reconcile_all.py."""
    import json
    from pathlib import Path
    rj = Path(__file__).parent.parent.parent / "coverage_analysis" / "reconciliation.json"
    assert rj.is_file(), f"missing {rj} — run reconcile_all.py"
    r = json.loads(rj.read_text())
    assert r["assets_call_vs_fdic"]["agree_pct"] >= 99.0, "assets agreement regressed"
    assert r["assets_call_vs_fdic"]["sign_flips"] == 0, "asset sign flips appeared"
    assert r["deposits_call_vs_fdic"]["agree_pct"] >= 99.0, "deposits agreement regressed"
    assert r["domestic_deposits_sod_vs_fdic"]["agree_pct"] >= 97.0, "SOD↔SDI domestic deposits regressed"
    assert r["luck_vs_feddirect"]["core_pct"] >= 99.0, "Luck core reconciliation regressed"


# ---------------------------------------------------------------------------
# Dictionary-driven reconciliation suite (added W2.6, dictionary v10.0).
#
# These wire CONFIRMED CRITICAL/HIGH identities from dict.relationships into bulk-SQL
# regression tests, per BANK_DICTIONARY_QA_FINDINGS.md §4-5. Each test pivots one recent
# quarter wide and evaluates one identity on the **all-reported subset** (every component
# NOT NULL) with the project tolerance GREATEST(1.0, 0.001*ABS(rhs)) — so documented
# upstream sparsity (DATA_GAP) does not trip the gate while a genuine ingestion drop or a
# definitional break does. Pass-rate floor is the documented empirical rate minus a small
# margin (>= 0.97 where the registry confirms ~1.0).
#
# Quarters: Call Report + Call↔FDIC concordances on 2024-12-31 (the documented window
# shared with the two pre-existing tests above); FR Y-9C / BHCF identities on 2025-09-30
# (the latest fully-populated Y-9C quarter).
# ---------------------------------------------------------------------------

CALL_Q = "2024-12-31"   # documented Call-Report reconciliation window
Y9C_Q = "2025-09-30"    # latest fully-populated FR Y-9C quarter
_TOL = "GREATEST(1.0, 0.001*ABS({rhs}))"


def _rate_call(db, period, codes, rhs, lhs_expr, rhs_expr, min_n=500):
    """Pivot call_report_filings for `codes` at `period`, then compute the agree-rate of
    lhs_expr vs rhs_expr on the all-reported subset (every pivoted code NOT NULL).
    `rhs` is the column name used inside the tolerance. Returns (testable, rate)."""
    pivots = ",\n".join(
        f"MAX(value) FILTER (WHERE variable_id='{c}') AS {c.lower()}" for c in codes
    )
    notnull = " AND ".join(f"{c.lower()} IS NOT NULL" for c in codes)
    tol = _TOL.format(rhs=rhs)
    testable, agree = db.execute(f"""
        WITH piv AS (
          SELECT rssd_id,
                 {pivots}
          FROM call_report_filings
          WHERE period_end = DATE '{period}'
            AND variable_id IN ({", ".join(f"'{c}'" for c in codes)})
          GROUP BY rssd_id),
        sub AS (SELECT * FROM piv WHERE {notnull})
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE ABS(({lhs_expr}) - ({rhs_expr})) <= {tol})
        FROM sub
    """).fetchone()
    assert testable >= min_n, f"too few all-reported banks ({testable}) for {codes} @ {period}"
    return testable, agree / testable


def _rate_bhcf(db, period, codes, rhs, lhs_expr, rhs_expr, min_n=500):
    """FR Y-9C analogue of _rate_call against bhcf_filings."""
    pivots = ",\n".join(
        f"MAX(value) FILTER (WHERE variable_id='{c}') AS {c.lower()}" for c in codes
    )
    notnull = " AND ".join(f"{c.lower()} IS NOT NULL" for c in codes)
    tol = _TOL.format(rhs=rhs)
    testable, agree = db.execute(f"""
        WITH piv AS (
          SELECT rssd_id,
                 {pivots}
          FROM bhcf_filings
          WHERE period_end = DATE '{period}'
            AND variable_id IN ({", ".join(f"'{c}'" for c in codes)})
          GROUP BY rssd_id),
        sub AS (SELECT * FROM piv WHERE {notnull})
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE ABS(({lhs_expr}) - ({rhs_expr})) <= {tol})
        FROM sub
    """).fetchone()
    assert testable >= min_n, f"too few all-reported HCs ({testable}) for {codes} @ {period}"
    return testable, agree / testable


# --- Call Report balance-sheet & income identities -------------------------

def test_call_total_liabilities_plus_equity_identity(db):
    """REL_3838 (CRITICAL, 1.0000): total liabilities+equity RCON3300 = total assets RCON2170."""
    n, rate = _rate_call(db, CALL_Q, ["RCON3300", "RCON2170"], "rcon2170",
                         "rcon3300", "rcon2170")
    assert rate >= 0.99, f"RCON3300=RCON2170 (bal-sheet identity) {rate:.4f} < 0.99 ({n} banks)"


def test_call_total_deposits_decomposition(db):
    """REL_7300 (1.0000): total deposits RCON2200 = noninterest RCON6631 + interest RCON6636."""
    n, rate = _rate_call(db, CALL_Q, ["RCON2200", "RCON6631", "RCON6636"], "rcon2200",
                         "rcon6631 + rcon6636", "rcon2200")
    assert rate >= 0.99, f"RCON2200=RCON6631+RCON6636 (deposits) {rate:.4f} < 0.99 ({n} banks)"


def test_call_total_equity_capital_buildup(db):
    """REL_7305 (0.9999): total bank equity RCON3210 = sum of its 6 components."""
    codes = ["RCON3210", "RCON3230", "RCON3632", "RCON3838", "RCON3839", "RCONA130", "RCONB530"]
    n, rate = _rate_call(db, CALL_Q, codes, "rcon3210",
                         "rcon3230 + rcon3632 + rcon3838 + rcon3839 + rcona130 + rconb530",
                         "rcon3210")
    assert rate >= 0.98, f"RCON3210 equity build-up {rate:.4f} < 0.98 ({n} banks)"


def test_call_net_interest_income_identity(db):
    """REL_7281 (0.9999, NII): net interest income RIAD4074 = -interest expense RIAD4073
    + interest income RIAD4107."""
    n, rate = _rate_call(db, CALL_Q, ["RIAD4074", "RIAD4073", "RIAD4107"], "riad4074",
                         "-riad4073 + riad4107", "riad4074")
    assert rate >= 0.99, f"RIAD4074=-RIAD4073+RIAD4107 (NII) {rate:.4f} < 0.99 ({n} banks)"


def test_call_total_interest_income_buildup(db):
    """REL_7277 (0.9968): total interest income RIAD4107 = sum of its 9 components."""
    codes = ["RIAD4107", "RIAD4010", "RIAD4020", "RIAD4060", "RIAD4065",
             "RIAD4069", "RIAD4115", "RIAD4518", "RIADB488", "RIADB489"]
    n, rate = _rate_call(db, CALL_Q, codes, "riad4107",
                         "riad4010 + riad4020 + riad4060 + riad4065 + riad4069 "
                         "+ riad4115 + riad4518 + riadb488 + riadb489", "riad4107", min_n=50)
    assert rate >= 0.97, f"RIAD4107 interest-income build-up {rate:.4f} < 0.97 ({n} banks)"


def test_call_net_loans_allowance_identity(db):
    """REL_7297 (1.0000, loans-net): net loans RCONB529 = -allowance RCON3123 + loans RCONB528."""
    n, rate = _rate_call(db, CALL_Q, ["RCONB529", "RCON3123", "RCONB528"], "rconb529",
                         "-rcon3123 + rconb528", "rconb529")
    assert rate >= 0.99, f"RCONB529=-RCON3123+RCONB528 (net loans) {rate:.4f} < 0.99 ({n} banks)"


def test_call_total_loans_decomposition(db):
    """REL_7342 (allcomp 1.0000): total loans RCON2122 = Σ loan categories − unearned income.
    Tested on the all-reported subset so DATA_GAP sparsity does not false-fail."""
    codes = ["RCON2122", "RCON1288", "RCON1420", "RCON1460", "RCON1590", "RCON1766",
             "RCON1797", "RCON2107", "RCON2123", "RCON2165", "RCON5367", "RCON5368",
             "RCONB538", "RCONB539", "RCONF158", "RCONF159", "RCONF160", "RCONF161",
             "RCONJ454", "RCONJ464", "RCONK137", "RCONK207"]
    rhs = ("rcon1288 + rcon1420 + rcon1460 + rcon1590 + rcon1766 + rcon1797 + rcon2107 "
           "- rcon2123 + rcon2165 + rcon5367 + rcon5368 + rconb538 + rconb539 + rconf158 "
           "+ rconf159 + rconf160 + rconf161 + rconj454 + rconj464 + rconk137 + rconk207")
    n, rate = _rate_call(db, CALL_Q, codes, "rcon2122", rhs, "rcon2122", min_n=50)
    assert rate >= 0.97, f"RCON2122 loan decomposition (all-reported) {rate:.4f} < 0.97 ({n} banks)"


def test_call_critical_rcc_k_decomposition(db):
    """REL_4792 (CRITICAL, allcomp 1.0000): RCONK163 + RCONK164 = RCONK256."""
    n, rate = _rate_call(db, CALL_Q, ["RCONK163", "RCONK164", "RCONK256"], "rconk256",
                         "rconk163 + rconk164", "rconk256", min_n=50)
    assert rate >= 0.99, f"RCONK163+K164=K256 (CRITICAL) {rate:.4f} < 0.99 ({n} banks)"


def test_call_noninterest_income_buildup(db):
    """REL_7282 (allcomp 1.0000): noninterest income RIAD4079 = Σ15 components (all-reported)."""
    codes = ["RIAD4079", "RIAD4070", "RIAD4080", "RIAD5415", "RIAD5416", "RIADA220",
             "RIADB491", "RIADB492", "RIADB493", "RIADB496", "RIADB497", "RIADC386",
             "RIADC387", "RIADC886", "RIADC887", "RIADC888"]
    rhs = ("riad4070 + riad4080 + riad5415 + riad5416 + riada220 + riadb491 + riadb492 "
           "+ riadb493 + riadb496 + riadb497 + riadc386 + riadc387 + riadc886 + riadc887 "
           "+ riadc888")
    n, rate = _rate_call(db, CALL_Q, codes, "riad4079", rhs, "riad4079", min_n=50)
    assert rate >= 0.97, f"RIAD4079 noninterest-income build-up {rate:.4f} < 0.97 ({n} banks)"


# --- Call↔FDIC concordances (3 of the 16 confirmed mappings) ---------------

def _concordance_rate(db, period, call_expr, call_codes, fdic_var, min_n=1000):
    """Pivot call to one value via call_expr over call_codes, MAX the FDIC variable, and
    agree within GREATEST(1.0, 0.001*ABS(fdic)). Mirrors the two pre-existing tests."""
    both, ok = db.execute(f"""
        WITH cr AS (
            SELECT rssd_id, {call_expr} AS a
            FROM call_report_filings
            WHERE period_end = DATE '{period}' AND variable_id IN ({", ".join(f"'{c}'" for c in call_codes)})
            GROUP BY rssd_id),
        fd AS (
            SELECT rssd_id, MAX(value) a FROM fdic_financials
            WHERE period_end = DATE '{period}' AND variable_id='{fdic_var}' GROUP BY rssd_id)
        SELECT COUNT(*),
               COUNT(*) FILTER (WHERE abs(cr.a - fd.a) <= GREATEST(1.0, 0.001*abs(fd.a)))
        FROM cr JOIN fd USING (rssd_id)
        WHERE cr.a IS NOT NULL AND fd.a IS NOT NULL
    """).fetchone()
    assert both >= min_n, f"too few overlapping banks ({both}) for FDIC:{fdic_var} @ {period}"
    return both, ok / both


def test_concordance_fdic_eq_vs_call_3210(db):
    """REL_7511 (corrected mapping, 0.9972): FDIC EQ = COALESCE(RCFD3210, RCON3210)
    (total bank equity capital, NOT G105 which includes minority interest)."""
    n, rate = _concordance_rate(
        db, CALL_Q, "COALESCE(MAX(CASE WHEN variable_id='RCFD3210' THEN value END), "
                    "MAX(CASE WHEN variable_id='RCON3210' THEN value END))",
        ["RCFD3210", "RCON3210"], "EQ")
    assert rate >= 0.99, f"EQ↔COALESCE(RCFD3210,RCON3210) {rate:.4f} < 0.99 ({n} banks)"


def test_concordance_fdic_lnlsnet_vs_call_2122_minus_3123(db):
    """REL_7515 (corrected mapping, 0.9989): FDIC LNLSNET = COALESCE(RCFD2122,RCON2122) −
    COALESCE(RCFD3123,RCON3123,0) (net loans & leases, NOT the single B529 line)."""
    call_expr = (
        "COALESCE(MAX(CASE WHEN variable_id='RCFD2122' THEN value END), "
        "MAX(CASE WHEN variable_id='RCON2122' THEN value END)) "
        "- COALESCE(MAX(CASE WHEN variable_id='RCFD3123' THEN value END), "
        "MAX(CASE WHEN variable_id='RCON3123' THEN value END), 0)")
    n, rate = _concordance_rate(
        db, CALL_Q, call_expr, ["RCFD2122", "RCON2122", "RCFD3123", "RCON3123"], "LNLSNET")
    assert rate >= 0.99, f"LNLSNET↔RCFD/RCON2122−3123 {rate:.4f} < 0.99 ({n} banks)"


def test_concordance_fdic_asset_vs_call_2170(db):
    """REL_7509 (0.9984): FDIC ASSET = COALESCE(RCFD2170, RCON2170)."""
    n, rate = _concordance_rate(
        db, CALL_Q, "COALESCE(MAX(CASE WHEN variable_id='RCFD2170' THEN value END), "
                    "MAX(CASE WHEN variable_id='RCON2170' THEN value END))",
        ["RCFD2170", "RCON2170"], "ASSET")
    assert rate >= 0.99, f"ASSET↔COALESCE(RCFD2170,RCON2170) {rate:.4f} < 0.99 ({n} banks)"


# --- FR Y-9C (holding-company) identities ----------------------------------

def test_y9c_balance_sheet_identity(db):
    """REL_0066 (CRITICAL, 1.0000): BHC total liabilities+equity BHCK3300 = total assets BHCK2170.

    The modern FR Y-9C filer population is small (~380 holding companies per quarter),
    so the all-reported subset is order-hundreds, not thousands."""
    n, rate = _rate_bhcf(db, Y9C_Q, ["BHCK3300", "BHCK2170"], "bhck2170",
                         "bhck3300", "bhck2170", min_n=300)
    assert rate >= 0.99, f"BHCK3300=BHCK2170 (HC bal-sheet identity) {rate:.4f} < 0.99 ({n} HCs)"


def test_y9c_hcg_other_liabilities_tie(db):
    """REL_0061 (CRITICAL, 1.0000): the HC↔HC-G tie BHCK2750 = BHCT2750
    (HC.20 Other liabilities = HC-G.5 total)."""
    n, rate = _rate_bhcf(db, Y9C_Q, ["BHCK2750", "BHCT2750"], "bhct2750",
                         "bhck2750", "bhct2750", min_n=100)
    assert rate >= 0.99, f"BHCK2750=BHCT2750 (HC-G tie) {rate:.4f} < 0.99 ({n} HCs)"


def test_y9c_net_interest_income_identity(db):
    """REL_0011 (CRITICAL, 1.0000): BHC net interest income BHCK4074 =
    interest income BHCK4107 − interest expense BHCK4073."""
    n, rate = _rate_bhcf(db, Y9C_Q, ["BHCK4074", "BHCK4107", "BHCK4073"], "bhck4074",
                         "bhck4107 - bhck4073", "bhck4074", min_n=300)
    assert rate >= 0.99, f"BHCK4107-BHCK4073=BHCK4074 (HC NII) {rate:.4f} < 0.99 ({n} HCs)"
