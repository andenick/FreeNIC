"""FastMCP instrumentation (Carson Telemetry Standard §4).

``instrument_mcp(mcp, service=...)`` wraps a FastMCP instance so every tool
call emits ``surface="mcp"``, ``endpoint=<tool name>``, with status + latency.

It does NOT import ``mcp`` at module top (the package is an optional extra) and
must degrade gracefully across FastMCP versions whose internals differ. Strategy:

  1. Wrap ``mcp.tool`` (the decorator factory) so any tool registered *after*
     instrumentation is recorded — this is the primary, supported integration
     point and matches the §4 recipe (``mcp = telemetry.instrument_mcp(mcp, ...)``
     placed before tool registration, exactly like Methodex's
     ``for fn in TOOLS: mcp.tool()(fn)``).
  2. Best-effort wrap of an internal dispatch handler (``call_tool`` /
     ``_call_tool`` / a tool manager) so tools registered *before*
     instrumentation are still covered when the internals are recognisable.

If neither hook is found, the original ``mcp`` is returned unchanged (no-op
safe) and a one-line note is emitted to stderr — the service still runs.
"""
from __future__ import annotations

import functools
import inspect
import sys
import time
from typing import Any, Callable, Optional

from .events import record_event

# Names FastMCP has used across versions for "register a tool" / "dispatch a call".
_TOOL_DECORATOR_ATTRS = ("tool",)
_DISPATCH_ATTRS = ("call_tool", "_call_tool")


def _emit(service: str, tool_name: str, latency_ms: int, status: str, db_path: Optional[str]) -> None:
    try:
        record_event(
            service,
            "mcp",
            tool_name,
            status=status,
            latency_ms=latency_ms,
            client_id=None,  # MCP transport carries no client IP in-band
            meta=None,
            db_path=db_path,
        )
    except Exception:
        pass  # telemetry must never break a tool call


def _wrap_callable(fn: Callable, service: str, name: Optional[str], db_path: Optional[str]) -> Callable:
    tool_name = name or getattr(fn, "__name__", "unknown")

    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = "ok"
            try:
                return await fn(*args, **kwargs)
            except Exception:
                status = "error"
                raise
            finally:
                _emit(service, tool_name, int((time.perf_counter() - start) * 1000), status, db_path)
        return async_wrapper

    @functools.wraps(fn)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        status = "ok"
        try:
            return fn(*args, **kwargs)
        except Exception:
            status = "error"
            raise
        finally:
            _emit(service, tool_name, int((time.perf_counter() - start) * 1000), status, db_path)
    return sync_wrapper


def _instrument_tool_decorator(mcp: Any, service: str, db_path: Optional[str]) -> bool:
    """Wrap ``mcp.tool`` so newly-registered tools are instrumented.

    FastMCP's ``tool`` is a decorator factory: ``mcp.tool()(fn)`` or
    ``@mcp.tool()``. We intercept the inner decorator and substitute a wrapped
    function (so the timing wrapper is what actually gets registered/dispatched).
    """
    original_tool = getattr(mcp, "tool", None)
    if original_tool is None or not callable(original_tool):
        return False

    @functools.wraps(original_tool)
    def tool_factory(*d_args, **d_kwargs):
        inner = original_tool(*d_args, **d_kwargs)

        def decorator(fn: Callable) -> Callable:
            # Honour an explicit name=... passed to mcp.tool(name=...).
            name = d_kwargs.get("name")
            wrapped = _wrap_callable(fn, service, name, db_path)
            # Register the wrapped function; return what FastMCP returns.
            return inner(wrapped)

        return decorator

    try:
        mcp.tool = tool_factory  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def _instrument_dispatch(mcp: Any, service: str, db_path: Optional[str]) -> bool:
    """Best-effort: wrap an internal dispatch method to cover pre-registered tools."""
    for attr in _DISPATCH_ATTRS:
        target = getattr(mcp, attr, None)
        if target is None or not callable(target):
            continue
        original = target

        if inspect.iscoroutinefunction(original):
            @functools.wraps(original)
            async def wrapper(name, *args, __orig=original, **kwargs):  # type: ignore[misc]
                start = time.perf_counter()
                status = "ok"
                try:
                    return await __orig(name, *args, **kwargs)
                except Exception:
                    status = "error"
                    raise
                finally:
                    tn = name if isinstance(name, str) else getattr(name, "name", str(name))
                    _emit(service, tn, int((time.perf_counter() - start) * 1000), status, db_path)
        else:
            @functools.wraps(original)
            def wrapper(name, *args, __orig=original, **kwargs):  # type: ignore[misc]
                start = time.perf_counter()
                status = "ok"
                try:
                    return __orig(name, *args, **kwargs)
                except Exception:
                    status = "error"
                    raise
                finally:
                    tn = name if isinstance(name, str) else getattr(name, "name", str(name))
                    _emit(service, tn, int((time.perf_counter() - start) * 1000), status, db_path)

        try:
            setattr(mcp, attr, wrapper)
            return True
        except Exception:
            continue
    return False


def instrument_mcp(mcp: Any, service: str, *, db_path: Optional[str] = None) -> Any:
    """Instrument a FastMCP instance in place; return it (for the §4 one-liner).

    Idempotent: calling twice will not double-wrap (guarded by a marker attr).
    """
    if getattr(mcp, "_carson_instrumented", False):
        return mcp

    hooked = _instrument_tool_decorator(mcp, service, db_path)
    # Dispatch wrapping is additive only when it clearly exists; ignore failures.
    _instrument_dispatch(mcp, service, db_path)

    if not hooked:
        print(
            "[carson-telemetry] instrument_mcp: could not find a known FastMCP "
            "'tool' decorator on the supplied object; returning it unwrapped "
            "(MCP telemetry disabled, service unaffected).",
            file=sys.stderr,
        )

    try:
        mcp._carson_instrumented = True  # type: ignore[attr-defined]
    except Exception:
        pass
    return mcp
