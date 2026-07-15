"""instrument_mcp emits a row for a dummy FastMCP-like object (no `mcp` needed)."""
from __future__ import annotations

from carson_telemetry import db
from carson_telemetry.mcp import instrument_mcp


class FakeFastMCP:
    """A minimal stand-in mimicking FastMCP's `tool()` decorator factory.

    Real FastMCP: `mcp.tool()(fn)` registers `fn`. Here `tool()` returns a
    decorator that stores the (possibly wrapped) callable so we can dispatch it.
    """

    def __init__(self):
        self.registry = {}

    def tool(self, *args, name=None, **kwargs):
        def decorator(fn):
            self.registry[name or fn.__name__] = fn
            return fn
        return decorator


def test_instrument_mcp_emits_row(telemetry_env):
    mcp = FakeFastMCP()
    mcp = instrument_mcp(mcp, service="methodex", db_path=telemetry_env["db_path"])

    @mcp.tool()
    def get_methodology(statistic_id, as_of):
        return {"ok": statistic_id}

    # Dispatch the registered (wrapped) tool, as FastMCP would on a call.
    result = mcp.registry["get_methodology"]("US.BEA.GDP", 1985)
    assert result == {"ok": "US.BEA.GDP"}

    rows = db.fetch_events(path=telemetry_env["db_path"], service="methodex")
    assert len(rows) == 1
    r = rows[0]
    assert r["surface"] == "mcp"
    assert r["endpoint"] == "get_methodology"
    assert r["status"] == "ok"


def test_instrument_mcp_records_error_status(telemetry_env):
    mcp = instrument_mcp(FakeFastMCP(), service="svc", db_path=telemetry_env["db_path"])

    @mcp.tool()
    def boom():
        raise RuntimeError("nope")

    try:
        mcp.registry["boom"]()
    except RuntimeError:
        pass

    rows = db.fetch_events(path=telemetry_env["db_path"], service="svc")
    assert rows[0]["status"] == "error"


def test_instrument_mcp_idempotent(telemetry_env):
    mcp = FakeFastMCP()
    a = instrument_mcp(mcp, service="svc", db_path=telemetry_env["db_path"])
    b = instrument_mcp(a, service="svc", db_path=telemetry_env["db_path"])
    assert a is b


def test_instrument_mcp_no_tool_attr_is_noop(telemetry_env):
    class NoTool:
        pass

    obj = NoTool()
    # Should not raise; returns the object unwrapped.
    assert instrument_mcp(obj, service="svc") is obj
