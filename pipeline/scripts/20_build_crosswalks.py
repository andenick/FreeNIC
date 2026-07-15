"""Phase 20: Build variable crosswalk tables for non-MDRM sources.

Maps plain-language variable names from Luck, FDIC SDI, OCC, DFAST, and Pillar 3
to MDRM codes and standardized concept names, enabling cross-source queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


# --- Crosswalk definitions ---
# Format: (source_variable, source_table, mdrm_variable, concept, match_confidence, notes)

LUCK_CROSSWALK = [
    # Balance sheet - assets
    ("assets", "luck_call_reports", "RCFD2170", "total_assets", "exact", "Total assets"),
    ("securities", "luck_call_reports", "RCFD0390", "total_securities", "probable", "Total investment securities"),
    ("ln_tot", "luck_call_reports", "RCFD1400", "total_loans", "exact", "Total loans and leases"),
    ("ln_re", "luck_call_reports", "RCFD1410", "real_estate_loans", "exact", "Loans secured by real estate"),
    ("ln_ci", "luck_call_reports", "RCFD1766", "ci_loans", "exact", "Commercial and industrial loans"),
    ("ln_cons", "luck_call_reports", "RCFDB538", "consumer_loans", "probable", "Loans to individuals"),
    ("ln_agr", "luck_call_reports", "RCFD1590", "ag_loans", "probable", "Loans to agriculture"),
    ("cash", "luck_call_reports", "RCFD0010", "cash_balances", "exact", "Cash and balances due"),
    ("ffsold", "luck_call_reports", "RCFD1350", "fed_funds_sold", "exact", "Federal funds sold"),
    ("fixed_ass", "luck_call_reports", "RCFD2145", "fixed_assets", "exact", "Premises and fixed assets"),
    ("oreo", "luck_call_reports", "RCFD2150", "oreo", "exact", "Other real estate owned"),
    ("llres", "luck_call_reports", "RCFD3123", "loan_loss_reserve", "exact", "Allowance for loan losses"),
    # Balance sheet - liabilities
    ("deposits", "luck_call_reports", "RCFD2200", "total_deposits", "exact", "Total deposits"),
    ("demand_deposits", "luck_call_reports", "RCFD2210", "demand_deposits", "exact", "Demand deposits"),
    ("time_deposits", "luck_call_reports", "RCON2604", "time_deposits", "probable", "Time deposits"),
    ("domestic_dep", "luck_call_reports", "RCON2200", "domestic_deposits", "exact", "Total domestic deposits"),
    ("foreign_dep", "luck_call_reports", "RCFN2200", "foreign_deposits", "probable", "Deposits in foreign offices"),
    ("ffpurch", "luck_call_reports", "RCFD2800", "fed_funds_purchased", "exact", "Fed funds purchased"),
    ("subdebt", "luck_call_reports", "RCFD3200", "subordinated_debt", "exact", "Subordinated notes and debentures"),
    ("liab_tot", "luck_call_reports", "RCFD2948", "total_liabilities", "exact", "Total liabilities"),
    # Equity
    ("equity", "luck_call_reports", "RCFD3210", "total_equity", "exact", "Total equity capital"),
    ("surplus", "luck_call_reports", "RCFD3230", "surplus", "exact", "Surplus (exclude undivided profits)"),
    ("retain_earn", "luck_call_reports", "RCFD3632", "retained_earnings", "exact", "Retained earnings"),
    ("comm_stock", "luck_call_reports", "RCFD3230", "common_stock", "probable", "Common stock"),
    ("pref_stock", "luck_call_reports", "RCFD3838", "preferred_stock", "probable", "Preferred stock"),
    # Income (YTD)
    ("ytdint_inc", "luck_call_reports", "RIAD4107", "interest_income", "exact", "Total interest income"),
    ("ytdint_exp", "luck_call_reports", "RIAD4073", "interest_expense", "exact", "Total interest expense"),
    ("ytdint_inc_net", "luck_call_reports", "RIAD4074", "net_interest_income", "exact", "Net interest income"),
    ("ytdllprov", "luck_call_reports", "RIAD4230", "provision_loan_losses", "exact", "Provision for loan losses"),
    ("ytdnonint_inc", "luck_call_reports", "RIAD4079", "noninterest_income", "exact", "Total noninterest income"),
    ("ytdnonint_exp", "luck_call_reports", "RIAD4093", "noninterest_expense", "exact", "Total noninterest expense"),
    ("ytdnetinc", "luck_call_reports", "RIAD4340", "net_income", "exact", "Net income"),
    # Identifiers
    ("id_fdic_cert", "luck_call_reports", None, "fdic_cert", "metadata", "FDIC certificate number"),
    ("id_occ", "luck_call_reports", None, "occ_charter", "metadata", "OCC charter number"),
    ("state_cd", "luck_call_reports", None, "state_code", "metadata", "State FIPS code"),
]

FDIC_SDI_CROSSWALK = [
    # Balance sheet
    ("ASSET", "fdic_financials", "RCFD2170", "total_assets", "exact", "Total assets"),
    ("LIAB", "fdic_financials", "RCFD2948", "total_liabilities", "exact", "Total liabilities"),
    ("EQ", "fdic_financials", "RCFD3210", "total_equity", "exact", "Total equity capital"),
    ("EQTOT", "fdic_financials", "RCFD3210", "total_equity", "exact", "Total equity capital (alt)"),
    ("DEP", "fdic_financials", "RCFD2200", "total_deposits", "exact", "Total deposits"),
    ("DEPDOM", "fdic_financials", "RCON2200", "domestic_deposits", "exact", "Total domestic deposits"),
    ("CHBAL", "fdic_financials", "RCFD0010", "cash_balances", "exact", "Cash and balances due"),
    ("SC", "fdic_financials", "RCFD0390", "total_securities", "probable", "Total securities"),
    ("LNLSNET", "fdic_financials", "RCFD2122", "net_loans", "exact", "Net loans and leases"),
    # Income
    ("INTINC", "fdic_financials", "RIAD4107", "interest_income", "exact", "Total interest income"),
    ("EINTEXP", "fdic_financials", "RIAD4073", "interest_expense", "exact", "Total interest expense"),
    ("NIM", "fdic_financials", "RIAD4074", "net_interest_income", "exact", "Net interest income"),
    ("NONII", "fdic_financials", "RIAD4079", "noninterest_income", "exact", "Total noninterest income"),
    ("NONIX", "fdic_financials", "RIAD4093", "noninterest_expense", "exact", "Total noninterest expense"),
    ("NETINC", "fdic_financials", "RIAD4340", "net_income", "exact", "Net income"),
    ("PTAXNETINC", "fdic_financials", "RIAD4301", "pretax_net_income", "exact", "Income before taxes"),
    # Ratios
    ("ROA", "fdic_financials", None, "return_on_assets", "derived", "Return on assets (annualized)"),
    ("ROAPTX", "fdic_financials", None, "pretax_roa", "derived", "Pretax return on assets"),
    ("NIMY", "fdic_financials", None, "net_interest_margin", "derived", "Net interest margin"),
    ("ERNASTR", "fdic_financials", None, "earning_asset_ratio", "derived", "Earning assets to total assets"),
    # Off-balance sheet
    ("OFFDOM", "fdic_financials", None, "off_balance_sheet", "probable", "Off-balance sheet items"),
    ("AOA", "fdic_financials", None, "all_other_assets", "probable", "All other assets"),
]

ROBIN_CROSSWALK = [
    # Robin panel variables → MDRM / concepts
    ("assets", "robin_panel", "RCFD2170", "total_assets", "exact", "Total assets"),
    ("deposits", "robin_panel", "RCFD2200", "total_deposits", "exact", "Total deposits"),
    ("loans", "robin_panel", "RCFD1400", "total_loans", "probable", "Total loans"),
    ("equity", "robin_panel", "RCFD3210", "total_equity", "exact", "Total equity capital"),
    ("capital", "robin_panel", None, "capital", "probable", "Capital (pre-Basel definition varies)"),
    ("demand_deposits", "robin_panel", "RCFD2210", "demand_deposits", "exact", "Demand deposits"),
    ("time_deposits", "robin_panel", "RCON2604", "time_deposits", "probable", "Time deposits"),
    ("surplus", "robin_panel", "RCFD3230", "surplus", "exact", "Surplus"),
    ("oreo", "robin_panel", "RCFD2150", "oreo", "exact", "Other real estate owned"),
    ("failed_bank", "robin_panel", None, "failure_indicator", "metadata", "Binary failure flag (0/1)"),
    ("run", "robin_panel", None, "bank_run_indicator", "metadata", "Bank run indicator"),
    ("time_to_fail", "robin_panel", None, "time_to_failure", "metadata", "Years until failure"),
]

# cdr_unrealized_losses fields -> MDRM (FFIEC CDR Public bulk; values in $ thousands).
# HTM fair value is RCFD1771 (RCB), corrected from the V0 plan's RCFDJJ34; brokered
# deposits is RCON2365 (total brokered), corrected from RCONJ473/J474 (time-deposit
# maturity buckets). See 33_parse_cdr_unrealized.py header for the verification vs SVB 10-K.
CDR_CROSSWALK = [
    ("afs_amort_cost", "cdr_unrealized_losses", "RCFD1772", "afs_amortized_cost", "exact", "AFS securities amortized cost (Schedule RCB)"),
    ("afs_fair_value", "cdr_unrealized_losses", "RCFD1773", "afs_fair_value", "exact", "AFS securities fair value (Schedule RCB)"),
    ("htm_amort_cost", "cdr_unrealized_losses", "RCFD1754", "htm_amortized_cost", "exact", "HTM securities amortized cost (Schedule RCB)"),
    ("htm_fair_value", "cdr_unrealized_losses", "RCFD1771", "htm_fair_value", "exact", "HTM securities fair value (Schedule RCB; corrected from RCFDJJ34)"),
    ("aoci", "cdr_unrealized_losses", "RCFDB530", "aoci", "exact", "Accumulated other comprehensive income (Schedule RC)"),
    ("brokered_deposits", "cdr_unrealized_losses", "RCON2365", "brokered_deposits", "exact", "Total brokered deposits (Schedule RCE; corrected from RCONJ473/J474)"),
]

# NOTE: fdic_sdi_features carries no new MDRM rows. Its inputs derive from FDIC SDI
# variables already crosswalked in FDIC_SDI_CROSSWALK above (ASSET, DEP, EQ, etc.);
# its remaining columns (income_ratio, noncore_proxy, uninsured_ratio, insured_ratio,
# securities_ratio, equity_ratio, nim_ratio, roa, log_age, F1/F3/F5_failure) are
# derived ratios / engineered features with no direct single-MDRM counterpart.

DFAST_CROSSWALK = [
    ("common_equity_tier1_capital_ratio_min", "dfast_results", None, "cet1_ratio_stressed", "manual", "CET1 ratio minimum under stress"),
    ("tier1_capital_ratio_min", "dfast_results", None, "tier1_ratio_stressed", "manual", "Tier 1 capital ratio minimum"),
    ("total_capital_ratio_min", "dfast_results", None, "total_capital_ratio_stressed", "manual", "Total capital ratio minimum"),
    ("tier1_leverage_ratio_min", "dfast_results", None, "leverage_ratio_stressed", "manual", "Tier 1 leverage ratio minimum"),
    ("net_income_pretax", "dfast_results", "RIAD4301", "pretax_net_income", "probable", "Pre-tax net income (projected)"),
    ("provision_for_loan_losses", "dfast_results", "RIAD4230", "provision_loan_losses", "probable", "Provision for loan losses (projected)"),
    ("total_loan_losses", "dfast_results", None, "total_loan_losses_stressed", "manual", "Total loan losses under stress"),
]


def main():
    elapsed = timer()
    print("=== Phase 20: Build Variable Crosswalks ===")

    con = get_db()

    # Create the crosswalk table
    con.execute("DROP TABLE IF EXISTS variable_crosswalk")
    con.execute("""
        CREATE TABLE variable_crosswalk (
            source_variable VARCHAR,
            source_table VARCHAR,
            mdrm_variable VARCHAR,
            concept VARCHAR,
            match_confidence VARCHAR,
            notes VARCHAR
        )
    """)

    # Insert all crosswalk entries
    all_entries = LUCK_CROSSWALK + FDIC_SDI_CROSSWALK + ROBIN_CROSSWALK + DFAST_CROSSWALK + CDR_CROSSWALK
    for entry in all_entries:
        con.execute("""
            INSERT INTO variable_crosswalk
            (source_variable, source_table, mdrm_variable, concept, match_confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, entry)

    total = con.execute("SELECT COUNT(*) FROM variable_crosswalk").fetchone()[0]
    by_source = con.execute("""
        SELECT source_table, COUNT(*) as cnt,
               COUNT(mdrm_variable) as with_mdrm
        FROM variable_crosswalk
        GROUP BY source_table
        ORDER BY cnt DESC
    """).fetchall()

    print(f"\n  Total crosswalk entries: {total}")
    print(f"\n  By source:")
    for row in by_source:
        print(f"    {row[0]:<25} {row[1]:>3} entries ({row[2]} with MDRM mapping)")

    # Show concept coverage
    concepts = con.execute("""
        SELECT concept, COUNT(DISTINCT source_table) as sources,
               GROUP_CONCAT(DISTINCT source_table ORDER BY source_table) as tables
        FROM variable_crosswalk
        WHERE concept NOT IN ('fdic_cert', 'occ_charter', 'state_code')
        GROUP BY concept
        HAVING COUNT(DISTINCT source_table) >= 2
        ORDER BY sources DESC, concept
    """).fetchall()

    print(f"\n  Cross-source concepts (mapped in 2+ sources):")
    for row in concepts:
        print(f"    {row[0]:<30} {row[1]} sources: {row[2]}")

    con.close()

    secs = elapsed()
    log_ingestion("20", f"Variable crosswalks: {total} entries across {len(by_source)} sources. {secs:.1f}s")
    print(f"\nPhase 20 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
