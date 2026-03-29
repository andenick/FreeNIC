# FR Y-14Q Instructions -- Schedule H.2 Commercial Real Estate Data Fields (Fields 59-67)

## H.2 CRE Field Specifications (continued)

### Field 59 -- Participation Interest (ParticipationInterest)
- For participated or syndicated credit facilities, report the percentage of the total loan commitment held by the BHC or IHC or SLHC.
- If the credit facility is not participated or syndicated, report 1.
- **Format**: Express as a decimal to 4 decimal places (e.g., 0.05% is 0.0005). Use decimal format; do not use scientific notation.
- **Mandatory**

### Field 60 -- Leveraged Loan Flag (LeveragedLoanFlag)
- Indicate '2' (Yes) if the credit facility is defined as a leveraged loan per criteria in the reporting entity's internal risk management framework developed pursuant to SR 13-3 (Interagency Guidance on Leveraged Lending).
- **Values**: 1 = No; 2 = Yes
- **Mandatory**

### Field 61 -- Disposition Flag (DispositionFlag)
- Report the disposition method for any credit facility that was disposed during the reporting quarter.
- If the BHC or IHC or SLHC is still pursuing payment of principal, interest or fees, report as option 0.
- Rebookings/restructures where loan amounts are transferred or combined between obligations should be reported as either option 1 (Payoff) or option 2 (Involuntary payoff) depending on the occurrence of default.
- **Values**:
  - 0 = Active -- Report for all credit facilities required to be reported in this data collection and do not meet the definitions of options 1 through 7 as of the reporting date.
  - 1 = Payoff -- Credit facility paid in full by the borrower, or undrawn credit facility reaches maturity and is not renewed.
  - 2 = Involuntary Payoff -- Credit facility paid in full after the occurrence of default per terms of credit agreement.
  - 3 = Involuntary Liquidation -- Credit facility liquidated through foreclosure proceedings or another settlement option resulting in incomplete repayment of principal. Includes short-sales, charge-offs, REO, and instances where credit has been resolved but not through foreclosures, servicing transfers, or payments.
  - 4 = Sold or fully participated -- Loan sold or participated to another institution during reporting quarter.
  - 5 = Below reporting threshold -- Credit facility fell below $1 million reporting threshold.
  - 6 = Transfer to another Y-14 schedule -- Indicate schedule in Field 62 below.
  - 7 = Expired Commitment to Commit
- **Mandatory**

### Field 62 -- Disposition Schedule Shift (DispositionScheduleShift)
- For credit facilities reported with option 6 (Transfer to another Y-14 schedule) in Field 61, indicate the Y-14 report, schedule, and sub-schedule to which the credit facility shifted.
- **Format examples**:
  - If transferred to FR Y-14Q Schedule H.1 Corporate Loans, report "Q.H.1"
  - If transferred to FR Y-14M Schedule A.1 Domestic First Lien Closed-end 1-4 Family Residential Loan Data Dictionary, report "M.A.1"
- **Mandatory**

### Field 63 -- ASC326-20 (ASC32620)
- Report the allowance for credit losses per ASC 326-20.
- Provide at the credit facility level if available otherwise report a pro-rated allocation from the collective (pool).
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar signs, commas, or decimals. Should be 0 if there is no ASC326-20 Reserve for the loan.
- **Mandatory**

### Field 64 -- Purchased Credit Deteriorated Noncredit Discount (PCDNoncreditDiscount)
- If the facility is a purchased credit-deteriorated (PCD) asset, report the noncredit discount (or premium) resulting from its acquisition (ASC 326-20-30-13).
- Provide at the credit facility level if available, otherwise report a pro-rated allocation from the collective (pool) basis.
- Leave Blank if the facility is not considered a PCD asset.
- **Format**: Rounded whole dollar amount. No dollar signs, commas, or decimals.
- **Mandatory**

### Field 65 -- Current Maturity Date (CurrentMaturityDate)
- Report the maturity date as the last date upon which the funds must be repaid, exclusive of extension options.
- For demand loan, enter '9999-01-01'.
- For commitments to commit, report the estimated maturity date based on the tenor in the terms extended to the borrower.
- **Format**: yyyy-mm-dd
- **Mandatory**

### Field 66 -- Committed Exposure Global Par Value
- For held for sale loans and loans accounted for under a fair value option, report the total commitment amount as the amount the obligor is contractually allowed to borrow according to the credit agreement for the entire credit facility.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.
- **Mandatory**

### Field 67 -- Outstanding Balance Par Value
- For held for sale loans and loans accounted for under a fair value option, report the outstanding funded exposure.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.
- **Mandatory**
