# FR Y-14M Instructions - Chunk 016
## Schedule D.1 Loan Level Table (continued): Line Items 59 (concluded) through 91

This chunk continues the Schedule D (Domestic Credit Card) data dictionary D.1 Loan Level Table, covering the conclusion of Line Item 59 and Line Items 60 through 91.

### Line Item 59: Month-end Account Status - Closed (concluded) (MDRM M102)
(Continued from chunk 015) Report cases where company representatives request the closure of an employee credit card (a corporate card under consideration) as 1.
- 0 = No, the account is not closed and not charged-off.
- 1 = Yes, closed, at the request of the borrower.
- 2 = Yes, closed, not at the request of the borrower.
- 3 = Yes, closed, borrower deceased.
- 4 = Yes, closed due to charge off.

Charged off loans or closed loans are required to be included up to twelve months after they are closed or charged off.

### Line Item 60: Collection Re-age Date (MDRM M103)
Report the date of the last account re-age performed by the collections department, or in relation to any performance-related delinquency.

### Line Item 61: Charge-off Reason (MDRM M104)
Report the reason for charge-off and loss recognition on an account in the current month. This line item should be left blank for accounts that have not been charged off.
- 1 = Contractual - losses incurred as a result of borrower's inability to make full repayment under the contractual terms of the account.
- 2 = Bankruptcy - losses incurred as a result of borrower's bankruptcy proceedings.
- 3 = Deceased - losses incurred as a result of death of account holder.
- 4 = Other - any other known reason.
- 5 = Charge-off Reason Unknown - any other charge-off, reason unknown.
- 6 = Fraud - losses as a result of fraud, whether by account holder or a third party.

### Line Item 62: Gross Charge-off Amount - Current Month (MDRM M105)
Report the total amount of gross charge-offs on the account during the reporting month, including charge-offs related to principal, interest and fees. Report all gross charge-offs, including those related to acquired impaired loans. Value will only be populated in the month charged-off.

### Line Item 63: Recovery Amount - Current Month (MDRM M106)
Report the dollar amount of any balance recovery from a previously charged-off account collected during the month. When possible assign recoveries at account level, including bulk recoveries. For example, in some instances it may be reasonable to establish a relationship between recoveries (or recovery rate) at the account level, exposure at default, and potentially other account characteristics. This stated relationship can be used in conjunction with observed losses at a higher level of aggregation in order to generate consistent losses at the account level. This established relationship may be model based in some cases or judgmentally based in others. If it is not possible to reasonably assign recoveries at the account level for any reason, leave blank as indicated in the schedule's instructions. Report all recoveries, including those related to acquired impaired loans.

### Line Item 64: Purchase Amount (MDRM M107)
Report the net purchase dollar volume during the current month's cycle.

### Line Item 65: Cash Advance Amount (MDRM M108)
Report the net cash advance dollar volume during the current month's cycle.

### Line Item 66: Balance Transfer Amount (MDRM M109)
Report the balance transfer dollar volume during the current month's cycle.

### Line Item 67: Convenience Check amount (MDRM M110)
Report the convenience check dollar volume during the current month's cycle.

### Line Item 68: Account Sold Flag (MDRM M111)
Report accounts that have been sold during the current month. Identifier should persist while the account is reported from the sale announcement date. (1 = Yes, 0 = No)

### Line Item 69: Bankruptcy Flag (MDRM M112)
Report whether a borrower has filed for bankruptcy and bankruptcy process is ongoing, or has filed for bankruptcy and has completed the bankruptcy process. Identifier should persist while the account is reported. (1 = Yes, 0 = No)

### Line Item 70: Loss sharing (MDRM M113)
Report accounts that are part of a loss sharing agreement, as defined in the FR Y-9C, Schedule HC-M, item 6. (1 = Yes, 0 = No)

### Line Item 71: Probability of Default - PD (MDRM M114)
Report the Probability of Default for the account as defined in the most recent capital framework. More specifically, report the PD associated with the account's corresponding segment. Example, a one in ten probability of default should be reported as 0.1. This item is mandatory for firms subject to the advanced approaches rule.

### Line Item 72: Loss Given Default - LGD (MDRM M115)
Report the Loss Given Default for the account as defined in the most recent capital framework. More specifically, report the LGD associated with the account's corresponding segment. Example, a ninety percent loss given default should be reported as 0.9. This item is mandatory for firms subject to the advanced approaches rule.

### Line Item 73: Expected Loss Given Default - ELGD (MDRM M116)
Report the Expected Loss Given Default parameter for the account as defined in the most recent capital framework. More specifically, report the ELGD associated with the account's corresponding segment. For example, a ninety percent expected loss given default should be reported as 0.9. This item is mandatory for firms subject to the advanced approaches rule.

### Line Item 74: Exposure at Default - EAD (MDRM M117)
Report the Exposure at Default for the account as defined in the most recent capital framework. More specifically, report the EAD associated with the account's corresponding segment. In particular, for open-ended exposures assign to all the accounts in a particular segment the corresponding LEQ, CCF, or related parameters, associated with that segment. After the corresponding parameter is assigned to each account, calculate the account EAD and report this as the variable value. This item is mandatory for firms subject to the advanced approaches rule.

### Line Item 75: EAD id segment (MDRM M118)
Report the unique EAD segment Id identifier -- A unique number identifying the EAD segment where the loan record resides in the current month. This item is mandatory for firms subject to the advanced approaches rule.

### Line Item 76: Corporate ID (MDRM N031)
For corporate cards, report a unique identifier that will be the same for a given corporation from month to month. The Aggregator will recommend a best practice for the identification or generation of this identifier and the safeguarding of account privacy information. For non-corporate card, leave blank.

### Line Item 77: Variable Rate Index (MDRM N032)
Report variable purchase APR (variable 55) index, if a loan has a fixed purchase APR, report as 0.
- 0 = Fixed APR
- 1 = Prime Rate
- 2 = 1 month LIBOR
- 3 = 2 month LIBOR
- 4 = 3 month LIBOR
- 5 = 6 month LIBOR
- 6 = 12 month LIBOR
- 7 = 1 month Treasury Bill
- 8 = 3 month Treasury Bill
- 9 = 6 month Treasury Bill
- 10 = 12 month Treasury
- 11 = Others
- 12 = SOFR 1mo
- 13 = SOFR 3mo
- 14 = SOFR 6mo
- 15 = SOFR 1yr
- 16 = SOFR Other
- 17 = SOFR Unknown Type

### Line Item 78: Variable Rate Margin (MDRM 6271)
Report variable purchase APR (variable 55) margin, if a loan has a fixed purchase APR, leave blank.

### Line Item 79: Maximum APR (MDRM N033)
Report the maximum APR (rate cap applying to purchase APR and cash APR) allowed for the account during the reporting month. Such maximum APR is stipulated in the account agreement or set by the regulatory limit that BHCs, IHCs, or SLHCs may charge a consumer. For accounts where the maximum APR is unknown or the account is a fixed rate account, this field should be left blank.

### Line Item 80: Rate Reset Frequency (MDRM N034)
Report the frequency for resetting the APR. Resetting the APR refers to the contractual frequency at which APRs are reset for variable rate APR credit cards. Rate resets that occur as a result of promotional offer should not be included in this item. If the BHC or IHC or SLHC does not have a reset schedule, report option 6.
- 0 = Fixed rate no reset
- 1 = Monthly
- 2 = Every 2 months
- 3 = Every 3 months
- 4 = Every 6 months
- 5 = Every 12 months
- 6 = Others

### Line Item 81: Promotional APR (MDRM N035)
Report the APR for the balance under promotion with a positive promotional balance (Cycle Ending Balances Mix - Promotional (Line item 18)). If there are multiple APRs, report the weighted average promotional APR corresponding to Line item 18 Cycle Ending Balances Mix - Promotional.

### Line Item 82: Cash APR (MDRM N036)
Report the contractual APR for the cash balance. If there are multiple APRs, report the weighted average promotional APR corresponding to Line item 19 Cycle Ending Balances Mix - Cash.

### Line Item 83: Loss Share ID (MDRM N037)
If the account is associated with a loss sharing agreement, report a unique number generated by the institution that can be used to separately identify any reported loan associated with a specific loss sharing agreement. A unique ID should be generated for each active sharing agreement. The specific ID should be consistent over time for as long as the agreement remains active without a relevant change in the terms of the loss sharing agreement. The institution should also provide a written summary of the relevant terms of each loss sharing agreement along with the corresponding LossShareId number. Additional supporting documentation may be requested if necessary. Leave blank if the account is not associated with a loss sharing agreement.

### Line Item 84: Loss Share Rate (MDRM N038)
If the account is associated with a loss sharing agreement, report the percentage of credit loss that the reporting institution will bear in the case of default. For example, if the reporting institution bears 20.8% of the credit losses in this portfolio report 0.208.
- 0 = Report the number zero if the account is not associated with a loss sharing agreement.
- 2 = Report the number two if the account is associated with a loss sharing agreement that is too complex to be characterized by a simple loss share rate. It is particularly important in this case that the institution provides a written summary of the relevant terms of each loss sharing agreement. Additional supporting documentation may be requested if necessary.

### Line Item 85: Other Credits (MDRM N039)
Report the dollar amount of all credits (other than cardholder payments) received during the current month's cycle, including merchandise returns and reward cash credits. Exclude fee reversals or waivers, which are accounted for in the "Fees Incurred" line item.

### Line Item 86: Cycles Past Due at Cycle Date (MDRM N129)
Report the number of cycles the account is past due as of the current month's cycle date.

### Line Item 87: Cycles Past Due at Month-End (MDRM N130)
Report the number of cycles the account is past due on the last day of the current reporting month.

### Line Item 88: Finance Charge (Effective for submission of June 2013 data) (MDRM N131)
Report the dollar amount of the net finance charges assessed on the reporting month's statement. If the account did not have finance charges on the statement, report as zero.

### Line Item 89: Fees Incurred - Late (MDRM N132)
Report the net late fees assessed for late or nonpayment. Report fees posted during current month's cycle.

### Line Item 90: Fees Incurred - Over Limit (MDRM N133)
Report the over limit fees assessed for an account exceeding its credit limit. Report fees posted during current month's cycle.

### Line Item 91: Fees Incurred - NSF (MDRM N134)
Report the non-sufficient funds fees (NSF) assessed against an account when payment is returned unpaid because of non-sufficient funds. Report fees posted during current month's cycle.
