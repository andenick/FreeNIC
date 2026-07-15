"""Phase 7f (A3): SURGICAL recovery of the Luck-only 1976+ gap cells from FFIEC CDR.

The 2,285 gap cells (entity_id, period_end absent from call_report_filings; mostly non-deposit
trust companies, 2001-2006) are recovered WITHOUT duplicating the existing Chicago Fed layer:
for each gap period that CDR offers (>=2001), parse the CDR Single-Period ZIP (reusing 07e's
parser) and insert ONLY rows whose (rssd_id, period_end) is in the gap-set. Those cells are
absent from call_report_filings by definition, so the insert is duplicate-free.

Reversible: recovered rows carry source_file='cdrgap_<zip>' -> undo via
  DELETE FROM call_report_filings WHERE source_file LIKE 'cdrgap_%'.

After this, re-run 08b_slim_luck.py (the recovered cells now exist in call_report_filings, so
08b drops them from luck) and re-export. Idempotent: re-running skips (rssd,period) already present.
"""
import importlib.util
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from utils import get_db, DB_PATH, INPUT_PATHS, OUTPUTS_DIR  # noqa: E402

# import 07e's parser (module name starts with a digit -> importlib)
spec = importlib.util.spec_from_file_location("ingest07e", HERE / "07e_ingest_call_reports_cdr.py")
m07e = importlib.util.module_from_spec(spec); spec.loader.exec_module(m07e)
parse_zip_to_long = m07e.parse_zip_to_long

RAW = INPUT_PATHS['cdr_call_bulk']
KEEP = (OUTPUTS_DIR.parent / "Technical" / "coverage_analysis" / "d2_keep_cells.parquet").as_posix()
CDR_MIN = "2001-01-01"  # CDR Single-Period bulk availability floor


def main():
    con = get_db()
    # gap-set restricted to CDR-recoverable range
    gap = con.execute(f"""
        SELECT DISTINCT entity_id AS rssd_id, period_end
        FROM read_parquet('{KEEP}')
        WHERE period_end >= DATE '{CDR_MIN}'
    """).df()
    periods = sorted(gap['period_end'].astype(str).unique())
    print(f"gap cells in CDR range (>= {CDR_MIN}): {len(gap):,} across {len(periods)} periods")

    recovered_total = 0
    recovered_cells = 0
    per_period = []
    have_zip, no_zip = [], []
    for pe in periods:
        ymd = pe.replace("-", "")
        zp = RAW / f"call_single_{ymd}.zip"
        gp = gap[gap['period_end'].astype(str) == pe]
        gap_rssds = set(int(x) for x in gp['rssd_id'])
        if not zp.exists():
            no_zip.append(ymd)
            continue
        have_zip.append(ymd)
        df = parse_zip_to_long(zp, pe)
        df_gap = df[df['rssd_id'].isin(gap_rssds)].copy()
        found_rssds = set(df_gap['rssd_id'].unique())
        if not df_gap.empty:
            df_gap['source_file'] = 'cdrgap_' + df_gap['source_file'].astype(str)
            # idempotency: drop (rssd,period) already in call_report_filings
            con.register('df_gap', df_gap)
            con.execute("""
                INSERT INTO call_report_filings (rssd_id, period_end, schedule, variable_id, value, source_file)
                SELECT g.rssd_id, g.period_end, g.schedule, g.variable_id, g.value, g.source_file
                FROM df_gap g
                WHERE NOT EXISTS (
                    SELECT 1 FROM call_report_filings c
                    WHERE c.rssd_id = g.rssd_id AND c.period_end = g.period_end
                )
            """)
            con.unregister('df_gap')
            recovered_total += len(df_gap)
        recovered_cells += len(found_rssds & gap_rssds)
        per_period.append((pe, len(gap_rssds), len(found_rssds & gap_rssds), len(df_gap)))
        print(f"  {pe}: gap_rssds={len(gap_rssds)} found_in_cdr={len(found_rssds & gap_rssds)} rows_inserted={len(df_gap):,}")

    con.execute("CHECKPOINT")
    con.close()
    print(f"\n[summary] periods with ZIP: {len(have_zip)} | missing ZIP: {len(no_zip)} -> {no_zip}")
    print(f"  gap entity-quarters recovered (found in CDR): {recovered_cells:,}")
    print(f"  rows inserted into call_report_filings: {recovered_total:,} (source_file LIKE 'cdrgap_%')")
    print("  NEXT: run 08b_slim_luck.py to drop the now-recovered cells from luck, then re-export.")


if __name__ == "__main__":
    main()
