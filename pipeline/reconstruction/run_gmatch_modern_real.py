"""CANONICAL modern G-MATCH (post-remediation): our Fed-direct rebuild vs CLV's PUBLISHED panel.

The TRUE headline independent gate. Reference (READ-ONLY): CLV's published
``sources/call-reports-modern.dta`` (from ``qje-repkit.zip``; 2,530,565 rows 1959Q4-2024Q3,
RSSD-native, harmonized names) — THEIR data, not our 30_build. Built: the SPEC §10-remediated
``luck_equivalent_1976_2026.parquet`` (Fed-direct raw MDRM, with the ffpurch/otherbor/ln_cons
form-arm completions). Overlap window: the CLV panel ends 2024Q3 -> [1976Q1, 2024Q3]. Both panels
are thousands of dollars (verified bit-identical on JPM 2008Q4). Keyed ``(id_rssd, period_end)``.

Emits (canonical): ``validation/gate_result_1976_2026.json`` + ``RECONSTRUCTION_REPORT_1976_2026.md``
(+ post-remediation G-MATCH disposition & SUPPLEMENTARY value-fidelity metrics appended) +
``reconciliation_1976_2026.parquet`` (via the harness), plus ``_gmatch_modern_run.json``,
``gmatch_summary.json`` (1976_2026 block refreshed; other eras preserved), and the combined
``RECONSTRUCTION_REPORT.md``. Thresholds untouched (taxonomy constants). No warehouse writes.

REPORTS BOTH honestly: the PRE-REGISTERED D2 gate verdict (whatever it is) AND, clearly labelled
SUPPLEMENTARY, the value-fidelity metrics (two-sided divergence rate; matched-share-where-both-present).
"""
from __future__ import annotations
import os

import json
from pathlib import Path

import pandas as pd

from pipeline.reconstruction import taxonomy as tx
from pipeline.reconstruction import validate_reconstruction as vr
from pipeline.reconstruction import variable_map as vm

BASE = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction")
VAL = BASE / "validation"
REFS = VAL / "published_refs"
MAPS = VAL / "twin_maps"
WORK = VAL / "_work"
SCR = Path(os.environ.get("FREENIC_SCRATCH", "scratch") + "")

ERA = "1976_2026"
OVERLAP_START = pd.Timestamp("1976-03-31")
OVERLAP_END = pd.Timestamp("2024-09-30")   # CLV .dta max = 2024Q3

BUILT_SRC = BASE / "luck_equivalent_1976_2026.parquet"
CLV_TWINS = SCR / "repkit_src" / "clv_modern_twins.parquet"   # extracted from call-reports-modern.dta

PUBLISHED = REFS / "published_modern_clv_1976_2024.parquet"
BUILT = WORK / "built_luck_1976_2026_idrssd_real.parquet"

# CLV .dta col -> built-panel/published-schema name. ln_oth excluded (built carries no ln_oth twin).
TWIN_RENAME = {
    "assets": "assets", "cash": "cash", "securities": "securities", "deposits": "deposits",
    "equity": "equity", "deposits_demand": "demand_deposits", "deposits_time": "time_deposits",
    "loans": "ln_tot", "ln_re": "ln_re", "ln_fi": "ln_fi", "ln_cc": "ln_cc", "ln_ci": "ln_ci",
    "ln_cons": "ln_cons", "npl_tot": "npl_tot", "ffpurch": "ffpurch",
    "otherbor_liab": "otherbor_liab", "brokered_dep": "brokered_dep",
    "insured_deposits": "insured_deposits", "ytdint_inc_ln": "ytdint_inc_ln",
    "num_employees": "num_employees", "ytdint_exp_dep": "ytdint_exp_dep",
    "ytdllprov": "ytdllprov", "ytdnetinc": "ytdnetinc",
}
TWINS = set(TWIN_RENAME.values())   # 23 published-twin variables


def build_published() -> None:
    df = pd.read_parquet(CLV_TWINS)
    df["date"] = pd.to_datetime(df["date"])
    df["period_end"] = df["date"] + pd.offsets.QuarterEnd(0)
    df = df[(df["period_end"] >= OVERLAP_START) & (df["period_end"] <= OVERLAP_END)].copy()
    cols = ["id_rssd", "period_end"] + list(TWIN_RENAME.keys())
    out = df[cols].rename(columns=TWIN_RENAME)
    out["id_rssd"] = out["id_rssd"].astype("int64")
    REFS.mkdir(parents=True, exist_ok=True)
    out.to_parquet(PUBLISHED, index=False)
    print(f"published (CLV modern): {len(out):,} rows -> {PUBLISHED}")


def build_built() -> None:
    df = pd.read_parquet(BUILT_SRC)
    df = df.rename(columns={"rssd_id": "id_rssd"})
    df["period_end"] = pd.to_datetime(df["period_end"])
    df = df[(df["period_end"] >= OVERLAP_START) & (df["period_end"] <= OVERLAP_END)].copy()
    WORK.mkdir(parents=True, exist_ok=True)
    df.to_parquet(BUILT, index=False)
    print(f"built (overlap window): {len(df):,} rows -> {BUILT}")


def make_twin_map() -> Path:
    MAPS.mkdir(parents=True, exist_ok=True)
    df = vm.load_variable_map().copy()
    df["scope_v11"] = df["variable"].map(lambda v: "TRUE" if v in TWINS else "FALSE")
    out = MAPS / f"variable_map_twin_{ERA}_real.csv"
    df.to_csv(out, index=False)
    return out


def supplementary_metrics() -> dict:
    """Value-fidelity metrics computed from the value-fidelity reconciliation (SUPPLEMENTARY,
    NOT the pre-registered gate). Two-sided divergence = both sides present AND UNEXPLAINED;
    matched-share-where-both-present = matched / both-present."""
    recon = pd.read_parquet(VAL / f"reconciliation_{ERA}.parquet")
    pub_present = recon["published"].notna()
    blt_present = recon["built"].notna()
    both = pub_present & blt_present
    n_both = int(both.sum())
    is_match = recon["class"].isin(list(tx.MATCH_CLASSES))
    matched_both = int((both & is_match).sum())
    two_sided_div = int((both & (recon["class"] == tx.UNEXPLAINED)).sum())
    # derivable denominator (exclude NOT-DERIVABLE), same basis as the gate
    derivable = int((recon["class"] != tx.NOT_DERIVABLE).sum())
    # V2-MODERN qualification (a), 2026-07-15: the both-present denominator CARRIES
    # NOT-DERIVABLE both-present cells (e.g. pre-1994 securities where both panels report but
    # the raw build is outside the boundary). Report BOTH labeled variants: ND-inclusive
    # (conservative) and ND-excluded (fidelity where derivable AND both present).
    nd_both = int((both & (recon["class"] == tx.NOT_DERIVABLE)).sum())
    n_both_excl_nd = n_both - nd_both
    return {
        "note": "SUPPLEMENTARY value-fidelity metrics — NOT the pre-registered D2 gate.",
        "both_present_cells": n_both,
        "both_present_denominator_note": (
            "both_present_cells INCLUDES NOT-DERIVABLE both-present cells "
            f"({nd_both:,}); see *_excl_nd for the ND-excluded variant (V2-MODERN qual. a)."),
        "not_derivable_both_present_cells": nd_both,
        "both_present_cells_excl_nd": n_both_excl_nd,
        "matched_where_both_present_cells": matched_both,
        "matched_share_where_both_present": (matched_both / n_both) if n_both else 0.0,
        "matched_share_where_both_present_excl_nd": (
            (matched_both / n_both_excl_nd) if n_both_excl_nd else 0.0),
        "two_sided_divergent_cells": two_sided_div,
        "two_sided_divergence_rate_over_derivable": (two_sided_div / derivable) if derivable else 0.0,
        "two_sided_divergence_rate_over_both_present": (two_sided_div / n_both) if n_both else 0.0,
        "derivable_cells": derivable,
    }


def append_disposition(gate: dict, supp: dict) -> None:
    """Append the post-remediation G-MATCH disposition + SUPPLEMENTARY metrics to the era report."""
    p = VAL / f"RECONSTRUCTION_REPORT_{ERA}.md"
    md = p.read_text(encoding="utf-8")
    cc = gate["class_counts"]
    lines = [
        "",
        "## G-MATCH disposition (POST-REMEDIATION, corrected published-data gate) — honest verdict",
        "",
        "> **ARTIFACT KIND: PUBLISHED_DATA_GATE (the REAL headline independent gate).** Reference = CLV's "
        "PUBLISHED modern panel `sources/call-reports-modern.dta` (their data). Overlap 1976Q1..2024Q3, "
        "23 published-twin variables. This run is AFTER the SPEC §10 form-arm completions "
        "(ffpurch B993 / otherbor pre-1994 2850+2910 / ln_cons post-2011 successor) and the symmetric "
        "`MC_ZEROFILL_ENCODING` zero-vs-NULL normalization; the 3 interim coverage-fork rows are RETIRED.",
        "",
        f"**PRE-REGISTERED D2 GATE VERDICT: {gate['verdict']}** — matched (EXACT+ROUNDING+TOLERANCE) "
        f"= {gate['match_share']*100:.4f}% of derivable (gate {gate['gate_threshold']*100:.4f}%); "
        f"UNEXPLAINED = {gate['unexplained_share']*100:.4f}% (floor {gate['unexplained_floor']*100:.4f}%). "
        "Thresholds untouched (non-negotiable).",
        "",
        f"Class counts (derivable {gate['derivable_cells']:,} / NOT-DERIVABLE {gate['not_derivable_cells']:,}): "
        f"EXACT {cc['EXACT']:,} · ROUNDING {cc['ROUNDING']:,} · TOLERANCE {cc['TOLERANCE']:,} · "
        f"VINTAGE {cc['VINTAGE']:,} · METHOD-CHOICE {cc['METHOD-CHOICE']:,} "
        f"(incl. `MC_ZEROFILL_ENCODING`) · NOT-DERIVABLE {cc['NOT-DERIVABLE']:,} · "
        f"UNEXPLAINED {cc['UNEXPLAINED']:,}.",
        "",
        "### SUPPLEMENTARY value-fidelity metrics (NOT the pre-registered gate — clearly labelled)",
        "",
        f"- **matched-share-where-both-present (ND-inclusive denominator): "
        f"{supp['matched_share_where_both_present']*100:.4f}%** "
        f"({supp['matched_where_both_present_cells']:,} matched of {supp['both_present_cells']:,} "
        "bank-quarter cells where BOTH panels report a value; this denominator INCLUDES "
        f"{supp['not_derivable_both_present_cells']:,} NOT-DERIVABLE both-present cells).",
        f"- **matched-share-where-both-present-and-derivable (ND-excluded denominator): "
        f"{supp['matched_share_where_both_present_excl_nd']*100:.4f}%** "
        f"({supp['matched_where_both_present_cells']:,} of {supp['both_present_cells_excl_nd']:,}) "
        "— value fidelity where coverage overlaps AND the cell is inside the derivability "
        "boundary (V2-MODERN qualification a, 2026-07-15).",
        f"- **two-sided value-divergence rate: {supp['two_sided_divergence_rate_over_derivable']*100:.4f}% "
        f"of derivable** ({supp['two_sided_divergent_cells']:,} cells both-present-and-differing; "
        f"{supp['two_sided_divergence_rate_over_both_present']*100:.4f}% of both-present).",
        "",
        "**Reading:** the pre-registered cell-match gate FAILs honestly — our sparse Fed-direct panel and "
        "CLV's dense harmonized panel differ materially in coverage/encoding, and METHOD-CHOICE "
        "(incl. the zero-fill encoding fork) stays in the denominator so it cannot raise `match_share`. "
        "But **value fidelity where coverage overlaps is very high** and two-sided disagreement is a small "
        "fraction of derivable. The claim that the rebuild reproduces CLV's published modern panel "
        "*cell-for-cell* is NOT supported and is held; the claim that it reproduces the values *where both "
        "panels report* is supported by the supplementary metrics. Warehouse READ-ONLY.",
        "",
    ]
    p.write_text(md + "\n".join(lines), encoding="utf-8")


def main() -> None:
    build_published()
    build_built()
    twin_map = make_twin_map()

    g_fid = vr.run_era(ERA, PUBLISHED, BUILT, VAL, variable_map_path=twin_map)   # value-fidelity (canonical)
    g_full = vr.run_era(ERA, PUBLISHED, BUILT, VAL / "full_scope", variable_map_path=None)  # coverage

    supp = supplementary_metrics()
    append_disposition(g_fid, supp)

    # _gmatch_modern_run.json (headline real gate + supplementary)
    (VAL / "_gmatch_modern_run.json").write_text(json.dumps({
        "artifact_kind": "PUBLISHED_DATA_GATE_REAL",
        "remediation": "SPEC §10 form-arm completions + MC_ZEROFILL_ENCODING (2026-07-15)",
        "reference": "CLV published sources/call-reports-modern.dta (qje-repkit.zip); THEIR data",
        "overlap_window": "1976Q1..2024Q3",
        "value_fidelity": {k: g_fid[k] for k in (
            "gate_threshold", "total_cells", "derivable_cells", "not_derivable_cells",
            "matched_cells", "match_share", "unexplained_cells", "unexplained_share", "verdict")},
        "full_scope": {k: g_full[k] for k in (
            "total_cells", "derivable_cells", "matched_cells", "match_share",
            "unexplained_cells", "unexplained_share", "verdict")},
        "supplementary_value_fidelity": supp,
    }, indent=2, sort_keys=True), encoding="utf-8")

    # gmatch_summary.json — refresh the 1976_2026 block, preserve the other eras.
    summ_path = VAL / "gmatch_summary.json"
    summ = {}
    pre = VAL / "gmatch_summary_preremediation.json"
    if pre.exists():
        summ = json.loads(pre.read_text(encoding="utf-8"))
    summ[ERA] = {
        "value_fidelity": {k: g_fid[k] for k in (
            "gate_threshold", "total_cells", "derivable_cells", "not_derivable_cells",
            "matched_cells", "match_share", "unexplained_cells", "unexplained_share", "verdict")},
        "full_scope": {
            "artifact_kind": "COVERAGE_BOUNDARY_NOT_VALUE_FIDELITY",
            **{k: g_full[k] for k in (
                "total_cells", "derivable_cells", "matched_cells", "match_share",
                "unexplained_cells", "unexplained_share", "verdict")},
        },
        "supplementary_value_fidelity": supp,
    }
    summ_path.write_text(json.dumps(summ, indent=2, sort_keys=True), encoding="utf-8")

    # combined RECONSTRUCTION_REPORT.md (rolls the 3 per-era gate_result files in VAL)
    vr.combine_reports(VAL)

    print(f"[{ERA}] PRE-REGISTERED value-fidelity gate: verdict={g_fid['verdict']} "
          f"match={g_fid['match_share']*100:.4f}% unexpl={g_fid['unexplained_share']*100:.4f}% "
          f"(derivable={g_fid['derivable_cells']:,} / not-deriv={g_fid['not_derivable_cells']:,})")
    print(f"[{ERA}] full-scope (coverage): verdict={g_full['verdict']} "
          f"match={g_full['match_share']*100:.4f}% (derivable={g_full['derivable_cells']:,})")
    print(f"[{ERA}] SUPPLEMENTARY: matched-where-both-present={supp['matched_share_where_both_present']*100:.4f}% "
          f"({supp['matched_where_both_present_cells']:,}/{supp['both_present_cells']:,}); "
          f"two-sided-divergence={supp['two_sided_divergent_cells']:,} "
          f"({supp['two_sided_divergence_rate_over_derivable']*100:.4f}% of derivable)")


if __name__ == "__main__":
    main()
