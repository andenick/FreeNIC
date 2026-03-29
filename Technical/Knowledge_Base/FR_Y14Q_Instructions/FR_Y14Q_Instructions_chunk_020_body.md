# FR Y-14Q Instructions -- Schedule H.1 Corporate Loan Data Fields (Fields 52-80)

## H.1 - Corporate Loan Data Schedule: Field Specifications (Part 3) -- Obligor Financial Data Section

This chunk contains the field specification table for Fields 52-80 of the H.1 Corporate Loan Data Schedule. These fields comprise the **Obligor Financial Data** section, which collects data related to the financial health of the obligor or the entity that is the primary source of repayment for the loan.

### Exclusions for Obligor Financial Data Section

Fields 52-82 should be left blank for loans with:
- Obligor domiciled outside the US
- Obligor with NAICS code beginning with 52, 5312, or 551111
- Obligor that is a nonprofit or government entity
- Obligor that is a Natural Person

### Fields Covered

| Field Range | Category |
|---|---|
| Fields 52-53 | Reporting Dates (Date of Financials, Date of Last Audit) |
| Fields 54-55 | Revenue (Net Sales Current TTM, Net Sales Prior Year TTM) |
| Fields 56-60 | Income Statement (Operating Income, Depreciation & Amortization, Interest Expense, Net Income Current, Net Income Prior Year) |
| Fields 61-62 | Liquid Assets (Cash & Marketable Securities, Accounts Receivable Current) |
| Fields 63-65 | Working Capital Assets (A/R Prior Year, Inventory Current, Inventory Prior Year) |
| Fields 66-67 | Current Assets (Current Assets Current, Current Assets Prior Year) |
| Fields 68-69 | Long-Term Assets (Tangible Assets, Fixed Assets net of depreciation) |
| Fields 70-71 | Total Assets (Total Assets Current, Total Assets Prior Year) |
| Fields 72-73 | Accounts Payable (A/P Current, A/P Prior Year) |
| Fields 74-75 | Debt (Short Term Debt, Current Maturities of Long Term Debt) |
| Fields 76-77 | Current Liabilities (Current Liabilities Current, Current Liabilities Prior Year) |
| Fields 78-80 | Other Liabilities (Long Term Debt, Minority Interest, Total Liabilities) |

### Reporting Period Rules

- **TTM Fields** (54, 56, 57, 58, 59, 82): Report for trailing twelve month period ended on Date of Financials (Field 52). If insufficient TTM data, use underwritten annual information.
- **Prior Year Fields** (55, 60): Report for TTM period ended one year prior to Field 52 date. If insufficient, use underwritten annual information.
- **Balance Sheet Fields**: Report as of Date of Financials (Field 52) for current; one year prior for prior year fields.

### Data Standards

- All financial data reported in accordance with GAAP
- Use financial spreading system definitions in accordance with credit policy
- Populate with most recent financial statement data available as of report date
- Not bound by data used in most recent formal rating review
- All amounts reported as rounded whole dollar amounts, no formatting characters

*See companion CSV file: FR_Y14Q_Instructions_chunk_020_table_001.csv for complete field specifications.*
