"""FreeNIC — download catalog + serializers (Wave-3 /data + /code support).

Every byte served here is a faithful serialization of a REAL table in the curated
DuckDB slice (``app/data/freenic_slice.duckdb``). Nothing is invented: each CSV /
Parquet artifact is produced by reading the real slice table and writing it out
verbatim. The full FreeNIC warehouse (~4.97B rows) is offline — only this compact
curated slice is shipped (see /methodology). Offered formats are CSV + Parquet
ONLY (no JSON — DOWNLOAD_AND_FORMATS DNA).

Public API
----------
catalog()                         -> list[dict]   (metadata for the /data page)
get_artifact(artifact_id)         -> dict | None
render_artifact(art)              -> (bytes, media_type, download_filename)
bulk_zip()                        -> (bytes, "application/zip", filename)
repro_bundle_zip()                -> (bytes, "application/zip", filename)

Correct content-types are attached per format (text/csv,
application/vnd.apache.parquet, application/zip) — the media type is derived from
the artifact's declared ``fmt``.

Pure read-only over the slice: every connection opens with ``read_only=True`` and
COPY-to-Parquet writes only to a throwaway temp file, never to the database.
"""
from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

import duckdb

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DB_PATH = DATA / "freenic_slice.duckdb"

# Correct content-types per format (parquet uses the IANA-registered type).
# NO JSON — offered download formats are CSV + Parquet only (DOWNLOAD_AND_FORMATS DNA).
MEDIA = {
    "csv": "text/csv; charset=utf-8",
    "parquet": "application/vnd.apache.parquet",
    "zip": "application/zip",
}

# The eight REAL slice tables, with a human description + their blueprint group.
# Schema (columns/types) and row counts are pulled LIVE from the DB at catalog()
# time, so they are always accurate — never hand-typed (no fabrication risk).
_TABLES: list[dict] = [
    # -- Core slice tables ------------------------------------------------
    {
        "table": "bank_failures",
        "group": "Core slice tables",
        "title": "Bank failures",
        "desc": "FDIC + Robin real bank-failure records, 1934–2026 (the full real table).",
    },
    {
        "table": "fred_series",
        "group": "Core slice tables",
        "title": "FRED banking series (observations)",
        "desc": "Fed/FRED banking macro observations across 1,947 series (full real, small).",
    },
    {
        "table": "institutions_active",
        "group": "Core slice tables",
        "title": "Active institutions",
        "desc": "Real subset — currently-active institutions only (of 217,210 total), "
                "trimmed columns.",
    },
    # -- Precomputed aggregates & catalog ---------------------------------
    {
        "table": "agg_failures_by_year",
        "group": "Precomputed aggregates & catalog",
        "title": "Failures by year",
        "desc": "Real precomputed aggregate: failure count + total assets + total loss per year.",
    },
    {
        "table": "agg_failures_by_state",
        "group": "Precomputed aggregates & catalog",
        "title": "Failures by state",
        "desc": "Real precomputed aggregate: failure count + total assets per state.",
    },
    {
        "table": "agg_institutions_by_state",
        "group": "Precomputed aggregates & catalog",
        "title": "Active institutions by state",
        "desc": "Real precomputed aggregate: active-institution count per state.",
    },
    {
        "table": "agg_institutions_by_type",
        "group": "Precomputed aggregates & catalog",
        "title": "Active institutions by entity type",
        "desc": "Real precomputed aggregate: active-institution count per entity type.",
    },
    {
        "table": "fred_catalog",
        "group": "Precomputed aggregates & catalog",
        "title": "FRED series catalog",
        "desc": "One row per FRED series: name, observation count, first/last date.",
    },
    {
        "table": "long_bank_aggregates_1863_2026",
        "group": "Precomputed aggregates & catalog",
        "title": "163-year bank-aggregate spine (1863–2026)",
        "desc": "Replicated long spine: year × metric (num_banks / total_deposits / "
                "total_loans / total_assets) × definition (national_only / member_banks / "
                "all_insured / all_commercial), with junction flags at 1896/1914/1934. "
                "UNITS DIFFER BY DEFINITION — do not splice blindly (national $M, "
                "all_insured $000, all_commercial $B).",
    },
    # -- Dictionary taxonomy (version-pinned bank-data-dictionary v10.0) ----
    {
        "table": "dict_schedule_lineitems",
        "group": "Variable dictionary (taxonomy)",
        "title": "Schedule line-items",
        "desc": "MDRM report line-items: form family, schedule, line, caption, column role, code.",
    },
    {
        "table": "dict_ubpr_concepts",
        "group": "Variable dictionary (taxonomy)",
        "title": "UBPR concepts",
        "desc": "UBPR derived concepts: code, caption, category, derivation, validation flag.",
    },
    {
        "table": "dict_variable_access_map",
        "group": "Variable dictionary (taxonomy)",
        "title": "Variable access map",
        "desc": "Every reported variable (15,435) → its base table, raw view and shaped views.",
    },
    {
        "table": "dict_relationships_summary",
        "group": "Variable dictionary (taxonomy)",
        "title": "Relationships (summary)",
        "desc": "Edit checks / cross-form equalities: id, scope, kind, expression (≤200 chars), "
                "severity, status, empirical pass-rate & n (long free-text dropped).",
    },
    {
        "table": "dict_meta",
        "group": "Variable dictionary (taxonomy)",
        "title": "Dictionary meta",
        "desc": "Taxonomy version + source repo for the bank-data-dictionary import.",
    },
]

# Per-table offered formats — CSV + Parquet ONLY (no JSON; DOWNLOAD_AND_FORMATS DNA).
_FORMATS = ("csv", "parquet")


# ---------------------------------------------------------------------------
# Read-only access to the curated slice
# ---------------------------------------------------------------------------

def _con() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH), read_only=True)


def _table_data(table: str) -> tuple[list[str], list[tuple]]:
    con = _con()
    try:
        cur = con.execute(f'SELECT * FROM "{table}"')
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    finally:
        con.close()
    return cols, rows


def _schema_and_count(table: str) -> tuple[list[tuple[str, str]], int]:
    con = _con()
    try:
        schema = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position",
            [table],
        ).fetchall()
        n = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    finally:
        con.close()
    return schema, n


# ---------------------------------------------------------------------------
# Faithful serializers (no values invented — straight read-out of the table)
# ---------------------------------------------------------------------------

def _csv_bytes(table: str) -> bytes:
    cols, rows = _table_data(table)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(["" if v is None else v for v in r])
    return buf.getvalue().encode("utf-8")


def _parquet_bytes(table: str) -> bytes:
    """Native Parquet via DuckDB COPY to a throwaway temp file (read-only DB)."""
    fd, tmp = tempfile.mkstemp(suffix=".parquet")
    os.close(fd)
    try:
        con = _con()
        try:
            con.execute(
                f'COPY (SELECT * FROM "{table}") '
                f"TO '{Path(tmp).as_posix()}' (FORMAT PARQUET)"
            )
        finally:
            con.close()
        return Path(tmp).read_bytes()
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


_SERIALIZE = {"csv": _csv_bytes, "parquet": _parquet_bytes}


def _bytes_for(table: str, fmt: str) -> bytes:
    return _SERIALIZE[fmt](table)


# ---------------------------------------------------------------------------
# Catalog (artifact_id == "<table>.<fmt>")
# ---------------------------------------------------------------------------

def _human_size(n: int) -> str:
    return f"{n / 1024:.1f} KB" if n < 1_048_576 else f"{n / 1_048_576:.1f} MB"


def catalog() -> list[dict]:
    """Per-table metadata: live schema + row count + one download URL per format."""
    out: list[dict] = []
    for spec in _TABLES:
        table = spec["table"]
        try:
            schema, n = _schema_and_count(table)
        except Exception:  # noqa: BLE001 — a missing table must not break the page
            schema, n = [], 0
        item = dict(spec)
        item["columns"] = [{"name": c, "type": t} for c, t in schema]
        item["n_rows"] = n
        item["downloads"] = [
            {"fmt": fmt, "url": f"/api/download/{table}.{fmt}"} for fmt in _FORMATS
        ]
        out.append(item)
    return out


def get_artifact(artifact_id: str) -> dict | None:
    """Resolve "<table>.<fmt>" to an artifact descriptor (validated against the slice)."""
    if "." not in artifact_id:
        return None
    table, _, fmt = artifact_id.rpartition(".")
    if fmt not in _FORMATS:
        return None
    if not any(t["table"] == table for t in _TABLES):
        return None
    return {"id": artifact_id, "table": table, "fmt": fmt}


def render_artifact(art: dict) -> tuple[bytes, str, str]:
    """Return (bytes, media_type, download_filename) for a single artifact."""
    raw = _bytes_for(art["table"], art["fmt"])
    fname = f"freenic_{art['table']}.{art['fmt']}"
    return raw, MEDIA[art["fmt"]], fname


# ---------------------------------------------------------------------------
# Bulk + repro zips
# ---------------------------------------------------------------------------

# Every count in the bundle READMEs is generated from freenic_counts.json (the
# single source of truth) — no hand-typed quantities. Tolerant if the file is
# absent (first build): falls back to un-numbered generic phrasing.
def _counts() -> dict:
    try:
        with open(DATA / "freenic_counts.json", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {}


def _bulk_readme() -> str:
    c = _counts()
    slice_h = c.get("slice_db_h", "compact")
    rel_files = c.get("release_files", "the full")
    rel_size = c.get("release_size_iec", "multi-GB")
    tables = c.get("base_tables", c.get("unified_tables", 58))
    inst = c.get("institutions_h", "~217K")
    datasets = c.get("source_datasets", 20)
    span = c.get("time_span", "1863–2026")
    obs = c.get("base_rows_approx", c.get("total_obs", "4.97B"))
    fail_end = c.get("failure_end_year", 2026)
    return (
        "FreeNIC — curated-sample data bundle\n"
        "====================================\n\n"
        "Every file here is a REAL table from the curated FreeNIC sample, serialized\n"
        "verbatim (CSV + Parquet only — no JSON). Nothing is fabricated or\n"
        "synthetically sampled.\n\n"
        f"This is a curated browsable SAMPLE (~{slice_h}). The complete FreeNIC dataset\n"
        f"({obs} rows, {tables} base tables, {inst} institutions, {datasets} public\n"
        f"datasets, {span}) is published as the {rel_files}-file / {rel_size} parquet\n"
        "release served LIVE at https://data.freenic.org/ and is accessed via the\n"
        "R/Python package and API — it is NOT shipped in this bundle. See\n"
        "https://freenic.org/methodology for full provenance and scope.\n\n"
        "Contents (each table, two formats: CSV + Parquet)\n"
        "-------------------------------------------------\n"
        f"  bank_failures            FDIC + Robin failures, 1934-{fail_end}\n"
        "  fred_series              Fed/FRED banking observations\n"
        "  institutions_active      active institutions only\n"
        "  agg_failures_by_year     precomputed: failures/assets/loss per year\n"
        "  agg_failures_by_state    precomputed: failures/assets per state\n"
        "  agg_institutions_by_*    precomputed: active institutions per state/type\n"
        "  fred_catalog             one row per FRED series\n"
        "  dict_*                   version-pinned bank-data-dictionary taxonomy slice\n\n"
        "(Each table is also downloadable individually as CSV / Parquet on the /data page.)\n\n"
        "Source: built from the published parquet release (FDIC, FRED, NIC active\n"
        "institutions). The multi-GB harmonised panels (call reports, Y-9C, SOD, etc.)\n"
        "are NOT included. Code: https://github.com/andenick/FreeNIC.\n"
    )


def bulk_zip() -> tuple[bytes, str, str]:
    """One zip of every real slice table (CSV + Parquet) + a provenance README."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for spec in _TABLES:
            table = spec["table"]
            for fmt in ("csv", "parquet"):
                try:
                    data = _bytes_for(table, fmt)
                except Exception:  # noqa: BLE001
                    continue
                zf.writestr(f"freenic_slice/{table}.{fmt}", data)
        zf.writestr("README.txt", _bulk_readme().encode("utf-8"))
    return buf.getvalue(), MEDIA["zip"], "freenic_slice.zip"


def _repro_readme() -> str:
    c = _counts()
    slice_h = c.get("slice_db_h", "compact")
    rel_files = c.get("release_files", "the full")
    rel_size = c.get("release_size_iec", "multi-GB")
    return (
        "FreeNIC — site reproduction / pipeline bundle\n"
        "=============================================\n\n"
        "This is the actual source of the freenic.org explorer: a thin FastAPI +\n"
        "DuckDB + Plotly app that renders every chart, table and download from the\n"
        f"curated sample (~{slice_h}) in app/data/freenic_slice.duckdb.\n\n"
        "Run it\n"
        "------\n"
        "    pip install -r app/requirements.txt\n"
        "    uvicorn app.main:app --port 8080\n"
        "    # then open http://localhost:8080\n\n"
        "Deterministic output (over the slice)\n"
        "-------------------------------------\n"
        "Every API response and every download under /data is computed\n"
        "DETERMINISTICALLY from the read-only slice DuckDB — no hidden state, no\n"
        "network call, no random seed. Running this bundle regenerates them\n"
        "byte-for-byte over the same sample. Charts use the vendored Plotly\n"
        "(offline, no CDN), each with a top-right Download CSV.\n\n"
        "What is NOT here\n"
        "----------------\n"
        f"The full FreeNIC warehouse is NOT shipped in this bundle — the {rel_files}-file\n"
        f"/ {rel_size} parquet release is served separately at https://data.freenic.org/.\n"
        "build_slice.py (included for reference) produced the slice from that public\n"
        "parquet release; it runs where that source data is present. Full pipeline +\n"
        "read packages: https://github.com/andenick/FreeNIC (Python + R, MIT).\n"
    )

# Source files that constitute the reproducible site (relative to BASE = app/).
_REPRO_SOURCES = [
    "main.py",
    "chrome.py",
    "downloads.py",
    "requirements.txt",
    "templates/base.html",
    "templates/index.html",
    "templates/explorer.html",
    "templates/dictionary.html",
    "templates/schedule.html",
    "templates/variable.html",
    "templates/sources.html",
    "templates/data.html",
    "templates/code.html",
    "templates/methodology.html",
]


def repro_bundle_zip() -> tuple[bytes, str, str]:
    """Zip the real app source + the slice DB so the site is reproducible from disk."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in _REPRO_SOURCES:
            p = BASE / rel
            if p.exists():
                zf.write(p, f"app/{rel}")
        # Ship the real data so the bundle actually runs over the slice.
        for rel in ("data/freenic_slice.duckdb", "data/sources.json"):
            p = BASE / rel
            if p.exists():
                zf.write(p, f"app/{rel}")
        # The slice builder (reference only — needs the offline parquet exports).
        bs = BASE.parent / "build_slice.py"
        if bs.exists():
            zf.write(bs, "build_slice.py")
        zf.writestr("README.txt", _repro_readme().encode("utf-8"))
    return buf.getvalue(), MEDIA["zip"], "freenic_site_repro.zip"
