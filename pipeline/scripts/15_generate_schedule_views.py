#!/usr/bin/env python3
"""Phase 15: generate schedule-shaped views from the dict layer (run after 14).

For every schedule in dict.schedule_lineitems, emits
  CREATE OR REPLACE VIEW sched_<family>_<schedule>
pivoting the base filing table per (rssd_id, period_end) with one column per
line-item cell, named l<line>_<mdrm>. Also:
  - ubpr_matrix : validated UBPR concepts wide per rssd x period
  - luck_wide   : the Luck historical panel's variables wide per entity x period
  - raw_<table> : thin catch-all views formalizing the long tables as views of
                  record (the >=1-view coverage guarantee's backstop)

Mechanically regenerated whenever the dictionary updates — never hand-edit views.
"""
import os
import re

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "Outputs", "freenic.duckdb"))

BASE = {"y9c": "bhcf_filings", "call": "call_report_filings"}
RAW_TABLES = [
    "call_report_filings", "bhcf_filings", "ubpr_ratios", "luck_call_reports",
    "occ_historical", "ncua_5300", "fdic_financials", "y15_systemic_indicators",
]


def ident(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def main():
    con = duckdb.connect(DB)
    schedules = con.execute("""
        SELECT form_family, schedule, line_number, column_role, mdrm_code
        FROM dict.schedule_lineitems
        ORDER BY form_family, schedule, line_number, column_role
    """).fetchall()
    by_sched = {}
    for fam, sched, line, col, code in schedules:
        by_sched.setdefault((fam, sched), []).append((line, col, code))

    made = []
    for (fam, sched), cells in by_sched.items():
        seen = set()
        cols = []
        for line, colrole, code in cells:
            name = f"l{ident(line)}_{code.lower()}"
            if name in seen:
                continue
            seen.add(name)
            cols.append(f"MAX(CASE WHEN variable_id = '{code}' THEN value END) AS {name}")
        codes = sorted({c for _, _, c in cells})
        vname = f"sched_{fam}_{ident(sched)}"
        con.execute(f"""
          CREATE OR REPLACE VIEW {vname} AS
          SELECT rssd_id, period_end,
            {", ".join(cols)}
          FROM {BASE[fam]}
          WHERE variable_id IN ({", ".join(f"'{c}'" for c in codes)})
          GROUP BY rssd_id, period_end
        """)
        made.append((vname, len(cols)))

    # ubpr_matrix: validated concepts only (wide stays manageable)
    ub = [r[0] for r in con.execute(
        "SELECT DISTINCT ubpr_code FROM dict.ubpr_concepts WHERE validated = 'yes'").fetchall()]
    if ub:
        cols = [f"MAX(CASE WHEN ubpr_code = '{c}' THEN value END) AS {c.lower()}" for c in sorted(ub)]
        con.execute(f"""
          CREATE OR REPLACE VIEW ubpr_matrix AS
          SELECT rssd_id, period_end, {", ".join(cols)}
          FROM ubpr_ratios
          WHERE ubpr_code IN ({", ".join(f"'{c}'" for c in sorted(ub))})
          GROUP BY rssd_id, period_end
        """)
        made.append(("ubpr_matrix", len(ub)))

    # luck_wide: all Luck variables (245, snake-case mnemonics already)
    lv = [r[0] for r in con.execute(
        "SELECT DISTINCT variable_id FROM luck_call_reports").fetchall()]
    cols = [f"MAX(CASE WHEN variable_id = '{c}' THEN value END) AS {ident(c)}" for c in sorted(lv)]
    con.execute(f"""
      CREATE OR REPLACE VIEW luck_wide AS
      SELECT entity_id, period_end, {", ".join(cols)}
      FROM luck_call_reports
      GROUP BY entity_id, period_end
    """)
    made.append(("luck_wide", len(lv)))

    # raw catch-alls (views of record)
    for t in RAW_TABLES:
        con.execute(f"CREATE OR REPLACE VIEW raw_{t} AS SELECT * FROM {t}")
        made.append((f"raw_{t}", 0))

    con.close()
    print(f"generated {len(made)} views:")
    for v, n in made:
        print(f"  {v}" + (f" ({n} cols)" if n else ""))


if __name__ == "__main__":
    main()
