"""Generate anu/series_registry.json — the canonical FreeNIC data contract.

The registry is organized by DATA TABLE / TABLE FAMILY, not by individual
series: the warehouse serves ~5 billion rows over 67 Parquet files, so the
unit of replication is the served table (e.g. 'bank_failures', 'fred_series',
'call_report_filings'), each carrying its source family, construction scripts,
coverage, and row count.

Row counts and tiers are merged from the authoritative release manifest:
  1. --remote  https://data.freenic.org/release_manifest.json  (served v1.1.0, 67 files)
  2. fallback: release-tools/release_v1.0.0/release_manifest.json (61 root files)
     + the committed reconstruction-layer row counts below.

Usage:
  python anu/scripts/make_registry.py [--remote] [--local]

Writes anu/series_registry.json. No network required with --local.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "series_registry.json"

REMOTE_MANIFEST = "https://data.freenic.org/release_manifest.json"
LOCAL_MANIFEST = REPO_ROOT / "release-tools" / "release_v1.0.0" / "release_manifest.json"

RELEASE_VERSION = "1.1.0"
RELEASE_DATE = "2026-07-15"
DATA_VINTAGE = "2026Q1"

# Reconstruction layer (v1.1.0) row counts as served under reconstruction/.
# Source: served release_manifest.json (v1.1.0), verified against the local
# warehouse build 2026-07-15.
RECONSTRUCTION_ROWS = {
    "luck_core_1959_1975.parquet": 601566,
    "luck_equivalent_1976_2026.parquet": 2026104,
    "finhist_equivalent_1863_1941.parquet": 367312,
    "reconciliation_1976_2026.parquet": 40261405,
    "reconciliation_1959_1975.parquet": 7470087,
    "reconciliation_finhist.parquet": 2632440,
}

PD = "US federal government work (public domain)"  # most common license

# ---------------------------------------------------------------------------
# Curated per-table metadata. Keys are the served Parquet file names.
# source.url is the public acquisition point; `access` documents the honesty
# tier: public (keyless), public-key (free API key), public-browser (public but
# JS-driven bulk UI), bundled (bulk historical file, see DPR), manual
# (hand-collected), internal-derived (FreeNIC build artifact).
# ---------------------------------------------------------------------------
C = {}


def entry(series_id, file, family, title, desc, src_name, src_url, license_,
          access, retrieved, method, scripts, transforms, units, freq,
          cov, status, notes):
    C[file] = dict(
        series_id=series_id, family=family, title=title, description=desc,
        src_name=src_name, src_url=src_url, license=license_, access=access,
        retrieved=retrieved, method=method, scripts=scripts,
        transforms=transforms, units=units, frequency=freq,
        coverage=cov, status=status, notes=notes)


# ------------------------------------------------------------- FDIC BankFind
entry(
    "FDIC_FAILURES", "bank_failures.parquet", "FDIC BankFind Suite",
    "Bank Failures 1934-2026",
    "Every FDIC-insured bank failure on record: failing institution, failure "
    "date, estimated loss to the Deposit Insurance Fund, and total assets where "
    "reported. 4,115 failure events.",
    "FDIC BankFind Suite API - failures endpoint",
    "https://api.fdic.gov/banks/failures", PD, "public", "2026-05-27",
    "Full API pull (paginated JSON), flattened to one row per failure event.",
    ["16_ingest_fdic_failures.py"],
    ["json_flatten"],
    "failure events; estimated loss and total assets in USD",
    "event", {"start": "1934", "end": "2026"}, "verified",
    "Includes the 2023 failure wave (SVB, Signature, First Republic).")

entry(
    "FDIC_FINANCIALS", "fdic_financials.parquet", "FDIC BankFind Suite",
    "FDIC SDI Financials 1984-2026",
    "Quarterly financial statements for every FDIC-insured institution from the "
    "Statistics on Depository Institutions (SDI): 69.5M institution-quarter-"
    "variable observations, wide-to-long.",
    "FDIC BankFind Suite API - financials endpoint (Statistics on Depository "
    "Institutions)",
    "https://api.fdic.gov/banks/financials", PD, "public", "2026-04-30",
    "168 paginated JSON pages concatenated, loaded via DuckDB JSON reader, "
    "SQL-unpivoted wide-to-long.",
    ["17_ingest_fdic_financials.py"],
    ["json_concat", "wide_to_long"],
    "USD in SDI reporting units (see FDIC SDI codebook per variable)",
    "quarterly", {"start": "1984Q1", "end": "2026Q1"}, "verified",
    "Long format: one row per (institution, quarter, variable).")

entry(
    "FDIC_HISTORY", "fdic_history.parquet", "FDIC BankFind Suite",
    "FDIC Institution History 1782-2026",
    "Institution event history: mergers, acquisitions, name changes, charter "
    "conversions, closings - 582K events back to 1782.",
    "FDIC BankFind Suite API - history endpoint",
    "https://api.fdic.gov/banks/history", PD, "public", "2026-05-27",
    "Paginated API pull, flattened to one row per event.",
    ["25_ingest_fdic_history.py"],
    ["json_flatten"],
    "event records (dates, event codes)",
    "event", {"start": "1782", "end": "2026"}, "verified", "")

entry(
    "FDIC_SOD", "fdic_sod.parquet", "FDIC Summary of Deposits",
    "FDIC Summary of Deposits 1994-2025",
    "Branch-level deposit records from the annual Summary of Deposits survey: "
    "2.8M branch-year records with deposit amounts.",
    "FDIC BankFind Suite API - SOD endpoint",
    "https://banks.data.fdic.gov/api/sod", PD, "public", "2025-10-31",
    "Paginated API download (limit=10000) cached as JSON pages, then flattened.",
    ["18_download_fdic_sod.py", "19_ingest_fdic_sod.py"],
    ["paginated_download", "json_flatten"],
    "USD deposit amounts; count of branches",
    "annual", {"start": "1994", "end": "2025"}, "verified", "")

entry(
    "FDIC_SDI_FEATURES", "fdic_sdi_features.parquet", "FDIC BankFind Suite",
    "SDI-Derived Bank Feature Panel 1984-2025",
    "Annual institution-level feature panel derived from fdic_financials: "
    "asset ratios, NIM/ROA, log age, and F1/F3/F5 forward failure flags used "
    "in failure-prediction research. 413K institution-years.",
    "FreeNIC derived (from FDIC SDI financials)",
    "https://api.fdic.gov/banks/financials", "MIT (FreeNIC build)", 
    "internal-derived", RELEASE_DATE,
    "Deterministic SQL feature build over fdic_financials.",
    ["31_build_sdi_feature_panel.py"],
    ["ratio_features", "forward_failure_flags", "log_age"],
    "ratios (dimensionless), percent, log-years",
    "annual", {"start": "1984", "end": "2025"}, "verified",
    "Derived table - the public API is the upstream source.")

# ------------------------------------------------------------ FFIEC Call Reports
entry(
    "CALL_REPORTS", "call_report_filings.parquet", "FFIEC Call Reports",
    "Consolidated Call Reports 1976-2026",
    "The unified Call Report long table: 1.92 billion (institution, quarter, "
    "MDRM item) observations across 50 years, harmonized from three vintages: "
    "Chicago Fed Commercial Bank Data (1976-2002), FFIEC CDR public bulk "
    "(2012+), and gap-fill from CDR. This single table carries the modern "
    "regulatory balance-sheet and income-statement core of the warehouse.",
    "FFIEC Central Data Repository (public bulk) + Chicago Fed Commercial "
    "Bank Data (historical vintage)",
    "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx", PD,
    "public-browser", "2026-03-31",
    "Three-track ingest: SAS XPT files 1976-2002 (146 quarterly files, "
    "wide-to-long over 2,800+ variable columns); FFIEC CDR bulk ZIPs 2012+ "
    "via the bulk download flow; CDR gap-fill for missing quarters. All "
    "tracks unpivot to (rssd, period_end, mdrm_item, value).",
    ["07_ingest_call_reports.py", "07d_acquire_cdr_call_bulk.py",
     "07e_ingest_call_reports_cdr.py", "07f_recover_gap_from_cdr.py"],
    ["xpt_read", "wide_to_long", "zip_extract", "period_keyed_merge"],
    "varies by MDRM item (USD thousands for $ items, counts, ratios - see "
    "MDRM definitions)",
    "quarterly", {"start": "1976Q1", "end": "2026Q1"}, "verified",
    "The 1976-2002 XPT vintage is the Chicago Fed Commercial Bank Data "
    "product, distributed under its own license (institutional/subscription "
    "distribution); public keyless coverage starts 2001+ at FFIEC CDR. See "
    "D03 for the honest reproduction ladder.")

# ------------------------------------------------------------------- FFIEC UBPR
entry(
    "UBPR_RATIOS", "ubpr_ratios.parquet", "FFIEC UBPR",
    "Uniform Bank Performance Report Ratios 2002-2026",
    "UBPR per-institution ratio data: 1.25 billion (institution, quarter, "
    "ratio) observations.",
    "FFIEC CDR public bulk - UBPR Ratio, Single Period (tab-delimited ZIPs)",
    "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx", PD,
    "public-browser", "2026-03-31",
    "Per-quarter tab-delimited ZIPs acquired from the CDR bulk download flow "
    "and ingested long.",
    ["07g_acquire_ubpr.py", "39_ingest_ubpr.py"],
    ["zip_extract", "wide_to_long"],
    "ratios (percent, dimensionless - see UBPR definitions)",
    "quarterly", {"start": "2002Q4", "end": "2026Q1"}, "verified", "")

entry(
    "UBPR_PEER_STATS", "ubpr_peer_stats.parquet", "FFIEC UBPR",
    "UBPR Peer Group Statistics 2002-2026",
    "Peer-group percentile statistics for UBPR ratios (22.1M rows).",
    "FFIEC CDR public bulk - UBPR Peer Stats (Four Periods, XBRL ZIPs)",
    "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx", PD,
    "public-browser", "2026-03-31",
    "Year-bucketed XBRL ZIPs acquired via the CDR bulk flow and parsed.",
    ["07i_acquire_ubpr_peer.py", "42_ingest_ubpr_peer.py"],
    ["xbrl_parse", "percentile_stats"],
    "ratios (percentiles)",
    "quarterly", {"start": "2002Q4", "end": "2026Q1"}, "verified", "")

entry(
    "UBPR_PEER_RANK", "ubpr_peer_rank.parquet", "FFIEC UBPR",
    "UBPR Peer Ranks 2002-2026",
    "Per-bank percentile ranks within UBPR peer groups (250M rows).",
    "FFIEC CDR public bulk - UBPR Rank (Four Periods, XBRL ZIPs)",
    "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx", PD,
    "public-browser", "2026-03-31",
    "Year-bucketed XBRL ZIPs acquired via the CDR bulk flow and parsed.",
    ["07i_acquire_ubpr_peer.py", "42_ingest_ubpr_peer.py"],
    ["xbrl_parse", "rank_computation"],
    "percentile ranks",
    "quarterly", {"start": "2002Q4", "end": "2026Q1"}, "verified", "")

entry(
    "CDR_UNREALIZED", "cdr_unrealized_losses.parquet", "FFIEC UBPR",
    "AFS/HTM Unrealized Losses 2019-2026",
    "Available-for-sale / held-to-maturity fair values, unrealized gains and "
    "losses, AOCI, and brokered deposits from Call Report schedules RC-B, RC, "
    "RC-E (46.9K institution-quarter rows). Built for the 2023 failure-wave "
    "securities-exposure analysis.",
    "FFIEC CDR public bulk - Call Report schedules",
    "https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx", PD,
    "public-browser", "2026-03-31",
    "CDR bulk ZIPs acquired via the public bulk download flow; schedule "
    "line-items parsed to a focused layer.",
    ["32_acquire_cdr_unrealized.py", "33_parse_cdr_unrealized.py"],
    ["zip_extract", "schedule_parse"],
    "USD fair values and unrealized gains/losses",
    "quarterly", {"start": "2019Q4", "end": "2025Q4"}, "verified", "")

# ----------------------------------------------------------------- BHCF / Y-9C
entry(
    "BHCF_FILINGS", "bhcf_filings.parquet", "Federal Reserve Y-9C",
    "Bank Holding Company Financials (FR Y-9C / BHCF) 1986-2026",
    "FR Y-9C consolidated financial statements for bank holding companies: "
    "208M (BHC, quarter, item) observations, 1986-2025 from caret-delimited "
    "TXT (2000+) and pre-2000 CSV vintages.",
    "FFIEC NIC / CDR - FR Y-9C bulk data (BHCF)",
    "https://www.ffiec.gov/npw/FinancialReport/ReturnY9C", PD,
    "public-browser", "2026-01-26",
    "104 caret-delimited TXT files (2000-2025) + pre-2000 CSV vintage, "
    "unpivoted wide-to-long.",
    ["04_ingest_bhcf_txt.py", "05_ingest_bhcf_csv.py"],
    ["delimited_read", "wide_to_long"],
    "USD thousands for $ items; counts (see FR Y-9C item definitions)",
    "quarterly", {"start": "1986Q3", "end": "2025Q4"}, "verified",
    "Trailing product in the quarterly refresh (lags Call Reports ~1 quarter).")

# ------------------------------------------------------------------ FFIEC NIC
entry(
    "INSTITUTIONS", "institutions.parquet", "FFIEC NIC",
    "List of Insured Depository Institutions (NIC universe)",
    "Every regulated depository institution (active + closed) from the FFIEC "
    "National Information Center: 217K entities with regulator, charter, "
    "dates, and status.",
    "FFIEC National Information Center - institution attributes download",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "NIC attribute CSVs (active + closed) loaded via DuckDB native reader.",
    ["02_ingest_attributes.py"],
    ["csv_load", "active_closed_union"],
    "entity records (identifiers, dates, status codes)",
    "snapshot", {"start": "1782", "end": "2026"}, "verified",
    "Coverage start reflects the earliest charter dates of closed entities "
    "carried in the history; the NIC attribute set itself is a current "
    "snapshot plus closed-institution history.")

entry(
    "INSTITUTION_ATTRIBUTES", "institution_attributes.parquet", "FFIEC NIC",
    "Institution Attributes",
    "NIC attribute records per institution (charter class, regulator codes, "
    "dates, identifiers) - the core entity dimension (217K rows).",
    "FFIEC National Information Center - CSV_ATTRIBUTES_ACTIVE / CLOSED",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Native CSV load of the NIC attribute files.",
    ["02_ingest_attributes.py"],
    ["csv_load"],
    "attribute records",
    "snapshot", {"start": "1782", "end": "2026"}, "verified", "")

entry(
    "BRANCHES", "branches.parquet", "FFIEC NIC",
    "Branch Locations",
    "Branch records from NIC attribute tables: 173K branch locations.",
    "FFIEC National Information Center - CSV_ATTRIBUTES_BRANCHES",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Native CSV load.",
    ["02_ingest_attributes.py"],
    ["csv_load"],
    "branch records (locations)",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "RELATIONSHIPS", "relationships.parquet", "FFIEC NIC",
    "Entity Relationships",
    "NIC entity-to-entity relationships (parent/child, affiliations): 286K rows.",
    "FFIEC National Information Center - CSV_RELATIONSHIPS",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Native CSV load.",
    ["02_ingest_attributes.py"],
    ["csv_load"],
    "relationship records",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "TRANSFORMATIONS", "transformations.parquet", "FFIEC NIC",
    "Entity Transformations",
    "NIC-recorded entity transformation events (mergers, conversions, "
    "absorptions): 58.9K rows.",
    "FFIEC National Information Center - CSV_TRANSFORMATIONS",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Native CSV load.",
    ["02_ingest_attributes.py"],
    ["csv_load"],
    "transformation event records",
    "event", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "NIC_ENTITY_IDS", "nic_entity_identifiers.parquet", "FFIEC NIC",
    "NIC Authoritative Identifier Crosswalk",
    "The authoritative Fed multi-regulator identifier crosswalk per RSSD: "
    "LEI, CUSIP, thrift IDs, ABA, FDIC cert, NCUA, OCC, tax ID (103K rows).",
    "FFIEC NIC attribute CSVs (74-column vintage)",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Harvested from the full 74-column NIC attribute set into a canonical "
    "identifier table.",
    ["37_ingest_nic_identifiers.py"],
    ["column_harvest"],
    "identifiers",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "NIC_ATTRS_EXT", "nic_attributes_ext.parquet", "FFIEC NIC",
    "NIC Attribute Extension (Geography, Charter Codes)",
    "Fed-direct geography (street/zip/county/url), charter/regulator codes, "
    "status and type per RSSD (220K rows) - the remainder of the 74-column "
    "NIC attribute set beyond the core 13 columns.",
    "FFIEC NIC attribute CSVs (74-column vintage)",
    "https://www.ffiec.gov/npw/FinancialReport/DataDownload", PD, "public",
    "2026-05-29",
    "Additive harvest of the remaining NIC attribute columns.",
    ["37b_ingest_nic_attributes_ext.py"],
    ["column_harvest"],
    "attribute records",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "Y15_INDICATORS", "y15_systemic_indicators.parquet", "Federal Reserve Y-15",
    "FR Y-15 Systemic Indicators 2020-2024",
    "FR Y-15 G-SIB systemic-risk indicator snapshots: 22.5K rows.",
    "FFIEC NIC - FR Y-15 Snapshots",
    "https://www.ffiec.gov/npw/FinancialReport/FRY15Reports", PD,
    "public-browser", "2025-12-31",
    "Per-year snapshot CSVs acquired from the FR Y-15 reports page (the "
    "listing is JS-gated; the static CSV assets download directly) and loaded.",
    ["07h_acquire_y15.py", "41_ingest_y15.py"],
    ["csv_load"],
    "USD billions and indicator scores (see FR Y-15 instructions)",
    "quarterly", {"start": "2020Q4", "end": "2024Q4"}, "verified",
    "FR Y-9LP has no bulk product and is intentionally not included.")

entry(
    "BHC_OWNERSHIP", "bhc_ownership.parquet", "Failing Banks catalogs",
    "BHC Hierarchy / Ownership",
    "Bank holding company parent-child hierarchy with ownership percentages: "
    "36.7K relationships.",
    "Failing Banks database catalogs (derived from NIC)",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "Catalog CSV ingested and normalized.",
    ["29_ingest_volcker_catalogs.py"],
    ["csv_load"],
    "ownership percentages",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

# ------------------------------------------------------------------------ MDRM
entry(
    "MDRM", "mdrm.parquet", "Federal Reserve MDRM",
    "MDRM Variable Dictionary",
    "The Fed Micro Data Reference Manual: 87K reporting-item definitions "
    "(codes, titles, descriptions) that key every Call Report variable.",
    "Federal Reserve MDRM (via FFIEC bulk distribution)",
    "https://www.federalreserve.gov/apps/mdrm/", PD, "public", "2026-01-26",
    "MDRM_CSV.csv parsed (HTML entities cleaned, PUBLIC header handled).",
    ["01_ingest_mdrm.py"],
    ["csv_clean"],
    "definitions (text)",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

# ------------------------------------------------------------------------ FRED
entry(
    "FRED_SERIES", "fred_series.parquet", "FRED Banking & Macro Series",
    "FRED Banking Series (H.8 + macro context) 1954-2026",
    "Federal Reserve H.8 aggregate banking series (bank credit, loans, "
    "securities, deposits), key rates, and macro context (GDP, unemployment, "
    "CPI, industrial production): 1.35M observations. The 15 aggregate "
    "series are keyless; the full disaggregated H.8 release (~1,938 series "
    "by bank size/type) requires a free FRED API key.",
    "FRED (St. Louis Fed) - fredgraph.csv (keyless) + FRED API release 22 "
    "(full H.8)",
    "https://fred.stlouisfed.org/", PD, "public-key", "2026-05-31",
    "Keyless CSV download per series for the 15 aggregates; API-paged JSON "
    "for the full H.8 release; both appended to one long table.",
    ["27_ingest_fed_h8.py", "27b_ingest_fed_h8_disagg.py"],
    ["csv_download", "api_pagination", "append_long"],
    "varies by series (USD billions, percent, index) - series_id keys to FRED",
    "mixed (weekly/monthly/quarterly by series)",
    {"start": "1954", "end": "2026"}, "verified",
    "Full H.8 layer needs FRED_API_KEY (free). Frequency varies by series; "
    "per-series metadata lives in the table itself.")

# ------------------------------------------------------------ OCC / Luck / finhist
entry(
    "OCC_HISTORICAL", "occ_historical.parquet", "OCC Annual Reports",
    "OCC Historical Condition Statements 1863-1941",
    "Digitized OCC Annual Report national-bank condition statements: 17.8M "
    "(bank, report date, item) observations across the national banking era.",
    "OCC Annual Reports, digitized (Luck historical database distribution)",
    "https://www.occ.gov/about/what-we-do/hist-publications/hist-publications-index.html",
    PD, "bundled", "2026-03-11",
    "Wide TSV (111K rows x 116 cols) loaded with DuckDB native reader and "
    "unpivoted long; variable labels mapped from the accompanying YAML "
    "documentation; year mapped to actual report dates.",
    ["09_ingest_occ.py"],
    ["tsv_load", "wide_to_long", "label_map", "date_map"],
    "USD (era units as digitized - see variable_labels)",
    "quarterly to annual (report dates)", {"start": "1863", "end": "1941"},
    "verified",
    "Distributed inside the Luck historical database files; the same OCC "
    "source is also published standalone in the finhist public vintage.")

entry(
    "OCC_HIST_CLV", "occ_historical_clv.parquet", "finhist / CLV",
    "finhist Historical Call Reports 1863-1941 (CLV vintage)",
    "The Correia-Luck-Verner public historical-call file: 371K bank-report "
    "rows, wide, full 1863-1941 span - penny-exact verified against the "
    "Luck TSV vintage of the same OCC source.",
    "finhist.com / Harvard Dataverse historical-call (Correia-Luck-Verner)",
    "https://doi.org/10.7910/DVN/Q22XR1", "CC BY 4.0", "public",
    "2026-03-11",
    "Stata DTA loaded wide, kept as the CLV-published schema.",
    ["09b_ingest_occ_finhist.py"],
    ["dta_load"],
    "USD (as published by the authors)",
    "quarterly to annual", {"start": "1863", "end": "1941"}, "verified", "")

entry(
    "LUCK_CALL", "luck_call_reports.parquet", "Luck historical database",
    "Luck Historical Call Reports 1959-1975 (core)",
    "The pre-1976 call-report core from the Luck historical database: 37.8M "
    "rows after dedup to the 1959Q4-1975Q4 core plus Fed-absent gap-fill "
    "(from 311.8M raw source rows).",
    "Luck historical call reports (Correia-Luck-Verner public dataset, "
    "FRBNY distribution)",
    "https://www.newyorkfed.org/research/banking_research/datasets.html",
    "CC BY 4.0 (author replication license)", "bundled", "2026-03-11",
    "Stata DTA (balance sheets + income statements) loaded, quarter-start "
    "dates converted to quarter-end, then deduplicated to the core span.",
    ["08_ingest_luck.py", "08b_slim_luck.py"],
    ["dta_load", "quarter_end_conversion", "dedup_core"],
    "USD (as published)",
    "quarterly", {"start": "1959Q4", "end": "1975Q4"}, "verified",
    "Sourced span extends to 2023Q1; the served table is the slimmed core. "
    "The raw DTA files are the authors' public replication files.")

# -------------------------------------------------------- Failing Banks (Robin)
entry(
    "FB_PANEL", "robin_panel_base.parquet", "Failing Banks panel",
    "Failing Banks Annual Panel 1863-2024",
    "Annual panel of ALL US banks (failed + surviving) from the Correia-"
    "Luck-Verner Failing Banks database repackaging: 2.87M bank-year "
    "observations, 156 variables - financial data, failure indicators, macro "
    "context, computed ratios. Partially fills the 1905-1958 coverage gap.",
    "Failing Banks database (Correia-Luck-Verner panel, andenick/failing-banks)",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "Processed panel CSVs loaded verbatim (no recomputation).",
    ["28_ingest_robin_panel.py"],
    ["csv_load"],
    "USD and ratios as published (see the source repo codebook)",
    "annual", {"start": "1863", "end": "2024"}, "verified",
    "Panel v3.3 export; regenerators can rebuild the CSVs with the "
    "conversion scripts in the public source repo.")

entry(
    "FB_DEPOSITS_HIST", "robin_deposits_historical.parquet",
    "Failing Banks panel",
    "Deposits Before Failure - Historical Era 1864-1935",
    "Pre-FDIC-era deposit dynamics for failing banks: 2,961 rows.",
    "Failing Banks database",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "CSV loaded verbatim.",
    ["28_ingest_robin_panel.py"], ["csv_load"],
    "USD deposits",
    "event", {"start": "1864", "end": "1935"}, "verified", "")

entry(
    "FB_DEPOSITS_MODERN", "robin_deposits_modern.parquet",
    "Failing Banks panel",
    "Deposits Before Failure - Modern Era 1993-2023",
    "Modern-era deposit run-up dynamics with run indicators: 547 rows.",
    "Failing Banks database",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "CSV loaded verbatim.",
    ["28_ingest_robin_panel.py"], ["csv_load"],
    "USD deposits",
    "event", {"start": "1993", "end": "2023"}, "verified", "")

entry(
    "FB_CROSSWALK", "robin_crosswalk.parquet", "Failing Banks catalogs",
    "Bank Identifier Crosswalk (Failing Banks bank_id <-> RSSD <-> FDIC cert)",
    "14,287 bank_id-to-RSSD-to-FDIC-cert mappings linking the Failing Banks "
    "panel identifiers to the regulatory universes.",
    "Failing Banks database catalogs",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "Catalog CSV ingested.",
    ["29_ingest_volcker_catalogs.py"], ["csv_load"],
    "identifiers",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "SECTOR_GROUPINGS", "sector_groupings.parquet", "Failing Banks catalogs",
    "Sector Groupings (CIK -> SIC -> sector)",
    "16,548 CIK-to-SIC-to-sector classifications used for industry grouping.",
    "Failing Banks database catalogs (SEC SIC basis)",
    "https://github.com/andenick/failing-banks", "MIT", "public",
    "2026-05-19",
    "Catalog CSV ingested.",
    ["29_ingest_volcker_catalogs.py"], ["csv_load"],
    "classifications",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

# ------------------------------------------------------------------------ NCUA
entry(
    "NCUA_5300", "ncua_5300.parquet", "NCUA",
    "NCUA 5300 Credit Union Call Reports 1994-2025",
    "Credit-union call reports (Form 5300): 1.18 billion (CU, quarter, item) "
    "observations. A distinct institution universe keyed by NCUA CU_NUMBER - "
    "additive to the bank core, never unioned on bank identifiers.",
    "NCUA credit union call report data (quarterly bulk ZIPs)",
    "https://www.ncua.gov/analysis/credit-union-corporate-call-report-data",
    PD, "public", "2026-04-30",
    "Quarterly bulk ZIPs parsed to long format.",
    ["26_ingest_ncua.py"],
    ["zip_extract", "wide_to_long"],
    "USD and counts per 5300 acct code",
    "quarterly", {"start": "1994Q1", "end": "2025Q4"}, "verified",
    "SCOPE EXPANSION beyond FDIC-insured depositories/BHCs: credit unions.")

entry(
    "NCUA_DIRECTORY", "ncua_cu_directory.parquet", "NCUA",
    "NCUA Credit Union Directory",
    "Credit-union directory records (names, charters, fields of membership): "
    "851K rows.",
    "NCUA credit union call report data",
    "https://www.ncua.gov/analysis/credit-union-corporate-call-report-data",
    PD, "public", "2026-04-30",
    "Directory layer parsed from the 5300 bulk distribution.",
    ["26_ingest_ncua.py"], ["csv_load"],
    "entity records",
    "snapshot", {"start": "1994", "end": "2025"}, "verified", "")

# ------------------------------------------------------------- Supervisory
entry(
    "DFAST_RESULTS", "dfast_results.parquet", "Federal Reserve stress tests",
    "DFAST Stress Test Results 2013-2025",
    "Comprehensive capital-analysis results for the 22-43 largest BHCs per "
    "exercise: capital ratios, loan losses, revenue and income projections "
    "under stress (28K observations across 14 annual exercises).",
    "Federal Reserve DFAST published results",
    "https://www.federalreserve.gov/supervisionreg/dfast-archive.htm", PD,
    "public", "2025-06-30",
    "Published results CSVs loaded.",
    ["23_ingest_dfast.py"], ["csv_load"],
    "capital ratios (percent), losses/revenue (USD)",
    "annual", {"start": "2013", "end": "2025"}, "verified", "")

entry(
    "STRESS_SCENARIOS", "stress_scenarios.parquet", "Federal Reserve stress tests",
    "Supervisory Stress Scenarios",
    "DFAST/CCAR supervisory scenario definitions (historical actuals, "
    "baseline, severely adverse): 200 rows of macro paths.",
    "Federal Reserve supervisory scenarios",
    "https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm", PD,
    "public", "2025-02-28",
    "Six published scenario CSVs harmonized into one table.",
    ["30_ingest_stress_scenarios.py"], ["csv_load", "harmonize"],
    "macro variables (percent, index, USD as defined per scenario)",
    "quarterly projection paths", {"start": "2024", "end": "2026"}, "verified", "")

entry(
    "STRESS_SCENARIOS_DOM", "stress_scenarios_domestic.parquet",
    "Federal Reserve stress tests",
    "Stress Scenarios - Domestic",
    "Domestic scenario block (226 rows).",
    "Federal Reserve supervisory scenarios",
    "https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm", PD,
    "public", "2025-02-28",
    "Published CSVs loaded.",
    ["30_ingest_stress_scenarios.py"], ["csv_load"],
    "macro variables", "quarterly", {"start": "2024", "end": "2026"},
    "verified", "")

entry(
    "STRESS_SCENARIOS_INTL", "stress_scenarios_international.parquet",
    "Federal Reserve stress tests",
    "Stress Scenarios - International",
    "International scenario block (226 rows).",
    "Federal Reserve supervisory scenarios",
    "https://www.federalreserve.gov/supervisionreg/dfa-stress-tests.htm", PD,
    "public", "2025-02-28",
    "Published CSVs loaded.",
    ["30_ingest_stress_scenarios.py"], ["csv_load"],
    "macro variables", "quarterly", {"start": "2024", "end": "2026"},
    "verified", "")

entry(
    "PILLAR3", "pillar3_disclosures.parquet", "G-SIB Pillar 3 disclosures",
    "Pillar 3 Disclosures (5 G-SIBs) 2024-2025",
    "Quarterly Basel III Pillar 3 disclosures (capital, RWA, ratios, SLR, "
    "TLAC) transcribed from the investor-relations pages of JPM, BAC, WFC, "
    "C, MS: 8.7K rows.",
    "G-SIB Pillar 3 disclosure documents (bank investor-relations pages)",
    "https://www.bis.org/bcbs/pillar3.htm", 
    "bank-published disclosures (public documents; see DPR D12)", "manual",
    "2025-11-30",
    "Tables transcribed from the published disclosure PDFs/pages into CSV, "
    "then parsed - a hand-collected layer, not a bulk download.",
    ["24_ingest_pillar3.py"], ["manual_transcription", "csv_parse"],
    "USD and regulatory ratios",
    "quarterly", {"start": "2024Q1", "end": "2025Q3"}, "verified",
    "Hand-collected from 5 banks' public disclosures; no single bulk source "
    "exists. See D12 for the honest reproduction path.")

# ------------------------------------------------------ Market crosswalks
entry(
    "CRSP_MAPPING", "crsp_mapping.parquet", "Market crosswalks",
    "CRSP-FRB PERMCO Mapping 1971-2024",
    "PERMCO-to-RSSD linking table from the NY Fed's CRSP-FRB link: 18.9K "
    "entries enabling market-data joins to the regulatory universe.",
    "NY Fed CRSP-FRB link table",
    "https://www.newyorkfed.org/research/banking_research/datasets.html",
    PD, "public", "2026-03-11",
    "16 mapping CSVs loaded, notice/copyright rows dropped.",
    ["03_ingest_crsp.py"], ["csv_load", "row_filter"],
    "identifiers",
    "snapshot", {"start": "1971", "end": "2024"}, "verified",
    "Ships the public LINK TABLE only - CRSP market data itself is "
    "proprietary and is NOT in FreeNIC.")

entry(
    "SEC_CIK", "sec_cik_crosswalk.parquet", "Market crosswalks",
    "SEC EDGAR CIK Crosswalk",
    "SEC CIK identity for bank/BHC filers (ticker, SIC, size hint): 371 rows "
    "- an identity crosswalk, not a financials table.",
    "SEC EDGAR structured data (submissions + XBRL frames, data.sec.gov)",
    "https://data.sec.gov/", PD, "public", "2026-06-30",
    "SIC-filtered submissions + XBRL frames API queried for bank/BHC "
    "filers; assembled into a crosswalk.",
    ["34_ingest_sec_edgar.py"], ["api_query", "sic_filter"],
    "identifiers; Assets as coarse size hint (USD)",
    "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "HMDA_SUMMARY", "hmda_summary.parquet", "Market crosswalks",
    "HMDA Mortgage-Lending Summary 2022-2023",
    "CFPB HMDA institution-by-year mortgage summary keyed by LEI at "
    "(lei, activity_year, loan_purpose): loan counts and amounts. A SUMMARY "
    "aggregated from the Data Browser API - not the full LAR.",
    "CFPB HMDA Data Browser API",
    "https://ffiec.cfpb.gov/data-browser/", PD, "public", "2026-06-30",
    "Filers list + per-LEI loan-purpose aggregations pulled from the Data "
    "Browser API and transcribed verbatim.",
    ["35_ingest_hmda.py"], ["api_aggregation"],
    "loan counts; loan amount in USD thousands",
    "annual", {"start": "2022", "end": "2023"}, "verified",
    "Adjacent dataset (mortgage lending), not the call-report core.")

# ------------------------------------------------------- Variable dictionary
_DICT_SRC = (
    "bank-data-dictionary (harmonized variable taxonomy, pinned release)",
    "https://github.com/andenick/bank-data-dictionary", "MIT", "public")
for _sid, _file, _title, _desc, _rows_note in [
    ("DICT_META", "dict_meta.parquet", "Dictionary Meta",
     "Release metadata for the pinned bank-data-dictionary build (3 rows).", ""),
    ("DICT_CROSSWALK", "dict_crosswalk.parquet", "Dictionary Crosswalk",
     "Cross-dictionary variable mappings (2,057 rows).", ""),
    ("DICT_EDIT_HISTORY", "dict_edit_history.parquet", "Dictionary Edit History",
     "Taxonomy edit log (15.6K rows).", ""),
    ("DICT_RELATIONSHIPS", "dict_relationships.parquet", "Dictionary Relationships",
     "Variable-to-variable relationships (7,539 rows).", ""),
    ("DICT_SCHEDULE_LINEITEMS", "dict_schedule_lineitems.parquet",
     "Schedule Line-Items",
     "Call Report schedule line-item definitions (3,198 rows).", ""),
    ("DICT_UBPR_CONCEPTS", "dict_ubpr_concepts.parquet", "UBPR Concepts",
     "UBPR concept definitions (4,099 rows).", ""),
    ("DICT_ACCESS_MAP", "dict_variable_access_map.parquet",
     "Variable Access Map",
     "Which warehouse view exposes each variable (14.4K rows).", "")]:
    entry(_sid, _file, "Variable dictionary", _title, _desc,
          _DICT_SRC[0], _DICT_SRC[1], _DICT_SRC[2], _DICT_SRC[3], "2026-07-01",
          "Pinned dictionary release imported and re-pinned each quarterly "
          "refresh.",
          ["14_import_dictionary.py"], ["import"],
          "definitions (text)", "snapshot",
          {"start": "2026", "end": "2026"}, "verified", "")

# ------------------------------------------------------- Warehouse catalogs
_CAT_SRC = ("FreeNIC warehouse catalog (self-describing build artifacts)",
            "https://github.com/andenick/FreeNIC", "MIT", "internal-derived")
for _sid, _file, _title, _desc, _cov in [
    ("CATALOG_DATA_SOURCES", "catalog_data_sources.parquet", "Data Source Catalog",
     "One row per registered source family with provenance (779 rows).",
     {"start": "2026", "end": "2026"}),
    ("CATALOG_ENTITY_COVERAGE", "catalog_entity_coverage.parquet",
     "Entity Coverage Catalog",
     "Per-source entity coverage (141K rows).", {"start": "1782", "end": "2026"}),
    ("CATALOG_FILING_COVERAGE", "catalog_filing_coverage.parquet",
     "Filing Coverage Catalog",
     "Per-source period coverage (53.6K rows).", {"start": "1782", "end": "2026"}),
    ("CATALOG_NAMESPACE_VARIABLES", "catalog_namespace_variables.parquet",
     "Namespace Variable Catalog",
     "Variables per reporting namespace (6,754 rows).",
     {"start": "2026", "end": "2026"}),
    ("CATALOG_SCHEMA_EVOLUTION", "catalog_schema_evolution.parquet",
     "Schema Evolution Catalog",
     "How reporting schemas changed over time (13.4K rows).",
     {"start": "1976", "end": "2026"}),
    ("CATALOG_VARIABLES", "catalog_variables.parquet", "Variable Catalog",
     "Every warehouse variable with namespace and lineage (13.4K rows).",
     {"start": "2026", "end": "2026"}),
    ("FREENIC_MANIFEST", "freenic_manifest.parquet", "Warehouse Self-Manifest",
     "The warehouse's own table manifest (110 rows).",
     {"start": "2026", "end": "2026"}),
    ("FILING_METADATA", "filing_metadata.parquet", "Filing Metadata",
     "Ingestion-log metadata per filing batch (359 rows).",
     {"start": "1976", "end": "2026"}),
    ("REPORTING_FORMS", "reporting_forms.parquet", "Reporting Forms",
     "Reporting-form definitions (180 rows).",
     {"start": "2026", "end": "2026"})]:
    entry(_sid, _file, "Warehouse catalogs", _title, _desc,
          _CAT_SRC[0], _CAT_SRC[1], _CAT_SRC[2], _CAT_SRC[3], RELEASE_DATE,
          "Built by the catalog/coverage/self-describing phases over the "
          "completed warehouse.",
          ["10_build_catalog.py", "49_coverage_matrix.py", "47_self_describing.py"],
          ["catalog_build"],
          "metadata records", "snapshot", _cov, "verified", "")

# ----------------------------------------------------------- Derived panels
_DER_SRC = ("FreeNIC derived (from public regulatory sources)",
            "https://github.com/andenick/FreeNIC", "MIT", "internal-derived")
entry(
    "CLEAN_BANK_PANEL", "clean_bank_panel.parquet", "Derived panels",
    "Clean Bank Panel 1863-2026",
    "The canonical clean annual bank panel: 1.11M bank-year rows across "
    "three strata (OCC era 1863-1941, Luck era 1959-1975, Call Report era "
    "1976-2026) with nominal and real (1990=100) USD levels - the fix for "
    "uncalibrated absolute-$ panels.",
    _DER_SRC[0], _DER_SRC[1], _DER_SRC[2], _DER_SRC[3], RELEASE_DATE,
    "From-raw rebuild over occ_historical_clv + Luck + scheduled call "
    "items; deterministic and byte-stable; unit-gate verified against "
    "published anchors (JPM-2008, SVB-2023, OCC-1929).",
    ["45_build_clean_bank_panel.py"],
    ["real_deflation_1990_100", "strata_union", "unit_gate"],
    "USD nominal and real levels (1990=100)",
    "annual", {"start": "1863", "end": "2026"}, "verified",
    "finhist historical-call v2.10.0 basis.")

entry(
    "LONG_AGGREGATES", "long_bank_aggregates_1863_2026.parquet", "Derived panels",
    "Bank Aggregate Spine 1863-2026 (163 years)",
    "The replicated 163-year year-by-metric spine (810 rows): num_banks, "
    "total_assets, total_deposits, total_loans, with definition toggles, "
    "source-series provenance, and junction flags at the 1896/1914/1934 "
    "regime joins.",
    _DER_SRC[0], _DER_SRC[1], _DER_SRC[2], _DER_SRC[3], RELEASE_DATE,
    "Aggregate build over OCC condition statements, FDIC HSOB, and modern "
    "Call Report aggregates, staged by the release slice tooling.",
    ["release-tools/build_slice.py"],
    ["aggregation", "regime_join_annotation"],
    "count of banks; USD (assets/deposits/loans)",
    "annual", {"start": "1863", "end": "2026"}, "verified", "")

entry(
    "ENTITY_XREF", "entity_xref.parquet", "Derived panels",
    "Entity Cross-Reference",
    "Cross-source entity resolution across NIC/FDIC/NCUA/SEC identifiers "
    "(234K rows).",
    _DER_SRC[0], _DER_SRC[1], _DER_SRC[2], _DER_SRC[3], RELEASE_DATE,
    "Entity-resolution build over the identifier tables.",
    ["20b_build_entity_xref.py"], ["entity_resolution"],
    "identifiers", "snapshot", {"start": "1782", "end": "2026"}, "verified", "")

entry(
    "ID_CROSSWALK", "id_crosswalk.parquet", "Derived panels",
    "Identifier Crosswalk (RSSD <-> LEI <-> FDIC cert <-> ...)",
    "The unified identifier crosswalk (103K rows), with LEIs gap-filled "
    "from the GLEIF golden copy by normalized-name match.",
    "FreeNIC derived + GLEIF Level-1 golden copy",
    "https://www.gleif.org/en/lei-data/gleif-golden-copy",
    "MIT + GLEIF data (CC BY 4.0)", "internal-derived", RELEASE_DATE,
    "Identifier tables merged, then LEI filled from GLEIF US/ACTIVE by "
    "unambiguous normalized-name match (source-tagged, never overwriting).",
    ["36_build_id_crosswalk.py", "36b_gleif_lei.py"],
    ["merge", "name_match_fill"],
    "identifiers", "snapshot", {"start": "2026", "end": "2026"}, "verified", "")

entry(
    "VARIABLE_CROSSWALK", "variable_crosswalk.parquet", "Warehouse catalogs",
    "Variable Crosswalk",
    "Cross-vintage variable mappings (Chicago Fed vs CDR vs MDRM vs "
    "dictionary): 76 rows.",
    _CAT_SRC[0], _CAT_SRC[1], _CAT_SRC[2], _CAT_SRC[3], RELEASE_DATE,
    "Curated cross-vintage variable mapping build.",
    ["20_build_crosswalks.py"], ["crosswalk_build"],
    "variable-code mappings", "snapshot",
    {"start": "1976", "end": "2026"}, "verified", "")

# ------------------------------------------------------------ Reconstruction
entry(
    "RECON_LUCK_CORE", "luck_core_1959_1975.parquet", "Reconstruction layer",
    "Reconstructed Luck Core 1959-1975",
    "The Luck-era core rebuilt from raw public sources with the verified "
    "reconstruction engine (601K rows); validated cell-by-cell against the "
    "published Luck numbers (gate: PASS).",
    "FreeNIC reconstruction from FFIEC/FDIC public raw sources",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Rebuild via the pipeline/reconstruction module (entity spine + "
    "variable map + gmatch), then cell-level reconciliation.",
    ["50_reconstruct_luck.py", "pipeline/reconstruction/build_luck_core.py"],
    ["entity_spine", "variable_map", "gmatch", "cell_reconciliation"],
    "USD (as reconstructed; reconciliation deltas in partner table)",
    "quarterly", {"start": "1959Q4", "end": "1975Q4"}, "verified",
    "Served under reconstruction/. Gate JSON + report alongside.")

entry(
    "RECON_LUCK_EQUIV", "luck_equivalent_1976_2026.parquet",
    "Reconstruction layer",
    "Reconstructed Luck-Equivalent Panel 1976-2026",
    "The modern-era Luck-equivalent panel rebuilt from CDR Call Reports "
    "(2.03M rows); pre-registered verdict: FAIL against the published Luck "
    "reference at the strictest tier (documented divergence - the honest "
    "record of what the public sources can and cannot reproduce).",
    "FreeNIC reconstruction from FFIEC CDR public raw sources",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Rebuild + cell-by-cell reconciliation against published Luck values.",
    ["50_reconstruct_luck.py", "pipeline/reconstruction/build_luck_equivalent.py"],
    ["entity_spine", "variable_map", "gmatch", "cell_reconciliation"],
    "USD (as reconstructed)",
    "quarterly", {"start": "1976Q1", "end": "2026Q1"}, "known_issues",
    "Pre-registered reconstruction FAIL is documented, not hidden - see "
    "pipeline/reconstruction/reports/ and D15.")

entry(
    "RECON_FINHIST", "finhist_equivalent_1863_1941.parquet",
    "Reconstruction layer",
    "Reconstructed finhist Panel 1863-1941",
    "The OCC-era finhist-equivalent rebuilt from digitized OCC condition "
    "statements (367K rows); gate: PASS.",
    "FreeNIC reconstruction from OCC Annual Report digitizations",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Rebuild + cell-by-cell reconciliation against finhist published values.",
    ["51_reconstruct_finhist.py",
     "pipeline/reconstruction/build_finhist_equivalent.py"],
    ["entity_spine", "variable_map", "reconciliation"],
    "USD (as reconstructed)",
    "annual", {"start": "1863", "end": "1941"}, "verified", "")

entry(
    "RECON_REC_MODERN", "reconciliation_1976_2026.parquet",
    "Reconstruction layer",
    "Cell-Level Reconciliation - Modern Era 1976-2026",
    "Every reconstructed-vs-published comparison cell for the modern era: "
    "40.3M rows of deltas with reasons.",
    "FreeNIC reconstruction validation artifacts",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Emitted by the reconstruction validation engine.",
    ["50_reconstruct_luck.py", "pipeline/reconstruction/validate_reconstruction.py"],
    ["cell_reconciliation"],
    "value deltas and match flags",
    "quarterly", {"start": "1976Q1", "end": "2026Q1"}, "verified", "")

entry(
    "RECON_REC_LUCK", "reconciliation_1959_1975.parquet",
    "Reconstruction layer",
    "Cell-Level Reconciliation - Luck Era 1959-1975",
    "Reconstructed-vs-published comparison cells for the Luck era: 7.5M rows.",
    "FreeNIC reconstruction validation artifacts",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Emitted by the reconstruction validation engine.",
    ["50_reconstruct_luck.py", "pipeline/reconstruction/validate_reconstruction.py"],
    ["cell_reconciliation"],
    "value deltas and match flags",
    "quarterly", {"start": "1959Q4", "end": "1975Q4"}, "verified", "")

entry(
    "RECON_REC_FINHIST", "reconciliation_finhist.parquet",
    "Reconstruction layer",
    "Cell-Level Reconciliation - finhist Era 1863-1941",
    "Reconstructed-vs-published comparison cells for the OCC era: 2.6M rows.",
    "FreeNIC reconstruction validation artifacts",
    "https://github.com/andenick/FreeNIC/tree/master/pipeline/reconstruction",
    "MIT", "internal-derived", RELEASE_DATE,
    "Emitted by the reconstruction validation engine.",
    ["51_reconstruct_finhist.py", "pipeline/reconstruction/validate_reconstruction.py"],
    ["cell_reconciliation"],
    "value deltas and match flags",
    "annual", {"start": "1863", "end": "1941"}, "verified", "")


def load_manifest(remote: bool) -> dict[str, dict]:
    """Return {filename: {rows, tier, provenance, span}} merged from manifests."""
    merged: dict[str, dict] = {}
    src = "local"
    data = None
    if remote:
        try:
            req = urllib.request.Request(
                REMOTE_MANIFEST, headers={"User-Agent": "freenic-anu/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            src = "remote"
        except Exception as exc:  # noqa: BLE001 - fall back with a warning
            print(f"[make_registry] remote manifest unreachable ({exc}); "
                  "falling back to the committed v1.0.0 manifest")
    if data is None and LOCAL_MANIFEST.exists():
        with open(LOCAL_MANIFEST, encoding="utf-8") as fh:
            data = json.load(fh)
    if data:
        for f in data.get("files", []):
            merged[f["name"]] = dict(
                rows=f.get("rows"), tier=f.get("tier"),
                provenance=f.get("provenance_provider"),
                span=f.get("period_span", ""))
    if src == "local":
        for name, rows in RECONSTRUCTION_ROWS.items():
            merged[name] = dict(rows=rows, tier="derived",
                                provenance="FreeNIC reconstruction",
                                span="reconstruction/")
    return merged


def main() -> int:
    remote = "--remote" in sys.argv
    manifest = load_manifest(remote)
    missing_meta = sorted(set(manifest) - set(C))
    missing_manifest = sorted(set(C) - set(manifest))
    if missing_meta:
        print("[make_registry] manifest files without curated metadata: "
              + ", ".join(missing_meta))
    if missing_manifest:
        print("[make_registry] curated files absent from manifest: "
              + ", ".join(missing_manifest))

    series = []
    for fname, meta in C.items():
        m = manifest.get(fname, {})
        rows = m.get("rows")
        if rows is None:
            print(f"[make_registry] WARNING: no manifest row count for {fname}")
        s = {
            "series_id": meta["series_id"],
            "table_family": meta["family"],
            "title": meta["title"],
            "description": meta["description"],
            "output_file": fname,
            "source": {
                "name": meta["src_name"],
                "url": meta["src_url"],
                "retrieved": meta["retrieved"],
                "license": meta["license"],
                "access": meta["access"],
            },
            "construction": {
                "method": meta["method"],
                "scripts": meta["scripts"],
                "transformations": meta["transforms"],
            },
            "units": meta["units"],
            "frequency": meta["frequency"],
            "coverage": meta["coverage"],
            "rows": rows,
            "tier": m.get("tier", ""),
            "quality": {"status": meta["status"], "notes": meta["notes"]},
        }
        series.append(s)

    registry = {
        "schema_version": "1.0",
        "project": "FreeNIC",
        "generated_at": str(date.today()),
        "_meta": {
            "registry_unit": "served data table / table family (not individual series)",
            "release_version": RELEASE_VERSION,
            "release_date": RELEASE_DATE,
            "data_vintage": DATA_VINTAGE,
            "served_root": "https://data.freenic.org/",
            "reconstruction_root": "https://data.freenic.org/reconstruction/",
            "row_counts_from": "authoritative release manifest (remote when "
                               "reachable, else committed v1.0.0 manifest + "
                               "reconstruction counts)",
            "table_count": len(series),
            "pipeline_of_record": "pipeline/scripts/ (74 phase scripts); this "
                                  "package wraps, documents, and validates it",
        },
        "series": series,
    }
    OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    n_fam = len({s["table_family"] for s in series})
    print(f"[make_registry] wrote {OUT}")
    print(f"[make_registry] {len(series)} tables across {n_fam} families "
          f"({len(missing_meta)} unmapped, {len(missing_manifest)} unmatched)")
    return 0 if not missing_meta and not missing_manifest else 1


if __name__ == "__main__":
    raise SystemExit(main())
