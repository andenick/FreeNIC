# FR Y-14M Instructions - Chunk 017
## Schedule D.1 Loan Level Table (continued): Line Items 92-123

This chunk continues the Schedule D (Domestic Credit Card) data dictionary D.1 Loan Level Table, covering Line Items 92 through 123.

### Line Item 92: Fees Incurred - Cash Advance (MDRM N135)
Report the cash advance fees assessed for cash advances made on the credit card. Report fees posted during current month's cycle.

### Line Item 93: Fees Incurred - Monthly/Annual (MDRM N136)
Report the monthly/annual fees assessed for the privilege of holding the credit card. Report fees posted during current month's cycle.

### Line Item 94: Fees Incurred - Debt Suspension (MDRM N137)
Report the debt suspension/cancellation fees assessed to protect consumer in the event of a significant life event like the loss of a job. Report fees posted during current month's cycle.

### Line Item 95: Fees Incurred - Balance Transfer (MDRM N138)
Report the balance transfer fees assessed for balances transferred from another institution to this cardholder's account. Report fees posted during current month's cycle.

### Line Item 96: Fees Incurred - Other (MDRM N139)
Report all other fees not included elsewhere in this report. Examples include convenience check fees and foreign currency fees.

### Line Item 97: Debt Suspension/Cancellation Program Enrollment (MDRM N140)
Report whether the account is enrolled in a debt waiver/cancellation program, including payment protection plans. (1 = Yes, 0 = No)

### Line Item 98: Debt Suspension/Cancellation Program Active (MDRM N141)
Report whether the borrower is receiving benefits under a debt suspension/cancellation program, including payment protection plans. (1 = Yes, 0 = No)

### Line Item 99: Cycle-end Account Status - Active (MDRM N142)
Report whether the account has had any debit, credit, or balance activity in the last twelve months as of cycle end. If the account does not cycle in the current month, leave blank.
- 0 = Open & Active - account is open and has had debit, credit or balance activity in the last twelve months
- 1 = Open & Inactive - account is open, but has not had any debit, credit, or balance activity in the last twelve months
- 2 = Account is closed / not open - account is closed and has no further charging privileges. Include accounts in default and expired accounts.

### Line Item 100: Cycle-end Account Status - Closed (MDRM N143)
Report whether, in the current reporting cycle, the account is closed or revoked and has no further charging privileges. Include accounts in default, in credit management programs and expired accounts. The account may or may not have a balance. If the account does not cycle in the current month report the last known status.
- 0 = No, the account is not closed and not charged-off.
- 1 = Yes, closed, at the request of the borrower.
- 2 = Yes, closed, not at the request of the borrower.
- 3 = Yes, closed, borrower deceased.
- 4 = Yes, closed due to charge off.

### Line Item 101: Skip-a-payment (MDRM N144)
Report whether the account holder opted for a promotional skip-a-payment during the reporting month. (1 = Yes, 0 = No)

### Line Item 102: Credit Card Workout Program (MDRM N145)
Report whether the account entered into any type of workout program during the current reporting month. (1 = Yes, 0 = No). Report "No" if the BHC or IHC or SLHC does not offer a workout program.

### Line Item 103: Workout Program Type (MDRM N146)
For accounts in a workout program at month-end, report the type of program in one of the options below. Leave blank if the account did not enter into any type of workout program or the BHC or IHC or SLHC does not offer workout option.
- 1 = External Program - a permanent external program, often administered by a Consumer Credit Counseling Service (CCCS).
- 2 = Internal Long-Term Program - an internal program where terms have been modified and the account holder is paying off outstanding balances over an extended period. Include all programs with enrollment durations in excess of 12 months.
- 3 = Internal Temporary Programs - an internal program where terms are temporarily modified, not to exceed 12 months, in recognition of short term hardship.
- 4 = Settlement Programs - an agreement where the lender will accept less than the full balance outstanding to satisfy and close the account.
- 5 = Other - any other workout arrangement.
- 6 = Not Applicable - includes Service members Civil Relief Act (SCRA) programs

Leave blank if the BHC or IHC or SLHC does not offer workout option.

### Line Item 104: Workout Program Performance Status (MDRM N147)
Report the performance of borrowers in all workout plans. These plans include the external Consumer Credit Counseling Programs, as well as, internal long-term and temporary programs. Report performance as of the reporting date in one of the following categories. Leave blank if the account did not enter into any type of workout program or the BHC or IHC or SLHC does not offer workout option.
- 1 = Active and Performing - the borrower is performing as scheduled under the terms of an executed workout program. Include in this option accounts in a settlement program, where the borrower is fulfilling all obligations as agreed, reported in line item #103 as option 4.
- 2 = Active and Non-Performing - the borrower is in a workout plan but is currently delinquent but not yet has defaulted
- 3 = Broken - the borrower has defaulted on the terms of an executed plan during the month. Use the bank's internal definition of broken.

### Line Item 105: Settlement Portion Forgiven (MDRM N148)
For any account for which the "Settlement" option has been selected under the Workout Program type, report the total amount of the outstanding balance forgiven in the current month. Leave blank if the BHC or IHC or SLHC does not offer workout options or the 'Settlement' option has not been selected.

### Line Item 106: Customer Service Re-age Date (MDRM N149)
Report the date of the last re-age performed by any customer service rep (for example, in response to an erroneous payment posting or other similar non-performance issue.) Customer service re-ages occur anytime an account's delinquency status is changed by someone or through some program outside of the established collections program - this includes moving a current account to delinquent (i.e. due to NSF insufficient funds) or moving a delinquent account to current.

### Line Item 107: Principal Charge-off Amount - Current Month (MDRM N150)
Report the total amount of any principal write-downs (or principal reversals) on the account during the reporting month. Record all charges against the Allowance for credit losses on loans and leases, as defined in the FR Y-9C glossary entry for "allowance for credit losses on loans and leases". Do not report write-downs related to fees, finance charges and other non-principal write-downs that are included in Gross Charge-off Amount - CurrentMonth. Report all charge-offs, including those related to acquired impaired loans. Value will only be populated in month charged-off.

### Line Item 108: Fraud in the current month (MDRM N151)
Report whether the account is currently frozen due to potential fraud or has been closed for cause at the conclusion of a fraud investigation month. (1 = Yes, 2 = No)

### Line Item 109: Original Credit Bureau Score Name (MDRM N152)
List the name of the commercially available credit score provided, or mapped to, in item 38. If the name of the commercially available credit bureau score reported, or mapped to, in item 38 is not among those listed, please select "Other" and report the name in item 116. List the version of the credit score in item 116. If, and only if, a commercially available credit score was not provided in item 38 and the internal score provided was not mapped to a commercially available credit score, please select "None".
- 1 = FICO
- 2 = VantageScore
- 3 = Other
- 4 = None

### Line Item 110: Refreshed Credit Bureau Score Name (MDRM N153)
List the name of the commercially available credit score provided or mapped to in item 40. If the name of the commercially available credit bureau score reported or mapped to in item 40 is not among those listed, please select "Other" and report the name in item 117. List the version of the credit score in item 117. If, and only if, a commercially available credit score was not provided in item 40 and the internal score provided was not mapped to a commercially available credit score, please select "None".
- 1 = FICO
- 2 = VantageScore
- 3 = Other
- 4 = None

### Line Item 111: Behavioral Score Name/Version (MDRM N154)
Report the name and version of the behavior score reported in line item 42.

### Line Item 112: Credit Limit Type (MDRM N155)
Report the type of credit limit reported in line item 44 when there is no credit limit. A Shadow Limit is the maximum total outstanding balance allowed on an account and is not advertised to the account holder. A Purchase Limit is the maximum amount that can be purchased on an account in a given billing cycle and is not advertised to the account holder. If the credit limit reported in line item 44 (Current Credit Limit) is not a shadow or purchase limit, leave the line item blank. For Corporate accounts, report the limit type at the account level and not the relationship credit limit.
- 1 = Purchase Limit
- 2 = Shadow Limit

### Line Item 113: Credit Line Change Type (MDRM N156)
Report the line change reported in line item 47 as proactive (bank-initiated) or reactive (borrower request). Pre-qualified offers sent by the bank where the customer must take action to accept the offer should be reported as bank-initiated.
- 1 = Proactive
- 2 = Reactive
- 3 = Unknown
- 0 = No line change

### Line Item 114: Date Co-Borrower Was Added (MDRM N157)
Report the date the co-borrower was added to the account.

### Line Item 115: Entity Type (MDRM M952)
Report the entity type that owns the reported loan. Entity type refers to the legal form or charter of the subsidiary of the BHC or IHC or SLHC that owns the reported loan.
- 1 = National Bank
- 2 = State Member Bank
- 3 = Nonmember Bank
- 4 = State Credit Union
- 5 = Federal Credit Union
- 6 = Non-bank Subsidiary
- 0 = Other

### Line Item 116: Origination Credit Bureau Score Version (Effective for submission of June 2014 data) (MDRM R037)
Provide the version of the commercially available credit bureau score reported or mapped to in item 38 using the format "score-name score-version" (for example, "FICO 08" or "FICO Classic" or "FICO NextGen" or "FICO Industry" or "VantageScore 3.0", or the corresponding score name and version using the specified format if "Other" was selected in item 109).

### Line Item 117: Refreshed Credit Bureau Score Version (Effective for submission of June 2014 data) (MDRM R039)
Provide the version of the commercially available credit bureau score reported or mapped to in item 40 using the format "score-name score-version" (for example, "FICO 08" or "FICO Classic" or "FICO NextGen" or "FICO Industry" or "VantageScore 3.0", or the corresponding score name and version using the specified format if "Other" was selected in item 110).

### Line Item 118: Internal Origination Credit Score Flag (Effective for submission of June 2014 data) (MDRM R040)
Indicate if an internal score was used to map to a commercially available credit bureau score in item 38, or if a commercially available credit bureau score was reported directly. If none of these options were selected, leave this field blank.
- 1 = An internal score was used to map to a commercially available credit bureau score.
- 2 = A commercially available credit bureau score was reported directly.

### Line Item 119: Internal Origination Credit Score Value (MDRM R041)
If an internal score was used in any way in item 38, report the corresponding value of the internal score here.

### Line Item 120: Internal Refreshed Credit Score Flag (MDRM R042)
Indicate if an internal score was used to map to a commercially available credit bureau score in item 40, or if a commercially available credit bureau score is reported directly. If none of these options were selected, leave this field blank.
- 1 = An internal score is used to map to a commercially available credit bureau score.
- 2 = A commercially available credit bureau score is reported directly.

### Line Item 121: Internal Refreshed Credit Score Value (MDRM R043)
If an internal score was used in any way in item 40, report the corresponding value of the internal score here.

### Line Item 122: Month-Ending Balance (MDRM JA25)
Report the total outstanding balance for the account at the end of the current reporting month.

### Line Item 123: National Bank RSSD ID (MDRM JA26)
Report the RSSD ID of the national bank that has a financial interest in the loan. For these purposes, a national bank subsidiary is deemed to have a financial interest in a loan if it owns the loan and/or services the loan. For loans that are serviced by a National Bank subsidiary of the BHC but owned by another entity, the respondent should report the RSSD ID of the National Bank subsidiary that services the loan. For loans that are owned by a National Bank subsidiary of the BHC but serviced by another entity, the respondent should report the RSSD ID of the National Bank subsidiary that owns the loan. If a National bank subsidiary of the BHC both owns and services the loan, the respondent should report the RSSD ID of the National Bank subsidiary that both owns and services the loan. If no National Bank subsidiary of the reporting BHC either owns or services the loan, this field should be left blank (null). In all cases, this field either would be left null or will contain the RSSD ID of a chartered national bank that is a subsidiary of the reporting BHC.
