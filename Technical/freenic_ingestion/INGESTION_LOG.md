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
| 2026-03-24 21:40:31 | Phase 28 | Robin panel: 2,867,936 + deposits: 3,508. 42.7s |
| 2026-03-24 21:41:01 | Phase 29 | Volcker catalogs: crosswalk=14,286, hierarchy=36,668, sectors=16,548. 1.6s |
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
