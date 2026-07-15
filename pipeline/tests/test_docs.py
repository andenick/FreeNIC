"""Docs==DB consistency tests (Q7, Definitive Build, added 2026-06-08).

Every base table (main + catalog) must be documented in Outputs/DATA_DICTIONARY.md, and the dictionary
must not reference tables/views that no longer exist. A new undocumented table fails here until a
`### `name`` section is added. Keeps the public schema reference honest and in lockstep with the DB.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from utils import OUTPUTS_DIR  # noqa: E402

DD = OUTPUTS_DIR / "DATA_DICTIONARY.md"


def _documented():
    text = DD.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"^#{2,4}\s+`([a-zA-Z0-9_.]+)`", text, re.MULTILINE)}


def test_data_dictionary_exists():
    assert DD.is_file(), f"missing {DD}"


def test_every_base_table_documented(db):
    documented = _documented()
    main = [r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main' "
        "AND table_type='BASE TABLE'").fetchall()]
    cat = [r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='catalog' "
        "AND table_type='BASE TABLE'").fetchall()]
    missing = [t for t in main if t not in documented]
    missing += [f"catalog.{t}" for t in cat if f"catalog.{t}" not in documented and t not in documented]
    assert not missing, f"base tables missing from DATA_DICTIONARY.md: {sorted(missing)}"


def test_no_stale_doc_entries(db):
    """Every documented `name` must correspond to a live base table or view (no doc drift)."""
    documented = _documented()
    main = {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main' "
        "AND table_type='BASE TABLE'").fetchall()}
    cat = {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='catalog' "
        "AND table_type='BASE TABLE'").fetchall()}
    views = {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main' "
        "AND table_type='VIEW'").fetchall()}
    known = main | views | {f"catalog.{t}" for t in cat} | cat
    stale = [d for d in documented if d not in known]
    assert not stale, f"DATA_DICTIONARY.md documents non-existent tables: {sorted(stale)}"
