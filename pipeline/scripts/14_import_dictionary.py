#!/usr/bin/env python3
"""Phase 14: import the bank-data-dictionary taxonomy into freenic.duckdb (schema `dict`).

The dictionary (github.com/andenick/bank-data-dictionary) is the taxonomy source of
truth: per-schedule line-item maps for both report families, the empirically validated
relationship registry, UBPR concept derivations, the MDRM crosswalk, and the official
edit history. This script imports its machine-readable CSVs as-is (no hand-maintained
duplicates), version-stamped from the repo's git tag.

Idempotent: CREATE OR REPLACE everything. Re-run after each dictionary release.
"""
import csv
import io
import os
import re
import subprocess
import sys

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "Outputs", "freenic.duckdb"))
# Path to a local checkout of the public bank-data-dictionary repo. Set via env var.
DICT_REPO = os.environ.get("BANK_DATA_DICTIONARY_REPO", "")

# Y-9C schedule CSVs: (file, schedule label). Schemas vary; we normalize via melt below.
Y9C_FILES = [
    ("HC_BALANCE_SHEET.csv", "HC"), ("HC_B_SECURITIES.csv", "HC-B"),
    ("HC_C_LOANS.csv", "HC-C"), ("HC_D_TRADING_ASSETS.csv", "HC-D"),
    ("HC_E_DEPOSITS.csv", "HC-E"), ("HC_F_OTHER_ASSETS.csv", "HC-F"),
    ("HC_G_OTHER_LIABILITIES.csv", "HC-G"), ("HC_H_INTEREST_SENSITIVITY.csv", "HC-H"),
    ("HC_I_INSURANCE.csv", "HC-I"), ("HC_K_QUARTERLY_AVERAGES.csv", "HC-K"),
    ("HC_L_DERIVATIVES.csv", "HC-L"), ("HC_M_MEMORANDA.csv", "HC-M"),
    ("HC_N_PAST_DUE.csv", "HC-N"), ("HC_P_MORTGAGE_BANKING.csv", "HC-P"),
    ("HC_Q_FAIR_VALUE.csv", "HC-Q"), ("HC_R_CAPITAL.csv", "HC-R"),
    ("HC_S_SECURITIZATION.csv", "HC-S"), ("HC_V_VIES.csv", "HC-V"),
    ("HI_INCOME_STATEMENT.csv", "HI"), ("HI_A_EQUITY_CHANGES.csv", "HI-A"),
    ("HI_B_CHARGEOFFS.csv", "HI-B"), ("HI_C_ALLOWANCE.csv", "HI-C"),
]
CALL_FILES = [
    ("CALL_RC_BALANCE_SHEET.csv", "RC"), ("CALL_RI_INCOME.csv", "RI"),
    ("CALL_RC_B_SECURITIES.csv", "RC-B"), ("CALL_RC_C_LOANS.csv", "RC-C"),
    ("CALL_RC_E_DEPOSITS.csv", "RC-E"), ("CALL_RC_N_PAST_DUE.csv", "RC-N"),
    ("CALL_RC_R_CAPITAL.csv", "RC-R"),
]
CODE = re.compile(r"^[A-Z]{4}[A-Z0-9]{4}$")


def dict_version() -> str:
    try:
        r = subprocess.run(["git", "describe", "--tags", "--always"],
                           capture_output=True, text=True, cwd=DICT_REPO)
        return r.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def melt_schedule(path: str, family: str, schedule: str):
    """Normalize any schedule CSV: every mdrm-bearing column becomes one row."""
    rows = []
    with io.open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            line = (r.get("line_number") or "").strip()
            desc = (r.get("item_description") or r.get("loan_category")
                    or r.get("caption") or "").strip()
            forms = (r.get("forms") or r.get("form") or "").strip()
            start = (r.get("start_date") or "").strip()
            notes = (r.get("notes") or "").strip()[:400]
            for col, val in r.items():
                if not col or val is None:
                    continue
                v = val.strip()
                if not CODE.match(v):
                    continue
                if not (col.startswith("mdrm") or col in ("call_mdrm",)):
                    continue
                rows.append((family, schedule, line, desc, col, v, forms, start, notes))
    return rows


def main():
    ver = dict_version()
    con = duckdb.connect(DB)
    con.execute("CREATE SCHEMA IF NOT EXISTS dict")

    # --- dict.schedule_lineitems (melted, normalized) ---
    all_rows = []
    missing = []
    for fname, sched in Y9C_FILES:
        p = os.path.join(DICT_REPO, "csv", fname)
        if os.path.exists(p):
            all_rows += melt_schedule(p, "y9c", sched)
        else:
            missing.append(fname)
    for fname, sched in CALL_FILES:
        p = os.path.join(DICT_REPO, "csv", fname)
        if os.path.exists(p):
            all_rows += melt_schedule(p, "call", sched)
        else:
            missing.append(fname)
    if missing:
        print(f"FATAL: dictionary CSVs missing: {missing}", file=sys.stderr)
        sys.exit(1)
    con.execute("""
      CREATE OR REPLACE TABLE dict.schedule_lineitems (
        form_family VARCHAR, schedule VARCHAR, line_number VARCHAR,
        item_description VARCHAR, column_role VARCHAR, mdrm_code VARCHAR,
        forms VARCHAR, start_date VARCHAR, notes VARCHAR)
    """)
    con.executemany(
        "INSERT INTO dict.schedule_lineitems VALUES (?,?,?,?,?,?,?,?,?)", all_rows)

    # --- verbatim imports ---
    def load_csv(table, fname):
        p = os.path.join(DICT_REPO, "csv", fname).replace(os.sep, "/")
        con.execute(f"""CREATE OR REPLACE TABLE dict.{table} AS
                        SELECT * FROM read_csv_auto('{p}', header=true, all_varchar=true)""")
        return con.execute(f"SELECT COUNT(*) FROM dict.{table}").fetchone()[0]

    n_rel = load_csv("relationships", "RELATIONSHIP_REGISTRY.csv")
    n_ub = load_csv("ubpr_concepts", "UBPR_CONCEPTS.csv")
    n_xw = load_csv("crosswalk", "MDRM_CROSSWALK_EXPANDED.csv")
    n_eh = load_csv("edit_history", "EDIT_HISTORY.csv")

    # --- meta ---
    con.execute("CREATE OR REPLACE TABLE dict.meta (key VARCHAR, value VARCHAR)")
    con.executemany("INSERT INTO dict.meta VALUES (?, ?)", [
        ("dictionary_version", ver),
        ("dictionary_repo", "https://github.com/andenick/bank-data-dictionary"),
        ("imported_by", "scripts/14_import_dictionary.py"),
    ])

    n_li = con.execute("SELECT COUNT(*) FROM dict.schedule_lineitems").fetchone()[0]
    n_codes = con.execute(
        "SELECT COUNT(DISTINCT mdrm_code) FROM dict.schedule_lineitems").fetchone()[0]
    con.close()
    print(f"dict layer imported (dictionary {ver}):")
    print(f"  schedule_lineitems: {n_li} rows, {n_codes} distinct codes, "
          f"{len(Y9C_FILES)} y9c + {len(CALL_FILES)} call schedules")
    print(f"  relationships: {n_rel} | ubpr_concepts: {n_ub} | crosswalk: {n_xw} | edit_history: {n_eh}")


if __name__ == "__main__":
    main()
