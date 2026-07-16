# Reconstruction validation report (combined)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715

| era | era_group | key | matched | match_share | unexplained_share | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 1976_2026 | MODC | `('id_rssd', 'period_end')` | 38469955 | 96.4338% | 2.2258% | **FAIL** |
| 1959_1975 | MODL | `('id_rssd', 'period_end')` | 7468243 | 99.9753% | 0.0247% | **PASS** |
| finhist | HIST | `('bank_id', 'year')` | 2624703 | 99.7061% | 0.0172% | **PASS** |

## Overall: NOT ALL ERAS PASS

### 1976_2026 boundary

1976-2026 is a TRUE independent re-derivation from Fed-direct raw MDRM (`call_report_filings`, Chicago Fed + FFIEC CDR). The `securities` series carries a documented ~94% public-data ceiling pre-1994 (the raw-MDRM build lives in the un-shipped `3-create-variables.do`); those cells are pre-registered NOT-DERIVABLE, reported honestly and never imputed (SPEC §0, §2.6).

### 1959_1975 boundary

1959Q4-1975Q4 is a DERIVATION-LAYER reconstruction: their digitized `.dta` is the only machine source, and our open code re-runs their documented 04/05/07 method. Because we run their formula on their input, near-perfect agreement is the bar (gate 99.9%). No step fabricates a value (SPEC §0).

### finhist boundary

1863-1941 (finhist) is a DERIVATION-LAYER reconstruction from `historical-call.dta` (their OCC OCR) to the published derivation. The OCR itself is NOT-DERIVABLE (physical archives); 1942-1958 is a genuine gap, kept absent, never synthetically filled (SPEC §0).
