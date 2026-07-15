"""Phase 26: Ingest NCUA 5300 Credit-Union Call Reports (FreeNIC campaign C3).

=====================================================================
SCOPE EXPANSION -- READ THIS:
  NCUA regulates CREDIT UNIONS. This source EXPANDS FreeNIC beyond
  FDIC-insured depositories and bank holding companies (BHCs). Credit
  unions are a DISTINCT institution universe keyed by NCUA CU_NUMBER
  (NOT by RSSD or FDIC cert -- though FOICU carries an RSSD column where
  one exists). Treat ncua_5300 / ncua_cu_directory as a separate, additive
  layer; do NOT union them with bank tables on identifier columns.
=====================================================================

Source: NCUA Credit Union / Corporate Call Report (5300) quarterly bulk data.
  https://ncua.gov/analysis/credit-union-corporate-call-report-data
Input ZIP (pre-downloaded): Inputs/ncua_5300/call-report-data-YYYY-MM.zip

Structure (inspected before parsing):
  * Comma-delimited, quoted header row, CRLF line endings, latin-1-safe.
  * FS220.txt + FS220A.txt .. FS220S.txt are WIDE financial schedules:
      first columns are identifiers (CU_NUMBER, CYCLE_DATE, JOIN_NUMBER,
      sometimes UPDATE_DATE), then NCUA Account codes (ACCT_010, ACCT_PG0001,
      ...) plus a handful of TEXT columns (e.g. Board*/CurMem* minority-status
      flags in FS220S). One row per credit union.
  * FOICU.txt is the credit-union directory (CU_NUMBER, CU_NAME, STATE,
      CharterState, RSSD, ...).

Melt strategy (faithful transcription only -- no fabricated values):
  For each FS220* schedule we load the wide table, then for every column that
  is NOT a known identifier we attempt TRY_CAST(value AS DOUBLE). A column is
  kept only if at least one non-null numeric value parses; purely text /
  identifier columns are skipped. The kept columns are melted to long:
      (cu_number, period_end, schedule, account_code, value, source_file)
  Dedup on (cu_number, schedule, account_code) -- keep one row per cell.

period_end is derived from the ZIP name (2024-12 -> 2024-12-31).
Idempotent: if the period is already loaded for a table, the load is skipped.

Tables created here (CREATE TABLE IF NOT EXISTS -- not in 00_setup):
  ncua_5300         (cu_number INT, period_end DATE, schedule VARCHAR,
                     account_code VARCHAR, value DOUBLE, source_file VARCHAR)
  ncua_cu_directory (cu_number INT, period_end DATE, cu_name VARCHAR,
                     charter_state VARCHAR, state VARCHAR, rssd INTEGER)

FOLLOW-UP (documented, intentionally NOT done here so existing gates stay green):
  ncua_5300 / ncua_cu_directory are additive artifacts. Wiring them into
  00_setup.py / 12_export_parquet.py / 13_validate.py / 20_build_crosswalks.py
  is a deliberate follow-up; this script keeps 13_validate.py at 8/8 and
  pytest at 194 passed. Parquet is exported directly by this script.
"""

import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

# Full call-report history (1994Q1..present) ships under THREE filename patterns:
#   * modern     call-report-data-YYYY-MM.zip   (2016+, lowercase)
#   * transition Call-Report-Data-YYYY-MM.zip   (2015-06/09/12, TitleCase)
#   * historical QCRYYYYMM.zip / .Zip           (1994-03 .. 2015-03, no dash)
#   * special    5300Data0613Final.zip          (== 2013 Q2 / June 2013)
# We therefore discover ALL *.zip (any case) and rely on period_end_from_zip to
# recognise the pattern. A literal "call-report-data-*.zip" glob silently dropped
# 85 of 128 zips (everything pre-2016) -- the root cause of the 2022+-only history.

# AcctDesc filename drift (account-description dictionary, NOT loaded here -- this
# script melts FS220 by raw account_code; descriptions are a separate dictionary
# step). For any future loader, the file is named, by era:
#   Acct_Des.txt  (1994) -> Acct_Desc.txt (2000) -> AcctDesc.txt (2012+).

# Identifier / metadata columns that must NEVER be melted as account values,
# even if they happen to parse as numeric.
#   ACCT_PG0001 is FS220S's page/program CODE (not a financial account); it parses
#   as a huge bogus integer (~1.16e16) and would otherwise leak in as a value —
#   root-caused in the 2026-06-07 DQ audit (Step 9). Excluding it here makes the
#   exclusion permanent across all quarters instead of a one-off post-load DELETE.
#   ERRORS / USER_ID are bookkeeping columns in old FS220/FS220A (1994-2000); ERRORS
#   is numeric and would otherwise leak in as a bogus account_code='Errors'.
ID_COLS = {
    "CU_NUMBER", "CYCLE_DATE", "JOIN_NUMBER", "UPDATE_DATE", "RSSD",
    "ACCT_PG0001", "ERRORS", "USER_ID",
}

# Parquet export options (mirror export_helpers.COMPRESSION = ZSTD).
PARQUET_OPTS = "(FORMAT PARQUET, COMPRESSION ZSTD)"


def period_end_from_zip(zip_path: Path) -> str:
    """Derive the quarter-end date from any of the three NCUA zip name patterns.

    Examples:
      call-report-data-2024-12.zip -> 2024-12-31   (modern, dash)
      Call-Report-Data-2015-06.zip -> 2015-06-30   (transition, dash)
      QCR199403.zip                -> 1994-03-31   (historical, no dash)
      QCR201006.Zip                -> 2010-06-30   (historical, .Zip)
      5300Data0613Final.zip        -> 2013-06-30   (special June-2013 file)
    """
    name = zip_path.name
    # Special-case the one-off June-2013 final file (MMYY = 06/13).
    if re.match(r"5300Data0613Final", name, re.IGNORECASE):
        year, month = 2013, 6
    # Dashed patterns: call-report-data-YYYY-MM / Call-Report-Data-YYYY-MM.
    elif (m := re.search(r"(\d{4})-(\d{2})", name)):
        year, month = int(m.group(1)), int(m.group(2))
    # Historical: QCRYYYYMM (no dash), case-insensitive (.zip or .Zip).
    elif (m := re.match(r"QCR(\d{4})(\d{2})", name, re.IGNORECASE)):
        year, month = int(m.group(1)), int(m.group(2))
    else:
        raise ValueError(f"Cannot parse period from zip name: {name}")
    # 5300 reports are quarter-end; map the period month to its last day.
    last_day = {3: 31, 6: 30, 9: 30, 12: 31}.get(month)
    if last_day is None:
        raise ValueError(f"Unexpected (non-quarter-end) month {month:02d} in {zip_path.name}")
    return f"{year:04d}-{month:02d}-{last_day:02d}"


def list_fs220_members(zf: zipfile.ZipFile):
    """Return FS220.txt and FS220<suffix> schedule members present in the zip.

    Suffix is zero-or-more letters ([A-Z]*) so multi-letter schedules are kept --
    notably FS220CUSO.txt (real CUSO data, ~2008-2015). The old single-letter
    pattern (FS220[A-Z]?) silently dropped FS220CUSO entirely.
    """
    members = []
    for name in zf.namelist():
        stem = Path(name).name
        if re.fullmatch(r"FS220[A-Z]*\.txt", stem, re.IGNORECASE):
            members.append(name)
    return sorted(members)


def schedule_name(member: str) -> str:
    """'.../FS220A.txt' -> 'FS220A'; '.../FS220.txt' -> 'FS220'."""
    return Path(member).stem.upper()


def _extract_as_utf8(zf, member, tmp_dir):
    """Extract a zip member, transcoding latin-1 bytes -> UTF-8 on disk.

    latin-1 decode is a total 1:1 byte->codepoint map (never raises), so every
    original byte is preserved; re-encoding to UTF-8 gives DuckDB a file its
    reader accepts without any data loss. Returns the output Path.
    """
    out_path = tmp_dir / Path(member).name
    with zf.open(member) as src:
        raw = src.read()
    text = raw.decode("latin-1")
    with open(out_path, "w", encoding="utf-8", newline="") as dst:
        dst.write(text)
    return out_path


def load_wide(con, csv_path: str, view_name: str, names=None):
    """Load one FS220* schedule as an all-VARCHAR wide temp table.

    all_varchar=true keeps every cell as text so we can decide numeric-ness
    column-by-column ourselves (faithful: no silent type coercion at read).

    `names` (optional): explicit column-name list for a HEADERLESS file. When
    supplied we read with header=false and pin these names positionally, so the
    first physical row is treated as DATA (not a header). Used only for the rare
    headerless schedule file, where the names are BORROWED from a same-schedule
    sibling of identical width (see _borrow_header_names) -- not fabricated.
    """
    if names is not None:
        names_sql = "[" + ", ".join("'" + n.replace("'", "''") + "'" for n in names) + "]"
        header_clause = f"header=false, names={names_sql},"
    else:
        header_clause = "header=true,"
    # strict_mode=false: some quarters' text-heavy schedules (e.g. FS220D, which
    # carries CEO/preparer names, phones, URLs) contain RFC-noncompliant quoting
    # that defeats DuckDB's strict dialect sniffer. Relaxing strict mode lets the
    # well-formed structure parse; because we keep ONLY numeric columns via
    # per-column TRY_CAST downstream, any cell shifted by a malformed row simply
    # fails the cast and is dropped (no fabrication). max_line_size guards the
    # widest rows. delim/quote stay pinned so columns are still by-name.
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE {view_name} AS
        SELECT * FROM read_csv('{csv_path}',
            delim=',', quote='"', {header_clause}
            all_varchar=true, ignore_errors=false,
            strict_mode=false, max_line_size=10000000,
            parallel=false, null_padding=true)
    """)


# Cache for borrowed headers: (schedule, ncols) -> [names] or None.
_BORROWED_HEADER_CACHE = {}


def _borrow_header_names(sched: str, ncols: int):
    """Recover column names for a HEADERLESS schedule file by borrowing them from
    a same-schedule sibling zip whose header is intact AND has the identical
    column count -> a positional account-code map.

    Observed need: QCR199609.zip/FS220B.txt ships with no header row (the first
    physical line is data: '13,9/30/96 0:00:00,...'). The bracketing quarters
    QCR199606 and QCR199612 both carry an intact 209-column FS220B header that is
    byte-identical to each other, so the positional account codes are stable and
    borrowing is an evidenced reconstruction, not fabrication. Returns the name
    list (containing CU_NUMBER) or None if no matching-width sibling is found.
    """
    import csv
    import io

    key = (sched, ncols)
    if key in _BORROWED_HEADER_CACHE:
        return _BORROWED_HEADER_CACHE[key]

    ncua_dir = INPUT_PATHS["ncua"]
    result = None
    for zp in sorted(p for p in ncua_dir.iterdir()
                     if p.is_file() and p.suffix.lower() == ".zip"):
        try:
            with zipfile.ZipFile(zp) as zf:
                member = next((n for n in zf.namelist()
                               if Path(n).stem.upper() == sched), None)
                if member is None:
                    continue
                raw = zf.read(member).decode("latin-1")
                first_line = raw.split("\n", 1)[0]
                if "CU_NUMBER" not in first_line.upper():
                    continue  # this sibling is also headerless -- keep looking
                cand = next(csv.reader(io.StringIO(first_line)))
                if len(cand) == ncols:
                    result = cand
                    break
        except Exception:
            continue

    _BORROWED_HEADER_CACHE[key] = result
    return result


def numeric_columns(con, view_name: str, cols):
    """Return columns (excluding ID_COLS) that have >=1 parseable FINITE numeric
    value. isfinite() excludes NaN/Inf so a text/name column whose stray value
    happens to read as 'Inf'/'NaN' (e.g. FS220D Preparer_F / CEO_M, FS220CUSO
    CU_Name) is not mistaken for a financial column -- non-finite is never a
    valid 5300 value."""
    kept = []
    for col in cols:
        if col.upper() in ID_COLS:
            continue
        n = con.execute(
            f'SELECT COUNT(*) FROM {view_name} '
            f'WHERE isfinite(TRY_CAST("{col}" AS DOUBLE))'
        ).fetchone()[0]
        if n > 0:
            kept.append(col)
    return kept


def melt_schedule(con, zf, member, tmp_dir, period_end, sched):
    """Extract one FS220* schedule from the zip, melt numeric cols to long.

    Returns rows inserted into ncua_5300 for this schedule.
    """
    # Extract the member to a temp file (DuckDB reads from disk, not the zip).
    # NCUA files are not consistently UTF-8/latin-1 (FS220D carries stray bytes
    # DuckDB's latin-1 reader rejects). Transcode bytes latin-1 -> UTF-8 in
    # Python (latin-1 decode never fails: it is a 1:1 byte->codepoint map), which
    # preserves every byte faithfully and yields a clean UTF-8 file for DuckDB.
    out_path = _extract_as_utf8(zf, member, tmp_dir)
    csv_path = str(out_path).replace("\\", "/")

    view = "ncua_wide"
    load_wide(con, csv_path, view)
    cols = [r[0] for r in con.execute(f"DESCRIBE {view}").fetchall()]

    if "CU_NUMBER" not in [c.upper() for c in cols]:
        # Headerless file: the first data row was consumed as the header. Recover
        # by borrowing column names from a same-schedule, same-width sibling that
        # has an intact header (positional account-code map -- evidenced, not
        # fabricated). Then re-read with header=false + those names.
        borrowed = _borrow_header_names(sched, len(cols))
        if borrowed is None or "CU_NUMBER" not in [c.upper() for c in borrowed]:
            raise ValueError(
                f"{sched}: headerless and no matching-width sibling header found "
                f"(ncols={len(cols)}; first row: {cols[:5]})"
            )
        print(f"    {sched}: HEADERLESS in {Path(member).name} -> borrowed "
              f"{len(borrowed)}-col header from sibling (positional account-code map)")
        load_wide(con, csv_path, view, names=borrowed)
        cols = [r[0] for r in con.execute(f"DESCRIBE {view}").fetchall()]
    # Resolve the actual CU_NUMBER column name (case-preserving).
    cu_col = next(c for c in cols if c.upper() == "CU_NUMBER")

    value_cols = numeric_columns(con, view, cols)
    skipped = [c for c in cols if c not in value_cols and c.upper() not in ID_COLS]

    inserted_before = con.execute("SELECT COUNT(*) FROM ncua_5300").fetchone()[0]
    src_file = Path(member).name

    # UNPIVOT in column batches (UNION ALL of one SELECT per kept column),
    # then dedup on (cu_number, schedule, account_code) via ROW_NUMBER.
    batch_size = 40
    for i in range(0, len(value_cols), batch_size):
        batch = value_cols[i:i + batch_size]
        selects = []
        for col in batch:
            selects.append(f"""
                SELECT
                    TRY_CAST("{cu_col}" AS INTEGER)        AS cu_number,
                    DATE '{period_end}'                    AS period_end,
                    '{sched}'                              AS schedule,
                    '{col}'                                AS account_code,
                    TRY_CAST("{col}" AS DOUBLE)            AS value,
                    '{src_file}'                           AS source_file
                FROM {view}
                WHERE TRY_CAST("{cu_col}" AS INTEGER) IS NOT NULL
                  AND isfinite(TRY_CAST("{col}" AS DOUBLE))
            """)
        union_sql = "\nUNION ALL\n".join(selects)
        con.execute(f"""
            INSERT INTO ncua_5300
            SELECT cu_number, period_end, schedule, account_code, value, source_file
            FROM (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY cu_number, schedule, account_code
                    ORDER BY value
                ) AS rn
                FROM ({union_sql})
            ) WHERE rn = 1
        """)

    inserted = con.execute("SELECT COUNT(*) FROM ncua_5300").fetchone()[0] - inserted_before
    con.execute(f"DROP TABLE IF EXISTS {view}")
    con.commit()  # commit per schedule -> bounded WAL, resilient to interruption
    out_path.unlink(missing_ok=True)
    print(f"    {sched}: {len(value_cols)} numeric cols kept, "
          f"{len(skipped)} text/id cols skipped, +{inserted:,} rows")
    return inserted


def load_directory(con, zf, member, tmp_dir, period_end):
    """Load FOICU.txt into ncua_cu_directory for this period."""
    out_path = _extract_as_utf8(zf, member, tmp_dir)
    csv_path = str(out_path).replace("\\", "/")

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE foicu_wide AS
        SELECT * FROM read_csv('{csv_path}',
            delim=',', quote='"', header=true,
            all_varchar=true, ignore_errors=false,
            strict_mode=false, max_line_size=10000000,
            parallel=false, null_padding=true)
    """)
    cols = {c[0].upper(): c[0] for c in con.execute("DESCRIBE foicu_wide").fetchall()}

    def colref(name):
        real = cols.get(name)
        return f'"{real}"' if real else "NULL"

    con.execute(f"""
        INSERT INTO ncua_cu_directory
        SELECT
            TRY_CAST({colref('CU_NUMBER')} AS INTEGER) AS cu_number,
            DATE '{period_end}'                        AS period_end,
            {colref('CU_NAME')}                        AS cu_name,
            {colref('CHARTERSTATE')}                   AS charter_state,
            {colref('STATE')}                          AS state,
            TRY_CAST({colref('RSSD')} AS INTEGER)      AS rssd
        FROM foicu_wide
        WHERE TRY_CAST({colref('CU_NUMBER')} AS INTEGER) IS NOT NULL
    """)
    n = con.execute(
        f"SELECT COUNT(*) FROM ncua_cu_directory WHERE period_end = DATE '{period_end}'"
    ).fetchone()[0]
    con.execute("DROP TABLE IF EXISTS foicu_wide")
    out_path.unlink(missing_ok=True)
    print(f"    FOICU: {n:,} credit unions loaded into ncua_cu_directory")
    return n


def create_tables(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS ncua_5300 (
            cu_number    INTEGER,
            period_end   DATE,
            schedule     VARCHAR,
            account_code VARCHAR,
            value        DOUBLE,
            source_file  VARCHAR
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ncua_cu_directory (
            cu_number     INTEGER,
            period_end    DATE,
            cu_name       VARCHAR,
            charter_state VARCHAR,
            state         VARCHAR,
            rssd          INTEGER
        )
    """)


def already_loaded(con, table, period_end):
    n = con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE period_end = DATE '{period_end}'"
    ).fetchone()[0]
    return n > 0


def schedule_loaded(con, period_end, sched):
    """Per-(period, schedule) idempotency: True if this schedule already has rows.

    Finer-grained than period-level so an interrupted run RESUMES the missing
    schedules on re-run instead of skipping the whole (partial) period.
    """
    n = con.execute(
        "SELECT COUNT(*) FROM ncua_5300 WHERE period_end = ? AND schedule = ?",
        [period_end, sched],
    ).fetchone()[0]
    return n > 0


def export_parquet(con):
    """Export ncua_5300 + ncua_cu_directory to Outputs/parquet/ (ZSTD)."""
    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    # Memory-safe export of the 1.18B-row ncua_5300:
    # A global ORDER BY over 1.18B rows is UNSTABLE in this DuckDB build on the
    # full-history table -- it OOMed (281 GiB, then a bogus 7424 PiB estimate with
    # the VARCHAR schedule/account_code keys) and then SEGFAULTED even with a
    # DATE+INT key. So ncua_5300 is exported UNORDERED: a plain streaming scan->
    # parquet write (low memory, no sort), exactly like the 1.25B-row ubpr_ratios
    # export. The rows are already period-CLUSTERED by insertion order (ingested
    # oldest->newest), so parquet row-group min/max stats still prune by period;
    # parity is count-based, so order is immaterial to correctness. The small
    # ncua_cu_directory (851k rows) keeps its cheap ordered export.
    con.execute("SET preserve_insertion_order=false")
    results = {}
    for table, sort_sql in [
        ("ncua_5300",
         "SELECT * FROM ncua_5300"),
        ("ncua_cu_directory",
         "SELECT * FROM ncua_cu_directory ORDER BY period_end, cu_number"),
    ]:
        out = str(parquet_dir / f"{table}.parquet").replace("\\", "/")
        con.execute(f"COPY ({sort_sql}) TO '{out}' {PARQUET_OPTS}")
        pq_rows = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
        db_rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        results[table] = (db_rows, pq_rows)
        status = "OK" if db_rows == pq_rows else "MISMATCH"
        print(f"    {table}.parquet: db={db_rows:,} parquet={pq_rows:,} parity={status}")
    return results


def main():
    elapsed = timer()
    print("=== Phase 26: NCUA 5300 Credit-Union Call Reports ===")
    print("    SCOPE EXPANSION: credit unions (NCUA), distinct from FDIC/BHC universe.\n")

    ncua_dir = INPUT_PATHS["ncua"]
    # Discover ALL zips (any case: .zip / .Zip) so the full 1994-present history is
    # ingested, not just modern call-report-data-*.zip. period_end_from_zip handles
    # the three name patterns; anything it cannot parse raises (no silent skip).
    zips = sorted(
        p for p in ncua_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".zip"
    )
    if not zips:
        print(f"  ERROR: no *.zip found under {ncua_dir}. Nothing to ingest.")
        return

    con = get_db()
    create_tables(con)

    tmp_dir = ncua_dir / "_tmp_extract"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    total_5300 = 0
    total_dir = 0
    for zip_path in zips:
        period_end = period_end_from_zip(zip_path)
        print(f"  ZIP {zip_path.name} -> period_end {period_end}")

        loaded_dir = already_loaded(con, "ncua_cu_directory", period_end)

        with zipfile.ZipFile(zip_path) as zf:
            names = {Path(n).name.upper(): n for n in zf.namelist()}

            members = list_fs220_members(zf)
            print(f"    {len(members)} FS220 schedules: "
                  f"{', '.join(schedule_name(m) for m in members)}")
            for member in members:
                sched = schedule_name(member)
                if schedule_loaded(con, period_end, sched):
                    print(f"    {sched}: already loaded for {period_end} -- skipping (idempotent)")
                    continue
                total_5300 += melt_schedule(con, zf, member, tmp_dir, period_end, sched)

            if not loaded_dir:
                foicu = names.get("FOICU.TXT")
                if foicu:
                    total_dir += load_directory(con, zf, foicu, tmp_dir, period_end)
                else:
                    print("    WARNING: FOICU.txt not found in zip -- directory not loaded")
            else:
                print(f"    ncua_cu_directory for {period_end} already loaded -- skipping")

    # Summary stats
    rows_5300 = con.execute("SELECT COUNT(*) FROM ncua_5300").fetchone()[0]
    rows_dir = con.execute("SELECT COUNT(*) FROM ncua_cu_directory").fetchone()[0]
    n_cu = con.execute("SELECT COUNT(DISTINCT cu_number) FROM ncua_5300").fetchone()[0]
    n_acct = con.execute("SELECT COUNT(DISTINCT account_code) FROM ncua_5300").fetchone()[0]
    n_sched = con.execute("SELECT COUNT(DISTINCT schedule) FROM ncua_5300").fetchone()[0]

    print("\n--- Summary (SCOPE EXPANSION: credit unions, NCUA) ---")
    print(f"  ncua_5300 rows:        {rows_5300:,}")
    print(f"  ncua_cu_directory rows:{rows_dir:,}")
    print(f"  distinct credit unions:{n_cu:,}")
    print(f"  distinct account codes:{n_acct:,}")
    print(f"  schedules:             {n_sched}")

    print("\n  Exporting parquet (ZSTD)...")
    export_parquet(con)

    # Clean up temp extraction dir.
    try:
        for p in tmp_dir.iterdir():
            p.unlink(missing_ok=True)
        tmp_dir.rmdir()
    except OSError:
        pass

    con.close()
    secs = elapsed()
    log_ingestion("26", f"NCUA 5300 credit-union call reports (SCOPE EXPANSION): "
                  f"{rows_5300:,} cells, {rows_dir:,} directory rows, {n_cu:,} credit unions, "
                  f"{n_acct:,} account codes, {n_sched} schedules. {secs:.1f}s")
    print(f"\nPhase 26 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
