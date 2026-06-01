"""Phase 7e: INCREMENTAL, non-destructive ingest of FFIEC CDR Public bulk Call Reports
(tab-delimited Single-Period ZIPs acquired by 07d_acquire_cdr_call_bulk.py).

Closes the post-2011 gap in call_report_filings: extends from 1976Q1-2011Q4 (144
quarters) toward 2012Q1-2025Q4. Mirrors 07b's melt-to-long logic and is incremental +
idempotent: a reporting period already present in call_report_filings is skipped, so a
partial/interrupted run resumes cleanly on re-run.

CDR tab-delimited layout (verified on 2022Q4 ZIP):
  - One ZIP per reporting period; ~49 'Schedule XX' .txt files + a POR (entity directory)
    + Readme. Each .txt is tab-delimited, double-quote quoted.
  - Column 0 = "IDRSSD" (the RSSD id).  Remaining columns are MDRM codes (RCON*, RCFD*,
    RIAD*, RCFN*, ...) plus some TEXT*/RSSD9*/non-financial columns.
  - Row 1 = header (MDRM codes); ROW 2 = a human-readable DESCRIPTION row (skip it);
    data rows start at row 3.

Convention match with the existing 144 quarters (Chicago Fed source):
  - `schedule` = the 4-char YYMM period tag (one per quarter), NOT the RCFD schedule name.
    (The existing table has exactly 144 distinct schedule values = 144 quarters; the
    RCFD-schedule grouping is preserved inside the MDRM prefix of `variable_id`.)
  - `variable_id` = the MDRM code (e.g. RCFD2170). `value` = DOUBLE.

Filtering: keep only MDRM-named columns whose value is non-empty, not '.', and parses as
a float. Non-numeric TEXT*/identifier columns and 'CONF' confidential cells are dropped.
Within a period a (rssd_id, variable_id) is de-duplicated (first non-null wins) — the
same MDRM can appear in 'RCFD' and a split-file variant; (rssd, period, schedule,
variable) stays unique because schedule is constant per period.

NO values fabricated. A ZIP that cannot be opened is logged and skipped (loader resumes).
"""
import csv
import gc
import io
import re
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS  # noqa: E402

RAW = INPUT_PATHS['cdr_call_bulk']

# MDRM financial-variable column codes: 4-char prefix (RCON/RCFD/RIAD/RCFN/...) + 4 chars.
MDRM = re.compile(r'^(RCON|RCFD|RIAD|RCFN|RCOA|RCOB|RCFW|RCOW|RCEW|RCFA|RCFC|RCOC|RCFY|RCOY|RCFE|RCOE)[A-Z0-9]{4}$')

# CDR Python engine occasionally hits very long quoted narrative lines; lift the limit.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def period_from_zipname(name: str) -> str | None:
    """call_single_20221231.zip -> '2022-12-31'."""
    m = re.search(r'call_single_(\d{4})(\d{2})(\d{2})\.zip$', name)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def schedule_tag(period_end: str) -> str:
    """'2022-12-31' -> '2212' (YYMM period tag, matching the existing 144 quarters)."""
    y, m, _ = period_end.split('-')
    return f"{y[2:]}{m}"


def parse_zip_to_long(zip_path: Path, period_end: str) -> pd.DataFrame:
    """Read every Schedule .txt, melt MDRM columns to long, return deduped DataFrame."""
    sched_tag = schedule_tag(period_end)
    frames = []
    with zipfile.ZipFile(zip_path) as z:
        sched_files = [n for n in z.namelist()
                       if 'Schedule' in n and n.lower().endswith('.txt')]
        for n in sched_files:
            with z.open(n) as f:
                rdr = csv.reader(io.TextIOWrapper(f, encoding='latin-1'),
                                 delimiter='\t', quotechar='"')
                try:
                    header = [h.strip().strip('"') for h in next(rdr)]
                    next(rdr)  # skip the human-readable description row
                except StopIteration:
                    continue
                mdrm_idx = [(i, c) for i, c in enumerate(header) if MDRM.match(c)]
                if not mdrm_idx:
                    continue
                rids, vids, vals = [], [], []
                for row in rdr:
                    if not row:
                        continue
                    rid = row[0].strip().strip('"')
                    if not rid.isdigit():
                        continue
                    rid_i = int(rid)
                    for i, code in mdrm_idx:
                        if i >= len(row):
                            continue
                        v = row[i].strip()
                        if v == '' or v == '.':
                            continue
                        try:
                            fv = float(v)
                        except ValueError:
                            continue
                        rids.append(rid_i)
                        vids.append(code)
                        vals.append(fv)
                if rids:
                    frames.append(pd.DataFrame(
                        {'rssd_id': rids, 'variable_id': vids, 'value': vals}))
    if not frames:
        return pd.DataFrame(columns=['rssd_id', 'period_end', 'schedule',
                                     'variable_id', 'value', 'source_file'])
    df = pd.concat(frames, ignore_index=True)
    # De-dup (rssd_id, variable_id): same MDRM can recur across split files; first wins.
    df = df.drop_duplicates(subset=['rssd_id', 'variable_id'], keep='first')
    df['period_end'] = period_end
    df['schedule'] = sched_tag
    df['source_file'] = zip_path.name
    return df[['rssd_id', 'period_end', 'schedule', 'variable_id', 'value', 'source_file']]


def main() -> None:
    elapsed = timer()
    print("=== Phase 7e: INCREMENTAL CDR Call Reports Ingestion (non-destructive) ===")

    con = get_db()  # read-write
    rows_before = con.execute("SELECT COUNT(*) FROM call_report_filings").fetchone()[0]
    q_before = con.execute("SELECT COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()[0]
    span_before = con.execute("SELECT MIN(period_end), MAX(period_end) FROM call_report_filings").fetchone()
    existing_periods = set(
        (r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]))
        for r in con.execute("SELECT DISTINCT period_end FROM call_report_filings").fetchall()
    )
    print(f"BEFORE: {rows_before:,} rows, {q_before} quarters, span {span_before[0]}..{span_before[1]}")

    zips = sorted(RAW.glob("call_single_*.zip"))
    print(f"Found {len(zips)} CDR ZIP(s) in {RAW}")

    todo = []
    skipped_existing = []
    for zp in zips:
        pe = period_from_zipname(zp.name)
        if not pe:
            print(f"  SKIP {zp.name}: unparseable name")
            continue
        if pe in existing_periods:
            skipped_existing.append(pe)
            continue
        todo.append((zp, pe))

    print(f"Already loaded (skipped): {len(skipped_existing)}")
    print(f"New periods to process:   {len(todo)} -> {[pe for _, pe in todo]}")

    total_new_rows = 0
    loaded_quarters = []
    failed = []
    start = time.time()

    for i, (zp, pe) in enumerate(todo):
        t0 = time.time()
        try:
            df_insert = parse_zip_to_long(zp, pe)
        except Exception as e:
            failed.append((zp.name, pe, f"{type(e).__name__}: {str(e)[:90]}"))
            print(f"  [{i+1}/{len(todo)}] {zp.name}: FAILED {type(e).__name__}: {str(e)[:90]}")
            continue
        if df_insert.empty:
            failed.append((zp.name, pe, "no numeric MDRM rows parsed"))
            print(f"  [{i+1}/{len(todo)}] {zp.name}: SKIPPED (no rows) period={pe}")
            continue

        con.register('df_insert', df_insert)
        con.execute("""
            INSERT INTO call_report_filings (rssd_id, period_end, schedule, variable_id, value, source_file)
            SELECT rssd_id, period_end, schedule, variable_id, value, source_file FROM df_insert
        """)
        con.unregister('df_insert')

        n = len(df_insert)
        total_new_rows += n
        loaded_quarters.append(pe)
        n_ent = df_insert['rssd_id'].nunique()
        n_var = df_insert['variable_id'].nunique()
        try:
            con.execute("""
                INSERT OR REPLACE INTO filing_metadata
                (filing_type, period_end, source_file, entity_count, variable_count, ingestion_ts)
                VALUES ('CALL', ?, ?, ?, ?, ?)
            """, (pe, zp.name, n_ent, n_var, datetime.now()))
        except Exception:
            pass  # filing_metadata is auxiliary; never fail the ingest on it

        dt = time.time() - t0
        rate = (i + 1) / (time.time() - start)
        eta = (len(todo) - i - 1) / rate / 60 if rate else 0
        print(f"  [{i+1}/{len(todo)}] {pe}: {n:,} obs, {n_ent:,} banks, {n_var} vars "
              f"({dt:.1f}s) [new total {total_new_rows:,}, ETA {eta:.0f}m]")
        del df_insert
        gc.collect()

    rows_after = con.execute("SELECT COUNT(*) FROM call_report_filings").fetchone()[0]
    q_after = con.execute("SELECT COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()[0]
    span_after = con.execute("SELECT MIN(period_end), MAX(period_end) FROM call_report_filings").fetchone()
    periods_after = set(
        (r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]))
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
    print(f"  Failed/empty: {len(failed)}")
    for nm, pe, note in failed:
        print(f"      {nm} period={pe}: {note}")
    print(f"  NON-DESTRUCTIVE check: prior periods missing after = {len(missing_prior)} "
          f"{'OK' if not missing_prior else sorted(missing_prior)}")
    con.close()

    secs = elapsed()
    log_ingestion(
        "7e",
        f"CDR post-2011 Call Reports: +{rows_after - rows_before:,} rows, "
        f"+{len(loaded_quarters)} quarters {sorted(loaded_quarters)}, "
        f"span now {span_after[0]}..{span_after[1]} ({q_after} quarters). "
        f"Skipped existing={len(skipped_existing)}, failed={len(failed)}. "
        f"Non-destructive (prior missing={len(missing_prior)}). {secs:.1f}s"
    )
    print(f"\nPhase 7e complete in {secs:.1f}s ({secs/60:.1f} min).")


if __name__ == "__main__":
    main()
