"""Stdlib-only read queries for the dashboard (no FastAPI dependency).

Kept separate from ``app.py`` so the SQL is unit-testable without installing the
``[fastapi]`` extra.
"""
from __future__ import annotations

import math
from typing import Any, Optional

from .. import db


def _percentile(sorted_vals: list[int], pct: float) -> int:
    if not sorted_vals:
        return 0
    if len(sorted_vals) == 1:
        return int(sorted_vals[0])
    rank = math.ceil(pct / 100.0 * len(sorted_vals))
    rank = max(1, min(rank, len(sorted_vals)))
    return int(sorted_vals[rank - 1])


def overview(db_path: Optional[str] = None, *, service: Optional[str] = None) -> dict[str, Any]:
    """Compute the dashboard panels from raw ``usage_events``."""
    conn = db.get_connection(db_path)
    try:
        where = "WHERE service = ?" if service else ""
        params: tuple = (service,) if service else ()

        total = conn.execute(
            f"SELECT COUNT(*) AS n FROM usage_events {where}", params
        ).fetchone()["n"]

        services = [
            dict(r) for r in conn.execute(
                "SELECT service, COUNT(*) AS calls FROM usage_events "
                "GROUP BY service ORDER BY calls DESC"
            ).fetchall()
        ]

        top_endpoints = [
            dict(r) for r in conn.execute(
                f"SELECT surface, endpoint, COUNT(*) AS calls "
                f"FROM usage_events {where} "
                f"GROUP BY surface, endpoint ORDER BY calls DESC LIMIT 25", params
            ).fetchall()
        ]

        over_time = [
            dict(r) for r in conn.execute(
                f"SELECT substr(ts,1,10) AS day, COUNT(*) AS calls "
                f"FROM usage_events {where} "
                f"GROUP BY day ORDER BY day", params
            ).fetchall()
        ]

        uniq = conn.execute(
            f"SELECT COUNT(DISTINCT client_id) AS u FROM usage_events {where}"
            + (" AND" if where else " WHERE") + " client_id IS NOT NULL",
            params,
        ).fetchone()["u"]

        err_rows = conn.execute(
            f"SELECT status FROM usage_events {where}", params
        ).fetchall()
        errors = sum(
            1 for r in err_rows
            if str(r["status"]) == "error"
            or (str(r["status"]).isdigit() and int(r["status"]) >= 400)
        )
        error_rate = (errors / total) if total else 0.0

        lats = sorted(
            int(r["latency_ms"] or 0)
            for r in conn.execute(
                f"SELECT latency_ms FROM usage_events {where}", params
            ).fetchall()
        )
        p50 = _percentile(lats, 50)
        p95 = _percentile(lats, 95)

        return {
            "service": service,
            "total_calls": total,
            "services": services,
            "top_endpoints": top_endpoints,
            "over_time": over_time,
            "unique_clients": uniq,
            "errors": errors,
            "error_rate": round(error_rate, 4),
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
        }
    finally:
        conn.close()
