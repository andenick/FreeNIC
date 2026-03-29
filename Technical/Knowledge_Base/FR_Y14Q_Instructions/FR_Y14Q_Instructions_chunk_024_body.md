# FR Y-14Q Instructions -- Schedule H.2 Commercial Real Estate Data Fields (Fields 40-58)

## H.2 CRE Field Specifications (continued)

### Field 40 -- Net Operating Income (NOI) Current (CurrentNetOperatingInc)
- **MDRM (CRED)**: K472
- Report the most recent annualized NOI (as defined in Field 12) as of the report date that serves as the primary source of repayment.
- Refer to Field 12 for allowable values and formatting guidelines.
- **Mandatory**

### Field 41 -- Last NOI Date (LastNOIDate)
- **MDRM (CRED)**: K473
- Report the date for the value provided in CurrentNetOperatingInc (Field 40).
- **Format**: yyyy-mm-dd. Must be before or equal to the report date. May be Null (blank) if Field 40 is 'NA'.
- **Mandatory**

### Field 42 -- Current Value (CurrentValue)
- **MDRM (CRED)**: M209
- Report the most recent value of the subject property, which may be either from an appraisal or an independent evaluation depending on legal (12 CFR 34) and bank policy requirements.
- If the most recent valuation is the value reported in Field 13, then report the amount reported in Field 13.
- Value is prorated based on the bank's ownership interest. For multiple properties, report the sum of all property values as adjusted for prorated participations. For cross-collateralization, provide the sum of all property values.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar signs, commas, or decimals.
- **Mandatory**

### Field 43 -- Last Valuation Date (LastValuationDate)
- **MDRM (CRED)**: K475
- Report the date of the most recent valuation provided in Current Value (Field 42).
- **Format**: yyyy-mm-dd. Must be before or equal to the report date.
- **Mandatory**

### Field 44 -- Cross Collateralized Loan Numbers (CrossCollateralizedLoans)
- **MDRM (CRED)**: M290
- Report the LoanNumbers (Field 1) for all loans which are cross-collateralized with the loan in Field 1. This includes loans with committed balance less than $1 million.
- One loan secured by multiple properties is NOT considered cross-collateralized. Only report loans that share properties in the collateral pool.
- The provided loan numbers must have a corresponding entry in the CRE collection. Cross-collateralized loans that are not CRE Loans should be excluded.
- **Format**: LoanNumbers separated by comma. Leave blank if not cross-collateralized.
- **Mandatory**

### Field 45 -- Additional Collateral (AdditionalCollateral)
- **MDRM (CRED)**: M291
- Report the value of any cash and marketable securities that are pledged as collateral and where the bank has a first perfected security interest.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar signs, commas, or decimals.
- **Optional**

### Field 46 -- DO NOT USE

### Field 47 -- DO NOT USE

### Field 48 -- DO NOT USE

### Field 49 -- Troubled Debt Restructuring (TroubledDebtRestructuring)
- Indicate whether the loan has been restructured in a troubled debt restructuring as defined in the FR Y-9C Glossary entry for "troubled debt restructuring."
- **Values**: 1 = No; 2 = Yes
- **Mandatory**

### Field 50 -- DO NOT USE

### Field 51 -- DO NOT USE

### Field 52 -- Lower of Cost or Market Flag (LOCOM)
- Indicate whether the loan is accounted for under the fair value option or is held for sale and carried at the lower-of-cost-or-market (LOCOM).
- For loans not accounted for under the fair value option or not held for sale, report Option 3 (NA).
- **Values**: 1 = LOCOM; 2 = FVO; 3 = NA
- **Mandatory**

### Field 53 -- SNC Internal Credit ID (SNCInternalCreditID)
- If the credit facility is reported in the Shared National Credit collection and the reporting BHC or IHC or SLHC is the lead bank/agent (option 5 in Field 7), indicate the reporting entity's Internal Credit ID as reported in the SNC collection as of the most recent filing date.
- If not reported in SNC or the reporting entity is a participant, report 'NA'.
- **Format**: No carriage return, line feed, comma, or unprintable characters.
- **Mandatory**

### Field 54 -- Renewal Date (RenewalDate)
- If the credit facility has been renewed per the terms of the original loan agreement, re-priced, or has a change in the maturity date such that the Origination Date did not change, report the date on which the most recent renewal notification became effective.
- The Renewal Date is intended to capture maturity date extensions provided to the obligor and extension options at the sole discretion of the borrower.
- If renewed as part of a major modification changing the contractual date, report the date in Field 10 and enter 9999-12-31 here.
- If not renewed, report 9999-12-31.
- **Format**: yyyy-mm-dd
- **Mandatory**

### Field 55 -- Credit Facility Currency (CreditFacilityCurrency)
- Indicate the currency denomination for contractual principal and interest payments using the relevant three-letter ISO 4217 currency code.
- If payments permitted in more than one currency, indicate the predominant currency.
- All amounts in other fields must be in terms of US Dollars regardless of the credit facility currency denomination.
- The predominant currency = the currency representing the predominant share of the credit facility committed balance.
- **Format**: Standard ISO 4217 three-letter currency codes
- **Mandatory**

### Field 56 -- Current Occupancy Date (CurrentOccupancyDate)
- Report the date on which the most recent occupancy level indicated in Field 23 (Current Occupancy) was determined by the borrower.
- **Format**: yyyy-mm-dd. Must be before or equal to report date. May be Null (blank) if Field 23 is 'NA'.
- **Mandatory**

### Field 57 -- Current Value Basis (CurrentValueBasis)
- Provide integer code if the Current Value in Field 42 was calculated using "as is," "as stabilized" or "as completed" value as defined in SR10-16.
- **Values**: 1 = As Is; 2 = As Stabilized; 3 = As Completed
- **Mandatory**

### Field 58 -- Prepayment Penalty Flag (PrepaymentPenaltyFlag)
- Indicate whether the credit facility has a prepayment penalty clause in effect which may include yield maintenance.
- **Values**: 1 = Yes; 2 = The prepayment penalty has expired; 3 = No prepayment penalty clause
- **Mandatory**
