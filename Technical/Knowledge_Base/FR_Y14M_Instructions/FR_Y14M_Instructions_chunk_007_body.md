# FR Y-14M Instructions - Chunk 007
## Schedule A: Domestic First Lien Closed-End 1-4 Family Residential Mortgage Loan Data Dictionary (Continued)

### A.1 Loan Level Table (Continued and Concluded)

This chunk continues the Schedule A.1 Loan Level Table data dictionary, covering Line Items 120 through 144, concluding the A.1 table. It then introduces the A.2 Portfolio Level Table (Items 1-3).

#### Line Items 120-123: Disposition and Historical Delinquency

**Item 120 - Loss/Write down Date (M947):** Retired March 2020.

**Item 121 - Sales Price of Property (M948):** Reports the final sales price at which the property was disposed by the BHC or IHC or SLHC in the case of involuntary termination. Provide the same price as the BHC or IHC or SLHC would submit to public records data. Net proceeds from short sales or third party sales should be reported in Line item 94. This is a required line item for Investor Type code values 4 (Private Securitized) and 7 (Portfolio) and best efforts for all others.

**Item 122 - Performance of Junior Lien(s) (M949):** Retired June 2016.

**Item 123 - Ever 90+ DPD in the Past 12 months (M950):** Retired March 2020.

#### Line Items 124-128: Commercial, Risk, and Capital Framework Items

**Item 124 - Commercial Loan Flag (M951):** Reports whether the loan is a commercial real estate (CRE) or commercial business purpose loan or transaction. This line item is reserved for certain CRE or commercial business purpose loans secured by 1-4 residential properties where the underlying 1-4 residential loans are required to be reported on Schedule Y-9C as 1-4 residential mortgage loans. Values: 0 = No; 1 = Yes.

**Item 125 - Probability of Default - PD (M114):** Reports the Probability of Default (PD) for the account as defined in the most recent capital framework. Report the PD associated with the account's corresponding segment. Applicable only to firms subject to the advanced approaches rule. Required for BHC/IHC/SLHC-owned loans only. A one in ten probability of default should be reported as 0.1.

**Item 126 - Loss Given Default - LGD (M115):** Reports the Loss Given Default (LGD) for the account as defined in the most recent capital framework. Report the LGD associated to the account's corresponding segment. Applicable only to firms subject to the advanced approaches rule. Required for BHC/IHC/SLHC-owned loans only. A ninety percent loss given default should be reported as 0.9.

**Item 127 - Expected Loss Given Default - ELGD (M116):** Reports the Expected Loss Given Default (ELGD) parameter for the account as defined in the most recent capital framework. Report the ELGD associated to the account's corresponding segment. Missing or unavailable values should be left blank. If the BHC or IHC or SLHC generates this field, they are required to report it. ELGD is an input into the LGD calculation. Report the BHC's, IHC's or SLHC's empirically based best estimate of the long-run default-weighted average economic loss, per dollar of EAD. Applicable only to firms subject to the advanced approaches rule. Required for BHC/IHC/SLHC-owned loans only.

**Item 128 - Exposure at Default - EAD (M117):** Reports the dollar Exposure at Default (EAD) for the account as defined in the most recent capital framework. For open-ended exposures, assign to all accounts in a particular segment the corresponding LEQ, CCF, or related parameters, then calculate account EAD. Abbreviations: LEQ = Loan-equivalent-exposure; CCF = Credit Conversion Factor. Applicable only to firms subject to the advanced approaches rule. Required for BHC/IHC/SLHC-owned loans only.

#### Line Items 129-130: Entity and Portfolio Classification

**Item 129 - Entity Type (M952):** Reports the registered entity type of the BHC, IHC or SLHC subsidiary that owns the reported loan. If the loan is not owned by the BHC or IHC or SLHC or its subsidiaries, report the entity type as "Other." Values: 1=National Bank, 2=State Member Bank, 3=Nonmember Bank, 4=State Credit Union, 5=Federal Credit Union, 6=Non-bank Subsidiary, 0=Other.

**Item 130 - HFI FVO/HFS Flag (M953):** Portfolio HFI FVO / HFS Flag -- Reports whether all portfolio loans are held for investment (HFI) measured at fair value under a fair value option (FVO) or held for sale (HFS). For non-portfolio loans, leave this line item blank.

#### Line Items 131-133: Interest and Product Type

**Item 131 - Interest Only Term - Original (M954):** Reports the number of months where the loan payment is interest only, based on the original loan terms.

**Item 132 - Interest Type - Current (M248):** Reports the loan interest type in the current reporting month. Fixed (1) -- loans where the interest rate is fixed for the entire term. Variable (2) -- loans where the interest rate fluctuates based on a spread to an index.

**Item 133 - Product Type - Origination (M955):** Reports the product type as of the loan origination. Identifies the product type of the mortgage, including the interest type, amortization term and initial fixed period for hybrid products. Detailed code values:
- 1 = Fixed 30 (also includes fixed rate loans with terms >20 and <30 years)
- 2 = Fixed 20 (also includes fixed rate loans with terms >15 and <20 years)
- 3 = Fixed 15
- 4 = ARM 2 (initial reset >1 year and <=2 years)
- 5 = ARM 3 (initial reset >2 years and <=3 years)
- 6 = ARM 5 (initial reset >3 years and <=5 years)
- 7 = ARM 7 (initial reset >5 years and <=7 years)
- 8 = ARM 10 (initial reset >7 years and <=10 years)
- 9 = ARM Other (e.g., Option ARM)
- 10 = Other (e.g., Graduated Payment Mortgages)
- 11 = Fixed 40 (also includes fixed rate loans with terms >30 and <40 years)
- 12 = Fixed Greater than 40
- 13 = Fixed Other (Balloon, interest only, fixed rate pay option loans)
- 14 = Fixed 10 (also includes fixed rate loans with terms <10 years)
- 15 = ARM 1 (initial reset <=1 year)
- 16 = ARM 15 (initial reset >10 years and <=15 years)

#### Line Items 134-138: Credit Bureau Score Metadata

**Item 134 - Origination Credit Bureau Score Vendor (R036):** Lists the vendor of the commercially available credit bureau score reported in item 13. Values: 1=FICO, 2=VantageScore, 3=Other. If Other, report vendor in item 135.

**Item 135 - Origination Credit Bureau Score Version (R037):** Provides the version of the commercially available credit bureau score reported in item 13 (e.g., FICO 08 or VantageScore 3.0). If "Other" was selected in item 134, report the vendor name along with the score version (format: "vendor name - score version").

**Item 136 - Current Credit Bureau Score Vendor (R038):** Lists the vendor of the commercially available credit bureau score reported in item 48. Values: 1=FICO, 2=VantageScore, 3=Other. The current credit bureau score related fields are required for portfolio loans and optional for loans serviced for others.

**Item 137 - Current Credit Bureau Score Version (R039):** Provides the version of the commercially available credit bureau score reported in item 48. The current credit bureau score related fields are required for portfolio loans and optional for loans serviced for others.

**Item 138 - Current Credit Bureau Score Date (S382):** Provides the date on which the commercially available credit bureau score reported in item 48 was obtained. This field must be updated at least one month within the quarter, and refreshed at least one month within every subsequent quarter. Required for portfolio loans, optional for serviced-for-others loans.

#### Line Items 139-141: Servicing and Identification

**Item 139 - Serviced by Others (SBO) Flag (R622):** Indicates the servicer of the loan. Y = loan is serviced by entities other than the BHC or IHC or SLHC or its subsidiary. N = loan is serviced by the BHC or IHC or SLHC or its subsidiary.

**Item 140 - Reporting As of Month Date (R623):** Indicates the reporting as of month date. Generally consistent with the AS_OF_MON_ID used in the file naming convention. However, loans flagged as SBO loans may have a different reporting as of date. Format: YYYYMM.

**Item 141 - National Bank RSSD ID (JA26):** Reports the RSSD ID of the national bank that has a financial interest in the loan. A national bank subsidiary is deemed to have a financial interest if it owns the loan and/or services the loan. For loans serviced by a National Bank subsidiary but owned by another entity, report the RSSD ID of the servicing National Bank. For loans owned by a National Bank but serviced by another entity, report the RSSD ID of the owning National Bank. If no National Bank subsidiary either owns or services the loan, leave blank (null).

#### Line Items 142-144: Payment and Loss Mitigation

**Item 142 - Actual Payment Amount (M259):** Reports the actual dollar amount of the principal and interest payment received in the reporting month, which could include principal curtailments. Do not include fee payments or reversals.

**Item 143 - Workout Type Started (PG60):** Reports the workout type started. Should be coded for any loan where a loss mitigation effort has started or is in progress for the current month. Code in the reporting month when the workout type was started and in subsequent months up to, but not including, the month the workout type was completed. If the workout plan began and ended in the same month, code as 0 and fill out Line 77 (Workout Type Completed). Codes:
- 0 = No Active Workout Plan
- 1 = Modification (started but new loan terms not yet in effect)
- 2 = Repayment Plan (started but not yet completed)
- 3 = Deed in Lieu (started but not yet completed)
- 4 = Short Sale (started but not yet completed)
- 9 = Forbearance (started but not yet completed)
- 10 = MI Claim Advance (started but not yet completed)
- 12 = Other
- 16 = Refinance (started but not yet completed, resulting from loss mitigation)
- 17 = Partial Claim/Junior Lien (started but not yet completed, resulting from loss mitigation)

**Item 144 - Fair Value Amount (PG61):** Reports the current fair value of the loan as of the reporting month if held under the fair value option (FVO) or held for sale (HFS). Should be populated if the value in Field 130 = "Y" (HFI FVO/HFS Flag).

---

### A.2 Portfolio Level Table

The Schedule A.2 Portfolio Level Table provides aggregate portfolio-level summary data. Note that the MDRM code for this table uses the prefix CCFP (rather than CCFL for the loan-level table).

**Item 1 - Portfolio Segment ID (M240):** Reports the portfolio segment. Values: 1=Serviced, 2=Portfolio HFI Purchased Credit Deteriorated, 3=Portfolio HFI FVO / HFS, 4=Other Portfolio.

**Item 2 - Unpaid Principal Balance (M201):** Reports the total principal amount outstanding as of the end of the month for the portfolio segment. The UPB should not reflect any accounting-based write-downs and should only be reduced to zero when the loan has been liquidated (paid-in-full, charged-off, REO sold, or service transferred). Report in millions of dollars.

**Item 3 - Loss / Write-down Amount (M241):** For all active loans, reports all cumulative lifetime write-downs and reversals of loan principal and interest recorded as charge-offs against the Allowance for Credit Losses on Loans and Leases pursuant to FR Y-9C instructions. Also includes all reversals of accrued but not collected interest not directly charged against the Allowance. The loss-write down amount is the cumulative loss or principal write-down, and will equal the charge-offs incurred over the life of the loan. Principal write-downs and losses should be expressed as positive numbers. Report in millions of dollars.
