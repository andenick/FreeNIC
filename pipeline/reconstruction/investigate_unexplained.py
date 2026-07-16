"""Investigate UNEXPLAINED cells in the value-fidelity reconciliations (honest disposition)."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

VAL = Path(os.environ.get("FREENIC_OUTPUTS", "Outputs") + "/reconstruction/validation")


def look(era: str, recon_name: str, key: list[str]):
    df = pd.read_parquet(VAL / recon_name)
    print(f"\n================ {era} ({recon_name}) ================")
    print("class totals:\n", df["class"].value_counts())
    un = df[df["class"] == "UNEXPLAINED"].copy()
    print(f"\nUNEXPLAINED cells: {len(un):,}")
    print("UNEXPLAINED by variable:\n", un["variable"].value_counts())
    # one-sided vs two-sided divergence split
    both = un["published"].notna() & un["built"].notna()
    print(f"UNEXPLAINED two-sided (both present, true value divergence): {int(both.sum()):,}")
    print(f"UNEXPLAINED one-sided (coverage gap): {int((~both).sum()):,}")
    # sample up to 20 two-sided divergences with delta/rel
    samp = un[both].copy()
    if len(samp):
        samp["delta"] = (samp["built"] - samp["published"]).abs()
        samp["rel"] = samp["delta"] / samp["published"].abs().replace(0, np.nan)
        cols = key + ["variable", "published", "built", "delta", "rel"]
        print("\nsample (up to 20) two-sided UNEXPLAINED:")
        with pd.option_context("display.width", 200, "display.max_columns", 20):
            print(samp.sort_values("rel", ascending=False)[cols].head(20).to_string(index=False))
        # per-variable rel distribution
        print("\ntwo-sided UNEXPLAINED rel-delta by variable (median / p90 / max):")
        g = samp.groupby("variable")["rel"].agg(["count", "median", lambda s: s.quantile(0.9), "max"])
        print(g.to_string())


if __name__ == "__main__":
    look("finhist", "reconciliation_finhist.parquet", ["bank_id", "year"])
    look("1959_1975", "reconciliation_1959_1975.parquet", ["id_rssd", "period_end"])
