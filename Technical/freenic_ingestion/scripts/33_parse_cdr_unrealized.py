"""V0.2 (parse) — parse the FFIEC CDR Public bulk ZIPs (downloaded by
_v0_cdr_bulk_playwright.py) into a tidy panel of the fair-value / duration / brokered
fields that FDIC SDI lacks. One row per (rssd_id, period_end).

Schedules / MDRMs (verified against the 2022Q4 bulk headers):
  RCB  -> AFS amortized cost  RCFD1772 (else RCON1772)
          AFS fair value      RCFD1773 (else RCON1773)
          HTM amortized cost  RCFD1754 (else RCON1754)
  RC   -> HTM fair value      RCFDJJ34 (else RCONJJ34)   [ASU 2016-13 fair value of HTM]
          AOCI                RCFDB530 (else RCONB530)
  RCE  -> brokered deposits   RCON2365  (TOTAL BROKERED DEPOSITS)  *** see note ***
          time dep 100-250k   RCONJ473  (maturity bucket)
          time dep >250k      RCONJ474  (maturity bucket)

NOTE (MDRM correction, logged): the V0 plan listed "brokered deposits RCONJ473/J474".
Per the FFIEC schema those two codes are TIME-DEPOSIT maturity buckets, NOT brokered
deposits. The true brokered-deposit total is RCON2365. We capture all three and label
them honestly; no values are fabricated or relabeled.

Banks file EITHER RCFD (consolidated, foreign offices) OR RCON (domestic only): we take
RCFD when non-empty, else RCON. Values are in $ thousands (FFIEC standard) — same unit as
SDI ASSET, enabling cert/rssd-level reconciliation.

Output: data/correia/cdr_unrealized_2019_2025.parquet
"""
import zipfile
import io
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("D:/Arcanum/Projects/Volcker/Technical/AnuData/data/correia/_cdr_raw")
OUT = Path("D:/Arcanum/Projects/Volcker/Technical/AnuData/data/correia/cdr_unrealized_2019_2025.parquet")

# schedule keyword -> {output_col: (rcfd_code, rcon_code)}
SCHED_FIELDS = {
    "Schedule RCB": {
        "afs_amort_cost": ("RCFD1772", "RCON1772"),
        "afs_fair_value": ("RCFD1773", "RCON1773"),
        "htm_amort_cost": ("RCFD1754", "RCON1754"),
        # CORRECTED: true HTM fair value is RCFD1771 (RCB), NOT RCFDJJ34. RCFDJJ34 reports
        # HTM net of credit-loss allowance (~= amortized cost) post ASU 2016-13, which gives
        # a spurious ~0 unrealized loss (verified vs SVB 10-K: RCFD1771=$76.2B = true FV).
        "htm_fair_value": ("RCFD1771", "RCON1771"),
    },
    "Schedule RC ": {
        "aoci":           ("RCFDB530", "RCONB530"),
    },
    "Schedule RCE ": {
        "brokered_deposits":  ("RCON2365", "RCON2365"),
        "time_dep_100_250k":  ("RCONJ473", "RCONJ473"),
        "time_dep_gt_250k":   ("RCONJ474", "RCONJ474"),
    },
}


def read_sched(z, member, code_map):
    """Return DataFrame indexed by IDRSSD with one column per output field."""
    with z.open(member) as f:
        raw = f.read().decode("utf-8", "replace")
    lines = raw.split("\n")
    header = lines[0].rstrip("\r").split("\t")
    header = [h.strip().strip('"') for h in header]
    col_idx = {c: i for i, c in enumerate(header)}
    id_i = col_idx.get("IDRSSD")
    if id_i is None:
        return None
    # data starts after the descriptive 2nd row
    out = {}
    rssd = []
    vals = {k: [] for k in code_map}
    for ln in lines[2:]:
        if not ln.strip():
            continue
        parts = ln.rstrip("\r").split("\t")
        if len(parts) <= id_i:
            continue
        try:
            rid = int(parts[id_i].strip().strip('"'))
        except ValueError:
            continue
        rssd.append(rid)
        for outcol, (rcfd, rcon) in code_map.items():
            v = None
            for code in (rcfd, rcon):
                ci = col_idx.get(code)
                if ci is not None and ci < len(parts):
                    raw_v = parts[ci].strip().strip('"')
                    if raw_v not in ("", "."):
                        try:
                            v = float(raw_v)
                            break
                        except ValueError:
                            pass
            vals[outcol].append(v)
    df = pd.DataFrame({"rssd_id": rssd, **vals})
    return df.groupby("rssd_id", as_index=False).first()


def parse_zip(zp: Path) -> pd.DataFrame:
    m = re.search(r"(\d{8})", zp.name)
    ymd = m.group(1)
    period_end = pd.Timestamp(f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}")
    z = zipfile.ZipFile(zp)
    # POR -> cert
    por_name = [n for n in z.namelist() if "POR" in n][0]
    with z.open(por_name) as f:
        por = pd.read_csv(f, sep="\t", dtype=str, usecols=[0, 1],
                          names=["rssd_id", "cert"], header=0)
    por["rssd_id"] = pd.to_numeric(por["rssd_id"], errors="coerce")
    por["cert"] = pd.to_numeric(por["cert"], errors="coerce")
    por = por.dropna(subset=["rssd_id"]).drop_duplicates("rssd_id")
    por["rssd_id"] = por["rssd_id"].astype(int)

    base = por[["rssd_id", "cert"]].copy()
    for kw, code_map in SCHED_FIELDS.items():
        members = [n for n in z.namelist() if kw in n and n.endswith(".txt")]
        if not members:
            print(f"  [{ymd}] WARN schedule '{kw}' not found")
            continue
        parts = [read_sched(z, mm, code_map) for mm in members]
        parts = [p for p in parts if p is not None and not p.empty]
        sched_df = pd.concat(parts).groupby("rssd_id", as_index=False).first() if parts else None
        if sched_df is not None:
            base = base.merge(sched_df, on="rssd_id", how="left")
    base["period_end"] = period_end
    base["year"] = period_end.year
    z.close()
    return base


def _write_table(panel):
    """WS1 (2026-05-31): persist the CDR panel as the canonical freeNIC table
    `cdr_unrealized_losses` (the Volcker parquet is kept for CLV consumers)."""
    import duckdb
    from utils import DB_PATH, log_ingestion
    _w = duckdb.connect(str(DB_PATH))
    _w.register("panel_df", panel)
    _w.execute("CREATE OR REPLACE TABLE cdr_unrealized_losses AS SELECT * FROM panel_df")
    _w.unregister("panel_df")
    _w.close()
    pmin = pd.to_datetime(panel.period_end).min().date()
    pmax = pd.to_datetime(panel.period_end).max().date()
    log_ingestion("33", f"cdr_unrealized_losses table built: {len(panel):,} rows, "
                        f"{panel.rssd_id.nunique():,} entities, periods {pmin}..{pmax} "
                        f"(FFIEC CDR fair-value/AOCI/brokered).")
    print(f"[write] freeNIC table cdr_unrealized_losses: {len(panel):,} rows")


def main():
    zips = sorted(RAW.glob("call_single_*.zip"))
    if not zips:
        # No raw ZIPs (e.g. cleaned up): (re)build the freeNIC table from the
        # canonical parquet if it exists, so this step stays idempotent without re-download.
        if OUT.exists():
            print(f"[parse] no CDR ZIPs in {RAW}; loading existing {OUT.name} to (re)build the table")
            panel = pd.read_parquet(OUT)
            _write_table(panel)
            return
        print("[BLOCKED] no CDR ZIPs and no existing parquet at", OUT)
        sys.exit(2)
    print(f"[parse] {len(zips)} ZIP(s)")
    frames = []
    for zp in zips:
        df = parse_zip(zp)
        frames.append(df)
        print(f"  [{zp.name}] rows={len(df):,} rssd={df.rssd_id.nunique():,}")
    panel = pd.concat(frames, ignore_index=True)

    # derived unrealized loss (amort cost - fair value; positive = unrealized LOSS)
    panel["afs_unrealized_loss"] = panel["afs_amort_cost"] - panel["afs_fair_value"]
    panel["htm_unrealized_loss"] = panel["htm_amort_cost"] - panel["htm_fair_value"]
    panel["total_unrealized_loss"] = panel[["afs_unrealized_loss", "htm_unrealized_loss"]].sum(
        axis=1, min_count=1)

    cols = ["rssd_id", "cert", "period_end", "year",
            "afs_amort_cost", "afs_fair_value", "htm_amort_cost", "htm_fair_value",
            "afs_unrealized_loss", "htm_unrealized_loss", "total_unrealized_loss",
            "aoci", "brokered_deposits", "time_dep_100_250k", "time_dep_gt_250k"]
    panel = panel[cols]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(OUT, index=False)
    _write_table(panel)
    print(f"\n[write] {OUT}")
    print(f"[write] rows={len(panel):,} rssd={panel.rssd_id.nunique():,} "
          f"periods={sorted(panel.period_end.dt.strftime('%Y-%m-%d').unique())}")

    print("\n========== VALIDATION ==========")
    print("non-null fraction per field (all periods):")
    for c in cols[4:]:
        print(f"  {c:22} {panel[c].notna().mean():.3f}")

    print("\n2022Q4 crisis-bank unrealized-loss check (SVB 802866, Signature 2942690, FRC 4114567):")
    p22 = panel[panel.period_end == "2022-12-31"]
    for name, rssd in [("SVB", 802866), ("Signature", 2942690), ("First Republic", 4114567)]:
        r = p22[p22.rssd_id == rssd]
        if len(r):
            r = r.iloc[0]
            print(f"  {name:16} cert={r.cert} AFS amort={r.afs_amort_cost} fv={r.afs_fair_value} "
                  f"HTM amort={r.htm_amort_cost} htm_fv={r.htm_fair_value} "
                  f"total_unrl_loss={r.total_unrealized_loss} aoci={r.aoci} "
                  f"brokered={r.brokered_deposits}")
        else:
            print(f"  {name:16} rssd={rssd}: NOT in 2022Q4 CDR")

    # unrealized_loss / equity percentile in 2022Q4 (the V2 SVB-killer ratio).
    # equity from the SDI panel (EQ) joined by rssd.
    try:
        sdi = pd.read_parquet("D:/Arcanum/Projects/Volcker/Technical/AnuData/data/correia/"
                              "sdi_feature_panel.parquet")
        eq22 = sdi[sdi.year == 2022][["rssd_id", "assets", "equity_ratio"]].copy()
        eq22["equity"] = eq22.assets * eq22.equity_ratio
        m = p22.merge(eq22[["rssd_id", "equity"]], on="rssd_id", how="inner")
        m["unrl_to_equity"] = m.total_unrealized_loss / m.equity
        m = m[m.equity > 0]
        print(f"\nunrealized_loss/equity coverage in 2022Q4: {len(m):,} banks "
              f"({len(m)/len(p22)*100:.1f}% of CDR filers joined to SDI equity)")
        for name, rssd in [("SVB", 802866), ("Signature", 2942690), ("First Republic", 4114567)]:
            r = m[m.rssd_id == rssd]
            if len(r):
                v = r.unrl_to_equity.iloc[0]
                pct = (m.unrl_to_equity < v).mean() * 100
                print(f"  {name:16} unrl/equity={v:.3f} ({pct:.1f}th %ile)")
    except Exception as e:
        print(f"[warn] unrl/equity percentile step skipped: {str(e)[:80]}")
    print("================================")


if __name__ == "__main__":
    main()
