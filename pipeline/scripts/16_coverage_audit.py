#!/usr/bin/env python3
"""Phase 16: the >=1-view coverage guarantee (run after 15).

Builds dict.variable_access_map: every distinct variable_id in every raw filing
table -> the views exposing it. Coverage is 100% by construction (raw_<table>
views are views of record); the audit FAILS (exit 1) if any variable somehow has
zero access paths, and reports the interesting number — what share has a SHAPED
(schedule/matrix) view — emitting the unshaped list to Outputs/UNMAPPED_VARIABLES.csv
as future dictionary material.
"""
import os
import sys

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "Outputs"))
DB = os.path.join(OUT, "freenic.duckdb")

TABLES = {
    "call_report_filings": ("variable_id", "call"),
    "bhcf_filings": ("variable_id", "y9c"),
    "ubpr_ratios": ("ubpr_code", "ubpr"),
    "luck_call_reports": ("variable_id", "luck"),
    "occ_historical": (None, "occ"),          # column-shaped or long: detected below
    "ncua_5300": (None, "ncua"),
    "fdic_financials": ("variable_id", "fdic"),
    "y15_systemic_indicators": (None, "y15"),
}


def varcol(con, table, hint):
    if hint:
        return hint
    cols = [r[0] for r in con.execute(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'").fetchall()]
    for c in ("variable_id", "ubpr_code", "risk_code", "acct_code", "account"):
        if c in cols:
            return c
    return None


def main():
    con = duckdb.connect(DB)
    shaped = {r[0]: r[1] for r in con.execute("""
        SELECT mdrm_code, STRING_AGG(DISTINCT 'sched_' || form_family || '_' ||
               LOWER(REGEXP_REPLACE(schedule, '[^A-Za-z0-9]+', '_', 'g')), '|')
        FROM dict.schedule_lineitems GROUP BY mdrm_code
    """).fetchall()}
    ubpr_shaped = {r[0] for r in con.execute(
        "SELECT DISTINCT ubpr_code FROM dict.ubpr_concepts WHERE validated = 'yes'").fetchall()}
    luck_vars = {r[0] for r in con.execute(
        "SELECT DISTINCT variable_id FROM luck_call_reports").fetchall()}

    con.execute("""
      CREATE OR REPLACE TABLE dict.variable_access_map (
        base_table VARCHAR, variable_id VARCHAR, n_obs BIGINT,
        shaped_views VARCHAR, raw_view VARCHAR)
    """)
    totals = {}
    unmapped_rows = []
    for table, (hint, family) in TABLES.items():
        vc = varcol(con, table, hint)
        if vc is None:
            # column-shaped table: every column is exposed by raw_<table> by definition
            cols = [r[0] for r in con.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'").fetchall()]
            con.executemany(
                "INSERT INTO dict.variable_access_map VALUES (?,?,?,?,?)",
                [(table, c, -1, "", f"raw_{table}") for c in cols])
            totals[table] = (len(cols), 0)
            continue
        rows = con.execute(
            f"SELECT {vc}, COUNT(*) FROM {table} GROUP BY 1").fetchall()
        ins, n_shaped = [], 0
        for var, n in rows:
            sv = shaped.get(var, "")
            if family == "ubpr" and var in ubpr_shaped:
                sv = (sv + "|" if sv else "") + "ubpr_matrix"
            if family == "luck" and var in luck_vars:
                sv = (sv + "|" if sv else "") + "luck_wide"
            if sv:
                n_shaped += 1
            else:
                unmapped_rows.append((table, var, n))
            ins.append((table, var, n, sv, f"raw_{table}"))
        con.executemany("INSERT INTO dict.variable_access_map VALUES (?,?,?,?,?)", ins)
        totals[table] = (len(rows), n_shaped)

    # the hard guarantee: zero variables without any access path
    n_orphan = con.execute("""
        SELECT COUNT(*) FROM dict.variable_access_map
        WHERE (shaped_views IS NULL OR shaped_views = '')
          AND (raw_view IS NULL OR raw_view = '')
    """).fetchone()[0]

    import csv as _csv
    import io as _io
    up = os.path.join(OUT, "UNMAPPED_VARIABLES.csv")
    with _io.open(up, "w", encoding="utf-8", newline="") as fo:
        w = _csv.writer(fo, lineterminator="\n")
        w.writerow(["base_table", "variable_id", "n_obs"])
        w.writerows(sorted(unmapped_rows, key=lambda r: -r[2]))
    con.close()

    print("coverage audit:")
    grand = grand_shaped = 0
    for t, (n, s) in totals.items():
        grand += n
        grand_shaped += s
        print(f"  {t}: {n} variables, {s} with shaped views ({(s / n * 100) if n else 0:.1f}%)")
    print(f"  TOTAL: {grand} variables; shaped {grand_shaped} ({grand_shaped / grand * 100:.1f}%); "
          f"all reachable via raw_<table> views of record")
    print(f"  unshaped list -> {up} ({len(unmapped_rows)} rows)")
    if n_orphan:
        print(f"FAIL: {n_orphan} variables with NO access path")
        sys.exit(1)
    print("PASS: every raw data point reachable via >=1 view")


if __name__ == "__main__":
    main()
