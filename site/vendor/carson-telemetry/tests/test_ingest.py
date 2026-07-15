"""Ingest sidecar: HTTP POST -> row, malformed -> 400, JSONL tailer -> rows."""
from __future__ import annotations

import json
import threading
import time
from http.client import HTTPConnection

from carson_telemetry import db
from carson_telemetry import ingest


def _start_server(db_path):
    server = ingest.build_server("127.0.0.1", 0, db_path=db_path)  # port 0 = ephemeral
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, server.server_address[1]


def test_ingest_post_writes_row(telemetry_env):
    server, port = _start_server(telemetry_env["db_path"])
    try:
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        payload = json.dumps({
            "service": "external-svc", "surface": "rest",
            "endpoint": "/v1/thing", "status": "ok",
            "latency_ms": 12, "bytes": 100, "meta": {"id": "abc"},
        })
        conn.request("POST", "/ingest", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        body = json.loads(resp.read())
        assert resp.status == 200
        assert body["ok"] is True
    finally:
        server.shutdown()

    rows = db.fetch_events(path=telemetry_env["db_path"], service="external-svc")
    assert len(rows) == 1
    assert rows[0]["endpoint"] == "/v1/thing"


def test_ingest_malformed_returns_400(telemetry_env):
    server, port = _start_server(telemetry_env["db_path"])
    try:
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        conn.request("POST", "/ingest", body="{not json",
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        resp.read()
        assert resp.status == 400

        # Missing required field also -> 400 (no crash).
        conn2 = HTTPConnection("127.0.0.1", port, timeout=5)
        conn2.request("POST", "/ingest", body=json.dumps({"surface": "rest"}),
                      headers={"Content-Type": "application/json"})
        resp2 = conn2.getresponse()
        resp2.read()
        assert resp2.status == 400
    finally:
        server.shutdown()

    # No rows should have been written by the malformed requests.
    assert db.fetch_events(path=telemetry_env["db_path"]) == []


def test_jsonl_tailer_appends_rows(telemetry_env):
    ingest_dir = telemetry_env["ingest_dir"]
    jf = f"{ingest_dir}/events.jsonl"
    with open(jf, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"service": "jsvc", "surface": "download",
                             "endpoint": "/d/a.zip", "status": "ok"}) + "\n")
        fh.write("garbage line that is not json\n")
        fh.write(json.dumps({"service": "jsvc", "surface": "rest",
                             "endpoint": "/v1/b", "status": "200"}) + "\n")

    written = ingest.tail_jsonl_dir(ingest_dir, db_path=telemetry_env["db_path"], once=True)
    assert written == 2  # malformed line skipped, not counted

    rows = db.fetch_events(path=telemetry_env["db_path"], service="jsvc")
    endpoints = {r["endpoint"] for r in rows}
    assert endpoints == {"/d/a.zip", "/v1/b"}
