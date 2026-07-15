#!/usr/bin/env python3
"""build_slice.py — export a small REAL curated slice of the FreeNIC dataset.

Reads the large source parquet exports in Projects/freenic/Outputs/parquet and writes a
compact DuckDB (target < ~100 MB) holding a handful of real tables plus a few precomputed
aggregate tables for the draft freenic.org explorer. NO full DB / multi-GB parquet is shipped.

All rows are a real subset of the published FreeNIC data — nothing is fabricated.
"""
from __future__ import annotations

import os
from pathlib import Path

import duckdb

# Build-host locations, all overridable by env var. FREENIC_OUTPUTS is the warehouse
# export dir holding parquet/, SHA256SUMS.txt, PROVENANCE.csv and the derived spine.
OUTPUTS_ROOT = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs"))
SRC = Path(os.environ.get("FREENIC_PARQUET_DIR", str(OUTPUTS_ROOT / "parquet")))
# The runnable site app whose app/data the slice is written into (default: ../site).
SITE_DIR = Path(os.environ.get("FREENIC_SITE_DIR", str(Path(__file__).resolve().parent.parent / "site")))
OUT = SITE_DIR / "app" / "data" / "freenic_slice.duckdb"


def src(name: str) -> str:
    return f"read_parquet('{(SRC / (name + '.parquet')).as_posix()}')"


# The full warehouse (read-only) holds the version-pinned `dict` taxonomy schema
# (from the public bank-data-dictionary repo). The parquet exports do not carry it,
# so the dict slice tables are read directly from the warehouse DuckDB.
WAREHOUSE = Path(os.environ.get("FREENIC_WAREHOUSE", str(OUTPUTS_ROOT / "freenic.duckdb")))


def main() -> None:
    if OUT.exists():
        OUT.unlink()
    con = duckdb.connect(str(OUT))

    # ---- 1. bank_failures: full real table (4,115 rows, FDIC + Robin, 1934-2025) ----
    con.execute(f"CREATE TABLE bank_failures AS SELECT * FROM {src('bank_failures')}")

    # ---- 2. fred_series: full real Fed banking macro series (~130k rows, small) ----
    con.execute(f"CREATE TABLE fred_series AS SELECT * FROM {src('fred_series')}")

    # ---- 3. institutions_active: real subset — active institutions only, trimmed cols ----
    con.execute(
        f"""
        CREATE TABLE institutions_active AS
        SELECT rssd_id, name_legal, name_short, entity_type, charter_type,
               city, state_code, fdic_cert, date_established, is_active
        FROM {src('institutions')}
        WHERE is_active = TRUE
        """
    )

    # ---- Precomputed aggregate tables (small, real, derived) ----
    # failures per year
    con.execute(
        """
        CREATE TABLE agg_failures_by_year AS
        SELECT failure_year AS year, COUNT(*) AS n_failures,
               SUM(total_assets) AS total_assets, SUM(estimated_loss) AS total_loss
        FROM bank_failures
        WHERE failure_year IS NOT NULL
        GROUP BY failure_year ORDER BY failure_year
        """
    )
    # failures by state
    con.execute(
        """
        CREATE TABLE agg_failures_by_state AS
        SELECT state_code, COUNT(*) AS n_failures, SUM(total_assets) AS total_assets
        FROM bank_failures WHERE state_code IS NOT NULL
        GROUP BY state_code ORDER BY n_failures DESC
        """
    )
    # active institutions by state
    con.execute(
        """
        CREATE TABLE agg_institutions_by_state AS
        SELECT state_code, COUNT(*) AS n
        FROM institutions_active WHERE state_code IS NOT NULL
        GROUP BY state_code ORDER BY n DESC
        """
    )
    # active institutions by entity type
    con.execute(
        """
        CREATE TABLE agg_institutions_by_type AS
        SELECT entity_type, COUNT(*) AS n
        FROM institutions_active WHERE entity_type IS NOT NULL
        GROUP BY entity_type ORDER BY n DESC
        """
    )
    # FRED series catalog (one row per series)
    con.execute(
        """
        CREATE TABLE fred_catalog AS
        SELECT series_id, ANY_VALUE(series_name) AS series_name,
               COUNT(*) AS n_obs,
               MIN(observation_date) AS first_date, MAX(observation_date) AS last_date
        FROM fred_series GROUP BY series_id ORDER BY series_id
        """
    )

    # ---- long_bank_aggregates_1863_2026: the replicated 163-year spine -------
    # Real derived aggregate panel (year x metric: num_banks / total_assets /
    # total_deposits / total_loans), with a `definition` toggle, `source_series`
    # provenance, and `junction_flag` markers at the regime joins (1896/1914/1934).
    # 810 rows, 1863-2026. Source: Projects/freenic/Outputs (long sequence build).
    lba = (OUTPUTS_ROOT / "long_bank_aggregates_1863_2026.parquet").as_posix()
    con.execute(
        f"CREATE TABLE long_bank_aggregates_1863_2026 AS "
        f"SELECT * FROM read_parquet('{lba}')"
    )

    # ---- dict taxonomy slice (version-pinned bank-data-dictionary) ----------
    # The `dict` schema in the warehouse is the harmonized variable taxonomy
    # (schedule line-items, UBPR concepts, the variable->view access map, edit
    # relationships, and meta). All are small except `relationships`, which carries
    # long free-text columns we drop here, baking a compact SUMMARY instead. Read
    # the warehouse read-only and ATTACH it so we can copy across DB files.
    con.execute(
        f"ATTACH '{WAREHOUSE.as_posix()}' AS wh (READ_ONLY)"
    )
    # full small tables
    con.execute("CREATE TABLE dict_schedule_lineitems AS SELECT * FROM wh.dict.schedule_lineitems")
    con.execute("CREATE TABLE dict_ubpr_concepts     AS SELECT * FROM wh.dict.ubpr_concepts")
    con.execute("CREATE TABLE dict_variable_access_map AS SELECT * FROM wh.dict.variable_access_map")
    con.execute("CREATE TABLE dict_meta              AS SELECT * FROM wh.dict.meta")
    # relationships SUMMARY — drop the long free-text fields (expression truncated
    # to 200 chars; condition_text / sources / codes-list dropped) to keep it small.
    con.execute(
        """
        CREATE TABLE dict_relationships_summary AS
        SELECT rel_id, scope, kind,
               substr(expression, 1, 200) AS expression,
               codes,
               severity, status, empirical_pass_rate, empirical_n
        FROM wh.dict.relationships
        """
    )
    con.execute("DETACH wh")

    # report
    print("=== curated slice tables ===")
    for (t,) in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name"
    ).fetchall():
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:32s} {n:>10,} rows")
    con.close()

    mb = OUT.stat().st_size / (1024 * 1024)
    print(f"\nslice file: {OUT}")
    print(f"slice size: {mb:.2f} MB  (target < 100 MB)")
    assert mb < 100, "slice exceeds 100 MB budget"

    # ---- content layer: merge explanations + bake per-schedule CSVs --------
    # The dictionary explorer's prose comes from the reviewed staging files, and
    # each schedule page offers a per-schedule CSV. Both are baked here from the
    # freshly built slice so a rebuild keeps content + CSVs in lock-step.
    import build_content
    build_content.main()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
