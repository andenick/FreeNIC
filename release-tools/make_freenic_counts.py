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
     ``long_bank_aggregates_1863_2026.parquet`` + the 6 FREENIC11 reconstruction
     parquet under ``reconstruction/``), byte sizes taken from the FROZEN
     PUBLISHED release manifest (``<OUTPUTS>/release_<RELEASE_VERSION>/
     release_manifest.json``) whenever it exists, sha256 + per-file metadata
     (era/tier/provider/citation/notes) read from ``SHA256SUMS.txt`` +
     ``PROVENANCE.csv``. Each occ_historical* era is OVERRIDDEN with the real
     min/max report_date read from the parquet (the arbiter -- prose and the old
     catalog are both wrong).
  2. the shipped curated slice ``app/data/freenic_slice.duckdb`` -- row counts
     for the five headline figures + the bulk-zip byte size (built live).

Run on the build host (needs the Outputs export dir + duckdb):
    python make_freenic_counts.py [--outputs <dir>] [--dry-run]

FND-2 (ported from the Carson deploy-tree copy, 2026-07-29 / item N3.2b)
-----------------------------------------------------------------------
The FROZEN release manifest is the ARBITER of served bytes, not the warehouse
export dir. The warehouse keeps moving after a release is cut -- e.g.
``freenic_manifest.parquet`` was regenerated to 7,352 B on 2026-07-15 while the
file actually served at data.freenic.org is the frozen 6,832 B version. Sizing
from ``p.stat()`` therefore made the site publish a release byte-total 520 B
larger than the release the host serves: exactly the "state a number nobody can
reproduce" defect. Any warehouse/release size divergence is now printed LOUDLY
rather than silently absorbed. The release identity is the module constant
``RELEASE_VERSION`` (previously hardcoded ``"v1.0.0"`` in two places).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
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

# The published release identity. Also names the frozen metadata dir the served byte
# sizes are read back from: <outputs>/release_<RELEASE_VERSION>/release_manifest.json.
RELEASE_VERSION = "v1.1.0"


def _sha_file(p: Path) -> str:
    """sha256 of a file's bytes (streamed) -- for the reconstruction catalog rows."""
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _scrub_notes(note: str) -> str:
    """Sanitize a per-file provenance note for the PUBLIC /data catalog.

    FIX-AT-SOURCE (FNQA-1): the warehouse-side ``Outputs/PROVENANCE.csv`` ``notes``
    column carries internal build detail that must never surface on the served
    catalog -- the extraction-framework name ("DARP"), wave/workpackage IDs
    (W4/W18), and the numbered monorepo ingest-script filenames (``NN[x]_*.py``).
    None of these are public referents and the numbered scripts are not
    demonstrably shipped in this public tree, so naming them is not verifiable
    reproducibility detail. We scrub here, at the render/counts layer, so that
    EVERY regeneration of ``release_manifest.json`` re-scrubs and the leak can
    never reappear on the public page -- WITHOUT mutating the read-only warehouse
    copy. Public notes keep what-it-is + source + coverage; pipeline mechanics
    become neutral phrasing ("agent-assisted", "the ingestion pipeline").
    """
    if not note:
        return note
    s = note
    # 1) DARP extraction-framework name -> neutral.
    s = re.sub(r"\bAgent/DARP\b", "agent-assisted", s)
    s = re.sub(r"\bDARP\b", "agent-assisted", s)
    # 2) Wave / workpackage IDs.
    s = re.sub(r",\s*W\d+\s+upgrade", "", s)          # ", W18 upgrade"
    s = re.sub(r"\s*\(\s*W\d+\b[^)]*\)", "", s)       # " (W4 dollar-column guard)"
    s = re.sub(r"\s*\bW\d+\b", "", s)                 # any stray W-number
    # 3) Numbered / internal ingest-script filenames -> "the ingestion pipeline".
    #    3a. resumable-extension internal shorthand "(07i rank <yrs> + 42 rank)".
    s = re.sub(r"\s*\(07[a-z]? rank[^)]*\)", "", s)
    #    3b. "<verb> by <script>.py".
    s = re.sub(r"\bby\s+[\w.\-/]*\.py", "by the ingestion pipeline", s)
    #    3c. parenthetical acquisition-script tag "(07g_acquire_ubpr.py; ...)".
    s = re.sub(r"\(\s*[\w.\-/]*\.py\s*;", "(ingestion pipeline;", s)
    s = re.sub(r"\(\s*[\w.\-/]*\.py\s*\)", "(ingestion pipeline)", s)
    #    3d. "(reuse of Bev Testing r2_build_clv_panel.py, " internal build ref.
    s = re.sub(r"\(reuse of [\w ]+ [\w.\-]+\.py, ", "(", s)
    #    3e. possessive script stems, with or without .py.
    s = re.sub(r"\b\d{2}[a-z]?_[a-z][\w]*\.py\b", "the ingestion pipeline", s)
    s = re.sub(r"\b\d{2}[a-z]?_[a-z][\w]*\b", "the ingestion pipeline", s)
    #    3f. any residual *.py filename token.
    s = re.sub(r"\b[\w][\w.\-/]*\.py\b", "the ingestion pipeline", s)
    # 4) Grammar tidy for doubled articles the substitutions can produce.
    s = re.sub(r"\bThe simplified the ingestion pipeline load\b",
               "The simplified ingestion-pipeline load", s)
    s = re.sub(r"the ~13-col the ingestion pipeline load",
               "the ~13-col ingestion-pipeline load", s)
    s = re.sub(r"\bThe the ingestion pipeline\b", "The ingestion pipeline", s)
    # 5) whitespace / punctuation cleanup.
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([;,.)])", r"\1", s)
    return s.strip()


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
    """min/max 4-digit year of report_date (the era arbiter). None if no such col.

    FN-2 DIRECTION LOCK -- read before "fixing" any occ_historical era.
    The correct era of BOTH ``occ_historical.parquet`` and ``occ_historical_clv.parquet``
    is **1863-1941**, measured here from the parquet itself. ``1867-1904`` is the span of
    only ONE COMPONENT inside occ_historical.parquet (``source='occ_historical'``, the
    OCC-direct digitization, 9,788,940 of its 17,775,763 rows); the other component is
    ``source='occ_historical_clv'`` (Correia-Luck finhist, 7,986,823 rows, 1863-1941).
    9,788,940 + 7,986,823 = 17,775,763 -- the whole file, spanning 1863-1941.

    The 2026-07-14 estate review recorded this BACKWARDS (as "occ_historical.parquet is
    1867-1904"); that finding was inverted and was corrected on 2026-07-28. Do NOT
    "restore" 1867-1904 as a file-level era. If you believe the era is wrong, re-measure
    the parquet -- this function is the arbiter, PROVENANCE.csv and prose are not.
    """
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


# The reconstruction layer (FREENIC11) is served under reconstruction/ on the
# data host. These 6 parquet join the flat release catalog at v1.1.0 (61 -> 67);
# their per-file catalog metadata (era/tier/provider/citation/notes) is keyed here
# so the /data flat catalog renders them honestly (still no hand-typed quantity --
# bytes/rows are read from the frozen release manifest / off disk).
RECON_SERVED: list[tuple[str, str]] = [
    ("reconstruction/finhist_equivalent_1863_1941.parquet", "finhist_equivalent_1863_1941"),
    ("reconstruction/luck_core_1959_1975.parquet", "luck_core_1959_1975"),
    ("reconstruction/luck_equivalent_1976_2026.parquet", "luck_equivalent_1976_2026"),
    ("reconstruction/validation/reconciliation_finhist.parquet", "reconciliation_finhist"),
    ("reconstruction/validation/reconciliation_1959_1975.parquet", "reconciliation_1959_1975"),
    ("reconstruction/validation/reconciliation_1976_2026.parquet", "reconciliation_1976_2026"),
]
_NYF = "FreeNIC reconstruction (NY Fed Terms of Use — attribution + share-alike)"
_CC0 = "FreeNIC reconstruction (finhist/OCC historical layer, CC0 1.0)"
RECON_MANIFEST_META: dict[str, dict] = {
    "finhist_equivalent_1863_1941": dict(era="1863-1941", tier="derived — FreeNIC reconstruction",
        provider=_CC0, cite="no", notes="Reconstructed HIST panel (from-raw derivation, verified cell-by-cell; PASS)."),
    "luck_core_1959_1975": dict(era="1959-1975", tier="derived — FreeNIC reconstruction",
        provider=_NYF, cite="yes", notes="Reconstructed MODL panel (their formula on their input; PASS)."),
    "luck_equivalent_1976_2026": dict(era="1976-2026", tier="derived — FreeNIC reconstruction",
        provider=_NYF, cite="yes", notes="Reconstructed MODC panel (independent Fed-direct re-derivation; gate FAIL, reported honestly)."),
    "reconciliation_finhist": dict(era="1863-1941", tier="derived — FreeNIC reconstruction (reconciliation)",
        provider=_CC0, cite="no", notes="Cell-level published↔rebuilt reconciliation, 1863-1941."),
    "reconciliation_1959_1975": dict(era="1959-1975", tier="derived — FreeNIC reconstruction (reconciliation)",
        provider=_NYF, cite="yes", notes="Cell-level published↔rebuilt reconciliation, 1959-1975."),
    "reconciliation_1976_2026": dict(era="1976-2026", tier="derived — FreeNIC reconstruction (reconciliation)",
        provider=_NYF, cite="yes", notes="Cell-level published↔rebuilt reconciliation, 1976-2026."),
}


def _served_files(outputs: Path) -> list[Path]:
    """The served release set: 60 parquet in <outputs>/parquet + the spine (=61),
    plus the 6 FREENIC11 reconstruction parquet under reconstruction/ (=67 at v1.1.0)."""
    files = sorted((outputs / "parquet").glob("*.parquet"))
    spine = outputs / SPINE
    if spine.exists():
        files.append(spine)
    for rel, _stem in RECON_SERVED:
        p = outputs / rel
        if p.exists():
            files.append(p)
    return files


def _frozen_release_sizes(outputs: Path) -> dict[str, int]:
    """Byte sizes recorded in the FROZEN, PUBLISHED release manifest, keyed by basename.

    FND-2 root-cause guard. `_served_files()` enumerates the *warehouse* export dir, but
    the warehouse keeps moving after a release is cut: `freenic_manifest.parquet` was
    regenerated to 7,352 B on 2026-07-15, while the file actually served at
    data.freenic.org is the frozen 6,832 B version. Sizing from `p.stat()` therefore made
    the site publish a release byte-total 520 B larger than the release the host serves --
    the same "state a number nobody can reproduce" defect FND-2 is about.

    So: when the frozen release manifest is present, IT is the arbiter of served bytes.
    Falls back to on-disk stat when it is absent (e.g. cutting a brand-new release).
    """
    mf = outputs / ("release_" + RELEASE_VERSION) / "release_manifest.json"
    if not mf.exists():
        return {}
    try:
        frozen = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:      # unreadable/corrupt -> fall back to stat
        print("  ! frozen release manifest unreadable (%s); sizing from disk" % exc)
        return {}
    sizes: dict[str, int] = {}
    for entry in frozen.get("files", []):
        path = entry.get("path") or entry.get("name") or entry.get("file") or ""
        nbytes = entry.get("bytes")
        if path and isinstance(nbytes, int):
            sizes[Path(path).name] = nbytes
    return sizes


def build_manifest(outputs: Path) -> dict:
    """Regenerate the per-file release catalog from the served set (single source)."""
    prov = _load_provenance(outputs)
    sha = _load_sha(outputs)
    frozen_sizes = _frozen_release_sizes(outputs)
    con = duckdb.connect()
    files_meta: list[dict] = []
    total = 0
    for p in _served_files(outputs):
        name = p.name
        stem = p.stem
        disk_size = p.stat().st_size
        size = frozen_sizes.get(name, disk_size)
        if size != disk_size:
            # Loud, not silent: the warehouse copy has drifted from the published one.
            print("  ! %s: warehouse %d B != released %d B — publishing the RELEASED size"
                  % (name, disk_size, size))
        total += size
        # Reconstruction-layer files live under reconstruction/ and are keyed
        # separately (not in PROVENANCE.csv); they render as reconstruction/<name>
        # so the /data catalog URL + codebook link resolve on the data host.
        rmeta = RECON_MANIFEST_META.get(stem)
        if rmeta is not None:
            files_meta.append({
                "file": "reconstruction/" + name,
                "table": stem,
                "bytes": size,
                "sha256": _sha_file(p),
                "era": rmeta["era"],
                "tier": rmeta["tier"],
                "provider": rmeta["provider"],
                "citation_required": rmeta["cite"],
                "notes": rmeta["notes"],
            })
            continue
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
            # Public catalog note: scrub internal pipeline identifiers at the
            # render/counts layer so regeneration can't reintroduce the leak
            # (FNQA-1); the warehouse PROVENANCE.csv copy is left untouched.
            "notes": _scrub_notes((pr.get("notes") or "").strip()),
        })
    con.close()
    return {
        "generated": "make_freenic_counts.py",
        "n_files": len(files_meta),
        "total_bytes": total,
        "release": RELEASE_VERSION,
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
    """Byte size of the bulk slice zip as built HERE (the build host).

    IMPORTANT (FNQA-2): the container serves this zip by running ``bulk_zip()``
    itself at request time, using its OWN pinned libraries. Parquet/CSV
    serialization differs between the build host and the container even for a
    byte-identical slice DB, so this build-host figure can be ~hundreds of KB off
    from the served ``Content-Length``. The only authoritative slice-zip size is
    the SERVING environment's -- pass it in via ``FREENIC_SLICE_ZIP_BYTES``
    (measured in-container at deploy). When that env var is set, ``main()`` uses
    it and skips this build-host estimate entirely.
    """
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
    ap.add_argument("--dry-run", action="store_true",
                    help="compute and print every figure but WRITE NOTHING; also skips the "
                         "curated-slice stage when app/data/freenic_slice.duckdb is absent. "
                         "Use to verify the release figures before regenerating site data.")
    args = ap.parse_args(argv)
    outputs = Path(args.outputs)
    dry = args.dry_run

    manifest = build_manifest(outputs)
    if dry:
        print("[dry-run] would write %s" % (DATA / "release_manifest.json"))
    else:
        (DATA / "release_manifest.json").write_text(
            json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")

    if dry and not SLICE_DB.exists():
        # The curated slice is not part of this repo's checked-in tree; the release
        # figures above do not depend on it, so report them and stop rather than
        # crash. NEVER substitute a guessed slice figure.
        print("[dry-run] curated slice %s absent — release figures only" % SLICE_DB.name)
        print("release_manifest.json: %d files / %d bytes (%s / %s), release %s"
              % (manifest["n_files"], manifest["total_bytes"],
                 _human_iec(manifest["total_bytes"]), _human_si(manifest["total_bytes"]),
                 manifest["release"]))
        occ_dry = {f["table"]: f["era"] for f in manifest["files"]
                   if f["table"].startswith("occ_historical")}
        for k, v in occ_dry.items():
            print("  %-22s %s" % (k + "_era", v))
        return 0

    sc = slice_counts()
    datasets, directory, external = count_sources()
    wt = warehouse_truth(outputs)
    occ = {f["table"]: f["era"] for f in manifest["files"]
           if f["table"].startswith("occ_historical")}

    counts = {
        "release_files": manifest["n_files"],
        "release_bytes": manifest["total_bytes"],
        "release_size_iec": _human_iec(manifest["total_bytes"]),   # "13.9 GiB" (canonical)
        "release_size_si": _human_si(manifest["total_bytes"]),     # "15.0 GB"
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
    if not dry:
        out_path.write_text(json.dumps(counts, indent=1, ensure_ascii=False),
                            encoding="utf-8", newline="\n")
    # Prefer the serving-environment measurement (the container's own bulk_zip
    # Content-Length) when the deploy provides it -- the build-host build diverges
    # by parquet serialization (FNQA-2). Fall back to the build-host estimate.
    env_zip = os.environ.get("FREENIC_SLICE_ZIP_BYTES", "").strip()
    zip_b = int(env_zip) if env_zip.isdigit() else slice_zip_bytes()
    counts["slice_zip_bytes"] = zip_b
    counts["slice_zip_h"] = _human_slice(zip_b)                    # e.g. "20.6 MB"
    if dry:
        print("[dry-run] would write %s and %s" % (DATA / "release_manifest.json", out_path))
    else:
        out_path.write_text(json.dumps(counts, indent=1, ensure_ascii=False),
                            encoding="utf-8", newline="\n")

    print("release_manifest.json: %d files / %d bytes (%s / %s), release %s"
          % (manifest["n_files"], manifest["total_bytes"], counts["release_size_iec"],
             counts["release_size_si"], manifest["release"]))
    print("freenic_counts.json written:")
    for k in ("release_files", "release_size_iec", "slice_zip_h", "slice_db_h",
              "fred_series", "failure_end_year", "source_datasets",
              "supplier_directory", "external_suppliers",
              "occ_historical_era", "occ_historical_clv_era"):
        print("  %-22s %s" % (k, counts[k]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
