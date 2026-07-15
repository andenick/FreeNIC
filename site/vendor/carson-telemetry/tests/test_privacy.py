"""Global privacy guarantee: no raw IP is ever stored, across every write path."""
from __future__ import annotations

from carson_telemetry import db
from carson_telemetry.asgi import ASGIMiddleware
from carson_telemetry.events import record_event
from tests.test_asgi import _run_request, dummy_app

RAW_IP = "203.0.113.250"


def test_no_raw_ip_anywhere_in_db(telemetry_env):
    path = telemetry_env["db_path"]

    # 1) Via the ASGI middleware (IP arrives in X-Forwarded-For + client peer).
    app = ASGIMiddleware(dummy_app, service="svc", db_path=path)
    scope = {
        "type": "http", "method": "GET", "path": "/x",
        "headers": [(b"x-forwarded-for", RAW_IP.encode())],
        "client": (RAW_IP, 1),
    }
    _run_request(app, scope)

    # 2) Via a direct record_event whose meta tries to smuggle the IP in.
    record_event("svc", "rest", "/y", client_id=None,
                 meta={"client_ip": RAW_IP, "ok": True}, db_path=path)

    # Scan every value of every row for the raw IP.
    conn = db.get_connection(path)
    try:
        rows = conn.execute("SELECT * FROM usage_events").fetchall()
    finally:
        conn.close()
    assert len(rows) == 2
    for r in rows:
        for value in tuple(r):
            assert RAW_IP not in (str(value) if value is not None else "")
