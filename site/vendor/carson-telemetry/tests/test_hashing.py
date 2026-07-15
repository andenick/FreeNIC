"""Daily-salted client hashing: stable within a day, differs across salt/date."""
from __future__ import annotations

from carson_telemetry import hashing


def test_hash_stable_within_day(telemetry_env):
    ip = "203.0.113.7"
    a = hashing.hash_client(ip, day="2026-06-05")
    b = hashing.hash_client(ip, day="2026-06-05")
    assert a == b
    assert a is not None
    assert len(a) == 16


def test_hash_differs_across_days(telemetry_env):
    ip = "203.0.113.7"
    d1 = hashing.hash_client(ip, day="2026-06-05")
    d2 = hashing.hash_client(ip, day="2026-06-06")
    assert d1 != d2  # rotating daily salt -> unlinkable across days


def test_hash_differs_with_explicit_salt(telemetry_env):
    ip = "203.0.113.7"
    h1 = hashing.hash_client(ip, salt="salt-A")
    h2 = hashing.hash_client(ip, salt="salt-B")
    assert h1 != h2


def test_none_ip_returns_none(telemetry_env):
    assert hashing.hash_client(None) is None
    assert hashing.hash_client("") is None


def test_salt_persisted_file(telemetry_env):
    s1 = hashing.get_daily_salt("2026-06-05")
    s2 = hashing.get_daily_salt("2026-06-05")
    assert s1 == s2  # second read comes from the persisted file
    assert len(s1) >= 32


def test_raw_ip_not_in_hash(telemetry_env):
    ip = "198.51.100.42"
    h = hashing.hash_client(ip, day="2026-06-05")
    assert ip not in h
