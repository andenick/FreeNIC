"""SQLite WAL-mode event store for Carson telemetry.

Implements the storage half of the Carson Telemetry Standard v1.0 §3:
single SQLite DB per box, WAL mode, table ``usage_events`` with the exact
column set from the event contract, indexed on ``(service, ts)`` and
``(service, endpoint)``. The nightly rollup (``rollup.py``) creates and fills
``usage_daily``.

Writes are thread/async-safe: each write opens a short-lived connection
(SQLite connections are not shareable across threads) and serialises through a
module-level lock so concurrent ASGI/MCP workers cannot interleave a write.
WAL mode additionally lets readers (the dashboard) run without blocking writers.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
from pathlib import Path
from typing import Any, Iterable, Optional

# Default production path per the standard (§3). On a dev/Windows box that path
# is not writable, so we fall back to a CWD/temp location.
_DEFAULT_POSIX_DB = "/var/lib/carson/telemetry.db"

_WRITE_LOCK = threading.Lock()

# DDL ----------------------------------------------------------------------

# Column order/names are LOAD-BEARING — they mirror the §3 contract exactly.
_CREATE_USAGE_EVENTS = """
CREATE TABLE IF NOT EXISTS usage_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT    NOT NULL,   -- ISO-8601 UTC, e.g. 2026-06-05T14:03:22Z
    service     TEXT    NOT NULL,   -- registry name (methodex, gerhard, ...)
    surface     TEXT    NOT NULL,   -- mcp | rest | web | download
    endpoint    TEXT    NOT NULL,   -- tool name / route / file path (names only)
    client_id   TEXT,              -- sha256(ip + daily_salt)[:16]; NEVER a raw IP
    status      TEXT    NOT NULL,   -- ok | error | HTTP code
    latency_ms  INTEGER NOT NULL DEFAULT 0,
    bytes       INTEGER NOT NULL DEFAULT 0,
    meta        TEXT                -- JSON, PII-free, <=1KB
);
"""

_CREATE_INDICES = (
    "CREATE INDEX IF NOT EXISTS ix_usage_events_service_ts "
    "ON usage_events (service, ts);",
    "CREATE INDEX IF NOT EXISTS ix_usage_events_service_endpoint "
    "ON usage_events (service, endpoint);",
)

# usage_daily is created by the rollup, but we keep its DDL here so db.py owns
# all schema and the dashboard can rely on it existing after a rollup.
_CREATE_USAGE_DAILY = """
CREATE TABLE IF NOT EXISTS usage_daily (
    service   TEXT    NOT NULL,
    surface   TEXT    NOT NULL,
    endpoint  TEXT    NOT NULL,
    day       TEXT    NOT NULL,   -- YYYY-MM-DD (UTC)
    count     INTEGER NOT NULL,
    uniq      INTEGER NOT NULL,
    err       INTEGER NOT NULL,
    p95       INTEGER NOT NULL,
    PRIMARY KEY (service, surface, endpoint, day)
);
"""


def resolve_db_path(explicit: Optional[str] = None) -> str:
    """Resolve the telemetry DB path.

    Order: explicit arg > env ``CARSON_TELEMETRY_DB`` > the standard POSIX path
    > a writable fallback (temp dir) on platforms where the POSIX path is not
    usable (e.g. Windows dev boxes).
    """
    path = explicit or os.environ.get("CARSON_TELEMETRY_DB") or _DEFAULT_POSIX_DB
    parent = Path(path).parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        # Probe writability without leaving a file behind.
        if not os.access(parent, os.W_OK):
            raise PermissionError(parent)
        return path
    except (OSError, PermissionError):
        fallback_dir = Path(tempfile.gettempdir()) / "carson_telemetry"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return str(fallback_dir / "telemetry.db")


def _connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=30.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: Optional[str] = None) -> str:
    """Create the schema (idempotent). Returns the resolved path."""
    resolved = resolve_db_path(path)
    with _WRITE_LOCK:
        conn = _connect(resolved)
        try:
            conn.execute(_CREATE_USAGE_EVENTS)
            for stmt in _CREATE_INDICES:
                conn.execute(stmt)
            conn.execute(_CREATE_USAGE_DAILY)
        finally:
            conn.close()
    return resolved


def get_connection(path: Optional[str] = None, *, init: bool = True) -> sqlite3.Connection:
    """Open a fresh connection (caller owns/closes it). Used by readers."""
    resolved = resolve_db_path(path)
    if init:
        init_db(resolved)
    return _connect(resolved)


def write_event(row: dict[str, Any], *, path: Optional[str] = None) -> int:
    """Insert one validated event row. Returns the new rowid.

    ``row`` is expected to already be validated/serialised by ``events.py``
    (meta is a JSON string or a dict; a dict is serialised here defensively).
    """
    resolved = resolve_db_path(path)
    meta = row.get("meta")
    if isinstance(meta, (dict, list)):
        meta = json.dumps(meta, separators=(",", ":"), ensure_ascii=False)
    params = (
        row["ts"],
        row["service"],
        row["surface"],
        row["endpoint"],
        row.get("client_id"),
        str(row["status"]),
        int(row.get("latency_ms") or 0),
        int(row.get("bytes") or 0),
        meta,
    )
    with _WRITE_LOCK:
        conn = _connect(resolved)
        try:
            # Ensure schema exists even if init_db was never called.
            conn.execute(_CREATE_USAGE_EVENTS)
            for stmt in _CREATE_INDICES:
                conn.execute(stmt)
            cur = conn.execute(
                "INSERT INTO usage_events "
                "(ts, service, surface, endpoint, client_id, status, latency_ms, bytes, meta) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                params,
            )
            return int(cur.lastrowid)
        finally:
            conn.close()


def fetch_events(
    *,
    path: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = 1000,
) -> list[sqlite3.Row]:
    """Read recent events (helper for tests/dashboard)."""
    conn = get_connection(path)
    try:
        if service:
            cur = conn.execute(
                "SELECT * FROM usage_events WHERE service = ? ORDER BY id DESC LIMIT ?",
                (service, limit),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM usage_events ORDER BY id DESC LIMIT ?", (limit,)
            )
        return cur.fetchall()
    finally:
        conn.close()


def executemany_events(rows: Iterable[dict[str, Any]], *, path: Optional[str] = None) -> int:
    """Bulk insert (used by the JSONL tailer). Returns count written."""
    n = 0
    for r in rows:
        write_event(r, path=path)
        n += 1
    return n
