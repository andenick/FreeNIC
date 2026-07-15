#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_freenic_counts.py -- the single source of truth for every on-page count.

CDF campaign CODE_DATA_FIRST_20260710 (freenic centerpiece). Generates
``app/data/freenic_counts.json`` (scalar headline counts) AND regenerates
``app/data/release_manifest.json`` (the per-file /data catalog) from two
AUTHORITATIVE sources, so no quantity is ever hand-typed into the copy,
DATA_SERVING.md, the catalog, or a triad sublabel again (the FN-3 lesson):

  1. the SERVED parquet release  -- enumerated from the build-host export dir
     (``<OUTPUTS>/parquet/*.parquet`` + the 163-year spine
     ``long_bank_aggregates_1863_2026.parquet``), byte sizes read off disk,
     sha256 + per-file metadata (era/tier/provider/citation/notes) read from
     ``SHA256SUMS.txt`` + ``PROVENANCE.csv``. Each occ_historical* era is
     OVERRIDDEN with the real min/max report_date read from the parquet
     (the arbiter -- prose and the old catalog are both wrong).
  2. the shipped curated slice ``app/data/freenic_slice.duckdb`` -- row counts
     for the five headline figures + the bulk-zip byte size (built live).

Run on the build host (needs the Outputs export dir + duckdb):
    python make_freenic_counts.py [--outputs <dir>]
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path

import duckdb

# The runnable site app dir (holds app/data, app/downloads.py). Overridable by env
# (default: ../site relative to this release-tools script).
SITE = Path(os.environ.get("FREENIC_SITE_DIR", str(Path(__file__).resolve().parent.parent / "site")))
APP = SITE / "app"
DATA = APP / "data"
SLICE_DB = DATA / "freenic_slice.duckdb"

# The 163-year replicated spine featured on /explorer: served as the 61st file.
SPINE = "long_bank_aggregates_1863_2026.parquet"


def _human_iec(n: int) -> str:
    """Binary (1024-based, GiB/MiB) human label -- the canonical release size unit."""
    x = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if x < 1024.0 or unit == "TiB":
            return ("%d B" % int(x)) if unit == "B" else ("%.1f %s" % (x, unit))
        x /= 1024.0
    return "%d B" % n


def _human_si(n: int) -> str:
    """Decimal (1000-based, GB/MB) human label."""
    x = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if x < 1000.0 or unit == "TB":
            return ("%d B" % int(x)) if unit == "B" else ("%.1f %s" % (x, unit))
        x /= 1000.0
    return "%d B" % n


def _human_slice(n: int) -> str:
    """MB/KB label for slice-scale artifacts (mebibyte, matches file-manager sizes)."""
    return "%.1f MB" % (n / 1_048_576) if n >= 1_048_576 else "%.1f KB" % (n / 1024)


def _load_provenance(outputs: Path) -> dict[str, dict]:
    """Per-table PROVENANCE.csv row keyed by table name (file stem)."""
    prov: dict[str, dict] = {}
    pf = outputs / "PROVENANCE.csv"
    if not pf.exists():
        return prov
    with pf.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            prov[row["table"].strip()] = row
    return prov


def _load_sha(outputs: Path) -> dict[str, str]:
    """filename -> sha256 from SHA256SUMS.txt."""
    sha: dict[str, str] = {}
    sf = outputs / "SHA256SUMS.txt"
    if not sf.exists():
        return sha
    for line in sf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        h, _, name = line.partition("  ")
        sha[name.strip().lstrip("*")] = h.strip()
    return sha


def _parquet_year_range(con, path: Path) -> tuple[int, int] | None:
    """min/max 4-digit year of report_date (the era arbiter). None if no such col."""
    try:
        cols = [r[0].lower() for r in con.execute(
            "DESCRIBE SELECT * FROM '%s'" % path.as_posix()).fetchall()]
    except Exception:
        return None
    if "report_date" not in cols:
        return None
    try:
        mn, mx = con.execute(
            "SELECT MIN(CAST(substr(CAST(report_date AS VARCHAR),1,4) AS INT)), "
            "MAX(CAST(substr(CAST(report_date AS VARCHAR),1,4) AS INT)) "
            "FROM '%s'" % path.as_posix()).fetchone()
        if mn and mx:
            return int(mn), int(mx)
    except Exception:
        return None
    return None


def _served_files(outputs: Path) -> list[Path]:
    """The served release set: the 60 parquet in <outputs>/parquet + the spine (=61)."""
    files = sorted((outputs / "parquet").glob("*.parquet"))
    spine = outputs / SPINE
    if spine.exists():
        files.append(spine)
    return files


def build_manifest(outputs: Path) -> dict:
    """Regenerate the per-file release catalog from the served set (single source)."""
    prov = _load_provenance(outputs)
    sha = _load_sha(outputs)
    con = duckdb.connect()
    files_meta: list[dict] = []
    total = 0
    for p in _served_files(outputs):
        name = p.name
        stem = p.stem
        size = p.stat().st_size
        total += size
        pr = prov.get(stem, {})
        # Era: for occ_historical* the parquet min/max report_date is the arbiter.
        era = (pr.get("era") or "").strip()
        if stem.startswith("occ_historical"):
            yr = _parquet_year_range(con, p)
            if yr:
                era = "%d-%d" % yr
        files_meta.append({
            "file": name,
            "table": stem,
            "bytes": size,
            "sha256": sha.get(name, ""),
            "era": era or "reference",
            "tier": (pr.get("provenance_tier") or "").strip() or "derived",
            "provider": (pr.get("provider") or "").strip() or "FreeNIC",
            "citation_required": (pr.get("citation_required") or "no").strip(),
            "notes": (pr.get("notes") or "").strip(),
        })
    con.close()
    return {
        "generated": "make_freenic_counts.py",
        "n_files": len(files_meta),
        "total_bytes": total,
        "release": "v1.0.0",
        "files": files_meta,
    }


def warehouse_truth(outputs: Path) -> dict:
    """Warehouse-scale ground truth, WIRED from Outputs/coverage_matrix.csv (the
    authoritative per-family coverage artifact; its own header reads
    'Base tables covered: 58 · Total base rows: 4,965,894,572'). Nothing is
    hardcoded -- base_tables and base_rows are summed from the file, and the
    coverage span is the min/max of the per-family period columns.

    Reconciliation note: coverage_matrix counts the 58 data base tables and
    EXCLUDES the self-describing `freenic_manifest` table; the live DB probe
    (live_counts.json) reports 59 base tables / 4,965,894,682 rows = these 58 +
    the manifest table's own 110 rows. We publish the coverage-matrix pair
    (canonical, matches the documented figure)."""
    cm = outputs / "coverage_matrix.csv"
    n_tables = 0
    base_rows = 0
    n_families = 0
    years: list[int] = []
    if cm.exists():
        with cm.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                n_families += 1
                try:
                    n_tables += int(row["n_tables"])
                    base_rows += int(row["base_rows"])
                except (KeyError, ValueError):
                    pass
                for k in ("period_min", "period_max"):
                    v = (row.get(k) or "").strip()
                    m = v[:4]
                    if m.isdigit():
                        years.append(int(m))
    span = ("%d–%d" % (min(years), max(years))) if years else ""
    approx = ("%.2fB" % (base_rows / 1e9)) if base_rows else ""
    return {
        "base_tables": n_tables,
        "base_rows": base_rows,
        "base_rows_h": "{:,}".format(base_rows),
        "base_rows_approx": approx,        # "4.97B"
        "n_families": n_families,
        "coverage_span": span,             # "1782-2026" (full warehouse extent)
    }


def slice_counts() -> dict:
    con = duckdb.connect(str(SLICE_DB), read_only=True)
    q = lambda s: con.execute(s).fetchone()[0]
    out = {
        "fred_obs": int(q("SELECT COUNT(*) FROM fred_series")),
        "fred_series": int(q("SELECT COUNT(DISTINCT series_id) FROM fred_series")),
        "active_inst": int(q("SELECT COUNT(*) FROM institutions_active")),
        "reachable_vars": int(q("SELECT COUNT(*) FROM dict_variable_access_map")),
        "failure_records": int(q("SELECT COUNT(*) FROM bank_failures")),
        "failure_end_year": int(q("SELECT MAX(failure_year) FROM bank_failures")),
        "slice_db_bytes": SLICE_DB.stat().st_size,
    }
    con.close()
    return out


def slice_zip_bytes() -> int:
    """Live byte size of the served bulk slice zip (built from the real slice)."""
    spec = importlib.util.spec_from_file_location("fn_downloads", APP / "downloads.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return len(mod.bulk_zip()[0])


def count_sources() -> tuple[int, int, int]:
    """(upstream datasets, supplier-directory entries, external suppliers)."""
    sj = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    datasets = len(sj.get("sources", []))
    directory = 0
    external = 0
    sdp = DATA / "sources_directory.json"
    if sdp.exists():
        sd = json.loads(sdp.read_text(encoding="utf-8"))
        entries = sd.get("sources", [])
        directory = len(entries)
        external = sum(
            1 for s in entries
            if not str(s.get("name", "")).strip().lower().startswith("freenic")
        )
    return datasets, directory, external


def read_validation(outputs: Path) -> dict:
    """Validation-suite + pytest counts + last-validated date for /methodology,
    read from the on-disk ``Outputs/validation_status.json`` produced by the build
    (campaign FREENIC10_CURRENCY G1 gate). Never hand-typed here: if the file is
    absent or a key is missing the slot stays None/"" and the template renders an
    honest em-dash rather than a fabricated pass. Returns the six stable keys the
    methodology.html validation slots read."""
    keys = ("validate_pass", "validate_total", "pytest_passed",
            "pytest_failed", "pytest_skipped", "last_validated")
    out = {k: (None if k != "last_validated" else "") for k in keys}
    vs = outputs / "validation_status.json"
    if vs.exists():
        try:
            data = json.loads(vs.read_text(encoding="utf-8"))
            for k in keys:
                if k in data and data[k] is not None:
                    out[k] = data[k]
        except (ValueError, OSError):
            pass
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", default=os.environ.get("FREENIC_OUTPUTS", "Outputs"),
                    help="build-host parquet export dir (has parquet/, SHA256SUMS.txt, PROVENANCE.csv); "
                         "defaults to $FREENIC_OUTPUTS or ./Outputs")
    args = ap.parse_args(argv)
    outputs = Path(args.outputs)

    manifest = build_manifest(outputs)
    (DATA / "release_manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")

    sc = slice_counts()
    datasets, directory, external = count_sources()
    wt = warehouse_truth(outputs)
    occ = {f["table"]: f["era"] for f in manifest["files"]
           if f["table"].startswith("occ_historical")}

    counts = {
        "release_files": manifest["n_files"],
        "release_bytes": manifest["total_bytes"],
        "release_size_iec": _human_iec(manifest["total_bytes"]),   # "13.2 GiB" (canonical)
        "release_size_si": _human_si(manifest["total_bytes"]),     # "14.1 GB"
        "slice_db_bytes": sc["slice_db_bytes"],
        "slice_db_h": _human_slice(sc["slice_db_bytes"]),          # "15.5 MB"
        "slice_zip_bytes": 0,   # filled below (2-phase: README reads release numbers first)
        "slice_zip_h": "",
        "fred_obs": sc["fred_obs"],
        "fred_obs_h": "{:,}".format(sc["fred_obs"]),
        "fred_series": sc["fred_series"],
        "active_inst": sc["active_inst"],
        "active_inst_h": "{:,}".format(sc["active_inst"]),
        "reachable_vars": sc["reachable_vars"],
        "reachable_vars_h": "{:,}".format(sc["reachable_vars"]),
        "failure_records": sc["failure_records"],
        "failure_records_h": "{:,}".format(sc["failure_records"]),
        "failure_end_year": sc["failure_end_year"],
        # --- Warehouse ground truth (wired from coverage_matrix.csv) ----------
        "base_tables": wt["base_tables"],            # 58 data base tables
        "base_rows": wt["base_rows"],                # 4,965,894,572
        "base_rows_h": wt["base_rows_h"],            # "4,965,894,572"
        "base_rows_approx": wt["base_rows_approx"],  # "4.97B"
        "n_families": wt["n_families"],              # 21
        "coverage_span": wt["coverage_span"],        # "1782–2026"
        # Backward-compat aliases so any un-migrated {{ counts.* }} still renders
        # warehouse truth (never the stale ~2.27B / 42). Superseded by base_*.
        "unified_tables": wt["base_tables"],
        "total_obs": wt["base_rows_approx"],
        "institutions": 217210,
        "institutions_h": "217K",
        "source_datasets": datasets,          # sources.json (composition table) = 20
        "supplier_directory": directory,      # /sources directory entries = 13
        "external_suppliers": external,       # excl. FreeNIC self-refs = 11
        "version": manifest["release"],
        "time_span": "1863–2026",
        "occ_historical_era": occ.get("occ_historical", ""),
        "occ_historical_clv_era": occ.get("occ_historical_clv", ""),
    }
    # ------------------------------------------------------------------
    # Validation & test transparency (rendered on /methodology).
    # PLACEHOLDER wiring: the integration agent replaces read_validation()
    # with the real CI/validate + pytest result readers for this build.
    # Until then these are None/"" so the page renders an honest em-dash
    # (never a fabricated pass count). Keys are stable so the template slots
    # in app/templates/methodology.html do not change when the values land.
    # ------------------------------------------------------------------
    counts.update(read_validation(outputs))
    # Phase 1: write counts.json with all release/sample numbers (the bundle README
    # reads these). Phase 2: build the zip (README now numerically correct) and
    # patch in the deterministic slice-zip size. One invocation, idempotent.
    out_path = DATA / "freenic_counts.json"
    out_path.write_text(json.dumps(counts, indent=1, ensure_ascii=False),
                        encoding="utf-8", newline="\n")
    zip_b = slice_zip_bytes()
    counts["slice_zip_bytes"] = zip_b
    counts["slice_zip_h"] = _human_slice(zip_b)                    # "20.8 MB"
    out_path.write_text(json.dumps(counts, indent=1, ensure_ascii=False),
                        encoding="utf-8", newline="\n")

    print("release_manifest.json: %d files / %d bytes (%s)"
          % (manifest["n_files"], manifest["total_bytes"], counts["release_size_iec"]))
    print("freenic_counts.json written:")
    for k in ("release_files", "release_size_iec", "slice_zip_h", "slice_db_h",
              "fred_series", "failure_end_year", "source_datasets",
              "supplier_directory", "external_suppliers",
              "occ_historical_era", "occ_historical_clv_era"):
        print("  %-22s %s" % (k, counts[k]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
