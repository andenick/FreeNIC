# FR Y-14Q Instructions -- Schedule H.1 Corporate Loan Data Fields (Fields 1-27)

## H.1 - Corporate Loan Data Schedule: Field Specifications (Part 1)

This chunk contains the field specification table for the first 27 fields of the H.1 Corporate Loan Data Schedule. These fields cover the **Loan and Obligor Description** section, including obligor identification, geographic information, industry classification, risk rating, credit facility identifiers, dates, facility type and purpose, exposure amounts, FR Y-9C line mapping, and line of business.

### Fields Covered

| Field Range | Category |
|---|---|
| Fields 1-7 | Obligor Identification (Customer ID, Internal ID, Original Internal ID, Obligor Name, City, Country, Zip Code) |
| Fields 8-9 | Industry Classification (NAICS/SIC/GICS Code and Type) |
| Field 10 | Internal Risk Rating (PD rating) |
| Fields 11-14 | External Identifiers (TIN, Stock Exchange, Ticker Symbol, CUSIP) |
| Fields 15-16 | Credit Facility Identifiers (Internal Credit Facility ID, Original Internal Credit Facility ID) |
| Field 17 | DO NOT USE |
| Fields 18-19 | Dates (Origination Date, Maturity Date) |
| Fields 20-23 | Facility Type and Purpose (Credit Facility Type/Purpose with 20 type codes and 31 purpose codes) |
| Fields 24-25 | Exposure Amounts (Committed Exposure Global, Utilized Exposure Global) |
| Fields 26-27 | Classification (Line Reported on FR Y-9C with 11 HC-C categories, Line of Business) |

### Key Data Points

- **Data Format**: XML file, one record per active loan, no quotation marks as text identifiers
- **Reporting Level**: Credit facility level (not individual loan/draw level)
- **Currency**: All amounts in US dollars
- **Date Format**: yyyy-mm-dd (for datetime XSD fields, append T00:00:00)
- **Demand Loans**: Use maturity date '9999-01-01'
- **20 Credit Facility Types**: From 0 (Other) through 19 (Commitment to Commit), mirroring Shared National Credit reporting
- **31 Credit Facility Purposes**: From 0 (Other) through 30 (Capital Call Subscription), codes 31-33 marked DO NOT USE

*See companion CSV file: FR_Y14Q_Instructions_chunk_018_table_001.csv for complete field specifications.*
