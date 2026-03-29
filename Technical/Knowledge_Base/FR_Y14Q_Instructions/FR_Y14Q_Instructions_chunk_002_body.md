# FR Y-14Q Instructions - Chunk 002
## Schedule A - Retail

### A.1 - International Auto Loan

This section provides general guidance and data definitions for the International Auto Loan Worksheet. In this worksheet, include international auto loans as defined in the FR Y-9C, Schedule HC-C, item 6.c and international auto leases as defined in the FR Y-9C, Schedule HC-C, item 10.a. For Summary Variable line items #10 & #11 include all repossessed international auto loans as defined in the FR Y-9C, Schedule HC-F, item 6. Include only "managed" (securitized or non-securitized) loans, where "managed" refers to loans originated by the BHC or IHC or SLHC, including securitized loans put back on the books due to ASC Topics 860 and 810 (FAS 166/167). Do not include loans that were originated by a third party and only serviced by the BHC or IHC or SLHC. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option. For the US Auto Loan Worksheet, see instructions for Worksheet 2.

Segment the portfolio along all combinations of the segment variables listed in Section A below. There are three product type segments, three original industry standard credit score or equivalent segments, six delinquency status segments, and four geography segments; therefore, the portfolio must be divided into a total of 3*3*6*4 = 216 distinct segments. Each segment should be identified by a unique eight-digit segment ID (variable name: SEGMENT_ID) based on the segment ID positions and attribute codes listed in Table A.1.a. For example, the segment containing new auto loans (product type segment "01") that had an origination FICO score or equivalent of greater than 620 (origination industry standard credit score or equivalent "02"), are 120+ DPD (delinquency status segment "06"), and where the borrowers reside in the Asia Pacific region (geography segment "04") should be identified by the segment ID "01020604". When reporting the segment ID, do not drop leading zeroes.

For each month in the required reporting period, report the summary variables listed below in Section B for each of the 216 portfolio segments described above. First time filers must submit all data for each month from January 2007 to the end of the current reporting period; returning filers must submit all data for each month in the current reporting period. Start each row of data with your BHC or IHC or SLHC name (Variable name: BHC_NAME), your RSSD ID number (Variable name: RSSD_ID), the reporting month (Variable name: REPORTING_MONTH), and the portfolio ID (Variable name: PORTFOLIO_ID) and segment ID (variable name: SEGMENT_ID). Use the portfolio ID "IntAuto" for this worksheet. For each row, populate the segment variables listed in Table A.1.a and the summary variables listed in Table A.1.b. Provide all dollar amounts in millions.

**Note:** For Summary Variable line items (items 20-23) use the loan level parameters defined in the most recent capital framework for all accounts in a specific segment and calculate the account weighted average. Each month's parameters need to be calculated specific to that month.

If Basel data are not refreshed monthly, use the appropriate Basel data from the prior quarter. For example, if the Basel data are not refreshed until the third month of a quarter, use the Basel data for the prior quarter for the first two months of the next reporting quarter.

#### A. Segment Variables

Segment the portfolio along the following segment variables as described above. For each resulting segment, report the summary variables described in Section B.

1. **Product type** - Segment the portfolio into the following product types.
   - 01 - New auto loans
   - 02 - Used auto loans
   - 03 - Auto leases

2. **Original commercially available credit bureau score or equivalent** - Segment the portfolio by the credit score of the borrower at origination using a commercially available credit bureau score (e.g. FICO Score, VantageScore, or another qualifying credit score). If the underwriting decision was based on an internal score and a commercially available credit bureau score was not available at origination, please map this internal score to an industry standard credit score. Please provide supporting documentation listing the credit score supplied or mapped to.
   - 01 - <=620
   - 02 - >620
   - 03 - N/A - Original credit score is missing or unknown

3. **Delinquency status** - Segment the portfolio into the following six delinquency statuses:
   - 01 - Current: Accounts that are not past due (accruing and non-accruing) as of month-end.
   - 02 - 1-29 days past due (DPD): Accounts that are 1 to 29 days past due (accruing and non-accruing) as of month-end.
   - 03 - 30-59 DPD: Accounts that are 30 to 59 days past due (accruing and non-accruing) as of month-end.
   - 04 - 60-89 DPD: Accounts that are 60 to 89 days past due (accruing and non-accruing) as of month-end.
   - 05 - 90-119 DPD: Accounts that are 90 to 119 days past due (accruing and non-accruing) as of month-end.
   - 06 - 120+ DPD: Accounts that are 120 or more days past due (accruing and non-accruing) as of month-end.

4. **Geography** - Segment the portfolio into the following four geographical area designations. The borrower's current place of residency should be used to define the region.
   - 01 - Canada
   - 02 - EMEA - Europe, Middle East, and Africa
   - 03 - LATAM - Latin America and Caribbean
   - 04 - APAC - Asia Pacific

#### B. Summary Variables

For each month in the reporting period, report the following summary variables for each segment described in Section A.

When reporting $ Vehicle Type (lines 5-8), vehicles should be classified for the purpose of this schedule by body style; however, a luxury vehicle may include all body styles that meet the qualification of a high cost vehicle that aspires to provide drivers with the peak of driving comfort and performance. A luxury vehicle may be manufactured by a conventional automobile manufacturer but still be considered a luxury vehicle if it meets the standards of high price as compared to conventional vehicles and peak driving performance and comfort.

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total unpaid principal balance for accounts on the book for the segment reported as of month-end.
3. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
4. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **$ Vehicle type car/van** - The unpaid principal balance in the portfolio with vehicle type classified as "car/van" for the segment as of month-end.
6. **$ Vehicle type SUV/truck** - The unpaid principal balance in the portfolio with vehicle type classified as "SUV/truck" for the segment as of month-end.
7. **$ Vehicle type sport/luxury/convertible** - The unpaid principal balance in the portfolio with vehicle type classified as "sport/luxury/convertible" for the segment as of month-end.
8. **$ Vehicle type unknown** - The unpaid principal balance in the portfolio with vehicle type classified as "unknown" for the segment as of month-end.
9. **$ Repossession** - The unpaid principal balance of loans still on the books whose vehicles have been repossessed for the segment as of month-end. This field captures the stock of repos.
10. **$ Current month repossession** - The unpaid principal balance of loans still on the books whose vehicles were newly repossessed in the given month for the segment as of month-end. This field captures the flow of repos in the current month, and should include both active and charged-off loans.
11. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower (see the variable $ Bankruptcy Charge-offs). The amount reported here should be consistent with the amount reported on Schedule HI-B, Part I, Column A of the FR Y-9C. For the Delinquency Status segment, categorize charged-off loans by their delinquency status at charge-off. Charge-offs should be performed per loss recognition policy consistent with the FFIEC Uniform Retail Credit Classification and Account Management Policy.
12. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month. The amount reported here should be consistent with the amount reported on Schedule HI-B, Part I, Column A of the FR Y-9C. For the Delinquency Status segment, categorize charged-off loans by their delinquency status at charge-off.
13. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off, including recoveries on acquired loans/portfolios. The amount reported here should be consistent with the amount reported on Schedule HI-B, Part I, Column B of the FR Y-9C for the corresponding time period. For the Delinquency Status segment, categorize charged-off loans by their delinquency status at charge-off. Reversals of recoveries should be recorded as negative recoveries.
14. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries in the reporting month on loans in the segment that were previously charged-off. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
15. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ net charge-offs equals [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries], provide the value of $ net charge-offs minus [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries] in this variable. As a separate document included in the submission, provide an explanation for such a difference (for example, fraud losses are also included in the BHC's or IHC's or SLHC's $ net charge-offs variable). If the adjustment factor variable represents more than one factor leading to the difference, provide a separate breakout of the multiple factors.
16. **$ Ever 30DPD in the last 12 months** - The total unpaid principal balance for the segment as of month-end that was 30 or more days past due at any given time in the twelve months ending in the reference month.
17. **$ Ever 60DPD in the last 12 months** - The total unpaid principal balance for the segment as of month-end that was 60 or more days past due at any given time in the twelve months ending in the reference month.
18. **Projected value** - Total projected value of lease at termination. Only calculated for leased vehicles.
19. **Actual sale proceeds** - Sales proceeds from terminated leases. Only calculated for leased vehicles.
20. **Probability of Default (PD)** - Report the average Probability of Default (PD) as defined in the most recent capital framework for accounts within the segment. More specifically, use the PD associated with each account's corresponding segment and then calculate the account weighted average PD of all the accounts in this specific Y-14Q segment. Note: Applicable only to the advanced approaches reporting banks. A one in ten probability of default should be reported as 0.1.
21. **Loss Given Default (LGD)** - Report the Loss Given Default (LGD) as defined in the most recent capital framework for accounts within the segment. More specifically, use the LGD associated with each account's corresponding segment and then calculate the account weighted average LGD of all the accounts in this specific Y-14Q segment. Note: Applicable only to the advanced approaches reporting banks. A ninety percent loss given default should be reported as 0.9.
22. **Expected Loss Given Default (ELGD)** - Report the Expected Loss Given Default (ELGD) as defined in the most recent capital framework parameter for accounts within the segment. More specifically, use the ELGD associated with each account's corresponding segment and then calculate the account weighted average ELGD of all the accounts in this specific Y-14Q segment. Missing or unavailable values should be reported as null. Note: Applicable only to the advanced approaches reporting banks. A ninety percent expected loss given default should be reported as 0.9.
23. **Risk-Weighted Asset (RWA)** - Report the aggregate dollar Risk Weighted Asset (RWA) for accounts within the segment as defined in the most recent capital framework. More specifically, calculate the RWA associated with each account based on the IRB Risk-Based Capital Formula and then calculate the account weighted average RWA of all the accounts in this specific Y-14Q segment. Note: Applicable only to banks subject to the advanced approaches rule. This item is required for BHC or IHC or SLHC-owned loans only.
24. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end. It should reflect the weighted average of time to principal actual repayment (as modeled) for all positions in the segment, rounded to the nearest monthly term.

---

### A.2 - US Auto Loan

This section provides general guidance and data definitions for the US Auto Loan Worksheet. For the International Auto Loan Worksheet, see the instructions for Worksheet 1. In this worksheet, include all domestic auto loans as defined in the FR Y-9C, Schedule HC-C, item 6.c and domestic auto leases as defined in the FR Y-9C, Schedule HC-C, item 10.a. For Summary Variable line items 10 & 11 include all repossessed auto loans as defined in the FR Y-9C, Schedule HC-F, item 6. Include only "managed" (securitized or non-securitized) loans, where "managed" refers to loans originated by the BHC or IHC or SLHC, including securitized loans put back on the books due to FAS 166/167 (ASC Topics 860 and 810). Do not include loans that were originated by a third party and only serviced by the BHC or IHC or SLHC. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations of the segment variables listed in Section A below. There are three product type segments, six age segments, four original LTV segments, six original industry standard credit score or equivalent segments, six geography segments, and five delinquency status segments; therefore, the portfolio must be divided into a total of 3*6*4*6*6*5 = 12,960 distinct segments. Each segment should be identified by a unique twelve-digit segment ID (variable name: SEGMENT_ID) based on the segment ID positions and attribute codes listed in Table A.2.a.

For each month in the required reporting period, report the summary variables listed below in Section B for each of the 10,800 portfolio segments described above. First time filers must submit all data for each month from January 2007 to the end of the current reporting period; returning filers must submit all data for each month in the current reporting period. Start each row of data with your BHC or IHC or SLHC name (Variable name: BHC_NAME), your RSSD ID number (Variable name: RSSD_ID), the reporting month (Variable name: REPORTING_MONTH), and the portfolio ID (Variable name: PORTFOLIO_ID). Use the portfolio ID "Auto" for your Portfolio ID within this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into the following product types:
   - 01 - New auto loans
   - 02 - Used auto loans
   - 03 - Auto leases

2. **Age** - Refers to the time that has elapsed since the loan was originated. If there were multiple disbursements tied to an original then use the time since the first disbursement. There are six possible ages to report:
   - 01 - 5 years <= Age
   - 02 - 4 years <= Age < 5 years
   - 03 - 3 years <= Age < 4 years
   - 04 - 2 years <= Age < 3 years
   - 05 - 1 year <= Age < 2 years
   - 06 - Age < 1 year

3. **Original LTV** - Segment the portfolio into the loan to value ratio at origination (calculated using the wholesale price of the vehicle). Please round any LTV ratios up to the next integer (LTV 90.01-90.99 to 91). Please break into the following segments:
   - 01 - <= 90
   - 02 - 91-120
   - 03 - > 120
   - 04 - N/A - Original LTV is missing or unknown

4. **Original commercially available credit bureau score or equivalent** - Segment the portfolio by the credit score of the borrower at origination using a commercially available credit bureau score (e.g. FICO Score, VantageScore, or another qualifying credit score). If the underwriting decision was based on an internal score and a commercially available credit bureau score was not available at origination, please map this internal score to an industry standard credit score.
   - 00 - <=560
   - 01 - >560 and <= 620
   - 02 - > 620 and <= 660
   - 03 - > 660 and <= 720
   - 04 - > 720
   - 05 - N/A - Original credit score is missing or unknown

5. **Geography** - Segment the portfolio into the following six geographical area designations. The primary borrower's current place of residence should be used to define the region.
   - 01 - Region 1: California, Nevada, Florida, Arizona
   - 02 - Region 2: Rhode Island, South Carolina, Oregon, Michigan, Indiana, Kentucky, Georgia, Ohio, Illinois
   - 03 - Region 3: Washington D.C., Mississippi, North Carolina, New Jersey, Tennessee, Missouri, West Virginia, Connecticut, Idaho, Pennsylvania, Washington, Alabama
   - 04 - Region 4: Delaware, Massachusetts, New York, Colorado, New Mexico, Texas
   - 05 - Region 5: Alaska, Louisiana, Wisconsin, Arkansas, Maine, Maryland, Utah, Montana, Minnesota, Oklahoma, Iowa, Virginia, Wyoming, Kansas, Hawaii
   - 06 - Region 6: Vermont, New Hampshire, Nebraska, South Dakota, North Dakota

6. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current + 1-29 DPD: Accounts that are not past due (accruing and non-accruing) or are 1-29 DPD (accruing and non-accruing) as of month-end.
   - 02 - 30-59 DPD: Accounts that are 30 to 59 days past due (accruing and non-accruing) as of month-end.
   - 03 - 60-89 DPD: Accounts that are 60 to 89 days past due (accruing and non-accruing) as of month-end.
   - 04 - 90-119 DPD: Accounts that are 90 to 119 days past due (accruing and non-accruing) as of month-end.
   - 05 - 120+ DPD: Accounts that are 120 or more days past due (accruing and non-accruing) as of month-end.

#### B. Summary Variables

For each month in the reporting period, report the following summary variables for each segment described in Section A.

When reporting $ Vehicle Type (lines 6-9), vehicles should be classified for the purpose of this schedule by body style; however, a luxury vehicle may include all body styles that meet the qualification of a high cost vehicle.

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total unpaid principal balance for accounts on the book for the segment as of month-end.
3. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
4. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **Interest rate** - The average annual percentage rate for accounts on the book for the segment as of month-end. In making this calculation, report the purchase APR unless the account is in default or workout. If the account is in default, then use the default APR. If the account is in a workout program (temporary or permanent), use the workout APR.
6. **$ Vehicle type car/van** - The unpaid principal balance in the portfolio with vehicle type classified as "Car/Van" for the segment as of month-end.
7. **$ Vehicle type SUV/truck** - The unpaid principal balance in the portfolio with vehicle type classified as "SUV/Truck" for the segment as of month-end.
8. **$ Vehicle type sport/luxury/convertible** - The unpaid principal balance in the portfolio with vehicle type classified as "Sport/Luxury/Convertible" for the segment as of month-end.
9. **$ Vehicle type unknown** - The unpaid principal balance in the portfolio with vehicle type classified as "Unknown" for the segment as of month-end.
10. **$ Repossession** - The unpaid principal balance of loans still on the books whose vehicles have been repossessed for the segment as of month-end. This field captures the stock of repos.
11. **$ Current Month Repossession** - The unpaid principal balance of loans still on the books whose vehicles were newly repossessed in the given month for the segment as of month-end. This field captures the flow of repos in the current month, and should include both active and charged-off loans.
12. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower. The amount reported here should be consistent with the amount reported on Schedule HI-B, Part I, Column A of the FR Y-9C.
13. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
14. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off, including recoveries on acquired loans/portfolios.
15. **$ Net charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, net of any recoveries in the reporting month on loans in the segment that were previously charged-off. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
16. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ Net Charge-offs equals [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs -$ Recoveries], provide the value of $ Net Charge-offs minus [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs - $ Recoveries] in this variable.
17. **$ Ever 30DPD in the last 12 months** - The total unpaid principal balance for the segment as of month-end that was 30 or more days past due at any given time in the twelve months ending in the reference month.
18. **$ Ever 60DPD in the last 12 months** - The total Unpaid Principal Balance for the segment as of month-end that was 60 or more days past due at any given time in the twelve months ending in the reference month.
19. **Projected value** - Total projected market value of lease at termination. Only calculated for leased vehicles.
20. **Actual sale proceeds** - Sales proceeds from terminated leases. Only calculated for leased vehicles.
21. **Original term <= 48 months** - The total unpaid principal balance for accounts on the book for the segment as of month-end that had an original term of 48 months or less.
22. **Original term 49-60 months** - The total unpaid principal balance for accounts on the book for the segment as of month-end that had an original term of 49-60 months.
23. **Original term 61-72 months** - The total unpaid principal balance for accounts on the book for the segment as of month-end that had an original term of 61-72 months.
24. **Original term >72 months** - The total unpaid principal balance for accounts on the book for the segment as of month-end that had an original term of greater than 72 months.
25. **$ Origination channel (direct)** - The total unpaid principal balance for accounts on the book for the segment as of month-end that were originated through direct channels (i.e., a chartered bank, a non-bank subsidiary).
26. **$ Loss mitigation** - The total unpaid principal balance for accounts on the book for the segment as of month-end that are currently in a loss mitigation program.
27. **$ Joint application** - The total unpaid principal balance for accounts on the book for the segment as of month-end that were originated with a co-applicant.
28. **Probability of Default (PD)** - Report the average Probability of Default (PD) as defined in the most recent capital framework for accounts within the segment. Applicable only to the advanced approaches reporting banks.
29. **Loss Given Default (LGD)** - Report the Loss Given Default (LGD) as defined in the most recent capital framework for accounts within the segment. Applicable only to the advanced approaches reporting banks.
30. **Expected Loss Given Default (ELGD)** - Report the Expected Loss Given Default (ELGD) parameter as defined in the most recent capital framework for accounts within the segment. Applicable only to the advanced approaches reporting banks.
31. **Risk-Weighted Asset (RWA)** - Report the aggregate dollar Risk Weighted Asset (RWA) for accounts within the segment as defined in the most recent capital framework. Applicable only to banks subject to the advanced approaches rule.
32. **$ Unpaid Principal Balance at Charge-off** - The total unpaid principal balance of loans in the segment that were charged-off (either partially or fully) during the reporting month and had not been partially charged-off in a prior reporting month. Report the unpaid principal balance at the time of the charge-off. Do not include interest and fees.
33. **Percent Loss Severity (3 month Lagged)** - Report the total loss net of all recoveries as a percent of the unpaid principal balance (UPB) for all accounts in the segment that were charged-off for the first time in the third month prior to the current reporting month.
34. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.
