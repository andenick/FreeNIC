# freenic Ingestion Log

| Timestamp | Phase | Message |
|---|---|---|
| 2026-03-22 13:10:48 | Phase 0 | Database created with 18 tables |
| 2026-03-22 13:15:22 | Phase 1 | MDRM ingested: 87,351 rows, 847 mnemonics, 180 forms. Duplicates identical: False. 159.6s |
| 2026-03-22 14:30:49 | Phase 2 | Entities: 59,824 active + 157,386 closed institutions, 173,250 branches, 286,223 relationships, 58,935 transformations. 4.4s |
| 2026-03-22 14:32:38 | Phase 3 | CRSP: 18,908 records from 16 files, 1,457 PERMCOs, 1,516 RSSDs. 40.0s |
| 2026-03-22 14:50:24 | Phase 4 | BHCF TXT: 154,292,629 observations, 9,050 entities, 3,208 variables, 104 quarters. 888.2s |
| 2026-03-22 15:05:08 | Phase 4 | BHCF TXT: 154,292,629 observations, 9,050 entities, 3,208 variables, 104 quarters. 873.5s |
| 2026-03-22 15:10:00 | Phase 5 | BHCF CSV pre-2000: 53,855,143 observations from 54 files. Grand total: 208,147,772. 170.3s |
| 2026-03-22 15:10:27 | Phase 6 | Y-9C verification: 3 checked, 3 matches. Confirmed duplicates, skipped. |
| 2026-03-22 15:44:29 | Phase 7 | Call Reports: 896,251,036 observations, 22,185 entities, 4,473 variables, 101 quarters, 101 schedules. 1909.8s |
| 2026-03-22 15:57:56 | Phase 8 | Luck Database: 311,809,300 observations, 24,716 entities, 245 variables, 0 quarters. 256.0s |
| 2026-03-22 17:07:14 | Phase 8 | Luck Database: 311,809,300 observations, 24,716 entities, 245 variables, 246 quarters. 709.9s |
| 2026-03-22 17:07:40 | Phase 9 | OCC Historical: 9,788,940 observations, 7,109 banks, 95 variables. 12.6s |
| 2026-03-22 17:14:28 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 158.5s |
| 2026-03-22 17:15:03 | Phase 11 | Built 4 convenience views: bhcf_enriched, current_hierarchy, entity_summary, variable_dictionary. 3.6s |
| 2026-03-22 17:47:36 | Phase 12 | Parquet export: 18 tables, 3,313.2 MB total. 1930.9s |
| 2026-03-22 17:59:50 | Phase 12 | Parquet export: 18 tables, 3,314.6 MB total. 1988.0s |
| 2026-03-22 19:17:51 | Phase 13 | Validation: 5/6 checks passed. 12.6s |
| 2026-03-22 23:35:16 | Phase 16 | FDIC Failed Banks: 4,114 failures, 1934-04-19 to 2026-01-30. 8.3s |
| 2026-03-23 01:50:27 | Phase 17 | FDIC Financials: 69,272,714 obs, 24,056 institutions, 58 vars, 168 quarters, 1984-03-31 to 2025-12-31. 548.3s |
| 2026-03-23 10:44:17 | Phase 18 | FDIC SOD Download: 2,000,000 records, 200 pages. 1306.1s |
| 2026-03-23 21:58:42 | Phase 19 | FDIC SOD: 2,740,878 records, 15,505 institutions, 32 years (1994-2025). 301.4s |
| 2026-03-23 22:09:24 | Phase 24 | Pillar 3: 7,952 obs, 5 banks, 6 periods, 319 tables. 23.6s |
| 2026-03-23 22:13:38 | Phase 23 | DFAST: 28,231 obs, 43 banks, 13 years (2013-2025), 56 variables. 41.2s |
| 2026-03-23 22:21:01 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 255.6s |
| 2026-03-23 22:25:11 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 239.7s |
| 2026-03-23 22:53:49 | Phase 12 | Parquet export: 23 tables, 1,438.9 MB total. 916.8s |
| 2026-03-24 12:12:24 | Phase 13 | Validation: 5/6 checks passed. 13.3s |
| 2026-03-24 12:16:26 | Phase 13 | Validation: 6/7 checks passed. 11.7s |
| 2026-03-24 12:18:03 | Phase 20 | Variable crosswalks: 61 entries across 3 sources. 2.2s |
| 2026-03-24 12:18:58 | Phase 11 | Built 8 convenience views. 5.5s |
| 2026-03-24 12:21:00 | Phase 20 | Variable crosswalks: 64 entries across 3 sources. 1.9s |
| 2026-03-24 12:21:12 | Phase 11 | Built 8 convenience views. 11.5s |
| 2026-03-24 12:21:41 | Phase 11 | Built 8 convenience views. 15.7s |
| 2026-03-24 12:22:42 | Phase 11 | Built 8 convenience views. 6.4s |
| 2026-03-24 13:15:24 | Phase 12 | Parquet export: 24 tables, 3,864.8 MB total. 1708.8s |
| 2026-03-24 13:15:50 | Phase 13 | Validation: 6/7 checks passed. 15.6s |
| 2026-03-24 14:48:31 | Phase 25 | FDIC history: 581,588 records. 4.2s |
| 2026-03-24 15:14:59 | Phase 27 | FRED series: 0 obs from 15 series. 1.2s |
| 2026-03-24 15:16:57 | Phase 27 | FRED series: 75,037 obs from 15 series. 94.7s |
| 2026-03-24 16:07:26 | Phase 12 | Parquet export: 26 tables, 4,492.6 MB total. 3014.8s |
| 2026-03-24 21:40:31 | Phase 28 | Failing Banks panel: 2,867,936 + deposits: 3,508. 42.7s |
| 2026-03-24 21:41:01 | Phase 29 | BHC/identifier catalogs: crosswalk=14,286, hierarchy=36,668, sectors=16,548. 1.6s |
| 2026-03-24 21:41:46 | Phase 30 | Stress scenarios: domestic=226, intl=226. 1.3s |
| 2026-03-24 21:43:31 | Phase 11 | Built 10 convenience views. 9.4s |
| 2026-03-24 23:52:07 | Phase 12 | Parquet export: 34 tables, 5,083.0 MB total. 7671.6s |
| 2026-03-25 07:59:43 | Phase 20 | Variable crosswalks: 76 entries across 4 sources. 44.9s |
| 2026-03-25 08:00:35 | Phase 13 | Validation: 6/7 checks passed. 13.1s |
| 2026-03-30 22:01:12 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 178.2s |
| 2026-03-30 22:47:25 | Phase 12 | Parquet export: 34 tables, 5,065.2 MB total. 2722.1s |
| 2026-05-29 22:20:19 | Phase 9b | OCC Historical CLV (finhist): 7,986,823 obs, 14,258 banks, 66 vars, 1863-11-28..1941-12-31, source='occ_historical_clv'. Existing occ_historical untouched (9,788,940 rows). 19.4s |
| 2026-05-29 22:21:05 | Phase 9b | occ_historical.parquet re-export: 17,775,763 rows (44.1 MB). 2.4s |
| 2026-05-29 23:48:51 | Phase 7b | Incremental Call Reports: +202,525,602 rows, +13 quarters ['1976-12-31', '1997-09-30', '1997-12-31', '2009-09-30', '2009-12-31', '2010-03-31', '2010-06-30', '2010-09-30', '2010-12-31', '2011-03-31', '2011-06-30', '2011-09-30', '2011-12-31'], span now 1976-03-31..2011-12-31 (132 quarters). Skipped existing=119, unreadable=10. Non-destructive (prior missing=0). 316.4s |
| 2026-05-30 16:38:19 | Phase 7b | Re-export call_report_filings.parquet: 1,401,595,327 rows, 134 quarters (+2002Q3,2003Q1 recovered), 3,973.8 MB. Supersedes 132-qtr export of 2026-05-30 00:08. |
| 2026-05-30 18:51:56 | Phase 7b | Incremental Call Reports: +122,865,603 rows, +8 quarters ['2003-06-30', '2003-09-30', '2003-12-31', '2004-06-30', '2004-12-31', '2005-03-31', '2005-09-30', '2006-03-31'], span now 1976-03-31..2011-12-31 (142 quarters). Skipped existing=134, unreadable=0. Non-destructive (prior missing=0). 179.9s |
| 2026-05-31 09:52:09 | Phase 7b | Incremental Call Reports: +0 rows, +0 quarters [], span now 1976-03-31..2011-12-31 (142 quarters). Skipped existing=142, unreadable=0. Non-destructive (prior missing=0). 70.2s |
| 2026-05-31 10:19:10 | Phase 7b | Incremental Call Reports: +22,833,915 rows, +2 quarters ['1997-03-31', '1997-06-30'], span now 1976-03-31..2011-12-31 (144 quarters). Skipped existing=142, unreadable=0. Non-destructive (prior missing=0). 32.3s |
| 2026-05-31 19:32:14 | Phase 31 | fdic_sdi_features table built: 413,130 rows, 23,065 entities, 1984-2025 (Q4, FDIC SDI features). |
| 2026-05-31 19:32:25 | Phase 33 | cdr_unrealized_losses table built: 46,929 rows, 5,290 entities, periods 2019-12-31..2025-12-31 (FFIEC CDR fair-value/AOCI/brokered). |
| 2026-05-31 19:46:37 | Phase 16 | FDIC Failed Banks: 4,115 failures, 1934-04-19 to 2026-05-01. 57.5s |
| 2026-05-31 19:53:02 | Phase 25 | FDIC history: 582,628 records. 251.6s |
| 2026-05-31 19:58:19 | Phase 27 | FRED series: 75,257 obs from 15 series. 152.0s |
| 2026-05-31 20:15:11 | Phase 17 | FDIC Financials: 69,455,560 obs, 24,060 institutions, 58 vars, 169 quarters, 1984-03-31 to 2026-03-31. 70.0s |
| 2026-05-31 20:18:22 | Phase 18 | FDIC SOD Download: 160,000 records, 16 pages. 87.2s |
| 2026-05-31 20:52:52 | Phase 18 | FDIC SOD Download: 2,000,000 records, 200 pages. 1965.6s |
| 2026-05-31 21:27:23 | Phase 19 | FDIC SOD: 2,815,984 records, 15,505 institutions, 32 years (1994-2025). 363.6s |
| 2026-05-31 21:30:10 | Phase 23 | DFAST: 28,231 obs, 43 banks, 13 years (2013-2025), 56 variables. 83.4s |
| 2026-05-31 22:41:48 | Phase 7e | CDR post-2011 Call Reports: +364,790,180 rows, +56 quarters ['2012-03-31', '2012-06-30', '2012-09-30', '2012-12-31', '2013-03-31', '2013-06-30', '2013-09-30', '2013-12-31', '2014-03-31', '2014-06-30', '2014-09-30', '2014-12-31', '2015-03-31', '2015-06-30', '2015-09-30', '2015-12-31', '2016-03-31', '2016-06-30', '2016-09-30', '2016-12-31', '2017-03-31', '2017-06-30', '2017-09-30', '2017-12-31', '2018-03-31', '2018-06-30', '2018-09-30', '2018-12-31', '2019-03-31', '2019-06-30', '2019-09-30', '2019-12-31', '2020-03-31', '2020-06-30', '2020-09-30', '2020-12-31', '2021-03-31', '2021-06-30', '2021-09-30', '2021-12-31', '2022-03-31', '2022-06-30', '2022-09-30', '2022-12-31', '2023-03-31', '2023-06-30', '2023-09-30', '2023-12-31', '2024-03-31', '2024-06-30', '2024-09-30', '2024-12-31', '2025-03-31', '2025-06-30', '2025-09-30', '2025-12-31'], span now 1976-03-31..2025-12-31 (200 quarters). Skipped existing=0, failed=0. Non-destructive (prior missing=0). 1155.4s |
| 2026-05-31 23:17:28 | Phase 7b | Re-export call_report_filings.parquet: 1,912,085,025 rows, 200 quarters (+2002Q3,2003Q1 recovered), 5,186.9 MB. Supersedes 132-qtr export of 2026-05-30 00:08. |
| 2026-05-31 23:33:01 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 489.5s |
| 2026-05-31 23:33:53 | Phase 11 | Built 10 convenience views. 10.8s |
| 2026-06-01 00:05:26 | Phase 12 | Targeted re-export of 12 changed/new tables (fdic_sdi_features, cdr_unrealized_losses, refreshed FDIC/FRED + catalog); 413.9 MB. call_report_filings already current (7b 23:17). |
| 2026-06-01 00:06:20 | Phase 13 | Validation: 5/8 checks passed. 21.9s |
| 2026-06-01 00:07:28 | Phase 13 | Validation: 5/8 checks passed. 19.6s |
| 2026-06-01 | Summary | freeNIC comprehensive update complete: call_report_filings extended to 2025Q4 (200 qtrs, 1.912B rows via FFIEC CDR 07d/07e); new tables fdic_sdi_features (413,130) + cdr_unrealized_losses (46,929); occ_historical 1863-1941 (17.8M); FDIC SDI/failures/SOD/history + FRED refreshed; bank_failures.state_code fixed; bank_failures_enriched cert-reuse guard. DB ~2.53B rows, 32 main + 5 catalog tables + 10 views. Docs (DATA_DICTIONARY, DATA_SOURCE_INVENTORY, COVERAGE_GAPS) + tests updated. |
| 2026-06-01 08:25:52 | Phase 20b | entity_xref built: 234,462 distinct rssd identities (union of institutions/transformations/crsp_mapping/robin_crosswalk/bank_failures_enriched/fdic_history). 27.9s |
| 2026-06-01 10:02:14 | Phase 12b | Re-export call_report_filings.parquet (period-chunk, spill-safe): 1,912,085,025 rows, 200 quarters, 4,685.3 MB. 2026-06-01. |
| 2026-06-01 10:03:27 | Phase 13 | Validation: 6/8 checks passed. 15.9s |
| 2026-06-01 10:06:10 | Phase 12b/13/Validation | Wave-2 robust-export + referential validation (2026-06-01). TRACK 1: 12b period-chunk spill-safe export of call_report_filings --force COMPLETED with NO hang in 86m44s (200 period chunks sort-then-concatenate, peak RAM ~21GB under memory_limit=40GB, temp_directory=Outputs/_duckdb_tmp on D:). Parity TRUE: DB==parquet 1,912,085,025 rows / 200 quarters (1976-03-31..2025-12-31) / 4,685.3 MB; atomic publish, zero leftover tmp_*.parquet, markers JSON written. TRACK 2: entity_xref=234,462 rssds (217,210 institutions + 17,252 historical). 13_validate.py 6/8 (was 5/8): referential check #1 now PASSES era-stratified vs entity_xref (call_report 95.6%/modern 96.5%, luck 100%, fdic_financials 99.8%, fdic_sod 99.7%, bhcf 97.7%, dfast 97.7%, pillar3 100%); remaining 2 non-pass are pre-existing WARNs (occ date-range, cdr timestamp-format) unrelated to either fix. pytest 174 passed (test_mcp excluded, missing mcp pkg); injected-break regression guard test_modern_gate_fails_on_injected_break PASSES (gate is honest, not a no-op). BOTH fixes validated end-to-end. |
| 2026-06-01 10:22:14 | Phase 13 | Validation: 8/8 checks passed. 11.0s |
| 2026-06-01 12:35:01 | Phase 12 | Parquet export: 36 tables (exported 36, skipped 0, empty 0, errors 0); 7,339.0 MB newly written. 7540.1s |
| 2026-06-01 12:37:09 | Phase 12 | Parquet export: 37 tables (exported 1, skipped 36, empty 0, errors 0); 0.8 MB newly written. 4.0s |
| 2026-06-01 13:09:17 | Phase 13 | Validation: 8/8 checks passed. 14.9s |
| 2026-06-01 13:17:54 | Phase 7e | CDR post-2011 Call Reports: +3,207,071 rows, +1 quarters ['2026-03-31'], span now 1976-03-31..2026-03-31 (201 quarters). Skipped existing=56, failed=0. Non-destructive (prior missing=0). 16.6s |
| 2026-06-01 14:46:43 | Phase 12 | Parquet export: 37 tables (exported 1, skipped 36, empty 0, errors 0); 4,692.1 MB newly written. 5250.9s |
| 2026-06-01 14:47:54 | Phase 13 | Validation: 7/8 checks passed. 19.2s |
| 2026-06-01 14:49:10 | Phase 13 | Validation: 7/8 checks passed. 13.6s |
| 2026-06-01 14:51:53 | Phase 13 | Validation: 8/8 checks passed. 13.4s |
| 2026-06-01 14:54:28 | Phase 12 | Post-2026Q1 re-export: call_report_filings (201 quarters, 1,915,292,096 rows, 4,692.1 MB, period-chunk, 87.5m) + filing_metadata catch-up (359 rows). filing_metadata now ALWAYS_EXPORT (skip-if-current cannot detect its own growth). Parity 37/37 OK. 13_validate 8/8 (call_report date bound 2025-12-31->2026-06-30). |
| 2026-06-05 18:25:35 | Phase 13 | Validation: 8/8 checks passed. 12.4s |
| 2026-06-05 18:41:40 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 514.1s |
| 2026-06-05 18:47:48 | Dedup | Luck slimmed 311,809,300 -> 38,105,257 rows (pre-1976 core + 2,285 Fed-absent gap-fill cells); 1976+ dropped as 99.88% redundant with call_report_filings (D1 gate core 99.89%). Catalog rebuilt; validate 8/8; pytest 189/0. |
| 2026-06-05 19:16:15 | Phase 8b | Slim Luck: 38,105,257 -> 38,105,257 rows (dropped 0 redundant 1976+; kept pre-1976 37,716,069 + gap-fill 389,188). 1959-12-31..2023-03-31. 8.4s |
| 2026-06-05 19:28:53 | Phase 13 | Validation: 8/8 checks passed. 10.3s |
| 2026-06-05 19:56:25 | Phase 13 | Validation: 8/8 checks passed. 8.2s |
| 2026-06-05 20:29:23 | Phase 8b | Slim Luck: 38,105,257 -> 37,753,719 rows (dropped 351,538 redundant 1976+; kept pre-1976 37,716,069 + gap-fill 37,650). 1959-12-31..2023-03-31. 6.5s |
| 2026-06-05 21:51:31 | Phase 13 | Validation: 8/8 checks passed. 8.5s |
| 2026-06-05 22:51:33 | Phase 24 | Pillar 3: 7,974 obs, 7 banks, 6 periods, 325 tables. 63.5s |
| 2026-06-05 22:53:19 | Phase 13 | Validation: 8/8 checks passed. 9.4s |
| 2026-06-05 23:14:52 | Phase 24 | Pillar 3: 9,172 obs, 7 banks, 6 periods, 369 tables. 19.4s |
| 2026-06-05 23:15:08 | Phase 13 | Validation: 8/8 checks passed. 14.3s |
| 2026-06-05 23:57:03 | Phase 26 | NCUA 5300 credit-union call reports (SCOPE EXPANSION): 11,542,859 cells, 4,550 directory rows, 4,550 credit unions, 2,539 account codes, 12 schedules. 6.0s |
| 2026-06-06 00:00:56 | Phase 26 | NCUA 5300 credit-union call reports (SCOPE EXPANSION): 14,755,171 cells, 4,550 directory rows, 4,550 credit unions, 3,262 account codes, 17 schedules. 49.8s |
| 2026-06-06 00:02:13 | Phase 26 | NCUA 5300 credit-union call reports (SCOPE EXPANSION): 14,755,171 cells, 4,550 directory rows, 4,550 credit unions, 3,262 account codes, 17 schedules. 41.7s |
| 2026-06-06 00:05:13 | Phase 13 | Validation: 7/8 checks passed. 13.2s |
| 2026-06-06 00:05:33 | Phase 13 | Validation: 7/8 checks passed. 8.9s |
| 2026-06-06 00:05:58 | Phase 13 | Validation: 7/8 checks passed. 8.1s |
| 2026-06-06 00:11:16 | Phase 13 | Validation: 8/8 checks passed. 9.5s |
| 2026-06-06 00:11:43 | Phase 13 | Validation: 8/8 checks passed. 8.8s |
| 2026-06-06 09:52:03 | Phase 24 | Pillar 3: 9,523 obs, 8 banks, 6 periods, 387 tables. 38.8s |
| 2026-06-06 09:53:08 | Phase 13 | Validation: 8/8 checks passed. 9.8s |
| 2026-06-06 10:48:23 | Phase 34 | SEC EDGAR CIK<->bank/BHC crosswalk (data.sec.gov): 371 rows, 6 distinct SIC codes, 321 with ticker, 351 with 2024Q4 assets. www.sec.gov Akamai-blocked; built via XBRL frames + submissions SIC filter. 363.5s |
| 2026-06-06 10:50:34 | Phase 13 | Validation: 8/8 checks passed. 16.9s |
| 2026-06-06 11:40:08 | Phase 13 | Validation: 8/8 checks passed. 9.4s |
| 2026-06-06 15:32:11 | Phase 35 | HMDA mortgage-lending institution x year summary (CFPB Data Browser API): 57,654 rows at (lei, activity_year, loan_purpose), 9,609 institution-years, years [2022, 2023]. LEI->RSSD name-matched 5,569/9,609 (58.0%). SUMMARY not full LAR; adjacent to call-report core. cross-check mismatches=0. 2112.6s |
| 2026-06-06 15:33:24 | Phase 13 | Validation: 8/8 checks passed. 8.6s |
| 2026-06-06 23:09:21 | Phase 13 | Validation: 8/8 checks passed. 9.2s |
| 2026-06-06 23:35:27 | Phase 13 | Validation: 8/8 checks passed. 9.2s |
| 2026-06-06 23:56:25 | Phase 13 | Validation: 8/8 checks passed. 9.2s |
| 2026-06-07 00:23:05 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 454.0s |
| 2026-06-07 00:25:23 | Phase 13 | Validation: 8/8 checks passed. 8.8s |
| 2026-06-07 00:33:51 | Phase 13 | Validation: 8/8 checks passed. 8.9s |
| 2026-06-07 00:42:59 | Phase 13 | Validation: 8/8 checks passed. 8.6s |
| 2026-06-07 00:49:35 | Phase 36 | id_crosswalk: 3,440 rows (cik=204, lei=3,240, cert=3,440). RSSD<->cert<->CIK<->LEI from in-warehouse data; GLEIF enrichment optional. 8.2s |
| 2026-06-07 00:53:42 | Phase 13 | Validation: 8/8 checks passed. 9.6s |
| 2026-06-07 01:04:08 | Phase 13 | Validation: 8/8 checks passed. 9.0s |
| 2026-06-07 01:17:42 | Phase 26 | NCUA 5300 credit-union call reports (SCOPE EXPANSION): 75,330,908 cells, 23,149 directory rows, 4,720 credit unions, 3,278 account codes, 17 schedules. 381.5s |
| 2026-06-07 01:19:55 | Phase 13 | Validation: 7/8 checks passed. 8.4s |
| 2026-06-07 01:20:14 | Phase 13 | Validation: 7/8 checks passed. 8.4s |
| 2026-06-07 01:20:56 | Phase 13 | Validation: 8/8 checks passed. 8.4s |
| 2026-06-07 01:35:00 | Phase 35 | HMDA mortgage-lending institution x year summary (CFPB Data Browser API): 208,302 rows at (lei, activity_year, loan_purpose), 34,717 institution-years, years [2018, 2019, 2020, 2021, 2022, 2023, 2024]. LEI->RSSD name-matched 19,349/34,717 (55.7%). SUMMARY not full LAR; adjacent to call-report core. cross-check mismatches=0. 370.3s |
| 2026-06-07 01:35:25 | Phase 13 | Validation: 8/8 checks passed. 9.1s |
| 2026-06-07 12:55:14 | Phase 13 | Validation: 8/8 checks passed. 12.6s |
| 2026-06-07 14:58:38 | Phase 37 | NIC entity identifiers (authoritative Fed crosswalk): 102,932 rows; lei=12,754 occ=2,037 ncua=21,984 cert=10,433. 3.4s |
| 2026-06-07 15:05:33 | Phase 36 | id_crosswalk (W18 authoritative): 103,037 rows (cik=204, lei=15,278 [nic=12,754/hmda=2,524], cert=102,720, occ=2,037, ncua=21,984). Authoritative NIC IDs from nic_entity_identifiers. 253.2s |
| 2026-06-07 15:08:28 | Phase 13 | Validation: 8/8 checks passed. 14.2s |
| 2026-06-07 15:54:32 | Phase 37b | NIC attribute extension: 220,092 rows, 33 Fed-direct attribute cols (geography + charter/reg + status/type). 4.7s |
| 2026-06-07 15:56:11 | Phase 37b | NIC attribute extension: 220,092 rows, 33 Fed-direct attribute cols (geography + charter/reg + status/type). 5.4s |
| 2026-06-07 15:57:47 | Phase 13 | Validation: 8/8 checks passed. 12.5s |
| 2026-06-07 18:19:00 | Phase 39 | UBPR ratios: 11,280,931 rows, 4,543 banks, 1 periods, 2,803 concepts (XBRL from CDR bulk). 32.0s |
| 2026-06-07 18:23:31 | Phase 13 | Validation: 8/8 checks passed. 16.1s |
| 2026-06-07 18:32:19 | Phase 39 | UBPR ratios: 54,324,336 rows, 4,650 banks, 5 periods, 2,803 concepts (XBRL from CDR bulk). 183.0s |
| 2026-06-07 18:33:02 | Phase 13 | Validation: 8/8 checks passed. 16.0s |
| 2026-06-07 18:43:50 | Phase 39 | UBPR ratios: 43,294,650 rows, 4,650 banks, 5 periods, 2,803 concepts (XBRL from CDR bulk). 298.6s |
| 2026-06-07 18:44:32 | Phase 13 | Validation: 8/8 checks passed. 13.9s |
| 2026-06-07 19:53:37 | Phase 41 | FR Y-15 systemic-risk indicators: 22,481 rows, 57 institutions, 5 years, 184 RISK line items (FFIEC NIC Y-15 snapshots). 10.9s |
| 2026-06-07 19:56:03 | Phase 13 | Validation: 8/8 checks passed. 13.4s |
| 2026-06-07 20:20:10 | Phase 27b | FRED H.8 disaggregated: +118 series; fred_series now 130,188 rows / 133 series. 34.1s |
| 2026-06-07 22:26:10 | Phase 27b | FRED H.8 disaggregated: +1,934 series; fred_series now 1,334,059 rows / 1,943 series. 1034.2s |
| 2026-06-07 22:27:23 | Phase 13 | Validation: 8/8 checks passed. 19.4s |
| 2026-06-07 22:48:06 | Phase 39 | UBPR ratios: 79,120,269 rows, 4,879 banks, 9 periods, 2,817 concepts (XBRL from CDR bulk). 208.8s |
| 2026-06-07 22:54:15 | Phase 13 | Validation: 8/8 checks passed. 13.1s |
| 2026-06-07 23:10:52 | Phase 10 | Catalog built: variables, filing_coverage, entity_coverage, schema_evolution, data_sources. 538.3s |
| 2026-06-07 23:12:07 | Phase 13 | Validation: 8/8 checks passed. 9.4s |
| 2026-06-07 23:28:39 | Phase 13 | Validation: 8/8 checks passed. 9.6s |
| 2026-06-08 00:17:29 | Phase 13 | Validation: 8/8 checks passed. 9.3s |
| 2026-06-08 00:35:22 | Phase 13 | Validation: 8/8 checks passed. 7.8s |
| 2026-06-08 01:48:55 | Phase 39 | UBPR ratios: 116,155,287 rows, 5,073 banks, 13 periods, 2,817 concepts (XBRL from CDR bulk). 242.7s |
| 2026-06-08 01:58:53 | Phase 13 | Validation: 8/8 checks passed. 11.2s |
| 2026-06-08 02:47:52 | Phase 13 | Validation: 8/8 checks passed. 7.7s |
| 2026-06-08 21:45:22 | Phase 13 | Validation: 8/8 checks passed. 11.0s |
| 2026-06-08 21:59:49 | Phase 13 | Validation: 9/9 checks passed. 8.3s |
| 2026-06-08 22:44:44 | Phase 44 | Built catalog.namespace_variables. 2.9s |
| 2026-06-08 22:45:33 | Phase 44 | Built catalog.namespace_variables. 2.9s |
| 2026-06-08 22:46:59 | Phase 12 | Parquet export: 47 tables (exported 4, skipped 43, empty 0, errors 0); 4,807.9 MB newly written. 4.6s |
| 2026-06-08 22:47:33 | Phase 13 | Validation: 10/10 checks passed. 16.7s |
| 2026-06-08 22:55:42 | Phase 13 | Validation: 10/10 checks passed. 18.3s |
| 2026-06-08 23:22:52 | Phase 12 | Parquet export: 48 tables (exported 2, skipped 46, empty 0, errors 0); 0.0 MB newly written. 1.1s |
| 2026-06-08 23:54:48 | Phase 13 | Validation: 10/10 checks passed. 13.9s |
| 2026-06-09 00:22:10 | Phase 13 | Validation: 10/10 checks passed. 9.9s |
| 2026-06-09 01:37:44 | Phase 42 | UBPR peer ingest: 988,450 rows in 10.4s |
| 2026-06-09 01:39:57 | Phase 42 | UBPR peer ingest: 939,214 rows in 9.4s |
| 2026-06-09 02:09:30 | Phase 42 | UBPR peer ingest: 22,067,752 rows in 204.3s |
| 2026-06-09 02:10:44 | Phase 12 | Parquet export: 49 tables (exported 2, skipped 47, empty 0, errors 0); 88.8 MB newly written. 5.2s |
| 2026-06-09 02:11:57 | Phase 13 | Validation: 10/10 checks passed. 15.3s |
| 2026-06-09 02:41:50 | Phase 42 | UBPR peer ingest: 250,012,503 rows in 292.7s |
| 2026-06-09 02:45:19 | Phase 12 | Parquet export: 50 tables (exported 2, skipped 48, empty 0, errors 0); 902.0 MB newly written. 81.4s |
| 2026-06-09 02:45:45 | Phase 13 | Validation: 10/10 checks passed. 12.2s |
| 2026-06-09 03:40:31 | Phase 39 | UBPR ratios: 154,188,856 rows, 5,221 banks, 17 periods, 2,822 concepts (XBRL from CDR bulk). 249.0s |
| 2026-06-09 03:51:37 | Phase 39 | UBPR ratios: 237,585,672 rows, 5,735 banks, 25 periods, 2,943 concepts (XBRL from CDR bulk). 554.7s |
| 2026-06-09 03:52:21 | Phase 13 | Validation: 9/10 checks passed. 17.3s |
| 2026-06-09 03:53:19 | Phase 13 | Validation: 9/10 checks passed. 12.1s |
| 2026-06-09 03:53:44 | Phase 44 | Built catalog.namespace_variables. 2.9s |
| 2026-06-09 03:53:45 | Phase 12 | Parquet export: 50 tables (exported 1, skipped 49, empty 0, errors 0); 0.0 MB newly written. 0.9s |
| 2026-06-09 03:54:12 | Phase 13 | Validation: 10/10 checks passed. 12.5s |
| 2026-06-09 04:51:53 | Phase 39 | UBPR ratios: 393,041,241 rows, 6,567 banks, 37 periods, 2,971 concepts (XBRL from CDR bulk). 1584.1s |
| 2026-06-09 04:52:38 | Phase 44 | Built catalog.namespace_variables. 15.3s |
| 2026-06-09 04:52:57 | Phase 13 | Validation: 10/10 checks passed. 17.8s |
| 2026-06-09 05:36:20 | Phase 39 | UBPR ratios: 434,527,232 rows, 6,576 banks, 42 periods, 2,971 concepts (XBRL from CDR bulk). 1032.9s |
| 2026-06-09 05:36:57 | Phase 13 | Validation: 10/10 checks passed. 18.8s |
| 2026-06-09 06:42:18 | Phase 39 | UBPR ratios: 618,599,995 rows, 7,477 banks, 54 periods, 3,059 concepts (XBRL from CDR bulk). 2432.7s |
| 2026-06-09 06:42:44 | Phase 44 | Built catalog.namespace_variables. 5.5s |
| 2026-06-09 06:43:04 | Phase 13 | Validation: 10/10 checks passed. 19.0s |
| 2026-06-09 08:08:38 | Phase 39 | UBPR ratios: 805,554,926 rows, 8,360 banks, 66 periods, 3,092 concepts (XBRL from CDR bulk). 3663.3s |
| 2026-06-09 08:09:09 | Phase 44 | Built catalog.namespace_variables. 7.0s |
| 2026-06-09 08:09:30 | Phase 13 | Validation: 10/10 checks passed. 20.4s |
| 2026-06-09 09:42:26 | Phase 39 | UBPR ratios: 1,004,062,459 rows, 9,298 banks, 78 periods, 3,101 concepts (XBRL from CDR bulk). 4264.8s |
| 2026-06-09 09:42:51 | Phase 44 | Built catalog.namespace_variables. 7.2s |
| 2026-06-09 09:43:12 | Phase 13 | Validation: 10/10 checks passed. 21.0s |
| 2026-06-09 11:17:04 | Phase 39 | UBPR ratios: 1,207,754,536 rows, 10,194 banks, 90 periods, 3,111 concepts (XBRL from CDR bulk). 5402.5s |
| 2026-06-09 12:13:54 | Phase 39 | UBPR ratios: 1,224,921,102 rows, 10,250 banks, 91 periods, 3,112 concepts (XBRL from CDR bulk). 3368.8s |
| 2026-06-09 14:51:40 | Phase 39 | UBPR ratios: 1,251,149,050 rows, 10,250 banks, 94 periods, 3,112 concepts (XBRL from CDR bulk). 4538.5s |
| 2026-06-09 14:54:10 | Phase 44 | Built catalog.namespace_variables. 42.9s |
| 2026-06-09 14:57:04 | Phase 13 | Validation: 10/10 checks passed. 34.9s |
| 2026-06-09 23:10:17 | Phase 44 | Built catalog.namespace_variables. 14.1s |
| 2026-06-09 23:10:52 | Phase 13 | Validation: 10/10 checks passed. 23.4s |
| 2026-06-10 00:08:00 | Phase 13 | Validation: 10/10 checks passed. 24.6s |
| 2026-06-10 00:19:12 | Phase 36b | GLEIF LEI widening: id_crosswalk.lei 15,278 -> 17,713 (+2,435; lei_source='gleif'=2,435). Unambiguous normalized-name match GLEIF US/ACTIVE legal_name <-> NIC institutions. 11.7s |
| 2026-06-10 00:19:51 | Phase 13 | Validation: 10/10 checks passed. 26.5s |
| 2026-06-10 00:55:11 | Phase 27b-backfill | A7 FRED H.8 backfill: +3 series (LTDDCBW027SBOG, CASACBW027SBOG, TLADCBW027SBOG, H8B3053NFRA) via API-host fallback; fred_series 1,946 distinct. |
| 2026-06-10 00:57:36 | Phase 27b-backfill | A7 FRED H.8 backfill: +1 series (LTDDCBW027NBOG) via API-host fallback; fred_series 1,947 distinct. |
| 2026-06-10 00:58:31 | Phase 13 | Validation: 10/10 checks passed. 26.9s |
| 2026-06-10 01:14:12 | Phase 13 | Validation: 10/10 checks passed. 26.2s |
| 2026-06-12 10:17:50 | Phase 13 | Validation: 10/10 checks passed. 89.1s |
| 2026-06-12 11:07:40 | Phase 17 | dict parquet export: 7 tables (47,953 rows, 0.546 MB); SHA256SUMS + PROVENANCE refreshed. 0.3s |
| 2026-06-12 11:11:08 | Phase 13 | Validation: 11/11 checks passed. 47.1s |
| 2026-06-12 11:12:05 | Phase 13 | Validation: 11/11 checks passed. 38.8s |
| 2026-06-12 11:22:02 | Phase 13 | Validation: 11/11 checks passed. 38.6s |
| 2026-06-12 12:38:15 | Phase 13 | Validation: 11/11 checks passed. 39.4s |
| 2026-06-14 20:50:41 | Phase 45 | clean_bank_panel built: 1,114,822 rows, span 1863-2026; unit gate JPM $1.746T / SVB $209.0B / occ29 $1.80B. sha d0fb7c8dc35de828. 261.1s |
| 2026-06-14 20:57:48 | Phase 45 | clean_bank_panel built: 1,114,822 rows, span 1863-2026; unit gate JPM $1.746T / SVB $209.0B / occ29 $1.80B. sha d0fb7c8dc35de828. 241.7s |
| 2026-06-14 21:08:27 | Phase 13 | Validation: 12/12 checks passed. 154.6s |
