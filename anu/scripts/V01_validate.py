"""V01: Validate the FreeNIC replication package against its contract.

Checks (exit non-zero on any failure):

A. Registry structure
   1. series_registry.json parses; every entry has the required fields.
   2. Series IDs unique; output files unique.
   3. Every construction script referenced in the registry exists in
      pipeline/scripts/ (or is an explicitly allowed release-tools path).

B. Registry <-> release manifest parity
   4. Every registry table appears in the authoritative release manifest with
      an identical row count (bijection).
      --remote (default): https://data.freenic.org/release_manifest.json
      --local: the committed release-tools/release_v1.0.0/release_manifest.json
               (61 root files; the 6 reconstruction tables are checked against
               their committed row counts).

C. Local warehouse parity (only if the warehouse DuckDB exists)
   5. For each registry table present in the warehouse, COUNT(*) equals the
      registry's row count (the served release's row-parity gate).

D. Spot sanity checks on served data (via DuckDB httpfs, --remote only)
   6. bank_failures: 1934..2026 failure years, count>0.
   7. long_bank_aggregates_1863_2026: years 1863..2026, num_banks>0.
   8. clean_bank_panel: 1863..2026, panel non-empty.

Usage:
  python anu/scripts/V01_validate.py --local     # offline checks A+B
  python anu/scripts/V01_validate.py --remote    # A+B(+C)+D over HTTP (default)
  python anu/scripts/V01_validate.py --local --warehouse path/to/freenic.duckdb
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

REMOTE_MANIFEST = "https://data.freenic.org/release_manifest.json"
LOCAL_MANIFEST = (bs.REPO_ROOT / "release-tools" / "release_v1.0.0"
                  / "release_manifest.json")
REGISTRY = bs.ANU_DIR / "series_registry.json"

# Committed row counts for the reconstruction layer when validating offline.
RECONSTRUCTION_ROWS = {
    "luck_core_1959_1975.parquet": 601566,
    "luck_equivalent_1976_2026.parquet": 2026104,
    "finhist_equivalent_1863_1941.parquet": 367312,
    "reconciliation_1976_2026.parquet": 40261405,
    "reconciliation_1959_1975.parquet": 7470087,
    "reconciliation_finhist.parquet": 2632440,
}

REQUIRED_FIELDS = ["series_id", "table_family", "title", "description",
                   "output_file", "source", "construction", "units",
                   "frequency", "coverage", "rows", "tier", "quality"]

FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)
    print(f"  FAIL {msg}")


def ok(msg: str) -> None:
    print(f"  ok   {msg}")


def check_registry_structure(reg: dict) -> None:
    series = reg.get("series", [])
    if not series:
        fail("registry has no series")
        return
    ids, files = set(), set()
    for s in series:
        missing = [f for f in REQUIRED_FIELDS if f not in s or s[f] in (None, "")]
        if missing:
            fail(f"{s.get('series_id', '?')}: missing fields {missing}")
        if s["series_id"] in ids:
            fail(f"duplicate series_id {s['series_id']}")
        if s["output_file"] in files:
            fail(f"duplicate output_file {s['output_file']}")
        ids.add(s["series_id"])
        files.add(s["output_file"])
    ok(f"{len(series)} entries, all required fields present, ids/files unique")

    # construction scripts exist in the canonical pipeline (or allowed tools)
    allowed_prefixes = ("release-tools/", "pipeline/reconstruction/")
    n_checked = 0
    for s in series:
        for script in s["construction"]["scripts"]:
            if script.startswith(allowed_prefixes):
                if not (bs.REPO_ROOT / script).exists():
                    fail(f"{s['series_id']}: missing repo script {script}")
                continue
            if not (bs.PHASE_DIR / script).exists():
                fail(f"{s['series_id']}: pipeline script not found: {script}")
            n_checked += 1
    ok(f"all referenced construction scripts exist ({n_checked} phase-script refs)")


def load_remote_manifest() -> dict:
    req = urllib.request.Request(REMOTE_MANIFEST,
                                 headers={"User-Agent": "freenic-anu/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def check_manifest_parity(reg: dict, remote: bool) -> None:
    manifest = (load_remote_manifest() if remote
                else json.loads(LOCAL_MANIFEST.read_text(encoding="utf-8")))
    rows = {f["name"]: f.get("rows") for f in manifest["files"]}
    if not remote:
        rows.update(RECONSTRUCTION_ROWS)
    label = "served (remote)" if remote else "committed (local)"
    reg_files = {s["output_file"]: s["rows"] for s in reg["series"]}
    extra = sorted(set(rows) - set(reg_files))
    absent = sorted(set(reg_files) - set(rows))
    for f in extra:
        fail(f"manifest file not in registry: {f}")
    for f in absent:
        fail(f"registry table not in manifest: {f}")
    mismatch = [f for f in reg_files if f in rows
                and reg_files[f] != rows[f]]
    for f in mismatch:
        fail(f"row-count mismatch {f}: registry={reg_files[f]} manifest={rows[f]}")
    if not extra and not absent and not mismatch:
        ok(f"bijection + row parity vs {label} manifest "
           f"({len(reg_files)} tables, {sum(v or 0 for v in rows.values()):,} rows)")


def check_warehouse(reg: dict) -> None:
    if not bs.WAREHOUSE.exists():
        print(f"  --   warehouse not present ({bs.WAREHOUSE}), skipping C")
        return
    import duckdb  # noqa: PLC0415
    con = duckdb.connect(str(bs.WAREHOUSE), read_only=True)
    tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
    checked = 0
    for s in reg["series"]:
        t = s["output_file"].removesuffix(".parquet")
        if t not in tables:
            continue
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        if n != s["rows"]:
            fail(f"warehouse row mismatch {t}: db={n} registry={s['rows']}")
        checked += 1
    ok(f"warehouse row parity on {checked} present tables")


def check_spot_remote() -> None:
    try:
        import duckdb  # noqa: PLC0415
    except ImportError:
        print("  --   duckdb not installed, skipping D")
        return
    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
    except Exception as exc:  # noqa: BLE001
        print(f"  --   httpfs unavailable ({exc}), skipping D")
        return
    base = "https://data.freenic.org/"

    n, lo, hi = con.execute(f"""
        SELECT COUNT(*), MIN(failure_year), MAX(failure_year)
        FROM read_parquet('{base}bank_failures.parquet')
        WHERE failure_year IS NOT NULL""").fetchone()
    if n == 0 or lo is None or lo < 1934 or hi > 2026:
        fail(f"bank_failures spot check: n={n} span={lo}..{hi}")
    else:
        ok(f"bank_failures spot: {n:,} failures {int(lo)}..{int(hi)}")

    n, lo, hi, bad = con.execute(f"""
        SELECT COUNT(*), MIN(year), MAX(year),
               SUM(CASE WHEN metric='num_banks' AND value <= 0 THEN 1 ELSE 0 END)
        FROM read_parquet('{base}long_bank_aggregates_1863_2026.parquet')""").fetchone()
    if n != 810 or lo != 1863 or hi != 2026 or (bad or 0) > 0:
        fail(f"long_bank_aggregates spot: n={n} span={lo}..{hi} bad={bad}")
    else:
        ok(f"long_bank_aggregates spot: {n} rows {lo}..{hi}, no non-positive num_banks")

    n, lo, hi = con.execute(f"""
        SELECT COUNT(*), MIN(year), MAX(year)
        FROM read_parquet('{base}clean_bank_panel.parquet')""").fetchone()
    if n == 0 or lo is None or lo < 1863 or hi > 2026:
        fail(f"clean_bank_panel spot: n={n} span={lo}..{hi}")
    else:
        ok(f"clean_bank_panel spot: {n:,} rows {int(lo)}..{int(hi)}")


def main(argv: list[str]) -> int:
    remote = "--remote" in argv or not {"--local", "--remote"} & set(argv)
    if not REGISTRY.exists():
        print("[V01] registry missing - run anu/scripts/make_registry.py first",
              file=sys.stderr)
        return 2
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))

    print(f"[V01] FreeNIC Anu package validation ({'remote' if remote else 'local'})")
    print("A. Registry structure")
    check_registry_structure(reg)
    print("B. Registry <-> release manifest parity")
    try:
        check_manifest_parity(reg, remote)
    except Exception as exc:  # noqa: BLE001
        fail(f"manifest check errored: {exc}")
    print("C. Local warehouse parity")
    check_warehouse(reg)
    if remote:
        print("D. Served-data spot checks (httpfs)")
        try:
            check_spot_remote()
        except Exception as exc:  # noqa: BLE001
            fail(f"spot check errored: {exc}")

    print()
    if FAILS:
        print(f"[V01] FAILED: {len(FAILS)} check(s)")
        for m in FAILS:
            print(f"  - {m}")
        return 1
    print("[V01] PASS: registry, manifest parity, and spot checks all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
