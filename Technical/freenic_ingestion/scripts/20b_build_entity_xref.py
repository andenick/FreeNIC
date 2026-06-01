"""Phase 20b: Build the canonical entity_xref identity table.

PURPOSE
-------
`institutions` (the NIC active-entity attribute table, 217,210 rssds) is an
incomplete universe of "known" RSSD identities: it under-covers 1976-2011
defunct / merged / small entities. Referential checks that test filing rssds
*only* against `institutions` therefore report a misleadingly low match rate
(call_report 34%, luck 37.7%, fdic_financials 39.7%, fdic_sod 38.3% overall),
even though the misses are overwhelmingly historical entities NIC simply
tracks in OTHER public identity tables (chiefly `transformations`, which
records predecessor/successor RSSDs for mergers and charter changes).

`entity_xref` is the UNION of every distinct RSSD identity that appears in a
public NIC/identity table:

    institutions.rssd_id
  ∪ transformations.rssd_predecessor
  ∪ transformations.rssd_successor
  ∪ crsp_mapping.rssd_id
  ∪ robin_crosswalk.rssd_id
  ∪ robin_crosswalk.rssd_id_bhc
  ∪ bank_failures_enriched.rssd_id
  ∪ fdic_history (via cert->rssd crosswalk)

NO SYNTHESIS: every rssd in entity_xref comes verbatim from one of the source
tables above. No identities are invented; certs are mapped to rssds only via
the OBSERVED cert<->rssd pairs in institutions / robin_crosswalk /
bank_failures_enriched (the `cert2rssd` crosswalk).

A `source` provenance column records (pipe-delimited, sorted) which source
table(s) contributed each rssd, so consumers can see *why* an entity is known.

Non-destructive: CREATE OR REPLACE of `entity_xref` only; source tables are
never altered.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer


# Each source: (provenance_label, SELECT yielding a single column `r` of rssd ids).
# fdic_history is handled separately because it carries only fdic_cert and must
# be mapped through the observed cert->rssd crosswalk.
RSSD_SOURCES = [
    ("institutions",
     "SELECT DISTINCT rssd_id AS r FROM institutions WHERE rssd_id IS NOT NULL"),
    ("transformations_predecessor",
     "SELECT DISTINCT rssd_predecessor AS r FROM transformations WHERE rssd_predecessor IS NOT NULL"),
    ("transformations_successor",
     "SELECT DISTINCT rssd_successor AS r FROM transformations WHERE rssd_successor IS NOT NULL"),
    ("crsp_mapping",
     "SELECT DISTINCT rssd_id AS r FROM crsp_mapping WHERE rssd_id IS NOT NULL"),
    ("robin_crosswalk",
     "SELECT DISTINCT rssd_id AS r FROM robin_crosswalk WHERE rssd_id IS NOT NULL"),
    ("robin_crosswalk_bhc",
     "SELECT DISTINCT rssd_id_bhc AS r FROM robin_crosswalk WHERE rssd_id_bhc IS NOT NULL"),
    ("bank_failures_enriched",
     "SELECT DISTINCT rssd_id AS r FROM bank_failures_enriched WHERE rssd_id IS NOT NULL"),
    ("fdic_history",
     "SELECT DISTINCT c.rssd_id AS r FROM fdic_history h "
     "JOIN cert2rssd c ON h.fdic_cert = c.cert WHERE c.rssd_id IS NOT NULL"),
]

# Observed cert->rssd crosswalk, used ONLY to map fdic_history (cert-keyed).
CERT2RSSD_SQL = """
CREATE OR REPLACE TEMP TABLE cert2rssd AS
SELECT DISTINCT fdic_cert AS cert, rssd_id FROM institutions
    WHERE fdic_cert IS NOT NULL AND rssd_id IS NOT NULL
UNION
SELECT DISTINCT fdic_cert, rssd_id FROM robin_crosswalk
    WHERE fdic_cert IS NOT NULL AND rssd_id IS NOT NULL
UNION
SELECT DISTINCT cert, rssd_id FROM bank_failures_enriched
    WHERE cert IS NOT NULL AND rssd_id IS NOT NULL
"""

FILING_TABLES = [
    ("call_report_filings", "rssd_id"),
    ("luck_call_reports", "entity_id"),
    ("fdic_financials", "rssd_id"),
    ("fdic_sod", "rssd_id"),
]


def build_entity_xref(con):
    """Build entity_xref = de-duped UNION of all public rssd identity sources."""
    con.execute("SET progress_bar_time = 999999")  # suppress interactive progress bar
    con.execute(CERT2RSSD_SQL)

    # Stage every (rssd, source) pair, then aggregate to one row per rssd with
    # a sorted pipe-delimited provenance string.
    con.execute("CREATE OR REPLACE TEMP TABLE xref_stage (rssd_id INTEGER, source VARCHAR)")
    for label, query in RSSD_SOURCES:
        con.execute(
            f"INSERT INTO xref_stage SELECT r, '{label}' FROM ({query})"
        )

    con.execute("""
        CREATE OR REPLACE TABLE entity_xref AS
        SELECT
            rssd_id,
            STRING_AGG(DISTINCT source, '|' ORDER BY source) AS source,
            COUNT(DISTINCT source) AS n_sources
        FROM xref_stage
        GROUP BY rssd_id
    """)


def report(con):
    """Print per-source contribution and before/after match rates."""
    total = con.execute("SELECT COUNT(*) FROM entity_xref").fetchone()[0]
    inst = con.execute(
        "SELECT COUNT(DISTINCT rssd_id) FROM institutions WHERE rssd_id IS NOT NULL"
    ).fetchone()[0]
    print(f"\n  entity_xref: {total:,} distinct rssd_id "
          f"({total - inst:,} beyond institutions' {inst:,})")

    # Per-source membership (how many xref rssds each source vouches for).
    print("\n  Source membership (rssds each source contributes to):")
    rows = con.execute("""
        WITH exploded AS (
            SELECT rssd_id, UNNEST(STRING_SPLIT(source, '|')) AS s FROM entity_xref
        )
        SELECT s, COUNT(*) AS n FROM exploded GROUP BY s ORDER BY n DESC
    """).fetchall()
    for s, n in rows:
        print(f"    {s:<28} {n:>9,}")

    # Incremental (waterfall) contribution in source order.
    print("\n  Incremental contribution (waterfall, source order):")
    con.execute("CREATE OR REPLACE TEMP TABLE accum (r INTEGER)")
    con.execute(CERT2RSSD_SQL)
    for label, query in RSSD_SOURCES:
        new = con.execute(
            f"SELECT COUNT(*) FROM (SELECT DISTINCT r FROM ({query}) "
            "EXCEPT SELECT DISTINCT r FROM accum)"
        ).fetchone()[0]
        con.execute(f"INSERT INTO accum SELECT DISTINCT r FROM ({query})")
        cum = con.execute("SELECT COUNT(DISTINCT r) FROM accum").fetchone()[0]
        print(f"    +{label:<28} new={new:>8,}  cumulative={cum:>9,}")

    # Before/after match rate per filing table.
    print("\n  Filing-table match rate (distinct ids): institutions -> entity_xref")
    for tbl, idcol in FILING_TABLES:
        t = con.execute(f"SELECT COUNT(DISTINCT {idcol}) FROM {tbl}").fetchone()[0]
        m_inst = con.execute(f"""
            SELECT COUNT(DISTINCT f.{idcol}) FROM {tbl} f
            JOIN institutions i ON f.{idcol} = i.rssd_id
        """).fetchone()[0]
        m_xref = con.execute(f"""
            SELECT COUNT(DISTINCT f.{idcol}) FROM {tbl} f
            JOIN entity_xref x ON f.{idcol} = x.rssd_id
        """).fetchone()[0]
        print(f"    {tbl:<24} {m_inst/t*100:5.1f}% -> {m_xref/t*100:5.1f}%  "
              f"(n={t:,})")
    return total


def main():
    elapsed = timer()
    print("=== Phase 20b: Build entity_xref (canonical rssd identity universe) ===")

    con = get_db()
    build_entity_xref(con)
    total = report(con)
    con.close()

    secs = elapsed()
    log_ingestion("20b", f"entity_xref built: {total:,} distinct rssd identities "
                         f"(union of institutions/transformations/crsp_mapping/"
                         f"robin_crosswalk/bank_failures_enriched/fdic_history). {secs:.1f}s")
    print(f"\nPhase 20b complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
