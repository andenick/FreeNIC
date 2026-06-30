# freenic Data Source Inventory

*Comprehensive listing of all known US banking regulatory data sources.*
*Updated: 2026-06-14 (clean_bank_panel promotion + honest live-DB recount)*

> **Live-DB recount (verified read-only; authoritative numbers in
> `Technical/coverage_analysis/live_counts.json`, gated by `tools/check_doc_counts.py`):** the
> warehouse holds **59 base tables** (46 `main` + 6 `catalog` + 7 `dict`; was 58 / 45-`main`
> before the `freenic_manifest` self-describing layer) plus **52 shaped views**, and
> **4,965,894,682 rows (~4.97B)** summed
> over all base tables — substantially
> more than the "37 tables / 2.25B rows" figure below, which predates the NCUA (1.18B),
> UBPR (1.25B + 250M peer-rank + 22M peer-stats), Y-15, HMDA, extended-NIC, dictionary-layer,
> and `clean_bank_panel` additions. Treat the per-row counts in the table below as
> source-by-source minimums; the authoritative live totals are: `call_report_filings`
> 1,917,025,977 · `ubpr_ratios` 1,251,149,050 · `ncua_5300` 1,180,127,221 · `ubpr_peer_rank`
> 250,012,503 · `bhcf_filings` 208,147,772 · `fdic_financials` 69,455,560 · `luck_call_reports`
> 37,753,719 · `ubpr_peer_stats` 22,067,752 · `occ_historical` 17,775,763 ·
> `clean_bank_panel` 1,114,822.

## Ingested Sources

| # | Source | Provider | Script | Table | Rows | Coverage |
|---|--------|----------|--------|-------|------|----------|
| 1 | FR Y-9C (BHCF) | FFIEC | 04, 05 | `bhcf_filings` | 208.1M | 1986Q3-2025Q4 |
| 2 | Call Reports (pre-2012) | Chicago Fed | 07, 07b | `call_report_filings` | (part of 1.912B) | 1976Q1-2011Q4 |
| 2b | Call Reports (post-2011) | FFIEC CDR | 07d, 07e | `call_report_filings` | (part of 1.912B) | 2012Q1-2025Q4 |
| 3 | Luck Database | FRBNY (free public) | 08 | `luck_call_reports` | 37.75M | 1959Q4-1975Q4 (+384 Fed-absent cells) |
| 4 | OCC Historical | Academic + OCC-CLV | 09, 09b | `occ_historical` | 17.8M | 1863-1941 |
| 5 | FDIC Failures | FDIC API | 16 | `bank_failures` | 4.1K | 1934 - 2026-05-01 |
| 6 | FDIC SDI Financials | FDIC API | 17 | `fdic_financials` | 69.5M | 1984Q1-2026Q1 |
| 7 | FDIC SOD | FDIC API | 18-19 | `fdic_sod` | 2.82M | 1994-2025 |
| 8 | FDIC History | FDIC API | 25 | `fdic_history` | 582.6K | All dates |
| 9 | DFAST | Federal Reserve | 23 | `dfast_results` | 28K | 2013-2025 |
| 10 | Pillar 3 | PDF extract | 24 | `pillar3_disclosures` | 8K | 2024Q1-2025Q3 |
| 11 | NIC Attributes | FFIEC | 02 | `institutions` + 4 tables | 217K | Current |
| 12 | CRSP-FRB Link | NY Fed | 03 | `crsp_mapping` | 19K | 2008-2024 |
| 13 | MDRM | FFIEC | 01 | `mdrm` | 87K | Reference |
| 14 | FRED Banking/Macro | FRED | 27 | `fred_series` | 75.3K | 1919 - 2026-05 |
| 15 | Failing Banks Panel (CLV derived ADD-ON; ratios clean, absolute-$ uncalibrated — use #23 for levels) | failing-banks (CLV-derived) | 28 | `robin_panel` | 2.87M | 1863-2024 |
| 16 | Failing Banks Deposit Dynamics | failing-banks (CLV-derived) | 28 | `robin_deposits_*` | 3.5K | 1863-2024 |
| 17 | Failing Banks↔FFIEC Crosswalk | Derived (FFIEC/NIC) | 29 | `robin_crosswalk` | 14.3K | Reference |
| 18 | BHC Ownership Hierarchy | Derived (NIC structure) | 29 | `bhc_ownership` | 36.7K | Reference |
| 19 | Sector/SIC Groupings | Derived (CIK→SIC) | 29 | `sector_groupings` | 16.5K | Reference |
| 20 | Fed Stress Scenarios | Federal Reserve | 30 | `stress_scenarios_*` | 452 | 1976-2029 |
| 21 | FFIEC CDR Unrealized Losses | FFIEC CDR | 32, 33 | `cdr_unrealized_losses` | 46.9K | 2019-2025 |
| 22 | FDIC-SDI Feature Panel | Derived (from #6) | 31 | `fdic_sdi_features` | 413.1K | 1984-2025 (annual) |
| 23 | **Clean Bank Panel (CANONICAL from-raw levels)** | Derived FROM RAW (#3 luck_wide + #4 occ_historical_clv + Call schedules); finhist-primary | 45 | `clean_bank_panel` | 1.11M | 1863-2026 (annual) |

> **#23 `clean_bank_panel` is the canonical per-bank panel for absolute dollar LEVELS** — nominal +
> CPI-real $ (base 1990=100), unit-gate-verified (JPM-2008 $1.7462T, SVB $209.0B, occ-1929 $1.80B),
> deterministic/byte-stable (sha d0fb7c8d). It is the fix for `robin_panel`'s uncalibrated absolute-$
> columns. **finhist.com is primary; this from-raw panel is primary; `robin_panel` is a derived
> add-on, not the base.** Built by `45_build_clean_bank_panel.py` (reuse of Bev Testing
> `r2_build_clv_panel.py`); finhist historical-call v2.10.0 (2026-03-31), arXiv:2506.06082.

**Total** (legacy figure, undercounts — see the live-DB recount note at the top of this file):
~2,258,132,117 rows across 37 tables (32 main + 5 catalog) — Luck deduped to pre-1976 core 2026-06-05 (−273.7M redundant 1976+ rows, served by `call_report_filings`); +1.73M trust-company rows recovered into `call_report_filings` from FFIEC CDR (Phase 7f). `call_report_filings` now 1,917,025,977.

## Blocked Sources

| # | Source | Provider | Status | Notes |
|---|--------|----------|--------|-------|
| 23 | FR Y-9LP | FFIEC NPW | BLOCKED | 403 as of 2026-03-24, Cloudflare |

> **Post-2011 call reports — NO LONGER BLOCKED (2026-05-31).** Previously listed here as
> "Cloudflare-blocked, no REST API." The W16 CLV campaign proved the FFIEC CDR Bulk Data
> single-period flow is downloadable via a Playwright RadAjax automation (`07d`); all 56 quarters
> 2012Q1-2025Q4 are now ingested (source #2b). The Cloudflare-blocked note is retired.

## Potential Future Sources

| # | Source | Provider | Effort | Est. Rows | Value |
|---|--------|----------|--------|-----------|-------|
| 23 | SEC EDGAR | SEC | Medium | ~100K | BHC 10-K/10-Q filings, CIK crosswalk |
| 24 | HMDA Summary | CFPB | Medium | ~500K-1M | Mortgage lending by institution |
| 25 | FDIC Locations | FDIC API | Low | ~100K | Branch lat/lon (may overlap SOD) |
| 26 | NCUA 5300 | NCUA | Medium | ~10M | Credit union call reports |

## Out of Scope

| Source | Reason |
|--------|--------|
| FR Y-14 | Confidential (FOMC stress testing) |
| FR 2052a | Confidential (liquidity monitoring) |
| BIS Banking Stats | International focus, low US value |
| FHLB Advances | Requires FHLB registration |
| Bloomberg/Refinitiv | Proprietary, not public data |

## Coverage Timeline

```
1863 ─────── OCC Historical ──────── 1941
                    1959 ─── Luck Database ──────────────── 2025
       1919 ─── FRED Macro ────────────────────────────── 2026
                         1976 ──── Call Reports ──────────── 2025
                              1984 ── FDIC SDI ─────────── 2026Q1
                                   1986 ── BHCF (Y-9C) ─── 2025
                                   1934 ── FDIC Failures ── 2026
                                        1994 ── FDIC SOD ── 2025
                                             2008 ── CRSP ── 2024
                                                  2013 DFAST 2025
                                              2019 CDR Unrealized 2025
                                  1984 ── SDI Features (annual) ── 2025
1863 ─────── Failing Banks Panel (annual, all banks) ──── 2024
```
