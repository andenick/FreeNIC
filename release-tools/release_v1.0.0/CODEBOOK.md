# FreeNIC v1.0.0 — Codebook Index

Release 1.0.0 (2026-07-14); warehouse build 1.4, data vintage 2026Q1.
61 released tables. Per-table column codebooks in `codebook/`.
Descriptions come from warehouse column comments (COMMENT ON COLUMN) plus the FFIEC MDRM / variable-crosswalk dictionaries (82 of 893 columns = 9.2%); empty where no dictionary description exists (never invented).

| table | codebook | rows | cols | cols w/ description | coverage span | description |
|---|---|---:|---:|---:|---|---|
| bank_failures | codebook/bank_failures.csv | 4,115 | 16 | 0 |  |  |
| bhc_ownership | codebook/bhc_ownership.csv | 36,668 | 14 | 0 |  |  |
| bhcf_filings | codebook/bhcf_filings.csv | 208,147,772 | 5 | 2 | period_end: 1986-09-30 .. 2025-12-31 | Bank-HOLDING-COMPANY consolidated FR Y-9C financials (long/EAV). |
| branches | codebook/branches.csv | 173,250 | 10 | 0 |  |  |
| call_report_filings | codebook/call_report_filings.csv | 1,917,025,977 | 6 | 2 | period_end: 1976-03-31 .. 2026-03-31 | Individual-bank FFIEC Call Report filings (long/EAV). |
| catalog_data_sources | codebook/catalog_data_sources.csv | 779 | 11 | 0 |  |  |
| catalog_entity_coverage | codebook/catalog_entity_coverage.csv | 141,333 | 5 | 0 |  |  |
| catalog_filing_coverage | codebook/catalog_filing_coverage.csv | 53,580 | 7 | 0 | period_end: 1782-01-01 .. 2026-05-29 |  |
| catalog_namespace_variables | codebook/catalog_namespace_variables.csv | 6,754 | 6 | 0 |  |  |
| catalog_schema_evolution | codebook/catalog_schema_evolution.csv | 13,446 | 4 | 0 |  |  |
| catalog_variables | codebook/catalog_variables.csv | 13,446 | 14 | 0 |  |  |
| cdr_unrealized_losses | codebook/cdr_unrealized_losses.csv | 46,929 | 16 | 0 | period_end: 2019-12-31 00:00:00 .. 2025-12-31 00:00:00 |  |
| clean_bank_panel | codebook/clean_bank_panel.csv | 1,114,822 | 47 | 21 | call_date: 1863-11-28 .. 2026-03-31 | CANONICAL per-bank dollar-LEVEL panel (from-raw, nominal + CPI-real). |
| crsp_mapping | codebook/crsp_mapping.csv | 18,908 | 7 | 0 |  |  |
| dfast_results | codebook/dfast_results.csv | 28,231 | 8 | 0 | year: 2013 .. 2025 |  |
| dict_crosswalk | codebook/dict_crosswalk.csv | 2,057 | 16 | 0 |  |  |
| dict_edit_history | codebook/dict_edit_history.csv | 15,622 | 8 | 0 |  |  |
| dict_meta | codebook/dict_meta.csv | 3 | 2 | 0 |  |  |
| dict_relationships | codebook/dict_relationships.csv | 7,539 | 14 | 0 |  |  |
| dict_schedule_lineitems | codebook/dict_schedule_lineitems.csv | 3,198 | 9 | 0 |  |  |
| dict_ubpr_concepts | codebook/dict_ubpr_concepts.csv | 4,099 | 8 | 0 |  |  |
| dict_variable_access_map | codebook/dict_variable_access_map.csv | 15,435 | 5 | 0 |  |  |
| entity_xref | codebook/entity_xref.csv | 234,462 | 3 | 0 |  | Canonical RSSD identity universe + source coverage. |
| fdic_financials | codebook/fdic_financials.csv | 69,455,560 | 6 | 2 | period_end: 1984-03-31 .. 2026-03-31 | FDIC SDI bank-level financials (long/EAV). |
| fdic_history | codebook/fdic_history.csv | 582,628 | 11 | 0 | effective_date: 1782-01-01 .. 2026-05-27 |  |
| fdic_sdi_features | codebook/fdic_sdi_features.csv | 413,130 | 17 | 1 | year: 1984 .. 2025 | Engineered bank-year ratios + failure flags (from fdic_financials). |
| fdic_sod | codebook/fdic_sod.csv | 2,815,984 | 25 | 0 | year: 1994 .. 2025 |  |
| filing_metadata | codebook/filing_metadata.csv | 359 | 6 | 0 | period_end: 1976-03-31 .. 2026-03-31 |  |
| fred_series | codebook/fred_series.csv | 1,345,207 | 4 | 0 |  |  |
| freenic_manifest | codebook/freenic_manifest.csv | 110 | 11 | 0 |  | Self-describing warehouse manifest (one row per table/view). |
| hmda_summary | codebook/hmda_summary.csv | 208,302 | 10 | 0 |  |  |
| id_crosswalk | codebook/id_crosswalk.csv | 103,037 | 14 | 0 |  | Keystone identity crosswalk across identifier systems. |
| institution_attributes | codebook/institution_attributes.csv | 217,210 | 14 | 0 |  |  |
| institutions | codebook/institutions.csv | 217,210 | 15 | 0 |  | Master entity table (NIC): the rssd_id join key. |
| long_bank_aggregates_1863_2026 | codebook/long_bank_aggregates_1863_2026.csv | 810 | 6 | 0 | year: 1863 .. 2026 | Replicated 163-year national/insured/commercial bank-aggregate spine: long form year x met |
| luck_call_reports | codebook/luck_call_reports.csv | 37,753,719 | 5 | 2 | period_end: 1959-12-31 .. 2023-03-31 | Luck/FRBNY historical Call reconstruction 1959-1975 (long/EAV). |
| mdrm | codebook/mdrm.csv | 87,351 | 11 | 0 |  | FFIEC MDRM label dictionary for variable codes. |
| ncua_5300 | codebook/ncua_5300.csv | 1,180,127,221 | 6 | 2 | period_end: 1994-03-31 .. 2025-12-31 | NCUA credit-union 5300 call reports (long/EAV). |
| ncua_cu_directory | codebook/ncua_cu_directory.csv | 851,288 | 7 | 0 | period_end: 1994-03-31 .. 2025-12-31 |  |
| nic_attributes_ext | codebook/nic_attributes_ext.csv | 220,092 | 36 | 0 |  |  |
| nic_entity_identifiers | codebook/nic_entity_identifiers.csv | 102,932 | 13 | 0 |  |  |
| occ_historical | codebook/occ_historical.csv | 17,775,763 | 5 | 2 | report_date: 1863-11-28 .. 1941-12-31 | OCC national-bank balance sheets 1863-1941 (long/EAV). |
| occ_historical_clv | codebook/occ_historical_clv.csv | 7,986,823 | 5 | 2 | report_date: 1863-11-28 .. 1941-12-31 | Typed view: occ_historical WHERE source='occ_historical_clv' (finhist, 1863-1941). |
| pillar3_disclosures | codebook/pillar3_disclosures.csv | 8,653 | 9 | 0 | period_end: 2024-03-31 .. 2025-09-30 |  |
| relationships | codebook/relationships.csv | 286,223 | 10 | 0 |  |  |
| reporting_forms | codebook/reporting_forms.csv | 180 | 3 | 0 |  |  |
| robin_crosswalk | codebook/robin_crosswalk.csv | 14,286 | 19 | 0 |  |  |
| robin_deposits_historical | codebook/robin_deposits_historical.csv | 2,961 | 79 | 12 | call_date: 1864-11-25 .. 1935-12-31 |  |
| robin_deposits_modern | codebook/robin_deposits_modern.csv | 547 | 48 | 12 | call_date: 1993-04-01 .. 2023-04-01 |  |
| robin_panel_base | codebook/robin_panel_base.csv | 2,867,936 | 157 | 18 | call_date: 1863-11-28 .. 2024-10-01 | Base table behind the guarded robin_panel view (CLV 'Failing Banks' verbatim import). |
| sec_cik_crosswalk | codebook/sec_cik_crosswalk.csv | 371 | 7 | 0 |  |  |
| sector_groupings | codebook/sector_groupings.csv | 16,548 | 5 | 0 |  |  |
| stress_scenarios | codebook/stress_scenarios.csv | 200 | 20 | 0 |  |  |
| stress_scenarios_domestic | codebook/stress_scenarios_domestic.csv | 226 | 19 | 0 |  |  |
| stress_scenarios_international | codebook/stress_scenarios_international.csv | 226 | 15 | 0 |  |  |
| transformations | codebook/transformations.csv | 58,935 | 6 | 0 |  |  |
| ubpr_peer_rank | codebook/ubpr_peer_rank.csv | 250,012,503 | 6 | 0 |  |  |
| ubpr_peer_stats | codebook/ubpr_peer_stats.csv | 22,067,752 | 6 | 0 |  |  |
| ubpr_ratios | codebook/ubpr_ratios.csv | 1,251,149,050 | 5 | 2 | period_end: 2002-12-31 .. 2026-03-31 | FFIEC UBPR standardized ratios + dollar items (long/EAV). |
| variable_crosswalk | codebook/variable_crosswalk.csv | 76 | 6 | 0 |  | Cross-source variable -> standardized concept mapping. |
| y15_systemic_indicators | codebook/y15_systemic_indicators.csv | 22,481 | 5 | 2 | period_end: 2020-12-31 .. 2024-12-31 | FR Y-15 systemic-risk indicators (G-SIB scoring) (long/EAV). |
