# HDARP v4.5 Completion Report: gs_bhcpr

## Document Information
- **Document**: FR BHCPR (Bank Holding Company Performance Report)
- **Entity**: Goldman Sachs Group, Inc., The
- **RSSD Number**: 2380443
- **Federal Reserve District**: 2
- **Peer Group**: 1 (Consolidated assets >= $10 billion)
- **Report Date**: September 30, 2025
- **Total Pages**: 23
- **Source Chunks**: 5 PDF files

## Processing Summary

### Chunk 1 (Pages 1-5: Cover, Summary Ratios, Income, Assets)
| Output File | Description |
|---|---|
| gs_bhcpr_chunk_001_body.md | Cover page, peer group definitions, disclaimer, table of contents, section descriptions for Summary Ratios, Income Statement, Relative Income/Margin Analysis, Non-Interest Income/Expenses, Assets |
| gs_bhcpr_chunk_001_table_001.csv | Summary Ratios (Page 1) -- 40+ metrics across 5 periods |
| gs_bhcpr_chunk_001_table_002.csv | Income Statement Revenues and Expenses (Page 2) -- all line items |
| gs_bhcpr_chunk_001_table_003.csv | Non-Interest Income and Expenses (Page 4) -- dollar amounts |
| gs_bhcpr_chunk_001_table_004.csv | Assets (Page 5) -- all line items including memoranda |

### Chunk 2 (Pages 6-10: Liabilities, Composition, Loan Mix, Liquidity, Derivatives OBS, Derivative Instruments)
| Output File | Description |
|---|---|
| gs_bhcpr_chunk_002_body.md | Section descriptions for Liabilities/Capital, Percent Composition, Loan Mix/Concentrations, Liquidity/Funding, Derivatives/OBS Transactions |
| gs_bhcpr_chunk_002_table_001.csv | Liabilities and Changes in Capital (Page 6) -- all line items |
| gs_bhcpr_chunk_002_table_002.csv | Derivatives and Off-Balance-Sheet Transactions (Page 9) -- notional amounts |
| gs_bhcpr_chunk_002_table_003.csv | Derivative Instruments detail (Page 10) -- full breakdown |

### Chunk 3 (Pages 11-14: Derivatives Analysis, Allowance/Credit Losses, Past Due/Nonaccrual, Regulatory Capital)
| Output File | Description |
|---|---|
| gs_bhcpr_chunk_003_body.md | Section descriptions for Derivatives Analysis, Allowance/Net Credit Losses, Past Due/Nonaccrual Assets (13, 13A, 13B), Regulatory Capital |
| gs_bhcpr_chunk_003_table_001.csv | Derivatives Analysis (Page 11) -- percent of notional amount, Tier 1 capital ratios |
| gs_bhcpr_chunk_003_table_002.csv | Allowance and Net Credit Losses (Page 12) -- dollar amounts and analysis ratios |
| gs_bhcpr_chunk_003_table_003.csv | Past Due and Nonaccrual Assets (Page 13) -- dollar amounts and percent ratios |
| gs_bhcpr_chunk_003_table_004.csv | Regulatory Capital Components and Ratios (Page 14) -- CET1, AT1, T2, total capital, RWA, capital ratios |

### Chunk 4 (Pages 15-20: Insurance/Broker-Dealer, Foreign Activities, Securitization Parts 1-3, Parent Company Income)
| Output File | Description |
|---|---|
| gs_bhcpr_chunk_004_body.md | Section descriptions for Insurance/Broker-Dealer Activities, Foreign Activities, Servicing/Securitization Parts 1-3, Parent Company Income Statement |
| gs_bhcpr_chunk_004_table_001.csv | Insurance and Broker-Dealer Activities (Page 15) -- dollar amounts and analysis ratios |
| gs_bhcpr_chunk_004_table_002.csv | Foreign Activities (Page 16) -- foreign loans, deposits, analysis ratios |
| gs_bhcpr_chunk_004_table_003.csv | Servicing/Securitization Part 1 (Page 17) -- securitization activity, retained credit exposure |
| gs_bhcpr_chunk_004_table_004.csv | Servicing/Securitization Part 2 (Page 18) -- past due and net losses on securitized assets |
| gs_bhcpr_chunk_004_table_005.csv | Parent Company Income Statement (Page 20) -- operating income/expenses, net income |

### Chunk 5 (Pages 21-23: Parent Company Balance Sheet, Parent Company Analysis Parts 1-2)
| Output File | Description |
|---|---|
| gs_bhcpr_chunk_005_body.md | Section descriptions for Parent Company Balance Sheet, Parent Company Analysis Parts 1 and 2 |
| gs_bhcpr_chunk_005_table_001.csv | Parent Company Balance Sheet (Page 21) -- assets, liabilities, equity capital, memoranda |

## Output Totals
- **Body markdown files**: 5
- **CSV table files**: 18
- **Total output files**: 23 (plus this completion report)

## Notes on Data Structure

### Report Format
The FR BHCPR presents data in a standardized format with five reporting periods (09/30/2025, 09/30/2024, 12/31/2024, 12/31/2023, 12/31/2022). Most pages include:
- **Dollar amount tables**: Raw values in thousands
- **Ratio sections**: BHC value, Peer Group 1 median, and percentile ranking
- **Percent change**: 1-year and 5-year growth rates (on select pages)

### Pages Not Separately Extracted as CSV
- **Page 3 (Relative Income Statement/Margin Analysis)**: Ratio-only page with BHC/Peer/Pct format; described in chunk 1 body
- **Pages 7/7A (Percent Composition of Assets/Loan Mix)**: Ratio-only pages; described in chunk 2 body
- **Page 8 (Liquidity and Funding)**: Ratio-only page; described in chunk 2 body
- **Pages 13A/13B (Past Due and Nonaccrual Loans detail)**: Ratio-only pages with BHC/Peer/Pct by loan type; described in chunk 3 body
- **Page 19 (Securitization Part 3)**: Ratio-only page; described in chunk 4 body
- **Pages 22-23 (Parent Company Analysis Parts 1-2)**: Ratio-only pages with BHC/Peer/Pct; described in chunk 5 body

### Key Financial Highlights (09/30/2025)
- Total assets: $1,807,982,000 thousand ($1.808 trillion)
- Total equity capital: $124,402,000 thousand ($124.4 billion)
- Net income (YTD): $12,559,000 thousand ($12.6 billion)
- CET1 ratio (column A): 14.34%
- Tier 1 leverage ratio: 6.59%
- Total risk-weighted assets: $723,406,000 thousand ($723.4 billion)
- Net assets of broker-dealer subsidiaries: $1,038,727,000 thousand ($1.039 trillion)
- Derivative notional amount: $44,652,459,000 thousand ($44.7 trillion)

## Processing Status
- **Status**: COMPLETE
- **All 5 chunks processed**: Yes
- **Errors**: None
