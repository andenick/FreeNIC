# FR Y-14M Instructions - Chunk 013
## Schedule C: Address Matching Loan Level Data Collection; Schedule D: Domestic Credit Card (Introduction and D.1 Items 1-7)

### Schedule C: Address Matching Loan Level Data Collection

#### Data Format
This will be a "month-end" file produced each month and reported no later than thirty (30) calendar days after the end of the reporting month. This file will contain one record per active loan in the contributor's inventory.

For every loan reported on the FR Y-14M First Lien Closed-end 1-4 Family Loan or Home Equity Loan and Home Equity Line of Credit Schedules, the BHCs or IHCs or SLHCs shall provide the information set forth in this schedule. Starting with the March 2013 data submission, these schedules have been expanded to include REO loans, and such loans will also be included in the Address Matching data collection.

#### Additional Formatting
- Options for all line items are comprehensive identifying a valid value for all loans regardless of status. If a value is Unknown or Unavailable, the line item should be left blank - populated with a sequence of two vertical bars (|, ASCII decimal 124, ASCII hexadecimal 7C) with no intervening spaces or explicit N/A coding.
- No quotation marks should be used as text identifiers.
- Please do not provide a header row.

Inactive inventory that was paid off in one manner or another (servicing transfer, involuntary liquidation or paid-in-full by borrower) before the beginning of the reporting month should not be included.

#### File Naming Convention
The standard data files, which the Federal Reserve will receive from the data aggregator, will follow the following file naming conventions. BHCs, IHCs, and SLHCs will use this naming convention to send the data files to the data aggregator.

`FRY14_ADDRESSMATCH_<ID_RSSD>_<AS_OF_MON_ID>_<SUBMISSION_NUMBER>.TXT`

SUBMISSION_NUMBER will be used to track revisions and resubmissions of this schedule. It must be populated as a two-digit number. For example, the first submission for a given period would have a submission number of '01.' If the BHC or IHC or SLHC has to resubmit the same file, then use '02' for the next submission, and so on.

In the case of the Address Matching Schedule, BHCs, IHCs, and SLHCs should provide the data each month in a single bar-delimited text file. This is also referred to as a pipe-delimited text file. Line items should be delimited with a vertical bar (|, ASCII decimal 124, ASCII hexadecimal 7C).

Example: Institution A has ID_RSSD equal to 999999. For the Address Match data file submitted for period 201206, the file would be named as FRY14_ADDRESSMATCH_999999_201206_01.TXT. Any subsequent revised Address Match data file submitted by the institution for the same period will be named as FRY14_ADDRESSMATCH_999999_201206_02.TXT, and so on.

### C.1 Data Table
The C.1 Data Table contains 13 line items covering loan identification, property and mailing addresses, liquidation status, lien position, census tract, and data file reference. See table CSV for full details.

---

### Schedule D: Domestic Credit Card Data Collection Data Dictionary

#### Loan Population
Loans should be reported based on their classification on the FR Y-9C, Schedule HC-C (i.e. based on the loans security, counterparty, or purpose). Refer to the FR Y-9C instructions for Schedule HC-C for guidance on loan classification. Below is a list of FR Y-9C items that are considered applicable loans for this schedule:

a. **General Purpose Credit Cards:** These are credit cards that can be used at a wide variety of merchants, including any who accept MasterCard, Visa, American Express or Discover credit cards. Include affinity, co-brand cards in this category, and student cards if applicable. This includes loans reported on the FR Y-9C, Schedule HC-C, item 6.a, and domestic general purpose cards reported in other FR Y-9C lines.

b. **Private Label Credit Cards:** These credit cards, also known as Proprietary Credit Cards, are tied to the retailer issuing the card and can only be used in that retailer's stores. Include oil & gas cards in this loan type, and student cards if applicable. This includes loans reported on the FR Y-9C, Schedule HC-C, item 6.a, and domestic private label cards reported in other FR Y-9C lines.

c. **Business Card:** Include small business credit card accounts where the loan is underwritten with the sole proprietor or primary business owner as applicant. If the commercial credit card account is delinquency managed or scored then report as a business card. For commercial credit card accounts with no individual liability and performance not reported to credit bureaus and over $1 million in committed balances then report on the FR Y-14Q Corporate Loan Schedule. Report at the control account level or the individual pay level (not at the sub-account level). This includes SME credit card loans that are those reported on the FR Y-9C, Schedule HC-C, item 4.a, and domestic business cards reported in other FR Y-9C lines.

d. **Corporate Credit Cards:** Employer-sponsored credit cards for use by a company's employees. If the commercial card account is classifiably managed, and either there is any individual/joint liability or performance is reported to a credit bureau then report as a corporate card. This includes US corporate credit card loans that are those reported on the FR Y-9C, Schedule HC-C, item 4.a, and domestic corporate cards reported in other FR Y-9C lines.

e. **Other:** Other cards accounts to consumers, small business, or corporations reported in the FR Y-9C in line items not represented above. Please do not include home equity lines of credit or other revolving consumer loans other than credit cards.

#### Additional Reporting Requirements
- Do not report data from international cards but include domestic cards, as defined by the FR Y-9C glossary entry for "domestic offices".
- For all variables reported please report as blank if information is missing or unknown. Also, if a line item does not apply to the loan, the line item should be left blank.
- Account and loan-level files should sum up to the portfolio level. An amount, zero or null (be left blank) should be entered for all items, except in those cases where other options such as "not available" or "other" are specified.
- Avoid account duplications.
- For account level variables representing monetary value please use the U.S. Dollar ($) as the reporting monetary unit.
- For portfolio level variables representing monetary value please use millions of dollars ($ Millions) as the reporting monetary unit.
- In the case of closed or charged-off accounts, account information should be reported up to 24 months after the account's closure or charge off, if at the time of closure or charge-off the account had a positive unpaid balance that needed to be repaid or recovered. Closed accounts that are only partially charged-off and have a positive balance that needs to be repaid should continue to be reported beyond 24 months until full repayment or fully charged off. Line item #61 (Charge-off Reason code) can be used to identify charged off accounts. If the account was closed due to inactivity or did not have a positive unpaid balance at the time of closure, do not continue reporting after the month of closure.
- All accounts managed (including accounts tagged as securitized) should be reported as managed accounts. All accounts owned but not tagged as securitized should be reported as booked accounts.
- Cards should be included regardless of delinquency status.
- For portfolio level variables, the list of summary variables is to be reported for each portfolio segment. The variables 'Credit Card Type' and 'Lending Type' should be used to define the portfolio segment in a reporting month. There are four Credit Card Type segments and four Lending type segments, resulting in up to 16 rows of data per reporting month.
- No quotation marks should be used as text identifiers.
- Mandatory variables should be provided in all cases. Optional variables should be provided when available, or when not directly available they should be provided on a best effort basis. Variables designated "optional" must be reported if the reporter uses the requested information in the course of the reporter's risk management practices or otherwise generates or stores the requested information.
- Items related to the most recent capital framework are mandatory for firms subject to the advanced approaches rule, optional for all others.

#### Inclusion of Corporate and Business Card Loans
- Loans for which a commercially graded corporation is ultimately responsible for repayment of credit losses incurred should be reported in the FR Y-14Q Corporate Loan schedule.
- If there is any individual liability associated with the sub-lines such that individual borrower characteristics are taken into account during the underwriting decision, and/or performance on the credit is reported to the credit bureaus, the loan should be reported in the FR Y-14M Credit Card schedule.

### D.1 Loan Level Table (Items 1-7)
The D.1 Loan Level Table for Schedule D uses a different column structure than Schedules A-C, with columns: Line Item No., Line Item Name, Technical Line Item Name, MDRM (CCRS), Description, Static or Dynamic, Mandatory or Optional, and Format. See table CSV for Items 1-7.
