"""Phase 52: Validate the reconstruction warehouse integration (B3 gate wrapper).

THIN WRAPPER over the repo-canonical `pipeline/reconstruction` validation artifacts
(campaign FREENIC11_RECONSTRUCTION_20260715). Default mode verifies, READ-ONLY:

  1. The three gate verdict JSONs parse and carry the pre-registered D2 fields
     (gate_result_1976_2026 / _1959_1975 / _finhist under Outputs/reconstruction/validation/).
  2. The warehouse tables (luck_equivalent_panel, luck_core_panel,
     clean_bank_panel_clv_derived) exist and their row counts match the parquet
     BUILD_META sidecars exactly.
  3. Six anchor cells in luck_equivalent_panel match the canonical reconciliation
     parquet (validation/reconciliation_1976_2026.parquet) — the BUILD_META self-smoke
     anchor set, checked THROUGH the warehouse table this time.

`--full` additionally re-runs the era gate harnesses via the module (heavy: rebuilds the
published-ref alignment + reclassifies every cell; the modern gate alone scans ~40M cells).
The harnesses never write to the warehouse (SPEC non-negotiable).

Exit code 0 = all green; 1 = any check failed (prints the failures).
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
VAL_DIR = RECON_DIR / "validation"

GATES = {
    "1976_2026": VAL_DIR / "gate_result_1976_2026.json",
    "1959_1975": VAL_DIR / "gate_result_1959_1975.json",
    "finhist": VAL_DIR / "gate_result_finhist.json",
}
GATE_REQUIRED_FIELDS = ("verdict", "match_share", "unexplained_share", "gate_threshold",
                        "class_counts", "derivable_cells")

TABLES = {  # table -> (BUILD_META path, row-count extractor)
    "luck_equivalent_panel": (RECON_DIR / "luck_equivalent_1976_2026_BUILD_META.json",
                              lambda m: int(m["rows"])),
    "luck_core_panel": (RECON_DIR / "luck_core_1959_1975_BUILD_META.json",
                        lambda m: int(m["output"]["rows"])),
    "clean_bank_panel_clv_derived": (RECON_DIR / "finhist_equivalent_1863_1941_BUILD_META.json",
                                     lambda m: int(m["output"]["rows"])),
}

#: Anchor cells: the luck_equivalent BUILD_META self-smoke set (SPEC §5 unit anchors).
#: Each is verified warehouse-table value == reconciliation-parquet built value (and the
#: reconciliation row must be class EXACT, i.e. == CLV's published value too).
ANCHORS = [
    (852218, "2008-12-31", "assets"),
    (852218, "2008-12-31", "deposits"),
    (480228, "2008-12-31", "equity"),
    (480228, "2008-12-31", "ln_tot"),
    (476810, "2008-12-31", "securities"),
    (852218, "2008-12-31", "time_deposits"),
]


def check_gates(failures: list) -> None:
    for era, path in GATES.items():
        if not path.exists():
            failures.append(f"gate JSON missing: {path}")
            continue
        try:
            g = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            failures.append(f"gate JSON unparseable: {path} ({e})")
            continue
        missing = [f for f in GATE_REQUIRED_FIELDS if f not in g]
        if missing:
            failures.append(f"gate {era}: missing fields {missing}")
            continue
        print(f"  gate {era}: verdict={g['verdict']} match={g['match_share']*100:.4f}% "
              f"unexpl={g['unexplained_share']*100:.4f}% (threshold {g['gate_threshold']})")


def check_tables(con, failures: list) -> None:
    for table, (meta_path, extract) in TABLES.items():
        exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema='main' AND table_name=?", [table]).fetchone()[0]
        if not exists:
            failures.append(f"warehouse table missing: {table} (run 50/51)")
            continue
        if not meta_path.exists():
            failures.append(f"BUILD_META missing for {table}: {meta_path}")
            continue
        exp = extract(json.loads(meta_path.read_text(encoding="utf-8")))
        got = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        ok = got == exp
        if not ok:
            failures.append(f"{table}: rows {got:,} != BUILD_META {exp:,}")
        print(f"  {table}: {got:,} rows vs BUILD_META {exp:,} [{'PASS' if ok else 'FAIL'}]")


def check_anchors(con, failures: list) -> None:
    recon = VAL_DIR / "reconciliation_1976_2026.parquet"
    if not recon.exists():
        failures.append(f"reconciliation parquet missing: {recon}")
        return
    for rssd, pe, var in ANCHORS:
        ref = con.execute(f"""
            SELECT built, published, class
            FROM read_parquet('{recon.as_posix()}')
            WHERE id_rssd = ? AND period_end = ? AND variable = ?""",
            [rssd, pe, var]).fetchone()
        wh = con.execute(
            f'SELECT "{var}" FROM luck_equivalent_panel '
            f"WHERE rssd_id = ? AND period_end = ?", [rssd, pe]).fetchone()
        if not ref or ref[0] is None:
            failures.append(f"anchor {rssd}/{pe}/{var}: absent from reconciliation parquet")
            continue
        if not wh or wh[0] is None:
            failures.append(f"anchor {rssd}/{pe}/{var}: absent from luck_equivalent_panel")
            continue
        ok = (wh[0] == ref[0]) and (ref[2] == "EXACT")
        if not ok:
            failures.append(f"anchor {rssd}/{pe}/{var}: warehouse {wh[0]} vs recon built "
                            f"{ref[0]} (class {ref[2]})")
        print(f"  anchor {var} rssd={rssd} {pe}: warehouse={wh[0]:.0f} recon_built={ref[0]:.0f} "
              f"published={ref[1]:.0f} class={ref[2]} [{'PASS' if ok else 'FAIL'}]")


def run_full_harnesses() -> None:
    """Re-run the era gate harnesses (heavy). Never writes to the warehouse."""
    from pipeline.reconstruction import run_gmatch_modern_real as rg
    print("[52] --full: re-running the canonical modern gate harness ...")
    rg.main()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--full", action="store_true",
                    help="re-run the era gate harnesses before verifying (heavy)")
    args = ap.parse_args()

    elapsed = timer()
    print("=== Phase 52: Reconstruction integration validation ===")
    if args.full:
        run_full_harnesses()

    failures: list = []
    print("\n  1. Gate verdict JSONs")
    check_gates(failures)

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        print("\n  2. Warehouse tables vs BUILD_META")
        check_tables(con, failures)
        print("\n  3. Anchor cells (warehouse vs reconciliation parquet)")
        check_anchors(con, failures)
    finally:
        con.close()

    secs = elapsed()
    if failures:
        print(f"\n--- Phase 52 FAILED ({len(failures)} failure(s)) ---")
        for f in failures:
            print(f"  FAIL: {f}")
        log_ingestion("52", f"reconstruction validation FAILED: {len(failures)} failure(s). "
                            f"{secs:.1f}s")
        return 1
    print("\n--- Phase 52: all reconstruction integration checks PASS ---")
    log_ingestion("52", f"reconstruction validation PASS: 3 gates parsed, 3 tables == "
                        f"BUILD_META, 6/6 anchors. {secs:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
