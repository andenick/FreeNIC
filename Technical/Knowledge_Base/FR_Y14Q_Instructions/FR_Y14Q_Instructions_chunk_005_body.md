# FR Y-14Q Instructions - Chunk 005
## Schedule A - Retail (continued)

### A.8 - International Small Business

In this worksheet, include all "scored" or "delinquency managed" international small business loans. The main differentiating factor between corporate loans and small business loans is how the consolidated holding company evaluates the creditworthiness of the borrower. For small business lending, banks look at the credit score of the borrower (scored rating) and/or use delinquency management. Therefore, small business loans are loans that are "scored" or "delinquency managed" for which a commercial internal risk rating is not used or that uses a different scale than other corporate loans. Include international small business loans as defined in the FR Y-9C, Schedule HC-C included in items 2.a, 2.b, 3, 4.a, 4.b, 7, 9.a, 9.b.2, and 10.b. Exclude corporate and SME credit card loans as defined in the FR Y-9C, Schedule HC-C, item 4.b. Exclude all non-purpose securities-based loans and loans for purchasing and carrying securities. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option. For domestic small business loans, see the instructions for Worksheet 9.

Segment the portfolio along all combinations: three product type segments, two age segments, four geography segments, three original credit score segments, five delinquency status segments, and two secured or unsecured segments; therefore, the portfolio must be divided into a total of 3*2*4*3*5*2 = 720 distinct segments. Use "IntSB" for the portfolio ID within this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into the following product types as of month-end:
   - 01 - Line of Credit
   - 02 - Term Loan
   - 03 - Other

2. **Age** - Age refers to the time that has elapsed since the account was originated:
   - 01 - <= Three years old
   - 02 - > Three years old

3. **Geography** - Segment the portfolio into the following four geographical area designations:
   - 01 - Region 1: Canada
   - 02 - Region 2: EMEA - Europe, Middle East, and Africa
   - 03 - Region 3: LATAM - Latin America and Caribbean
   - 04 - Region 4: APAC - Asia-Pacific

4. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 620
   - 02 - > 620
   - 03 - N/A - Original credit score is missing or unknown

5. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current and 1-29 days past due (DPD)
   - 02 - 30-59 DPD
   - 03 - 60-89 DPD
   - 04 - 90-119 DPD
   - 05 - 120+ DPD

6. **Secured or unsecured** - Segment the portfolio based on the following two categories:
   - 01 - Secured
   - 02 - Unsecured

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total unpaid principal balance for accounts on the book for the segment as of month-end.
3. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
4. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **$ Commitments** - The total dollar amount of commitments for the segment as of month-end.
6. **$ Modifications** - Total unpaid principal balance of loans that have been adjusted as part of a loan modification program. For purposes of this Schedule, a loan modification occurs when the terms of the loan were changed from those stated in the original loan contract as part of loss mitigation efforts.
7. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
8. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
9. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
10. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
11. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ net charge-offs equals [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries], provide the value of $ net charge-offs minus [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries] in this variable.
12. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.

---

### A.9 - US Small Business

In this worksheet, include all "scored" or "delinquency managed" domestic small business loans. The main differentiating factor between corporate loans and small business loans is how the consolidated holding company evaluates the creditworthiness of the borrower. For small business lending, banks look at the credit score of the borrower (scored rating) and/or use delinquency management. Therefore, small business loans are loans that are "scored" or "delinquency managed" for which a commercial internal risk rating is not used or that uses a different scale than other corporate loans. Include domestic small business loans as defined in the FR Y-9C, Schedule HC-C included in items 2.a, 2.b, 3, 4.a, 4.b, 7, 9.a, 9.b.2, and 10.b. Exclude corporate and SME credit card loans as defined in the FR Y-9C, Schedule HC-C, item 4.a. Exclude all non-purpose securities-based loans and loans for purchasing and carrying securities. Only include loans and leases held for investment at amortized cost. For international small business loans, see the instructions for Worksheet 8. **Exclude Paycheck Protection Program (PPP) loans from this schedule.**

Segment the portfolio along all combinations: three product type segments, two age segments, three original credit score segments, five delinquency status segments, and two secured or unsecured segments; therefore, the portfolio must be divided into a total of 3*2*3*5*2 = 180 distinct segments. Use "USSB" for portfolio ID within this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into the following product types as of month-end:
   - 01 - Line of Credit
   - 02 - Term Loan
   - 03 - Other

2. **Age** - Age refers to the time that has elapsed since the account was originated:
   - 01 - <= Three years old
   - 02 - > Three years old

3. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 620
   - 02 - > 620
   - 03 - N/A - Original credit score is missing or unknown

4. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current and 1-29 (days past due) DPD
   - 02 - 30-59 DPD
   - 03 - 60-89 DPD
   - 04 - 90-119 DPD
   - 05 - 120+ DPD

5. **Secured or unsecured** - Segment the portfolio based on the following two categories:
   - 01 - Secured
   - 02 - Unsecured

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total unpaid principal balance for accounts on the book for the segment as of month-end.
3. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
4. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **$ Commitments** - The total dollar amount of commitments for the segment as of month-end.
6. **$ Modifications** - Total unpaid principal balance of loans that have been adjusted as part of a loan modification program.
7. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
8. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
9. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
10. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
11. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ net charge-offs equals [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries], provide the value of $ net charge-offs minus [$ gross contractual charge-offs + $ bankruptcy charge-offs - $ recoveries] in this variable.
12. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.

---

### A.10 - Student Loan

In this worksheet, include all student loans as defined in the FR Y-9C, Schedule HC-C, lines 6.b and 6.d. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations: two product type segments, five age segments, three original credit score segments, five delinquency status segments, and four education level segments; therefore, the portfolio must be divided into a total of 2*5*3*5*4 = 600 distinct segments. Use the portfolio ID "Student" for this worksheet.

#### A. Segment Variables

1. **Product type** - Reporting institutions should segment the portfolio into the following two product types. An example of a government guaranteed loan is a FFELP loan.
   - 01 - Managed - Gov Guaranteed
   - 02 - Managed - Private

2. **Age** - Refers to the time that has elapsed since the loan was originated. If there were multiple disbursements tied to an original then use the time since the first disbursement:
   - 01 - 6 years <= Age
   - 02 - 5 years <= Age < 6 years
   - 03 - 4 years <= Age < 5 years
   - 04 - 3 years <= Age < 4 years
   - 05 - Age < 3 years

3. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 660
   - 02 - > 660
   - 03 - N/A - Original credit score is missing or unknown

4. **Delinquency status** - Reporting institutions should segment the portfolio into the following five delinquency statuses:
   - 01 - Current + 1-29 DPD
   - 02 - 30-59 DPD
   - 03 - 60-89 DPD
   - 04 - 90-119 DPD
   - 05 - 120+ DPD

5. **Education level** - The level of education being pursued by the recipient of the loan. For consolidated loans, report the highest level of education pursued by the borrower.
   - 01 - Undergraduate - 4 year
   - 02 - Graduate / Professional
   - 03 - Other (e.g. community college, trade school, etc.)
   - 04 - Not available

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total unpaid principal balance for accounts on the book for the segment as of month-end.
3. **# Accounts in repayment** - Total number of accounts on the book for the segment as of month-end that have entered the loan's repayment period.
4. **$ Outstandings in repayment** - Total unpaid principal balance for accounts on the book for the segment as of month-end that have entered the loan's repayment period.
5. **# New disbursements** - The total number of new disbursements in the given month for the segment as of month-end.
6. **$ New disbursements** - The total dollar amount disbursed in the given month for the segment as of month-end.
7. **$ of Unpaid principal balance with co-signer** - The dollar amount of unpaid principal balance in the segment that was underwritten with a co-signer reported as of the month-end.
8. **$ of Unpaid principal balance in grace** - The dollar amount of unpaid principal balance for accounts that are in grace status for the segment being reported as of month-end.
9. **$ of Unpaid principal balance in deferment** - The dollar amount of unpaid principal balance for accounts that are in deferment status for the segment being reported as of month-end.
10. **$ of Unpaid principal balance in forbearance** - The dollar amount of unpaid principal balance for accounts that are in forbearance status for the segment being reported as of month-end.
11. **$ CDR [0% through 1.99%)** - The total unpaid principal balance in the segment that has a school cohort default rate as computed by the Department of Education falling within 0% through 1.99% as of the month-end.
12. **$ CDR [2% through 3.99%)** - The total unpaid principal balance in the segment that has a school cohort default rate as computed by the Department of Education falling within 2% through 3.99% as of the month-end.
13. **$ CDR [4% through 5.99%)** - The total unpaid principal balance in the segment that has a cohort default rate falling within 4% through 5.99% as of the month-end.
14. **$ CDR [6% through 7.99%)** - The total unpaid principal balance in the segment that has a cohort default rate falling within 6% through 7.99% as of the month-end.
15. **$ CDR [8% through 9.99%)** - The total unpaid principal balance in the segment that has a cohort default rate falling within 8% through 9.99% as of the month-end.
16. **$ CDR >= 10%** - The total unpaid principal balance in the segment that has a cohort default rate 10% or higher as of the month-end.
17. **$ CDR = N/A** - The total unpaid principal balance in the segment that has no cohort default rate as of the month-end.
18. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
19. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
20. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
