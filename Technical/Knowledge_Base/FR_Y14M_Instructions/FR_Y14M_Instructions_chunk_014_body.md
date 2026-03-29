# FR Y-14M Instructions - Chunk 014
## Schedule D.1 Loan Level Table (continued): Line Items 7 (concluded) through 32

This chunk continues the Schedule D (Domestic Credit Card) data dictionary D.1 Loan Level Table, concluding Item 7 and covering Items 8 through 32.

### Line Item 7: Credit Card Type (concluded)
Continuation of code definitions:
- 4 = Corporate Card: Employer-sponsored credit cards for use by a company's employees. Report cards for which the employees are financially responsible for repayment of the balance. If loans have joint liability, then they should be reported in the FR Y-14M Credit Card schedule. If the employers are ultimately responsible for repayment of the balances, there is no individual liability and performance is not reported to a credit bureau, then report under the FR Y-14Q corporate loan schedule.
- 5 = Others: Other cards accounts to consumers, small business, or corporations reported in the FR Y-9C in line items not represented above. For small business or corporate cards report cards for which employees are financially responsible for repayment of balances.

### Line Item 8: Product Type (MDRM M051)
Report each account in one of the following product types:
1. Co-brand (typically related to products and services, including retail stores, airlines, etc. Excluding Oil and Gas cards)
2. Oil and Gas Co-Brand
3. Affinity (having affiliations such as Unions, Universities, etc. These cards typically do not offer rewards from these organizations)
4. Student (if internally identified as a student card)
5. Other
6. Health Care Card (a card that can only be used specifically with the chosen medical providers and carry terms not typically available to general purpose cards or private label cards)

### Line Item 9: Lending Type (MDRM M052)
Report each account in one of the following categories:
1. Consumer Bank Card: Regular general purpose credit cards that can be used at a wide variety of merchants. Also includes private label or propriety credit cards tied to a retailer.
2. Consumer Charge Card: Consumer credit cards for which the balance is repaid in full in each billing cycle.
3. Non Consumer Bank Card: Include small business credit card accounts where the loan is underwritten with the sole proprietor or primary business owner as applicant. Also report Corporate Card Employer-sponsored credit cards for use by a company's employees.
4. Non Consumer Charge Card: Small business credit card or corporate credit card for which the balance is repaid in full in each billing cycle.

### Line Item 10: Revolve Feature (MDRM M053)
Report whether the account has an associated revolve feature i.e. where the entire balance or part of the balance is not required to be repaid in full at the end of the billing cycle. (1 = Yes, 0 = No)

### Line Item 11: Network ID (MDRM M054)
Report each account in one of the following categories: 1 = Visa, 2 = MasterCard, 3 = American Express, 4 = Discover, 5 = Other.

### Line Item 12: Secured Credit Type (MDRM M055)
Report whether the card is included in a program where any portion of the line is secured by collateral. (1 = Yes, 0 = No)

### Line Item 13: Loan Source/Channel (MDRM M056)
Report the source or channel by which the lender solicited or otherwise acquired the account:
- 0 = Take-One Other application
- 1 = Pre-approved
- 2 = Invitation to Apply "ITA"
- 3 = Take-One Branch application
- 4 = Accounts Purchased from a 3rd Party
- 5 = Other loan source known and not included in 0-4 above
- 6 = Loan source unknown

### Line Item 14: Purchased Credit Deteriorated Status (MDRM M234)
Report whether any loans are accounted for as purchased credit-deteriorated (PCD). If the loan is a PCD loan, this line item should be a "1"; otherwise it should be "0".

### Line Item 15: Cycle Ending Balance (MDRM M058)
Report the total outstanding balance for the account at the end of the current month's cycle.

### Line Item 16: Cycle Ending Balance Flag (Retired March 2018) (MDRM M059)

### Line Item 17: Accounts Under Promotion (MDRM M060)
Report accounts under promotion with a positive promotional balance (i.e. subject to promotional pricing) in the current month's cycle. This may include purchase or any other type of teasers as well as all forms of private label promotional pricing. A lower rate due to debt management would not be reported in this line item if the lower rate is permanent. Exclude accounts that have been offered or are eligible for a promotion but have not accepted the promotion. (1 = Yes, 0 = No)

### Line Item 18: Cycle Ending Balances Mix - Promotional (MDRM M061)
Balances at a Promotional Rate - Report any amount outstanding priced at rates below the account's normal purchase APR at the end of the current month's cycle. Do not include balances under a workout program.

### Line Item 19: Cycle Ending Balances Mix - Cash (MDRM M062)
Balances at a Cash Advance Rate - Report any amount outstanding priced at cash advance APR at the end of the current month's cycle.

### Line Item 20: Cycle Ending Balances Mix - Penalty (MDRM M063)
Balances Subject to Default or Penalty Pricing - Report any amount outstanding subject to default or penalty pricing due to performance at the end of the current month's cycle.

### Line Item 21: Cycle Ending Balances Mix - Other (MDRM M064)
Report all other balances outstanding at the end of the current month's cycle ending date not included in line items 18, 19, and 20. Include balances under a workout program in this line item.

### Line Item 22: Average Daily Balance (ADB) (MDRM M065)
Report the average daily balance in the reporting month or cycle.

### Line Item 23: Total Reward Cash (MDRM M066)
For accounts that offer cash, miles or other rewards, report the total equivalent dollar amount of cash rewards accumulated as of the reporting month. Institutions should report the cumulative reward available to the customer. The institution should report Net Cash Reward = Cumulative earned cash (or cash equivalent) - redeemed/forfeited cash (or cash equivalent). For Cards that do not offer rewards, institutions should report "0". For cards that offer rewards but the net accumulative balance for the month is negative, institutions should report the negative values as-is. Do not include merchant loyalty points if a merchant houses the loyalty points on its own system.

### Line Item 24: Reward Type (MDRM M067)
Report reward type: 1 = Cash, 2 = Miles, 3 = None, 4 = Other.

### Line Item 25: Account Cycle Date (MDRM M068)
Report the date in which transactions were accumulated for billing in the reporting month. For accounts that cycle more than one time during the reporting month report the last cycle information. All data elements related to account balances and status should be as of the last cycle end date; all data elements related to account activities and fees should be aggregated from the last reporting cycle end date in the previous FR Y-14M month to the current reporting cycle end date in the current FR Y-14M month. Leave blank if the account does not have a statement date in the current reporting month.

### Line Item 26: Account Origination Date (MDRM M069)
Report the date on which the original credit card was issued. If unknown due to acquisition or merger, leave blank. In cases where an account was closed (for example, card loss or theft) and reopened, report the original account origination date and not subsequent issuance date(s).

### Line Item 27: Acquisition Date (MDRM M070)
For accounts resulting from acquisition or merger, report the loan's acquisition or merger date. If the date of acquisition/merger is unknown report 19000101, if the loan was not acquired, report 19000102.

### Line Item 28: Multiple Banking Relationships (MDRM M071)
Report accounts that currently have other non-credit card banking relationships with the bank. Loans the BHC/IHC owns, but does not service should be included in the calculation for this field. Insurance and safety box are not considered as a banking relationship.
Codes: 1 = Deposit, 2 = Trust or investment account, 3 = Mortgage, 4 = Home Equity, 5 = Auto, 6 = Student Loans, 7 = Installment Loans, 8 = More than one types, 9 = Unknown, 0 = No other products or cross-sellings.

### Line Item 29: Multiple Credit Card Relationships (MDRM M072)
Report accounts where the bank has issued more than one credit card to the primary or joint account holder(s). (1 = Yes, 0 = No)

### Line Item 30: Joint Account (MDRM M073)
Report whether the account has more than one primary obligor. Exclude other authorized users. (1 = Yes, 0 = No)

### Line Item 31: Authorized Users (MDRM M074)
Report total number of authorized users including primary obligors. Leave blank for closed/charged off accounts with or without a balance.

### Line Item 32: Flagged as Securitized (MDRM M075)
Report whether the account has been securitized (designated for inclusion in a master trust). (1 = Yes, 0 = No)
