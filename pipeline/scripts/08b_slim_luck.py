"""Phase 8b: Slim luck_call_reports to its irreplaceable footprint (canonical, idempotent).

Runs AFTER 07/07b/07e (call_report_filings) and 08 (full Luck ingest). Makes the 2026-06-05
dedup reproducible from the pipeline itself rather than a one-off coverage_analysis script.

Policy (see Technical/FREENIC_PUBLICATION_DEDUP_PLAN.md, COVERAGE_GAPS §8):
  KEEP  - all pre-1976 rows (Fed-direct has 0 coverage before 1976Q1), AND
          all 1976+ rows whose (entity_id, period_end) is ABSENT from call_report_filings
          (the genuinely Fed-absent gap-fill, e.g. non-deposit trust companies).
  DROP  - all 1976+ rows whose (entity_id, period_end) IS present in call_report_filings
          (proven 99.88% redundant + value-reconciled 99.89% on core aggregates; query 1976+
          call reports from call_report_filings instead).

The keep-set is computed ON THE FLY from call_report_filings — no external artifact, fully
reproducible. Idempotent: re-running on an already-slim table deletes 0 rows.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer

CUT = "DATE '1976-01-01'"


def main():
    elapsed = timer()
    print("=== Phase 8b: Slim Luck to pre-1976 core + Fed-absent gap-fill ===")
    con = get_db()  # read-write; fails loudly if MCP holds the lock

    before = con.execute("SELECT COUNT(*) FROM luck_call_reports").fetchone()[0]
    print(f"  rows before: {before:,}")

    # Drop 1976+ rows that are covered (entity_id, period_end) by Fed-direct call_report_filings.
    deleted = con.execute(f"""
        DELETE FROM luck_call_reports L
        WHERE L.period_end >= {CUT}
          AND EXISTS (
              SELECT 1 FROM call_report_filings C
              WHERE C.rssd_id = L.entity_id AND C.period_end = L.period_end
          )
        RETURNING 1
    """).fetchall()
    n_del = len(deleted)
    con.execute("CHECKPOINT")

    after = con.execute("SELECT COUNT(*) FROM luck_call_reports").fetchone()[0]
    pre = con.execute(f"SELECT COUNT(*) FROM luck_call_reports WHERE period_end < {CUT}").fetchone()[0]
    gap = con.execute(f"SELECT COUNT(*) FROM luck_call_reports WHERE period_end >= {CUT}").fetchone()[0]
    rng = con.execute("SELECT MIN(period_end), MAX(period_end), COUNT(DISTINCT entity_id) FROM luck_call_reports").fetchone()
    con.close()

    print(f"  deleted (redundant 1976+): {n_del:,}")
    print(f"  rows after: {after:,}  (pre-1976 core: {pre:,} | Fed-absent gap-fill 1976+: {gap:,})")
    print(f"  span: {rng[0]}..{rng[1]} | {rng[2]:,} entities")
    print(f"  idempotent: {'YES (0 deleted)' if n_del == 0 else 'applied this run'}")

    log_ingestion("8b", f"Slim Luck: {before:,} -> {after:,} rows "
                  f"(dropped {n_del:,} redundant 1976+; kept pre-1976 {pre:,} + gap-fill {gap:,}). "
                  f"{rng[0]}..{rng[1]}. {elapsed():.1f}s")
    print(f"\nPhase 8b complete in {elapsed():.1f}s. (Re-export parquet via 12 to publish.)")


if __name__ == "__main__":
    main()
