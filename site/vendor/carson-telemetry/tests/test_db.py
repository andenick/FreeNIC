"""DB write+read roundtrip and schema/index checks."""
from __future__ import annotations

from carson_telemetry import db
from carson_telemetry.events import Event


def test_write_read_roundtrip(telemetry_env):
    path = telemetry_env["db_path"]
    row = Event(
        service="methodex", surface="mcp", endpoint="get_methodology",
        status="ok", latency_ms=42, bytes=128, client_id="abc123",
        meta={"statistic": "US.BEA.GDP", "as_of": 1985},
    ).to_row()
    rowid = db.write_event(row, path=path)
    assert rowid > 0

    rows = db.fetch_events(path=path, service="methodex")
    assert len(rows) == 1
    r = rows[0]
    assert r["service"] == "methodex"
    assert r["surface"] == "mcp"
    assert r["endpoint"] == "get_methodology"
    assert r["status"] == "ok"
    assert r["latency_ms"] == 42
    assert r["bytes"] == 128
    assert r["client_id"] == "abc123"
    assert '"statistic":"US.BEA.GDP"' in r["meta"]


def test_schema_columns_exact(telemetry_env):
    conn = db.get_connection(telemetry_env["db_path"])
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(usage_events)").fetchall()]
    finally:
        conn.close()
    # Contract columns from TELEMETRY_STANDARD §3 (id is our surrogate PK).
    for c in ["ts", "service", "surface", "endpoint", "client_id",
              "status", "latency_ms", "bytes", "meta"]:
        assert c in cols, f"missing column {c}"


def test_indices_present(telemetry_env):
    conn = db.get_connection(telemetry_env["db_path"])
    try:
        idx = {r[1] for r in conn.execute("PRAGMA index_list(usage_events)").fetchall()}
    finally:
        conn.close()
    assert "ix_usage_events_service_ts" in idx
    assert "ix_usage_events_service_endpoint" in idx


def test_wal_mode(telemetry_env):
    conn = db.get_connection(telemetry_env["db_path"])
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    finally:
        conn.close()
    assert str(mode).lower() == "wal"
