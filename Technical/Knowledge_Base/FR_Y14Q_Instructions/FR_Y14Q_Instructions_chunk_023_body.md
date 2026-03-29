# FR Y-14Q Instructions -- Schedule H.2 Commercial Real Estate Data Fields (Fields 19-39)

## H.2 CRE Field Specifications (continued)

### Field 19 -- Maturity Date (MaturityDate)
- **MDRM (CRED)**: 9914
- Report the maturity date as the last date upon which the funds must be repaid, inclusive of extension options that are solely at the borrower's discretion, and according to the most recent terms of the credit agreement.
- If extension options are conditional on certain terms being met, such extensions should be considered to be at the sole discretion of the borrower.
- For demand loan, enter '9999-01-01'.
- For commitments to commit, report the estimated maturity date based on the tenor in the extended terms.
- **Format**: yyyy-mm-dd
- **Mandatory**

### Field 20 -- Amortization (Amortization)
- **MDRM (CRED)**: K457
- For loans with a monthly amortization schedule, report the original amortization term in months from the date in Field 10 at the rate implied by the current payment disregarding any balloon payment.
- For interest only loans, enter '0' (zero). After the interest only period is over, report the number of months to fully amortize.
- For a non-standard amortization schedule, report '-1'. Non-standard amortization refers to payment schedules not based on a preset amortization schedule of equal monthly payments, including schedules with varying repayments based on percentage of balance or trigger events.
- **Format**: Whole months (e.g., 10 years = 120). '-1' for non-standard.
- **Mandatory**

### Field 21 -- Recourse (Recourse)
- **MDRM (CRED)**: G106
- Indicate whether credit facility provides for full, partial or no recourse to a sponsor or guarantor as a source of repayment, as of the reporting date.
- **Values**: 1 = DO NOT USE; 2 = DO NOT USE; 3 = Full; 4 = Partial; 5 = None
- **Mandatory**

### Field 22 -- Line of Business (LineOfBusiness)
- **MDRM (CRED)**: K458
- Indicate the internal line of business.
- Free text (e.g., Retail, Private Banking, Corporate Banking). Must be consistent with Schedule H.3 (Line of Business Schedule), Field 1.
- **Optional**

### Field 23 -- Current Occupancy (CurrentOccupancy)
- **MDRM (CRED)**: K459
- Report the current physical occupancy of rent-paying tenants (including tenants still in concessionary periods) as a percentage of net rentable square footage.
- Use NA if 1-4 family Residential Construction (HC-C item 1.a(1)) or other construction and land development loans (HC-C item 1.a(2)) does not have a currently valid certificate of occupancy.
- For condo construction where construction is completed but not all units sold, report physical occupancy based on units owned by the borrower.
- "Current occupancy" means as close to the reporting date as possible.
- **Format**: Fraction to 2 decimal places (e.g., "0.80" for 80%). '0' if actually zero. NA if not applicable.
- **Mandatory**

### Field 24 -- Anchor Tenant (AnchorTenant)
- **MDRM (CRED)**: K460
- Report the name of anchor tenant(s), if applicable. Anchor tenant = any tenant named in a co-tenancy clause or whose rental income accounts for the majority of gross rental income at the property level.
- If multiple anchor tenants, separate names with a double semi-colon ';;'.
- **Optional**

### Field 25 -- Loan Purpose (LoanPurpose)
- **MDRM (CRED)**: G073
- Indicate the purpose of the CRE Loan at the origination date using an integer code.
- **Values**:
  - 1 = Construction Build to Suit / Credit Tenant Lease (100% occupancy to investment grade tenant on long term triple-net lease)
  - 2 = Land Acquisition & Development (vacant land acquisition or improvement of unimproved real property prior to construction)
  - 3 = Construction Other (construction of buildings/structures, additions, alterations, demolition for new structures)
  - 4 = DO NOT USE
  - 5 = DO NOT USE
  - 6 = Acquisition (nonowner occupied) (purchase or majority ownership change of non-owner occupied nonfarm nonresidential or multifamily)
  - 7 = Refinance (replacement of existing loan with different terms; generally no purchase or structural changes)
  - 8 = Other
  - 9 = Mini-Perm (short term financing for completed construction projects; report once loan moves from construction to options 3, 5, or 7 in Field 4)
  - 10 = DO NOT USE
  - 11 = DO NOT USE
  - 12 = DO NOT USE
- **Mandatory**

### Field 26 -- Interest Rate Variability (InterestRateVariability)
- **MDRM (CRED)**: K461
- Indicate the variability of current interest rates to maturity.
- For fully undrawn commitments, report variability that would apply if funded and fully drawn. If allows either fixed or floating at borrower's discretion, report '3' Mixed.
- For facilities where revenue is entirely fee based and no interest is or will ever be collected, enter '4'.
- **Values**: 0 = DO NOT USE; 1 = Fixed; 2 = Floating; 3 = Mixed; 4 = Entirely fee based
- **Mandatory**

### Field 27 -- Interest Rate (InterestRate)
- **MDRM (CRED)**: 7889
- Report the current interest rate charged. For multiple draws with different rates, enter the dollar weighted average rate on the drawn balance, exclusive of interest rate swaps.
- For fully undrawn commitments, report the rate that would apply if funded and fully drawn.
- For fully undrawn facilities allowing multiple rates at borrower's discretion, report the most conservative (highest) rate as of most recent origination or renewal date.
- For fully undrawn facilities with multiple lines of credit, enter the dollar weighted average rate.
- For entirely fee based facilities, report 'NA'.
- **Format**: Decimal (e.g., 0.0575 for 5.75%)
- **Mandatory**

### Field 28 -- Interest Rate Index (InterestRateIndex)
- **MDRM (CRED)**: K462
- For floating rate CRE Loans, report the base interest rate index. If borrower has an option, select the index actually in use.
- If fixed or entirely fee based, choose "Not applicable." For mixed base interest rates, choose "Mixed."
- For fully undrawn commitments, report the index that would apply; if multiple indices at borrower's discretion, report the index used to calculate Field 27.
- **Values**: 0 = DO NOT USE; 1 = LIBOR; 2 = PRIME or Base; 3 = Treasury Index; 4 = Other; 5 = Not applicable (Fixed or entirely fee based); 6 = Mixed; 7 = SOFR
- **Mandatory**

### Field 29 -- Interest Rate Spread (InterestRateSpread)
- **MDRM (CRED)**: K463
- For floating rate CRE Loans, report the spread from base rate (can be positive or negative).
- If fixed or entirely fee based, populate 'NA'.
- For multiple draws with different spreads, provide the spread that approximates the overall spread.
- For fully undrawn commitments, report the spread per the credit agreement terms.
- **Format**: Decimal (e.g., 0.0575 for 5.75%). 'NA' if fixed or fee based. Negative values use '-'.
- **Mandatory**

### Field 30 -- Interest Rate Ceiling (InterestRateCeiling)
- **MDRM (CRED)**: K464
- For floating rate CRE Loans, report the rate ceiling from credit agreement.
- If no ceiling, populate 'NONE'. If fixed or entirely fee based, populate 'NA'.
- For multiple ceilings, provide the maximum. For fully undrawn commitments, report the ceiling that would apply.
- **Format**: Decimal (e.g., 0.0575 for 5.75%). 'NA' if fixed/fee based. 'NONE' if no ceiling.
- **Mandatory**

### Field 31 -- Interest Rate Floor (InterestRateFloor)
- **MDRM (CRED)**: K465
- For floating rate CRE Loans, report the rate floor from credit agreement.
- If no floor, populate 'NONE'. If fixed or entirely fee based, populate 'NA'.
- For multiple floors, provide the minimum. For fully undrawn commitments, report the floor that would apply.
- **Format**: Decimal (e.g., 0.0575 for 5.75%). 'NA' if fixed/fee based. 'NONE' if no floor.
- **Mandatory**

### Field 32 -- Frequency of Rate Reset (FrequencyofRateReset)
- **MDRM (CRED)**: K466
- For floating rate CRE Loans, report the frequency of interest rate reset in months. For frequencies less than 1 month, report as 1 month.
- If fixed or entirely fee based, populate 'NA'.
- For fully undrawn commitments, report the frequency that would apply per credit agreement terms.
- **Format**: Whole months. 'NA' if fixed or fee based.
- **Mandatory**

### Field 33 -- Interest Reserves (InterestReserves)
- **MDRM (CRED)**: K467
- Report the dollar amount of remaining interest rate reserves. Interest reserves represent funds remaining from the original construction commitment to be used to pay interest during construction and lease-up phases. If a participation, prorate.
- If interest reserves are not applicable (e.g., non-construction loans) or not funded, populate '0'.
- **Format**: Rounded whole dollar amount. No cents, punctuation, or dollar signs.
- **Mandatory**

### Field 34 -- Origination Amount (OriginationAmount)
- **MDRM (CRED)**: K468
- Report the bank's total commitment as of the origination date in Field 10. Includes both drawn and undrawn amounts. For multiple lenders, only the reporting entity's pro-rata commitment.
- **Format**: Round to the whole dollar. No punctuation or dollar sign.
- **Mandatory**

### Field 35 -- Original/Previous Loan Number (OrigLoanNumber)
- **MDRM (CRED)**: G064
- Report the Internal identification code from the previous submission. If the credit facility represents fulfillment of a commitment to commit, report the prior ID. If no change or first submission, use Field 1 value.
- For disposed facilities with rebookings/restructures, report IDs separated by comma.
- **Format**: No carriage return, line feed, or unprintable characters. Comma-separated for multiple IDs.
- **Mandatory**

### Field 36 -- Acquired Loan (AcqLoan)
- **MDRM (CRED)**: K469
- Indicate if the loan was acquired via a bank, portfolio or individual loan purchase (outside original underwriting syndication). Includes secondary market purchases, bank acquisitions, or portfolio acquisitions.
- Loans originated and underwritten by the reporting bank = "2" (No).
- Once a loan has been renewed or modified (bank underwrites per its credit policy), it should no longer be reported as acquired.
- **Values**: 1 = Yes; 2 = No
- **Mandatory**

### Field 37 -- # Days Principal or Interest Past Due (PastDue)
- **MDRM (CRED)**: G077
- Report the longest number of days principal and/or interest payments are past due, if past due 30 days or more. Report as of last day of reporting period or disposition date.
- If not past due 30+ days, enter '0'. For fully undrawn commitments, enter '0'.
- **Mandatory**

### Field 38 -- Non-Accrual Date (NonAccrualDate)
- **MDRM (CRED)**: G078
- Report the date the credit facility was placed on non-accrual, if applicable.
- If no non-accrual date, enter '9999-12-31'. For fully undrawn commitments, enter '9999-12-31'.
- **Format**: yyyy-mm-dd
- **Mandatory**

### Field 39 -- Property Size (PropertySize)
- **MDRM (CRED)**: K471
- Report only for facilities secured by one property. Report size for the predominant property type:
  - Retail: Square Feet (net rentable area)
  - Industrial/Warehouse: Square Feet
  - Hotel/Hospitality/Gaming: Rooms
  - Multi-family for rent: Units
  - Homebuilders except condo: Lots
  - Condo: Units
  - Office: Square Feet
  - Land and Lot Development: Acreage
- If single property with multiple types and none predominates, report 'Other'. If property type is 'Other', report 'Other'. If secured by multiple properties, report 'NA'.
- Square footage = net rentable area; for properties under construction, report planned finished square footage.
- **Mandatory**
