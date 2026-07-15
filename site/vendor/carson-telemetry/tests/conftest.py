"""Shared pytest fixtures: isolate the DB and salt dir per test (no network)."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

# Make the in-repo src/ importable without an editable install.
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


@pytest.fixture()
def telemetry_env(tmp_path, monkeypatch):
    """Point the DB + salt dir at a fresh temp location for each test."""
    db_path = tmp_path / "telemetry.db"
    salt_dir = tmp_path / "salt"
    ingest_dir = tmp_path / "ingest"
    salt_dir.mkdir()
    ingest_dir.mkdir()
    monkeypatch.setenv("CARSON_TELEMETRY_DB", str(db_path))
    monkeypatch.setenv("CARSON_TELEMETRY_SALT_DIR", str(salt_dir))
    monkeypatch.setenv("CARSON_TELEMETRY_INGEST_DIR", str(ingest_dir))

    # Ensure modules pick up env at call-time (they read env lazily, so just init).
    from carson_telemetry import db
    db.init_db(str(db_path))

    return {
        "db_path": str(db_path),
        "salt_dir": str(salt_dir),
        "ingest_dir": str(ingest_dir),
    }
