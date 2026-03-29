# FR Y-14M Instructions - Chunk 009
## Schedule B: Domestic Home Equity Loan and Home Equity Line Data Dictionary (Continued)

### B.1 Loan/Line Level Table (Continued, Items 14-45)

This chunk continues the Schedule B.1 Loan/Line Level Table data dictionary, covering Line Items 14 through 45. These items address current credit scores, property and loan characteristics, ARM parameters, loan terms, payment information, and draw amounts.

#### Line Items 14-17: Borrower and Loan Characteristics

**Item 14 - Current Credit Bureau Score (M189):** Reports the current credit score of the borrower using a commercially available credit bureau score. Provide the most recently determined score. Report vendor in item 111 and version in item 112. Required for portfolio loans, optional for serviced-for-others loans. Must be updated at least one month within the quarter and refreshed at least one month within every subsequent quarter.

**Item 15 - Occupancy (M155):** Reports occupancy related information available on the mortgage at the time of origination. Values: 1=Primary, 2=Second Home, 3=Non Owner / Investment, U=Unknown.

**Item 16 - Lien Position at Origination (M158):** Reports the position of this loan relative to any additional liens on the property. If there are no additional liens, the loan is in first position. If the lien position is greater than third, code as "3". Values: 1=First lien, 2=Second lien, 3=Third lien or greater, U=Unknown.

**Item 17 - Home Equity Line Type (M243):** Reports the home equity line type. Home Equity Loan (1) = traditional fixed term second mortgages with no draw feature. Home Equity Line of Credit (2) = borrower may access an available credit line through draw features; balances may have fixed term, locked or amortizing portions. Other (3).

#### Line Items 18-20: Property and Interest Type

**Item 18 - Number of Units (M162):** Reports the number of units of the property. Values: 1-4 for individual unit counts, Y=Other (for CRE or commercial purpose mortgage loans on multiple properties), U=Unknown.

**Item 19 - Property Type (M164):** Reports the property type. For one property with multiple uses, report as "F" (Mixed Use). For properties with more than one piece of collateral, report as "Z" (Other). If it is known that a property is in a planned unit development (PUD) and the underlying property type is also known, report the underlying property type. Values: 1=Single Family Resident, 2=Condo, 3=Co-Op, 4=2-4 Units, 5=Townhouse, 6=Planned Unit Development, 7=5+Units, E=Commercial, F=Mixed Use, M=Manufactured Housing, Z=Other, U=Unknown.

**Item 20 - Interest Type at Origination (M244):** Reports the interest type at origination. 1=Fixed (rate fixed for entire term), 2=Variable (rate fluctuates based on spread to index, including all variable rate loans regardless of initial fixed period).

#### Line Items 21-24: Loan Origination Attributes

**Item 21 - Interest Only at Origination (M168):** Reports whether the loan required interest only at origination. An interest only (IO) mortgage is a nontraditional mortgage allowing the borrower to pay only interest for a specified number of years. Values: Y=Yes, N=No, U=Unknown.

**Item 22 - Interest Only in Reporting Month (M190):** Reports whether the minimum payment in the reporting month represents only the interest due. Values: N=Was not I/O in reporting month, Y=Was I/O in reporting month, U=Unknown.

**Item 23 - Loan Source (M159):** Reports the source by which the servicer originated or acquired the loan:
- 1 = Retail (Branch, Internet)
- 2 = Wholesale (Broker)
- 3 = Correspondent (whole loans purchased on flow basis)
- 4 = Servicing Rights Purchased (separately negotiated PMSR from third party)
- 5 = Bulk Purchased (pools of whole loans purchased from third party originator)
- 6 = Wealth Management / Private Banking
- U = Unknown

**Item 24 - Credit Class (M156):** Reports the credit class designation at origination (shall not change over time). Values: 1=Prime, 2=Alt-A, 3=Non-prime, 4=Government Owned. Government programs code value '4' added since they are difficult to classify within conventional market definitions.

#### Line Items 25-28: Ownership and Draw Period

**Item 25 - Loan / Line Owner (M245):** Reports the investor of the loan. Values: 1=Securitized, 2=Portfolio (owned and held on bank's balance sheet, including HFS and HFI), 3=Serviced For Others, 4=Other.

**Item 26 - ARM Initial Rate Period (M171):** Reports the ARM initial rate adjustment period in months -- the term from origination to the first interest rate change date. For adjustable rate hybrid loans, report the initial fixed principal and interest payment period in months.

**Item 27 - ARM Payment Reset Frequency (M246):** Reports the payment reset frequency for adjustable rate loans in months. For example, annual adjustment = 12; floating rate note resetting monthly = 1.

**Item 28 - Allowable Draw Period (M247):** For lines of credit only, reports the duration in months (starting from origination date) during which the borrower has the ability to make withdrawals against the credit line. Leave blank for home equity loans. Use value 999 for "evergreen" accounts where the borrower is always allowed to draw. Allowable values: 1-480; 999.

#### Line Items 29-37: ARM Parameters and Loan Term

**Item 29 - ARM Index (M173):** Reports the published financial index name used to determine the interest rate. All ARM interest rate and payment variables should be populated with origination values. If using Wall Street Journal prime rate, use code '50'. For HELOCs, use items 29-36 to report caps/floors, margins, and rate indexes. Extensive code list including: COSI (07), various T-bill types (10-1Z), COFI types (20-2Z), LIBOR types (30-3Z), FHLBB (40), Bank Prime Rate (50), Certificate of Deposit (60), FNMA/FHLMC (70), MTA (80), LAMA (81), SOFR types (91-9Z), BSBY types (B1-BZ), Other (ZZ), Unknown (UU).

**Item 30 - ARM Margin at Origination (M174):** Reports the margin for adjustable rate loans -- the rate added to the index to determine the monthly interest rate at origination. Provided as a fraction (e.g., 0.0575 for 5.75%).

**Item 31 - ARM Periodic Rate Cap (M176):** Reports the periodic interest rate cap for adjustable rate loans. Absolute rate cap (not spread from original). Populated with origination values.

**Item 32 - ARM Periodic Rate Floor (M177):** Reports the periodic interest rate floor for adjustable rate loans. Absolute rate floor (not spread from original). Populated with origination values.

**Item 33 - ARM Lifetime Rate Cap (M178):** Reports the lifetime interest rate cap for adjustable rate mortgages. Absolute rate cap (not spread from original).

**Item 34 - ARM Lifetime Rate Floor (M179):** Reports the minimum lifetime interest rate for adjustable rate mortgages. Absolute rate floor (not spread from original).

**Item 35 - ARM Periodic Pay Cap (M180):** Retired March 2020.

**Item 36 - ARM Periodic Pay Floor (M181):** Retired March 2020.

**Item 37 - Original Loan/Line Term (M184):** Reports the term in months on the original loan/line, applicable to both home equity loans and lines of credit. For a line of credit, the original loan term should be the combined draw period and the amortized repayment period. For commercial system accounts due on demand, leave blank (flag using Commercial Loan Flag field #102). Do not change the original loan term for loan modifications. For loans with no end date for the draw period (e.g., "Evergreen" loans), use value '999'. Allowable values: 0-600, 999.

#### Line Items 38-45: Loan Status and Payment

**Item 38 - Bankruptcy Flag (M194):** Reports whether the borrower is in bankruptcy as of the end of the reporting month. Flag all loans where the servicer has been notified of the borrowers' bankruptcy declaration, including co-borrowers.

**Item 39 - Next Payment Due Date (M196):** Reports the due date for the next outstanding payment on the loan. For delinquent loans, this date will be in the past. Leave blank for accounts closed in the current month. For Chapter 13 bankruptcy, report the contractual due date. Format: YYYYMMDD.

**Item 40 - Original Interest Rate (M185):** Reports the annual percentage rate as specified on the note at origination. Provided as a fraction (e.g., 0.0575 for 5.75%).

**Item 41 - Current Interest Rate (M197):** Reports the annual percentage rate as of the last day of the reporting month. Provided as a fraction.

**Item 42 - Interest Type - Current (M248):** Reports the interest type in the reporting month. 1=Fixed, 2=Variable.

**Item 43 - Principal and Interest (P&I) Amount Current (M200):** Reports the scheduled principal and interest due from the borrower in the reporting month. For balloon loans paying off, report the full amount due. For loans paying off, a value of 0 is permissible. For REO records where original P&I is not available, 0 is permissible. If mortgage bills quarterly, report zero for off-quarter months. Do not include past due amounts.

**Item 44 - Unpaid Principal Balance (M201):** Reports the current unpaid balance at the end of the reporting month. Does not include charge-offs, discounts, or other accounting marks. Should only be reduced to zero when: for loans, liquidated (paid-in-full, charged-off, REO sold, service transferred); for lines, liquidated or credit line not being utilized.

**Item 45 - Monthly Draw Amount (M249):** For home equity line of credit accounts, reports the total amount drawn during the month. For lines with zero balance and no draws, report '0'.
