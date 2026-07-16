"""Drive the G-MATCH harness for the two ready eras (MODL 1959-1975, finhist 1863-1941).

Two runs per era, both against the READ-ONLY published-twin panels built by
``build_published_refs.py`` and the REAL built parquets:

  * value-fidelity (canonical, -> validation/): scoped to the variables that HAVE a published
    twin in the source (a documented --variable-map override). This is the gate the D2
    99.9% (MODL) / 99.5% (finhist) thresholds evaluate — value fidelity where a reference exists.
  * full-scope (-> validation/full_scope/): the SHIPPED variable_map, so every scoped built
    variable with no published twin (derived ratios, reconstructed aggregates) surfaces as an
    honest one-sided coverage gap. Not a tuning knob — a transparency artifact.

Thresholds are untouched (taxonomy constants). No warehouse writes.
"""

from __future__ import annotations
import os

import json
from pathlib import Path

import pandas as pd

from pipeline.reconstruction import validate_reconstruction as vr
from pipeline.reconstruction import variable_map as vm

BASE = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction")
VAL = BASE / "validation"
REFS = VAL / "published_refs"
MAPS = VAL / "twin_maps"

BUILT = {
    "1959_1975": BASE / "luck_core_1959_1975.parquet",
    "finhist": BASE / "finhist_equivalent_1863_1941.parquet",
}
PUBLISHED = {
    "1959_1975": REFS / "published_luck_1959_1975.parquet",
    "finhist": REFS / "published_finhist_1863_1941.parquet",
}
# The published-twin variable sets (== the renamed columns in the published-ref panels).
TWINS = {
    "1959_1975": {
        "assets", "cash", "securities", "deposits", "equity", "otherbor_liab", "ffpurch",
        "ln_re", "ln_ci", "ln_cons", "ln_cc", "ln_fi", "ln_oth", "npl_tot", "brokered_dep",
        "insured_deposits", "num_employees", "ytdint_inc_ln", "ytdint_exp_dep", "ytdllprov",
        "ytdnetinc",
    },
    "finhist": {
        "assets", "equity", "securities", "surplus", "undivided_profits", "notes_nb",
        "demand_deposits", "time_deposits", "deposits", "leverage",
    },
}


def make_twin_map(era: str) -> Path:
    """A variable_map override scoping ONLY the era's published-twin variables (scope_v11)."""
    MAPS.mkdir(parents=True, exist_ok=True)
    df = vm.load_variable_map()  # shipped
    twin = TWINS[era]
    df = df.copy()
    df["scope_v11"] = df["variable"].map(lambda v: "TRUE" if v in twin else "FALSE")
    out = MAPS / f"variable_map_twin_{era}.csv"
    df.to_csv(out, index=False)
    return out


def run_one(era: str, out_dir: Path, variable_map_path: Path | None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    gate = vr.run_era(era, PUBLISHED[era], BUILT[era], out_dir,
                      variable_map_path=variable_map_path)
    return gate


def main() -> None:
    summary = {}
    for era in ("1959_1975", "finhist"):
        twin_map = make_twin_map(era)
        g_fid = run_one(era, VAL, twin_map)                       # canonical value-fidelity
        g_full = run_one(era, VAL / "full_scope", None)           # shipped scope (coverage)
        summary[era] = {
            "value_fidelity": {k: g_fid[k] for k in
                               ("gate_threshold", "total_cells", "derivable_cells",
                                "not_derivable_cells", "matched_cells", "match_share",
                                "unexplained_cells", "unexplained_share", "verdict")},
            "full_scope": {k: g_full[k] for k in
                           ("total_cells", "derivable_cells", "matched_cells", "match_share",
                            "unexplained_cells", "unexplained_share", "verdict")},
        }
        print(f"[{era}] value-fidelity: verdict={g_fid['verdict']} "
              f"match={g_fid['match_share']*100:.4f}% unexpl={g_fid['unexplained_share']*100:.4f}% "
              f"(derivable={g_fid['derivable_cells']:,})")
        print(f"[{era}] full-scope:     verdict={g_full['verdict']} "
              f"match={g_full['match_share']*100:.4f}% unexpl={g_full['unexplained_share']*100:.4f}% "
              f"(derivable={g_full['derivable_cells']:,})")
    (VAL / "gmatch_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True),
                                             encoding="utf-8")


if __name__ == "__main__":
    main()
