"""Phase 36 (Step 2, upgraded W18): build `id_crosswalk` — the keystone identity join.

RSSD <-> FDIC cert <-> SEC CIK <-> LEI, plus the authoritative NIC multi-regulator
identifiers (OCC / NCUA / OTS-thrift / CUSIP / ABA / tax). LEI and the regulator IDs
now come AUTHORITATIVELY from `nic_entity_identifiers` (Fed-direct NIC, phase 37) —
a big upgrade over the prior name-matched-only LEI. SEC CIK + ticker still come from
`sec_cik_crosswalk` via unambiguous normalized-name match. HMDA name-matched LEI is kept
ONLY as a fallback where NIC has no LEI. One row per RSSD carrying >=1 external id.
Idempotent: CREATE OR REPLACE.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, OUTPUTS_DIR

_SUFFIX = re.compile(r"\b(NATIONAL ASSOCIATION|N\.?A\.?|NA|INCORPORATED|INC|CORPORATION|CORP|"
                     r"COMPANY|CO|LLC|L\.?L\.?C\.?|LP|L\.?P\.?|FSB|F\.?S\.?B\.?|SSB|THE)\b")
_NONWORD = re.compile(r"[^A-Z0-9 ]")
_WS = re.compile(r"\s+")


def norm(name):
    if not name:
        return ""
    s = _NONWORD.sub(" ", str(name).upper())
    s = _SUFFIX.sub(" ", s)
    return _WS.sub(" ", s).strip()


def main():
    elapsed = timer()
    print("=== Phase 36: build id_crosswalk (RSSD<->cert<->CIK<->LEI + NIC reg IDs) ===")
    con = get_db()

    # fetchall() -> clean python types (None for SQL NULL, no pandas NA ambiguity)
    inst_idx = {}
    nmap = {}
    for rssd_id, name_legal, fdic_cert, entity_type in con.execute(
            "SELECT rssd_id, name_legal, fdic_cert, entity_type FROM institutions "
            "WHERE name_legal IS NOT NULL").fetchall():
        rs = int(rssd_id)
        inst_idx[rs] = (name_legal, fdic_cert, entity_type)
        k = norm(name_legal)
        if len(k) >= 3:
            nmap.setdefault(k, set()).add(rs)
    nmap = {k: next(iter(v)) for k, v in nmap.items() if len(v) == 1}
    print(f"  unambiguous NIC names: {len(nmap):,}")

    # CIK -> rssd via name match (unchanged)
    rssd_cik = {}
    sec_rows = con.execute("SELECT cik, entity_name, ticker FROM sec_cik_crosswalk").fetchall()
    for cik, entity_name, ticker in sec_rows:
        rs = nmap.get(norm(entity_name))
        if rs is not None:
            rssd_cik[rs] = (int(cik), ticker)
    print(f"  CIK->RSSD matched: {len(rssd_cik):,} / {len(sec_rows):,} sec rows")

    # HMDA name-matched LEI -> rssd (FALLBACK only)
    hmda_lei = {int(rssd): lei for rssd, lei in con.execute("""
        SELECT rssd_id, lei FROM hmda_summary WHERE rssd_id IS NOT NULL
        GROUP BY rssd_id, lei
        QUALIFY ROW_NUMBER() OVER (PARTITION BY rssd_id ORDER BY SUM(loan_count) DESC) = 1
    """).fetchall()}
    print(f"  HMDA name-matched LEI (fallback): {len(hmda_lei):,}")

    # AUTHORITATIVE NIC identifiers (phase 37)
    nic = {}
    for row in con.execute("""
        SELECT rssd_id, id_lei, id_fdic_cert, id_occ, id_ncua, id_thrift, id_cusip, id_aba_prim, id_tax
        FROM nic_entity_identifiers""").fetchall():
        nic[int(row[0])] = dict(id_lei=row[1], id_fdic_cert=row[2], id_occ=row[3], id_ncua=row[4],
                                id_thrift=row[5], id_cusip=row[6], id_aba_prim=row[7], id_tax=row[8])
    print(f"  NIC authoritative identifier rows: {len(nic):,}")

    # universe: any rssd with >=1 external id
    rssds = sorted(set(nic) | set(rssd_cik) | set(hmda_lei))
    rows = []
    n_nic_lei = n_hmda_lei = 0
    for rs in rssds:
        nm, cert, et = inst_idx.get(rs, (None, None, None))
        cik, tk = rssd_cik.get(rs, (None, None))
        nr = nic.get(rs)
        nic_lei = (nr['id_lei'] if nr is not None else None)
        if nic_lei:
            lei, lei_source = nic_lei, "nic"
            n_nic_lei += 1
        elif hmda_lei.get(rs):
            lei, lei_source = hmda_lei[rs], "hmda_name_match"
            n_hmda_lei += 1
        else:
            lei, lei_source = None, None
        # fdic_cert: prefer institutions, else NIC
        nic_cert = nr['id_fdic_cert'] if nr is not None else None
        cert_final = int(cert) if cert is not None else (int(nic_cert) if nic_cert is not None else None)
        rows.append((
            rs, cert_final, nm, et, cik, tk, lei, lei_source,
            (nr['id_occ'] if nr is not None else None),
            (nr['id_ncua'] if nr is not None else None),
            (nr['id_thrift'] if nr is not None else None),
            (nr['id_cusip'] if nr is not None else None),
            (nr['id_aba_prim'] if nr is not None else None),
            (nr['id_tax'] if nr is not None else None),
        ))

    con.execute("DROP TABLE IF EXISTS id_crosswalk")
    con.execute("""CREATE TABLE id_crosswalk (
        rssd_id INTEGER, fdic_cert INTEGER, name_legal VARCHAR, entity_type VARCHAR,
        cik INTEGER, ticker VARCHAR, lei VARCHAR, lei_source VARCHAR,
        id_occ VARCHAR, id_ncua VARCHAR, id_thrift VARCHAR, id_cusip VARCHAR,
        id_aba_prim VARCHAR, id_tax VARCHAR)""")
    con.executemany("INSERT INTO id_crosswalk VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.execute("CHECKPOINT")

    out = (OUTPUTS_DIR / "parquet" / "id_crosswalk.parquet").as_posix()
    con.execute(f"COPY (SELECT * FROM id_crosswalk ORDER BY rssd_id) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    n = con.execute("SELECT COUNT(*) FROM id_crosswalk").fetchone()[0]
    nc = con.execute("SELECT COUNT(*) FROM id_crosswalk WHERE cik IS NOT NULL").fetchone()[0]
    nl = con.execute("SELECT COUNT(*) FROM id_crosswalk WHERE lei IS NOT NULL").fetchone()[0]
    nce = con.execute("SELECT COUNT(*) FROM id_crosswalk WHERE fdic_cert IS NOT NULL").fetchone()[0]
    nocc = con.execute("SELECT COUNT(*) FROM id_crosswalk WHERE id_occ IS NOT NULL").fetchone()[0]
    nncua = con.execute("SELECT COUNT(*) FROM id_crosswalk WHERE id_ncua IS NOT NULL").fetchone()[0]
    pq = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    con.close()
    print(f"\n  id_crosswalk: {n:,} rows | cik={nc:,} | lei={nl:,} (nic={n_nic_lei:,}, hmda={n_hmda_lei:,}) "
          f"| cert={nce:,} | occ={nocc:,} | ncua={nncua:,}")
    print(f"  parquet={pq:,} parity={'OK' if n == pq else 'MISMATCH'}")
    log_ingestion("36", f"id_crosswalk (W18 authoritative): {n:,} rows (cik={nc:,}, lei={nl:,} "
                  f"[nic={n_nic_lei:,}/hmda={n_hmda_lei:,}], cert={nce:,}, occ={nocc:,}, ncua={nncua:,}). "
                  f"Authoritative NIC IDs from nic_entity_identifiers. {elapsed():.1f}s")


if __name__ == "__main__":
    main()
