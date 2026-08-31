"""P02: Ingest all raw sources into the warehouse.

Runs every canonical ingest phase in dependency order. The canonical pipeline
(pipeline/scripts/) is the construction method of record; each phase is
idempotent (already-loaded periods are skipped).

Usage:
  python anu/scripts/P02_ingest_sources.py --list
  python anu/scripts/P02_ingest_sources.py              # all phases
  python anu/scripts/P02_ingest_sources.py 16 17 19     # selected phases only

Phases 27b (full H.8) needs FRED_API_KEY. Phase 07h needs a headed browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap as bs  # noqa: E402

PHASES = [
    "02_ingest_attributes.py",        # NIC institutions/attrs/branches/relationships
    "03_ingest_crsp.py",              # CRSP-FRB mapping
    "04_ingest_bhcf_txt.py",          # BHCF TXT 2000+
    "05_ingest_bhcf_csv.py",          # BHCSV pre-2000
    "07_ingest_call_reports.py",      # Chicago Fed XPT 1976-2002
    "07c_finish_phase0a.py",
    "07e_ingest_call_reports_cdr.py",  # CDR bulk 2012+
    "07f_recover_gap_from_cdr.py",
    "08_ingest_luck.py",              # Luck DTA
    "08b_slim_luck.py",               # dedup to 1959-1975 core
    "09_ingest_occ.py",               # OCC historical
    "09b_ingest_occ_finhist.py",      # finhist vintage
    "16_ingest_fdic_failures.py",
    "17_ingest_fdic_financials.py",
    "19_ingest_fdic_sod.py",
    "23_ingest_dfast.py",
    "24_ingest_pillar3.py",
    "25_ingest_fdic_history.py",
    "26_ingest_ncua.py",
    "27_ingest_fed_h8.py",            # 15 keyless FRED series
    "27b_ingest_fed_h8_disagg.py",    # full H.8 (FRED_API_KEY)
    "28_ingest_robin_panel.py",       # Failing Banks panel
    "29_ingest_volcker_catalogs.py",  # identifier/BHC/sector catalogs
    "30_ingest_stress_scenarios.py",
    "31_build_sdi_feature_panel.py",
    "33_parse_cdr_unrealized.py",
    "34_ingest_sec_edgar.py",
    "35_ingest_hmda.py",
    "36b_gleif_lei.py",
    "37_ingest_nic_identifiers.py",
    "37b_ingest_nic_attributes_ext.py",
    "39_ingest_ubpr.py",
    "41_ingest_y15.py",
    "42_ingest_ubpr_peer.py",
]


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for i, ph in enumerate(PHASES, 1):
            print(f"  {i:2}. {ph}")
        return 0
    only = {a for a in argv if not a.startswith("--")}
    bs.ensure_dirs()
    rc = 0
    for ph in PHASES:
        if only and not any(k in ph for k in only):
            continue
        rc |= bs.run_phase(ph)
        if rc:
            print(f"[P02] stopping at first failure: {ph}", file=sys.stderr)
            break
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
