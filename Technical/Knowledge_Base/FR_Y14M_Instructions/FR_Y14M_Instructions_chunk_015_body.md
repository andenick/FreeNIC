# FR Y-14M Instructions - Chunk 015
## Schedule D.1 Loan Level Table (continued): Line Items 33-59

This chunk continues the Schedule D (Domestic Credit Card) data dictionary D.1 Loan Level Table, covering Line Items 33 through 59.

### Line Item 33: Borrower's Income at Origination (MDRM M076)
Report the borrower's total annual income obtained at the account's origination (annualized if monthly income was provided). For business credit cards the business income should be used.

### Line Item 34: Income Source at Origination (MDRM M077)
Income Source at Origination -- Report whether the original income information was for the primary cardholder only or for joint or household members also. (1 = Individual, 2 = Household, 3 = Other)

### Line Item 35: Updated Borrower's Income (Retired March 2020) (MDRM M078)

### Line Item 36: Updated Income Source (Retired March 2020) (MDRM M079)

### Line Item 37: Date Refreshed Income Obtained (Retired March 2020) (MDRM M080)

### Line Item 38: Origination Credit Bureau Score for the primary account holder (MDRM M081)
Report the credit score value of the primary account holder at origination using a commercially available credit bureau score (for a definition of a commercially available credit bureau score, see general instructions, section H). Report the credit score name in item 109 and list the credit score version in item 116.

If the underwriting decision was based on an internal score and a commercially available credit bureau score was not available at origination, please map this internal score to an industry standard credit score. Report that mapped score here and provide a separate document describing the mapping methodology. Report the name of the credit score to which the internal credit score was mapped in item 109 and list the credit score version in item 116. Indicate that an internal score is being mapped to the specified commercially available credit score in item 118 and report the value assigned by the internal credit score in item 119. Note that scores which do not meet the definition of a commercially available credit bureau score may be treated as missing data by the Federal Reserve.

For Small Business Cards, provide the score for the proprietor or primary business owner. For Corporate Cards, provide the score for the primary cardholder if available. If the original Industry standard score is not available, leave this line item blank.

### Line Item 39: Origination Credit Bureau Score for the co-borrower (if any) (MDRM M082)
Report the credit score of the co-borrower at origination using an industry standard credit bureau credit score (e.g., FICO, VantageScore, or another similar credit score), defined like "Origination Credit Bureau Score for the primary account holder" (see line item 38).

A co-borrower is a person who jointly borrows using the credit card and is responsible for repayment of the loan. The primary borrower will receive a credit card to make charges but the co-borrower may or may not receive a credit card.

Report the guarantor's credit score if there is no co-borrower or the credit score of the co-borrower is not available and there is a guarantor.

### Line Item 40: Refreshed Credit Bureau Score (MDRM M083)
Report the most recently updated credit score available for the primary account holder using a commercially available credit bureau score. Report the credit score name in item 110 and list the credit score version in item 117. Report the date on which the credit score was refreshed in item 41.

If a commercially available credit bureau score is not available, please map an internal score to an industry standard credit score. Report that mapped score here and provide a separate document describing the mapping methodology. Report the name of the credit score to which the internal credit score was mapped in item 110 and list the credit score version in item 117. Indicate that an internal score is being mapped to the specified commercially available credit score in item 120 and report the value assigned by the internal credit score in item 121. Report the date on which the internal credit score was refreshed in item 41.

For Small Business Cards, provide the score for the proprietor or primary business owner. For Corporate Cards, provide the score for the primary cardholder if available.

### Line Item 41: Credit Bureau Score Refresh Date (MDRM M084)
Report the date on which the commercially available credit score, or the internal score being mapped to a commercially available credit score, reported in item 40 was last refreshed.

### Line Item 42: Behavioral Score (MDRM M085)
Report the current internal behavior score available for the account in the reporting month. If no score is available, leave blank. Report the behavior score name and version in line item 111.

### Line Item 43: Original Credit Limit (MDRM M086)
Report the amount of the credit line set by the card issuer at origination. If no credit limit, report the purchase or shadow limit. If credit limit is not available, then leave blank.

A Shadow Limit is the maximum total outstanding balance allowed on an account and is not advertised to the account holder. A Shadow Limit can fluctuate based on the outstanding balance of the account holder during the course of a billing cycle.

A Purchase Limit is the maximum amount that can be purchased on an account in a given billing cycle and is not advertised to the account holder.

### Line Item 44: Current Credit Limit (MDRM M087)
Report the maximum dollar amount that may be borrowed on the account during the reporting month. Report at the reporting month's end. If no credit limit, report the purchase or shadow limit. Report the type of credit limit in line item 112. For closed accounts, report the last known credit limits. If unknown, leave blank.

For Corporate accounts, report the limit at the account level and not the relationship credit limit.

### Line Item 45: Current Cash Advance Limit (MDRM M088)
Report the maximum cash advance amount available to the borrower. Report at the reporting month's end.

### Line Item 46: Line Frozen in the current month (MDRM M089)
Report whether the account's credit line is involuntarily frozen and authorizations are prohibited on the account in the current reporting month. (1 = Yes, 0 = No)

### Line Item 47: Line Increase or Decrease in the current month (MDRM M090)
Report whether the account remains open but the credit line has been increased or reduced in the current reporting month. Report if the line change is proactive or reactive in line item 113. Report the flag to reflect the net change in credit limit, for accounts that have both an increase and a decrease of credit limit during the reporting month. Leave blank for closed accounts. (2 = Increase, 1 = Decrease, 0 = No change)

### Line Item 48: Minimum Payment Due (MDRM M091)
Report the current minimum dollar amount due that will make the account roll into the first delinquency bucket if not paid. For this item, the first delinquency bucket is defined as 1-29 days past due, with the general definition of past due taken from the FR Y-9C General Instructions for schedule HC-N. Use the most recent cycle date of the current reporting month. This is generally referred to as minimum payment due on cardholder's statement.

### Line Item 49: Total Payment Due (MDRM M092)
Report the dollar amount of the total payment due for the cycle ending in the current reporting month. This generally includes current minimum due, past due payments and any amount reported as over the credit limit.

### Line Item 50: Next Payment Due Date (MDRM M093)
Report the date the cardholder is told a payment must reach the bank for the cycle in the current reporting month to keep the account in a current status. Leave blank if no payment is due in the reporting month.

### Line Item 51: Actual Payment Amount (MDRM M094)
Report the dollar amount of all payments received during the current month's cycle. Aggregate multiple payments. Report net of checks returned for non-sufficient funds, account closed, etc. (even if related to prior cycles). If a statement was not generated or a payment was not made, report as zero. Include in this line item payments made on an account secured by a collateral deposit where the payment funds are withdrawn from the collateral account.

### Line Item 52: Total Past Due (MDRM M095)
Report the dollar amount of past due required payments at the end of the current month's cycle. Institutions should report the dollar amount of total required minimum payments past due at the end of the current month's cycle.

### Line Item 53: Days Past Due (MDRM M096)
Report the actual number of days the account is past due as of the current reporting month's cycle date. If cycle ending information is not available, report information at the month-end reporting date.

### Line Item 54: Account 60 Plus DPD Last Three Years Flag (MDRM M097)
Report whether an account was ever 60+ Days Past Due in the last 3 years. (1 = Yes, 0 = No)

### Line Item 55: Interest Type in current month (Retired March 2020) (MDRM M098)

### Line Item 56: APR at Cycle End (MDRM M099)
Report the purchase APR unless the account is in default or workout. If the account is in default then report the default APR. If the account is in a workout program (temporary or permanent), report the workout APR.

### Line Item 57: Fee Type (MDRM M100)
Report whether monthly or annual fee is assessed for the privilege of holding the credit card. (0 = No fee, 1 = Annual, 2 = Monthly, 3 = Other)

### Line Item 58: Month-end Account Status - Active (MDRM M101)
Report whether the account has had any debit, credit, or balance activity in the last twelve months at month end.
- 0 = Open & Active: account is open and has had debit, credit or balance activity in the last twelve months.
- 1 = Open & Inactive: account is open, but has not had any debit, credit, or balance activity in the last twelve months.
- 2 = Account is closed / not open: account is closed and has no further charging privileges. Include accounts in default and expired accounts.

### Line Item 59: Month-end Account Status - Closed (MDRM M102)
Report whether, in the current reporting month, the account is closed or revoked and has no further charging privileges. Include accounts in default, in credit management programs and expired accounts. The account may or may not have a balance. Report cases of bankruptcy as closed/revoked.
