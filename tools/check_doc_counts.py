"""Doc-count drift gate for freenic.

Parses the count claims out of the live-state docs (README, DATA_DICTIONARY,
QUICK_START, DATA_SOURCE_INVENTORY) and asserts they match the authoritative live
warehouse numbers from ``freenic_live_counts.py``. This is the permanent fix
(W1.4 of FREENIC_COMPLETENESS_PLAN) that stops the doc drift from recurring.

It does NOT touch the warehouse to recompute (the test harness reuses the live
connection); instead it reads ``Technical/coverage_analysis/live_counts.json`` —
so run ``tools/freenic_live_counts.py`` first (or call ``live_counts()`` here,
which regenerates it read-only if absent/stale).

Returns a list of mismatch strings; empty list == PASS. ``main()`` exits non-zero
on any mismatch so it can be a CI gate as well as a pytest.

Scope: only the *live-state* docs are gated. Dated release notes are point-in-time
records (their figures are the as-shipped snapshot) and are intentionally NOT gated.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = PROJECT_ROOT / "Outputs"
LIVE_JSON = PROJECT_ROOT / "Technical" / "coverage_analysis" / "live_counts.json"

README = PROJECT_ROOT / "README.md"
DATA_DICTIONARY = OUTPUTS / "DATA_DICTIONARY.md"
QUICK_START = OUTPUTS / "QUICK_START.md"
DATA_SOURCE_INVENTORY = OUTPUTS / "DATA_SOURCE_INVENTORY.md"


def live_counts(regenerate: bool = True) -> dict:
    """Load the authoritative live counts; regenerate read-only if missing."""
    if regenerate or not LIVE_JSON.is_file():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import freenic_live_counts  # noqa: E402

        counts = freenic_live_counts.collect()
        LIVE_JSON.parent.mkdir(parents=True, exist_ok=True)
        LIVE_JSON.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
        return counts
    return json.loads(LIVE_JSON.read_text(encoding="utf-8"))


def _digits(s: str) -> int:
    return int(s.replace(",", ""))


def check(counts: dict | None = None) -> list[str]:
    if counts is None:
        counts = live_counts()

    bt = counts["base_tables_total"]
    bs = counts["base_tables_by_schema"]
    main_n, cat_n, dict_n = bs["main"], bs["catalog"], bs["dict"]
    views = counts["views_total"]
    rows = counts["total_rows"]

    fails: list[str] = []

    def need(doc: Path, text: str, label: str, present: bool, detail: str = ""):
        if not present:
            fails.append(f"{doc.name}: {label} not found/incorrect{(' — ' + detail) if detail else ''}")

    # --- the canonical 'base tables (45 main + 6 catalog + 7 dict)' claim ---
    bt_pat = re.compile(
        rf"\b{bt}\s+base tables\s*\(\s*{main_n}\s+`?main`?\s*\+\s*{cat_n}\s+`?catalog`?\s*\+\s*{dict_n}\s+`?dict`?\s*\)",
        re.IGNORECASE,
    )
    # Some docs phrase it '58 (45 main + 6 catalog + 7 dict)' or '58 base tables (45 main...)'
    bt_pat2 = re.compile(
        rf"\b{bt}\b[^\n]*?{main_n}\s+`?main`?[^\n]*?{cat_n}\s+`?catalog`?[^\n]*?{dict_n}\s+`?dict`?",
        re.IGNORECASE,
    )

    # --- exact total-rows claim (the precise integer must appear) ---
    rows_str = f"{rows:,}"

    # The full schema breakdown (45 main + 6 catalog + 7 dict) is carried by the
    # reference docs; QUICK_START states the headline totals only.
    breakdown_docs = (README, DATA_DICTIONARY, DATA_SOURCE_INVENTORY)
    all_docs = (README, DATA_DICTIONARY, QUICK_START, DATA_SOURCE_INVENTORY)

    for doc in breakdown_docs:
        txt = doc.read_text(encoding="utf-8")
        present = bool(bt_pat.search(txt) or bt_pat2.search(txt))
        need(doc, txt, f"base-table breakdown ({bt} = {main_n} main + {cat_n} catalog + {dict_n} dict)", present)

    for doc in all_docs:
        txt = doc.read_text(encoding="utf-8")

        # headline base-table total must appear (either "58 base tables" or
        # "Base tables: 58" or the full breakdown line)
        bt_present = bool(
            re.search(rf"\b{bt}\s+base tables", txt, re.IGNORECASE)
            or re.search(rf"base tables\**:\s*\**{bt}\b", txt, re.IGNORECASE)
            or bt_pat.search(txt) or bt_pat2.search(txt)
        )
        need(doc, txt, f"base-table total ({bt})", bt_present)

        # exact total rows
        need(doc, txt, f"exact total rows ({rows_str})", rows_str in txt)

        # view count: require the live view number to appear adjacent to 'view'
        view_present = bool(re.search(rf"\b{views}\b[^\n]{{0,40}}views?", txt, re.IGNORECASE)
                            or re.search(rf"\b{views}\s+shaped", txt, re.IGNORECASE))
        need(doc, txt, f"view count ({views})", view_present)

    # --- README structural counts: parquet / scripts / tests ---
    readme = README.read_text(encoding="utf-8")
    pq = counts["parquet_files"]
    sc = counts["ingestion_scripts"]
    te = counts["test_files"]
    need(README, readme, f"parquet file count ({pq})",
         bool(re.search(rf"\b{pq}\s+Parquet tables", readme) or re.search(rf"\b{pq}\s+files", readme)))
    need(README, readme, f"ingestion-script count ({sc})",
         bool(re.search(rf"\b{sc}-script", readme)))
    need(README, readme, f"test-suite count ({te})",
         bool(re.search(rf"\b{te}\s+test suites", readme)))

    # --- assert no live-state doc presents a known-stale total as current ---
    # NOTE: DATA_SOURCE_INVENTORY deliberately preserves the legacy 2,258,132,117 figure
    # inside an explicitly-labeled "legacy figure, undercounts" note, so that exact integer
    # is allowed there; it is forbidden everywhere else.
    STALE_ALL = ["37 (32 main", "10 convenience views",
                 "~2.25 billion", "~2.26B", "37 Parquet tables", "30-script", "Seven test suites"]
    STALE_NONINVENTORY = ["2,258,132,117"]
    for doc in (README, DATA_DICTIONARY, QUICK_START, DATA_SOURCE_INVENTORY):
        txt = doc.read_text(encoding="utf-8")
        for s in STALE_ALL:
            if s in txt:
                fails.append(f"{doc.name}: still contains stale token {s!r}")
        if doc is not DATA_SOURCE_INVENTORY:
            for s in STALE_NONINVENTORY:
                if s in txt:
                    fails.append(f"{doc.name}: still contains stale token {s!r}")

    return fails


def main() -> int:
    counts = live_counts()
    fails = check(counts)
    if fails:
        print("DOC-COUNT GATE: FAIL")
        for f in fails:
            print(f"  - {f}")
        print(f"\nLive: {counts['base_tables_total']} base tables "
              f"({counts['base_tables_by_schema']}), {counts['views_total']} views, "
              f"{counts['total_rows']:,} rows, {counts['parquet_files']} parquet, "
              f"{counts['ingestion_scripts']} scripts, {counts['test_files']} tests.")
        return 1
    print("DOC-COUNT GATE: PASS — all live-state docs match the live warehouse.")
    print(f"Live: {counts['base_tables_total']} base tables, {counts['views_total']} views, "
          f"{counts['total_rows']:,} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
