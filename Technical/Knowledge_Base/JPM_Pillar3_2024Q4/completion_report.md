# Extraction completion report: JPM_Pillar3_2024Q4

## Document Information
- **Document**: JPMorgan Chase & Co. Pillar 3 Regulatory Capital Disclosures
- **Period**: Quarterly period ended June 30, 2025
- **Source**: 4 PDF chunks (29 pages total)
- **Processing Date**: 2026-03-22

## Note on Document Period
The document identifier says "2024Q4" but the actual content is for the quarterly period ended **June 30, 2025** (Q2 2025). All data extracted faithfully reflects the actual document content.

## Extraction Summary

### Chunk 001 (Pages 1-8: Cover, TOC, Disclosure Map, Introduction, Regulatory Capital)
- **Body text**: JPM_Pillar3_2024Q4_chunk_001_body.md
- **Tables extracted**: 5
  - table_001: Disclosure Map (cross-reference table)
  - table_002: Components of Capital reconciliation ($356.9B equity to $320.8B total capital)
  - table_003: Components of RWA ($1,873,142M total)
  - table_004: RWA Rollforward Q1->Q2 2025
  - table_005: Capital ratio requirements and well-capitalized ratios

### Chunk 002 (Pages 7-14: Capital Adequacy, TLAC, Credit Risk, Retail/Wholesale/Counterparty)
- **Body text**: JPM_Pillar3_2024Q4_chunk_002_body.md
- **Tables extracted**: 13
  - table_001: JPMorgan Chase & Co. capital metrics (CET1 15.2%, SLR 5.9%)
  - table_002: JPMorgan Chase Bank, N.A. capital metrics (CET1 16.7%, SLR 6.4%)
  - table_003: SLR components ($5,161,360M total leverage exposure)
  - table_004: TLAC ($559.9B external TLAC, $244.9B LTD)
  - table_005: Summary of credit risk RWA ($1,320,119M)
  - table_006: Retail RWA breakdown ($223,100M)
  - table_007: Residential mortgage exposures by PD range ($250,979M EAD)
  - table_008: Qualifying revolving exposures by PD range ($524,659M EAD)
  - table_009: Other retail exposures by PD range ($82,509M EAD)
  - table_010: Wholesale credit RWA breakdown ($572,037M)
  - table_011: Wholesale exposures by PD range ($2,019,469M EAD)
  - table_012: Counterparty credit RWA breakdown ($151,002M)
  - table_013: Counterparty credit exposures by PD range ($343,767M EAD)

### Chunk 003 (Pages 15-22: Securitization, Equity Risk, Market Risk, VaR)
- **Body text**: JPM_Pillar3_2024Q4_chunk_003_body.md
- **Tables extracted**: 10
  - table_001: Securitization RWA by approach (SFA/SSFA/1250%) - excluding re-securitization
  - table_002: Re-securitization RWA by approach
  - table_003: Total securitization ($291,600M exposure, $67,062M RWA)
  - table_004: Securitization exposure by collateral type
  - table_005: Assets securitized principal balance ($118,561M JPMC + $95,202M third-party)
  - table_006: Securitization activity (6 months ended June 30, 2025)
  - table_007: Equity risk-weighted assets by risk-weight category ($79,532M exposure, $65,092M RWA)
  - table_008: Carrying value and fair value of non-covered equity ($73,962M / $81,452M)
  - table_009: Market risk RWA components ($103,928M total)
  - table_010: CIB/Firm VBM by risk type (Avg/Min/Max/Period-end)

### Chunk 004 (Pages 23-29: Market Risk Capital Models, Stress Testing, Interest Rate Risk, Operational Risk, SLR Details, Appendix)
- **Body text**: JPM_Pillar3_2024Q4_chunk_004_body.md
- **Tables extracted**: 16
  - table_001: VBM Capital ($740M RBC, $9,250M RWA)
  - table_002: SVBM statistics (CIB and Firm)
  - table_003: SVBM Capital ($1,543M RBC, $19,290M RWA)
  - table_004: IRC statistics (CIB)
  - table_005: IRC Capital ($761M RBC, $9,516M RWA)
  - table_006: CRM statistics (CIB)
  - table_007: CRM Capital ($233M RBC, $2,914M RWA)
  - table_008: Aggregate correlation trading positions (-$2,073M fair value)
  - table_009: Non-modeled specific risk ($4,818M RBC, $60,229M RWA)
  - table_010: Other charges ($219M RBC, $2,729M RWA)
  - table_011: SLR Summary (duplicate for completeness in SLR section)
  - table_012: Derivative transactions components ($377,156M total, $300,502M adjustment)
  - table_013: Repo-style transactions components ($717,301M total, $49,263M adjustment)
  - table_014: Other off-balance sheet exposures ($429,375M adjustment)
  - table_015: MDA cross-references (Form 10-K and Form 10-Q)
  - table_016: Notes to financial statements cross-references

## Totals
- **Body text files**: 4
- **Table CSV files**: 44
- **Total output files**: 48

## Key Financial Highlights (June 30, 2025)
- Total assets: $4.6 trillion
- Total stockholders' equity: $356.9 billion
- CET1 capital: $283,854 million
- Total capital: $320,809 million
- Total RWA: $1,873,142 million (Credit: $1,320,119M, Market: $103,928M, Operational: $449,095M)
- CET1 ratio: 15.2% (Basel III Advanced)
- Tier 1 ratio: 16.2%
- Total capital ratio: 17.1%
- SLR: 5.9%
- Total leverage exposure: $5,161,360 million
- External TLAC: $559.9 billion (29.7% of RWA, surplus $126.9B)
- Regulatory multiplier (VaR): 3.5
- Backtesting exceptions (2Q25): 2

## Processing Quality Notes
- All tables extracted with exact numbers from the document
- All body text narrative content captured including cross-references
- Footnotes preserved with each relevant table/section
- No content appears to have been lost or omitted
- Document charts (VBM time series, backtesting distribution) described in body text but cannot be rendered as CSV -- key data points from chart annotations were captured
