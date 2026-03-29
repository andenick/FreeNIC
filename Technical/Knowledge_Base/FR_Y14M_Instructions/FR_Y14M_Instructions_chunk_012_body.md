# FR Y-14M Instructions - Chunk 012
## Schedule B.1 Loan/Line Level Table (concluded): Line Items 98-120

This chunk concludes the Schedule B.1 (Home Equity Loan/Line Level) data dictionary, covering Line Items 98 through 120.

### Line Item 98: Entity Serviced (MDRM M945)
Report the Federal Regulator of the BHC or IHC or SLHC subsidiary that is servicing the loan. If the loan is a commercial loan secured by residential real estate loans, report the Federal Regulator of the entity servicing the commercial loan.

Example: The 'Entity Serviced' should be segmented out by the entities within the BHC or IHC or SLHC. If the loan is serviced by a national bank, then the Entity Serviced is OCC (code value = 2). If the loan is serviced by a state nonmember bank, then the 'Entity Serviced' is FDIC (code value = 3). If the loan is serviced by a state member bank or a subsidiary of a BHC or IHC or SLHC that is not a federally insured bank, then the 'Entity Serviced' is FRB (code value = 1).

### Line Item 99: Total Debt at Time of any Involuntary Termination (MDRM M235)
Report the total debt at the time of any involuntary termination. Total debt should be reported at gross, not net values, and is comprised of:
1. Unpaid Principal Balance;
2. Interest pass through Amount (interest paid to the Investor to purchase loan out of pool or any prior year's interest charged-off at non-accrual status). This field will be used primarily for loans in private securitizations and should capture any interest that was passed through to investors, while the loan was non-performing, that would have to be recouped from the proceeds of a property sale before applying those proceeds to recovery of principal.;
3. Total Corporate Advance (incl. Property Preservation and Attorney's fees);
4. Total Escrow Advance (taxes and insurance paid)

Note: Any involuntary termination includes REO, short sale, deed-in-lieu of foreclosure, third party sale or charge-off. Do not include any write-downs prior to termination. If a loan goes through a foreclosure sale and comes into REO, report the aggregate of the various stages of the process.

Use Field #99 to record the total debt. If the loan is not totally charged off, use Field #100 Net Recovery Amount to record any recoveries on the loan at termination. If the recovery amount is unknown at the time the loan is last reported, leave the net recovery amount NULL.

This line item is a required line item for portfolio loans and best efforts for all others. Report NULL for any junior liens.

### Line Item 100: Net Recovery Amount (MDRM M236)
Report the cumulative recovery amount at the time the loan terminates. For first lien, this is computed as sales price net of costs of sales (e.g., sales commissions and buyer concessions.)

Use Field #99 to record the total debt. If the loan is not totally charged off, use Field #100 Net Recovery Amount to record any recoveries on the loan at termination. If the recovery amount is unknown at the time the loan is last reported, leave the net recovery amount NULL.

Note: Since net proceeds should be the same as Net Recovery Amount, report net proceeds in this line item for short sales and third party sales, along with all other involuntary terminations. Since the net recovery amount cannot be computed until the loan has been sold (or charged off), you need to also obtain the sales price the property sold at and place the sales price of the property in Line item 'Sales Price of Property'.

This line item is a required line item for portfolio loans and best efforts for all others. Report NULL for any junior liens.

### Line Item 101: Sales Price of Property (MDRM M948)
Report the final sales price at which the property was disposed by the BHC or IHC or SLHC in the case of involuntary termination. Provide the same price as the BHC or IHC or SLHC would submit to public records data.

In cases in which the home equity lender decides not to pursue recourse to the property collateral, or charges off a loan completely, report a 0 (zero) for this field.

Note: This line item is a required line item for portfolio loans and best efforts for all others. Report NULL for any junior liens.

### Line Item 102: Commercial Loan Flag (MDRM M951)
Report whether the loan is a commercial real estate (CRE) or commercial business purpose loan or transaction.

This line item is reserved for certain CRE or commercial business purpose loans secured by 1-4 residential properties where the underlying 1-4 residential loans are required to be reported on Schedule Y-9C as 1-4 residential mortgage loans. While the purpose of the transaction is commercial, Y-9C requires any 1-4 family residential loans securing the transaction to be reported as a 1-4 residential properties.

### Line Item 103: Probability of Default - PD (MDRM M114)
Report the Probability of Default (PD) for the account as defined in the most recent capital framework. More specifically, report the PD associated with the account's corresponding segment.

Note: Applicable only to firms subject to the advanced approaches rule. This item is required for BHC or IHC or SLHC-owned loans only.

### Line Item 104: Loss Given Default - LGD (MDRM M115)
Report the Loss Given Default (LGD) for the account as defined in the most recent capital framework. More specifically, report the LGD associated to the account's corresponding segment.

Note: Applicable only to firms subject to the advanced approaches rule. This item is required for BHC or IHC or SLHC-owned loans only.

### Line Item 105: Expected Loss Given Default - ELGD (MDRM M116)
Report the Expected Loss Given Default (ELGD) parameter for the account as defined in the most recent capital framework. More specifically, report the ELGD associated to the account's corresponding segment. Missing or unavailable values should be left blank.

If the BHC or IHC or SLHC generates this field, they are required to report it. ELGD is an input into the LGD calculation.

For ELGD, report the BHC's, IHC's or SLHC's empirically based best estimate of the long-run default-weighted average economic loss, per dollar of EAD, the BHC or IHC or SLHC would expect to incur if the obligor (or a typical obligor in the loss severity grade assigned by the bank to the exposure or segment) were to default within a one-year horizon, which is a floor for the Basel risk parameter LGD under the Rule. If the BHC or IHC or SLHC does not capture this field, then leave it blank.

Note: Applicable only to firms subject to the advanced approaches rule. This item is required for BHC or IHC or SLHC-owned loans only.

### Line Item 106: Exposure at Default - EAD (MDRM M117)
Report the dollar Exposure at Default (EAD) for the account as defined in the most recent capital framework. More specifically, report the EAD associated to the account's corresponding segment. In particular, for open-ended exposures assign to all the accounts in a particular segment the corresponding LEQ, CCF, or related parameters, associated with that segment. After the corresponding parameter is assigned to each account, calculate the account EAD and report this as the variable value.

Note: Applicable only to firms subject to the advanced approaches rule. This item is required for BHC or IHC or SLHC-owned loans only.

Abbreviations:
- LEQ: Loan-equivalent-exposure
- CCF: Credit Conversion Factor

### Line Item 107: Entity Type (MDRM M952)
Report the registered entity type of the BHC or IHC or SLHC subsidiary that owns the reported loan. If the loan is not owned by the BHC or IHC or SLHC or its subsidiaries, report the entity type as 'Other.'

### Line Item 108: HFI FVO/HFS Flag (MDRM M953)
Portfolio HFI FVO / HFS -- Report whether all portfolio loans held for investment (HFI) measured at fair value under a fair value option (FVO) or held for sale (HFS).

Note: For non-portfolio loans leave this line item blank.

### Line Item 109: Origination Credit Bureau Score Vendor (MDRM R036)
List the vendor of the commercially available credit bureau score reported in item 13. If the vendor of the commercially available credit score reported in item 13 is not among those listed, please select "Other" and report the vendor in item 110. List the version of the credit score in item 110. Note that scores which do not meet the definition of a commercially available credit bureau score as set forth in the General Instructions may be treated as missing data by the Federal Reserve.

### Line Item 110: Origination Credit Bureau Score Version (MDRM R037)
Provide the version of the commercially available credit bureau score reported in item 13 (for example, FICO 08 or VantageScore 3.0). If "Other" was selected in item 109, please report the vendor name along with the schedule version (in the format "vendor name - score version").

### Line Item 111: Current Credit Bureau Score Vendor (MDRM R038)
List the vendor of the commercially available credit bureau score reported in item 14. If the vendor of the commercially available credit score reported in item 14 is not among those listed, please select "Other" and report the vendor in item 112. List the version of the credit score in item 112. Note that scores which do not meet the definition of a commercially available credit bureau score as set forth in the General Instructions may be treated as missing data by the Federal Reserve.

The current credit bureau score related fields are required for portfolio loans and optional for loans that the BHC, IHC or SLHC services for others.

### Line Item 112: Current Credit Bureau Score Version (MDRM R039)
Provide the version of the commercially available credit bureau score reported in item 14 (for example, FICO 08 or VantageScore 3.0). If "Other" was selected in item 111, please report the vendor name along with the schedule version (in the format "vendor name - score version").

The current credit bureau score related fields are required for portfolio loans and optional for loans that the BHC, IHC or SLHC services for others.

### Line Item 113: Current Credit Bureau Score Date (MDRM S382)
Provide the date on which the commercially available credit bureau score reported in item 14 was obtained.

This field must be updated at least one month within the quarter, and refreshed at least one month within every subsequent quarter.

The current credit bureau score related fields are required for portfolio loans and optional for loans that the BHC, IHC or SLHC services for others.

### Line Item 114: Serviced by Others (SBO) Flag (MDRM R622)
Indicates the servicer of the loan. If the loan is serviced by entities other than the BHC or IHC or SLHC or its subsidiary, use a code of Y. If the loan is serviced by the BHC or IHC or SLHC or its subsidiary, use a code of N.

### Line Item 115: Reporting As of Month Date (MDRM R623)
Indicate the reporting as of month date.

Note: This field will generally be consistent with the AS_OF_MON_ID used in the file naming convention. However, loans that are flagged as SBO loans may have a different reporting as of date. Use this field to code the reporting as of date for all loans.

### Line Item 116: Payment Type at the end of draw period (MDRM R624)
Report how borrowers are required to repay any principal outstanding at the end of the Allowable Draw Period.

### Line Item 117: National Bank RSSD ID (MDRM JA26)
Report the RSSD ID of the national bank that has a financial interest in the loan. For these purposes, a national bank subsidiary is deemed to have a financial interest in a loan if it owns the loan and/or services the loan.

For loans that are serviced by a National Bank subsidiary of the BHC but owned by another entity, the respondent should report the RSSD ID of the National Bank subsidiary that services the loan. For loans that are owned by a National Bank subsidiary of the BHC but serviced by another entity, the respondent should report the RSSD ID of the National Bank subsidiary that owns the loan. If a National bank subsidiary of the BHC both owns and services the loan, the respondent should report the RSSD ID of the National Bank subsidiary that both owns and services the loan. If no National Bank subsidiary of the reporting BHC either owns or services the loan, this field should be left blank (null). In all cases, this field either would be left null or will contain the RSSD ID of a chartered national bank that is a subsidiary of the reporting BHC.

### Line Item 118: Charge-off Amount (MDRM LE95)
Cumulative amount charged off as of most recent charge-off event.

If the account has experienced any charge-off, report the most recent cumulative dollar amount charged-off. Continue to report that same value each month unless another charge-off event occurs. If another charge-off event occurs, update the charge-off amount and date. The cumulative charge-off amount can increase or decrease, depending on the nature of the charge-off adjustment. If the account has not been charged-off, do not report a value.

### Line Item 119: Charge-off Date (MDRM LE96)
Report the date of the most recent charge-off event for the account.

If the account has experienced a charge-off event, report the most recent date a charge-off occurred. If the account has not been charged-off, do not report a value.

### Line Item 120: Workout Type Started (MDRM PG60)
Report the workout type started. This line item should be coded for any loan where a loss mitigation effort has started in the current month.

The line item should be coded in the reporting month when the workout type was started and in subsequent months up to, but not including, the month the workout type was completed.

If the workout plan began and ended in the same month, code this field as 0 and fill out Line 61 - Workout Type Completed.
