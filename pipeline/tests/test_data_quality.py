"""Data-quality / anomaly invariants (Step 9, added 2026-06-06). Fast subset of dq_audit.py
(the full audit lives in coverage_analysis/dq_audit.py). Guards sign/range/units sanity.

Documented non-failures (NOT asserted here; they're plausible tails / pre-existing):
  - call_report_filings: 53 negative total-assets cells (tiny tail; see dq_audit.json).
  - fdic_sdi_features: 223 |ROA|>50 rows (near-zero-asset banks -> extreme % ; plausible).
  - units verified consistent: JPM (rssd 852218) 2023Q4 assets match call_report == FDIC ($3.395T thousands).
"""


def test_ncua_value_sane(db):
    """No absurd NCUA values (the ACCT_PG0001 page-code class was removed 2026-06-06).
    Real CU financials are well under 1e13."""
    mx = db.execute("SELECT MAX(abs(value)) FROM ncua_5300").fetchone()[0]
    assert mx is not None and mx < 1e13, f"ncua_5300 max|value| {mx:.3e} >= 1e13 (non-financial column leaked?)"


def test_fdic_sdi_features_sane(db):
    neg, eq_oob, flag_bad = db.execute("""
        SELECT COUNT(*) FILTER (WHERE assets < 0),
               COUNT(*) FILTER (WHERE equity_ratio > 1.0 OR equity_ratio < -0.5),
               COUNT(*) FILTER (WHERE F1_failure NOT IN (0,1) OR F3_failure NOT IN (0,1) OR F5_failure NOT IN (0,1))
        FROM fdic_sdi_features
    """).fetchone()
    assert neg == 0, f"{neg} negative-asset rows in fdic_sdi_features"
    assert eq_oob == 0, f"{eq_oob} equity_ratio out-of-band rows"
    assert flag_bad == 0, f"{flag_bad} non-binary failure-flag rows"


def test_hmda_nonnegative(db):
    # loan_count and activity_year are STRICT invariants (must never be negative /
    # out of range). loan_amount_000s is the CFPB-reported dollar `sum`, which the
    # CFPB Data Browser API itself returns NEGATIVE for a tiny number of filer-years
    # (e.g. HarborOne Mortgage 2018, TJC Mortgage 2019 — refinancing) — a documented
    # CFPB SOURCE anomaly we transcribe faithfully (we do not alter source values).
    # Bound it to a tolerance so the panel can grow without re-breaking, but flag any
    # systematic regression.
    bad_strict = db.execute("""
        SELECT COUNT(*) FROM hmda_summary
        WHERE loan_count < 0 OR activity_year NOT BETWEEN 2018 AND 2026
    """).fetchone()[0]
    assert bad_strict == 0, f"{bad_strict} hmda_summary rows with negative counts or out-of-range year"
    neg_amt = db.execute(
        "SELECT COUNT(*) FROM hmda_summary WHERE loan_amount_000s < 0").fetchone()[0]
    assert neg_amt <= 10, (
        f"{neg_amt} hmda_summary rows with negative loan_amount_000s — exceeds the "
        f"documented CFPB-source-anomaly tolerance (<=10); investigate for a parse regression")
