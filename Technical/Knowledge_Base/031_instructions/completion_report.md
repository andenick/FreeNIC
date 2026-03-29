# FFIEC 031 Call Report Instructions — Extraction Completion Report

**Document**: FFIEC 031 — Consolidated Reports of Condition and Income (for banks with domestic AND foreign offices)
**Total Pages**: 88 (RC-1 through RC-88)
**Chunks Processed**: 9 of 9 (chunks 001-009, covering pages 1-88) -- COMPLETE
**Processing Date**: 2026-03-22

---

## Summary

Extracted all MDRM variable definitions, reporting instructions, and schedule structures from all 88 pages of the FFIEC 031 Call Report form. This covers the complete Report of Income (Schedule RI and sub-schedules RI-A through RI-E) and the complete Report of Condition (Schedule RC balance sheet through Schedule RC-V Variable Interest Entities), plus the optional narrative statement page.

## Output Files

### Chunk 001 — Pages 1-10 (Cover, RI Income Statement)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_001_body.md` | 293 | Cover page, contact information, Schedule RI (Income Statement items 1-14, Memoranda M.1-M.15) |
| `031_instructions_chunk_001_table_001.csv` | 63 rows | Schedule RI main items — 63 RIAD variable codes (interest income, interest expense, noninterest income/expense, net income) |
| `031_instructions_chunk_001_table_002.csv` | 28 rows | Schedule RI Memoranda — 28 RIAD variable codes (trading revenue, fair value option, service charges, fiduciary income) |

### Chunk 002 — Pages 11-20 (RI Sub-Schedules, RC Balance Sheet)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_002_body.md` | 333 | Schedules RI-A (Equity Changes), RI-B (Charge-offs/Recoveries), RI-C (Disaggregated Allowance), RI-D (Foreign Office Income), RI-E (Explanations), RC (Balance Sheet), RC-A (Cash), RC-B (Securities, partial) |
| `031_instructions_chunk_002_table_001.csv` | 54 rows | RI-A equity changes (12 items) + RI-B Part I charge-offs/recoveries (38 items with paired RIAD codes) + RI-B Part II allowance changes (4 items) |
| `031_instructions_chunk_002_table_002.csv` | 42 rows | Schedule RC Balance Sheet — 42 RCFD/RCON variable codes (all assets, liabilities, equity capital items) |

### Chunk 003 — Pages 21-30 (RC-B Securities, RC-C Loans, RC-D Trading, RC-E Deposits)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_003_body.md` | 258 | Schedules RC-B (Securities, continued with memoranda), RC-C Part I (Loans and Leases, all items and memoranda), RC-C Part II (Small Business/Farm loans), RC-D (Trading Assets and Liabilities), RC-E (Deposit Liabilities Parts I and II with memoranda) |
| `031_instructions_chunk_003_table_001.csv` | 32 rows | RC-C Loans — 32 RCFD/RCON codes (all loan categories from real estate through leases) |

### Chunk 004 — Pages 31-40 (RC-F through RC-L)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_004_body.md` | 270 | Schedules RC-F (Other Assets), RC-G (Other Liabilities), RC-H (Domestic Office Items), RC-I (IBF Assets/Liabilities), RC-K (Quarterly Averages), RC-L (Derivatives and Off-Balance-Sheet Items — unused commitments, letters of credit, credit derivatives, position indicators, OTC counterparty data) |
| `031_instructions_chunk_004_table_001.csv` | 49 rows | RC-F Other Assets (16 items) + RC-G Other Liabilities (11 items) + RC-K Quarterly Averages (23 items) |

### Chunk 005 — Pages 41-50 (RC-M Memoranda, RC-N Past Due/Nonaccrual)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_005_body.md` | 212 | Schedules RC-M (Memoranda — insider credit, intangibles, OREO, borrowed money, mutual funds, internet websites, PPP loans), RC-N (Past Due and Nonaccrual — all loan categories with 3-column structure, memoranda on loan modifications, guaranteed loans, derivatives) |
| `031_instructions_chunk_005_table_001.csv` | 197 rows | RC-M (52 items) + RC-N past due/nonaccrual (145 items with Col A/B/C breakdown) |

### Chunk 006 — Pages 51-60 (RC-O Deposit Insurance, RC-P Mortgage Banking, RC-Q Fair Value)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_006_body.md` | 275 | Schedule RC-O (Other Data for Deposit Insurance Assessments — items 1-11, Memoranda M.1-M.18 including deposit account size breakdowns, criticized/classified items, PD buckets, guaranteed loans, counterparty exposures, fully consolidated data), Schedule RC-P (1-4 Family Residential Mortgage Banking Activities — originations, sales, HFS, noninterest income, rep and warranty reserves), Schedule RC-Q (Assets and Liabilities Measured at Fair Value on a Recurring Basis — 5-column fair value hierarchy for assets items 1-7 and liabilities items 8-14, memoranda for other assets/liabilities breakdown, loans at fair value, unpaid principal balance) |
| `031_instructions_chunk_006_table_001.csv` | 62 rows | RC-O main items (24) + RC-O memoranda M.1-M.17 (38 items — deposit account breakdowns, CECL, criticized items, nontraditional mortgages, higher-risk loans, counterparty exposures, consolidated data) |
| `031_instructions_chunk_006_table_002.csv` | 109 rows | RC-P (9 items — mortgage banking activities) + RC-Q assets and liabilities fair value hierarchy (90 items across 5 columns) + RC-Q memoranda (10 items — loans at fair value and UPB) |

### Chunk 007 — Pages 61-70 (RC-R Regulatory Capital)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_007_body.md` | 188 | Schedule RC-R Part I (Regulatory Capital Components and Ratios — CET1 capital items 1-19, additional tier 1 items 20-25, tier 1 capital item 26, leverage ratio items 27-31, CBLR qualifying criteria items 32-38, tier 2 capital items 39-46, total capital items 47-48, risk-based capital ratios items 49-51, capital buffer items 52-54, supplementary leverage ratio item 55) and Part II (Risk-Weighted Assets — balance sheet asset categories items 1-8 with 19-column risk-weight allocation from 0% through 1250% plus other approaches) |
| `031_instructions_chunk_007_table_001.csv` | 72 rows | RC-R Part I — 72 RCFA/RCOA/RCFW variable codes (CET1 components and deductions, additional tier 1, tier 2, leverage ratio, CBLR criteria, capital ratios, buffers) |

### Chunk 008 — Pages 71-80 (RC-R Part II cont., RC-S Securitization)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_008_body.md` | 130 | Schedule RC-R Part II continued (securitization exposures items 9-10, total balance sheet assets item 11, derivatives and OBS items 12-22, totals and RWA calculation items 23-31, memoranda M.1-M.4), Schedule RC-S (Servicing, Securitization, and Asset Sale Activities — bank securitization items 1-5 across 7 asset-type columns) |
| `031_instructions_chunk_008_table_001.csv` | 66 rows | RC-R Part II (33 items — securitization exposures, OBS items with CCFs, RWA totals, derivatives memoranda) + RC-S items 1-3 (33 items — securitized assets, max credit exposure, unused liquidity commitments across 7 columns) |

### Chunk 009 — Pages 81-88 (RC-S cont., RC-T Fiduciary, RC-V VIEs, Narrative)
| File | Lines | Description |
|------|-------|-------------|
| `031_instructions_chunk_009_body.md` | 234 | Schedule RC-S continued (items 6-12 — ownership interests, other institutions' securitizations, bank asset sales; memoranda M.2-M.4 — servicing for others, ABCP conduits, credit card fees), Schedule RC-T (Fiduciary and Related Services — fiduciary powers items 1-3, fiduciary assets items 4-13 across 4 columns, fiduciary income items 14-26, memoranda M.1-M.4 — managed asset composition, corporate trust, collective investment funds, fiduciary settlements), Schedule RC-V (Variable Interest Entities — consolidated VIE assets items 1.a-1.e and liabilities items 2.a-2.b across securitization vehicles and other VIEs, plus ABCP conduit items 5-6), Optional Narrative Statement page |
| `031_instructions_chunk_009_table_001.csv` | 86 rows | RC-S continued (27 items — other institutions' securitizations, asset sales, servicing memoranda, ABCP conduits) + RC-T (33 items — fiduciary assets, income, expenses) + RC-V (18 items — VIE assets and liabilities) + Narrative (2 items) |

---

## Totals

| Metric | Count |
|--------|-------|
| Body markdown files | 9 |
| Table CSV files | 11 |
| Total markdown lines | ~2,193 |
| Total CSV data rows (excl. headers) | ~831 |
| MDRM variable codes extracted | 830+ |
| Schedules covered | RI, RI-A, RI-B, RI-C, RI-D, RI-E, RC, RC-A, RC-B, RC-C, RC-D, RC-E, RC-F, RC-G, RC-H, RC-I, RC-K, RC-L, RC-M, RC-N, RC-O, RC-P, RC-Q, RC-R (Parts I and II), RC-S, RC-T, RC-V, Optional Narrative |

## MDRM Prefix Coverage

| Prefix | Meaning | Usage |
|--------|---------|-------|
| RIAD | Year-to-date income/expense items | Schedule RI and sub-schedules, RC-T income items |
| RCFD | Consolidated balance sheet items | All RC schedules (consolidated) |
| RCON | Domestic office items only | Deposit detail, domestic loans, OREO, RC-O deposits, RC-P mortgage banking |
| RCFN | Foreign office items only | Foreign deposits, foreign loans, IBF data, foreign fiduciary accounts |
| RCFA | Regulatory capital items (consolidated) | RC-R Part I (non-advanced approaches) |
| RCFW | Regulatory capital items (advanced approaches) | RC-R Part I (advanced approaches) |
| RCOA | Regulatory capital options/elections | AOCI opt-out, CECL transition, CBLR election, SA-CCR |
| TEXT | Text/descriptive fields | Website URLs, trade names, narrative statement |

## Document Status: COMPLETE

All 88 pages of the FFIEC 031 Call Report form have been fully extracted across 9 chunks. Every schedule from the Report of Income through the Optional Narrative Statement has been processed with MDRM variable codes, reporting rules, and structural notes captured in markdown body files and CSV tables.
