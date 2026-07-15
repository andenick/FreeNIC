"""ASGIMiddleware emits a row for a request, against a tiny dummy ASGI app."""
from __future__ import annotations

import asyncio

from carson_telemetry import db
from carson_telemetry.asgi import ASGIMiddleware


async def dummy_app(scope, receive, send):
    """Minimal ASGI app returning 200 with a small body."""
    assert scope["type"] == "http"
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"hello world"})


def _run_request(app, scope):
    async def _go():
        sent = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            sent.append(message)

        await app(scope, receive, send)
        return sent

    return asyncio.run(_go())


def test_asgi_emits_rest_row(telemetry_env):
    app = ASGIMiddleware(dummy_app, service="gerhard", db_path=telemetry_env["db_path"])
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/v1/forecast",
        "headers": [(b"x-forwarded-for", b"203.0.113.9")],
        "client": ("10.0.0.1", 5555),
    }
    _run_request(app, scope)

    rows = db.fetch_events(path=telemetry_env["db_path"], service="gerhard")
    assert len(rows) == 1
    r = rows[0]
    assert r["surface"] == "rest"
    assert r["endpoint"] == "/v1/forecast"
    assert r["status"] == "200"
    assert r["bytes"] == len(b"hello world")
    assert r["client_id"] is not None and len(r["client_id"]) == 16


def test_asgi_download_surface(telemetry_env):
    app = ASGIMiddleware(dummy_app, service="methodex", db_path=telemetry_env["db_path"])
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/download/bundle.zip",
        "headers": [],
        "client": ("198.51.100.1", 4444),
    }
    _run_request(app, scope)
    rows = db.fetch_events(path=telemetry_env["db_path"], service="methodex")
    assert rows[0]["surface"] == "download"


def test_asgi_no_raw_ip_stored(telemetry_env):
    app = ASGIMiddleware(dummy_app, service="svc", db_path=telemetry_env["db_path"])
    ip = "203.0.113.222"
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/x",
        "headers": [(b"x-forwarded-for", ip.encode())],
        "client": (ip, 1),
    }
    _run_request(app, scope)
    rows = db.fetch_events(path=telemetry_env["db_path"], service="svc")
    r = rows[0]
    # The raw IP must never appear in any stored column.
    for col in ("client_id", "endpoint", "meta", "ts", "service", "surface", "status"):
        assert ip not in (str(r[col]) if r[col] is not None else "")
