"""Nightly rollup + retention prune (Carson Telemetry Standard §5).

Aggregates raw ``usage_events`` into ``usage_daily(service, surface, endpoint,
day, count, uniq, err, p95)`` and prunes raw events older than the retention
window (default 400 days, configurable). Idempotent: re-running upserts the same
daily rows (a re-run after more events arrive updates the affected days).

Entry point: ``carson-telemetry-rollup``.
"""
from __future__ import annotations

import argparse
import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import db

_DEFAULT_RETENTION_DAYS = 400


def _percentile(sorted_vals: list[int], pct: float) -> int:
    """Nearest-rank percentile over a pre-sorted list (returns int ms)."""
    if not sorted_vals:
        return 0
    if len(sorted_vals) == 1:
        return int(sorted_vals[0])
    rank = math.ceil(pct / 100.0 * len(sorted_vals))
    rank = max(1, min(rank, len(sorted_vals)))
    return int(sorted_vals[rank - 1])


def rollup(
    *,
    db_path: Optional[str] = None,
    retention_days: int = _DEFAULT_RETENTION_DAYS,
    prune: bool = True,
) -> dict:
    """Build/refresh ``usage_daily`` and optionally prune old raw events.

    Returns a small summary dict (days_written, rows_pruned).
    """
    conn = db.get_connection(db_path)
    try:
        # Pull raw rows grouped by (service, surface, endpoint, day). We compute
        # p95 in Python so it works on any SQLite build (no percentile UDF).
        cur = conn.execute(
            "SELECT service, surface, endpoint, substr(ts, 1, 10) AS day, "
            "       status, latency_ms, client_id "
            "FROM usage_events"
        )
        buckets: dict[tuple, dict] = {}
        for row in cur.fetchall():
            key = (row["service"], row["surface"], row["endpoint"], row["day"])
            b = buckets.setdefault(
                key, {"count": 0, "err": 0, "lat": [], "clients": set()}
            )
            b["count"] += 1
            status = str(row["status"])
            is_err = status == "error" or (status.isdigit() and int(status) >= 400)
            if is_err:
                b["err"] += 1
            b["lat"].append(int(row["latency_ms"] or 0))
            if row["client_id"]:
                b["clients"].add(row["client_id"])

        days_written = 0
        for (service, surface, endpoint, day), b in buckets.items():
            b["lat"].sort()
            p95 = _percentile(b["lat"], 95)
            conn.execute(
                "INSERT INTO usage_daily "
                "(service, surface, endpoint, day, count, uniq, err, p95) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(service, surface, endpoint, day) DO UPDATE SET "
                "count=excluded.count, uniq=excluded.uniq, err=excluded.err, p95=excluded.p95",
                (service, surface, endpoint, day, b["count"], len(b["clients"]), b["err"], p95),
            )
            days_written += 1

        rows_pruned = 0
        if prune and retention_days is not None and retention_days >= 0:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            del_cur = conn.execute("DELETE FROM usage_events WHERE ts < ?", (cutoff,))
            rows_pruned = del_cur.rowcount or 0

        return {"days_written": days_written, "rows_pruned": rows_pruned}
    finally:
        conn.close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="carson-telemetry-rollup",
                                     description="Aggregate usage_events -> usage_daily and prune old raw events.")
    parser.add_argument("--db", default=None, help="override CARSON_TELEMETRY_DB")
    parser.add_argument("--retention-days", type=int, default=_DEFAULT_RETENTION_DAYS,
                        help=f"raw-event retention window (default {_DEFAULT_RETENTION_DAYS})")
    parser.add_argument("--no-prune", action="store_true", help="aggregate only; keep all raw events")
    args = parser.parse_args(argv)

    summary = rollup(db_path=args.db, retention_days=args.retention_days, prune=not args.no_prune)
    print(f"[carson-telemetry-rollup] usage_daily rows upserted: {summary['days_written']}; "
          f"raw events pruned: {summary['rows_pruned']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
