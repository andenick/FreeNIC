# Extraction completion report: gs_101

## Document Information
- **Document ID**: gs_101
- **Title**: FFIEC 101 -- Regulatory Capital Reporting for Institutions Subject to the Advanced Capital Adequacy Framework
- **Issuing Bodies**: Board of Governors of the Federal Reserve System, Federal Deposit Insurance Corporation, Office of the Comptroller of the Currency (via FFIEC)
- **Report Date**: September 30, 2025
- **Total Pages**: 38
- **Chunks Processed**: 5

## Processing Summary

### Chunk 1 (Pages 1-8): Cover Page, Schedule A, Schedule B (pp. B-1 to B-2)
- **Body**: Cover page (legal authority, attestation requirements, filing instructions, burden estimate), Schedule A items 1-90 (CET1, AT1, T2 capital; ratios; thresholds; SLR Tables 1-2), Schedule B summary structure (items 1-22)
- **Tables**: 6 CSV files
  - Table 001: Schedule A Page A-1 (CET1 capital items 1-29 with Goldman Sachs data)
  - Table 002: Schedule A Page A-2 (AT1, T1, T2 capital items 30-60 with data)
  - Table 003: Schedule A Page A-3 (ratios, thresholds, memoranda items 61-90 with data)
  - Table 004: SLR Table 1 (total leverage exposure items 1.1-1.8 with data)
  - Table 005: SLR Table 2 (supplementary leverage ratio items 2.1-2.23 with data)
  - Table 006: Schedule B summary (all exposure categories items 1-22 with data)

### Chunk 2 (Pages 9-16): Schedule B (p. B-3), Schedules C, D, E, F, G
- **Body**: Schedule B items 23-36 (equity, other assets, totals), Schedules C-G structure (wholesale PD range tables for Corporate, Bank, Sovereign, IPRE, HVCRE)
- **Tables**: 2 CSV files
  - Table 001: Schedule B page B-3 (items 23-36 MDRM grid)
  - Table 002: Schedule C corporate wholesale MDRM grid (12 columns x 13 PD ranges + memoranda)

### Chunk 3 (Pages 17-24): Schedules H, I, J, K
- **Body**: Schedules H-J structure (wholesale margin loans/repo/OTC derivatives with and without cross-product netting), Schedule K structure (retail mortgage closed-end first lien)
- **Tables**: 4 CSV files
  - Table 001: Schedule H MDRM grid (12 columns, dual EAD/LGD structure)
  - Table 002: Schedule I MDRM grid (with EAD adjustment method memoranda)
  - Table 003: Schedule J MDRM grid (OTC derivatives)
  - Table 004: Schedule K MDRM grid (16 columns including LTV buckets)

### Chunk 4 (Pages 25-32): Schedules L, M, N, O
- **Body**: Schedules L-M structure (retail mortgage junior lien and revolving), Schedules N-O structure (qualifying revolving and other retail)
- **Tables**: 3 CSV files
  - Table 001: Schedule L MDRM grid (junior lien, 16 columns)
  - Table 002: Schedule N MDRM grid (qualifying revolving, 10 columns)
  - Table 003: Schedule O MDRM grid (other retail, 10 columns)

### Chunk 5 (Pages 33-38): Schedules P, Q, R, S
- **Body**: Schedule P (securitization exposures), Q (cleared transactions), R (equity exposures with three approach methods), S (operational risk -- public and confidential items)
- **Tables**: 4 CSV files
  - Table 001: Schedule P (securitizations vs resecuritizations, 6 columns)
  - Table 002: Schedule Q (cleared transactions, 4 columns)
  - Table 003: Schedule R (equity exposures across SRWA/Full IMA/Partial IMA, 26 items)
  - Table 004: Schedule S (operational risk, 24 items with MDRM codes)

## Output Files Summary

| File | Type | Description |
|------|------|-------------|
| gs_101_chunk_001_body.md | Body | Cover page, Schedule A (all items), SLR Tables, Schedule B summary |
| gs_101_chunk_001_table_001.csv | Table | Schedule A page A-1: CET1 capital (items 1-29) |
| gs_101_chunk_001_table_002.csv | Table | Schedule A page A-2: AT1/T1/T2 capital (items 30-60) |
| gs_101_chunk_001_table_003.csv | Table | Schedule A page A-3: Ratios/thresholds/memoranda (items 61-90) |
| gs_101_chunk_001_table_004.csv | Table | SLR Table 1: Leverage exposure summary |
| gs_101_chunk_001_table_005.csv | Table | SLR Table 2: Supplementary leverage ratio |
| gs_101_chunk_001_table_006.csv | Table | Schedule B: Summary RWA (items 1-22) |
| gs_101_chunk_002_body.md | Body | Schedule B continued, Schedules C-G |
| gs_101_chunk_002_table_001.csv | Table | Schedule B page B-3 (items 23-36) |
| gs_101_chunk_002_table_002.csv | Table | Schedule C: Corporate wholesale MDRM grid |
| gs_101_chunk_003_body.md | Body | Schedules H, I, J, K |
| gs_101_chunk_003_table_001.csv | Table | Schedule H: Cross-product netting MDRM grid |
| gs_101_chunk_003_table_002.csv | Table | Schedule I: Margin loans/repos no cross-product netting |
| gs_101_chunk_003_table_003.csv | Table | Schedule J: OTC derivatives no cross-product netting |
| gs_101_chunk_003_table_004.csv | Table | Schedule K: Residential mortgage first lien MDRM grid |
| gs_101_chunk_004_body.md | Body | Schedules L, M, N, O |
| gs_101_chunk_004_table_001.csv | Table | Schedule L: Junior lien MDRM grid |
| gs_101_chunk_004_table_002.csv | Table | Schedule N: Qualifying revolving MDRM grid |
| gs_101_chunk_004_table_003.csv | Table | Schedule O: Other retail MDRM grid |
| gs_101_chunk_005_body.md | Body | Schedules P, Q, R, S |
| gs_101_chunk_005_table_001.csv | Table | Schedule P: Securitization exposures |
| gs_101_chunk_005_table_002.csv | Table | Schedule Q: Cleared transactions |
| gs_101_chunk_005_table_003.csv | Table | Schedule R: Equity exposures |
| gs_101_chunk_005_table_004.csv | Table | Schedule S: Operational risk |

## Key Data Points (from Goldman Sachs Example Filing, RSSD ID: 2380443)

- Common Equity Tier 1 Capital: $103,769,000 thousand
- Tier 1 Capital: $118,515,000 thousand
- Total Capital: $128,679,000 thousand
- Total Risk-Weighted Assets: $687,426,000 thousand
- CET1 Ratio: 15.0953%
- Tier 1 Ratio: 17.2404%
- Total Capital Ratio: 18.7190%
- Supplementary Leverage Ratio: 5.2316%
- Total Leverage Exposure: $2,265,348,000 thousand

## Schedules Inventory

| Schedule | Title | Exposure Type |
|----------|-------|---------------|
| A | Advanced Approaches Regulatory Capital | Capital adequacy |
| A (SLR) | Supplementary Leverage Ratio Tables 1-2 | Leverage |
| B | Summary Risk-Weighted Asset Information | All exposure types |
| C | Wholesale Exposure: Corporate | Wholesale |
| D | Wholesale Exposure: Bank | Wholesale |
| E | Wholesale Exposure: Sovereign | Wholesale |
| F | Wholesale Exposure: IPRE | Wholesale |
| G | Wholesale Exposure: HVCRE | Wholesale |
| H | Wholesale Exposure: Margin Loans/Repos/OTC with Cross-Product Netting | Wholesale |
| I | Wholesale Exposure: Margin Loans/Repos No Cross-Product Netting | Wholesale |
| J | Wholesale Exposure: OTC Derivatives No Cross-Product Netting | Wholesale |
| K | Retail Exposure: Residential Mortgage Closed-End First Lien | Retail |
| L | Retail Exposure: Residential Mortgage Closed-End Junior Lien | Retail |
| M | Retail Exposure: Residential Mortgage Revolving | Retail |
| N | Retail Exposure: Qualifying Revolving | Retail |
| O | Retail Exposure: Other Retail | Retail |
| P | Securitization Exposures | Securitization |
| Q | Cleared Transactions | Cleared |
| R | Equity Exposures | Equity |
| S | Operational Risk | Operational |

## Processing Notes
- Document contains both blank form templates and a completed example filing (Goldman Sachs Group, Inc.)
- All MDRM codes extracted and mapped to line items
- Goldman Sachs data values extracted for Schedule A, SLR Tables, and Schedule B summary
- Schedules C through S are template forms with MDRM code grids (no filled data visible in the template pages)
- All 38 pages across 5 chunks fully processed
- Processing date: 2026-03-22
