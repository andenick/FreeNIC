"""Local ingest sidecar (Carson Telemetry Standard §4).

Two intake paths for non-Python (or out-of-process) services, both writing to
the same SQLite DB so the event contract stays uniform:

  1. HTTP: ``POST http://127.0.0.1:9100/ingest`` with a JSON event body
     -> validated -> written. Malformed bodies return HTTP 400 (never crash).
  2. JSONL tailer: watches ``CARSON_TELEMETRY_INGEST_DIR/*.jsonl`` and appends
     each new line as a row.

Binds to 127.0.0.1 only (loopback) — it is a local sidecar, never exposed.

Entry point: ``carson-telemetry-ingest`` (see pyproject ``[project.scripts]``).
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from .events import Event, EventValidationError
from . import db

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 9100
_MAX_BODY = 64 * 1024  # 64 KB ceiling on an ingest POST body


def _row_from_payload(payload: dict, *, db_path: Optional[str]) -> int:
    """Build, validate, and persist an event from a decoded JSON dict."""
    event = Event(
        service=payload["service"],
        surface=payload["surface"],
        endpoint=payload["endpoint"],
        status=payload.get("status", "ok"),
        latency_ms=int(payload.get("latency_ms") or 0),
        bytes=int(payload.get("bytes") or 0),
        client_id=payload.get("client_id"),
        meta=payload.get("meta"),
        # honour caller ts if present and a string, else default to now
        ts=payload["ts"] if isinstance(payload.get("ts"), str) else None,  # type: ignore[arg-type]
    )
    if event.ts is None:  # dataclass default_factory only runs when field omitted
        from .events import utcnow_iso

        event.ts = utcnow_iso()
    return db.write_event(event.to_row(), path=db_path)


def make_handler(db_path: Optional[str]):
    class IngestHandler(BaseHTTPRequestHandler):
        server_version = "carson-telemetry-ingest/1.0"

        def _send(self, code: int, obj: dict) -> None:
            body = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802 (http.server API)
            if self.path.rstrip("/") != "/ingest":
                self._send(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except (TypeError, ValueError):
                self._send(400, {"error": "bad content-length"})
                return
            if length <= 0 or length > _MAX_BODY:
                self._send(400, {"error": "empty or oversized body"})
                return
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("body must be a JSON object")
                rowid = _row_from_payload(payload, db_path=db_path)
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError,
                    ValueError, TypeError, EventValidationError) as exc:
                self._send(400, {"error": "malformed event", "detail": str(exc)})
                return
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": "ingest failure", "detail": str(exc)})
                return
            self._send(200, {"ok": True, "id": rowid})

        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") in ("/health", "/healthz"):
                self._send(200, {"ok": True})
            else:
                self._send(404, {"error": "not found"})

        def log_message(self, *args) -> None:  # silence default stderr spam
            pass

    return IngestHandler


def build_server(host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT,
                 *, db_path: Optional[str] = None) -> ThreadingHTTPServer:
    db.init_db(db_path)
    return ThreadingHTTPServer((host, port), make_handler(db_path))


# --- JSONL tailer ---------------------------------------------------------

def tail_jsonl_dir(
    directory: str,
    *,
    db_path: Optional[str] = None,
    poll_seconds: float = 1.0,
    stop_event: Optional[threading.Event] = None,
    once: bool = False,
) -> int:
    """Tail every ``*.jsonl`` in ``directory``, writing new lines as rows.

    Tracks per-file byte offsets so a row is ingested once. Returns the number
    of rows written (useful when ``once=True`` for tests).
    """
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    offsets: dict[str, int] = {}
    written = 0
    while True:
        for jf in sorted(d.glob("*.jsonl")):
            key = str(jf)
            start = offsets.get(key, 0)
            try:
                size = jf.stat().st_size
            except OSError:
                continue
            if size < start:  # truncated/rotated
                start = 0
            if size == start:
                continue
            with open(jf, "r", encoding="utf-8") as fh:
                fh.seek(start)
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        if isinstance(payload, dict):
                            _row_from_payload(payload, db_path=db_path)
                            written += 1
                    except (json.JSONDecodeError, KeyError, ValueError,
                            TypeError, EventValidationError):
                        # skip malformed line; don't abort the tail
                        continue
                offsets[key] = fh.tell()
        if once:
            return written
        if stop_event is not None and stop_event.wait(poll_seconds):
            return written
        time.sleep(poll_seconds)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="carson-telemetry-ingest",
                                     description="Local telemetry ingest sidecar (HTTP + JSONL tailer).")
    parser.add_argument("--host", default=_DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT)
    parser.add_argument("--db", default=None, help="override CARSON_TELEMETRY_DB")
    parser.add_argument("--ingest-dir", default=os.environ.get("CARSON_TELEMETRY_INGEST_DIR"),
                        help="directory of *.jsonl files to tail (default $CARSON_TELEMETRY_INGEST_DIR)")
    parser.add_argument("--no-http", action="store_true", help="run only the JSONL tailer")
    args = parser.parse_args(argv)

    stop_event = threading.Event()
    threads: list[threading.Thread] = []

    if args.ingest_dir:
        t = threading.Thread(
            target=tail_jsonl_dir,
            args=(args.ingest_dir,),
            kwargs={"db_path": args.db, "stop_event": stop_event},
            daemon=True,
        )
        t.start()
        threads.append(t)

    if args.no_http:
        if not args.ingest_dir:
            print("nothing to do: --no-http with no --ingest-dir")
            return 2
        print(f"[carson-telemetry-ingest] tailing {args.ingest_dir} (Ctrl-C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_event.set()
        return 0

    server = build_server(args.host, args.port, db_path=args.db)
    print(f"[carson-telemetry-ingest] POST http://{args.host}:{args.port}/ingest"
          + (f"  + tailing {args.ingest_dir}" if args.ingest_dir else ""))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
