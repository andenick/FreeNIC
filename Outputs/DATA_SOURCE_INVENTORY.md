# freenic Data Source Inventory

*Comprehensive listing of all known US banking regulatory data sources.*
*Updated: 2026-06-01 (freeNIC comprehensive update)*

## Ingested Sources

| # | Source | Provider | Script | Table | Rows | Coverage |
|---|--------|----------|--------|-------|------|----------|
| 1 | FR Y-9C (BHCF) | FFIEC | 04, 05 | `bhcf_filings` | 208.1M | 1986Q3-2025Q4 |
| 2 | Call Reports (pre-2012) | Chicago Fed | 07, 07b | `call_report_filings` | (part of 1.912B) | 1976Q1-2011Q4 |
| 2b | Call Reports (post-2011) | FFIEC CDR | 07d, 07e | `call_report_filings` | (part of 1.912B) | 2012Q1-2025Q4 |
| 3 | Luck Database | Academic | 08 | `luck_call_reports` | 311.8M | 1959Q4-2025Q4 |
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
| 15 | Robin Failing Banks Panel | Volcker/Robin | 28 | `robin_panel` | 2.87M | 1863-2024 |
| 16 | Robin Deposit Dynamics | Volcker/Robin | 28 | `robin_deposits_*` | 3.5K | 1863-2024 |
| 17 | Robin↔FFIEC Crosswalk | Volcker Catalogs | 29 | `robin_crosswalk` | 14.3K | Reference |
| 18 | BHC Ownership Hierarchy | Volcker Catalogs | 29 | `bhc_ownership` | 36.7K | Reference |
| 19 | Sector/SIC Groupings | Volcker Catalogs | 29 | `sector_groupings` | 16.5K | Reference |
| 20 | Fed Stress Scenarios | Volcker/Fed | 30 | `stress_scenarios_*` | 452 | 1976-2029 |
| 21 | FFIEC CDR Unrealized Losses | FFIEC CDR | 32, 33 | `cdr_unrealized_losses` | 46.9K | 2019-2025 |
| 22 | FDIC-SDI Feature Panel | Derived (from #6) | 31 | `fdic_sdi_features` | 413.1K | 1984-2025 (annual) |

**Total**: ~2,527,000,000 rows across 37 tables (32 main + 5 catalog)

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
1863 ─────── Robin Panel (annual, all banks) ──────────── 2024
```
