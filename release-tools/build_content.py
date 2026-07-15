#!/usr/bin/env python3
"""build_content.py — bake the dictionary content layer + per-schedule CSVs.

Two build-time products, both derived from reviewed, shipped-quality sources:

1. ``app/data/explanations.json`` — a clean merge of the two staging explanation
   files (``content/staging/explanations_y9c.json`` and
   ``content/staging/explanations_call_other.json``). The staging files stay the
   editable source of truth; this merges their ``schedules`` (from both),
   ``layers`` and ``categories`` into one file the app loads at render time.

2. ``app/static/dictionary_csv/<form>_<schedule>.csv`` — one CSV per schedule,
   exported from the dict line-item tables in the baked slice, so each schedule
   page can offer a per-schedule CSV download as a plain static file.

Pure read-only over the slice; writes only to ``app/data`` and ``app/static``.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import duckdb

# The runnable site app dir (holds content/, app/). Overridable by env (default: ../site).
SITE = Path(os.environ.get("FREENIC_SITE_DIR", str(Path(__file__).resolve().parent.parent / "site")))
STAGING = SITE / "content" / "staging"
OUT_JSON = SITE / "app" / "data" / "explanations.json"
CSV_DIR = SITE / "app" / "static" / "dictionary_csv"
SLICE = SITE / "app" / "data" / "freenic_slice.duckdb"


def merge_explanations() -> dict:
    """Merge the two staging explanation files into one content dict.

    schedules: union of both files' schedule blocks (Y-9C + Call/other).
    layers:    from the Call/other file (ubpr, fdic, luck_historical).
    categories: from the Call/other file (one paragraph per source family).
    """
    y9c = json.loads((STAGING / "explanations_y9c.json").read_text(encoding="utf-8"))
    other = json.loads((STAGING / "explanations_call_other.json").read_text(encoding="utf-8"))

    schedules: dict[str, dict] = {}
    schedules.update(y9c.get("schedules", {}))
    schedules.update(other.get("schedules", {}))

    merged = {
        "schedules": schedules,
        "layers": other.get("layers", {}),
        "categories": other.get("categories", {}),
    }
    OUT_JSON.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return merged


# Schedule-page CSV columns, in the order the line-item grid presents them.
_CSV_COLS = [
    "form_family", "schedule", "line_number", "item_description",
    "column_role", "mdrm_code", "forms", "start_date", "notes",
]


def bake_schedule_csvs() -> list[str]:
    """Write one CSV per (form_family, schedule) from the slice line-item table.

    Returns the list of slug filenames written (e.g. ``call_RC``). Uses a safe
    temp-write then atomic replace so a partial write never leaves a truncated CSV.
    """
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(SLICE), read_only=True)
    try:
        pairs = con.execute(
            "SELECT DISTINCT form_family, schedule FROM dict_schedule_lineitems "
            "WHERE schedule IS NOT NULL ORDER BY form_family, schedule"
        ).fetchall()
        written: list[str] = []
        for form_family, schedule in pairs:
            rows = con.execute(
                f"SELECT {', '.join(_CSV_COLS)} FROM dict_schedule_lineitems "
                "WHERE form_family = ? AND schedule = ? "
                "ORDER BY try_cast(line_number AS DOUBLE) NULLS LAST, line_number, mdrm_code",
                [form_family, schedule],
            ).fetchall()
            slug = _slug(form_family, schedule)
            target = CSV_DIR / f"{slug}.csv"
            tmp = target.with_suffix(".csv.tmp")
            with open(tmp, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(_CSV_COLS)
                for r in rows:
                    w.writerow(["" if v is None else v for v in r])
            tmp.replace(target)
            written.append(slug)
        return written
    finally:
        con.close()


def _slug(form_family: str, schedule: str) -> str:
    """Filesystem-safe slug for a (form_family, schedule) pair."""
    return f"{form_family}_{schedule}".replace("/", "-").replace(" ", "_")


def copy_sources_directory() -> int:
    """Copy the reviewed supplier directory into app/data (the shipped tree).

    The staging file is the editable source of truth; the app loads the copy in
    app/data so the container image carries it. Returns the source count.
    """
    src = json.loads((STAGING / "sources_directory.json").read_text(encoding="utf-8"))
    (SITE / "app" / "data" / "sources_directory.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(src.get("sources", []))


def main() -> None:
    merged = merge_explanations()
    print(f"explanations.json: {len(merged['schedules'])} schedules, "
          f"{len(merged['layers'])} layers, {len(merged['categories'])} categories")
    n_src = copy_sources_directory()
    print(f"sources_directory.json: {n_src} suppliers copied to app/data")
    slugs = bake_schedule_csvs()
    print(f"per-schedule CSVs: {len(slugs)} written to {CSV_DIR}")


if __name__ == "__main__":
    main()
