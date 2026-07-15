"""48_footgun_guards.py — W4 footgun neutralization for the freenic warehouse.

ADDITIVE, REVERSIBLE, IDEMPOTENT changes only. NEVER drops fact data and NEVER
changes a fact row count. Encodes the two documented W4 footgun guards:

  1. robin_panel dollar-column guard (guarded-view approach, per the user's W4 decision).
     - Rename the base table  robin_panel -> robin_panel_base  (preserves every column,
       including the W2 `source` column).
     - CREATE OR REPLACE VIEW robin_panel that exposes ALL columns EXCEPT the four
       uncalibrated CPI-deflated dollar columns under their BARE names; those four
       (assets/deposits/loans/equity) are re-exposed ONLY under the explicit names
       assets_uncalibrated_real / deposits_uncalibrated_real / loans_uncalibrated_real /
       equity_uncalibrated_real. Net effect: `SELECT assets FROM robin_panel` now ERRORS
       (the bare name no longer resolves), while every clean ratio column (leverage, roe,
       roa, deposit_ratio, ...) keeps its original name.
     - Dependents that referenced robin_panel's dollar columns by bare name
       (robin_panel_enriched via rp.*, failure_timeline via rp.assets/deposits/equity) are
       recreated against robin_panel_base so they keep working unchanged.
     - COMMENT ON the view + the four renamed columns redirect to clean_bank_panel (CPI-
       deflated, calibrated) / call_report_filings RCFD2170 for real dollar levels.

  2. occ_historical two-vintage namespace guard.
     - The base table stacks two incompatible vintages distinguished by `source`
       (occ_historical 1867-1904; occ_historical_clv 1863-1941) using different,
       only-partly-overlapping variable_id namespaces. Add two typed convenience views
       occ_1867_1904 / occ_clv_1863_1941 (each filtered to one source) with COMMENT ON
       warning they must not be unioned blindly. Comment the base table accordingly.

  3. Manifest + comments refresh: reuse 47_self_describing.apply_comments + build_manifest
     so the freenic_manifest rows for robin_panel/robin_panel_base/occ_historical and the
     new views are regenerated (47 auto-discovers every live object).

Re-running this script twice produces an identical warehouse state (rename is skipped once
robin_panel_base exists; views are CREATE OR REPLACE; comments overwrite; manifest is
rebuilt). The base-table row count of robin_panel_base always equals the pre-rename
robin_panel row count.

Run:  python pipeline/scripts/48_footgun_guards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import DB_PATH  # noqa: E402

# Reuse the self-describing comment+manifest machinery (W3 / script 47).
import importlib.util

_SPEC = importlib.util.spec_from_file_location(
    "self_describing_47", SCRIPTS_DIR / "47_self_describing.py"
)
_SD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SD)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# The four uncalibrated CPI-deflated dollar columns on robin_panel and their
# explicit guarded names. Bare names are removed from the public view so a
# `SELECT assets FROM robin_panel` errors; the data is still reachable under the
# explicit *_uncalibrated_real name (opt-in).
# ---------------------------------------------------------------------------
UNCALIBRATED_COLS = {
    "assets": "assets_uncalibrated_real",
    "deposits": "deposits_uncalibrated_real",
    "loans": "loans_uncalibrated_real",
    "equity": "equity_uncalibrated_real",
}

_COL_REDIRECT = (
    "UNCALIBRATED CPI-deflated CLV-import level -- NOT a real dollar level (year-varying "
    "~4.8x-13.8x scale; the $8.4T 'JPMorgan 2008' artifact). For real dollar LEVELS use "
    "clean_bank_panel.assets_real (CPI-deflated, calibrated) or call_report_filings "
    "RCFD2170 (nominal thousands)."
)

# Per-column redirect comments for the four renamed columns.
RENAMED_COL_COMMENTS = {
    "assets_uncalibrated_real": _COL_REDIRECT,
    "deposits_uncalibrated_real": _COL_REDIRECT.replace(
        "clean_bank_panel.assets_real", "clean_bank_panel.deposits_real"
    ),
    "loans_uncalibrated_real": _COL_REDIRECT.replace(
        "clean_bank_panel.assets_real", "clean_bank_panel.loans_real"
    ),
    "equity_uncalibrated_real": _COL_REDIRECT.replace(
        "clean_bank_panel.assets_real", "clean_bank_panel.equity_real"
    ),
}

ROBIN_VIEW_COMMENT = (
    "GUARDED VIEW over robin_panel_base (CLV 'Failing Banks' verbatim import). The four "
    "UNCALIBRATED CPI-deflated dollar columns are re-exposed ONLY as "
    "assets_uncalibrated_real / deposits_uncalibrated_real / loans_uncalibrated_real / "
    "equity_uncalibrated_real -- the bare names assets/deposits/loans/equity are removed so "
    "a dollar-level SELECT errors instead of silently returning garbage. The RATIOS "
    "(leverage, deposit_ratio, ...) are clean and keep their original names. For real "
    "dollar LEVELS use clean_bank_panel (CPI-deflated, calibrated) or call_report_filings "
    "RCFD2170. Source-of-truth base table: robin_panel_base."
)

ROBIN_BASE_COMMENT = (
    "BASE table behind the guarded robin_panel view (CLV 'Failing Banks' verbatim import; "
    "annual 1863-2024). Holds the raw uncalibrated dollar columns assets/deposits/loans/equity "
    "(NOT real dollar levels -- year-varying scale). Query through the robin_panel view; for "
    "real dollar LEVELS use clean_bank_panel / call_report_filings RCFD2170. Do not add new "
    "dependents on the bare dollar columns."
)

OCC_BASE_COMMENT = (
    "OCC national-bank balance sheets, long format (bank_id x report_date x variable_id), "
    "USD WHOLE DOLLARS. STACKS TWO INCOMPATIBLE VINTAGES distinguished by `source`: "
    "'occ_historical' (1867-1904) and 'occ_historical_clv' (1863-1941) use DIFFERENT, only "
    "partly-overlapping variable_id namespaces -- DO NOT union/aggregate across both blindly. "
    "Use the typed views occ_1867_1904 / occ_clv_1863_1941, or filter by `source`. For humans: "
    "clean_bank_panel (HIST stratum, with CPI-real twin)."
)

OCC_VIEW_1_COMMENT = (
    "Typed view: occ_historical filtered to source='occ_historical' (OCC TSV layer, 1867-1904, "
    "~95 variables). Its variable_id namespace differs from occ_clv_1863_1941 -- DO NOT union "
    "the two views blindly (incompatible variable definitions)."
)

OCC_VIEW_2_COMMENT = (
    "Typed view: occ_historical filtered to source='occ_historical_clv' (finhist historical-call "
    "extension, 1863-1941, ~66 variables). Its variable_id namespace differs from occ_1867_1904 "
    "-- DO NOT union the two views blindly (incompatible variable definitions)."
)


def _esc(s: str) -> str:
    return s.replace("'", "''")


def _table_exists(con: duckdb.DuckDBPyConnection, name: str) -> bool:
    return con.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name=?",
        [name],
    ).fetchone()[0] > 0


def _columns(con: duckdb.DuckDBPyConnection, name: str) -> list[str]:
    return [
        r[0]
        for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='main' AND table_name=? ORDER BY ordinal_position",
            [name],
        ).fetchall()
    ]


def guard_robin_panel(con: duckdb.DuckDBPyConnection) -> dict:
    """Rename robin_panel -> robin_panel_base, build the guarded view, repoint dependents.
    Idempotent. Returns a small report dict."""
    report: dict = {"repointed": []}

    base_exists = _table_exists(con, "robin_panel_base")
    rp_exists = _table_exists(con, "robin_panel")

    # Capture the pre-state row count for the safety assertion.
    if base_exists:
        pre_rows = con.execute("SELECT count(*) FROM robin_panel_base").fetchone()[0]
    else:
        pre_rows = con.execute("SELECT count(*) FROM robin_panel").fetchone()[0]
    report["row_count"] = pre_rows

    # Dependent views reference robin_panel by name; drop them before any rename so the
    # rename/replace cannot fail on a dangling dependency, then recreate them against the
    # base table.
    con.execute("DROP VIEW IF EXISTS robin_panel_enriched")
    con.execute("DROP VIEW IF EXISTS failure_timeline")

    # 1. Rename the base table (only if not already done — idempotent).
    if not base_exists:
        # robin_panel must currently be a BASE TABLE for the first run.
        ttype = con.execute(
            "SELECT table_type FROM information_schema.tables "
            "WHERE table_schema='main' AND table_name='robin_panel'"
        ).fetchone()
        if ttype and ttype[0] == "BASE TABLE":
            con.execute("ALTER TABLE robin_panel RENAME TO robin_panel_base")
            report["renamed"] = "robin_panel -> robin_panel_base"
        else:
            raise RuntimeError(
                "robin_panel_base missing AND robin_panel is not a base table -- "
                "unexpected state; aborting (no destructive action taken)."
            )
    else:
        # Already renamed on a prior run; if a stale robin_panel view lingered we will
        # CREATE OR REPLACE it below.
        report["renamed"] = "(already robin_panel_base; skipped rename)"

    # 2. Build the guarded view column list from robin_panel_base's columns.
    base_cols = _columns(con, "robin_panel_base")
    select_parts: list[str] = []
    for c in base_cols:
        if c in UNCALIBRATED_COLS:
            select_parts.append(f'"{c}" AS {UNCALIBRATED_COLS[c]}')
        else:
            select_parts.append(f'"{c}"')
    select_sql = ",\n            ".join(select_parts)
    con.execute(
        f"""
        CREATE OR REPLACE VIEW robin_panel AS
        SELECT
            {select_sql}
        FROM robin_panel_base
        """
    )
    report["view_columns"] = len(base_cols)
    report["renamed_cols"] = list(UNCALIBRATED_COLS.values())

    # 3. Recreate dependents against robin_panel_base (so bare dollar names still resolve there).
    con.execute(
        """
        CREATE OR REPLACE VIEW robin_panel_enriched AS
        SELECT rp.*, xw.rssd_id, xw.fdic_cert, xw.name_ffiec, xw.match_confidence,
               xw.entity_type AS ffiec_entity_type, xw.rssd_id_bhc
        FROM robin_panel_base AS rp
        LEFT JOIN robin_crosswalk AS xw ON (rp.bank_id = xw.bank_id_robin)
        """
    )
    report["repointed"].append("robin_panel_enriched -> robin_panel_base (rp.*)")

    con.execute(
        """
        CREATE OR REPLACE VIEW failure_timeline AS
        SELECT rp.bank_id, rp.canonical_bank_name, rp.state_abbrev, rp."year",
               rp.assets, rp.deposits, rp.equity, rp.failed_bank, rp.receivership_date,
               rp.time_to_fail, rp.run AS bank_run_indicator,
               xw.rssd_id, xw.fdic_cert, bf.bank_name AS fdic_name,
               bf.closing_date AS fdic_closing_date, bf.acquiring_institution, bf.fund
        FROM robin_panel_base AS rp
        LEFT JOIN robin_crosswalk AS xw ON (rp.bank_id = xw.bank_id_robin)
        LEFT JOIN bank_failures AS bf ON (xw.fdic_cert = bf.cert)
        WHERE rp.failed_bank = 1
        """
    )
    report["repointed"].append(
        "failure_timeline -> robin_panel_base (rp.assets/deposits/equity by bare name)"
    )

    # 4. Comments on the view, the base table, and the four renamed columns.
    con.execute(f"COMMENT ON VIEW main.robin_panel IS '{_esc(ROBIN_VIEW_COMMENT)}'")
    con.execute(f"COMMENT ON TABLE main.robin_panel_base IS '{_esc(ROBIN_BASE_COMMENT)}'")
    for col, cmt in RENAMED_COL_COMMENTS.items():
        con.execute(
            f'COMMENT ON COLUMN main.robin_panel."{col}" IS \'{_esc(cmt)}\''
        )

    # Verify the guard actually closed: bare names must NOT resolve on the view.
    view_cols = _columns(con, "robin_panel")
    leaked = [c for c in UNCALIBRATED_COLS if c in view_cols]
    if leaked:
        raise RuntimeError(f"guard failed: bare uncalibrated names still on view: {leaked}")
    missing = [c for c in UNCALIBRATED_COLS.values() if c not in view_cols]
    if missing:
        raise RuntimeError(f"guard failed: renamed columns missing from view: {missing}")

    # Safety: row count preserved through the rename.
    post_rows = con.execute("SELECT count(*) FROM robin_panel_base").fetchone()[0]
    assert post_rows == pre_rows, (
        f"robin_panel_base row count changed: {pre_rows} -> {post_rows}"
    )
    view_rows = con.execute("SELECT count(*) FROM robin_panel").fetchone()[0]
    assert view_rows == pre_rows, f"robin_panel view row count {view_rows} != base {pre_rows}"

    return report


def guard_occ_historical(con: duckdb.DuckDBPyConnection) -> dict:
    """Add the two typed occ vintage views + comments. Idempotent. Returns a report dict."""
    con.execute(
        "CREATE OR REPLACE VIEW occ_1867_1904 AS "
        "SELECT * FROM occ_historical WHERE source = 'occ_historical'"
    )
    con.execute(
        "CREATE OR REPLACE VIEW occ_clv_1863_1941 AS "
        "SELECT * FROM occ_historical WHERE source = 'occ_historical_clv'"
    )
    con.execute(f"COMMENT ON TABLE main.occ_historical IS '{_esc(OCC_BASE_COMMENT)}'")
    con.execute(f"COMMENT ON VIEW main.occ_1867_1904 IS '{_esc(OCC_VIEW_1_COMMENT)}'")
    con.execute(f"COMMENT ON VIEW main.occ_clv_1863_1941 IS '{_esc(OCC_VIEW_2_COMMENT)}'")

    base = con.execute("SELECT count(*) FROM occ_historical").fetchone()[0]
    n1 = con.execute("SELECT count(*) FROM occ_1867_1904").fetchone()[0]
    n2 = con.execute("SELECT count(*) FROM occ_clv_1863_1941").fetchone()[0]
    assert n1 + n2 == base, f"occ views {n1}+{n2} != base {base} (a third source exists?)"
    return {"occ_base": base, "occ_1867_1904": n1, "occ_clv_1863_1941": n2}


def main() -> None:
    print(f"[48] opening {DB_PATH} read-write (additive/idempotent footgun guards)")
    con = duckdb.connect(str(DB_PATH), read_only=False)
    try:
        rp = guard_robin_panel(con)
        print(f"[48] robin_panel guard: {rp['renamed']}; view exposes {rp['view_columns']} cols, "
              f"renamed {rp['renamed_cols']}; row_count {rp['row_count']:,}")
        for r in rp["repointed"]:
            print(f"      repointed: {r}")

        occ = guard_occ_historical(con)
        print(f"[48] occ guard: occ_1867_1904={occ['occ_1867_1904']:,} + "
              f"occ_clv_1863_1941={occ['occ_clv_1863_1941']:,} = base {occ['occ_base']:,}")

        # Refresh comments + manifest (47 auto-discovers every live object incl. the new
        # views and robin_panel_base). 47's curated comments are re-applied; 48's view/base
        # comments above are NOT overwritten by 47 (47 does not target robin_panel_base, the
        # occ views, or robin_panel as a view target -- but 47 DOES comment robin_panel as a
        # table; harmless, we re-assert the view comment after).
        n_tab, n_col = _SD.apply_comments(con)
        # Re-assert 48's authoritative view/base comments (in case 47 touched robin_panel).
        con.execute(f"COMMENT ON VIEW main.robin_panel IS '{_esc(ROBIN_VIEW_COMMENT)}'")
        con.execute(f"COMMENT ON TABLE main.robin_panel_base IS '{_esc(ROBIN_BASE_COMMENT)}'")
        con.execute(f"COMMENT ON TABLE main.occ_historical IS '{_esc(OCC_BASE_COMMENT)}'")
        n_rows = _SD.build_manifest(con)
        print(f"[48] refreshed {n_tab} table + {n_col} column comments; "
              f"manifest rebuilt: {n_rows} rows")
    finally:
        con.close()
    print("[48] done. Warehouse closed.")


if __name__ == "__main__":
    main()
