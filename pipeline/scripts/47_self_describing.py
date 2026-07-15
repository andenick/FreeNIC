"""47_self_describing.py — W3 usability lift: make the freenic warehouse self-describing.

ADDITIVE, REVERSIBLE, IDEMPOTENT changes only:
  1. COMMENT ON every covered base table + its key (code) and value columns, stating
     units, long-format/EAV shape, code namespace, and the friendly "use → ..." pointer.
  2. CREATE OR REPLACE TABLE main.freenic_manifest — one row per table/view: purpose,
     grain, units, code_column, canonical_or_derived, use_instead, row_count, period_span.
     This is the "front door from inside the data."

This script NEVER drops/alters fact data and NEVER changes a base-table row count. It only
writes catalog comments and rebuilds the freenic_manifest metadata table. Re-running it
produces an identical result (COMMENT ON overwrites; manifest is CREATE OR REPLACE).

Run:  python pipeline/scripts/47_self_describing.py
Units convention reference: Outputs/UNITS.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import DB_PATH  # noqa: E402


# ---------------------------------------------------------------------------
# Units convention (single source of truth — mirrored into Outputs/UNITS.md)
# ---------------------------------------------------------------------------
# Verified read-only against the live warehouse (2026-06-17):
#   call_report_filings / fdic_financials / bhcf_filings : USD THOUSANDS
#       (JPM 2024Q4 total assets = 3,459,261,000 = $3.459T in thousands)
#   ncua_5300                                            : USD (whole dollars)
#       (Navy Federal ACCT_010 = 180,813,031,049 = ~$180.8B in whole dollars)
#   occ_historical                                       : USD (whole dollars)
#       (largest 1940 assets = 3,773,138,744 = ~$3.77B in whole dollars)
#   ubpr_ratios                                          : CODE-DEPENDENT
#       (ratio codes are percent; dollar codes are USD THOUSANDS)
#   clean_bank_panel  *_nominal                          : USD (whole nominal dollars)
#       (JPM 2024Q4 assets_nominal = 3,459,261,000,000 = $3.459T whole dollars)
#                     *_real                             : USD, CPI-deflated, base 1990=100
#   y15_systemic_indicators                              : CODE-DEPENDENT (USD thousands / count / ratio)
# ---------------------------------------------------------------------------


def _esc(s: str) -> str:
    """Escape a string literal for inline SQL (single quotes only)."""
    return s.replace("'", "''")


# (table, comment) — one-line purpose + grain + units + friendly pointer.
TABLE_COMMENTS: dict[str, str] = {
    "call_report_filings": (
        "Individual-bank FFIEC Call Report filings, long format (one row per "
        "rssd_id x period_end x variable_id). Dollar values are USD THOUSANDS "
        "(divide by 1e6 for $B, 1e9 for $T). Codes are MDRM (RCFD/RCON/RIAD...) -- "
        "join mdrm on variable_id for labels. For humans: use clean_bank_panel "
        "(dollar levels) or sched_call_rc (wide, line-item named)."
    ),
    "bhcf_filings": (
        "Bank-HOLDING-COMPANY consolidated financials (FR Y-9C), long format "
        "(rssd_id x period_end x variable_id). Holding-company level, NOT bank level -- "
        "use fdic_financials for the bank subsidiary. Dollar values are USD THOUSANDS. "
        "Codes are MDRM (BHCK/BHCP...) -- join mdrm on variable_id. For humans: bhcf_enriched."
    ),
    "fdic_financials": (
        "FDIC Statistics on Depository Institutions (SDI) bank-level financials, long "
        "format (fdic_cert/rssd_id x period_end x variable_id). BANK level (vs bhcf_filings "
        "holding-co level). Dollar values are USD THOUSANDS. Codes are FDIC SDI field names "
        "(ASSET, DEP, NETINC...). For engineered ratios/flags use fdic_sdi_features."
    ),
    "ubpr_ratios": (
        "FFIEC UBPR standardized ratios + supporting dollar items, long format "
        "(rssd_id x period_end x ubpr_code). UNITS ARE CODE-DEPENDENT: ratio codes are "
        "PERCENT, dollar codes are USD THOUSANDS -- check the code's concept. Codes are "
        "UBPR##### -- join dict.ubpr_concepts on the code. For humans: ubpr_matrix (wide)."
    ),
    "ncua_5300": (
        "NCUA credit-union 5300 call reports, long format (cu_number x period_end x "
        "schedule x account_code). Keyed by NCUA CU_NUMBER, NOT rssd_id (separate universe "
        "from banks). Dollar values are USD (WHOLE DOLLARS, not thousands). Codes are NCUA "
        "ACCT_* account codes -- join catalog.namespace_variables for labels."
    ),
    "luck_call_reports": (
        "Luck/FRBNY historical Call Report reconstruction 1959Q4-1975Q4, long format "
        "(entity_id x period_end x variable_id). Bridges the pre-1976 gap before the modern "
        "Call series. Dollar values are USD THOUSANDS. For humans: luck_wide (pivoted) or "
        "clean_bank_panel (the canonical combined historical+modern level panel)."
    ),
    "occ_historical": (
        "OCC national-bank balance sheets 1863-1941, long format (bank_id x report_date x "
        "variable_id). Keyed by OCC charter id (bank_id), NOT rssd_id. Dollar values are USD "
        "(WHOLE DOLLARS, not thousands). variable_id is a plain concept name (assets, "
        "deposits...). For humans: clean_bank_panel (HIST stratum, with CPI-real twin)."
    ),
    "clean_bank_panel": (
        "CANONICAL per-bank dollar-LEVEL panel, one row per (entity, year), 1863-2026 with "
        "an honest 1942-1958 gap. Built FROM RAW (occ_historical/luck_wide/sched_call). "
        "*_nominal columns are WHOLE USD DOLLARS (NOT thousands -- do NOT divide by 1000); "
        "*_real columns are CPI-deflated to base 1990=100. THIS is the friendly path for "
        "'total assets for a bank over time'. Use instead of robin_panel for dollar levels."
    ),
    "robin_panel": (
        "GUARDED VIEW over robin_panel_base (CLV 'Failing Banks' verbatim import, annual "
        "1863-2024). Its RATIOS (leverage, deposit/asset, etc.) are clean and usable; the four "
        "UNCALIBRATED CPI-deflated dollar columns are exposed only as *_uncalibrated_real "
        "(the bare names assets/deposits/loans/equity are removed so a dollar-level SELECT "
        "errors). For dollar LEVELS use clean_bank_panel instead. (Guard: scripts/48.)"
    ),
    "fdic_sdi_features": (
        "Engineered bank-YEAR ratios and failure flags derived from fdic_financials "
        "(1984-2025, Q4 snapshot). 'assets' is USD THOUSANDS; *_ratio/roa/nim/income_ratio "
        "are ratios; F1/F3/F5_failure are 0/1 flags. For raw line items use fdic_financials."
    ),
    "institutions": (
        "Master entity table (NIC): one row per rssd_id (active + closed/merged). The entity "
        "join key for the long fact tables. Join on rssd_id; map fdic_cert<->rssd_id via "
        "id_crosswalk. Not a fact table (no period grain)."
    ),
    "id_crosswalk": (
        "Keystone identity crosswalk: one row per rssd_id with fdic_cert, cik, ticker, lei, "
        "occ/ncua/thrift ids. Use to translate between identifier systems across sources "
        "(e.g. FDIC cert <-> RSSD <-> SEC CIK). Reference table, no period grain."
    ),
    "entity_xref": (
        "Canonical RSSD identity universe: one row per rssd_id with the set of source systems "
        "that reference it and a source count. Use to check which sources cover an entity. "
        "Reference table, no period grain."
    ),
    "mdrm": (
        "FFIEC Master Data Reference Manual: the label dictionary for MDRM variable codes "
        "(BHCK/RCFD/RCON/RIAD...). Join mdrm.variable_id = <fact>.variable_id to resolve a "
        "code to item_name/description. Reference table, no period grain."
    ),
    "variable_crosswalk": (
        "Cross-source variable mapping: source_variable/source_table -> standardized concept "
        "(total_assets, net_income...). Powers the cross_source_financials view. Use this (or "
        "the MCP search_variables tool) to find the right code in each source for a concept."
    ),
    "y15_systemic_indicators": (
        "FR Y-15 systemic-risk indicators (G-SIB scoring), long format (rssd_id x period_end x "
        "risk_code). UNITS ARE CODE-DEPENDENT (USD thousands / counts / ratios per indicator)."
    ),
}

# (table, column, comment) — value column + code/key column units & namespace.
COLUMN_COMMENTS: list[tuple[str, str, str]] = [
    # ---- USD-thousands long fact tables ----
    ("call_report_filings", "value", "USD THOUSANDS for dollar items (divide 1e6 for $B). Long-format value; meaning set by variable_id."),
    ("call_report_filings", "variable_id", "MDRM code (RCFD/RCON/RIAD prefix + item). Join mdrm on variable_id for the human label."),
    ("bhcf_filings", "value", "USD THOUSANDS for dollar items (holding-company consolidated). Long-format value; meaning set by variable_id."),
    ("bhcf_filings", "variable_id", "MDRM code (BHCK/BHCP prefix + item). Join mdrm on variable_id for the human label."),
    ("fdic_financials", "value", "USD THOUSANDS for dollar items (bank level). Long-format value; meaning set by variable_id."),
    ("fdic_financials", "variable_id", "FDIC SDI field name (ASSET, DEP, NETINC, ...). Not an MDRM code; see DATA_DICTIONARY."),
    ("luck_call_reports", "value", "USD THOUSANDS for dollar items. Long-format value; meaning set by variable_id."),
    ("luck_call_reports", "variable_id", "MDRM-style code; join mdrm on variable_id where available."),
    # ---- whole-dollar long fact tables ----
    ("ncua_5300", "value", "USD WHOLE DOLLARS (NOT thousands). Long-format value; meaning set by account_code."),
    ("ncua_5300", "account_code", "NCUA ACCT_* account code. Join catalog.namespace_variables for the label."),
    ("occ_historical", "value", "USD WHOLE DOLLARS (NOT thousands; 1863-1941 balance sheets). Long-format value; meaning set by variable_id."),
    ("occ_historical", "variable_id", "Plain concept name (assets, deposits, loans, ...). Not an MDRM code."),
    # ---- code-dependent long fact tables ----
    ("ubpr_ratios", "value", "CODE-DEPENDENT: PERCENT for ratio codes, USD THOUSANDS for dollar codes. Check the code's concept."),
    ("ubpr_ratios", "ubpr_code", "UBPR##### code. Join dict.ubpr_concepts for the concept/label and to tell ratio vs dollar."),
    ("y15_systemic_indicators", "value", "CODE-DEPENDENT units (USD thousands / count / ratio) per risk_code."),
    ("y15_systemic_indicators", "risk_code", "FR Y-15 indicator code; see DATA_DICTIONARY / namespace dictionary."),
    # ---- clean_bank_panel: the friendly level panel ----
    ("clean_bank_panel", "assets_nominal", "WHOLE USD DOLLARS, nominal (NOT thousands -- do NOT divide by 1000). Total assets level."),
    ("clean_bank_panel", "assets_real", "WHOLE USD DOLLARS, CPI-deflated to base 1990=100. Real total-assets level."),
    ("clean_bank_panel", "unit_basis", "Unit basis tag for the *_nominal columns; constant 'nominal_usd' (whole dollars)."),
    ("clean_bank_panel", "rssd_id", "RSSD id (MODERN rows only; NULL for HIST). Join institutions/id_crosswalk."),
    ("clean_bank_panel", "bank_id", "OCC charter id (HIST rows only; NULL for MODERN)."),
    # ---- robin_panel footgun: the bare dollar columns are removed by the scripts/48 guard;
    #      the *_uncalibrated_real columns are commented there (COMMENT ON COLUMN robin_panel.*).
    # ---- fdic_sdi_features ----
    ("fdic_sdi_features", "assets", "USD THOUSANDS (total assets; derived from fdic_financials)."),
]


def apply_comments(con: duckdb.DuckDBPyConnection) -> tuple[int, int]:
    """Apply table + column comments. Idempotent (COMMENT ON overwrites). Returns counts."""
    n_tab = 0
    for tbl, comment in TABLE_COMMENTS.items():
        con.execute(f"COMMENT ON TABLE main.{tbl} IS '{_esc(comment)}'")
        n_tab += 1
    n_col = 0
    for tbl, col, comment in COLUMN_COMMENTS:
        con.execute(f'COMMENT ON COLUMN main.{tbl}."{col}" IS \'{_esc(comment)}\'')
        n_col += 1
    return n_tab, n_col


# ---------------------------------------------------------------------------
# freenic_manifest rows. Fields:
#   name, kind, schema, purpose, grain, units, code_column,
#   canonical_or_derived, use_instead  (row_count + period_span filled live)
# Only objects we curate get rich rows; everything else is auto-filled minimally below.
# ---------------------------------------------------------------------------
MANIFEST_CURATED: dict[str, dict] = {
    # name: dict of the descriptive fields
    "call_report_filings": dict(
        purpose="Individual-bank FFIEC Call Report filings (long/EAV).",
        grain="rssd_id x period_end x variable_id", units="USD thousands (dollar items)",
        code_column="variable_id", canonical_or_derived="canonical",
        use_instead="clean_bank_panel (levels) / sched_call_rc (wide) / mdrm (labels)"),
    "bhcf_filings": dict(
        purpose="Bank-HOLDING-COMPANY consolidated FR Y-9C financials (long/EAV).",
        grain="rssd_id x period_end x variable_id", units="USD thousands (dollar items)",
        code_column="variable_id", canonical_or_derived="canonical",
        use_instead="bhcf_enriched (named) / fdic_financials (bank level not holding-co)"),
    "fdic_financials": dict(
        purpose="FDIC SDI bank-level financials (long/EAV).",
        grain="fdic_cert/rssd_id x period_end x variable_id", units="USD thousands (dollar items)",
        code_column="variable_id", canonical_or_derived="canonical",
        use_instead="fdic_sdi_features (engineered ratios/flags); bhcf_filings for holding-co"),
    "ubpr_ratios": dict(
        purpose="FFIEC UBPR standardized ratios + dollar items (long/EAV).",
        grain="rssd_id x period_end x ubpr_code", units="code-dependent: percent (ratios) / USD thousands (dollars)",
        code_column="ubpr_code", canonical_or_derived="canonical",
        use_instead="ubpr_matrix (wide) / dict.ubpr_concepts (labels)"),
    "ncua_5300": dict(
        purpose="NCUA credit-union 5300 call reports (long/EAV).",
        grain="cu_number x period_end x schedule x account_code", units="USD whole dollars (NOT thousands)",
        code_column="account_code", canonical_or_derived="canonical",
        use_instead="catalog.namespace_variables (labels). Keyed by CU_NUMBER, not rssd_id."),
    "luck_call_reports": dict(
        purpose="Luck/FRBNY historical Call reconstruction 1959-1975 (long/EAV).",
        grain="entity_id x period_end x variable_id", units="USD thousands (dollar items)",
        code_column="variable_id", canonical_or_derived="canonical",
        use_instead="luck_wide (pivoted) / clean_bank_panel (canonical level panel)"),
    "occ_historical": dict(
        purpose="OCC national-bank balance sheets 1863-1941 (long/EAV).",
        grain="bank_id x report_date x variable_id", units="USD whole dollars (NOT thousands)",
        code_column="variable_id", canonical_or_derived="canonical",
        use_instead="clean_bank_panel (HIST stratum, with CPI-real twin). Keyed by OCC charter id."),
    "clean_bank_panel": dict(
        purpose="CANONICAL per-bank dollar-LEVEL panel (from-raw, nominal + CPI-real).",
        grain="(entity, year) -- one row per bank-year", units="*_nominal = whole USD; *_real = whole USD, base 1990=100",
        code_column="(wide; no code column)", canonical_or_derived="canonical (derived from raw)",
        use_instead="THIS is the friendly path for dollar levels. Use over robin_panel."),
    "robin_panel": dict(
        purpose="GUARDED VIEW over robin_panel_base (CLV 'Failing Banks' import). Ratios clean; "
                "dollar cols exposed only as *_uncalibrated_real (bare names removed).",
        grain="(bank, year)", units="ratios clean; *_uncalibrated_real are NOT dollar levels",
        code_column="(wide; no code column)", canonical_or_derived="view (guarded; scripts/48)",
        use_instead="clean_bank_panel for dollar LEVELS; robin_panel ratios are usable"),
    "robin_panel_base": dict(
        purpose="Base table behind the guarded robin_panel view (CLV 'Failing Banks' verbatim import).",
        grain="(bank, year)", units="ratios clean; raw assets/deposits/loans/equity UNCALIBRATED",
        code_column="(wide; no code column)", canonical_or_derived="canonical (raw import)",
        use_instead="query via the robin_panel view; clean_bank_panel for dollar LEVELS"),
    "occ_1867_1904": dict(
        purpose="Typed view: occ_historical WHERE source='occ_historical' (OCC TSV, 1867-1904).",
        grain="bank_id x report_date x variable_id", units="USD whole dollars (NOT thousands)",
        code_column="variable_id", canonical_or_derived="view (typed split)",
        use_instead="DO NOT union with occ_clv_1863_1941 (incompatible variable_id namespace)"),
    "occ_clv_1863_1941": dict(
        purpose="Typed view: occ_historical WHERE source='occ_historical_clv' (finhist, 1863-1941).",
        grain="bank_id x report_date x variable_id", units="USD whole dollars (NOT thousands)",
        code_column="variable_id", canonical_or_derived="view (typed split)",
        use_instead="DO NOT union with occ_1867_1904 (incompatible variable_id namespace)"),
    "fdic_sdi_features": dict(
        purpose="Engineered bank-year ratios + failure flags (from fdic_financials).",
        grain="(rssd_id, year) -- Q4 snapshot", units="assets = USD thousands; *_ratio/roa/nim = ratios; F*_failure = 0/1",
        code_column="(wide; no code column)", canonical_or_derived="derived",
        use_instead="fdic_financials for raw line items"),
    "y15_systemic_indicators": dict(
        purpose="FR Y-15 systemic-risk indicators (G-SIB scoring) (long/EAV).",
        grain="rssd_id x period_end x risk_code", units="code-dependent (USD thousands / count / ratio)",
        code_column="risk_code", canonical_or_derived="canonical",
        use_instead="DATA_DICTIONARY / namespace dictionary for labels"),
    "institutions": dict(
        purpose="Master entity table (NIC): the rssd_id join key.",
        grain="one row per rssd_id", units="n/a",
        code_column="rssd_id", canonical_or_derived="canonical (reference)",
        use_instead="id_crosswalk to map fdic_cert/cik/ticker/lei <-> rssd_id"),
    "id_crosswalk": dict(
        purpose="Keystone identity crosswalk across identifier systems.",
        grain="one row per rssd_id", units="n/a",
        code_column="rssd_id", canonical_or_derived="canonical (reference)",
        use_instead="(this IS the crosswalk)"),
    "entity_xref": dict(
        purpose="Canonical RSSD identity universe + source coverage.",
        grain="one row per rssd_id", units="n/a",
        code_column="rssd_id", canonical_or_derived="canonical (reference)",
        use_instead="institutions for names/attributes"),
    "mdrm": dict(
        purpose="FFIEC MDRM label dictionary for variable codes.",
        grain="one row per MDRM code", units="n/a",
        code_column="variable_id", canonical_or_derived="canonical (reference)",
        use_instead="join to any MDRM-coded fact table on variable_id"),
    "variable_crosswalk": dict(
        purpose="Cross-source variable -> standardized concept mapping.",
        grain="one row per source_variable mapping", units="n/a",
        code_column="source_variable", canonical_or_derived="canonical (reference)",
        use_instead="cross_source_financials view; MCP search_variables tool"),
    # curated views
    "cross_source_financials": dict(
        purpose="Unified financials across BHCF/Luck/FDIC via variable_crosswalk.",
        grain="rssd_id x period_end x concept x source_table", units="inherits source: USD thousands (dollar concepts)",
        code_column="concept", canonical_or_derived="view (derived)",
        use_instead="THE friendly cross-source path; clean_bank_panel for levels"),
    "sched_call_rc": dict(
        purpose="Call Schedule RC (balance sheet) pivoted wide, line-item named.",
        grain="rssd_id x period_end", units="USD thousands (dollar items)",
        code_column="(wide; columns named l<line>_<mdrm>)", canonical_or_derived="view (derived)",
        use_instead="(named-column friendly view over call_report_filings)"),
    "ubpr_matrix": dict(
        purpose="UBPR validated concepts pivoted wide (one column per UBPR code).",
        grain="rssd_id x period_end", units="code-dependent (percent / USD thousands)",
        code_column="(wide; columns named by UBPR code)", canonical_or_derived="view (derived)",
        use_instead="(named-column friendly view over ubpr_ratios)"),
    "luck_wide": dict(
        purpose="luck_call_reports pivoted wide.",
        grain="entity_id x period_end", units="USD thousands (dollar items)",
        code_column="(wide)", canonical_or_derived="view (derived)",
        use_instead="clean_bank_panel for the canonical level panel"),
    "bhcf_enriched": dict(
        purpose="bhcf_filings joined with institution names + MDRM descriptions.",
        grain="rssd_id x period_end x variable_id", units="USD thousands (dollar items)",
        code_column="variable_id", canonical_or_derived="view (derived)",
        use_instead="(friendly named view over bhcf_filings)"),
}

PERIOD_CANDIDATES = ["period_end", "call_date", "report_date", "effective_date", "year", "quarter"]


def build_manifest(con: duckdb.DuckDBPyConnection) -> int:
    """CREATE OR REPLACE main.freenic_manifest with one row per table+view. Returns row count."""
    objs = con.execute(
        """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        ORDER BY table_type, table_schema, table_name
        """
    ).fetchall()

    rows = []
    for schema, name, ttype in objs:
        if name == "freenic_manifest":
            continue
        kind = "table" if ttype == "BASE TABLE" else "view"
        fq = f'"{schema}"."{name}"'
        rc = con.execute(f"SELECT count(*) FROM {fq}").fetchone()[0]
        cols = [
            c[0]
            for c in con.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = ? AND table_name = ?",
                [schema, name],
            ).fetchall()
        ]
        pcol = next((p for p in PERIOD_CANDIDATES if p in cols), None)
        span = None
        if pcol:
            mn, mx = con.execute(f"SELECT min({pcol}), max({pcol}) FROM {fq}").fetchone()
            if mn is not None:
                span = f"{pcol}: {mn} .. {mx}"

        cur = MANIFEST_CURATED.get(name, {})
        # default code_column: pick a recognizable code-ish column if present
        default_code = next(
            (c for c in ("variable_id", "ubpr_code", "account_code", "risk_code", "concept", "rssd_id")
             if c in cols),
            "",
        )
        rows.append(
            (
                name,
                kind,
                schema,
                cur.get("purpose", ""),
                cur.get("grain", ""),
                cur.get("units", ""),
                cur.get("code_column", default_code),
                cur.get("canonical_or_derived", "view (derived)" if kind == "view" else ""),
                cur.get("use_instead", ""),
                int(rc),
                span,
            )
        )

    con.execute("DROP TABLE IF EXISTS main.freenic_manifest")
    con.execute(
        """
        CREATE TABLE main.freenic_manifest (
            name                  VARCHAR,
            kind                  VARCHAR,
            schema                VARCHAR,
            purpose               VARCHAR,
            grain                 VARCHAR,
            units                 VARCHAR,
            code_column           VARCHAR,
            canonical_or_derived  VARCHAR,
            use_instead           VARCHAR,
            row_count             BIGINT,
            period_span           VARCHAR
        )
        """
    )
    con.executemany(
        "INSERT INTO main.freenic_manifest VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows
    )
    con.execute(
        "COMMENT ON TABLE main.freenic_manifest IS "
        "'Front door from inside the data: one row per freenic table/view with purpose, "
        "grain, units, code_column, canonical-vs-derived, and the friendly use_instead path. "
        "Start here: SELECT name, purpose, units, use_instead FROM freenic_manifest. "
        "Regenerated by Technical/freenic_ingestion/scripts/47_self_describing.py.'"
    )
    return len(rows)


def main() -> None:
    print(f"[47] opening {DB_PATH} read-write (additive/idempotent: comments + manifest)")
    con = duckdb.connect(str(DB_PATH), read_only=False)
    try:
        n_tab, n_col = apply_comments(con)
        print(f"[47] applied {n_tab} table comments + {n_col} column comments")
        n_rows = build_manifest(con)
        print(f"[47] freenic_manifest rebuilt: {n_rows} rows (1 per table+view)")
    finally:
        con.close()
    print("[47] done.")


if __name__ == "__main__":
    main()
