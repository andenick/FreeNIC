#!/usr/bin/env python3
"""Phase 17: export the dict (taxonomy) layer to Parquet for the dictionary sync.

Exports the 7 dict-schema tables imported by 14_import_dictionary.py — the six
bank-data-dictionary tables plus the coverage-audit map built by 16_coverage_audit.py:

    dict.schedule_lineitems   -> Outputs/parquet/dict_schedule_lineitems.parquet
    dict.relationships        -> Outputs/parquet/dict_relationships.parquet
    dict.ubpr_concepts        -> Outputs/parquet/dict_ubpr_concepts.parquet
    dict.crosswalk            -> Outputs/parquet/dict_crosswalk.parquet
    dict.edit_history         -> Outputs/parquet/dict_edit_history.parquet
    dict.meta                 -> Outputs/parquet/dict_meta.parquet
    dict.variable_access_map  -> Outputs/parquet/dict_variable_access_map.parquet

All ZSTD-compressed, language-agnostic, co-located with the other parquet exports
so the hosted release serves the taxonomy layer alongside the data tables.

Idempotent and READ-ONLY against the warehouse: it opens freenic.duckdb read_only,
COPYs each table out, then refreshes ONLY the dict_*.parquet lines in
Outputs/SHA256SUMS.txt and the dict-layer rows in Outputs/PROVENANCE.csv (both via
a backup -> tmp -> atomic-swap rewrite that never touches existing non-dict lines).

Usage:
    python 17_export_dict_parquet.py
"""
import csv
import io
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, file_checksum, OUTPUTS_DIR

# (dict table, parquet basename). variable_access_map is the coverage-audit map
# (built by 16) and is exported alongside the six imported dictionary tables.
DICT_TABLES = [
    ("schedule_lineitems", "dict_schedule_lineitems"),
    ("relationships", "dict_relationships"),
    ("ubpr_concepts", "dict_ubpr_concepts"),
    ("crosswalk", "dict_crosswalk"),
    ("edit_history", "dict_edit_history"),
    ("meta", "dict_meta"),
    ("variable_access_map", "dict_variable_access_map"),
]

# Per-table one-liner for the PROVENANCE.csv notes column.
DICT_NOTES = {
    "schedule_lineitems": "Per-schedule line-item map (FR Y-9C + Call), melted long; one row per "
                          "(schedule, line, mdrm code). Source of the sched_* shaped views.",
    "relationships": "Empirically-adjudicated reconciliation registry (FFIEC official edits + "
                     "official_calc derivations + curated identities) with per-row empirical_n / "
                     "pass_rate / verdict against the warehouse.",
    "ubpr_concepts": "UBPR (Uniform Bank Performance Report) concept derivations; validated subset "
                     "backs the ubpr_matrix view.",
    "crosswalk": "Expanded MDRM crosswalk (code <-> concept / cross-source mappings).",
    "edit_history": "Official FFIEC edit/validation history for the dictionary's identities.",
    "meta": "Dictionary version stamp and provenance keys (dictionary_version, repo, imported_by).",
    "variable_access_map": "Coverage-audit map (built by 16_coverage_audit.py): every raw variable_id "
                           "-> the shaped/raw views exposing it; the >=1-view reachability guarantee.",
}

DICT_REPO_URL = "https://github.com/andenick/bank-data-dictionary"
DICT_SITE_URL = "https://andenick.github.io/bank-data-dictionary"
INGESTION_SCRIPT = "14_import_dictionary.py"


def export_tables(con, parquet_dir):
    """COPY each dict table to a ZSTD parquet; return [(basename, path, rows, size_mb)]."""
    results = []
    for table, base in DICT_TABLES:
        rows = con.execute(f'SELECT COUNT(*) FROM dict."{table}"').fetchone()[0]
        out = parquet_dir / f"{base}.parquet"
        out_posix = str(out).replace(os.sep, "/")
        con.execute(
            f"COPY (SELECT * FROM dict.\"{table}\") TO '{out_posix}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        size_mb = out.stat().st_size / (1024 * 1024)
        results.append((base, out, rows, size_mb))
        print(f"    dict.{table:24} -> {base}.parquet  {rows:>8,} rows  {size_mb:8.3f} MB")
    return results


def refresh_sha256sums(results):
    """Recompute SHA-256 for ONLY the new dict_*.parquet files; leave every other
    line in SHA256SUMS.txt byte-for-byte unchanged. backup -> tmp -> atomic swap."""
    sums_path = OUTPUTS_DIR / "SHA256SUMS.txt"
    new = {f"{base}.parquet": file_checksum(path) for base, path, _, _ in results}

    existing_lines = []
    if sums_path.exists():
        with io.open(sums_path, encoding="utf-8") as f:
            existing_lines = f.readlines()

    # Keep all non-dict lines verbatim; drop any stale dict_ lines we are refreshing.
    kept = []
    for line in existing_lines:
        parts = line.split()
        fname = parts[1] if len(parts) == 2 else None
        if fname in new:
            continue  # will be re-emitted with the fresh hash
        kept.append(line if line.endswith("\n") else line + "\n")

    # Append the refreshed dict lines, sorted by filename for stable diffs.
    dict_lines = [f"{new[fn]}  {fn}\n" for fn in sorted(new)]

    # backup -> tmp -> atomic swap
    if sums_path.exists():
        shutil.copy2(sums_path, sums_path.with_suffix(".txt.bak"))
    tmp = sums_path.with_suffix(".txt.tmp")
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.writelines(kept)
        f.writelines(dict_lines)
    os.replace(tmp, sums_path)
    print(f"    SHA256SUMS.txt: refreshed {len(dict_lines)} dict_*.parquet line(s), "
          f"{len(kept)} existing line(s) untouched")


def refresh_provenance(con, results):
    """Add/refresh ONE PROVENANCE.csv row per dict_*.parquet. Keys on the 'table'
    column value (dict_<name>); leaves every non-dict row verbatim. backup -> tmp -> swap."""
    prov_path = OUTPUTS_DIR / "PROVENANCE.csv"
    ver = con.execute(
        "SELECT value FROM dict.meta WHERE key = 'dictionary_version'"
    ).fetchone()
    ver = ver[0] if ver else "unknown"

    rows_by_table = {table: rows for (table, _), (_, _, rows, _) in zip(DICT_TABLES, results)}
    # map basename -> (table, rows, checksum)
    new_rows = {}
    for (table, base), (b, path, rows, _size) in zip(DICT_TABLES, results):
        checksum = file_checksum(path)
        note = (f"{DICT_NOTES[table]} rows={rows}; sha256={checksum[:16]}...; "
                f"taxonomy companion {DICT_SITE_URL}.")
        new_rows[base] = {
            "table": base,
            "era": f"dictionary {ver}",
            "provenance_tier": "T1",
            "provider": "bank-data-dictionary (andenick)",
            "download_url": DICT_REPO_URL,
            "self_serve": "yes",
            "citation_required": "yes",
            "notes": note,
        }

    with io.open(prov_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing = [r for r in reader]

    # Drop any prior dict_ rows we are refreshing; keep everything else verbatim.
    kept = [r for r in existing if r.get("table") not in new_rows]
    out_rows = kept + [new_rows[b] for b in sorted(new_rows)]

    # backup -> tmp -> atomic swap
    shutil.copy2(prov_path, prov_path.with_suffix(".csv.bak"))
    tmp = prov_path.with_suffix(".csv.tmp")
    with io.open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    os.replace(tmp, prov_path)
    print(f"    PROVENANCE.csv: refreshed {len(new_rows)} dict row(s), "
          f"{len(kept)} existing row(s) untouched (dictionary {ver})")


def main():
    elapsed = timer()
    print("=== Phase 17: Export dict (taxonomy) layer to Parquet ===")

    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(exist_ok=True)

    con = get_db(read_only=True)  # READ-ONLY: export never mutates the warehouse
    results = export_tables(con, parquet_dir)
    refresh_sha256sums(results)
    refresh_provenance(con, results)
    con.close()

    total_mb = sum(s for _, _, _, s in results)
    total_rows = sum(r for _, _, r, _ in results)
    print(f"\n  Exported {len(results)} dict tables: {total_rows:,} rows, {total_mb:.3f} MB")

    secs = elapsed()
    log_ingestion(
        "17",
        f"dict parquet export: {len(results)} tables ({total_rows:,} rows, "
        f"{total_mb:.3f} MB); SHA256SUMS + PROVENANCE refreshed. {secs:.1f}s",
    )
    print(f"\nPhase 17 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
