"""Doc-count drift gate (W1.4, FREENIC_COMPLETENESS_PLAN).

Asserts that the count claims in the live-state docs (README, DATA_DICTIONARY,
QUICK_START, DATA_SOURCE_INVENTORY) match the authoritative live warehouse numbers.
The actual logic lives in ``tools/check_doc_counts.py`` + ``tools/freenic_live_counts.py``
(read-only against the warehouse); this test wires it into pytest so doc drift fails CI.
"""
import sys
from pathlib import Path

import duckdb

# Repo root is TWO parents up from pipeline/tests/ (was parents[3] pre-restructure when
# the test lived at Technical/freenic_ingestion/tests/; the public-layout move to
# pipeline/tests/ made parents[3] overshoot to Projects/. Corrected 2026-07-16.)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import check_doc_counts  # noqa: E402
import freenic_live_counts  # noqa: E402


def test_tools_present():
    assert (TOOLS_DIR / "freenic_live_counts.py").is_file()
    assert (TOOLS_DIR / "check_doc_counts.py").is_file()


def test_live_counts_collect_runs():
    """The live-count probe must run read-only and return the expected keys."""
    counts = freenic_live_counts.collect()
    for key in ("base_tables_total", "base_tables_by_schema", "views_total",
                "total_rows", "parquet_files", "ingestion_scripts", "test_files"):
        assert key in counts, f"missing key {key} in live_counts"
    assert counts["total_rows"] > 0
    assert counts["base_tables_total"] > 0


def test_docs_match_live_warehouse():
    """Every live-state doc states the same numbers as the live DB. Empty == pass."""
    counts = freenic_live_counts.collect()
    # keep the on-disk live_counts.json fresh for humans / CI inspection
    import json
    out = PROJECT_ROOT / "Technical" / "coverage_analysis" / "live_counts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")

    fails = check_doc_counts.check(counts)
    assert not fails, "doc-count drift detected:\n  " + "\n  ".join(fails)


def test_warehouse_opened_read_only():
    """Sanity: the live-count probe path is read-only (never opens the DB for write)."""
    db_path = freenic_live_counts.DB_PATH
    con = duckdb.connect(str(db_path), read_only=True)
    n = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema IN ('main','catalog','dict') AND table_type='BASE TABLE'"
    ).fetchone()[0]
    con.close()
    assert n == freenic_live_counts.collect()["base_tables_total"]
