# FR Y-14Q Instructions - Chunk 003
## Schedule A - Retail (continued)

### A.3 - International Credit Card

This section provides general guidance, data definitions and instructions for the International Card Worksheet. In this worksheet, include all international consumer credit and charge card loans as defined in the FR Y-9C, Schedule HC-C, items 6.a and 6.d, international corporate and SME card loans as defined in the FR Y-9C, Schedule HC-C, item 4.b. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option.

Segment the portfolio along all combinations of the segment variables listed in Section A below. There are three product type segments, two age segments, four geography segments, five delinquency status segments, and three original industry standard credit score or equivalent segments; therefore, the portfolio must be divided into a total of 3*2*4*5*3 = 360 distinct segments. Each segment should be identified by a unique ten-digit segment ID (variable name: SEGMENT_ID). Use the portfolio ID "IntCard" for this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into the following three product types:
   - 01 - Bank Card - Bank cards are regular general purpose credit cards that can be used at a wide variety of merchants, including any who accept MasterCard, Visa, American Express or Discover credit cards. Include affinity and co-brand cards in this category, and student cards if applicable. This product type also includes private label or propriety credit cards, which are tied to the retailer issuing the card and can only be used in that retailer's stores. Include oil & gas cards in this loan type.
   - 02 - Charge Card - Charge cards are consumer credit cards for which the balance is repaid in full each billing cycle.
   - 03 - Corporate, SME, and Business cards - Corporate cards are employer-sponsored credit cards for use by a company's employees and SME and Business cards are credit card accounts where the loan is underwritten with the sole proprietor or primary business owner as an applicant. Corporate, SME and Business cards only include cards where there is any individual liability associated with the sub-lines or the account is delinquency managed or scored. Also include cards where the account is delinquency managed or scored and performance is reported to the credit bureaus; corporate and SME cards do not include loans for which a commercially-graded corporation is ultimately responsible for repayment of credit losses with no reporting to credit bureaus.

2. **Age** - Age refers to the amount of time that has elapsed since the account was originated. There are two possible ages to report:
   - 01 - <= Two years old
   - 02 - > Two years old

3. **Geography** - Segment the portfolio into the following four geographical area designations. The primary borrower's current place of residency should be used to define the region.
   - 01 - Region 1: Canada
   - 02 - Region 2: EMEA - Europe, Middle East, and Africa
   - 03 - Region 3: LATAM - Latin America and Caribbean
   - 04 - Region 4: APAC - Asia Pacific

4. **Delinquency status** - Segment the portfolio into the following five delinquency statuses:
   - 01 - Current and 1-29 days past due (DPD): Accounts that are not past due (accruing and non-accruing) as of month-end and accounts that are 1 to 29 days past due (accruing and non-accruing) as of month-end.
   - 02 - 30-59 DPD: Accounts that are 30 to 59 days past due (accruing and non-accruing) as of month-end.
   - 03 - 60-89 DPD: Accounts that are 60 to 89 days past due (accruing and non-accruing) as of month-end.
   - 04 - 90-119 DPD: Accounts that are 90 to 119 days past due (accruing and non-accruing) as of month-end.
   - 05 - 120+ DPD: Accounts that are 120 or more days past due (accruing and non-accruing) as of month-end.

5. **Original commercially available credit bureau score or equivalent** - Segment the portfolio by the credit score of the borrower at origination.
   - 01 - <= 620
   - 02 - > 620
   - 03 - N/A - Original credit score is missing or unknown

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Receivables** - Total receivables for accounts on the book for the segment as of month-end.
3. **$ Unpaid principal balance** - Total Unpaid Principal Balance (UPB) on the book for the segment as of month-end. Unlike receivables, total UPB should be net of any interest and fees owed by the borrower.
4. **$ Commitments** - The total dollar amount of credit lines on the book for the segment as of month-end (include drawn and undrawn credit lines). The internal automated limit (shadow limit) should be used when there is no contractual limit.
5. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
6. **$ New commitments** - The total dollar amount of new commitments on accounts originated (or purchased) in the given month for the segment as of month-end. If unknown for some accounts due to an acquisition or a merger, report the credit line at acquisition.
7. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower. Also include write-downs to fair value on loans transferred to the held-for-sale account during the reporting month.
8. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
9. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
10. **# Accounts charged-off** - The total number of accounts which experienced a charge-off (contractual or bankruptcy) in the reference month.
11. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries in the reporting month. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
12. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ Net Charge-offs equals [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs - $ Recoveries], provide the value of $ Net Charge-offs minus [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs - $ Recoveries] in this variable.
13. **$ O/S for accounts that were 30+ DPD in last 24 months** - The total receivables for the segment as of month-end that was 30 or more days past due at any given time in the past 24 months ending in the reference month. Exclude charged-off accounts when making this calculation.
14. **# Accounts that were 30+ DPD in last 24 months** - The total number of accounts for the segment as of month-end that were 30 or more days past due at any given time in the past 24 months ending in the reference month. Exclude charged-off accounts when making this calculation.
15. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.

---

### A.4 - International Home Equity

This section provides general guidance and data definitions for the International Home Equity Worksheet. In this worksheet, include all international home equity loans secured by real estate as defined in the FR Y-9C, Schedule HC-C, item 1, that meet the loan criteria of item 1.c.1 and 1.c.2.b. Note that this includes international first lien and second lien home equity lines. Only include loans and leases held for investment at amortized cost; do not include loans or leases held for sale or held for investment and measured at fair value under the fair value option. For international first lien mortgages, see instructions for Worksheet 5.

Segment the portfolio along all combinations of the segment variables: two product type segments, three origination credit score segments, four geography segments, two age segments, two origination LTV segments, and five delinquency status segments; therefore, the portfolio must be divided into a total of 2*3*4*2*2*5 = 480 distinct segments. Use the portfolio ID "IntHE" for this worksheet.

#### A. Segment Variables

1. **Product type** - Segment the portfolio into product types based on specific features of the loan:
   - 01 - HELOAN
   - 02 - HELOC

2. **Original commercially available credit bureau score or equivalent** -
   - 01 - <= 660
   - 02 - > 660
   - 03 - N/A - Original credit score is missing or unknown

3. **Geography** - Report the region in which the property is located:
   - 01 - Region 1: Canada
   - 02 - Region 2: EMEA - Europe, Middle East, and Africa
   - 03 - Region 3: LATAM - Latin America and Caribbean
   - 04 - Region 4: APAC - Asia-Pacific

4. **Age** - Age refers to the amount of time that has elapsed since the account was originated:
   - 01 - <= Three years old
   - 02 - > Three years old

5. **Original LTV (or CLTV for 2nds)** - The original combined loan-to-value ratio is the original amount of the loan or line, in addition to any senior liens, divided by the property value at the time of origination:
   - 01 - < 80
   - 02 - >=80

6. **Delinquency status** - Divide the portfolio into the following five delinquency statuses:
   - 01 - Current & 1-29 days past due (DPD)
   - 02 - 30-89 DPD
   - 03 - 90-119 DPD
   - 04 - 120-179 DPD
   - 05 - 180+ DPD

#### B. Summary Variables

1. **# Accounts** - Total number of accounts on the book for the segment as of month-end.
2. **$ Outstandings** - Total principal amount outstanding as of the end of the month. This should be reported as unpaid principal balance (UPB) gross of any charge-offs.
3. **$ Commitment (HELOC only)** - The total dollar amount of HELOC credit lines on the book for the segment as of month-end. If there is no credit limit on certain accounts, report the purchase or shadow limit. Report this variable only for HELOC products.
4. **# New accounts** - The total number of new accounts originated (or purchased) in the given month for the segment as of month-end.
5. **$ New accounts** - The total dollar amount of new accounts originated (or purchased) in the given month for the segment as of month-end.
6. **$ New commitments (HELOC only)** - The total dollar amount of new HELOC credit lines booked on the system in the reporting month. Report this variable only for HELOC products.
7. **$ Commitment increases (HELOC only)** - The dollar amount increase on existing HELOC credit lines in the reporting-month. Report this variable only for HELOC products.
8. **$ Commitment decreases (HELOC only)** - The dollar amount decrease on existing HELOC credit lines in the reporting-month. Report this variable only for HELOC products.
9. **$ Gross contractual charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off during the reporting month, except where the charge-off arises from the bankruptcy of the borrower.
10. **$ Bankruptcy charge-offs** - The dollar amount of write-downs on loans in the segment that were charged-off due to bankruptcy during the reporting month.
11. **$ Recoveries** - The dollar amount recovered during the reporting month on loans in the segment that were previously charged-off. Reversals of recoveries should be recorded as negative recoveries.
12. **$ Net charge-offs** - The dollar amount of write-downs net on loans in the segment that were charged-off during the reporting month, net of any recoveries. Generally, $ Net Charge-offs should equal [$ Gross Contractual Charge-offs + $Bankruptcy Charge-offs - $ Recoveries].
13. **Adjustment factor to reconcile $ gross contractual charge-offs to $ net charge-offs** - If it is not the case that $ Net Charge-offs equals [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs - $ Recoveries], provide the value of $ Net Contractual Charge-offs minus [$ Gross Contractual Charge-offs + $ Bankruptcy Charge-offs - $ Recoveries] in this variable.
14. **$ Foreclosure** - The total unpaid principal balance of loans in the foreclosure process. These dollars are pre-OREO and should be coded as a foreclosure in the system.
15. **$ New foreclosure** - The total unpaid principal balance of loans that entered the foreclosure process in the reporting month.
16. **$ Other Real Estate Owned (OREO)** - The total unpaid principal balance of mortgages where the bank has obtained the title at foreclosure sale and the property is on the market and available for sale. Also include instances where the bank has obtained the title but the availability for sale is not known.
17. **$ New OREO** - The total unpaid principal balance of foreclosed loans where the institution has bought back the property.
18. **Weighted Average Life of Loans** - The Weighted Average Life of Loans should reflect the current position, the impact of new business activity, as well as the impact of behavioral assumptions such as prepayments or defaults, based on the expected remaining lives, inclusive of behavioral assumptions as of month-end.
