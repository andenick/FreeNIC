# FR Y-14Q Instructions -- Schedule H.1 Corporate Loan Data Fields (Fields 81-99)

## H.1 Field Specifications Part 4 -- Remaining Loan and Obligor Description Fields

This section continues the H.1 Corporate Loan Data Schedule field specifications, covering the remaining Obligor Financial Data fields (81-82), Special Purpose Entity identification (83), reserved fields (84-85), accounting treatment flags (86), Shared National Credit linkage (87), advanced IRB risk parameters (88-90), renewal and currency fields (91-92), collateral valuation (93), prepayment provisions (94), entity-level industry classification (95), participation details (96), leveraged lending classification (97), disposition tracking (98-99).

### Field 81 -- Retained Earnings (RetainedEarnings)
- **MDRM**: CLCE3247
- Report the cumulative retained earnings of the entity identified in Field 2 or Field 49 less total dividend distributions to shareholders. Typically, it is the prior year's retained earnings plus net income less distributions.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar sign, commas, or decimal.

### Field 82 -- Capital Expenditures (CapitalExpenditures)
- **MDRM**: CLCEM324
- Report the funds used to acquire a long-term asset resulting in depreciation deductions over the life of the acquired asset. Report gross of depreciation.
- Report data for the trailing twelve month (TTM) period ended on the date reported in Field 52.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal.

### Field 83 -- Special Purpose Entity Flag (SpecialPurposeEntityFlag)
- Indicate '2' (Yes) if the obligor (as identified in Field 2) is organized as a bankruptcy remote, special purpose entity (SPE) where the primary source of repayment depends on the performance of specified underlying assets.
- Relevant SPE obligors include ABCP conduits, securitization trusts, and other structured variable interest entities established to purchase and finance assets through the tranching of risk.
- Entities which are trusts for the purpose of personal wealth management or Op Co/Prop Co structures should be reported as '1' (No).
- **Values**: 1 = No; 2 = Yes

### Field 84 -- DO NOT USE

### Field 85 -- DO NOT USE

### Field 86 -- Lower of Cost or Market Flag (LOCOM)
- Indicate whether the loan is accounted for under the fair value option or is held for sale and carried at the lower-of-cost-or-market (LOCOM).
- For loans not accounted for under the fair value option or not held for sale, report Option 3 (NA).
- **Values**: 1 = LOCOM; 2 = FVO; 3 = NA

### Field 87 -- SNC Internal Credit ID (SNCInternalCreditID)
- If the credit facility is reported in the Shared National Credit collection and the reporting BHC or IHC or SLHC is the lead bank/agent (option 5 in Field 34), indicate the reporting BHC's or IHC's or SLHC's Internal Credit ID as reported in the Shared National Credit collection for this credit facility as of the most recent filing date.
- If the credit facility is not reported in the Shared National Credit collection or the reporting BHC or IHC or SLHC is a participant in the Shared National Credit credit facility, report 'NA'.
- **Format**: May not contain a carriage return, line feed, comma or any unprintable character.

### Field 88 -- Probability of Default (ProbabilityOfDefault)
- For firms subject to the advanced approaches for regulatory capital, report the advanced IRB parameter estimate for the probability of default (PD) as defined in the Rule.
- For a defaulted obligor, report 100 percent ('1').
- For firms not subject to the advanced approaches, report the PD estimate that corresponds to the Obligor Internal Risk Rating reported in Field 10. If the reporting entity does not assign a PD estimate to the Obligor Internal Risk Rating, report 'NA.'
- **Format**: Express as a decimal to 4 decimal places (e.g., 0.05% is 0.0005; 100% is 1). Use decimal format; do not use scientific notation.

### Field 89 -- Loss Given Default (LGD)
- **MDRM**: CLCOG081
- For firms subject to the advanced approaches for regulatory capital, report the advanced IRB LGD estimate at the loan level as defined in the Rule. If the credit facility includes multiple loans with different LGD assignments, report the dollar weighted average LGD that approximates the overall LGD on the committed balance of the credit facility.
- For firms not subject to the advanced approaches, report the credit facility LGD estimate from the reporting entity's credit risk management system. If an LGD estimate is not assigned, report 'NA.'
- **Format**: Express as a decimal to 4 decimal places (e.g., 0.05% is 0.0005). Use decimal format; do not use scientific notation.

### Field 90 -- Exposure At Default (EAD)
- For firms subject to the advanced approaches for regulatory capital, report the advanced IRB parameter estimate for the Exposure at Default (EAD). If the credit facility includes multiple loans with different EAD assignments, report the dollar weighted average EAD that approximates the overall EAD on the committed balance of the credit facility.
- For firms not subject to the advanced approaches, report the credit facility EAD estimate from the reporting entity's internal credit risk management system. If an EAD estimate is not assigned, report 'NA.'
- **Format**: Rounded whole dollar amount with no cents (e.g., 20000000). No dollar sign, commas, or decimal.

### Field 91 -- Renewal Date (RenewalDate)
- If the credit facility has been renewed per the terms of the original loan agreement, re-priced, or has a change in the maturity date such that the Origination Date did not change, report the date on which the most recent renewal notification became effective.
- The Renewal Date is intended to capture maturity date extensions provided to the obligor by the BHC or IHC or SLHC and extension options at the sole discretion of the borrower.
- If a credit facility has been renewed as part of a major modification such that the contractual date of the original loan is changed, then such date would be reported in Field 18 (Origination Date) and the BHC, IHC and SLHC should report 9999-12-31 in this field.
- If the credit facility has not been renewed, report 9999-12-31.
- **Format**: yyyy-mm-dd (e.g., 2005-02-01)

### Field 92 -- Credit Facility Currency (CreditFacilityCurrency)
- Indicate the currency denomination for contractual principal and interest payments on the credit facility, using the relevant three-letter ISO 4217 currency code.
- If payments are legally permitted or required in more than one currency, indicate the predominant currency for contractual credit facility payments.
- Whether or not the currency denomination is USD, all amounts reported in other fields must be in terms of US Dollars.
- The predominant currency should be the currency which represents the predominant share of the credit facility committed balance.
- **Format**: Standard ISO 4217 three-letter currency codes

### Field 93 -- Collateral Market Value (CollateralMarketValue)
- For facilities which require ongoing or periodic valuation of the collateral, report the market value of the collateral as of the reporting date.
- If the market value of collateral is not updated in the reporting entity's internal risk management systems as of the reporting date, report NA.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar sign, commas, or decimal.

### Field 94 -- Prepayment Penalty Flag (PrepaymentPenaltyFlag)
- Indicate whether the credit facility has a prepayment penalty clause in effect which may include yield maintenance.
- **Values**: 1 = Yes (currently in effect); 2 = The prepayment penalty has expired; 3 = No prepayment penalty clause

### Field 95 -- Entity Industry Code (EntityIndustryCode)
- Report the numeric code that describes the primary business activity of the entity identified in Field 49 according to the North American Industry Classification System (NAICS). If the NAICS code is not available, provide either the Standard Industrial Classification (SIC), or Global Industry Classification Standard (GICS).
- If the entity identified in Field 49 is an individual, the industry code should be consistent with the industry in which the commercial purpose of the loan operates.
- If the business or individual operates in multiple industries, report the industry that best represents the commercial risk of the loan (i.e., the predominant industry).
- **Format**: 4 to 6 digit number. If not available, provide SIC or GICS code.

### Field 96 -- Participation Interest (ParticipationInterest)
- For participated or syndicated credit facilities that have closed and settled, report the percentage of the total loan commitment held by the BHC or IHC or SLHC.
- If the credit facility is not participated or syndicated, report 1.
- If the credit facility is syndicated and reported as options 1, 2, or 3 in Field 100, report NA.
- For fronting exposures, report 1.
- **Format**: Express as a decimal to 4 decimal places (e.g., 0.05% is 0.0005). Use decimal format; do not use scientific notation.

### Field 97 -- Leveraged Loan Flag (LeveragedLoanFlag)
- Indicate '2' (Yes) if the credit facility is defined as a leveraged loan per criteria in the reporting entity's internal risk management framework developed pursuant to SR 13-3 (Interagency Guidance on Leveraged Lending).
- **Values**: 1 = No; 2 = Yes

### Field 98 -- Disposition Flag (DispositionFlag)
- Report the disposition method for any credit facility that was disposed during the reporting quarter.
- If the BHC or IHC or SLHC is still pursuing payment of principal, interest or fees, report as option "0".
- Rebookings/restructures where loan amounts are transferred or combined between obligations should be reported as either option 1 (Payoff) or option 2 (Involuntary payoff) depending on the occurrence of default.
- **Values**:
  - 0 = Active -- Report for all credit facilities required to be reported in this data collection and do not meet the definitions of options 1 through 8 as of the reporting date.
  - 1 = Payoff -- Report all instances where the credit facility has been paid in full by the borrower, or where an undrawn credit facility reaches maturity and is not renewed.
  - 2 = Involuntary Payoff -- Report all instances where the credit facility has been paid in full after the occurrence of default per the terms of the credit agreement.
  - 3 = Involuntary Liquidation -- Report all instances where the credit facility has been liquidated either through foreclosure proceedings or another settlement option resulting in incomplete repayment of principal. Include short-sales, charge-offs, as well as REO. This includes loans active in the quarter prior to the reporting quarter that were sold at a foreclosure sale and taken into REO in the reporting quarter. Also include all instances where credit has been resolved (i.e. no longer pursuing collection) but not through foreclosures, servicing transfers, or payments made by the obligor.
  - 4 = Sold or fully participated -- Report all instances where the loan has been sold or fully participated to another institution during the reporting quarter. For fully syndicated loans, report option 5.
  - 5 = Fully Syndicated -- Report all instances where 100% of the commitment has been syndicated to other institutions during the reporting quarter.
  - 6 = Below reporting threshold -- Report all instances where the credit facility fell below the $1 million reporting threshold.
  - 7 = Transfer to another Y-14 schedule. Indicate the schedule where the credit facility is now reported in Field 99 below.
  - 8 = Expired Commitment to Commit

### Field 99 -- Disposition Schedule Shift (DispositionScheduleShift)
- For credit facilities reported with option 7 (Transfer to another Y-14 schedule) in Field 98, indicate the Y-14 report, schedule, and subschedule to which the credit facility shifted.
- **Format examples**:
  - If transferred to FR Y-14Q Schedule H.2 Commercial Real Estate, report "Q.H.2"
  - If transferred to FR Y-14M Schedule D.1 Domestic Credit Card Data Collection Data Dictionary, report "M.D.1"
