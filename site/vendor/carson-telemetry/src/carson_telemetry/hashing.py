"""Privacy-preserving client identity hashing (Carson Telemetry Standard §3, §6).

client_id = sha256(client_ip + daily_salt)[:16]

The salt rotates by UTC date and is persisted to a per-day file so that, within
a single UTC day, every worker/process produces the SAME hash for the same IP
(needed for "distinct-ish clients today") while across days the same IP yields
an unlinkable hash. The raw IP is NEVER stored — only the truncated hash.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_SALT_DIR_POSIX = "/var/lib/carson/salt"
_HASH_LEN = 16  # hex chars kept from the digest


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _salt_dir() -> Path:
    raw = os.environ.get("CARSON_TELEMETRY_SALT_DIR")
    if raw:
        d = Path(raw)
    else:
        d = Path(_DEFAULT_SALT_DIR_POSIX)
    try:
        d.mkdir(parents=True, exist_ok=True)
        if not os.access(d, os.W_OK):
            raise PermissionError(d)
        return d
    except (OSError, PermissionError):
        import tempfile

        fb = Path(tempfile.gettempdir()) / "carson_telemetry_salt"
        fb.mkdir(parents=True, exist_ok=True)
        return fb


def get_daily_salt(day: Optional[str] = None) -> str:
    """Return the salt for ``day`` (UTC date string, default today).

    Persists a freshly-generated salt the first time a day is seen so all
    processes agree within the day. Reads are tolerant of races (two processes
    writing the same new day): whoever wrote first wins, and the loser re-reads.
    """
    day = day or _utc_today()
    salt_file = _salt_dir() / f"salt_{day}.txt"
    if salt_file.exists():
        try:
            return salt_file.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    new_salt = secrets.token_hex(32)
    try:
        # Exclusive create: if another worker already wrote it, fall through and read.
        with open(salt_file, "x", encoding="utf-8") as fh:
            fh.write(new_salt)
        return new_salt
    except FileExistsError:
        return salt_file.read_text(encoding="utf-8").strip()


def hash_client(ip: Optional[str], *, day: Optional[str] = None, salt: Optional[str] = None) -> Optional[str]:
    """Hash a client IP into a daily-salted, truncated, non-reversible id.

    Returns None if no IP is available (we never invent one). The raw IP is not
    retained by this function or anything it calls.
    """
    if not ip:
        return None
    daily_salt = salt if salt is not None else get_daily_salt(day)
    digest = hashlib.sha256((str(ip) + daily_salt).encode("utf-8")).hexdigest()
    return digest[:_HASH_LEN]
