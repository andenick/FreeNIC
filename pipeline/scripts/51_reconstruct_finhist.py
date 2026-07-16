"""Phase 51: Load the finhist CLV-derived layer into the warehouse (B3 integration).

THIN WRAPPER over the repo-canonical `pipeline/reconstruction/build_finhist_equivalent.py`
(campaign FREENIC11_RECONSTRUCTION_20260715, plan §B3). Implements the finhist builder's
D5 note (finhist_equivalent_1863_1941_BUILD_META.json d5_note_batch5_warehouse_integration)
in the LEAST-INVASIVE faithful shape:

  EXTEND `clean_bank_panel`'s HIST-stratum machinery — do NOT build a parallel
  finhist_equivalent table. Because the warehouse contract for this batch is NEW TABLES
  ONLY (never modify existing data tables), the "derived layer over the existing
  (era_group, entity, year) spine" is materialized as the companion table
  `clean_bank_panel_clv_derived`, joinable 1:1 on (bank_id, year) to
  clean_bank_panel WHERE era_group='HIST'. It carries ONLY the CLV-derived columns
  clean_bank_panel does NOT already have (the D5 new_columns_to_add list + their
  CPI-real twins + the two published threshold dummies) plus the provenance-tier trio —
  no duplicated value columns, so this is a derived layer, not a parallel table.

Column set (from the D5 note; loci = CLV do-file lines, cited in the SPEC §2/§4):
  keys/meta   bank_id, hist_panel_key, year, era_group('HIST'), call_date,
              reconstruction_tier('derivation-layer'), src_vintage, unit_basis, cpi_gfd
  levels      interbank (04 L68), liquid (04 L72-82), emergency (04 L94-95),
              surplus_profit (04 L87-90), total_deposits (04 L98 — CLV form; a
              METHOD-CHOICE fork vs clean_bank_panel.total_deposits_hist),
              deposits (04 L100-106 era-override — a METHOD-CHOICE fork vs
              clean_bank_panel.deposits_nominal COALESCE form), bonds_circ (04 L111-112),
              res_funding (04 L116-122 — the LEVEL; clean_bank_panel carries the ratio)
  real twins  interbank/liquid/emergency/surplus_profit/total_deposits/deposits/
              bonds_circ/res_funding _real (07 L26-34 /cpi_gfd)
  ratios      surplus_ratio (07 L71), profits_ratio (07 L74), emergency_borrowing (07 L96),
              interbank_ratio (07 L100), deposit_ratio_alt (07 L84), leverage_capital
              (07 L68), + equity_shortfall (07 L73) / profit_shortfall (07 L75) — the
              published threshold dummies of the two ratios above

The 1959-75 MODL D5 note is satisfied by `luck_core_panel` (phase 50) — the task-level
schema decision, documented there.

Run:
  python 51_reconstruct_finhist.py            # load existing parquet -> warehouse table
  python 51_reconstruct_finhist.py --rebuild  # re-run build_finhist_equivalent first

Single-writer contract: RW connection only for the CREATE OR REPLACE step.
"""

import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import argparse
import json
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).parent))
from utils import DB_PATH, PROJECT_ROOT, log_ingestion, timer  # noqa: E402

sys.path.insert(0, str(PROJECT_ROOT))

RECON_DIR = PROJECT_ROOT / "Outputs" / "reconstruction"
FINHIST_PARQUET = RECON_DIR / "finhist_equivalent_1863_1941.parquet"
FINHIST_META = RECON_DIR / "finhist_equivalent_1863_1941_BUILD_META.json"

#: The derived-layer column set (D5 note). Keys/meta + CLV-derived levels + real twins
#: + the §4 ratios clean_bank_panel does not carry. NO pass-through OCC line items
#: (assets/loans/securities/... stay ONLY in clean_bank_panel — no parallel columns).
DERIVED_COLS = [
    # keys + provenance trio
    "bank_id", "hist_panel_key", "year", "era_group", "call_date",
    "reconstruction_tier", "src_vintage", "unit_basis", "cpi_gfd",
    # CLV-derived levels (04)
    "interbank", "liquid", "emergency", "surplus_profit",
    "total_deposits", "deposits", "bonds_circ", "res_funding",
    # CPI-real twins (07 L26-34)
    "interbank_real", "liquid_real", "emergency_real", "surplus_profit_real",
    "total_deposits_real", "deposits_real", "bonds_circ_real", "res_funding_real",
    # §4 ratios + published threshold dummies (07)
    "surplus_ratio", "equity_shortfall", "profits_ratio", "profit_shortfall",
    "emergency_borrowing", "interbank_ratio", "deposit_ratio_alt", "leverage_capital",
]


def rebuild():
    from pipeline.reconstruction import build_finhist_equivalent as bfe
    print("[51] rebuilding finhist_equivalent_1863_1941 (.dta -> published derivation) ...")
    rc = bfe.main()
    if rc not in (0, None):
        raise SystemExit(f"build_finhist_equivalent failed with rc={rc}")


def load_table():
    assert FINHIST_PARQUET.exists() and FINHIST_META.exists(), (
        f"missing reconstruction artifacts under {RECON_DIR} (run with --rebuild?)")
    meta = json.loads(FINHIST_META.read_text(encoding="utf-8"))
    exp_rows = int(meta["output"]["rows"])

    cols_sql = ", ".join(f'"{c}"' for c in DERIVED_COLS)
    con = duckdb.connect(str(DB_PATH))  # RW; fails loudly if another writer is attached
    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE clean_bank_panel_clv_derived AS
            SELECT {cols_sql}
            FROM read_parquet('{FINHIST_PARQUET.as_posix()}')
        """)
        n = con.execute("SELECT COUNT(*) FROM clean_bank_panel_clv_derived").fetchone()[0]
        assert n == exp_rows, f"clean_bank_panel_clv_derived rows {n} != BUILD_META {exp_rows}"
        print(f"[51] clean_bank_panel_clv_derived: {n:,} rows (== BUILD_META)")

        # grain guard: 1:1 joinable on (bank_id, year)
        dups = con.execute("""SELECT COUNT(*) FROM (SELECT bank_id, year
            FROM clean_bank_panel_clv_derived GROUP BY 1,2 HAVING COUNT(*)>1)""").fetchone()[0]
        assert dups == 0, f"(bank_id, year) grain violated: {dups} duplicate keys"

        # spine-coverage report vs the clean_bank_panel HIST stratum (informational —
        # the derived layer drops CLV bs_merge==1 rows per 04 L37-54, so coverage <100%
        # of the raw stratum is EXPECTED and honest; a collapse would indicate a key break)
        cov = con.execute("""
            SELECT COUNT(*) AS hist_rows,
                   SUM(CASE WHEN d.bank_id IS NOT NULL THEN 1 ELSE 0 END) AS joined
            FROM clean_bank_panel p
            LEFT JOIN clean_bank_panel_clv_derived d
              ON p.bank_id = d.bank_id AND p.year = d.year
            WHERE p.era_group = 'HIST'
        """).fetchone()
        pct = cov[1] / cov[0] * 100 if cov[0] else 0.0
        print(f"[51] spine coverage: {cov[1]:,}/{cov[0]:,} clean_bank_panel HIST rows "
              f"({pct:.1f}%) carry a derived-layer row (CLV 04-drop rows honestly absent)")
        assert pct > 80.0, f"spine join coverage collapsed to {pct:.1f}% — key break?"
    finally:
        con.close()
    return n, pct


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebuild", action="store_true",
                    help="re-run pipeline/reconstruction/build_finhist_equivalent first")
    args = ap.parse_args()

    elapsed = timer()
    print("=== Phase 51: finhist CLV-derived layer -> warehouse ===")
    if args.rebuild:
        rebuild()
    n, pct = load_table()
    secs = elapsed()
    log_ingestion("51", f"clean_bank_panel_clv_derived {n:,} rows (HIST derivation-layer, "
                        f"D5 shape: derived layer over the clean_bank_panel HIST spine, "
                        f"{pct:.1f}% spine coverage). {secs:.1f}s")
    print(f"\nPhase 51 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
