"""Materialise the *published* reference panels the G-MATCH harness validates against.

READ-ONLY over the warehouse. For each era we project the builder's documented published
source to the cell-level validation key + the variables that have a genuine published twin
in that source, renaming the source columns to the BUILT panel's names (the builder's own
documented correspondence: _BUILD_META "already_present" + self-smoke anchors + variable_map
source_ref). Derived-ratio / reconstructed-aggregate variables that the published source does
NOT carry are simply absent here — they have no published twin and cannot be cell-matched
against this source (the honest derivability/coverage boundary, SPEC §0).

MODL (1959-1975): published source = ``luck_wide`` (entity_id==id_rssd, period_end); levels +
income only (no derived ratios exist in luck_wide). MODL twin renames: othbor_liab->otherbor_liab.

finhist (1863-1941): published source = ``clean_bank_panel`` HIST stratum (bank_id, year),
the freeNIC finhist-equivalent HIST panel; ``*_nominal`` levels + the derived ``leverage``.

No warehouse writes; all paths absolute/forward-slash.
"""

from __future__ import annotations
import os

from pathlib import Path

import duckdb
import pandas as pd

WAREHOUSE = os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/freenic.duckdb"
OUT = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction/validation/published_refs")

# MODL: luck_wide source-col -> built/published-schema name (identity unless noted).
MODL_TWINS = {
    "assets": "assets", "cash": "cash", "securities": "securities", "deposits": "deposits",
    "equity": "equity", "othbor_liab": "otherbor_liab",            # rename
    "ffpurch": "ffpurch", "ln_re": "ln_re", "ln_ci": "ln_ci", "ln_cons": "ln_cons",
    "ln_cc": "ln_cc", "ln_fi": "ln_fi", "ln_oth": "ln_oth", "npl_tot": "npl_tot",
    "brokered_dep": "brokered_dep", "insured_deposits": "insured_deposits",
    "num_employees": "num_employees", "ytdint_inc_ln": "ytdint_inc_ln",
    "ytdint_exp_dep": "ytdint_exp_dep", "ytdllprov": "ytdllprov", "ytdnetinc": "ytdnetinc",
}

# finhist: clean_bank_panel source-col -> built/published-schema name.
FINHIST_TWINS = {
    "assets_nominal": "assets", "equity_nominal": "equity", "securities_nominal": "securities",
    "surplus_nominal": "surplus", "undivided_profits_nominal": "undivided_profits",
    "notes_nb_nominal": "notes_nb", "demand_deposits_nominal": "demand_deposits",
    "time_deposits_nominal": "time_deposits", "deposits_nominal": "deposits",
    "leverage": "leverage",                                        # the one derived ratio with a twin
}


def _null_profile(df: pd.DataFrame, keys: list[str]) -> dict:
    return {c: int(df[c].notna().sum()) for c in df.columns if c not in keys}


def build_modl(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    sel = ", ".join(f'"{src}" AS "{dst}"' for src, dst in MODL_TWINS.items())
    q = (f'SELECT entity_id AS id_rssd, period_end, {sel} FROM luck_wide '
         f"WHERE period_end BETWEEN DATE '1959-01-01' AND DATE '1975-12-31'")
    df = con.execute(q).fetchdf()
    return df


def build_finhist(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    sel = ", ".join(f'"{src}" AS "{dst}"' for src, dst in FINHIST_TWINS.items())
    q = (f'SELECT bank_id, year, {sel} FROM clean_bank_panel '
         f"WHERE era_group = 'HIST' AND year BETWEEN 1863 AND 1941")
    df = con.execute(q).fetchdf()
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(WAREHOUSE, read_only=True)
    try:
        modl = build_modl(con)
        fin = build_finhist(con)
    finally:
        con.close()

    modl_path = OUT / "published_luck_1959_1975.parquet"
    fin_path = OUT / "published_finhist_1863_1941.parquet"
    modl.to_parquet(modl_path, index=False)
    fin.to_parquet(fin_path, index=False)

    print(f"MODL published: {len(modl):,} rows, {modl.shape[1]} cols -> {modl_path}")
    print("  twin non-null counts:", _null_profile(modl, ["id_rssd", "period_end"]))
    print(f"finhist published: {len(fin):,} rows, {fin.shape[1]} cols -> {fin_path}")
    print("  twin non-null counts:", _null_profile(fin, ["bank_id", "year"]))
    print("  finhist unique(bank_id,year):", fin[["bank_id", "year"]].drop_duplicates().shape[0])


if __name__ == "__main__":
    main()
