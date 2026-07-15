"""Phase 13: Validate database integrity and data quality.

Checks:
1. Referential integrity (filing entity IDs in institutions table)
2. Date range validity
3. No duplicate primary keys
4. Cross-source validation (BHCF vs Luck for common variables)
5. Spot-check known values (e.g., JPMorgan total assets)
6. Catalog completeness
7. Summary statistics report
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


# --- Referential check #1 calibration (era-stratified, coverage-aware) ---
#
# Rationale (see COVERAGE_GAPS.md S6): the OLD flat 90%-vs-`institutions` gate was
# mis-calibrated for tables
# spanning 1976-2025. `institutions` (217,210 rssds) under-covers historical
# defunct/merged entities, so matching filing rssds only against it produced a
# misleadingly low 34-40% rate -- and 3 permanent xfails -- even though those
# entities ARE known to NIC via `transformations` etc. We now validate against
# `entity_xref` (the de-duped union of all public identity tables, built by
# 20b_build_entity_xref.py) and stratify by era.
#
# HONEST GUARD: this is NOT a relaxation. The gate is the MODERN slice (entities
# whose latest activity is >= 2000), which MUST match entity_xref at >= the
# threshold below. A real regression -- a key-type/join break, or modern entities
# going unmatched -- still drops the modern rate below threshold and FAILS. Only
# the genuinely-unrecoverable pre-2000 residual is classified EXPECTED (reported,
# not failed); its size is itself reported so a blowup there is visible.
MODERN_ERA_THRESHOLD = 90.0   # modern (>=2000) match vs entity_xref must clear this
                              # (Q4 2026-06-08: tightened 85->90; audited min modern = 96.54% call_report)
OVERALL_FLOOR = 85.0          # overall match vs entity_xref sanity floor (Q4: tightened 80->85; min 95.59%)
# Tables validated against entity_xref with an activity-era column.
ERA_REF_CHECKS = [
    ("call_report_filings", "rssd_id", "EXTRACT(year FROM period_end)"),
    ("luck_call_reports", "entity_id", "EXTRACT(year FROM period_end)"),
    ("fdic_financials", "rssd_id", "EXTRACT(year FROM period_end)"),
    ("fdic_sod", "rssd_id", "year"),
    ("bhcf_filings", "rssd_id", "EXTRACT(year FROM period_end)"),
]
# Small modern-only tables: a flat entity_xref gate is appropriate (no historical tail).
# (Q4 2026-06-08: added ubpr_ratios + y15_systemic_indicators — audited 100% / 89.47%.)
FLAT_REF_CHECKS = [
    ("dfast_results", "rssd_id", 85.0),
    ("pillar3_disclosures", "rssd_id", 70.0),
    ("ubpr_ratios", "rssd_id", 95.0),
    ("ubpr_peer_rank", "rssd_id", 90.0),
    ("y15_systemic_indicators", "rssd_id", 85.0),
]


def check_referential_integrity(con):
    """Era-stratified, coverage-aware referential check against entity_xref.

    Validates filing entity ids against `entity_xref` (the full public identity
    universe), not just `institutions`. PASS requires the MODERN slice (latest
    activity >= 2000) to match >= MODERN_ERA_THRESHOLD AND overall >= OVERALL_FLOOR.
    The pre-2000 slice is reported and classified EXPECTED (historical orphans
    inherent to NIC coverage), not FAIL. Still a genuine regression guard: a
    join/key break or modern entities going missing drops the modern rate and FAILS.
    """
    print("\n  1. Referential Integrity (era-stratified vs entity_xref)")

    # Guard: entity_xref must exist and be populated (20b must have run).
    xref_n = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='entity_xref'"
    ).fetchone()[0]
    if xref_n == 0:
        print("    entity_xref MISSING -- run 20b_build_entity_xref.py [FAIL]")
        return False
    xref_rows = con.execute("SELECT COUNT(*) FROM entity_xref").fetchone()[0]
    if xref_rows < 200_000:
        print(f"    entity_xref only {xref_rows:,} rows (expected >200k) [FAIL]")
        return False

    all_pass = True

    for table, col, era_expr in ERA_REF_CHECKS:
        # Per-entity latest activity year -> era; match vs institutions & entity_xref.
        rows = con.execute(f"""
            WITH ent AS (
                SELECT {col} AS rssd, MAX({era_expr}) AS yr
                FROM {table} GROUP BY {col}
            ), tagged AS (
                SELECT rssd, CASE WHEN yr >= 2000 THEN 'modern' ELSE 'historical' END AS era
                FROM ent
            )
            SELECT t.era,
                   COUNT(*) AS n,
                   SUM(CASE WHEN i.rssd_id IS NOT NULL THEN 1 ELSE 0 END) AS m_inst,
                   SUM(CASE WHEN x.rssd_id IS NOT NULL THEN 1 ELSE 0 END) AS m_xref
            FROM tagged t
            LEFT JOIN institutions i ON t.rssd = i.rssd_id
            LEFT JOIN entity_xref x  ON t.rssd = x.rssd_id
            GROUP BY t.era
        """).fetchall()

        stats = {era: (n, mi, mx) for era, n, mi, mx in rows}
        mod_n, _, mod_x = stats.get("modern", (0, 0, 0))
        his_n, _, his_x = stats.get("historical", (0, 0, 0))
        tot_n = mod_n + his_n
        tot_x = mod_x + his_x

        mod_pct = (mod_x / mod_n * 100) if mod_n else 100.0
        his_pct = (his_x / his_n * 100) if his_n else 100.0
        tot_pct = (tot_x / tot_n * 100) if tot_n else 100.0

        # PASS rule: modern slice clears threshold AND overall clears floor.
        ok = (mod_pct >= MODERN_ERA_THRESHOLD) and (tot_pct >= OVERALL_FLOOR)
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"    {table}.{col}: overall {tot_pct:.1f}% (n={tot_n:,}) | "
              f"modern>=2000 {mod_pct:.1f}% (n={mod_n:,}) | "
              f"pre-2000 {his_pct:.1f}% [EXPECTED historical] [{status}]")

    # Flat modern-only tables.
    for table, col, thresh in FLAT_REF_CHECKS:
        total = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM {table}").fetchone()[0]
        matched = con.execute(f"""
            SELECT COUNT(DISTINCT f.{col}) FROM {table} f
            JOIN entity_xref x ON f.{col} = x.rssd_id
        """).fetchone()[0]
        pct = (matched / total * 100) if total else 100.0
        status = "PASS" if pct >= thresh else "FAIL"
        if pct < thresh:
            all_pass = False
        print(f"    {table}.{col}: {matched:,}/{total:,} matched ({pct:.1f}%) "
              f"[>= {thresh:.0f}%] [{status}]")

    return all_pass


def check_date_ranges(con):
    """Verify date ranges are sensible."""
    print("\n  2. Date Range Validity")

    checks = [
        ("bhcf_filings", "period_end", "1980-01-01", "2026-06-30"),
        ("call_report_filings", "period_end", "1970-01-01", "2026-06-30"),  # +2026Q1 via CDR (07d/07e)
        ("luck_call_reports", "period_end", "1930-01-01", "2026-06-30"),
        ("occ_historical", "report_date", "1860-01-01", "1942-01-01"),  # Phase 9b extended OCC-CLV to 1941
        ("bank_failures", "closing_date", "1930-01-01", "2027-01-01"),
        ("fdic_financials", "period_end", "1980-01-01", "2026-06-30"),
        ("pillar3_disclosures", "period_end", "2020-01-01", "2026-12-31"),
        ("ncua_5300", "period_end", "1994-01-01", "2026-12-31"),  # NCUA 5300 (credit unions), FULL history 1994Q1-2025Q4 (128 periods); bound leaves room for future quarters
        ("ubpr_ratios", "period_end", "2001-01-01", "2026-12-31"),  # FFIEC UBPR (CDR XBRL bulk)
        ("ubpr_peer_stats", "reporting_period", "2001-01-01", "2026-12-31"),  # UBPR Stats peer benchmarks (CDR Four-Periods)
        ("ubpr_peer_rank", "reporting_period", "2001-01-01", "2026-12-31"),  # UBPR Rank per-bank percentiles (CDR Four-Periods)
        ("y15_systemic_indicators", "period_end", "2015-01-01", "2026-12-31"),  # FR Y-15 (NIC snapshots)
    ]

    all_pass = True
    for table, col, expect_min, expect_max in checks:
        result = con.execute(f"SELECT MIN({col}), MAX({col}) FROM {table}").fetchone()
        actual_min, actual_max = str(result[0]), str(result[1])

        min_ok = actual_min >= expect_min
        max_ok = actual_max <= expect_max
        status = "PASS" if (min_ok and max_ok) else "WARN"
        if status != "PASS":
            all_pass = False

        print(f"    {table}: {actual_min} to {actual_max} [{status}]")

    return all_pass


def check_null_dates(con):
    """Check for NULL dates in filing tables."""
    print("\n  3. NULL Date Check")

    checks = [
        ("bhcf_filings", "period_end"),
        ("call_report_filings", "period_end"),
        ("luck_call_reports", "period_end"),
        ("occ_historical", "report_date"),
        ("bank_failures", "closing_date"),
        ("fdic_financials", "period_end"),
        ("pillar3_disclosures", "period_end"),
        ("ncua_5300", "period_end"),
        ("ubpr_ratios", "period_end"),
        ("ubpr_peer_stats", "reporting_period"),
        ("ubpr_peer_rank", "reporting_period"),
        ("y15_systemic_indicators", "period_end"),
    ]

    all_pass = True
    for table, col in checks:
        total = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        nulls = con.execute(f"SELECT COUNT(*) - COUNT({col}) FROM {table}").fetchone()[0]
        pct_null = (nulls / total) * 100 if total > 0 else 0

        status = "PASS" if nulls == 0 else "WARN" if pct_null < 1 else "FAIL"
        if status != "PASS":
            all_pass = False
        print(f"    {table}.{col}: {nulls:,} NULLs out of {total:,} ({pct_null:.2f}%) [{status}]")

    return all_pass


def check_cross_source_overlap(con):
    """Check BHCF vs Luck for overlapping entities and variables."""
    print("\n  4. Cross-Source Validation")

    # Entities in common between BHCF and Luck
    overlap = con.execute("""
        SELECT COUNT(DISTINCT b.rssd_id) AS common_entities
        FROM (SELECT DISTINCT rssd_id FROM bhcf_filings) b
        JOIN (SELECT DISTINCT entity_id FROM luck_call_reports) l
        ON b.rssd_id = l.entity_id
    """).fetchone()[0]
    print(f"    BHCF-Luck common entities: {overlap:,}")

    # Variables in common
    var_overlap = con.execute("""
        SELECT COUNT(*) AS common_vars
        FROM (SELECT DISTINCT variable_id FROM bhcf_filings) b
        JOIN (SELECT DISTINCT variable_id FROM luck_call_reports) l
        USING (variable_id)
    """).fetchone()[0]
    print(f"    BHCF-Luck common variables: {var_overlap:,}")

    # Spot-check: Compare a value for a known entity in overlapping quarters
    if overlap > 0 and var_overlap > 0:
        sample = con.execute("""
            SELECT b.rssd_id, b.period_end, b.variable_id,
                   b.value AS bhcf_value,
                   l.value AS luck_value,
                   ABS(b.value - l.value) AS diff
            FROM bhcf_filings b
            JOIN luck_call_reports l
                ON b.rssd_id = l.entity_id
                AND b.period_end = l.period_end
                AND b.variable_id = l.variable_id
            WHERE b.value != 0 AND l.value != 0
            LIMIT 5
        """).fetchdf()
        if not sample.empty:
            print(f"    Sample cross-source matches:")
            print(sample.to_string(index=False))

    return True


def check_cross_source_gsib(con):
    """Validate total assets for G-SIBs across BHCF, FDIC SDI, and DFAST."""
    print("\n  4b. G-SIB Cross-Source Validation")

    # 5 G-SIBs with known RSSDs
    gsibs = [
        (1039502, "JPMorgan Chase"),
        (1073757, "Bank of America"),
        (1951350, "Citigroup"),
        (1120754, "Wells Fargo"),
        (2162966, "Morgan Stanley"),
    ]

    all_pass = True
    for rssd, name in gsibs:
        # Latest BHCF total assets (BHCK2170)
        bhcf = con.execute(f"""
            SELECT value FROM bhcf_filings
            WHERE rssd_id = {rssd} AND variable_id = 'BHCK2170'
            ORDER BY period_end DESC LIMIT 1
        """).fetchone()

        # Latest FDIC total assets
        fdic = con.execute(f"""
            SELECT value FROM fdic_financials
            WHERE rssd_id = {rssd} AND variable_id = 'asset'
            ORDER BY period_end DESC LIMIT 1
        """).fetchone()

        # DFAST presence
        dfast_count = con.execute(f"""
            SELECT COUNT(*) FROM dfast_results WHERE rssd_id = {rssd}
        """).fetchone()[0]

        # Pillar 3 presence
        p3_count = con.execute(f"""
            SELECT COUNT(*) FROM pillar3_disclosures WHERE rssd_id = {rssd}
        """).fetchone()[0]

        bhcf_val = f"${bhcf[0]/1e6:,.0f}T" if bhcf and bhcf[0] else "N/A"
        fdic_val = f"${fdic[0]/1e6:,.0f}T" if fdic and fdic[0] else "N/A"

        status = "PASS" if bhcf and dfast_count > 0 else "WARN"
        if status != "PASS":
            all_pass = False
        print(f"    {name}: BHCF={bhcf_val}, FDIC={fdic_val}, DFAST={dfast_count} obs, P3={p3_count} obs [{status}]")

    return all_pass


def spot_check_known_values(con):
    """Spot-check known entities (JPMorgan, Bank of America, etc.)."""
    print("\n  5. Spot-Check Known Entities")

    # JPMorgan Chase RSSD: 1039502
    jpm = con.execute("""
        SELECT name_legal, entity_type, is_active, state_code
        FROM institutions
        WHERE rssd_id = 1039502
    """).fetchone()

    if jpm:
        print(f"    JPMorgan (1039502): {jpm[0]}, type={jpm[1]}, active={jpm[2]}, state={jpm[3]}")
    else:
        print("    JPMorgan (1039502): NOT FOUND [WARN]")

    # Check JPM has BHCF filings
    jpm_filings = con.execute("""
        SELECT COUNT(*) AS obs,
               COUNT(DISTINCT period_end) AS quarters,
               MIN(period_end) AS first_q,
               MAX(period_end) AS last_q
        FROM bhcf_filings
        WHERE rssd_id = 1039502
    """).fetchone()
    if jpm_filings:
        print(f"    JPM BHCF: {jpm_filings[0]:,} obs, {jpm_filings[1]} quarters ({jpm_filings[2]} to {jpm_filings[3]})")

    # Total assets variable (BHCK2170) for JPM, most recent
    ta = con.execute("""
        SELECT period_end, value
        FROM bhcf_filings
        WHERE rssd_id = 1039502 AND variable_id = 'BHCK2170'
        ORDER BY period_end DESC
        LIMIT 3
    """).fetchall()
    if ta:
        print(f"    JPM Total Assets (BHCK2170):")
        for row in ta:
            print(f"      {row[0]}: ${row[1]/1000:,.0f}B" if row[1] else f"      {row[0]}: NULL")
    else:
        print("    JPM Total Assets: No BHCK2170 data found [WARN]")

    return True


def catalog_completeness(con):
    """Check that catalog tables are populated and consistent."""
    print("\n  6. Catalog Completeness")

    catalog_tables = {
        'catalog.variables': 'Should match distinct variables across all filings',
        'catalog.filing_coverage': 'Should cover all quarters',
        'catalog.entity_coverage': 'Should cover all filing entities',
        'catalog.schema_evolution': 'Should match catalog.variables count',
        'catalog.data_sources': 'Should list all source files',
    }

    all_pass = True
    for table, desc in catalog_tables.items():
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        status = "PASS" if count > 0 else "FAIL"
        if status != "PASS":
            all_pass = False
        print(f"    {table}: {count:,} rows [{status}]")

    return all_pass


def check_clv_feature_tables(con):
    """Validate the two CLV-era public tables (fdic_sdi_features, cdr_unrealized_losses).

    Row-count floors, year/date ranges, and not-all-null key columns. Static
    thresholds (per WS1 spec): fdic_sdi_features >= 400,000 rows spanning 1984-2025;
    cdr_unrealized_losses >= 40,000 rows spanning 2019-2025.
    """
    print("\n  8. CLV Feature Tables")

    all_pass = True

    # --- fdic_sdi_features ---
    sdi_rows = con.execute("SELECT COUNT(*) FROM fdic_sdi_features").fetchone()[0]
    sdi_status = "PASS" if sdi_rows >= 400_000 else "FAIL"
    if sdi_status != "PASS":
        all_pass = False
    print(f"    fdic_sdi_features rows: {sdi_rows:,} (floor 400,000) [{sdi_status}]")

    sdi_yr = con.execute("SELECT MIN(year), MAX(year) FROM fdic_sdi_features").fetchone()
    yr_min, yr_max = sdi_yr[0], sdi_yr[1]
    yr_status = "PASS" if (yr_min is not None and yr_min >= 1984 and yr_max <= 2025) else "WARN"
    if yr_status != "PASS":
        all_pass = False
    print(f"    fdic_sdi_features year range: {yr_min} to {yr_max} (expect 1984-2025) [{yr_status}]")

    sdi_nn = con.execute("SELECT COUNT(uninsured_ratio) FROM fdic_sdi_features").fetchone()[0]
    nn_status = "PASS" if sdi_nn > 0 else "FAIL"
    if nn_status != "PASS":
        all_pass = False
    print(f"    fdic_sdi_features.uninsured_ratio non-null: {sdi_nn:,} [{nn_status}]")

    # --- cdr_unrealized_losses ---
    cdr_rows = con.execute("SELECT COUNT(*) FROM cdr_unrealized_losses").fetchone()[0]
    cdr_status = "PASS" if cdr_rows >= 40_000 else "FAIL"
    if cdr_status != "PASS":
        all_pass = False
    print(f"    cdr_unrealized_losses rows: {cdr_rows:,} (floor 40,000) [{cdr_status}]")

    cdr_pe = con.execute("SELECT MIN(period_end), MAX(period_end) FROM cdr_unrealized_losses").fetchone()
    # period_end is a TIMESTAMP -> str() yields "2025-12-31 00:00:00"; compare the
    # DATE portion only so the time suffix doesn't break the lexical range check.
    pe_min, pe_max = str(cdr_pe[0])[:10], str(cdr_pe[1])[:10]
    pe_status = "PASS" if (cdr_pe[0] is not None and pe_min >= "2019-01-01" and pe_max <= "2025-12-31") else "WARN"
    if pe_status != "PASS":
        all_pass = False
    print(f"    cdr_unrealized_losses period_end range: {pe_min} to {pe_max} (expect 2019-2025) [{pe_status}]")

    cdr_nn = con.execute("SELECT COUNT(total_unrealized_loss) FROM cdr_unrealized_losses").fetchone()[0]
    cnn_status = "PASS" if cdr_nn > 0 else "FAIL"
    if cnn_status != "PASS":
        all_pass = False
    print(f"    cdr_unrealized_losses.total_unrealized_loss non-null: {cdr_nn:,} [{cnn_status}]")

    return all_pass


def check_clean_bank_panel(con):
    """Validate the canonical clean_bank_panel: row floor, year span, the headline UNIT GATE
    (JPM 2008 ~$1.75T / SVB ~$209B / occ-1929 ~$1.8B), and the 1942-1958 honest-gap.

    This is the from-raw clean panel that FIXES robin_panel's uncalibrated absolute-$ columns
    (built by 45_build_clean_bank_panel.py). The unit gate is the load-bearing check: a units
    regression (e.g. a missing x1000 or a BHC-aggregate leaking in) trips it and FAILs.
    """
    print("\n  8b. Clean Bank Panel (canonical from-raw levels)")

    exists = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='clean_bank_panel'"
    ).fetchone()[0]
    if not exists:
        print("    clean_bank_panel MISSING -- run 45_build_clean_bank_panel.py [FAIL]")
        return False

    all_pass = True

    rows = con.execute("SELECT COUNT(*) FROM clean_bank_panel").fetchone()[0]
    r_status = "PASS" if rows >= 1_000_000 else "FAIL"
    if r_status != "PASS":
        all_pass = False
    print(f"    rows: {rows:,} (floor 1,000,000) [{r_status}]")

    yr = con.execute("SELECT MIN(year), MAX(year) FROM clean_bank_panel").fetchone()
    yr_status = "PASS" if (yr[0] is not None and yr[0] <= 1863 and yr[1] >= 2024) else "WARN"
    if yr_status != "PASS":
        all_pass = False
    print(f"    year span: {yr[0]}-{yr[1]} (expect 1863-2026) [{yr_status}]")

    gap = con.execute(
        "SELECT COUNT(*) FROM clean_bank_panel WHERE year BETWEEN 1942 AND 1958"
    ).fetchone()[0]
    g_status = "PASS" if gap == 0 else "FAIL"
    if g_status != "PASS":
        all_pass = False
    print(f"    1942-1958 honest gap: {gap} rows (expect 0) [{g_status}]")

    # --- UNIT GATE (the headline) ---
    jpm = con.execute("""SELECT assets_nominal FROM clean_bank_panel
      WHERE rssd_id=852218 AND call_date='2008-12-31' AND src_vintage='sched_call'""").fetchone()
    svb = con.execute("""SELECT assets_nominal FROM clean_bank_panel
      WHERE rssd_id=802866 AND src_vintage='sched_call' ORDER BY call_date DESC LIMIT 1""").fetchone()
    occ = con.execute("""SELECT assets_nominal FROM clean_bank_panel
      WHERE era_group='HIST' AND year=1929 ORDER BY assets_nominal DESC NULLS LAST LIMIT 1""").fetchone()
    for nm, val, tgt, tol, scale in [
        ("JPM 2008 assets", jpm, 1.75, 0.05, 1e12),
        ("SVB last assets", svb, 209.0, 5.0, 1e9),
        ("occ-1929 largest", occ, 1.8, 0.15, 1e9),
    ]:
        ok = bool(val) and val[0] is not None and abs(val[0] / scale - tgt) < tol
        if not ok:
            all_pass = False
        shown = f"{val[0]/scale:.4f}" if val and val[0] is not None else "NULL"
        print(f"    unit gate {nm}: {shown} (target ~{tgt}, tol {tol}) "
              f"[{'PASS' if ok else 'FAIL'}]")

    return all_pass


def check_provenance_completeness(con):
    """9. Provenance completeness: every base table has a row in Outputs/PROVENANCE.csv.

    Definitive-build Q1 guard. Ensures no canonical table ships without a documented
    source tier, provider, URL, and terms. Views are exempt (they inherit provenance
    from their base tables). A new un-provenanced base table FAILS the gate until a
    PROVENANCE.csv row is added.
    """
    import csv as _csv
    from utils import OUTPUTS_DIR
    print("\n  9. Provenance Completeness (every base table in PROVENANCE.csv)")

    prov_csv = OUTPUTS_DIR / "PROVENANCE.csv"
    # physical-table -> provenance-csv key, where the two legitimately differ
    aliases = {"occ_historical_clv": "occ_historical"}
    if not prov_csv.exists():
        print(f"    PROVENANCE.csv missing at {prov_csv} [FAIL]")
        return False

    prov_tables = set()
    with open(prov_csv, newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            prov_tables.add(row["table"].strip())

    base_tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_type='BASE TABLE' ORDER BY table_name"
    ).fetchall()]

    missing = [t for t in base_tables
               if aliases.get(t, t) not in prov_tables and t not in prov_tables]
    covered = len(base_tables) - len(missing)
    for t in missing:
        print(f"    MISSING provenance row: {t} [FAIL]")
    status = "PASS" if not missing else "FAIL"
    print(f"    {covered}/{len(base_tables)} base tables provenanced [{status}]")
    return not missing


def check_no_orphan_codes(con):
    """10. No-orphan codes: every code used in a namespaced fact table is registered in the
    variable dictionary (catalog.namespace_variables built by 44, or catalog.variables for MDRM).
    Definitive-build Q3 guard. Description coverage is REPORTED (not a hard gate — some derived NCUA
    FS220 accounts have no published AcctDesc entry); the PASS condition is registration (no orphans).
    """
    print("\n  10. No-Orphan Codes (UBPR/RISK/FS220 registered in dictionary)")
    nv = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='catalog' AND table_name='namespace_variables'").fetchone()[0]
    if nv == 0:
        print("    catalog.namespace_variables MISSING -- run 44_build_variable_dictionary.py [FAIL]")
        return False

    all_pass = True
    for ns, table, col in [("UBPR", "ubpr_ratios", "ubpr_code"),
                           ("RISK", "y15_systemic_indicators", "risk_code"),
                           ("FS220", "ncua_5300", "account_code")]:
        total = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM {table}").fetchone()[0]
        orphan = con.execute(f"""
            WITH codes AS (SELECT DISTINCT {col} AS c FROM {table})
            SELECT COUNT(*) FROM codes c
            LEFT JOIN catalog.namespace_variables nv ON c.c = nv.variable_id
            LEFT JOIN catalog.variables v ON c.c = v.variable_id
            WHERE nv.variable_id IS NULL AND v.variable_id IS NULL
        """).fetchone()[0]
        described = con.execute(
            "SELECT COUNT(*) FROM catalog.namespace_variables "
            "WHERE namespace=? AND description IS NOT NULL", [ns]).fetchone()[0]
        reg = con.execute(
            "SELECT COUNT(*) FROM catalog.namespace_variables WHERE namespace=?", [ns]).fetchone()[0]
        pct = f"{described/reg*100:.1f}%" if reg else "n/a"
        status = "PASS" if orphan == 0 else "FAIL"
        if orphan:
            all_pass = False
        print(f"    {ns}: {total:,} codes, {orphan} orphan, {described:,}/{reg:,} described ({pct}) [{status}]")
    return all_pass


def check_dict_layer(con):
    """11. Dictionary (taxonomy) layer: schema present, the 7 expected dict tables
    populated at sane minimums, and the coverage-audit map has zero orphans.

    Dictionary-sync guard (imported by 14, views by 15, coverage map by 16). The hard
    PASS condition is the >=1-view reachability guarantee: every variable in
    dict.variable_access_map must have at least one access path (a raw_<table> or a
    shaped view). A missing dict table, an under-populated table, or any orphan FAILs.
    """
    print("\n  11. Dictionary (taxonomy) layer")

    # Schema must exist (14_import_dictionary.py must have run).
    has_dict = con.execute(
        "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'dict'"
    ).fetchone()[0]
    if has_dict == 0:
        print("    dict schema MISSING -- run 14_import_dictionary.py [FAIL]")
        return False

    all_pass = True

    # The 7 expected dict tables with row-count floors (well below current counts so a
    # genuine import drop trips the gate; current: 3,198 / 7,539 / 4,099 / 2,057 /
    # 15,622 / 3 / 15,435).
    expected = [
        ("schedule_lineitems", 2_000),
        ("relationships", 5_000),
        ("ubpr_concepts", 3_000),
        ("crosswalk", 1_500),
        ("edit_history", 10_000),
        ("meta", 3),
        ("variable_access_map", 10_000),
    ]
    present = {r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'dict'"
    ).fetchall()}
    for table, floor in expected:
        if table not in present:
            print(f"    dict.{table}: MISSING [FAIL]")
            all_pass = False
            continue
        n = con.execute(f'SELECT COUNT(*) FROM dict."{table}"').fetchone()[0]
        ok = n >= floor
        if not ok:
            all_pass = False
        print(f"    dict.{table}: {n:,} rows (floor {floor:,}) [{'PASS' if ok else 'FAIL'}]")

    # Coverage guarantee: zero variables in the access map with no access path.
    if "variable_access_map" in present:
        orphans = con.execute("""
            SELECT COUNT(*) FROM dict.variable_access_map
            WHERE (shaped_views IS NULL OR shaped_views = '')
              AND (raw_view    IS NULL OR raw_view    = '')
        """).fetchone()[0]
        ok = orphans == 0
        if not ok:
            all_pass = False
        print(f"    coverage audit: {orphans} orphan variable(s) with no access path "
              f"[{'PASS' if ok else 'FAIL'}]")

    return all_pass


def summary_statistics(con):
    """Print comprehensive summary statistics."""
    print("\n  7. Summary Statistics")

    print(f"\n    --- Data Volume ---")
    tables = [
        'mdrm', 'reporting_forms', 'institutions', 'institution_attributes',
        'branches', 'relationships', 'transformations', 'crsp_mapping',
        'bhcf_filings', 'call_report_filings', 'luck_call_reports', 'occ_historical',
        'filing_metadata', 'bank_failures', 'fdic_financials', 'fdic_sod',
        'dfast_results', 'pillar3_disclosures',
        'fdic_history', 'fred_series', 'variable_crosswalk',
        'robin_panel', 'robin_deposits_historical', 'robin_deposits_modern',
        'robin_crosswalk', 'bhc_ownership', 'sector_groupings',
        'stress_scenarios_domestic', 'stress_scenarios_international',
        'fdic_sdi_features', 'clean_bank_panel', 'cdr_unrealized_losses', 'entity_xref',
        # C3 new sources (2026-06)
        'ncua_5300', 'ncua_cu_directory', 'sec_cik_crosswalk', 'hmda_summary',
        'ubpr_ratios', 'ubpr_peer_stats', 'ubpr_peer_rank', 'nic_entity_identifiers', 'nic_attributes_ext', 'id_crosswalk',
        'y15_systemic_indicators',
    ]
    grand_total = 0
    for t in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        grand_total += count
        print(f"    {t:<30} {count:>15,}")
    print(f"    {'GRAND TOTAL':<30} {grand_total:>15,}")

    print(f"\n    --- Temporal Coverage ---")
    print(f"    OCC Historical: 1867-1904 (annual)")
    luck_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM luck_call_reports").fetchone()
    print(f"    Luck Database:  {luck_range[0]} to {luck_range[1]} ({luck_range[2]} quarters)")
    call_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()
    print(f"    Call Reports:   {call_range[0]} to {call_range[1]} ({call_range[2]} quarters)")
    bhcf_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM bhcf_filings").fetchone()
    print(f"    BHCF Filings:   {bhcf_range[0]} to {bhcf_range[1]} ({bhcf_range[2]} quarters)")
    fdic_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM fdic_financials").fetchone()
    print(f"    FDIC SDI:       {fdic_range[0]} to {fdic_range[1]} ({fdic_range[2]} quarters)")
    sod_range = con.execute("SELECT MIN(year), MAX(year), COUNT(DISTINCT year) FROM fdic_sod").fetchone()
    print(f"    FDIC SOD:       {sod_range[0]} to {sod_range[1]} ({sod_range[2]} years)")
    dfast_range = con.execute("SELECT MIN(year), MAX(year), COUNT(DISTINCT year) FROM dfast_results").fetchone()
    print(f"    DFAST:          {dfast_range[0]} to {dfast_range[1]} ({dfast_range[2]} years)")
    p3_range = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM pillar3_disclosures").fetchone()
    print(f"    Pillar 3:       {p3_range[0]} to {p3_range[1]} ({p3_range[2]} quarters)")
    fail_range = con.execute("SELECT MIN(closing_date), MAX(closing_date), COUNT(*) FROM bank_failures").fetchone()
    print(f"    Bank Failures:  {fail_range[0]} to {fail_range[1]} ({fail_range[2]:,} events)")

    print(f"\n    --- Entity Coverage ---")
    total_entities = con.execute("SELECT COUNT(*) FROM institutions").fetchone()[0]
    active = con.execute("SELECT COUNT(*) FROM institutions WHERE is_active = true").fetchone()[0]
    with_filings = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM catalog.entity_coverage").fetchone()[0]
    print(f"    Total institutions: {total_entities:,} ({active:,} active)")
    print(f"    Institutions with filings: {with_filings:,}")
    print(f"    With CRSP mapping: {con.execute('SELECT COUNT(DISTINCT rssd_id) FROM crsp_mapping').fetchone()[0]:,}")

    print(f"\n    --- Variable Coverage ---")
    total_vars = con.execute("SELECT COUNT(*) FROM catalog.variables").fetchone()[0]
    mdrm_matched = con.execute("SELECT COUNT(*) FROM catalog.variables WHERE mnemonic IS NOT NULL").fetchone()[0]
    print(f"    Total variables observed: {total_vars:,}")
    print(f"    Matched to MDRM: {mdrm_matched:,} ({mdrm_matched/total_vars*100:.1f}%)")

    return True


def main():
    elapsed = timer()
    print("=== Phase 13: Validation ===")

    con = get_db(read_only=True)

    results = {}
    results['referential_integrity'] = check_referential_integrity(con)
    results['date_ranges'] = check_date_ranges(con)
    results['null_dates'] = check_null_dates(con)
    results['cross_source'] = check_cross_source_overlap(con)
    results['gsib_validation'] = check_cross_source_gsib(con)
    results['spot_checks'] = spot_check_known_values(con)
    results['catalog'] = catalog_completeness(con)
    results['clv_feature_tables'] = check_clv_feature_tables(con)
    results['clean_bank_panel'] = check_clean_bank_panel(con)
    results['provenance_completeness'] = check_provenance_completeness(con)
    results['no_orphan_codes'] = check_no_orphan_codes(con)
    results['dict_layer'] = check_dict_layer(con)
    summary_statistics(con)

    # Final verdict
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n--- Validation Result: {passed}/{total} checks passed ---")

    con.close()

    secs = elapsed()
    log_ingestion("13", f"Validation: {passed}/{total} checks passed. {secs:.1f}s")
    print(f"\nPhase 13 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
