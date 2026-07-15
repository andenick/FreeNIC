"""Dashboard: stdlib queries always tested; FastAPI app tested only if extra present."""
from __future__ import annotations

import importlib.util

import pytest

from carson_telemetry import db
from carson_telemetry.dashboard.queries import overview
from carson_telemetry.events import Event


def _seed(path):
    for i, (sfc, ep, st, lat) in enumerate([
        ("rest", "/a", "200", 10),
        ("rest", "/a", "200", 20),
        ("rest", "/b", "500", 30),
        ("mcp", "tool_x", "ok", 5),
    ]):
        row = Event(service="svc", surface=sfc, endpoint=ep, status=st,
                    latency_ms=lat, client_id=f"c{i % 2}").to_row()
        db.write_event(row, path=path)


def test_overview_queries(telemetry_env):
    path = telemetry_env["db_path"]
    _seed(path)
    o = overview(path, service="svc")
    assert o["total_calls"] == 4
    assert o["errors"] == 1
    assert 0 < o["error_rate"] < 1
    assert o["unique_clients"] == 2
    assert o["p50_latency_ms"] >= 1
    assert o["p95_latency_ms"] >= o["p50_latency_ms"]
    top_eps = {(e["surface"], e["endpoint"]): e["calls"] for e in o["top_endpoints"]}
    assert top_eps[("rest", "/a")] == 2


@pytest.mark.skipif(
    importlib.util.find_spec("fastapi") is None,
    reason="[fastapi] extra not installed",
)
def test_dashboard_app_builds_and_serves(telemetry_env):
    from fastapi.testclient import TestClient  # noqa: WPS433

    from carson_telemetry.dashboard.app import create_app

    _seed(telemetry_env["db_path"])
    app = create_app(telemetry_env["db_path"])
    client = TestClient(app)
    r = client.get("/api/overview?service=svc")
    assert r.status_code == 200
    assert r.json()["total_calls"] == 4
    html = client.get("/")
    assert html.status_code == 200
    assert "Carson Telemetry" in html.text
