"""Phase 50: Load the Luck reconstruction panels into the warehouse (B3 integration).

THIN WRAPPER over the repo-canonical reconstruction module `pipeline/reconstruction`
(campaign FREENIC11_RECONSTRUCTION_20260715, plan §B3). The module builds the parquets;
this script only (optionally) invokes the builders and then materializes the warehouse
tables via the 31/45 CREATE-OR-REPLACE pattern. NEW TABLES ONLY — no existing data
table is modified.

Tables materialized (D5 shape decision, documented in the module BUILD_META + SPEC §8):
  * `luck_equivalent_panel`   — MODC 1976Q1-2026Q1, TRUE independent Fed-direct re-derivation
        from raw MDRM (`call_report_filings`). One row per (rssd_id, period_end), 52 vars,
        USD THOUSANDS. Constant metadata columns added at load: reconstruction_tier=
        'independent', src_vintage='call_report_filings', unit_basis='nominal_usd_thousands'
        (matching luck_core_panel's tier trio; additive metadata, never a value change).
  * `luck_core_panel`         — MODL 1959Q4-1975Q4, DERIVATION-LAYER (their digitized .dta
        -> published schema via their documented 05/06/07 method). One row per
        (bank_id, quarter) == (id_rssd, period_end). Kept as ITS OWN table, NOT unioned
        into luck_equivalent_panel: the schemas do not honestly coincide (100 vs 57 cols;
        failure layer + real twins + CLV pseudo-id vs nominal-only; different honesty
        tiers 'derivation-layer' vs 'independent'). Documented choice per plan §B3.

Sources of truth:
  parquets  Outputs/reconstruction/luck_equivalent_1976_2026.parquet (+ _BUILD_META.json)
            Outputs/reconstruction/luck_core_1959_1975.parquet       (+ _BUILD_META.json)
  spec      Technical/reconstruction_spec/RECONSTRUCTION_SPEC.md (§5, §8, §10)
  gates     Outputs/reconstruction/validation/gate_result_1976_2026.json / _1959_1975.json

Run:
  python 50_reconstruct_luck.py            # load existing parquets -> warehouse tables
  python 50_reconstruct_luck.py --rebuild  # re-run the module builders first (~10 min;
                                           # luck_equivalent scan+derive; luck_core needs
                                           # Inputs/luck_database/qje-repkit.zip)

Single-writer contract: the RW connection is opened only for the CREATE OR REPLACE
step and fails loudly if another process holds the warehouse.
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

# repo-canonical reconstruction module
sys.path.insert(0, str(PROJECT_ROOT))

RECON_DIR = PROJECT_ROOT / "Outputs" / "reconstruction"
LUCK_EQ_PARQUET = RECON_DIR / "luck_equivalent_1976_2026.parquet"
LUCK_EQ_META = RECON_DIR / "luck_equivalent_1976_2026_BUILD_META.json"
LUCK_CORE_PARQUET = RECON_DIR / "luck_core_1959_1975.parquet"
LUCK_CORE_META = RECON_DIR / "luck_core_1959_1975_BUILD_META.json"


def rebuild():
    """Re-run the repo-canonical builders (imports, no subprocess)."""
    from pipeline.reconstruction import build_luck_equivalent as ble
    print("[50] rebuilding luck_equivalent_1976_2026 (scan+derive; warehouse READ-ONLY) ...")
    ble.main(["--stage", "all"])
    from pipeline.reconstruction import build_luck_core as blc
    print("[50] rebuilding luck_core_1959_1975 (repkit .dta -> published schema) ...")
    rc = blc.main()
    if rc not in (0, None):
        raise SystemExit(f"build_luck_core failed with rc={rc}")


def _meta_rows(meta_path: Path, key_candidates=("rows",)) -> int:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    for k in key_candidates:
        if k in meta:
            return int(meta[k])
    # luck_core meta nests row count under output.rows
    return int(meta["output"]["rows"])


def load_tables():
    """Materialize the two warehouse tables (the ONLY write; 31/45 pattern)."""
    for p in (LUCK_EQ_PARQUET, LUCK_EQ_META, LUCK_CORE_PARQUET, LUCK_CORE_META):
        assert p.exists(), f"missing reconstruction artifact: {p} (run with --rebuild?)"

    exp_eq = _meta_rows(LUCK_EQ_META)
    exp_core = _meta_rows(LUCK_CORE_META, key_candidates=())

    con = duckdb.connect(str(DB_PATH))  # RW; fails loudly if another writer is attached
    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE luck_equivalent_panel AS
            SELECT *,
                   'independent'            AS reconstruction_tier,
                   'call_report_filings'    AS src_vintage,
                   'nominal_usd_thousands'  AS unit_basis
            FROM read_parquet('{LUCK_EQ_PARQUET.as_posix()}')
        """)
        n_eq = con.execute("SELECT COUNT(*) FROM luck_equivalent_panel").fetchone()[0]
        assert n_eq == exp_eq, f"luck_equivalent_panel rows {n_eq} != BUILD_META {exp_eq}"
        print(f"[50] luck_equivalent_panel: {n_eq:,} rows (== BUILD_META)")

        con.execute(f"""
            CREATE OR REPLACE TABLE luck_core_panel AS
            SELECT * FROM read_parquet('{LUCK_CORE_PARQUET.as_posix()}')
        """)
        n_core = con.execute("SELECT COUNT(*) FROM luck_core_panel").fetchone()[0]
        assert n_core == exp_core, f"luck_core_panel rows {n_core} != BUILD_META {exp_core}"
        print(f"[50] luck_core_panel: {n_core:,} rows (== BUILD_META)")

        # key-uniqueness guards (the panels' documented grains)
        d1 = con.execute("""SELECT COUNT(*) FROM (SELECT rssd_id, period_end
            FROM luck_equivalent_panel GROUP BY 1,2 HAVING COUNT(*)>1)""").fetchone()[0]
        d2 = con.execute("""SELECT COUNT(*) FROM (SELECT bank_id, quarter
            FROM luck_core_panel GROUP BY 1,2 HAVING COUNT(*)>1)""").fetchone()[0]
        assert d1 == 0 and d2 == 0, f"grain violated: luck_eq dups={d1} luck_core dups={d2}"
    finally:
        con.close()
    return n_eq, n_core


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebuild", action="store_true",
                    help="re-run the pipeline/reconstruction builders before loading")
    args = ap.parse_args()

    elapsed = timer()
    print("=== Phase 50: Luck reconstruction panels -> warehouse ===")
    if args.rebuild:
        rebuild()
    n_eq, n_core = load_tables()
    secs = elapsed()
    log_ingestion("50", f"luck_equivalent_panel {n_eq:,} rows (MODC independent) + "
                        f"luck_core_panel {n_core:,} rows (MODL derivation-layer) "
                        f"materialized from Outputs/reconstruction parquets. {secs:.1f}s")
    print(f"\nPhase 50 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
