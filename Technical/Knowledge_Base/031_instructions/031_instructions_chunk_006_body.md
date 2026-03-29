# FFIEC 031 — Chunk 006: Schedules RC-O (Deposit Insurance), RC-P (Mortgage Banking), RC-Q (Fair Value)

**Pages**: 51-60 of 88 (RC-36 through RC-45)

---

## Schedule RC-O — Other Data for Deposit Insurance Assessments (Pages 51-56, RC-36 through RC-41)

All FDIC-insured depository institutions must complete items 1 through 9, 10, and 11, Memorandum item 1, and, if applicable, item 9.a, Memorandum items 2 through 18 each quarter. Unless otherwise indicated, complete items 1 through 11 and Memorandum items 1 through 4 on an "unconsolidated single FDIC certificate number basis" and complete Memorandum items 5 through 18 on a fully consolidated basis.

### Items 1-11: Core Deposit Insurance Data (RCFD unless noted)

| Item | Description | Prefix | Code |
|------|-------------|--------|------|
| 1 | Total deposit liabilities before exclusions (gross) as defined in Section 3(l) of the Federal Deposit Insurance Act | RCFD | F236 |
| 2 | Total allowable exclusions, including interest accrued and unpaid on allowable exclusions (including foreign deposits) | RCFD | F237 |
| 3 | Total foreign deposits, including interest accrued and unpaid thereon (included in item 2) | RCFN | F234 |
| 4 | Average consolidated total assets for the calendar quarter | RCFD | K652 |
| 4.a | Averaging method used (1=daily, 2=weekly) | RCFD | K653 |
| 5 | Average tangible equity for the calendar quarter | RCFD | K654 |
| 6 | Holdings of long-term unsecured debt issued by other FDIC-insured depository institutions | RCFD | K655 |

Tangible equity is defined as Tier 1 capital as set forth in banking agencies' regulatory capital standards and reported in Schedule RC-R, Part I, item 26.

#### Item 7: Unsecured "Other Borrowings" by Remaining Maturity (RCFD)

Sum of items 7.a through 7.d must be less than or equal to Schedule RC-M, items 5.b.(1)(a)-(d) minus item 10.b.

- **7.a.** One year or less — G465
- **7.b.** Over one year through three years — G466
- **7.c.** Over three years through five years — G467
- **7.d.** Over five years — G468

#### Item 8: Subordinated Notes and Debentures by Remaining Maturity (RCFD)

Sum of items 8.a through 8.d must equal Schedule RC, item 19.

- **8.a.** One year or less — G469
- **8.b.** Over one year through three years — G470
- **8.c.** Over three years through five years — G471
- **8.d.** Over five years — G472

#### Items 9-11: Bank Certifications

- **9.** Brokered reciprocal deposits (included in RC-E, Part I, M.1.b) — RCON G803
- **9.a.** Fully consolidated brokered reciprocal deposits (for institutions owning another insured depository institution) — RCON L190
- **10.** Banker's bank certification (Yes/No) — RCFD K656
  - **10.a.** Banker's bank deduction — RCFD K657
  - **10.b.** Banker's bank deduction limit — RCFD K658
- **11.** Custodial bank certification (Yes/No) — RCFD K659
  - **11.a.** Custodial bank deduction — RCFD K660
  - **11.b.** Custodial bank deduction limit — RCFD K661

### Memoranda

#### M.1: Deposit Account Breakdown by Size (RCON)

Sum of M.1.a.(1), M.1.b.(1), M.1.c.(1), and M.1.d.(1) must equal RC-O item 1 less item 2.

| Item | Description | Code |
|------|-------------|------|
| M.1.a.(1) | Amount of deposit accounts (excl. retirement) of $250,000 or less | F049 |
| M.1.a.(2) | Number of deposit accounts (excl. retirement) of $250,000 or less | F050 |
| M.1.b.(1) | Amount of deposit accounts (excl. retirement) of more than $250,000 | F051 |
| M.1.b.(2) | Number of deposit accounts (excl. retirement) of more than $250,000 | F052 |
| M.1.c.(1) | Amount of retirement deposit accounts of $250,000 or less | F045 |
| M.1.c.(2) | Number of retirement deposit accounts of $250,000 or less | F046 |
| M.1.d.(1) | Amount of retirement deposit accounts of more than $250,000 | F047 |
| M.1.d.(2) | Number of retirement deposit accounts of more than $250,000 | F048 |

#### M.2-M.4

- **M.2.** Estimated amount of uninsured deposits (banks with $1 billion+ total assets) — RCON 5597
- **M.3.** Has institution been consolidated with parent bank/savings association? — TEXT A545 / RCON A545 (FDIC Cert. No.)
- **M.4.** Dually payable deposits in foreign branches — RCFN GW43

#### M.5-M.15: Large and Highly Complex Institutions (RCFD)

Items 5 through 12 for "large institutions" and "highly complex institutions." Items 6 through 9, 14, and 15 are confidential.

| Item | Description | Code |
|------|-------------|------|
| M.5 | CECL transitional amount attributable to loans and leases held for investment | MW53 |
| M.6.a | Criticized items — Special mention | K663 |
| M.6.b | Criticized items — Substandard | K664 |
| M.6.c | Criticized items — Doubtful | K665 |
| M.6.d | Criticized items — Loss | K666 |
| M.7.a | Nontraditional 1-4 family residential mortgage loans | N025 |
| M.7.b | Securitizations of nontraditional 1-4 family residential mortgage loans | N026 |
| M.8.a | Higher-risk consumer loans | N027 |
| M.8.b | Securitizations of higher-risk consumer loans | N028 |
| M.9.a | Higher-risk C&I loans and securities | N029 |
| M.9.b | Securitizations of higher-risk C&I loans and securities | N030 |
| M.10.a | Total unfunded commitments to fund construction/land/other land loans | K676 |
| M.10.b | Portion of unfunded commitments guaranteed or insured by U.S. government | K677 |
| M.11 | OREO recoverable from U.S. government under guarantee/insurance | K669 |
| M.12 | Nonbrokered time deposits of more than $250,000 in domestic offices | RCON K678 |

#### M.13: Guaranteed/Insured Loans (Large and Highly Complex Institutions) (RCFD)

Item 13.a for both "large" and "highly complex"; items 13.b-13.h for "large institutions" only.

| Item | Description | Code |
|------|-------------|------|
| M.13.a | Construction, land development, and other land loans secured by RE | N177 |
| M.13.b | Loans secured by multifamily residential and nonfarm nonresidential | N178 |
| M.13.c | Closed-end first liens on 1-4 family residential | N179 |
| M.13.d | Closed-end junior liens and revolving open-end 1-4 family residential | N180 |
| M.13.e | Commercial and industrial loans | N181 |
| M.13.f | Credit card loans for personal expenditures | N182 |
| M.13.g | All other loans for personal expenditures | N183 |
| M.13.h | Non-agency residential mortgage-backed securities | M963 |

#### M.14-M.15: Highly Complex Institutions Only (RCFD)

- **M.14.** Amount of institution's largest counterparty exposure — K673
- **M.15.** Total amount of institution's 20 largest counterparty exposures — K674

#### M.16: Loan Modifications Guaranteed/Insured (RCFD)

- **M.16.** Portion of loan modifications to borrowers experiencing financial difficulty that are in compliance and guaranteed/insured by U.S. government — L189

#### M.17: Fully Consolidated Data (for Large/Highly Complex Institutions owning another insured depository)

| Item | Description | Prefix | Code |
|------|-------------|--------|------|
| M.17.a | Total deposit liabilities before exclusions (gross) | RCFD | L194 |
| M.17.b | Total allowable exclusions | RCFD | L195 |
| M.17.c | Unsecured other borrowings with remaining maturity of one year or less | RCFD | L196 |
| M.17.d | Estimated amount of uninsured deposits in domestic offices | RCON | L197 |

#### M.18: Two-Year Probability of Default (PD) Buckets

For "large institutions" and "highly complex institutions" only. Confidential. Outstanding balance of 1-4 family residential mortgage loans, consumer loans, and consumer leases by two-year PD, reported across 15 columns (A through O):

- Columns A-H: <=1%, 1.01-4%, 4.01-7%, 7.01-10%, 10.01-14%, 14.01-16%, 16.01-18%, 18.01-20%
- Columns I-M: 20.01-22%, 22.01-26%, 26.01-30%, >30%, Unscoreable
- Column N: Total
- Column O: PDs Were Derived Using (1=third-party vendor, 2=internal, 3=combination, 0=zero total)

Product types: M.18.a (nontraditional 1-4 family), M.18.b (closed-end first liens), M.18.c (closed-end junior liens), M.18.d (revolving open-end 1-4 family), M.18.e (credit cards), M.18.f (automobile loans), M.18.g (student loans), M.18.h (other consumer), M.18.i (consumer leases), M.18.j (total). See table CSV for all MDRM codes.

---

## Schedule RC-P — 1-4 Family Residential Mortgage Banking Activities in Domestic Offices (Page 57, RC-42)

To be completed by banks where either 1-4 family residential mortgage loan originations and purchases for resale, loan sales, or quarter-end loans held for sale or trading in domestic offices exceed $10 million for two consecutive quarters.

| Item | Description | Prefix | Code |
|------|-------------|--------|------|
| 1 | Retail originations during the quarter of 1-4 family residential mortgage loans for sale | RCON | HT81 |
| 2 | Wholesale originations and purchases during the quarter of 1-4 family residential mortgage loans for sale | RCON | HT82 |
| 3 | 1-4 family residential mortgage loans sold during the quarter | RCON | FT04 |
| 4 | 1-4 family residential mortgage loans held for sale or trading at quarter-end | RCON | FT05 |
| 5 | Noninterest income for the quarter from sale, securitization, and servicing of 1-4 family residential mortgage loans | RIAD | HT85 |
| 6 | Repurchases and indemnifications of 1-4 family residential mortgage loans during the quarter | RCON | HT86 |
| 7.a | Rep and warranty reserves — U.S. government and GSE | RCON | L191 |
| 7.b | Rep and warranty reserves — Other parties | RCON | L192 |
| 7.c | Total rep and warranty reserves (sum of 7.a and 7.b) | RCON | M288 |

Exclude originations and purchases of 1-4 family residential mortgage loans that are held for investment.

---

## Schedule RC-Q — Assets and Liabilities Measured at Fair Value on a Recurring Basis (Pages 58-60, RC-43 through RC-45)

To be completed by banks that: (1) have elected to report financial instruments or servicing assets/liabilities at fair value under a fair value option with changes in fair value recognized in earnings, or (2) are required to complete Schedule RC-D, Trading Assets and Liabilities.

Five columns: (A) Total Fair Value Reported on Schedule RC, (B) LESS: Amounts Netted in Determination of Total Fair Value, (C) Level 1 Fair Value Measurements, (D) Level 2 Fair Value Measurements, (E) Level 3 Fair Value Measurements.

### Assets (RCFD)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| 1 | AFS debt securities and equity securities with readily determinable FV not held for trading | JA36 | G474 | G475 | G476 | G477 |
| 2 | Federal funds sold and securities purchased under agreements to resell | G478 | G479 | G480 | G481 | G482 |
| 3 | Loans and leases held for sale | G483 | G484 | G485 | G486 | G487 |
| 4 | Loans and leases held for investment | G488 | G489 | G490 | G491 | G492 |
| 5.a | Trading assets — Derivative assets | 3543 | G493 | G494 | G495 | G496 |
| 5.b | Trading assets — Other trading assets | G497 | G498 | G499 | G500 | G501 |
| 5.b.(1) | Nontrading securities at FV with changes in earnings (included in 5.b) | F240 | F684 | F692 | F241 | F242 |
| 6 | All other assets | G391 | G392 | G395 | G396 | G804 |
| 7 | Total assets measured at FV on recurring basis (sum of 1 through 5.b plus 6) | G502 | G503 | G504 | G505 | G506 |

Item 1, column A, must equal sum of Schedule RC, items 2.b and 2.c.

### Liabilities (RCFD)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| 8 | Deposits | F252 | F686 | F694 | F253 | F254 |
| 9 | Federal funds purchased and securities sold under agreements to repurchase | G507 | G508 | G509 | G510 | G511 |
| 10.a | Trading liabilities — Derivative liabilities | 3547 | G512 | G513 | G514 | G515 |
| 10.b | Trading liabilities — Other trading liabilities | G516 | G517 | G518 | G519 | G520 |
| 11 | Other borrowed money | G521 | G522 | G523 | G524 | G525 |
| 12 | Subordinated notes and debentures | G526 | G527 | G528 | G529 | G530 |
| 13 | All other liabilities | G805 | G806 | G807 | G808 | G809 |
| 14 | Total liabilities measured at FV on recurring basis (sum of 8 through 13) | G531 | G532 | G533 | G534 | G535 |

### RC-Q Memoranda

#### M.1: All Other Assets Breakdown (items > $100,000 and > 25% of item 6) (RCFD)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| M.1.a | Mortgage servicing assets | G536 | G537 | G538 | G539 | G540 |
| M.1.b | Nontrading derivative assets | G541 | G542 | G543 | G544 | G545 |
| M.1.c-f | User-defined descriptions (TEXT codes G546, G551, G556, G561) | varies | varies | varies | varies | varies |

#### M.2: All Other Liabilities Breakdown (items > $100,000 and > 25% of item 13) (RCFD)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| M.2.a | Loan commitments (not accounted for as derivatives) | F261 | F689 | F697 | F262 | F263 |
| M.2.b | Nontrading derivative liabilities | G566 | G567 | G568 | G569 | G570 |
| M.2.c-f | User-defined descriptions (TEXT codes G571, G576, G581, G586) | varies | varies | varies | varies | varies |

#### M.3-M.4: Loans Measured at Fair Value (Consolidated Bank, RCFD)

| Item | Description | Code |
|------|-------------|------|
| M.3.a.(1) | Loans secured by RE — 1-4 family residential | HT87 |
| M.3.a.(2) | Loans secured by RE — All other | HT88 |
| M.3.b | Commercial and industrial loans | F585 |
| M.3.c | Consumer loans (includes purchased paper) | HT89 |
| M.3.d | Other loans | F589 |
| M.4.a.(1) | Unpaid principal balance — 1-4 family residential | HT91 |
| M.4.a.(2) | Unpaid principal balance — All other RE | HT92 |
| M.4.b | Unpaid principal balance — C&I | F597 |
| M.4.c | Unpaid principal balance — Consumer | HT93 |
| M.4.d | Unpaid principal balance — Other | F601 |
