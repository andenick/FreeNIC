# FR Y-14Q Instructions -- Schedule H.1 Corporate Loan Data Fields (Fields 28-51)

## H.1 - Corporate Loan Data Schedule: Field Specifications (Part 2)

This chunk contains the field specification table for Fields 28-51 of the H.1 Corporate Loan Data Schedule. These fields cover the remainder of the **Loan and Obligor Description** section, including charge-off history, delinquency status, participation/syndication information, collateral and lien details, interest rate characteristics, tax status, guarantor information, and the primary source of repayment entity identification.

### Fields Covered

| Field Range | Category |
|---|---|
| Field 28 | Cumulative Charge-offs |
| Fields 29-31 | DO NOT USE |
| Fields 32-33 | Delinquency Status (Days Past Due, Non-Accrual Date) |
| Field 34 | Participation/Syndication Flag (5 options including Shared National Credit) |
| Fields 35-36 | Collateral (Lien Position with 4 options, Security Type with 7 options) |
| Fields 37-42 | Interest Rate Characteristics (Variability, Rate, Index including SOFR, Spread, Ceiling, Floor) |
| Field 43 | Interest Income Tax Status (Taxable/Tax Exempt) |
| Fields 44-48 | Guarantor Information (Flag with 4 options, Internal ID, Name, TIN, Internal Risk Rating) |
| Fields 49-51 | Primary Source of Repayment Entity (Entity Internal ID, Name, Internal Risk Rating) |

### Key Interest Rate Indices (Field 39)

| Code | Index |
|---|---|
| 1 | LIBOR |
| 2 | PRIME or Base |
| 3 | Treasury Index |
| 4 | Other |
| 5 | Not applicable (Fixed or entirely fee based) |
| 6 | Mixed |
| 7 | SOFR |

### Guarantor Flag Options (Field 44)

| Code | Description |
|---|---|
| 1 | Full guarantee (non-US Government Agency) |
| 2 | Partial guarantee (includes partial US Government Agency) |
| 3 | Full U.S. Government Agency guarantee |
| 4 | No guarantee |

*See companion CSV file: FR_Y14Q_Instructions_chunk_019_table_001.csv for complete field specifications.*
