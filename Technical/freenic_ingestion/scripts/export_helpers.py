"""Shared Parquet export helpers for the freenic pipeline (Track 1 robustness).

This module isolates the robust-export logic used by ``12_export_parquet.py``
(full export) and ``12b_export_call_report_filings.py`` (single-table re-export):

  * Skip-if-current freshness gating (parquet mtime vs. table last-write signal),
    backed by a per-table ``_export_markers.json`` and the live ``filing_metadata``
    ingestion timestamps.
  * Memory / temp-directory spill safety so a billion-row sort spills to a large
    fast disk instead of hanging on a 0-byte tmp under memory contention.
  * Single-file period-chunk *sort-then-append* export for the >2 GB tables so no
    single 1.9B-row global in-memory sort is ever attempted, while still producing
    one sorted ``<table>.parquet`` (the layout MCP / packages read).
  * tmp-file + atomic rename, stale-tmp cleanup, per-table heartbeat, resumability.

IMPORTANT (Track 1 design constraint): nothing in this module opens a DuckDB
connection on import. The caller passes an already-open connection. Marker JSON
and file mtimes are pure filesystem reads (safe under the single-writer lock);
the ``filing_metadata`` freshness query runs only when the caller actually invokes
an export (i.e. when a connection is available).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

# Tables whose on-disk parquet exceeds ~2 GB and therefore must NOT be exported
# via a single global ``ORDER BY`` (which forces a full in-memory sort of up to
# ~1.9B rows). These are exported via period-chunk sort-then-append instead.
# Maps table -> (period_column, sort_key). The period column drives the chunk
# loop (ascending distinct values); each chunk is sorted within itself.
BIG_TABLES = {
    'call_report_filings': ('period_end', 'rssd_id, period_end'),
    'luck_call_reports': ('period_end', 'entity_id, period_end'),
    'bhcf_filings': ('period_end', 'rssd_id, period_end'),
    'fdic_financials': ('period_end', 'rssd_id, period_end'),
}

# Map a table to the ``filing_metadata.filing_type`` values that signal a write
# to it. Used by the skip-if-current freshness check: the table's "last write" is
# MAX(ingestion_ts) over these filing_types. Tables not listed here fall back to
# the marker JSON only (their freshness is whatever the last export recorded).
TABLE_FILING_TYPES = {
    'call_report_filings': ('CALL',),
    'luck_call_reports': ('luck',),
    'bhcf_filings': ('BHCF',),
}

ROW_GROUP_SIZE = 122880
COMPRESSION = 'ZSTD'

# Convenience empty sort-key map for single-table callers (e.g. 12b) that only
# export a BIG_TABLES entry, which carries its own sort key in BIG_TABLES.
SORT_KEYS_NONE: dict = {}


def markers_path(parquet_dir: Path) -> Path:
    """Path to the per-table export-markers JSON inside the parquet output dir."""
    return parquet_dir / "_export_markers.json"


def load_markers(parquet_dir: Path) -> dict:
    """Load the export-markers JSON (filesystem read only). Returns {} if absent."""
    p = markers_path(parquet_dir)
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupt / unreadable marker file: treat as no markers (forces re-export).
        return {}


def save_markers(parquet_dir: Path, markers: dict) -> None:
    """Persist the export-markers JSON atomically (tmp + rename)."""
    p = markers_path(parquet_dir)
    tmp = p.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(markers, f, indent=2, sort_keys=True)
    os.replace(tmp, p)


def cleanup_stale_tmp(parquet_dir: Path) -> int:
    """Remove any leftover ``tmp_*.parquet`` from a previously-killed run.

    A hung sorted COPY leaves a 0-byte ``tmp_<table>.parquet``; clearing these on
    start keeps the dir clean and prevents a stale tmp from masking a real failure.
    Returns the number of files removed.
    """
    removed = 0
    for f in parquet_dir.glob("tmp_*.parquet"):
        try:
            f.unlink()
            removed += 1
        except OSError:
            pass
    # Also drop an orphaned markers tmp.
    for f in parquet_dir.glob("_export_markers.json.tmp"):
        try:
            f.unlink()
        except OSError:
            pass
    return removed


def configure_session(con, temp_dir: Path, memory_limit: str = '40GB',
                      threads: int | None = None) -> None:
    """Apply memory / spill safety to a DuckDB connection before exporting.

    * ``temp_directory`` -> a large fast disk so big sorts spill to disk instead
      of thrashing / hanging (the root cause of the 0-byte-tmp hang).
    * ``memory_limit`` -> headroom (default 40 GB, below the 50 GiB ceiling) so the
      sort spills gracefully rather than OOMing under concurrent load.
    * ``threads`` (optional) -> lower for the giant tables to cut peak memory.

    temp_dir is created if missing. Pure SET statements — no data is mutated.
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_str = str(temp_dir).replace('\\', '/')
    con.execute(f"SET temp_directory='{temp_str}'")
    con.execute(f"SET memory_limit='{memory_limit}'")
    if threads is not None:
        con.execute(f"SET threads={int(threads)}")


def table_last_write(con, table: str) -> float | None:
    """Latest write-signal for ``table`` as a POSIX timestamp, or None if unknown.

    Reads MAX(ingestion_ts) from ``filing_metadata`` for the table's mapped
    filing_type(s). Returns None when the table has no filing_type mapping (its
    freshness then relies solely on the marker JSON). Executes a SELECT only —
    requires the caller's connection but does not mutate the DB.
    """
    ftypes = TABLE_FILING_TYPES.get(table)
    if not ftypes:
        return None
    placeholders = ",".join("?" for _ in ftypes)
    row = con.execute(
        f"SELECT MAX(ingestion_ts) FROM filing_metadata "
        f"WHERE filing_type IN ({placeholders})",
        list(ftypes),
    ).fetchone()
    if not row or row[0] is None:
        return None
    ts = row[0]
    if isinstance(ts, datetime):
        return ts.timestamp()
    # DuckDB may hand back a string for TIMESTAMP in some configs.
    try:
        return datetime.fromisoformat(str(ts)).timestamp()
    except ValueError:
        return None


def is_current(con, table: str, out_path: Path, markers: dict) -> bool:
    """True if ``out_path`` is already up to date and can be skipped.

    Up to date means the parquet exists AND its mtime is newer than the table's
    last write. Last write is the most recent of:
      * the live ``filing_metadata`` ingestion signal (if the table is mapped), and
      * the ``last_write_ts`` recorded in the marker JSON at the previous export.
    If neither signal is known, the parquet's mere existence is treated as current
    (the only writers of these tables log to filing_metadata or are re-run via
    ``--force``).
    """
    if not out_path.exists() or out_path.stat().st_size == 0:
        return False
    parquet_mtime = out_path.stat().st_mtime

    signals = []
    live = table_last_write(con, table)
    if live is not None:
        signals.append(live)
    marker = markers.get(table, {})
    if marker.get("last_write_ts") is not None:
        signals.append(float(marker["last_write_ts"]))

    if not signals:
        return True  # no freshness signal at all -> existence == current
    return parquet_mtime > max(signals)


def _copy_query(con, select_sql: str, out_str: str) -> None:
    """Run a COPY (<select_sql>) TO <out_str> with the standard parquet options."""
    con.execute(
        f"COPY ({select_sql}) TO '{out_str}' "
        f"(FORMAT PARQUET, COMPRESSION {COMPRESSION}, ROW_GROUP_SIZE {ROW_GROUP_SIZE})"
    )


def export_chunked(con, qualified: str, table: str, parquet_dir: Path,
                   tmp_str: str, period_col: str, sort_key: str) -> None:
    """Single-file period-chunk *sort-then-concatenate* export for a >2 GB table.

    Instead of one ``COPY (SELECT * ORDER BY ...)`` over up to 1.9B rows (a full
    global in-memory sort that hung), this:
      1. enumerates distinct ``period_col`` values ascending,
      2. writes EACH period to its own ``tmp_<table>_part_NNNN.parquet``, sorted
         within the period (a bounded, cheap sort — one period's rows only), then
      3. concatenates the parts, in period order, into the single ``tmp_str`` via
         ``COPY (SELECT * FROM read_parquet([part0, part1, ...])) TO tmp_str`` with
         NO ORDER BY.

    Why the concatenation is globally sorted: ``read_parquet`` over an explicit
    file LIST reads the files in list order and preserves intra-file row order, so
    the output is ordered by ``period_col`` across files and by the full sort key
    within each file. DuckDB never holds more than one period in memory to sort,
    so peak memory is bounded by the largest single period — never the 1.9B-row
    table. The concat pass is a streaming copy (no sort), also bounded.

    Part files are cleaned up afterward (and any stale ones up front).
    """
    # Clean any stale part files for this table from a prior killed run.
    part_glob = f"tmp_{table}_part_*.parquet"
    for f in parquet_dir.glob(part_glob):
        try:
            f.unlink()
        except OSError:
            pass

    periods = [r[0] for r in con.execute(
        f"SELECT DISTINCT {period_col} FROM {qualified} "
        f"WHERE {period_col} IS NOT NULL ORDER BY {period_col}"
    ).fetchall()]

    # Rows with a NULL period would be dropped by the period loop; capture them as
    # a final part so row-count parity holds.
    has_null = con.execute(
        f"SELECT COUNT(*) FROM {qualified} WHERE {period_col} IS NULL"
    ).fetchone()[0] > 0

    if not periods and not has_null:
        # Degenerate: no usable period values. Fall back to a single sorted COPY
        # (session memory_limit/temp_directory make it spill rather than hang).
        _copy_query(con, f"SELECT * FROM {qualified} ORDER BY {sort_key}", tmp_str)
        return

    n = len(periods) + (1 if has_null else 0)
    print(f"      period-chunk export: {n} chunks over {period_col}", flush=True)

    part_paths: list[Path] = []
    try:
        for i, period in enumerate(periods):
            part = parquet_dir / f"tmp_{table}_part_{i:04d}.parquet"
            part_str = str(part).replace('\\', '/')
            pliteral = _period_literal(period)
            _copy_query(
                con,
                f"SELECT * FROM {qualified} WHERE {period_col} = {pliteral} "
                f"ORDER BY {sort_key}",
                part_str,
            )
            part_paths.append(part)
            if (i + 1) % 10 == 0 or (i + 1) == len(periods):
                print(f"        ...{i + 1}/{len(periods)} period chunks written",
                      flush=True)

        if has_null:
            part = parquet_dir / f"tmp_{table}_part_{len(periods):04d}.parquet"
            part_str = str(part).replace('\\', '/')
            _copy_query(
                con,
                f"SELECT * FROM {qualified} WHERE {period_col} IS NULL "
                f"ORDER BY {sort_key}",
                part_str,
            )
            part_paths.append(part)

        # Concatenate parts (in order) into the single output, no re-sort.
        file_list = ", ".join(
            "'" + str(p).replace('\\', '/') + "'" for p in part_paths
        )
        print(f"        concatenating {len(part_paths)} chunks -> single file",
              flush=True)
        _copy_query(
            con,
            f"SELECT * FROM read_parquet([{file_list}])",
            tmp_str,
        )
    finally:
        for p in part_paths:
            try:
                p.unlink()
            except OSError:
                pass


def _period_literal(value) -> str:
    """Render a period value as a safe SQL literal (DATE / INT / quoted string)."""
    from datetime import date
    if isinstance(value, (datetime, date)):
        return f"DATE '{value.isoformat()[:10]}'"
    if isinstance(value, (int,)):
        return str(value)
    # String period (e.g. '2020Q1'); escape single quotes.
    return "'" + str(value).replace("'", "''") + "'"


def export_table(con, schema: str, table: str, parquet_dir: Path,
                 sort_keys: dict, markers: dict, *, force: bool = False) -> dict:
    """Export one table robustly. Returns a status dict for the marker JSON.

    Status dict keys: ``status`` in {skipped, exported, empty, error},
    ``rows``, ``size_mb``, ``error`` (optional).

    Mechanism:
      * skip-if-current (unless ``force``),
      * tmp-file + atomic rename,
      * period-chunk sort-then-concatenate for BIG_TABLES, else a single sorted COPY
        (now safe because the session has temp_directory/memory_limit set),
      * records the table's last-write signal into the returned marker.
    """
    qualified = f"{schema}.{table}" if schema != 'main' else table
    out_name = f"catalog_{table}" if schema == 'catalog' else table
    out_path = parquet_dir / f"{out_name}.parquet"
    tmp_path = parquet_dir / f"tmp_{out_name}.parquet"
    tmp_str = str(tmp_path).replace('\\', '/')

    print(f"  {qualified} ...", flush=True)

    # Resumability: if this run already exported the table this round, skip.
    if not force and markers.get(table, {}).get("run_done"):
        print(f"    already exported this run; skipping", flush=True)
        return markers.get(table, {})

    # Skip-if-current.
    if not force and is_current(con, table, out_path, markers):
        size_mb = out_path.stat().st_size / (1024 ** 2)
        print(f"    current (parquet newer than last write); skipping "
              f"[{size_mb:,.1f} MB]", flush=True)
        m = dict(markers.get(table, {}))
        m["status"] = "skipped"
        m["run_done"] = True
        return m

    try:
        count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
        if count == 0:
            print(f"    empty; skipping", flush=True)
            return {"status": "empty", "rows": 0, "run_done": True}

        # Clear a stale tmp for this specific table before writing.
        if tmp_path.exists():
            tmp_path.unlink()

        if table in BIG_TABLES:
            period_col, sort_key = BIG_TABLES[table]
            print(f"    big table ({count:,} rows) -> period-chunk export", flush=True)
            export_chunked(con, qualified, table, parquet_dir, tmp_str,
                           period_col, sort_key)
        else:
            sort_key = sort_keys.get(table, '')
            order_clause = f" ORDER BY {sort_key}" if sort_key else ""
            _copy_query(con, f"SELECT * FROM {qualified}{order_clause}", tmp_str)

        # Atomic publish: replace the live parquet only after a complete write.
        os.replace(tmp_path, out_path)

        size_mb = out_path.stat().st_size / (1024 ** 2)
        last_write = table_last_write(con, table)
        print(f"    {count:>15,} rows -> {size_mb:>8.1f} MB", flush=True)
        return {
            "status": "exported",
            "rows": count,
            "size_mb": round(size_mb, 1),
            "last_write_ts": last_write,
            "exported_ts": time.time(),
            "run_done": True,
        }

    except Exception as e:  # per-table: log + continue (caller keeps going)
        # Leave no partial tmp behind.
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        print(f"    ERROR - {e}", flush=True)
        return {"status": "error", "error": str(e), "run_done": False}
