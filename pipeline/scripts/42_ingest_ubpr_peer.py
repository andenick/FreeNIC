"""Phase 42: Ingest FFIEC CDR UBPR **Rank** and **Stats** (peer percentiles) — the official peer layer.

Source: Four-Periods bulk ZIPs acquired by 07i_acquire_ubpr_peer.py (Inputs/ubpr_rank_bulk,
ubpr_stats_bulk). Each ZIP = one YEAR (4 quarters), 27 tab-delimited schedule TXTs. Each schedule:
  row0 = column codes (UBPK#### rank / UBPS#### stats), row1 = mnemonic, row2 = description, data row3+.
  RANK  id cols: [Reporting Period, ID RSSD, Peer Group]      -> long table ubpr_peer_rank
  STATS id cols: [Reporting Period, Peer Group Description, Peer Group] -> long table ubpr_peer_stats

Melts each schedule wide->long via DuckDB UNPIVOT (row-by-row Python would be far too slow at rank scale).
Idempotent per ZIP (DELETE WHERE source_file = <zip> before insert). NO values fabricated.

Usage:
  python 42_ingest_ubpr_peer.py stats          # ingest all stats ZIPs on disk
  python 42_ingest_ubpr_peer.py rank 2024      # ingest rank ZIPs for given year(s)
  python 42_ingest_ubpr_peer.py both
"""
import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, INPUT_PATHS, timer, log_ingestion  # noqa: E402

BULK = INPUT_PATHS["cdr_call_bulk"].parent
CFG = {
    "rank":  {"dir": BULK / "ubpr_rank_bulk",  "table": "ubpr_peer_rank",
              "id_cols": ["Reporting Period", "ID RSSD", "Peer Group"], "code_prefix": "UBPK"},
    "stats": {"dir": BULK / "ubpr_stats_bulk", "table": "ubpr_peer_stats",
              "id_cols": ["Reporting Period", "Peer Group Description", "Peer Group"], "code_prefix": "UBPS"},
}


def ddl(con, prods):
    """Create ONLY the table(s) for the products being ingested (avoid leaving an empty table)."""
    if "rank" in prods:
        con.execute("""CREATE TABLE IF NOT EXISTS ubpr_peer_rank(
            reporting_period DATE, rssd_id INTEGER, peer_group VARCHAR,
            ubpr_code VARCHAR, value DOUBLE, source_file VARCHAR)""")
    if "stats" in prods:
        con.execute("""CREATE TABLE IF NOT EXISTS ubpr_peer_stats(
            reporting_period DATE, peer_group VARCHAR, peer_group_desc VARCHAR,
            ubpr_code VARCHAR, value DOUBLE, source_file VARCHAR)""")


def parse_period_sql(col):
    # "3/31/2024 11:59:59 PM" -> DATE. strptime on the date part before the space.
    return f"strptime(split_part({col}, ' ', 1), '%-m/%-d/%Y')::DATE"


def ingest_zip(con, prod, zp: Path):
    """Melt all 27 schedules into a per-zip staging temp table, then INSERT grain-deduped.
    A globally-unique UBPR code can appear in >1 schedule with the SAME value (verified
    max_spread=0); staging + GROUP-BY-grain collapses that redundancy so the grain is unique."""
    cfg = CFG[prod]
    src = zp.name
    # staging table mirrors the target's melt columns
    if prod == "rank":
        con.execute("CREATE OR REPLACE TEMP TABLE stage(reporting_period DATE, rssd_id INTEGER, "
                    "peer_group VARCHAR, ubpr_code VARCHAR, value DOUBLE)")
    else:
        con.execute("CREATE OR REPLACE TEMP TABLE stage(reporting_period DATE, peer_group VARCHAR, "
                    "peer_group_desc VARCHAR, ubpr_code VARCHAR, value DOUBLE)")
    with tempfile.TemporaryDirectory() as td:
        zf = zipfile.ZipFile(zp)
        sched = [n for n in zf.namelist() if n.lower().endswith(".txt") and "readme" not in n.lower()]
        for name in sched:
            tmp = Path(td) / "s.txt"
            tmp.write_bytes(zf.read(name))
            tp = tmp.as_posix()
            cols = [r[0] for r in con.execute(
                "SELECT column_name FROM (DESCRIBE SELECT * FROM "
                f"read_csv('{tp}', delim='\t', header=true, all_varchar=true, ignore_errors=true))").fetchall()]
            code_cols = [c for c in cols if c.upper().startswith(cfg["code_prefix"])]
            if not code_cols:
                continue
            in_list = ", ".join(f'"{c}"' for c in code_cols)
            rp, c1, c2 = (f'"{x}"' for x in cfg["id_cols"])
            base = (f"SELECT * FROM read_csv('{tp}', delim='\t', header=true, all_varchar=true, "
                    f"ignore_errors=true) WHERE {rp} LIKE '%/%'")
            if prod == "rank":
                con.execute(f"""INSERT INTO stage
                    SELECT {parse_period_sql(rp)}, TRY_CAST({c1} AS INTEGER), {c2},
                           ubpr_code, TRY_CAST(value AS DOUBLE)
                    FROM ({base}) UNPIVOT (value FOR ubpr_code IN ({in_list}))
                    WHERE value IS NOT NULL AND value <> ''""")
            else:
                con.execute(f"""INSERT INTO stage
                    SELECT {parse_period_sql(rp)}, {c2}, {c1}, ubpr_code, TRY_CAST(value AS DOUBLE)
                    FROM ({base}) UNPIVOT (value FOR ubpr_code IN ({in_list}))
                    WHERE value IS NOT NULL AND value <> ''""")
        zf.close()
    con.execute(f"DELETE FROM {cfg['table']} WHERE source_file = ?", [src])
    if prod == "rank":
        con.execute(f"""INSERT INTO ubpr_peer_rank
            SELECT reporting_period, rssd_id, peer_group, ubpr_code, ANY_VALUE(value), '{src}'
            FROM stage GROUP BY reporting_period, rssd_id, peer_group, ubpr_code""")
    else:
        con.execute(f"""INSERT INTO ubpr_peer_stats
            SELECT reporting_period, peer_group, ANY_VALUE(peer_group_desc), ubpr_code, ANY_VALUE(value), '{src}'
            FROM stage GROUP BY reporting_period, peer_group, ubpr_code""")
    inserted = con.execute(f"SELECT COUNT(*) FROM {cfg['table']} WHERE source_file = ?", [src]).fetchone()[0]
    print(f"  [{prod}] {src}: {inserted:,} rows")
    return inserted


def main():
    args = sys.argv[1:]
    prods = ["rank", "stats"] if (not args or args[0] == "both") else [args[0]]
    years = [a for a in args[1:] if a.isdigit()]
    elapsed = timer()
    con = get_db()
    ddl(con, prods)
    total = 0
    for prod in prods:
        if prod not in CFG:
            print(f"unknown product {prod}"); continue
        zips = sorted(CFG[prod]["dir"].glob("*.zip"))
        if years:
            zips = [z for z in zips if any(y in z.stem for y in years)]
        print(f"[{prod}] {len(zips)} ZIP(s)")
        for zp in zips:
            total += ingest_zip(con, prod, zp)
    con.close()
    secs = elapsed()
    log_ingestion("42", f"UBPR peer ingest: {total:,} rows in {secs:.1f}s")
    print(f"\nPhase 42 complete: {total:,} rows in {secs:.1f}s.")


if __name__ == "__main__":
    main()
