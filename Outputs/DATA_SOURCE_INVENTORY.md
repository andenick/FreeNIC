# freenic Data Source Inventory

*Comprehensive listing of all known US banking regulatory data sources.*
*Updated: 2026-03-24 (Session 8)*

## Ingested Sources

| # | Source | Provider | Script | Table | Rows | Coverage |
|---|--------|----------|--------|-------|------|----------|
| 1 | FR Y-9C (BHCF) | FFIEC | 04, 05 | `bhcf_filings` | 208.1M | 1986Q3-2025Q4 |
| 2 | Call Reports | Chicago Fed | 07 | `call_report_filings` | 896.3M | 1976Q1-2002Q2 |
| 3 | Luck Database | Academic | 08 | `luck_call_reports` | 311.8M | 1959Q4-2025Q4 |
| 4 | OCC Historical | Academic | 09 | `occ_historical` | 9.8M | 1867-1904 |
| 5 | FDIC Failures | FDIC API | 16 | `bank_failures` | 4.1K | 1934-2026 |
| 6 | FDIC SDI Financials | FDIC API | 17 | `fdic_financials` | 69.3M | 1984Q1-2025Q4 |
| 7 | FDIC SOD | FDIC API | 18-19 | `fdic_sod` | 2.7M | 1994-2025 |
| 8 | FDIC History | FDIC API | 25 | `fdic_history` | 581.6K | All dates |
| 9 | DFAST | Federal Reserve | 23 | `dfast_results` | 28K | 2013-2025 |
| 10 | Pillar 3 | HDARP | 24 | `pillar3_disclosures` | 8K | 2024Q1-2025Q3 |
| 11 | NIC Attributes | FFIEC | 02 | `institutions` + 4 tables | 217K | Current |
| 12 | CRSP-FRB Link | NY Fed | 03 | `crsp_mapping` | 19K | 2008-2024 |
| 13 | MDRM | FFIEC | 01 | `mdrm` | 87K | Reference |
| 14 | FRED Banking/Macro | FRED | 27 | `fred_series` | 75K | 1954-2025 |
| 15 | Robin Failing Banks Panel | Volcker/Robin | 28 | `robin_panel` | 2.87M | 1863-2024 |
| 16 | Robin Deposit Dynamics | Volcker/Robin | 28 | `robin_deposits_*` | 3.5K | 1863-2024 |
| 17 | Robin↔FFIEC Crosswalk | Volcker Catalogs | 29 | `robin_crosswalk` | 14.3K | Reference |
| 18 | BHC Ownership Hierarchy | Volcker Catalogs | 29 | `bhc_ownership` | 36.7K | Reference |
| 19 | Sector/SIC Groupings | Volcker Catalogs | 29 | `sector_groupings` | 16.5K | Reference |
| 20 | Fed Stress Scenarios | Volcker/Fed | 30 | `stress_scenarios_*` | 452 | 1976-2029 |

**Total**: 1,502,730,000+ rows across 34 tables

## Blocked Sources

| # | Source | Provider | Status | Notes |
|---|--------|----------|--------|-------|
| 21 | Post-2002 Call Reports | FFIEC CDR | BLOCKED | Cloudflare protection, no REST API |
| 22 | FR Y-9LP | FFIEC NPW | BLOCKED | 403 as of 2026-03-24, Cloudflare |

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
1867 ─────── OCC Historical ──── 1904
                    1959 ─── Luck Database ──────────────── 2025
              1954 ─── FRED Macro ─────────────────────── 2025
                         1976 ── Call Reports ── 2002
                              1984 ── FDIC SDI ──────── 2025
                                   1986 ── BHCF (Y-9C) ─── 2025
                                   1934 ── FDIC Failures ── 2026
                                        1994 ── FDIC SOD ── 2025
                                             2008 ── CRSP ── 2024
                                                  2013 DFAST 2025
1863 ─────── Robin Panel (annual, all banks) ──────────── 2024
```
