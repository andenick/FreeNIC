"""W7 bounded re-export: only the tables changed by W2-W4 of FREENIC_COMPLETENESS_PLAN.

Re-exports ONLY the changed tables to Outputs/parquet/ using the project's own
robust exporter (export_helpers.export_table) on a READ-ONLY DB connection:
  * the 16 W2 tables that gained a row-level `source`/`source_dataset` column,
  * occ_historical (W2 label standardization occ -> occ_historical),
  * robin_panel_base (W4 rename; NEW parquet),
  * freenic_manifest (W3 new metadata table; NEW parquet).
It does NOT touch the billion-row fact tables (call_report_filings, bhcf_filings,
luck_call_reports, fdic_financials) nor any unchanged table.

It also REMOVES the stale Outputs/parquet/robin_panel.parquet because robin_panel
is now a VIEW (views are not exported), superseded by robin_panel_base.parquet.

Row-count parity is asserted for each re-exported parquet vs the live table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import DB_PATH, OUTPUTS_DIR  # noqa: E402
import export_helpers as eh  # noqa: E402

# Changed tables (schema is 'main' for all). robin_panel intentionally absent (now a view).
CHANGED = [
    "branches", "relationships", "transformations", "nic_attributes_ext",
    "nic_entity_identifiers", "institution_attributes", "cdr_unrealized_losses",
    "stress_scenarios", "stress_scenarios_domestic", "stress_scenarios_international",
    "fdic_history", "fdic_sdi_features", "hmda_summary", "ncua_cu_directory",
    "robin_deposits_historical", "robin_deposits_modern",
    "occ_historical",        # W2 label fix
    "robin_panel_base",      # W4 rename (new parquet)
    "freenic_manifest",      # W3 new table (new parquet)
]

# Sort keys (match 12_export_parquet where defined; robin_panel_base keeps old robin_panel key).
SORT_KEYS = {
    "occ_historical": "bank_id, report_date",
    "fdic_sdi_features": "rssd_id, year",
    "robin_panel_base": "bank_id, year",
    "relationships": "rssd_parent, rssd_offspring",
    "transformations": "rssd_successor, dt_trans",
    "ncua_cu_directory": "cu_number",
    "hmda_summary": "activity_year, lei, loan_purpose",
    "nic_entity_identifiers": "rssd_id",
    "nic_attributes_ext": "rssd_id",
    "cdr_unrealized_losses": "rssd_id, period_end",
}


def main() -> None:
    parquet_dir = OUTPUTS_DIR / "parquet"
    temp_dir = OUTPUTS_DIR / "_duckdb_tmp"
    print(f"[W7] read-only re-export of {len(CHANGED)} changed tables -> {parquet_dir}")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    eh.configure_session(con, temp_dir, memory_limit="40GB")

    markers = eh.load_markers(parquet_dir)
    ok = err = 0
    for t in CHANGED:
        live = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        res = eh.export_table(con, "main", t, parquet_dir, SORT_KEYS, markers, force=True)
        markers[t] = res
        eh.save_markers(parquet_dir, markers)
        if res.get("status") != "exported":
            print(f"  !! {t}: status={res.get('status')} {res.get('error','')}")
            err += 1
            continue
        # Verify parquet row count == live table row count.
        pq = parquet_dir / f"{t}.parquet"
        pqn = con.execute(f"SELECT COUNT(*) FROM read_parquet('{str(pq).replace(chr(92),'/')}')").fetchone()[0]
        match = "OK" if pqn == live else "MISMATCH"
        print(f"  {t:34s} live={live:>12,}  parquet={pqn:>12,}  [{match}]")
        if pqn != live:
            err += 1
        else:
            ok += 1
    con.close()

    # Remove stale robin_panel.parquet (robin_panel is now a VIEW).
    stale = parquet_dir / "robin_panel.parquet"
    if stale.exists():
        sz = stale.stat().st_size
        stale.unlink()
        print(f"  removed stale robin_panel.parquet ({sz/1e6:.1f} MB) -- now a view")
        markers.pop("robin_panel", None)
        eh.save_markers(parquet_dir, markers)

    print(f"\n[W7] done: {ok} re-exported+verified, {err} problems.")
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
