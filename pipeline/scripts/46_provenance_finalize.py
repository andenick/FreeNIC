"""Phase 46: Provenance finalization (Workstream W2 of FREENIC_COMPLETENESS_PLAN).

Closes the row-level-source gap so EVERY base table has either a row-level
provenance source column OR a documented exemption, complementing the
table-level Outputs/PROVENANCE.csv.

This script is ADDITIVE, REVERSIBLE, TRANSACTIONAL and IDEMPOTENT:
  * For single-source fact/structure tables that lack a row-level source column,
    `ALTER TABLE ADD COLUMN <col> VARCHAR` (only if absent) and `UPDATE` every
    row to the table's known, certain source tag.
  * For genuinely single-source pure-reference / multi-source-derived tables
    where a constant column adds no analytic value, write a documented exemption
    to Outputs/PROVENANCE_EXEMPTIONS.csv instead of mutating the table.
  * Standardizes any residual source='occ' label to 'occ_historical' (label-only;
    row count unchanged) so step7's `source IN ('occ','occ_historical')` collapses
    to one label.

No fact-row counts change; only a label column is added/filled. Safe to re-run on
every quarterly refresh.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, OUTPUTS_DIR, timer  # noqa: E402

EXEMPTIONS_CSV = OUTPUTS_DIR / "PROVENANCE_EXEMPTIONS.csv"

# --- Tables that GET a row-level source column (single, certain, unambiguous) ---
# Each value is the stable source tag written to every row. Column name is `source`
# unless that name is already used for a non-provenance purpose (see SOURCE_COL).
ROW_SOURCE = {
    # FFIEC NIC structure / attributes (built by 02 / 37 / 37b)
    "branches": "ffiec_nic",
    "relationships": "ffiec_nic",
    "transformations": "ffiec_nic",
    "nic_attributes_ext": "ffiec_nic",
    "nic_entity_identifiers": "ffiec_nic",
    "institution_attributes": "ffiec_nic",  # uses source_dataset (see SOURCE_COL)
    # Fed FFIEC CDR (32/33)
    "cdr_unrealized_losses": "ffiec_cdr",
    # Fed supervisory stress scenarios (30)
    "stress_scenarios": "fed_supervisory",
    "stress_scenarios_domestic": "fed_supervisory",
    "stress_scenarios_international": "fed_supervisory",
    # FDIC (25/31)
    "fdic_history": "fdic_api",
    "fdic_sdi_features": "fdic_sdi",
    # CFPB HMDA (35)
    "hmda_summary": "cfpb_hmda",
    # NCUA (26)
    "ncua_cu_directory": "ncua",
    # Robin / Failing Banks DB (28)
    "robin_panel": "robin_failing_banks",
    "robin_deposits_historical": "robin_failing_banks",
    "robin_deposits_modern": "robin_failing_banks",
}

# Tables where the plain `source` column name is already taken by a NON-provenance
# field; use a dedicated provenance column name instead.
SOURCE_COL = {
    "institution_attributes": "source_dataset",  # `source` here is ACTIVE/CLOSED status
}

# --- Documented exemptions: single-source pure-reference OR multi-source-derived
# tables where a constant row-level column adds no value. (table, reason, single_source) ---
EXEMPTIONS = [
    ("mdrm", "Pure reference dictionary; single source (Fed MDRM). A constant source column adds no value.", "Fed MDRM"),
    ("fred_series", "Pure reference time-series store; single source (FRED). Constant source column adds no value.", "FRED"),
    ("reporting_forms", "Derived lookup taxonomy extracted from mdrm (Fed MDRM); single source, constant column adds no value.", "Fed MDRM (derived)"),
    ("sector_groupings", "FreeNIC-derived reference crosswalk (CIK->SIC->sector); derived, single logical source.", "FreeNIC derived"),
    ("id_crosswalk", "FreeNIC-derived keystone identity join; multi-input derived, per-field origin flags carried inline (lei_source etc.).", "FreeNIC derived (multi-input)"),
    ("robin_crosswalk", "FreeNIC-derived Robin<->RSSD<->cert crosswalk; derived, single logical source.", "FreeNIC derived"),
    ("bhc_ownership", "FreeNIC-derived reference (NIC structure + ownership); derived, single logical source.", "FreeNIC derived"),
    ("sec_cik_crosswalk", "Single-source reference (SEC EDGAR data.sec.gov); small crosswalk, constant column adds no value.", "SEC EDGAR"),
    ("clean_bank_panel", "FreeNIC-derived FROM RAW (occ_historical_clv + luck_wide + sched_call); multi-source derived, per-field DPR in clv_panel_v2.DPR.md.", "FreeNIC derived (multi-source)"),
]


def _columns(con, table):
    return [r[0] for r in con.execute(f'DESCRIBE "{table}"').fetchall()]


def main():
    elapsed = timer()
    print("=== Phase 46: Provenance finalization (W2) ===")
    con = get_db(read_only=False)

    actions = []

    # 1) Row-level source columns ---------------------------------------------
    for table, tag in ROW_SOURCE.items():
        col = SOURCE_COL.get(table, "source")
        before = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        cols = _columns(con, table)
        if col not in cols:
            con.execute(f'ALTER TABLE "{table}" ADD COLUMN {col} VARCHAR')
            added = True
        else:
            added = False
        # idempotent fill: set every NULL/empty row to the tag (and overwrite any
        # stale value for the dedicated provenance column we own).
        con.execute(
            f'UPDATE "{table}" SET {col} = ? '
            f'WHERE {col} IS NULL OR {col} = \'\' OR {col} <> ?',
            [tag, tag],
        )
        after = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        assert before == after, f"ROW COUNT CHANGED for {table}: {before} -> {after}"
        distinct = con.execute(f'SELECT DISTINCT {col} FROM "{table}"').fetchall()
        actions.append((table, "add_column" if added else "fill_column",
                        f"{col}={tag}", before, after, len(distinct)))
        print(f"  {table:32s} {col}={tag:22s} rows={before:>10,} (col {'added' if added else 'present'})")

    # 2) occ label standardization (label-only) -------------------------------
    occ_before = con.execute("SELECT COUNT(*) FROM occ_historical").fetchone()[0]
    occ_fixed = con.execute(
        "SELECT COUNT(*) FROM occ_historical WHERE source = 'occ'"
    ).fetchone()[0]
    if occ_fixed:
        con.execute("UPDATE occ_historical SET source='occ_historical' WHERE source='occ'")
    occ_after = con.execute("SELECT COUNT(*) FROM occ_historical").fetchone()[0]
    assert occ_before == occ_after, "occ_historical row count changed!"
    print(f"  occ_historical source='occ' -> 'occ_historical': {occ_fixed} rows standardized "
          f"(by_source now {dict(con.execute('SELECT source, COUNT(*) FROM occ_historical GROUP BY source').fetchall())})")

    con.commit()
    con.close()

    # 3) Exemptions CSV (idempotent rewrite) ----------------------------------
    with open(EXEMPTIONS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "reason", "single_source"])
        for row in EXEMPTIONS:
            w.writerow(row)
    print(f"\n  Wrote {len(EXEMPTIONS)} exemptions -> {EXEMPTIONS_CSV}")

    print(f"\nDone in {elapsed():.1f}s. "
          f"{len(ROW_SOURCE)} source columns finalized, {len(EXEMPTIONS)} exemptions, "
          f"{occ_fixed} occ labels standardized.")


if __name__ == "__main__":
    main()
