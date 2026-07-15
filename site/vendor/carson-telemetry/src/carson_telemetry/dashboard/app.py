"""FastAPI + Jinja2 read-only dashboard (Carson Telemetry Standard §5).

SECURITY: this is an admin surface. It MUST bind to the Tailscale interface only
(its tailnet IP, e.g. 100.x.y.z) — NEVER 0.0.0.0 and never a public address. The
``main()`` entry point defaults to 127.0.0.1 and refuses 0.0.0.0 unless
``--i-know-this-is-not-public`` is passed. Front it with Tailscale ACLs.

FastAPI/Starlette/Jinja2/uvicorn are the ``[fastapi]`` optional extra. Importing
this module without them raises a clear error; the stdlib core never imports it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .queries import overview

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def create_app(db_path: Optional[str] = None):
    """Build the FastAPI app. Raises ImportError if the [fastapi] extra is absent."""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse, JSONResponse
        from fastapi.templating import Jinja2Templates
    except ImportError as exc:  # pragma: no cover - exercised only without extra
        raise ImportError(
            "carson-telemetry dashboard requires the [fastapi] extra: "
            "pip install 'carson-telemetry[fastapi]'"
        ) from exc

    app = FastAPI(title="Carson Telemetry Dashboard", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, service: Optional[str] = None):
        data = overview(db_path, service=service)
        return templates.TemplateResponse(
            "index.html", {"request": request, "d": data}
        )

    @app.get("/api/overview", response_class=JSONResponse)
    def api_overview(service: Optional[str] = None):
        return overview(db_path, service=service)

    @app.get("/healthz", response_class=JSONResponse)
    def healthz():
        return {"ok": True}

    return app


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="carson-telemetry-dash",
        description="Read-only telemetry dashboard. TAILSCALE-ONLY — never bind public.",
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address — use the box's Tailscale IP (100.x.y.z). Default 127.0.0.1.")
    parser.add_argument("--port", type=int, default=9101)
    parser.add_argument("--db", default=None, help="override CARSON_TELEMETRY_DB")
    parser.add_argument("--i-know-this-is-not-public", action="store_true",
                        help="acknowledge binding to a non-loopback address (must still be Tailscale-only)")
    args = parser.parse_args(argv)

    if args.host in ("0.0.0.0", "::") and not args.i_know_this_is_not_public:
        print("[carson-telemetry-dash] REFUSING to bind to a wildcard address. "
              "This dashboard is a Tailscale-only admin surface. Pass the box's "
              "Tailscale IP as --host (recommended), or 127.0.0.1.", file=sys.stderr)
        return 2

    try:
        import uvicorn
    except ImportError:
        print("[carson-telemetry-dash] requires the [fastapi] extra "
              "(uvicorn). pip install 'carson-telemetry[fastapi]'", file=sys.stderr)
        return 1

    app = create_app(args.db)
    print(f"[carson-telemetry-dash] http://{args.host}:{args.port}  (Tailscale-only — do not expose)")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
