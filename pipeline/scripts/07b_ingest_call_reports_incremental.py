"""Phase 7b: INCREMENTAL, non-destructive ingest of Chicago Fed Call Reports (SAS XPT).

Extends call_report_filings from 1976-2002Q2 to 1976-2011Q4 by loading only the
quarters not already present. Mirrors 07_ingest_call_reports.py's melt-to-long logic
but is incremental + idempotent and NEVER deletes existing rows.

Key schema differences in newer (2002Q3+) XPT files handled here:
  - Period date lives in RSSD9999 (not DATE) -> fallback chain.
  - Entity id lives in RSSD9001 (not ENTITY) -> entity-column fallback.
  - Extra identifier/aux columns (DATE_SAS, RSSD9999, RSSD9001, RCON9804) are
    excluded from the melted variable set.

Period-end resolution (robust, in order):
  (a) XPT 'DATE' column (YYYYMMDD float) if present;
  (b) XPT 'RSSD9999' column (FFIEC reporting-date mnemonic) if present;
  (c) parse dir name callYYMM -> quarter-end. YY<=30 -> 2000+YY else 1900+YY;
      MM 03->31, 06->30, 09->30, 12->31.

Idempotency: skip a dir if its .xpt filename is already in filing_metadata
(filing_type='CALL', case-insensitive) OR its resolved period_end already exists
in call_report_filings.
"""

import re
import sys
import time
import gc
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS

CALL_DIR = INPUT_PATHS['call_reports']

# Identifier / auxiliary columns that are never call-report variables.
ID_AUX_COLS = {'DATE', 'ENTITY', 'CALL8786', 'DATE_SAS', 'RSSD9999', 'RSSD9001', 'RCON9804'}
# Candidate entity-id columns, in priority order.
ENTITY_CANDIDATES = ['ENTITY', 'RSSD9001']
QUARTER_END_DAY = {'03': '31', '06': '30', '09': '30', '12': '31'}


def parse_schedule_from_name(dirname: str) -> str:
    """call0003-zip -> 0003."""
    match = re.match(r'call(\d{4})', dirname)
    return match.group(1) if match else dirname


def date_float_to_str(date_val) -> str | None:
    """20000331.0 -> '2000-03-31'."""
    if date_val is None:
        return None
    try:
        if np.isnan(date_val):
            return None
    except TypeError:
        return None
    d = str(int(date_val))
    if len(d) == 8:
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return None


def period_from_dirname(dirname: str) -> str | None:
    """callYYMM-zip -> 'YYYY-MM-DD' quarter-end."""
    m = re.match(r'call(\d{2})(\d{2})', dirname)
    if not m:
        return None
    yy, mm = m.group(1), m.group(2)
    if mm not in QUARTER_END_DAY:
        return None
    yy_i = int(yy)
    year = 2000 + yy_i if yy_i <= 30 else 1900 + yy_i
    return f"{year}-{mm}-{QUARTER_END_DAY[mm]}"


def resolve_period_end(df, dirname: str):
    """Return (period_end_str, fallback_tag)."""
    if 'DATE' in df.columns:
        s = df['DATE'].dropna()
        if not s.empty:
            pe = date_float_to_str(s.iloc[0])
            if pe:
                return pe, 'DATE'
    if 'RSSD9999' in df.columns:
        s = df['RSSD9999'].dropna()
        if not s.empty:
            pe = date_float_to_str(s.iloc[0])
            if pe:
                return pe, 'RSSD9999'
    pe = period_from_dirname(dirname)
    if pe:
        return pe, 'dirname'
    return None, 'none'


def already_loaded(con, source_file: str, period_end: str) -> bool:
    """True if this source_file (case-insensitive) or period_end is already in the DB."""
    n_meta = con.execute(
        "SELECT COUNT(*) FROM filing_metadata "
        "WHERE filing_type='CALL' AND LOWER(source_file)=LOWER(?)",
        (source_file,),
    ).fetchone()[0]
    if n_meta > 0:
        return True
    n_rows = con.execute(
        "SELECT 1 FROM call_report_filings WHERE period_end = ? LIMIT 1",
        (period_end,),
    ).fetchone()
    return n_rows is not None


def ingest_one_xpt(con, xpt_path, schedule, dirname):
    """Read one XPT, resolve period, melt to long, insert. Returns (count, period_end, note)."""
    import pyreadstat

    filename = xpt_path.name
    # Some 2002Q3-2006 XPT files are Latin-1 / CP1252 encoded, not UTF-8, and may
    # raise errors OTHER than UnicodeDecodeError (e.g. ReadstatError) on the UTF-8
    # attempt. Retry LATIN1 on ANY read failure (LATIN1 accepts every byte).
    # (W16 scrounger fix 2026-05-30: recovered 8 quarters 2003Q2-2006Q1 that the
    # old UnicodeDecodeError-only fallback wrongly skipped.)
    try:
        df, meta = pyreadstat.read_xport(str(xpt_path))
    except Exception as e_utf8:
        try:
            df, meta = pyreadstat.read_xport(str(xpt_path), encoding='LATIN1')
        except Exception as e_latin1:
            return 0, None, f"ERROR reading (utf8: {e_utf8}; latin1: {e_latin1})"

    if df.empty:
        return 0, None, "empty dataframe"

    period_end, fallback = resolve_period_end(df, dirname)
    if not period_end:
        return 0, None, "no usable date (DATE/RSSD9999/dirname all failed)"

    # Idempotency re-check using the resolved period (filename checked by caller).
    if already_loaded(con, filename, period_end):
        return 0, period_end, f"already loaded (period {period_end} present); fallback={fallback}"

    # Entity column fallback.
    entity_col = next((c for c in ENTITY_CANDIDATES if c in df.columns), None)
    if entity_col is None:
        return 0, period_end, "no entity column (ENTITY/RSSD9001)"

    var_cols = [c for c in df.columns if c not in ID_AUX_COLS]
    numeric_var_cols = [
        c for c in var_cols
        if df[c].dtype in ('float64', 'float32', 'int64', 'int32')
    ]
    if not numeric_var_cols:
        return 0, period_end, "no numeric variable columns"

    df_long = df[[entity_col] + numeric_var_cols].melt(
        id_vars=[entity_col], var_name='variable_id', value_name='value'
    ).dropna(subset=['value'])

    df_long['rssd_id'] = df_long[entity_col].astype(int)
    df_long['period_end'] = period_end
    df_long['schedule'] = schedule
    df_long['source_file'] = filename
    df_insert = df_long[['rssd_id', 'period_end', 'schedule', 'variable_id', 'value', 'source_file']]

    con.execute("""
        INSERT INTO call_report_filings (rssd_id, period_end, schedule, variable_id, value, source_file)
        SELECT * FROM df_insert
    """)
    count = len(df_insert)

    n_entities = df_long['rssd_id'].nunique()
    n_vars = df_long['variable_id'].nunique()
    con.execute("""
        INSERT OR REPLACE INTO filing_metadata
        (filing_type, period_end, source_file, entity_count, variable_count, ingestion_ts)
        VALUES ('CALL', ?, ?, ?, ?, ?)
    """, (period_end, filename, n_entities, n_vars, datetime.now()))

    note = f"loaded (entity={entity_col}, date_fallback={fallback})"
    del df, df_long, df_insert
    gc.collect()
    return count, period_end, note


def main():
    elapsed = timer()
    print("=== Phase 7b: INCREMENTAL Call Reports Ingestion (non-destructive) ===")

    con = get_db()  # read-write

    rows_before = con.execute("SELECT COUNT(*) FROM call_report_filings").fetchone()[0]
    q_before = con.execute("SELECT COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()[0]
    span_before = con.execute("SELECT MIN(period_end), MAX(period_end) FROM call_report_filings").fetchone()
    existing_periods = set(
        r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0])
        for r in con.execute("SELECT DISTINCT period_end FROM call_report_filings").fetchall()
    )
    print(f"BEFORE: {rows_before:,} rows, {q_before} quarters, span {span_before[0]}..{span_before[1]}")

    xpt_dirs = sorted([
        d for d in CALL_DIR.iterdir()
        if d.is_dir() and d.name.startswith('call') and d.name.endswith('-zip')
    ])
    print(f"Found {len(xpt_dirs)} call report directories")

    # Pre-filter: determine new dirs (those not skippable by filename/period).
    todo = []
    skipped_existing = 0
    for d in xpt_dirs:
        xpts = list(d.glob('*.xpt'))
        if not xpts:
            print(f"  SKIP {d.name}: no XPT file")
            continue
        fname = xpts[0].name
        pe_guess = period_from_dirname(d.name)
        meta_hit = con.execute(
            "SELECT COUNT(*) FROM filing_metadata WHERE filing_type='CALL' AND LOWER(source_file)=LOWER(?)",
            (fname,),
        ).fetchone()[0]
        period_hit = pe_guess in existing_periods if pe_guess else False
        if meta_hit > 0 or period_hit:
            skipped_existing += 1
            continue
        todo.append((d, xpts[0]))

    print(f"Already loaded (skipped): {skipped_existing}")
    print(f"New dirs to process:      {len(todo)}")
    for d, _ in todo:
        print(f"    NEW -> {d.name} (period guess {period_from_dirname(d.name)})")

    total_new_rows = 0
    loaded_quarters = []
    skipped_unreadable = []
    start_time = time.time()
    total = len(todo)

    for i, (xpt_dir, xpt_path) in enumerate(todo):
        schedule = parse_schedule_from_name(xpt_dir.name)
        file_start = time.time()
        count, period_end, note = ingest_one_xpt(con, xpt_path, schedule, xpt_dir.name)
        file_time = time.time() - file_start
        total_new_rows += count

        elapsed_so_far = time.time() - start_time
        rate = (i + 1) / elapsed_so_far if elapsed_so_far > 0 else 1
        remaining = (total - i - 1) / rate if rate > 0 else 0

        if count > 0:
            loaded_quarters.append(period_end)
            print(f"  [{i+1}/{total}] {xpt_dir.name} (sch {schedule}): {count:,} obs "
                  f"period={period_end} ({file_time:.1f}s) {note} "
                  f"[new total: {total_new_rows:,}, ETA {remaining/60:.0f}m]")
        else:
            skipped_unreadable.append((xpt_dir.name, xpt_path.name, period_end, note))
            print(f"  [{i+1}/{total}] {xpt_dir.name}: SKIPPED ({note}) period={period_end}")

    # Final verification (post).
    rows_after = con.execute("SELECT COUNT(*) FROM call_report_filings").fetchone()[0]
    q_after = con.execute("SELECT COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()[0]
    span_after = con.execute("SELECT MIN(period_end), MAX(period_end) FROM call_report_filings").fetchone()
    # Non-destructive check: all prior periods still present.
    periods_after = set(
        r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0])
        for r in con.execute("SELECT DISTINCT period_end FROM call_report_filings").fetchall()
    )
    missing_prior = existing_periods - periods_after

    print("\n--- Summary ---")
    print(f"  Rows before: {rows_before:,}")
    print(f"  Rows after:  {rows_after:,}  (delta +{rows_after - rows_before:,})")
    print(f"  Quarters before/after: {q_before} -> {q_after}")
    print(f"  Span before: {span_before[0]}..{span_before[1]}")
    print(f"  Span after:  {span_after[0]}..{span_after[1]}")
    print(f"  New quarters loaded: {len(loaded_quarters)} -> {sorted(loaded_quarters)}")
    print(f"  Skipped/unreadable:  {len(skipped_unreadable)}")
    for nm, fn, pe, note in skipped_unreadable:
        print(f"      {nm} ({fn}) period={pe}: {note}")
    print(f"  NON-DESTRUCTIVE check: prior periods missing after = {len(missing_prior)} "
          f"{'OK' if not missing_prior else sorted(missing_prior)}")

    con.close()

    secs = elapsed()
    log_ingestion(
        "7b",
        f"Incremental Call Reports: +{rows_after - rows_before:,} rows, "
        f"+{len(loaded_quarters)} quarters {sorted(loaded_quarters)}, "
        f"span now {span_after[0]}..{span_after[1]} ({q_after} quarters). "
        f"Skipped existing={skipped_existing}, unreadable={len(skipped_unreadable)}. "
        f"Non-destructive (prior missing={len(missing_prior)}). {secs:.1f}s"
    )
    print(f"\nPhase 7b complete in {secs:.1f}s ({secs/60:.1f} minutes).")


if __name__ == "__main__":
    main()
