"""carson-telemetry — shared, privacy-first usage telemetry for Carson-hosted services.

Implements the Carson Telemetry Standard v1.0 (Layer 3 event contract). Every
Carson-hosted API/MCP/website imports this to emit one ``usage_events`` row per
invocation into a single SQLite DB.

Per the §4 integration recipe, a site author writes:

    from carson_telemetry import telemetry

    app.add_middleware(telemetry.ASGIMiddleware, service="gerhard")   # REST/download
    mcp = telemetry.instrument_mcp(mcp, service="methodex")           # MCP tools

``telemetry`` is this very module (the namespace), so both
``from carson_telemetry import telemetry`` and direct ``carson_telemetry.X``
work.
"""
from __future__ import annotations

import sys as _sys

from .asgi import ASGIMiddleware
from .events import (
    Event,
    EventValidationError,
    record_download,
    record_event,
    sanitize_meta,
)
from .hashing import hash_client
from .mcp import instrument_mcp

__version__ = "1.0.0"

__all__ = [
    "ASGIMiddleware",
    "instrument_mcp",
    "record_event",
    "record_download",
    "hash_client",
    "Event",
    "EventValidationError",
    "sanitize_meta",
    "telemetry",
]

# Expose a `telemetry` name that resolves to this module, so the §4 recipe
# `from carson_telemetry import telemetry` then `telemetry.ASGIMiddleware` works.
telemetry = _sys.modules[__name__]
