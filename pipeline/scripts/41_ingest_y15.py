"""Phase 41: Ingest FR Y-15 (Banking Organization Systemic-Risk Report / G-SIB indicators).

Source: Inputs/y15_bulk/*_FRY15_Snapshot_All.csv (annual snapshots, acquired by 07h).
Wide format: NAME, ID_RSSD, AsOfDate, then RISK#### line-item columns. Melt the RISK columns
to long; keep numeric values (the systemic indicators) — the few text RISK columns (preparer/
contact) fail the numeric cast and are dropped. NO values fabricated.

Output: y15_systemic_indicators(rssd_id, period_end, risk_code, value, source_file).
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, INPUT_PATHS, OUTPUTS_DIR

SRC = INPUT_PATHS['cdr_call_bulk'].parent / "y15_bulk"


def main():
    elapsed = timer()
    print("=== Phase 41: FR Y-15 systemic-risk indicators ===")
    csvs = sorted(SRC.glob("*_FRY15_Snapshot_All.csv"))
    if not csvs:
        print(f"  no Y-15 CSVs in {SRC}; run 07h_acquire_y15.py first.")
        return
    con = get_db()
    con.execute("""CREATE TABLE IF NOT EXISTS y15_systemic_indicators (
        rssd_id INTEGER, period_end DATE, risk_code VARCHAR, value DOUBLE, source_file VARCHAR)""")
    for csv in csvs:
        src = csv.name
        # period from the filename's report-date prefix (headers vary by year; filename is stable)
        m = re.match(r"(\d{4})(\d{2})(\d{2})", src)
        period_end = pd.Timestamp(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
        raw = pd.read_csv(csv, dtype=str, keep_default_na=False)
        rssd_col = next((c for c in raw.columns if c.strip().upper() == "ID_RSSD"), None)
        risk_cols = [c for c in raw.columns if c.strip().upper().startswith("RISK")]
        if rssd_col is None or not risk_cols:
            print(f"  {src}: no ID_RSSD/RISK cols -- skip")
            continue
        long = raw.melt(id_vars=[rssd_col], value_vars=risk_cols,
                        var_name="risk_code", value_name="val")
        long["rssd_id"] = pd.to_numeric(long[rssd_col], errors="coerce")
        long["value"] = pd.to_numeric(long["val"], errors="coerce")
        long = long.dropna(subset=["rssd_id", "value"])
        long["rssd_id"] = long["rssd_id"].astype(int)
        long["period_end"] = period_end
        long["source_file"] = src
        df = long[["rssd_id", "period_end", "risk_code", "value", "source_file"]]
        if df.empty:
            print(f"  {src}: no numeric values parsed -- skip")
            continue
        pe = df["period_end"].iloc[0].date()
        if con.execute("SELECT COUNT(*) FROM y15_systemic_indicators WHERE period_end=?",
                       [pe]).fetchone()[0] > 0:
            print(f"  {src}: {pe} already loaded -- skip")
            continue
        con.register("y15_df", df)
        con.execute("INSERT INTO y15_systemic_indicators SELECT rssd_id, CAST(period_end AS DATE), "
                    "risk_code, value, source_file FROM y15_df")
        con.unregister("y15_df")
        con.execute("CHECKPOINT")
        print(f"  {src}: +{len(df):,} indicator values ({df.rssd_id.nunique()} institutions)")

    tot = con.execute("SELECT COUNT(*) FROM y15_systemic_indicators").fetchone()[0]
    nb = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM y15_systemic_indicators").fetchone()[0]
    npd = con.execute("SELECT COUNT(DISTINCT period_end) FROM y15_systemic_indicators").fetchone()[0]
    nc = con.execute("SELECT COUNT(DISTINCT risk_code) FROM y15_systemic_indicators").fetchone()[0]
    print(f"\n  y15_systemic_indicators: {tot:,} rows | {nb} institutions | {npd} years | {nc} RISK line items")
    out = (OUTPUTS_DIR / "parquet" / "y15_systemic_indicators.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM y15_systemic_indicators ORDER BY period_end, rssd_id, risk_code) "
                f"TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  parquet={pq:,} parity={'OK' if pq == tot else 'MISMATCH'}")
    con.close()
    log_ingestion("41", f"FR Y-15 systemic-risk indicators: {tot:,} rows, {nb} institutions, {npd} years, "
                  f"{nc} RISK line items (FFIEC NIC Y-15 snapshots). {elapsed():.1f}s")
    print(f"\nPhase 41 complete in {elapsed():.1f}s.")


if __name__ == "__main__":
    main()
