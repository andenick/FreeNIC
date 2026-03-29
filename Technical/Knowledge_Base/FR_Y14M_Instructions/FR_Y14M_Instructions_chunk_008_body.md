# FR Y-14M Instructions - Chunk 008
## Schedule B: Domestic Home Equity Loan and Home Equity Line Data Dictionary

This chunk introduces Schedule B and begins the B.1 Loan/Line Level Table, covering Line Items 1 through 13. Schedule B covers domestic home equity loans (HELOANs) and home equity lines of credit (HELOCs).

### Loan Population

The relevant loan population includes all loans directly held on the BHC's, IHC's, and SLHC's portfolio and all loans serviced by the BHC, IHC and SLHC in that period. Loans should be reported based on their classification on the FR Y-9C, Schedule HC-C (i.e., based on the loan's security, counterparty, or purpose). Lien status (first, junior, etc.) is considered an origination attribute.

**Applicable FR Y-9C items:**
- Portfolio loans/lines: All loans meeting the definition of FR Y-9C, Schedule HC-C, items 1.c.(1) (revolving, open-end loan secured by 1-4 family residential properties and extended lines of credit) and 1.c.(2)(b) (junior lien closed-end loans secured by 1-4 family residential real estate)
- Serviced loans/lines: Those meeting the definition of home equity loans/lines reported in FR Y-9C, Schedule HC-S, item 1 (columns A and B), Schedule HC-S item M.2.a, Schedule HC-S item M.2.b, HC-S item M.2.c, and Schedule HC-S item M.2.d

**Key reporting rules:**
- Continue reporting HELOCs in the Y-14M Home Equity schedule even after they have entered pay-down status and are no longer revolving credits. The line type at origination determines where the exposure should be reported.
- If a second lien closed-end mortgage becomes a first lien during the life of the loan, continue to report under the FR Y-14M Home Equity schedule. Lien position at origination determines which schedule to use.
- In addition to currently active loans, also include:
  - All inventory transferred to another servicer during the reporting month
  - All inventory liquidated during the reporting month (sold or otherwise disposed of)
  - For involuntary terminations of first liens reported on the Home Equity schedule, report the loan for up to 24 months following termination, until data on Line items 99 (Total Debt at Time of any Involuntary Termination), 100 (Net Recovery Amount), and 101 (Sales Price of Property) are available. Firms are not required to report these three fields for junior liens.
- Starting with March 2013, BHCs and IHCs are required to continue reporting data on loans that become Real Estate Owned (REO), through the time the loan terminates as a REO sale or otherwise. REO balances should not be included in the Portfolio Level Table.
- Loan numbers must be consistent throughout the history of the loan and must not change due to sub-servicing.
- For loans secured by multiple pieces of collateral, only report as REO when all collateral has become REO and the loan has been terminated.
- For CRE or business purpose loans collateralized by properties, place values to the best of your ability.
- If the loan is a commercial purpose loan, only report attributes unique to the facility as a whole.
- For loans serviced for others, report the full outstanding balance. Participated loans should report the total loan balance as bank owned.
- An amount, zero, or null (blank) should be entered for all items, except where other options like "not available" or "other" are specified.
- Loan numbers must uniquely identify a loan through its entire life and be consistent with OCC Mortgage Metrics Data or OCC Home Equity Data if applicable.
- Report data based on updated/newer contract terms upon HELOC line renewals. Modify Allowable Draw Period (field #28), Original Loan/Line Term (field #37), and Remaining Term (field #84) for extensions. Use applicable Modification Type code (field #77) and Last Modified Date (field #78) for renewals.

### Additional Formatting

- The collection includes both loan/line level and portfolio level variables.
- Loan/line level data should be provided each month in a single text file, produced as a "month-end" file and reported no later than thirty (30) calendar days after the end of the reporting month. One record per active loan/line.
- Portfolio level variables should be provided in a separate text file, one record per portfolio segment:
  1. **Serviced** -- All serviced loans/lines
  2. **Portfolio HFI Purchased Credit Deteriorated** -- All portfolio loans/lines acquired with deteriorated credit quality and accounted for in accordance with ASC subtopic 326
  3. **Portfolio HFI FVO / HFS** -- All portfolio loans/lines held for investment measured at fair value under a fair value option or held for sale
  4. **Other Portfolio** -- All portfolio loans/lines that are not measured at fair value, not purchase credit deteriorated, and not serviced
- For loan/line level variables representing monetary value, use the U.S. Dollar ($) as the reporting monetary unit.
- For portfolio level variables, use millions of dollars ($ Millions).
- For any line item with a format of 'character', provide the code values as listed. Do not add leading/trailing zeros or other characters unless specified.
- No quotation marks as text identifiers.
- No header row.
- Inactive inventory paid off before the beginning of the reporting month should not be included (except REO loans).
- Pipe-delimited (|, ASCII decimal 124, ASCII hexadecimal 7C).

### File Naming Convention

```
FRY14_HOMEEQUITY_LOANLEVEL_<ID_RSSD>_<AS_OF_MON_ID>_<SUBMISSION_NUMBER>.TXT
FRY14_HOMEEQUITY_PORTFOLIOLEVEL_<ID_RSSD>_<AS_OF_MON_ID>_<SUBMISSION_NUMBER>.TXT
```

SUBMISSION_NUMBER is a two-digit number tracking revisions and resubmissions (first submission = '01', resubmissions = '02', '03', etc.).

Example: Institution A with ID_RSSD 999999, Home Equity Loan level data for period 201206, would be named `FRY14_HOMEEQUITY_LOANLEVEL_999999_201206_01.TXT`.

---

### B.1 Loan/Line Level Table (Items 1-13)

Note: The MDRM code for Schedule B uses the prefix CCHE (rather than CCFL for Schedule A).

#### Line Items 1-5: Loan Identification and Property Location

**Item 1 - Loan Number (M142):** Reports an identifier for a loan that will be the same from month to month. Must identify the loan for its entire life and must be unique (piggy-backs should be separated). If the BHC/IHC/SLHC is already submitting to the OCC as part of OCC Mortgage Metrics Data or OCC Home Equity Data, use the same loan number. Up to 32 alphanumeric characters.

**Item 2 - Loan Closing Date (M143):** Reports the date the loan originally closed. Used to determine the loan's vintage. If the loan closing date is not available, the origination date may be used instead. Format: YYYYMMDD.

**Item 3 - First Payment Date (M144):** Reports the date the borrower was scheduled to make the first payment on the loan, or first started making payments. For lines with a zero balance and no draws, leave blank. Format: YYYYMMDD.

**Item 4 - Property State (9200):** Reports the state in which the property is located using two-letter postal codes. If a loan is secured by two properties in different states and is flagged as a commercial loan, leave blank.

**Item 5 - Property ZIP Code (9220):** Reports the five-digit ZIP code, including leading zeroes (e.g., 00901, 10101).

#### Line Items 6-9: Loan Amounts and Valuation

**Item 6 - Original Loan Amount Disbursed (M147):** Reports the dollar amount of funds disbursed to the borrower at loan closing, rounded to the nearest whole dollar. This data must be populated.

**Item 7 - Original Loan / Line Commitment (M242):** Reports the total credit line available at origination (the total commitment), not the actual amount drawn (amount drawn is in Line Item 6). For HELOANs, Line items 6 and 7 will be the same value.

**Item 8 - Original Property Value (M148):** Reports the property value in dollars at the time the loan was originated, defined as the lesser of selling price or the appraised value.

**Item 9 - Original Combined LTV (M150):** Reports the original combined loan-to-value (LTV) ratio, which is the original amount of the home equity loan (or credit line) from Line Item 7, in addition to any senior or other junior liens, divided by the property value at origination. If there is only one lien, report LTV in this field. Populate with NULL if unavailable. Provided as a decimal (e.g., 0.8 for 80%, 1.05 for 105%).

#### Line Items 10-13: Borrower Characteristics

**Item 10 - Income Documentation (M151):** Reports how the borrower's income levels were documented at origination:
- 1 = Full (full verification via W2, pay stubs, tax returns; assets verified; underwriting criteria documented)
- 2 = Alt/Low - Lender (lender program without requiring verification of employment, assets, mortgage/rental history and/or DTI)
- 3 = Alt/Low - Borrower (borrower-requested low/no doc)
- 4 = Alt/Low - Unknown
- 5 = Stated - Lender (lender's automated underwriting system suggested stated income)
- 6 = Stated - Borrower (borrower-requested stated income)
- 7 = Stated - Unknown

May be provided on a best efforts basis for loans serviced for others and loans acquired through mergers and acquisitions.

**Item 11 - Debt to Income (DTI) Back-End at Origination (M152):** Reports the back-end DTI ratio -- the percent of borrower's total monthly debt payments (including proposed housing expenses) divided by gross monthly income. May be provided on best efforts basis for serviced-for-others and M&A-acquired loans.

**Item 12 - Debt to Income (DTI) Front-End at Origination (M153):** Reports the front-end DTI ratio -- the monthly principal, interest, tax, insurance (PITI) payment divided by gross monthly income (the PITI Housing Ratio).

**Item 13 - Origination Credit Bureau Score (M154):** Reports the credit score of the borrower at origination using a commercially available credit bureau score. Report the credit score vendor in item 109 and the credit score version in item 110. Provided as a whole number (e.g., 759).
