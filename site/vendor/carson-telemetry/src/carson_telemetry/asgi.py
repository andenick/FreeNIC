"""Pure-ASGI telemetry middleware (Carson Telemetry Standard §4).

``ASGIMiddleware(app, service=...)`` records exactly one ``usage_events`` row
per HTTP request. It is a plain ASGI callable — it does NOT import FastAPI or
Starlette at module top, so it composes with either (or raw ASGI) and stays
import-light. FastAPI/Starlette's ``app.add_middleware`` passes ``app`` plus
kwargs, which this signature accepts.

Per §3/§6 the client id is a daily-salted hash of the IP taken from
``X-Forwarded-For`` (Cloudflare/Caddy set this) or the ASGI ``client`` peer.
The raw IP is never stored.
"""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Optional

from .events import record_event
from .hashing import hash_client

Scope = dict
Receive = Callable[[], Awaitable[dict]]
Send = Callable[[dict], Awaitable[None]]

# Paths that count as downloads rather than generic REST calls.
_DOWNLOAD_PREFIXES = ("/download", "/api/download")


def _client_ip(scope: Scope) -> Optional[str]:
    """Extract a client IP, preferring X-Forwarded-For (leftmost = original)."""
    headers = dict(scope.get("headers") or [])
    xff = headers.get(b"x-forwarded-for")
    if xff:
        first = xff.decode("latin-1").split(",")[0].strip()
        if first:
            return first
    real = headers.get(b"x-real-ip")
    if real:
        return real.decode("latin-1").strip()
    client = scope.get("client")
    if client:
        return client[0]
    return None


def _endpoint(scope: Scope) -> str:
    """Route template if the framework resolved one, else the raw path.

    Starlette/FastAPI place the matched ``Route`` in ``scope['route']`` (or a
    ``path_format`` on some versions). Using the template — not the concrete
    path — keeps cardinality low and avoids logging argument values (§3).
    """
    route = scope.get("route")
    if route is not None:
        tmpl = getattr(route, "path_format", None) or getattr(route, "path", None)
        if tmpl:
            return str(tmpl)
    # Some setups stash the template directly.
    if scope.get("path_format"):
        return str(scope["path_format"])
    return scope.get("path", "/") or "/"


def _surface_for(path: str) -> str:
    p = path or "/"
    for prefix in _DOWNLOAD_PREFIXES:
        if p == prefix or p.startswith(prefix + "/") or p.startswith(prefix):
            return "download"
    return "rest"


class ASGIMiddleware:
    """ASGI middleware that emits one telemetry event per HTTP request."""

    def __init__(self, app: Callable, service: str, *, db_path: Optional[str] = None) -> None:
        self.app = app
        self.service = service
        self.db_path = db_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            # Pass through lifespan / websocket untouched.
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_holder: dict[str, Any] = {"code": 0, "bytes": 0}

        async def send_wrapper(message: dict) -> None:
            mtype = message.get("type")
            if mtype == "http.response.start":
                status_holder["code"] = message.get("status", 0)
            elif mtype == "http.response.body":
                body = message.get("body") or b""
                status_holder["bytes"] += len(body)
            await send(message)

        error: Optional[BaseException] = None
        try:
            await self.app(scope, receive, send_wrapper)
        except BaseException as exc:  # noqa: BLE001 — re-raised after recording
            error = exc
            raise
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            raw_path = scope.get("path", "/") or "/"
            code = status_holder["code"]
            if error is not None and not code:
                status = "error"
            elif code:
                status = str(code)
            else:
                status = "ok"
            client_id = hash_client(_client_ip(scope))
            try:
                record_event(
                    self.service,
                    _surface_for(raw_path),
                    _endpoint(scope),
                    status=status,
                    latency_ms=latency_ms,
                    bytes=status_holder["bytes"],
                    client_id=client_id,
                    meta=None,
                    db_path=self.db_path,
                )
            except Exception:
                # Telemetry must never break the request path.
                pass
