# FR Y-14Q Instructions -- Chunk 026

## Schedule H.2 Corporate Loan Data Fields (continued): Fields 68-72

### Field 68 -- Committed Exposure Global Fair Value

For held for sale loans and loans accounted for under a fair value option, report the fair value of the entire credit facility.

If not held for sale or accounted for under a fair value option, report 'NA'.

**Allowable Values:** Rounded whole dollar amount, e.g.: 20000000. Supply numeric values without any non-numeric formatting (no dollar sign, commas or decimal). For negative values use a negative sign '-', not parentheses (). If not held for sale or accounted for under a fair value option, report 'NA'.

**Mandatory/Optional:** Mandatory

### Field 69 -- Outstanding Balance Fair Value

For held for sale loans and loans accounted for under a fair value option, report the fair value of the outstanding funded exposure.

If not held for sale or accounted for under a fair value option, report 'NA'.

**Allowable Values:** Rounded whole dollar amount, e.g.: 20000000. Supply numeric values without any non-numeric formatting (no dollar sign, commas or decimal). For negative values use a negative sign '-', not parentheses (). If not held for sale or accounted for under a fair value option, report 'NA'.

**Mandatory/Optional:** Mandatory

### Field 70 -- DO NOT USE

### Field 71 -- DO NOT USE

### Field 72 -- Obligor LEI (ObligorLEI)

Report the Legal Entity Identifier (LEI) of the obligor identified in Field 2, if available. A LEI is a 20 character alphanumeric code that uniquely identifies legally distinct entities that engage in financial transactions. LEIs are issued by Local Operating Units (LOUs) of the Global LEI System. If LEI does not apply, enter 'NA'.

**Allowable Values:** Must be a valid 20 character alphanumeric LEI issued by a LOU of the Global LEI System, or 'NA'.

**Mandatory/Optional:** Mandatory

---

## H.3 -- Line of Business Schedule

The Line of Business schedule collects the universe of lines of business as reported on schedule H.1 and H.2 along with a free text description.

### A. Data Format

Data should be provided in a single extensible markup language file (.xml). No quotation marks should be used as text identifiers. Do not provide a header row or a row count. This file will contain one record per line of business.

### B. Line of Business Data Fields

The table on the following pages shows the fields that should be contained in the submission file. Report all fields with data as of the report date.

#### Field 1 -- Line of Business (LineOfBusinessName)

Provide the name of the internal line of business.

**Allowable Values:** Free text indicating the internal line of business. For example: Private Banking, Corporate Banking, Asset-Based Lending, etc. Collectively, Line of Business defines the set of allowable values for Field 27 on Schedule H.1 and Field 22 on Schedule H.2.

#### Field 2 -- Line of Business Description (LineOfBusinessDescription)

Provide a brief description of the internal line of business.

**Allowable Values:** Free text describing the internal line of business.

---

## H.4 -- Internal Risk Rating Schedule

The Internal Risk Rating schedule collects the universe of internal risk ratings as reported on schedule H.1 and H.2 along with a free text description.

### A. Data Format

Data should be provided in a single extensible markup language file (.xml). No quotation marks should be used as text identifiers. Do not provide a header row or a row count. This file will contain one record per internal risk rating.

### B. Internal Risk Rating Data Fields

The table on the following pages shows the fields that should be contained in the submission file. Report all fields with data as of the report date.

#### Field 1 -- Internal Risk Rating (InternalRating)

Report each rating grade used in the reporting entity's internal risk rating system.

**Allowable Values:** Free text indicating the internal risk rating grade. Collectively, Internal Risk Rating defines the set of allowable values for Field 10 "Obligor Internal Risk Rating" on Schedule H.1 and the portion of Field 15 "Internal Rating" associated with the internal risk rating code on Schedule H.2.

#### Field 2 -- Internal Risk Rating Description (InternalRatingDescription)

Provide a brief description of the internal risk rating.

**Allowable Values:** Free text describing the internal risk rating.

#### Field 3 -- Minimum Probability of Default (MinimumPD)

Provide the minimum probability of default associated with the Internal Risk Rating reported in Field 1.

Optionally, if the Internal Risk Rating is not reported on H.1 or H.2 during the reporting quarter, report 'NA.'

**Allowable Values:** Express as a decimal to 7 decimal places, e.g., 50% is 0.5000000. Use decimal format; do not use scientific notation. Optionally, if the Internal Risk Rating is not reported on H.1 or H.2 during the reporting quarter, report 'NA.'

#### Field 4 -- Maximum Probability of Default (MaximumPD)

Provide the maximum probability of default associated with the Internal Risk Rating reported in Field 1.

Optionally, if the Internal Risk Rating is not reported on H.1 or H.2 during the reporting quarter, report 'NA.'

**Allowable Values:** Express as a decimal to 7 decimal places, e.g., 50% is 0.5000000. Use decimal format; do not use scientific notation. Optionally, if the Internal Risk Rating is not reported on H.1 or H.2 during the reporting quarter, report 'NA.'

#### Field 5 -- PD Calculation Method

Indicate the calculation method used to determine the associated probabilities of default reported in Fields 3 and 4.

**Allowable Values:**
1. Through the cycle
2. Point in time
3. Hybrid

---

## Schedule J -- Retail Fair Value Option/Held for Sale (FVO/HFS)

The Fair Value Option/Held for Sale (FVO/HFS) schedule collects information on retail loans and leases that are classified as either (1) Held for Sale (HFS) or (2) Held for Investment (HFI) under the Fair Value Option (FVO). The loan population is limited to retail loans and leases.

For purposes of this schedule, retail loans and leases include credit card loans, first lien closed-end 1-4 family residential loans and leases, home equity loans and leases, student loans, auto loans and leases, and other consumer loans and leases (refer to the instructions for the respective FR Y-14Q/M schedules for definitions of these loan categories). Include SME and Corporate Card loans (defined in the FR Y-14Q, Balances Schedule).

**Exclusions:** Do not include commercial real estate loans (defined in the FR Y-14Q, Commercial Real Estate Schedule), corporate loans (defined in the FR Y-14Q, Corporate Loans Schedule), small business loans (defined in the FR Y-14Q US Small Business Schedule), loans secured by farmland (defined in the FR Y-9C, Schedule HC-C, item 1.b), or loans to finance agricultural production and other loans to farmers (defined in the FR Y-9C, Schedule HC-C, item 3) on this schedule. Do not include loans serviced for others (i.e. serviced loans that are not directly held in the loan portfolio).

### Table 1

Table 1 has two columns:
- **Column A:** Report the unpaid principal balance of loans and leases as of the report date in millions.
- **Column B:** Report the carrying value of loans and leases as of the report date in millions.

**Carrying Value Definitions:**
- For HFS loan: the carrying value is the lower of cost or fair value.
- For HFS loans under fair value option: the carrying value is fair value.
- For HFI loans under fair value option: the carrying value is fair value.

**Item Instructions:** For each column in Table 1: (i) the sum of items 1 through 3 must equal item 4; (ii) the sum of items 5 through 9 must equal item 10; and (iii) the sum of items 4, 10, and 11 must equal item 12.

#### Line item 1 -- Residential Loans with Forward Contracts to Federal Agencies
Report the unpaid principal balance and the carrying value of all residential retail loans and leases with forward contracts to Federal Agencies.

Residential retail loans include all loans meeting the definition of FR Y-9C, Schedule HC-C, items 1.c(1), 1.c(2)(a), and 1.c(2)(b). Residential retail leases include all leases reported in FR Y-9C, Schedule HC-C, item 10.b that otherwise meet the classification criteria to be considered a residential loan, except for the fact that they are a lease rather than a loan.

Loans and leases with forward contracts to Federal Agencies are loans and leases originated for the purpose of selling to Federal Agencies (i.e. Fannie Mae, Freddie Mac, Ginnie Mae, etc.) for future securitization.

#### Line item 2 -- Residential Loans Repurchased from Agencies with FHA/VA Insurance
Report the unpaid principal balance and the carrying value of all residential retail loans and leases repurchased from agencies such as the Federal Housing Administration (FHA) or Veterans Administration (VA) insurance.

#### Line item 3 -- All Other Residential Loans Not Included Above
Report the unpaid principal balance and the carrying value of all other residential retail loans and leases not included in items 2 or 3 above.

#### Line item 4 -- Total Residential Loans
Item 4 includes shaded cell and is derived from the sum of items 1, 2, and 3.

#### Line item 5 -- Non-Residential Loans with Forward Contracts to Federal Agencies
Report the unpaid principal balance and the carrying value of loans and leases that do not meet the definition of residential loans or leases, reported in Line item 1, that were originated for the purpose of selling to Federal Agencies (i.e. Fannie Mae, Freddie Mac, Ginnie Mae, etc.) for future securitization.

#### Line item 6 -- Student Loans (Not in Forward Contracts)
Report the unpaid principal balance and the carrying value of loans to finance educational expenses, as defined in the FR Y-9C, Schedule HC-C, item 6.d, that were not originated for the purpose of selling to Federal Agencies for future securitization.

#### Line item 7 -- Credit Card Loans (Not in Forward Contracts)
Report the unpaid principal balance and the Carrying Value of all extensions of credit to individuals for household, family, and other personal expenditures arising from credit cards, as defined in the FR Y-9C, Schedule HC-C, item 6.a. Also include the unpaid principal balance and carry value of SME and Corporate Cards, as defined in the FR Y-14Q Schedule M (Balances). Exclude loans originated for the purpose of selling to Federal Agencies for future securitization.

#### Line item 8 -- Auto Loans (Not in Forward Contracts)
Report the unpaid principal balance and the carrying value of all consumer loans and lease agreements extended for the purpose of purchasing new and used passenger cars and other vehicles such as minivans, vans, sport-utility vehicles, pickup trucks, and similar light trucks for personal use, as defined in the FR Y-9C, Schedule HC-C, item 6.c, that were not originated for the purpose of selling to Federal Agencies for future securitization. Include all relevant leases reported in FR Y-9C, Schedule HC-C, item 10.a that otherwise meet the classification criteria to be considered an auto loan, except for the fact that they are a lease rather than a loan.

#### Line item 9 -- All Other Non-Residential Loans Not Included Above
Report the unpaid principal balance and the carrying value of all non-residential loans and lease agreements and extensions of credit to individuals for household, family, and other personal expenditures as defined in the FR Y-9C, Schedule HC-C, items 6(b) & 6(d), that are not reported in Items 1 through 8 above. Include all relevant leases reported in FR Y-9C, Schedule HC-C, item 10 that otherwise meet the classification criteria to be considered other non-residential loans, except for the fact that they are a lease rather than a loan.

#### Line item 10 -- Total Non-Residential Loans
Item 10 includes shaded cells and is derived from the sum of items 5 through 9.

#### Line item 11 -- Other Retail Loans with Zero Principal or Interest Recourse to the Bank
Report the unpaid principal balance and the carrying value of any retail loans and leases that present no recourse liability to the bank.

#### Line item 12 -- Total Retail FVO/HFS Loans
Item 12 includes shaded cells and is derived from the sum of items 4, 10 and 11.

### Table 2

Table 2 has nine columns (A-I). The definitions of the loan categories in Columns A through H are defined in Table 1 above. Column I contains shaded cells, and items are derived from the sum of Columns A through H.

| Column | Description |
|--------|-------------|
| A | Residential Loans in Forward Contract |
| B | Residential Loans (Repurchased with FHA/VA Insurance) |
| C | All Other Residential Loans Not Included in Columns A or B |
| D | Non-Residential Loans with Forward Contracts to Federal Agencies |
| E | Student Loans (Not in Forward Contract) |
| F | Credit Card Loans (Not in Forward Contract) |
| G | Auto Loans (Not in Forward Contract) |
| H | All Other Non-Residential Loans Not Included in Columns D, E, F or G |
| I | Total (derived from sum of Columns A through H) |

**Item Instructions:** The rows refer to the vintage of the loan or lease. The vintage is the calendar year that the loan or lease was originated. The vintages range from Pre 2006 to the current calendar year.

Categorize loans and leases by vintage and report the entire carrying value of the loan or lease in the row corresponding with the calendar year that the loan or lease was originated. Additionally, categorize loans and leases by the loan classifications provided in columns A through H. Report the total carrying value of loans and leases as of the report date in millions in the appropriate column and row according to loan classification (column) and vintage (row).

The Total row contains shaded cells, and items are derived from the sum of the vintage years. The amount reported in Table 2, Column I, Row 8 should equal the sum of Table 1, Column B, Row 4 and Table 1, Column B, Row 10.
