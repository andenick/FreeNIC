"""Read-only telemetry dashboard (Carson Telemetry Standard §5).

Tailscale-only admin surface over ``telemetry.db``. FastAPI/Jinja2 are optional
extras (``pip install 'carson-telemetry[fastapi]'``); nothing here is imported
by the stdlib-only core.
"""
