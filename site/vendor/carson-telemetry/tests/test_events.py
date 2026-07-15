"""Event validation: surface whitelist, meta size/PII scrubbing."""
from __future__ import annotations

import json

import pytest

from carson_telemetry.events import Event, EventValidationError, sanitize_meta


def test_surface_whitelist():
    for s in ("mcp", "rest", "web", "download"):
        Event(service="x", surface=s, endpoint="e").validate()
    with pytest.raises(EventValidationError):
        Event(service="x", surface="ftp", endpoint="e").validate()


def test_required_fields():
    with pytest.raises(EventValidationError):
        Event(service="", surface="rest", endpoint="e").validate()
    with pytest.raises(EventValidationError):
        Event(service="x", surface="rest", endpoint="").validate()


def test_meta_must_be_dict():
    with pytest.raises(EventValidationError):
        Event(service="x", surface="rest", endpoint="e", meta="free text").validate()


def test_meta_pii_keys_stripped():
    cleaned = sanitize_meta({"ip": "1.2.3.4", "email": "a@b.com", "statistic": "GDP"})
    assert "ip" not in cleaned
    assert "email" not in cleaned
    assert cleaned["statistic"] == "GDP"


def test_meta_freetext_dropped():
    cleaned = sanitize_meta({"as_of": 1985, "query": "x" * 300, "note": "y" * 300})
    assert "query" not in cleaned  # banned key
    assert "note" not in cleaned   # long free text
    assert cleaned["as_of"] == 1985


def test_meta_size_cap_1kb():
    big = {f"k{i}": f"id{i}" for i in range(500)}  # serialises well over 1 KB
    cleaned = sanitize_meta(big)
    encoded = json.dumps(cleaned, separators=(",", ":")) if cleaned else "{}"
    assert len(encoded.encode("utf-8")) <= 1024


def test_to_row_serialises_meta():
    row = Event(service="x", surface="rest", endpoint="e",
                meta={"as_of": 1985}).to_row()
    assert row["meta"] == '{"as_of":1985}'
    assert row["status"] == "ok"
