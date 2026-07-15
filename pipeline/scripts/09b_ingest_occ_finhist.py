"""Phase 9b: Ingest CLV-published finhist historical call reports into occ_historical.

Source: Inputs/clv_historical_call/historical-call.dta
  (Correia/Luck/Verner "Failing Banks" public historical-call file;
   finhist.com / Harvard Dataverse doi:10.7910/DVN/Q22XR1 / NYFRB historical-call dataset)
  370,977 rows x 82 cols, WIDE, full 1863-1941 span, same OCC source as the Luck TSV
  vintage already loaded under source='occ_historical' (Wave 15A proved penny-exact
  value match + identical bank_id scheme + report_date == call_date).

This loads the FULLER public vintage alongside the existing one under a distinct
source tag so freeNIC becomes the complete public OCC-historical source of record.

Non-destructive & idempotent:
  - Deletes ONLY rows WHERE source='occ_historical_clv' before re-insert.
  - NEVER touches the existing source='occ_historical' rows.
  - Reversible: the whole ingestion is undone by that DELETE.

Schema (LONG, matches occ_historical): bank_id, report_date(VARCHAR YYYY-MM-DD),
  variable_id(VARCHAR, the finhist column name AS-IS), value(DOUBLE), source.

Mirrors 09_ingest_occ.py: pyreadstat -> pandas -> temp parquet -> DuckDB UNPIVOT.
"""

import sys
from pathlib import Path

import pyreadstat

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

DTA_PATH = INPUT_PATHS['occ_clv']
SOURCE_TAG = 'occ_historical_clv'

# Non-numeric / metadata / key columns to EXCLUDE from the unpivot (per Wave 15 plan).
# Everything else in historical-call.dta is a numeric line item -> a variable_id.
SKIP_COLS = {
    'bank_id', 'charter', 'year', 'bank_name', 'call_date', 'is_filled_in',
    'state_abbrev', 'city_name', 'page', 'docpage', 'table', 'row',
    'is_ambiguous', 'bs_merge', 'ok_bs', 'approx_ok_bs',
}


def main():
    elapsed = timer()
    print("=== Phase 9b: OCC Historical (CLV finhist) Ingestion ===")

    if not DTA_PATH.is_file():
        print(f"  ERROR: source not found at {DTA_PATH}")
        sys.exit(1)

    # --- Load the .dta via pyreadstat -> pandas ---
    print(f"  Reading {DTA_PATH} ...")
    df, meta = pyreadstat.read_dta(str(DTA_PATH))
    print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

    # report_date <- call_date (datetime.date) -> 'YYYY-MM-DD' VARCHAR to match table
    df['report_date'] = df['call_date'].map(lambda d: d.isoformat() if d is not None and d == d else None)

    var_cols = [c for c in df.columns if c not in SKIP_COLS and c != 'report_date']
    print(f"  Line-item (numeric) columns to unpivot: {len(var_cols)}")

    # Keep only the keys + line items for the temp parquet (drop string metadata to be safe)
    keep = ['bank_id', 'report_date'] + var_cols
    tmp_dir = OUTPUTS_DIR / "parquet"
    tmp_dir.mkdir(exist_ok=True)
    tmp_parquet = tmp_dir / "_tmp_occ_clv_wide.parquet"
    df[keep].to_parquet(tmp_parquet, index=False)
    print(f"  Wrote temp wide parquet: {tmp_parquet}")

    con = get_db()  # read-write; fails loudly if MCP holds the lock

    # Non-destructive idempotency: clear ONLY this source.
    pre_other = con.execute(
        "SELECT COUNT(*) FROM occ_historical WHERE source='occ_historical'"
    ).fetchone()[0]
    deleted = con.execute(
        "DELETE FROM occ_historical WHERE source=? RETURNING 1", (SOURCE_TAG,)
    ).fetchall()
    print(f"  Cleared {len(deleted):,} prior rows for source='{SOURCE_TAG}'")
    print(f"  (existing source='occ_historical' rows before insert: {pre_other:,})")

    con.execute(
        "CREATE OR REPLACE TEMP TABLE clv_wide AS SELECT * FROM read_parquet(?)",
        [str(tmp_parquet).replace('\\', '/')],
    )

    # UNPIVOT in batches via UNION ALL (mirrors 09); skip NULLs like 09.
    batch_size = 30
    total = 0
    for i in range(0, len(var_cols), batch_size):
        batch = var_cols[i:i + batch_size]
        selects = []
        for col in batch:
            selects.append(f"""
                SELECT
                    CAST(bank_id AS INTEGER) AS bank_id,
                    report_date AS report_date,
                    '{col}' AS variable_id,
                    TRY_CAST("{col}" AS DOUBLE) AS value,
                    '{SOURCE_TAG}' AS source
                FROM clv_wide
                WHERE TRY_CAST("{col}" AS DOUBLE) IS NOT NULL
                  AND report_date IS NOT NULL
            """)
        union_sql = "\nUNION ALL\n".join(selects)
        con.execute(f"""
            INSERT INTO occ_historical (bank_id, report_date, variable_id, value, source)
            {union_sql}
        """)
        now = con.execute(
            "SELECT COUNT(*) FROM occ_historical WHERE source=?", (SOURCE_TAG,)
        ).fetchone()[0]
        print(f"    Batch {i // batch_size + 1}: cols {i+1}-{min(i+batch_size, len(var_cols))}, "
              f"total {SOURCE_TAG}={now:,}")
        total = now

    # --- Summary for the new source ---
    summ = con.execute(f"""
        SELECT COUNT(*), COUNT(DISTINCT bank_id), COUNT(DISTINCT variable_id),
               MIN(report_date), MAX(report_date)
        FROM occ_historical WHERE source='{SOURCE_TAG}'
    """).fetchone()
    has_frb = con.execute(
        f"SELECT COUNT(*) FROM occ_historical WHERE source='{SOURCE_TAG}' AND variable_id='frb_reserve'"
    ).fetchone()[0]
    has_acc = con.execute(
        f"SELECT COUNT(*) FROM occ_historical WHERE source='{SOURCE_TAG}' AND variable_id='acceptances_receivable'"
    ).fetchone()[0]
    post_other = con.execute(
        "SELECT COUNT(*) FROM occ_historical WHERE source='occ_historical'"
    ).fetchone()[0]

    print(f"\n--- Summary (source='{SOURCE_TAG}') ---")
    print(f"  Total observations: {summ[0]:,}")
    print(f"  Unique banks:       {summ[1]:,}")
    print(f"  Unique variables:   {summ[2]:,}")
    print(f"  Date range:         {summ[3]} to {summ[4]}")
    print(f"  frb_reserve obs:    {has_frb:,}")
    print(f"  acceptances_receivable obs: {has_acc:,}")
    print(f"\n  NON-DESTRUCTIVE CHECK: source='occ_historical' rows "
          f"before={pre_other:,} after={post_other:,} "
          f"({'UNCHANGED' if pre_other == post_other else 'CHANGED!!!'})")

    con.close()

    # Clean up temp parquet
    try:
        tmp_parquet.unlink()
    except OSError:
        pass

    secs = elapsed()
    log_ingestion(
        "9b",
        f"OCC Historical CLV (finhist): {summ[0]:,} obs, {summ[1]:,} banks, "
        f"{summ[2]:,} vars, {summ[3]}..{summ[4]}, source='{SOURCE_TAG}'. "
        f"Existing occ_historical untouched ({post_other:,} rows). {secs:.1f}s"
    )
    print(f"\nPhase 9b complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
