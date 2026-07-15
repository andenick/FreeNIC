"""Arcanum Site Kit (ASK) v1 — shared-chrome context processor (freenic).

Single mechanism that injects the shared header/footer/switcher variables into
**every** Jinja template render, regardless of which route builds the per-route
context. It is wired in ``main.py`` via::

    Jinja2Templates(directory=..., context_processors=[chrome.ark_context])

Starlette runs each context processor for every ``TemplateResponse`` (it receives
only the ``Request`` and returns a dict merged into the context), so no per-route
edits are needed and freenic's existing page variables (sources, tables, ...) are
preserved — the keys injected here (``ecosystem``, ``nav``, ``site_key``, ...) do
not collide with them.

Reference recipe: this mirrors leontief's app/chrome.py, but freenic has no
``app.config`` module, so paths and the site title are computed/declared locally.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from starlette.requests import Request

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Per-site identity (the only values another site changes)
# ---------------------------------------------------------------------------
SITE_KEY: str = "freenic"             # ecosystem.json site.key -> switcher "current"
SITE_TITLE: str = "FreeNIC"           # display name shown next to the brand mark
SITE_HOME: str = "/"                  # what the site title links to
# Provenance / DPR target (footer link). Wave 3 built a dedicated /methodology
# page (the .ark-provenance DPR panel) over the real curated slice — the footer
# "Provenance" link now points there (was "/" while the page did not exist).
DPR_URL: str = "/methodology"

# Blueprint nav vocabulary mapped to freenic's REAL routes. The Data / Code /
# Methodology blueprint sections (over the real ~5 MB slice) are linked. The
# access paths are the Explorer + Download CSV + the R/Python package and API —
# the SQL query box was removed. Every linked route exists and 200s (D2
# completeness). Each entry: (label, href). ``active`` is computed per request.
NAV: list[tuple[str, str]] = [
    ("Overview",     "/"),            # Landing / brand home
    ("Explore",      "/explorer"),    # real Plotly browser over the slice
    ("Institutions", "/institutions"),# name/RSSD lookup over the active-institutions slice
    ("Failures",     "/failures"),    # FDIC/Robin bank-failure explorer over the slice
    ("Dictionary",  "/dictionary"),  # searchable variable catalog over the dict taxonomy slice
    ("Data",        "/data"),        # downloads of the real slice tables (CSV/Parquet)
    ("Sources",     "/sources"),     # annotated directory of official data suppliers
    ("API",         "/api-docs"),    # access layers: REST endpoints, httpfs, py/R/MCP
    ("Code",        "/code"),        # the real app source + repro bundle
    ("Methodology", "/methodology"), # the DPR / provenance panel
]

# Vendored canonical manifest (served at /static/_shared/ecosystem.json).
_STATIC_DIR = Path(__file__).resolve().parent / "static"
_ECOSYSTEM_PATH = _STATIC_DIR / "_shared" / "ecosystem.json"


@lru_cache(maxsize=1)
def load_ecosystem() -> dict:
    """Parse the vendored ecosystem.json once (cached). Non-fatal on error."""
    try:
        with open(_ECOSYSTEM_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: BLE001 — chrome must never break a render
        logger.warning("ecosystem.json not loaded (%s): %s", _ECOSYSTEM_PATH, exc)
        return {}


def _nav_for(path: str) -> list[dict]:
    """Build the nav list with ``active`` set from the current request path.

    Path-derived (not section-derived) so it is route-agnostic: any route under a
    section's prefix lights the right tab. A nav item is active when the path
    equals its href or sits beneath it.
    """
    items: list[dict] = []
    for label, href in NAV:
        active = path == href or (href != "/" and path.startswith(href + "/"))
        items.append({"label": label, "href": href, "active": active})
    return items


def ark_context(request: Request) -> dict:
    """Starlette context processor — runs for every TemplateResponse."""
    return {
        "site_key": SITE_KEY,
        "site_title": SITE_TITLE,
        "site_home": SITE_HOME,
        "dpr_url": DPR_URL,
        "dpr_label": "Provenance",
        "ecosystem": load_ecosystem(),
        "nav": _nav_for(request.url.path),
    }
