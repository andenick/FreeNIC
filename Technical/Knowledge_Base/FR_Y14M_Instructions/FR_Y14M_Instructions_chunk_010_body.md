# FR Y-14M Instructions - Chunk 010
## Schedule B: Domestic Home Equity Loan and Home Equity Line Data Dictionary (Continued)

### B.1 Loan/Line Level Table (Continued, Items 46-75)

This chunk continues the Schedule B.1 Loan/Line Level Table data dictionary, covering Line Items 46 through 75. These items address credit line management, loan status and delinquency, foreclosure proceedings, loss mitigation, modifications, and HELOC-specific features.

#### Line Items 46-49: Credit Line and Loan Status

**Item 46 - Current Credit Limit (M250):** For lines of credit, reports the total credit line currently available to the borrower. Leave blank for home equity loans.

**Item 47 - Loan Status (MBA method) (M251):** Reports the status of borrower payments (Current, 30, 60, 90, etc.). Also includes indicators for Foreclosure, Bankruptcy, and REO. Code value T=Terminated Reporting captures loans from previous month's submission no longer available in current month (e.g., loans sent to collections but not charged off or transferred). If liquidated by short sale or third party foreclosure sale in the reporting month, report "0". Values: C=Current, 3=30 days, 6=60 days, 9=90+ days, F=FC, R=REO, T=Terminated Reporting, S=Servicing Sold Release, 0=Paid off, U=Unknown.

**Item 48 - Foreclosure Referral Date (M203):** Reports the date the loan was referred to an attorney for initiating foreclosure proceedings. Should reflect the referral date of currently active foreclosure process. Loans cured from foreclosure should not have a referral date. Format: YYYYMMDD.

**Item 49 - Foreclosure Sale Date (M202):** Reports the date the foreclosure sale occurs on the subject property, typically the end of the foreclosure process unless the borrower is in a state with right of redemption. If a loan is not in foreclosure, leave blank (null). Populate for any loan that has completed foreclosure sale whether or not the title was acquired by the bank.

#### Line Items 50-54: Prepayment, Foreclosure, and Liquidation

**Item 50 - Pre-Payment Penalty Flag (M187):** Reports whether the loan carries a penalty if the borrower prepays during a specified period. Values: Y=Yes, N=No, U=Unknown.

**Item 51 - Pre-Payment Penalty Term (M188):** Reports the time period in months from loan origination that a prepayment penalty applies. This is an origination line item and should not change with the reporting month.

**Item 52 - Paid-in-full Coding (M205):** Retired March 2013.

**Item 53 - Foreclosure Status (M206):** Reports the current foreclosure status as of end of reporting month:
- 0 = Not in foreclosure
- 1 = In foreclosure, pre-sale (referred to attorney but not yet at foreclosure sale)
- 2 = Post-sale foreclosure, Redemption, non-REO (title obtained but property not yet marketed; if unavailable, code as REO; in month loan liquidates, code as '2')
- 3 = REO (title obtained and property on market/available for sale)

**Item 54 - Liquidation Status (M252):** Provides the liquidation method for any loan liquidated during the reporting month:
- 0 = Not paid-in-full (outstanding balance or active line of credit)
- 1 = Voluntary payoff (paid in full by borrower through refinance, sale, or principal payment)
- 2 = Involuntary liquidation/foreclosure (includes short-sales, charge-offs, REO liquidations)
- 3 = Servicing transfer (servicing transferred or sold to another institution)

#### Line Items 55-60: TDR, Modifications, and Credit Status

**Item 55 - Troubled Debt Restructure Date (N185):** Reports the date the loan was classified as a Troubled Debt Restructuring (TDR) as defined in the FR Y-9C Glossary. Reportable for the duration of TDR designation; if the loan is no longer designated as TDR, discontinue reporting.

**Item 56 - Repayment Plan Performance Status (M219):** Retired March 2020.

**Item 57 - Capitalization (M222):** Retired September 2022.

**Item 58 - Interest Rate Frozen (M232):** Reports on all loans where a floating interest rate was frozen at a fixed rate. If the loan was an adjustable rate and converted to fixed rate during modification, code "Y"; otherwise "N".

**Item 59 - Principal Deferred (M227):** Reports on any loans where principal payment or amortization has been deferred to a later date during modification process. Code "Y" if deferred; otherwise "N".

**Item 60 - Purchased Credit Deteriorated Status (M234):** Reports whether any loans are accounted for as purchased-credit deteriorated. If PCD loan, code "Y"; otherwise "N". None of the records should be left blank.

#### Item 61: Workout Type Completed

**Item 61 - Workout Type Completed (M218):** Reports the type of loss mitigation activity that has been successfully completed in the current month. Successful completion means closing of loss mitigation activities where the borrower has no remaining delinquent obligations. Code only in the reporting month when completed, not in subsequent months. If loss mitigation efforts are ongoing, leave blank. If never in loss mitigation, leave blank. If loss mitigation efforts fail, report 61=0 and 89-Loss Mitigation Status=3 (Broken). Codes:
- 0 = No Workout Plan Performed
- 1 = Modification (completed, new terms in effect; do not include stip-to-mod, use code 5 for those)
- 2 = Payment Plan
- 3 = Deed in Lieu
- 4 = Short Sale
- 5 = Stipulated Repayment / stip to mod (Retired; includes Home Affordable Modification program loans)
- 6 = Do not Use
- 7 = Settlement (agreement to accept less than contractually owed as payment in full)
- 8 = Other (e.g., strategic refinances or changes to balloon payments not under modification agreements)
- 9 = Forbearance Plan
- 16 = Refinance (resulting from loss mitigation)
- 17 = Partial Claim/Junior Lien (resulting from loss mitigation)

#### Line Items 62-68: Home Equity Specific Items

**Item 62 - First Mortgage Serviced In House (M253):** Reports whether the first mortgage associated with the home equity loan/line is serviced by the bank. Leave blank for first lien home equities. Values: N=No, Y=Yes.

**Item 63 - Settlement Negotiated Amount (M254):** Reports the settlement amount (portion of outstanding UPB) agreed to be paid by the customer. Populate for any loan/line where "Settlement" is selected under Workout Type Completed.

**Item 64 - Credit Line Frozen Flag (M255):** Reports whether the line of credit is frozen in the reporting month. Identifies any line in its draw period where the credit line has been temporarily frozen, allowing no further draws. Continue coding "Y" for each month the line remains frozen until paid in full or reinstated. Leave blank for home equity loans. Note: Frozen is temporary (due to decreased property value or short-term delinquency) and different from "closed."

**Item 65 - Locked Amount - Amortizing - LOC (M256):** For lines of credit, reports the total dollar amount of outstanding principal balance that has been "locked" and is now amortizing under independent loan terms. Leave blank for home equity loans and lines without lockout feature. If lockout feature exists but no balance locked, report zero.

**Item 66 - Locked Amount - Interest Only - LOC (M257):** For lines of credit, reports the total dollar amount of outstanding principal balance locked as interest only under independent terms. Same blank/zero rules as Item 65.

**Item 67 - Repayment Plan Start Date (M258):** Retired March 2020.

**Item 68 - Actual Payment Amount (M259):** Reports the actual dollar amount of principal and interest payment received in the reporting month. Do not include fee payments.

#### Line Items 69-75: LOC Features and Modifications

**Item 69 - Lockout Feature Flag (M260):** Reports whether the line of credit has a "lock-out" feature whereby a portion of the outstanding principal balance may be locked into an amortizing or interest only loan with separate terms. Leave blank for home equity loans. For HELOCs, only use "Y" or "N".

**Item 70 - Credit Line Closed Flag (M261):** Reports any line of credit in its draw period that has been closed, allowing no further draws. The status should remain until paid in full. Leave blank for home equity loans. Note: A closed line means the borrower will never regain use of the draw (distinct from "frozen").

**Item 71 - Interest Rate Reduced (M262):** Retired September 2022.

**Item 72 - Term modification (M263):** Reports whether the loan has been through a term modification (change to rate reset date, balloon feature, and/or maturity date). Code "Y" if modified; otherwise "N". None of the records should be left blank.

**Item 73 - Principal Write-down (M229):** Reports all loans where an adjustment to the unpaid principal balance has occurred through modification. Code "Y" if adjustment occurred; otherwise "N". Only for loans that have undergone a reduction in outstanding principal due to modification or loss mitigation activity. Should only be populated for loans also identified as modifications by the Modification Type field.

**Item 74 - Line Re-age (M264):** Reports whether the line of credit has been re-aged (delinquency status changed by collections or customer service as part of loss mitigation) but terms not formally modified. Code "Y" for re-aged lines not in active loss mitigation. Code "N" for modified but not re-aged lines. Leave blank if neither modified nor re-aged, or if this is a loan. Items 74 and 75 should carry forward from month to month reflecting the inventory of re-ages and extensions. Do not count holiday extensions as "Y".

**Item 75 - Loan Extension (M265):** Reports whether the home equity loan has been extended but terms not formally modified. Code "Y" for extended loans not in active loss mitigation. For loans in loss mitigation where amortization term is being changed, those should be captured under the Modification field. Leave blank for lines.
