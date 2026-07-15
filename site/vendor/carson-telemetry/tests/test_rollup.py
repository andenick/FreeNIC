"""Rollup: correct usage_daily aggregation, idempotency, and retention prune."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from carson_telemetry import db
from carson_telemetry.events import Event
from carson_telemetry import rollup


def _seed(path, ts, service="svc", surface="rest", endpoint="/e",
          status="ok", latency_ms=10, client_id="c1"):
    row = Event(service=service, surface=surface, endpoint=endpoint,
                status=status, latency_ms=latency_ms, client_id=client_id).to_row()
    row["ts"] = ts
    db.write_event(row, path=path)


def test_rollup_aggregates_usage_daily(telemetry_env):
    path = telemetry_env["db_path"]
    day = "2026-06-05"
    # 3 ok calls (2 distinct clients) + 1 error, varied latency.
    _seed(path, f"{day}T10:00:00Z", client_id="A", latency_ms=10)
    _seed(path, f"{day}T11:00:00Z", client_id="A", latency_ms=20)
    _seed(path, f"{day}T12:00:00Z", client_id="B", latency_ms=30)
    _seed(path, f"{day}T13:00:00Z", client_id="B", latency_ms=400, status="500")

    summary = rollup.rollup(db_path=path, prune=False)
    assert summary["days_written"] == 1

    conn = db.get_connection(path)
    try:
        r = conn.execute(
            "SELECT * FROM usage_daily WHERE service='svc' AND day=?", (day,)
        ).fetchone()
    finally:
        conn.close()
    assert r["count"] == 4
    assert r["uniq"] == 2            # clients A and B
    assert r["err"] == 1            # status 500
    assert r["p95"] >= 30          # nearest-rank p95 over [10,20,30,400]


def test_rollup_idempotent(telemetry_env):
    path = telemetry_env["db_path"]
    _seed(path, "2026-06-05T10:00:00Z")
    rollup.rollup(db_path=path, prune=False)
    rollup.rollup(db_path=path, prune=False)  # second run must not duplicate

    conn = db.get_connection(path)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM usage_daily").fetchone()["n"]
        cnt = conn.execute("SELECT count FROM usage_daily").fetchone()["count"]
    finally:
        conn.close()
    assert n == 1
    assert cnt == 1


def test_rollup_prunes_old_raw_events(telemetry_env):
    path = telemetry_env["db_path"]
    now = datetime.now(timezone.utc)
    old_ts = (now - timedelta(days=401)).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_ts = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed(path, old_ts, endpoint="/old")
    _seed(path, new_ts, endpoint="/new")

    summary = rollup.rollup(db_path=path, retention_days=400, prune=True)
    assert summary["rows_pruned"] == 1

    rows = db.fetch_events(path=path)
    endpoints = {r["endpoint"] for r in rows}
    assert "/old" not in endpoints
    assert "/new" in endpoints

    # Aggregates for the pruned day must still exist (retention keeps usage_daily).
    conn = db.get_connection(path)
    try:
        days = {r["day"] for r in conn.execute("SELECT day FROM usage_daily").fetchall()}
    finally:
        conn.close()
    assert old_ts[:10] in days


def test_rollup_no_prune_keeps_all(telemetry_env):
    path = telemetry_env["db_path"]
    old_ts = (datetime.now(timezone.utc) - timedelta(days=500)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed(path, old_ts)
    summary = rollup.rollup(db_path=path, retention_days=400, prune=False)
    assert summary["rows_pruned"] == 0
    assert len(db.fetch_events(path=path)) == 1
