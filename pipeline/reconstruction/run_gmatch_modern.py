"""Drive the G-MATCH harness for the MODERN era (MODC 1976_2026) — the campaign's headline gate.

This is the TRUE independent re-derivation gate: the Fed-direct raw-MDRM rebuild
(``luck_equivalent_1976_2026.parquet``, built purely from ``call_report_filings`` via the
``variable_map`` recipes) vs the published Luck panel (``public_luck_panel.parquet`` — the
freeNIC 30_build public Luck-equivalent, ~99.7% Luck-.dta-validated, the reference the
builder's own self-smoke anchors against). Unlike the derivation-layer eras (MODL/finhist),
REAL divergences are expected here (documented coverage/method extensions over 30_build,
plus any genuinely UNEXPLAINED cells).

Two runs, both against the READ-ONLY published panel + the REAL built parquet, keyed
``(id_rssd, period_end)`` (SPEC §6.1). Both source panels are RSSD-native (``rssd_id``); the
harness aligns MODC on ``id_rssd`` (``entity_spine.ALIGNMENT_KEY``), so we materialise
key-normalised copies (``rssd_id`` -> ``id_rssd``) — a pure rename, no value touched:

  * value-fidelity (canonical, -> validation/): scoped to the 25 variables that HAVE a
    published twin in ``public_luck_panel`` (a documented --variable-map override). This is
    the gate the D2 99.5% (MODC) / 0.1% UNEXPLAINED-floor thresholds evaluate.
  * full-scope (-> validation/full_scope/): the SHIPPED variable_map, so every scoped built
    variable with no published twin (derived ratios, reconstructed aggregates) surfaces as an
    honest one-sided COVERAGE gap. A COVERAGE-BOUNDARY artifact, NOT a value-fidelity result.

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
WORK = VAL / "_work"

ERA = "1976_2026"

# Source panels (RSSD-native, rssd_id key).
PUBLIC_LUCK_PANEL = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/public_luck_panel.parquet")
BUILT_SRC = BASE / "luck_equivalent_1976_2026.parquet"

# Key-normalised copies the harness reads (rssd_id -> id_rssd; values untouched).
PUBLISHED = REFS / "published_luck_1976_2026.parquet"
BUILT = WORK / "built_luck_1976_2026_idrssd.parquet"

# The published-twin variable set == the non-key columns present in public_luck_panel.
# (All 25 are also present in the built panel — verified.)
TWINS_1976_2026 = {
    "assets", "deposits", "equity", "cash", "ln_tot", "ln_re", "ln_ci", "ln_cons", "ln_agr",
    "demand_deposits", "domestic_dep", "oreo", "llres", "surplus", "subdebt", "liab_tot",
    "securities", "time_deposits", "npl_tot", "ffsold", "ffpurch", "ytdint_inc", "ytdint_exp",
    "ytdnetinc", "ytdllprov",
}


def _normalise_key(src: Path, dst: Path) -> None:
    """Write a key-normalised copy of a panel: rssd_id -> id_rssd, period_end -> datetime.
    Pure rename + dtype-normalise; no value column is touched."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(src)
    if "id_rssd" not in df.columns:
        if "rssd_id" not in df.columns:
            raise KeyError(f"{src.name}: neither id_rssd nor rssd_id present; have {list(df.columns)}")
        df = df.rename(columns={"rssd_id": "id_rssd"})
    df["period_end"] = pd.to_datetime(df["period_end"])
    df.to_parquet(dst, index=False)


def make_twin_map() -> Path:
    """A variable_map override scoping ONLY the era's 25 published-twin variables (scope_v11)."""
    MAPS.mkdir(parents=True, exist_ok=True)
    df = vm.load_variable_map().copy()
    df["scope_v11"] = df["variable"].map(lambda v: "TRUE" if v in TWINS_1976_2026 else "FALSE")
    out = MAPS / f"variable_map_twin_{ERA}.csv"
    df.to_csv(out, index=False)
    return out


def run_one(out_dir: Path, variable_map_path: Path | None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    return vr.run_era(ERA, PUBLISHED, BUILT, out_dir, variable_map_path=variable_map_path)


def main() -> None:
    _normalise_key(PUBLIC_LUCK_PANEL, PUBLISHED)
    _normalise_key(BUILT_SRC, BUILT)
    twin_map = make_twin_map()

    g_fid = run_one(VAL, twin_map)                      # canonical value-fidelity
    g_full = run_one(VAL / "full_scope", None)          # shipped scope (coverage boundary)

    print(f"[{ERA}] value-fidelity: verdict={g_fid['verdict']} "
          f"match={g_fid['match_share']*100:.4f}% unexpl={g_fid['unexplained_share']*100:.4f}% "
          f"(derivable={g_fid['derivable_cells']:,} / not-deriv={g_fid['not_derivable_cells']:,})")
    print(f"[{ERA}] full-scope:     verdict={g_full['verdict']} "
          f"match={g_full['match_share']*100:.4f}% unexpl={g_full['unexplained_share']*100:.4f}% "
          f"(derivable={g_full['derivable_cells']:,})")

    (VAL / "_gmatch_modern_run.json").write_text(json.dumps({
        "value_fidelity": {k: g_fid[k] for k in
                           ("gate_threshold", "total_cells", "derivable_cells",
                            "not_derivable_cells", "matched_cells", "match_share",
                            "unexplained_cells", "unexplained_share", "verdict")},
        "full_scope": {k: g_full[k] for k in
                       ("total_cells", "derivable_cells", "matched_cells", "match_share",
                        "unexplained_cells", "unexplained_share", "verdict")},
    }, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
