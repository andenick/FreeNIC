# FR Y-14Q Instructions - Chunk 004
## Schedule A - Retail (continued)

### A.5 - International First Lien Mortgage

This section provides general guidance and data definitions for the International First Lien Mortgage Worksheet. In this worksheet, include all international first lien mortgage loans secured by real estate as defined in the FR Y-9C, Schedule HC-C, item 1 which meet the loan criteria of item 1.c.2.a. Include international first lien residential mortgage and international first lien closed-end home equity loans. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations of the segment variables: two product type segments, three origination credit score segments, four geography segments, two age segments, two origination LTV segments, and five delinquency status segments; therefore, the portfolio must be divided into a total of 2*3*4*2*2*5 = 480 distinct segments. Use the portfolio ID "IntFM" for this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into product types based on payment terms of the loan (at origination):
   - 01 - Fixed Rate
   - 02 - Other

2. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 660
   - 02 - > 660
   - 03 - N/A - Original credit score is missing or unknown

3. **Geography** - Report the region in which the property is located:
   - 01 - Region 1: Canada
   - 02 - Region 2: EMEA - Europe, Middle East, and Africa
   - 03 - Region 3: LATAM - Latin America and Caribbean
   - 04 - Region 4: APAC - Asia Pacific

4. **Age** - Age refers to the time that has elapsed since the account was originated:
   - 01 - <= Three years old
   - 02 - > Three years old

5. **Original LTV** - The original loan-to-value ratio is the original amount of the loan divided by the property value at the time of origination:
   - 01 - < 80
   - 02 - >= 80

6. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current & 1-29 days past due (DPD)
   - 02 - 30-89 DPD
   - 03 - 90-119 DPD
   - 04 - 120-179 DPD
   - 05 - 180+ DPD

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total principal amount outstanding as of the end of the month. This should be reported as unpaid principal balance gross of any charge-offs. The $ outstanding should not reflect any accounting based write-downs and should only be reduced to zero when the loan has been liquidated.
3. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
4. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower. Also include write-downs to fair value on loans transferred to the held-for-sale account during the reporting month.
6. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
7. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
8. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
9. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ net charge-offs equals [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries], provide the value of $ net contractual charge-offs minus [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries] in this variable.
10. **$ Foreclosure** - The total unpaid principal balance of loans in the foreclosure process. These dollars are pre-OREO and should be coded as a foreclosure in the system.
11. **$ New foreclosure** - The total unpaid principal balance of loans that entered the foreclosure process in the reporting month.
12. **$ Other Real Estate Owned (OREO)** - The total unpaid principal balance of mortgages where the bank has obtained the title at foreclosure sale and the property is on the market and available for sale.
13. **$ New OREO** - The total unpaid principal balance of foreclosed loans where the institution has bought back the property in auction in the reporting month.
14. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end. It should reflect the weighted average of time to principal actual repayment (as modeled) for all positions in the segment, rounded to the nearest monthly term.

---

### A.6 - International Other Consumer Schedule

In this worksheet, include all international loans defined in the FR Y-9C, Schedule HC-C, item 6.b and 6.d, excluding student loans and non-purpose securities based loans and should also include all international non-auto leases as defined in the FR Y-9C, Schedule HC-C, item 10.a. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations: five product type segments, five delinquency status segments, three original credit score segments, two original LTV ratio segments, and four geography segments; therefore, the portfolio must be divided into a total of 5*5*3*2*4 = 600 distinct segments. Use "IntlOthCons" for portfolio ID for this worksheet.

#### A. Segment Variables

1. **Product type** - Reporting BHCs, IHCs, and SLHCs should segment the portfolio into the following five product types:
   - 01 - Secured-Revolving
   - 02 - Secured-Installment
   - 03 - Unsecured-Revolving
   - 04 - Unsecured-Installment
   - 05 - Overdraft

2. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current and 1-29 days past due (DPD)
   - 02 - 30-59 DPD
   - 03 - 60-89 DPD
   - 04 - 90-119 DPD
   - 05 - 120+ DPD

3. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 620
   - 02 - > 620
   - 03 - N/A - Original credit score is missing or unknown

4. **Original LTV** - The original combined loan-to-value ratio. For loans where the loan-to-value ratio is not applicable, include the lowest ratio for a segment identifier:
   - 01 - <= 70 or not applicable
   - 02 - > 70

5. **Geography** - Segment the portfolio into the following four geographical area designations:
   - 01 - Region 1: Canada
   - 02 - Region 2: EMEA - Europe, Middle East, and Africa
   - 03 - Region 3: LATAM - Latin America and Caribbean
   - 04 - Region 4: APAC - Asia-Pacific

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment being reported as of month-end.
2. **$ Outstandings** - The total unpaid principal balance for accounts on the book for the segment being reported as of month-end.
3. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
4. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
5. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
6. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
7. **# New accounts** - The total number of new accounts originated in the given month for the segment being reported as of month-end.
8. **$ New commitments** - The total dollar amount of new commitments on accounts originated in the given month for the segment being reported as of month-end. If unknown for some accounts due to acquisition or merger, report the credit line at acquisition.
9. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.

---

### A.7 - US Other Consumer

In this worksheet, include all domestic loans as defined in the FR Y-9C, Schedule HC-C, items 6.b and 6.d, excluding student loans and non-purpose securities based loans. Include domestic non-auto leases included as defined in the FR Y-9C, Schedule HC-C, item 10.a. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations: five product type segments, five delinquency status segments, three original credit score segments, and three original LTV ratio segments; therefore, the portfolio must be divided into a total of 5*5*3*3 = 225 distinct segments. Use "USOthCons" for the portfolio ID within this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into the following five product types:
   - 01 - Secured-Revolving
   - 02 - Secured-Installment
   - 03 - Unsecured-Revolving
   - 04 - Unsecured-Installment
   - 05 - Overdraft

2. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current and 1-29 days past due (DPD)
   - 02 - 30-59 DPD
   - 03 - 60-89 DPD
   - 04 - 90-119 DPD
   - 05 - 120+ DPD

3. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 620
   - 02 - > 620
   - 03 - N/A - Original credit score is missing or unknown

4. **Original LTV** - For unsecured loans for which loan-to-value is not applicable, report the summary variables in the segment entitled <=70 or not applicable:
   - 01 - <= 70 or not applicable
   - 02 - > 70 and < 100
   - 03 - >= 100

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - The total unpaid principal balance for accounts on the book for the segment as of month-end.
3. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
4. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
5. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
6. **$ Net Charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
7. **# New accounts** - The total number of new accounts originated in the given month for the segment as of month-end.
8. **$ New commitments** - The total dollar amount of new commitments on accounts originated in the given month for the segment as of month-end. If unknown for some accounts due to acquisition or merger, report the credit line at acquisition.
9. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.
