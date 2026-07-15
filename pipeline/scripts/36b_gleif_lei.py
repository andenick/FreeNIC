"""36b_gleif_lei.py — widen id_crosswalk.lei using the GLEIF Level-1 golden copy.

A6 (GLEIF). Fills `id_crosswalk.lei` WHERE it is currently NULL, via an
UNAMBIGUOUS normalized-name match between GLEIF US/ACTIVE `legal_name` and the
NIC `institutions` name. Newly filled rows are tagged `lei_source = 'gleif'`
(existing 'nic'/'hmda' LEIs are never overwritten).

Reuses `normalize_name` + `build_name_to_rssd` from 35_ingest_hmda.py so the
GLEIF and NIC sides are normalized identically (no drift).

DB-serial: single writer. Run only when no other process holds the DB. After
the UPDATE it re-exports id_crosswalk.parquet and checks parity.

Source: Inputs/gleif/gleif_level1.parquet (3,334,432 LEIs; 332,815 US/ACTIVE).
"""
import importlib.util
import sys
import time
from pathlib import Path

import duckdb

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from utils import DB_PATH, OUTPUTS_DIR, log_ingestion  # noqa: E402

PROJECT_ROOT = OUTPUTS_DIR.parent
GLEIF_PARQUET = PROJECT_ROOT / "Inputs" / "gleif" / "gleif_level1.parquet"
XWALK_PARQUET = OUTPUTS_DIR / "parquet" / "id_crosswalk.parquet"

_T0 = time.time()


def elapsed() -> float:
    return time.time() - _T0


def _load_hmda_module():
    """Import the digit-prefixed 35_ingest_hmda module to reuse its
    name-normalization helpers (genuine reuse, not a copy)."""
    spec = importlib.util.spec_from_file_location(
        "ingest_hmda35", SCRIPTS_DIR / "35_ingest_hmda.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_gleif_name_to_lei(con) -> dict:
    """Map normalized GLEIF legal_name -> lei, US/ACTIVE only, UNAMBIGUOUS
    (the normalized name resolves to exactly one LEI)."""
    hmda = _load_hmda_module()
    normalize_name = hmda.normalize_name
    rows = con.execute(
        f"""
        SELECT lei, legal_name
        FROM read_parquet('{GLEIF_PARQUET.as_posix()}')
        WHERE country = 'US' AND entity_status = 'ACTIVE'
          AND legal_name IS NOT NULL
        """
    ).fetchall()
    norm_to_leis = {}
    for lei, nm in rows:
        key = normalize_name(nm)
        if not key or len(key) < 3:
            continue
        norm_to_leis.setdefault(key, set()).add(lei)
    return {k: next(iter(v)) for k, v in norm_to_leis.items() if len(v) == 1}


def main():
    if not GLEIF_PARQUET.exists():
        sys.exit(f"GLEIF parquet not found: {GLEIF_PARQUET}")

    hmda = _load_hmda_module()
    con = duckdb.connect(str(DB_PATH))

    lei_before = con.execute(
        "SELECT COUNT(*) FROM id_crosswalk WHERE lei IS NOT NULL"
    ).fetchone()[0]
    null_before = con.execute(
        "SELECT COUNT(*) FROM id_crosswalk WHERE lei IS NULL"
    ).fetchone()[0]

    # Unambiguous name maps on both sides, normalized identically.
    name_to_rssd = hmda.build_name_to_rssd(con)           # NIC institutions
    name_to_lei = build_gleif_name_to_lei(con)            # GLEIF US/ACTIVE
    print(f"  unambiguous names: NIC={len(name_to_rssd):,}  GLEIF={len(name_to_lei):,}")

    # rssd -> lei only where BOTH sides are unambiguous for the same norm name.
    rssd_to_lei = {}
    for nm, rssd in name_to_rssd.items():
        lei = name_to_lei.get(nm)
        if lei is not None:
            rssd_to_lei[rssd] = lei
    print(f"  candidate rssd<->lei matches: {len(rssd_to_lei):,}")

    # Only fill rows whose lei is currently NULL. A rssd can map to one lei
    # (name_to_rssd is unambiguous), so no per-rssd conflict is possible.
    null_rssds = set(
        r[0] for r in con.execute(
            "SELECT rssd_id FROM id_crosswalk WHERE lei IS NULL"
        ).fetchall()
    )
    updates = [(lei, rssd) for rssd, lei in rssd_to_lei.items() if rssd in null_rssds]
    print(f"  applicable (lei currently NULL): {len(updates):,}")

    if "--dry-run" in sys.argv:
        print(f"  [DRY-RUN] would fill {len(updates):,} LEIs (lei={lei_before:,} -> "
              f"{lei_before + len(updates):,}); no write performed.")
        # sample a few proposed matches for eyeballing
        inv = {rssd: lei for rssd, lei in rssd_to_lei.items()}
        sample = con.execute(
            "SELECT rssd_id, name_legal FROM id_crosswalk "
            "WHERE lei IS NULL AND rssd_id IN "
            f"({','.join(str(r) for _, r in updates[:5]) or 'NULL'}) LIMIT 5"
        ).fetchall()
        for rssd, nm in sample:
            print(f"     rssd={rssd}  '{nm}'  -> {inv.get(rssd)}")
        con.close()
        return

    con.executemany(
        "UPDATE id_crosswalk SET lei = ?, lei_source = 'gleif' "
        "WHERE rssd_id = ? AND lei IS NULL",
        updates,
    )
    con.execute("CHECKPOINT")

    lei_after = con.execute(
        "SELECT COUNT(*) FROM id_crosswalk WHERE lei IS NOT NULL"
    ).fetchone()[0]
    n_gleif = con.execute(
        "SELECT COUNT(*) FROM id_crosswalk WHERE lei_source = 'gleif'"
    ).fetchone()[0]

    # Re-export id_crosswalk.parquet (mirrors 36_build_id_crosswalk export).
    out = XWALK_PARQUET.as_posix()
    con.execute(
        f"COPY (SELECT * FROM id_crosswalk ORDER BY rssd_id) "
        f"TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    n = con.execute("SELECT COUNT(*) FROM id_crosswalk").fetchone()[0]
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    con.close()

    lift = lei_after - lei_before
    print(f"\n  id_crosswalk LEI: {lei_before:,} -> {lei_after:,} (+{lift:,} via GLEIF; "
          f"lei_source='gleif' rows={n_gleif:,}; null_before={null_before:,})")
    print(f"  parquet={pq:,} parity={'OK' if n == pq else 'MISMATCH'}")
    if n != pq:
        sys.exit("PARITY MISMATCH — id_crosswalk.parquet out of sync")

    log_ingestion(
        "36b",
        f"GLEIF LEI widening: id_crosswalk.lei {lei_before:,} -> {lei_after:,} "
        f"(+{lift:,}; lei_source='gleif'={n_gleif:,}). Unambiguous normalized-name "
        f"match GLEIF US/ACTIVE legal_name <-> NIC institutions. {elapsed():.1f}s"
    )


if __name__ == "__main__":
    main()
