# FR Y-14M Instructions - Chunk 011
## Schedule B.1 Loan/Line Level Table (continued): Line Items 76-97

This chunk continues the Schedule B (Home Equity Loan and Home Equity Line of Credit) data dictionary, covering Line Items 76 through 97 of the B.1 Loan/Line Level Table.

### Line Item 76: Current Combined LTV (MDRM M266)
Report the current combined LTV. The current combined LTV includes the updated loan-to-value using the current commitment of the HE loan or line. The BHC or IHC or SLHC may use an updated 1st mortgage balance, if available (serviced in house), but is not required to do so. For property value, the BHC or IHC or SLHC should use the most recent estimate of property value. If the BHC or IHC or SLHC has not refreshed the value since loan origination, then use the origination value. If the BHC or IHC or SLHC has updated a property's value as part of a re-subordination process, then it should report the refreshed property value and current LTV along with the valuation method and date of valuation. Provide as a decimal (e.g., 0.51 for 51.1%). Please leave blank if unavailable.

### Line Item 77: Modification Type (MDRM M215)
Report the modification type. This line item should be populated for any loan that is currently operating under modified terms and identifies the specific terms that were altered through loss mitigation efforts.

Modification Type should be filled out for all months the loan is currently operating under modified terms (including the month where Workout Type Completed = 1).

If a loan is not operating under modified terms, this field should be populated as "0 = Loan has not been modified".

Active loss mitigation refers to instances where the loan is currently in loss mitigation, and the servicer is actively pursuing loss mitigation.

Report the code that reflects the current modification arrangement using all information available. If no information is available, code as 99 = Other.

This field will be filled out if Workout Type Completed = 1 (Modification).

**Modification Code Definitions:**
- Code 21 Principal deferral: code this line item if the modification results in deferred principal.
- Code 22 Rate change: code this line item if the modification results in a change in interest rate.
- Code 23 Term extension: code this line item if the modification results in a term extension.
- Code 24 Principal forgiveness: code this line item if the modification results in principal forgiveness.
- Code 25 Recapitalization: code this line item if the modification results in recapitalization. Recapitalization refers to instances where accrued and/or deferred principal, interest, servicing advances, expenses, fees, etc. are capitalized into the unpaid principal balance of the modified loan.
- Codes 27-34 are to be used if a combination of modifications are applied to a loan.

**HELOC Line Renewal (Regular):** Report any lines that have been renewed and contract terms have changed and the borrower meets BHC or IHC or SLHC current credit standards. This code value applies when the borrower has entered into a new contractual obligation with the lender and the HELOC terms have changed.

**HELOC Line Renewal (loss mitigation strategy):** Report any lines that have been renewed and contract terms have changed and the borrower does not meet the current BHC or IHC or SLHC credit standards. This code value applies when the borrower has entered into a new contractual obligation with the lender and the HELOC terms have changed.

### Line Item 78: Last Modified Date (MDRM M216)
Report the date of the most recent modification. This line item should only be populated for loans with a value in Line item 77 Modification Type, indicating that a loan has been modified. For HELOC Line Renewals, the field Modification Type will contain code 13 or 14, and Last Modified Date field will be populated with the line renewal date.

### Line Item 79: Refreshed Property Value (MDRM M209)
Refreshed property value -- Report the most current property value if updated subsequent to loan origination. Only provide a refreshed value when it is based on a property-specific valuation method (i.e., do not provide a refreshed property value based solely on applying a broad valuation index to all properties in geographic area.)

Refreshed values are expected to be populated for modified loans only and the information to be collected at the time modification terms are being set. These are optional for other loans.

Do not report where the refreshed property value was not obtained within the last year.

Line item 79 Refreshed Property Value, line item 80 Refreshed Property Valuation Method, and line item 81 Refreshed Property Valuation Date all refer to the same refreshed property valuation instance. If the property has been valued subsequent to origination, please provide the most recent property valuation date, the valuation method, and the property value.

### Line Item 80: Refreshed Property Valuation Method (MDRM M210)
Report the valuation method for any refreshed values in line item 79. Identifies the method by which the value of the property was determined.

- Full appraisal: Prepared by a certified appraiser and must involve both interior and exterior inspections of the subject property by a licensed appraiser
- Limited appraisal: Prepared by a certified appraiser that obtains characteristics of the property without the licensed appraiser performing a full interior and exterior inspection
- Broker Price Opinion "BPO": Prepared by a real estate broker or agent
- Desktop Valuation: Prepared by bank employee
- Automated Valuation Model "AVM"

The Refreshed Property Value, Refreshed Property Valuation Method, Property Method at Modification, and Most Recent Property Valuation Date line items refer to the same refreshed property valuation instance. If the property has been valued subsequent to origination, then provide the most recent property valuation date, the valuation method, and the property value.

### Line Item 81: Refreshed Property Valuation Date (MDRM M267)
Report the date of the most recent property valuation.

### Line Item 82: Escrow Amount Current (Retired March 2013) (MDRM M268)

### Line Item 83: Loan Purpose Coding (MDRM M161)
Report the purpose for the loan origination. If the loan has multiple purposes, report the primary purpose.

### Line Item 84: Remaining Term (MDRM M198)
Report the remaining term of the loan in months. For HELOC it should be the combined draw period and the repayment period. In the case of commercial loans, report commercial demand loans with a value of NULL.

Note: For the Remaining Term line items in the FR Y-14M First Lien and Home Equity schedules, a value of 0 should be assigned if a loan is past maturity.

### Line Item 85: Bankruptcy Chapter (MDRM M195)
Bankruptcy Chapter - For all the loans with a Bankruptcy Flag, report the Bankruptcy Chapter Type.

Note: If the Bankruptcy Flag line item (Line item 38) is coded with a value of 'N', then the Bankruptcy Chapter line item should be blank, i.e. null value. Do not populate this line item with any other value.

### Line Item 86: Accrual Status (MDRM M957)
Report the accrual status of the loan or line of credit as of the reporting month.

### Line Item 87: Foreclosure Suspended (MDRM M204)
Foreclosure Suspended -- Report all loans where foreclosure activities are being suspended regardless of the reason for suspension. Flag indicating an active foreclosure suspension.

Note: The code value for this line item should follow public reporting (SEC 10-K, etc.) of this item.

### Line Item 88: Property Valuation Method at Origination (appraisal method) (MDRM M940)
Report the method used to determine the property value at time of origination.

- Full Appraisal: Prepared by a certified appraiser and must involve both interior and exterior inspections of the subject property by a licensed appraiser
- Limited Appraisal: Prepared by a certified appraiser that obtains characteristics of the property without the licensed appraiser performing a full interior and exterior inspection
- Broker Price Opinion "BPO": Prepared by a real estate broker or agent
- Desktop Valuation: Prepared by a bank employee or non-appraiser

### Line Item 89: Loss Mitigation Performance Status (MDRM M226)
Loss Mitigation Performance Status -- Report whether a loan is being actively handled by the servicer's loss mitigation department. Refers to all loans where the servicer has initiated loss mitigation procedures whether or not a particular course of action or workout type has been executed. Active loss mitigation refers to instances where the loan is currently in loss mitigation, and the servicer is actively pursuing loss mitigation.

Applies to all loans regardless of workout type (Line item 61 Workout Type Completed/Executed).

**Code value definitions:**
- Not in loss mitigation: If a loan is not in loss mitigation, then it should be coded as "0".
- Active and performing: Refers to any loan that is currently in loss mitigation and is performing to the terms of a selected plan.
- Active and non-performing: Refers to instances where a loan is under a workout plan, as identified in Line item 61 Workout Type Completed/Executed, but borrower has missed at least one payment under the terms of the agreement.
- Broken: Populated for situations where the borrower has defaulted on the terms of loss plan and the servicer has removed the loan from loss mitigation. The broken flag should remain with the account until the loan has been paid-in-full, re-modified, or charged off.

### Line Item 90: Other Modification Action Type (MDRM M958)
Report any modification type not covered by the previous categories. If the loan was modified and none of the categories reflect how the loan was modified, this line item should be "Y"; otherwise, it should be "N".

Report for all loans with a value in Line item 77 Modification Type. Otherwise, leave blank.

Note: The modification action type categories already captured are 71 (Rate Reduction), 72 (Term Modification), 73 (Principal write-down), 57 (Capitalization), 58 (Interest Rate Frozen), 59 (Principal Deferred). If the loan was modified and none of these categories reflect how the loan was modified, this line item should be "Y"; otherwise, it should be "N".

### Line Item 91: Reason for Default
This item has been removed and should not be reported.

### Line Item 92: Third Party Sale Flag (MDRM M941)
Report any third party sales at time of foreclosure sale. Identify any loan where the title has transferred to a party other than the servicer at the time of foreclosure sale. If the loan was not sold to a third party or is not currently in foreclosure this line item should be coded with a zero. For example, if the loan was conveyed from the owner to the lender (or servicer), this would not be considered a Third Party Sale, and this line item should be coded with a zero.

### Line Item 93: Loss/Write down Amount (Retired March 2020) (MDRM M241)

### Line Item 94: Loss/Write down Date (Retired March 2020) (MDRM M947)

### Line Item 95: Unpaid Principal Balance (Net) (MDRM M960)
Report the current net unpaid balance at end of the reporting month rounded to the nearest dollar.

Net Unpaid Principal Balance for a Home Equity loan is the Gross Unpaid Principal Balance minus any charge-offs taken against the loan loss reserve (ACL) for that same loan. The charge-off amount for Net Unpaid Balance is the cumulative charge-off to date for the loan and not the partial charge-off amount for the given reporting month. The Net UPB value from the accounting system may include other adjustments like late fees, annual HELOC fees, deferred costs due to broker commissions and origination costs that have been capitalized for the life of the loan, etc. BHCs, IHCs, and SLHCs should provide whatever net balance is available in their accounting systems and not back out any other adjustments they may have made.

Net UPB is rounded to the nearest dollar. If Net UPB is unknown because the loan is Serviced for Others or for any other reason, this value should be left blank. This value should equal the book value on regulatory filings.

### Line Item 96: Performance of First Lien (Retired June 2016) (MDRM M961)

### Line Item 97: Ever 90+ DPD in the Past 12 months (Retired March 2020) (MDRM M950)

## Schedule B.2 Portfolio Level Table

### Line Item 1: Portfolio Segment ID (MDRM M240)
Report the portfolio segment.

### Line Item 2: Unpaid Principal Balance (MDRM M201)
Unpaid Principal Balance -- Report the total principal amount outstanding as of the end of the month for the portfolio segment. The UPB should not reflect any accounting based write-downs and should only be reduced to zero when the loan has been liquidated -- either paid-in-full, charged-off, REO sold or Service transferred. Report in millions of dollars.

### Line Item 3: Loss / Write-down Amount (MDRM M241)
Loss / Write-down Amount -- For active loans, report all cumulative lifetime write-downs and reversals of loan principal and interest recorded as charge-offs against the allowance for credit losses on loans and leases, as defined in the FR Y-9C glossary entry for "allowance for credit losses on loans and leases". Also include all reversals of accrued but not collected interest, not directly changed against the allowance for credit losses on loans and leases. This field should capture the lifetime loss/write down at time of liquidation or payoff. Principal Write downs and Losses should be expressed as positive numbers. Report in millions of dollars.
