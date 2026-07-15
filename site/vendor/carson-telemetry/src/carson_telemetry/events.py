"""Event dataclass + validation (Carson Telemetry Standard §3, §6).

An ``Event`` mirrors the §3 contract one-for-one. ``validate()`` enforces the
privacy/size rules: ``surface`` is constrained, ``meta`` must be
JSON-serialisable and <= 1 KB, and non-PII-safe meta content is stripped
(meta is for identifiers/keys, never user free-text).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

SURFACES = frozenset({"mcp", "rest", "web", "download"})
_META_MAX_BYTES = 1024  # 1 KB cap per §3

# Heuristic guard: meta keys that look like free-text/PII conduits are dropped.
# meta should carry identifiers (statistic ids, years, route params), not prose.
_BANNED_META_KEYS = frozenset({
    "ip", "ip_address", "client_ip", "remote_addr", "x_forwarded_for",
    "email", "user", "username", "user_id", "name", "full_name",
    "query", "q", "prompt", "text", "body", "message", "content",
    "args", "arguments", "input", "password", "token", "secret", "authorization",
    "cookie", "session", "user_agent",
})

# Any string value longer than this in meta is treated as free-text and dropped.
_META_FREETEXT_LEN = 120


class EventValidationError(ValueError):
    """Raised when an event cannot be made contract-compliant."""


def utcnow_iso() -> str:
    """ISO-8601 UTC with a trailing Z, second precision (per §3 example)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Event:
    service: str
    surface: str
    endpoint: str
    status: str = "ok"
    latency_ms: int = 0
    bytes: int = 0
    client_id: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    ts: str = field(default_factory=utcnow_iso)

    def to_row(self) -> dict[str, Any]:
        """Validated dict ready for ``db.write_event`` (meta serialised)."""
        self.validate()
        return {
            "ts": self.ts,
            "service": self.service,
            "surface": self.surface,
            "endpoint": self.endpoint,
            "client_id": self.client_id,
            "status": str(self.status),
            "latency_ms": int(self.latency_ms or 0),
            "bytes": int(self.bytes or 0),
            "meta": _serialise_meta(self.meta),
        }

    def validate(self) -> "Event":
        if not self.service or not isinstance(self.service, str):
            raise EventValidationError("service is required and must be a string")
        if not self.endpoint or not isinstance(self.endpoint, str):
            raise EventValidationError("endpoint is required and must be a string")
        if self.surface not in SURFACES:
            raise EventValidationError(
                f"surface must be one of {sorted(SURFACES)}, got {self.surface!r}"
            )
        # Normalise status to a string (ok | error | HTTP code).
        self.status = str(self.status)
        try:
            self.latency_ms = int(self.latency_ms or 0)
            self.bytes = int(self.bytes or 0)
        except (TypeError, ValueError) as exc:
            raise EventValidationError(f"latency_ms/bytes must be ints: {exc}") from exc
        # meta: scrub + size-check. Raises if it cannot be brought under cap.
        self.meta = sanitize_meta(self.meta)
        return self


def sanitize_meta(meta: Optional[Any]) -> Optional[dict[str, Any]]:
    """Return a PII-safe, JSON-serialisable, <=1KB meta dict (or None).

    - non-dict meta is rejected (meta is a small key/value map, not free text)
    - banned keys (ip/email/query/prompt/...) are dropped
    - long string values (free-text) are dropped
    - the result must serialise to <= 1 KB or it is progressively trimmed; if
      it still cannot fit after dropping all values, raise.
    """
    if meta is None:
        return None
    if not isinstance(meta, dict):
        raise EventValidationError("meta must be a JSON object (dict) of identifiers, not free text")

    clean: dict[str, Any] = {}
    for key, value in meta.items():
        k = str(key)
        if k.lower() in _BANNED_META_KEYS:
            continue
        if isinstance(value, str) and len(value) > _META_FREETEXT_LEN:
            # Looks like free text / a conduit for PII — drop it.
            continue
        # Only keep JSON-primitive-ish values.
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean[k] = value
        elif isinstance(value, (list, tuple)):
            # keep short lists of primitives (e.g. param ids)
            prims = [v for v in value if isinstance(v, (str, int, float, bool))]
            prims = [v for v in prims if not (isinstance(v, str) and len(v) > _META_FREETEXT_LEN)]
            clean[k] = prims
        else:
            # nested dicts / objects are not allowed (could hide free text)
            continue

    if not clean:
        return None

    # Enforce the 1 KB cap. If over, drop the largest values until it fits.
    while clean:
        encoded = json.dumps(clean, separators=(",", ":"), ensure_ascii=False)
        if len(encoded.encode("utf-8")) <= _META_MAX_BYTES:
            return clean
        # drop the key whose value serialises largest
        biggest = max(
            clean,
            key=lambda kk: len(json.dumps({kk: clean[kk]}, ensure_ascii=False).encode("utf-8")),
        )
        del clean[biggest]
    return None


def _serialise_meta(meta: Optional[dict[str, Any]]) -> Optional[str]:
    if meta is None:
        return None
    return json.dumps(meta, separators=(",", ":"), ensure_ascii=False)


def record_event(
    service: str,
    surface: str,
    endpoint: str,
    *,
    status: Any = "ok",
    latency_ms: int = 0,
    bytes: int = 0,
    client_id: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> int:
    """Validate and persist a single event. Returns the new rowid.

    This is the low-level primitive the middleware/MCP wrapper/ingest call.
    """
    from . import db  # local import to avoid import cycle at module load

    event = Event(
        service=service,
        surface=surface,
        endpoint=endpoint,
        status=status,
        latency_ms=latency_ms,
        bytes=bytes,
        client_id=client_id,
        meta=meta,
    )
    return db.write_event(event.to_row(), path=db_path)


def record_download(
    service: str,
    path_or_file: str,
    *,
    status: Any = "ok",
    latency_ms: int = 0,
    bytes: int = 0,
    client_id: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> int:
    """Convenience wrapper for ``surface="download"`` events (§4 downloads)."""
    return record_event(
        service,
        "download",
        path_or_file,
        status=status,
        latency_ms=latency_ms,
        bytes=bytes,
        client_id=client_id,
        meta=meta,
        db_path=db_path,
    )
