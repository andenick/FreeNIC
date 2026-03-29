# FFIEC 041 — Chunk 006 (Pages 51-60)
## Schedules RC-O, RC-P, RC-Q

---

## Schedule RC-O — Other Data for Deposit Insurance Assessments

**Applicability**: All FDIC-insured depository institutions must complete items 1 and 2, 4 through 9, 10, and 11, Memorandum item 1, and, if applicable, item 9.a, Memorandum items 2, 3, and 5 through 18 each quarter.

**Reporting basis**: Items 1 through 11 and Memorandum items 1 through 3 on an "unconsolidated single FDIC certificate number basis" (see instructions). Memorandum items 5 through 18 on a fully consolidated basis.

### Main Items (Pages 51)

| Item | Description | RCON | Notes |
|------|-------------|------|-------|
| 1 | Total deposit liabilities before exclusions (gross) as defined in Section 3(l) of the Federal Deposit Insurance Act and FDIC regulations | F236 | |
| 2 | Total allowable exclusions, including interest accrued and unpaid on allowable exclusions | F237 | |
| 3 | Not applicable | — | |
| 4 | Average consolidated total assets for the calendar quarter | K652 | |
| 4.a | Averaging method used (1=daily, 2=weekly) | K653 | Number field |
| 5 | Average tangible equity for the calendar quarter | K654 | See footnote 1 |
| 6 | Holdings of long-term unsecured debt issued by other FDIC-insured depository institutions | K655 | |
| 7 | Unsecured "Other borrowings" with a remaining maturity of (sum of 7.a-7.d must be <= RC-M items 5.b.(1)(a)-(d) minus item 10.b): | | |
| 7.a | One year or less | G465 | |
| 7.b | Over one year through three years | G466 | |
| 7.c | Over three years through five years | G467 | |
| 7.d | Over five years | G468 | |
| 8 | Subordinated notes and debentures with a remaining maturity of (sum of 8.a-8.d must equal Schedule RC, item 19): | | |
| 8.a | One year or less | G469 | |
| 8.b | Over one year through three years | G470 | |
| 8.c | Over three years through five years | G471 | |
| 8.d | Over five years | G472 | |
| 9 | Brokered reciprocal deposits (included in RC-E, Memo item 1.b) | G803 | |
| 9.a | Fully consolidated brokered reciprocal deposits | L190 | Complete on fully consolidated basis by institutions owning another insured depository institution |
| 10 | Banker's bank certification (Yes/No) | K656 | |
| 10.a | Banker's bank deduction | K657 | Complete if item 10 = YES |
| 10.b | Banker's bank deduction limit | K658 | Complete if item 10 = YES |
| 11 | Custodial bank certification (Yes/No) | K659 | |
| 11.a | Custodial bank deduction | K660 | Complete if item 11 = YES |
| 11.b | Custodial bank deduction limit | K661 | Complete if item 11 = YES |

**Footnote 1**: Tangible equity is defined as Tier 1 capital as set forth in banking agencies' regulatory capital standards, reported in Schedule RC-R, Part I, item 26, except as described in the instructions.

**Footnote 2**: If the amount reported in item 11.b is zero, item 11.a may be left blank.

### Memoranda (Page 52)

**Memorandum item 1**: Total deposit liabilities of the bank, including related interest accrued and unpaid, less allowable exclusions. Sum of M.1.a.(1), M.1.b.(1), M.1.c.(1), and M.1.d.(1) must equal RC-O item 1 less item 2.

| Item | Description | RCON | Notes |
|------|-------------|------|-------|
| M.1.a.(1) | Amount of deposit accounts (excl. retirement) of $250,000 or less | F049 | |
| M.1.a.(2) | Number of deposit accounts (excl. retirement) of $250,000 or less | F050 | Number |
| M.1.b.(1) | Amount of deposit accounts (excl. retirement) of more than $250,000 | F051 | |
| M.1.b.(2) | Number of deposit accounts (excl. retirement) of more than $250,000 | F052 | Number |
| M.1.c.(1) | Amount of retirement deposit accounts of $250,000 or less | F045 | |
| M.1.c.(2) | Number of retirement deposit accounts of $250,000 or less | F046 | Number |
| M.1.d.(1) | Amount of retirement deposit accounts of more than $250,000 | F047 | |
| M.1.d.(2) | Number of retirement deposit accounts of more than $250,000 | F048 | Number |
| M.2 | Estimated amount of uninsured deposits including related interest accrued and unpaid | 5597 | Banks with $1B+ in total assets |
| M.3 | Consolidated with parent bank/savings association (legal title and FDIC Cert. No.) | A545 | Text/Number |

**Footnotes**:
- Dollar amounts in M.1.a-M.1.d reflect deposit insurance limits in effect on the report date.
- $1B asset-size test based on total assets reported on June 30, 2024, Report of Condition.
- Uninsured deposits should be estimated based on deposit insurance limits in M.1.a-M.1.d.

### Memoranda — Continued (Page 53)

**Confidentiality note**: Amounts reported in Memorandum items 6 through 9, 14, and 15 will not be made available to the public on an individual institution basis.

Memorandum items 5 through 12 are to be completed by "large institutions" and "highly complex institutions" as defined in FDIC regulations.

| Item | Description | RCON | Notes |
|------|-------------|------|-------|
| M.5 | Applicable portion of CECL transitional amount attributable to loans and leases held for investment | MW53 | |
| M.6.a | Criticized and classified items: Special mention | K663 | |
| M.6.b | Substandard | K664 | |
| M.6.c | Doubtful | K665 | |
| M.6.d | Loss | K666 | |
| M.7.a | Nontraditional 1-4 family residential mortgage loans | N025 | Assessment purposes only |
| M.7.b | Securitizations of nontraditional 1-4 family residential mortgage loans | N026 | |
| M.8.a | Higher-risk consumer loans | N027 | Assessment purposes only |
| M.8.b | Securitizations of higher-risk consumer loans | N028 | |
| M.9.a | Higher-risk C&I loans and securities | N029 | Assessment purposes only |
| M.9.b | Securitizations of higher-risk C&I loans and securities | N030 | |
| M.10.a | Total unfunded commitments (construction, land dev., other land loans secured by RE) | K676 | |
| M.10.b | Portion of unfunded commitments guaranteed/insured by U.S. government (including FDIC) | K677 | |
| M.11 | Amount of OREO recoverable from U.S. government (excl. FDIC loss-sharing) | K669 | |
| M.12 | Nonbrokered time deposits of more than $250,000 in domestic offices (included in RC-E, Part I, Memo item 2.d) | K678 | |

### Memoranda items 13-15 (Page 53)

M.13.a is to be completed by "large institutions" and "highly complex institutions." M.13.b through M.13.h are for "large institutions" only.

| Item | Description | RCON |
|------|-------------|------|
| M.13.a | Portion of funded loans/securities guaranteed by U.S. govt: Construction, land development, other land loans secured by RE | N177 |
| M.13.b | Loans secured by multifamily residential and nonfarm nonresidential properties | N178 |
| M.13.c | Closed-end loans secured by first liens on 1-4 family residential properties | N179 |
| M.13.d | Closed-end loans secured by junior liens on 1-4 family residential properties and revolving, open-end loans secured by 1-4 family RE | N180 |
| M.13.e | Commercial and industrial loans | N181 |
| M.13.f | Credit card loans to individuals | N182 |
| M.13.g | All other loans to individuals | N183 |
| M.13.h | Non-agency residential mortgage-backed securities | M963 |

M.14 and M.15 are for "highly complex institutions" only:

| Item | Description | RCON |
|------|-------------|------|
| M.14 | Amount of the institution's largest counterparty exposure | K673 |
| M.15 | Total amount of the institution's 20 largest counterparty exposures | K674 |

### Memorandum item 16-17 (Page 54)

| Item | Description | RCON | Notes |
|------|-------------|------|-------|
| M.16 | Portion of loan modifications to borrowers experiencing financial difficulty in compliance with modified terms, guaranteed/insured by U.S. government (included in RC-C, Part I, Memo item 1) | L189 | Large + highly complex institutions |
| M.17.a | Total deposit liabilities before exclusions (gross) — fully consolidated | L194 | Large + highly complex institutions that own another insured depository institution |
| M.17.b | Total allowable exclusions — fully consolidated | L195 | |
| M.17.c | Unsecured "Other borrowings" with remaining maturity of one year or less | L196 | |
| M.17.d | Estimated amount of uninsured deposits — fully consolidated | L197 | |

### Memorandum item 18 — Probability of Default Matrix (Pages 55-56)

For "large institutions" and "highly complex institutions." Not made available to the public on an individual institution basis.

**Item 18**: Outstanding balance of 1-4 family residential mortgage loans, consumer loans, and consumer leases by two-year probability of default.

Columns A through O represent PD buckets, Column N = Total, Column O = PDs Were Derived Using (Number field).

PD Buckets: <=1% (A), 1.01-4% (B), 4.01-7% (C), 7.01-10% (D), 10.01-14% (E), 14.01-16% (F), 16.01-18% (G), 18.01-20% (H), 20.01-22% (I), 22.01-26% (J), 26.01-30% (K), >30% (L), Unscoreable (M), Total (N), PD Method (O).

See table CSV file `041_instructions_chunk_006_table_001.csv` for full RCON code matrix.

**PD derivation method (Column O)**: 1 = third-party vendor scores/default rate mappings; 2 = internal approach; 3 = combination of vendor and internal for different loans within same product type; 0 = if total in Column N is zero.

---

## Schedule RC-P — 1-4 Family Residential Mortgage Banking Activities (Page 57)

**Applicability**: Banks at which either 1-4 family residential mortgage loan originations and purchases for resale from all sources, loan sales, or quarter-end loans held for sale or trading exceed $10 million for two consecutive quarters.

| Item | Description | Code | Type |
|------|-------------|------|------|
| 1 | Retail originations during the quarter of 1-4 family residential mortgage loans for sale | RCON HT81 | |
| 2 | Wholesale originations and purchases during the quarter of 1-4 family residential mortgage loans for sale | RCON HT82 | |
| 3 | 1-4 family residential mortgage loans sold during the quarter | RCON FT04 | |
| 4 | 1-4 family residential mortgage loans held for sale or trading at quarter-end (included in RC items 4.a and 5) | RCON FT05 | |
| 5 | Noninterest income for the quarter from the sale, securitization, and servicing of 1-4 family residential mortgage loans (included in RI items 5.c, 5.f, 5.g, and 5.i) | RIAD HT85 | |
| 6 | Repurchases and indemnifications of 1-4 family residential mortgage loans during the quarter | RCON HT86 | |
| 7.a | Representation and warranty reserves: For representations and warranties made to U.S. government agencies and government-sponsored agencies | RCON L191 | |
| 7.b | For representations and warranties made to other parties | RCON L192 | |
| 7.c | Total representation and warranty reserves (sum of 7.a and 7.b) | RCON M288 | |

**Footnote**: Exclude originations and purchases of 1-4 family residential mortgage loans that are held for investment.

---

## Schedule RC-Q — Assets and Liabilities Measured at Fair Value on a Recurring Basis (Pages 58-60)

**Applicability**: Banks that: (1) Have elected to report financial instruments or servicing assets and liabilities at fair value under a fair value option with changes in fair value recognized in earnings, or (2) Are required to complete Schedule RC-D, Trading Assets and Liabilities.

### Structure
Five columns: (A) Total Fair Value Reported on Schedule RC, (B) LESS: Amounts Netted in Determination of Total Fair Value, (C) Level 1 Fair Value Measurements, (D) Level 2 Fair Value Measurements, (E) Level 3 Fair Value Measurements.

### Assets (Page 58)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| 1 | AFS debt securities and equity securities with readily determinable fair values not held for trading | JA36 | G474 | G475 | G476 | G477 |
| 2 | Not applicable | — | — | — | — | — |
| 3 | Loans and leases held for sale | G483 | G484 | G485 | G486 | G487 |
| 4 | Loans and leases held for investment | G488 | G489 | G490 | G491 | G492 |
| 5.a | Trading assets: Derivative assets | 3543 | G493 | G494 | G495 | G496 |
| 5.b | Trading assets: Other trading assets | G497 | G498 | G499 | G500 | G501 |
| 5.b.(1) | Nontrading securities at fair value with changes in fair value reported in current earnings (included in 5.b above) | F240 | F684 | F692 | F241 | F242 |
| 6 | All other assets | G391 | G392 | G395 | G396 | G804 |
| 7 | Total assets measured at fair value on a recurring basis (sum of items 1 through 5.b plus item 6) | G502 | G503 | G504 | G505 | G506 |

**Footnote**: Item 1, column A, must equal the sum of Schedule RC, items 2.b and 2.c.

### Liabilities (Page 58)

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| 8 | Deposits | F252 | F686 | F694 | F253 | F254 |
| 9 | Not applicable | — | — | — | — | — |
| 10.a | Trading liabilities: Derivative liabilities | 3547 | G512 | G513 | G514 | G515 |
| 10.b | Trading liabilities: Other trading liabilities | G516 | G517 | G518 | G519 | G520 |
| 11-12 | Not applicable | — | — | — | — | — |
| 13 | All other liabilities | G805 | G806 | G807 | G808 | G809 |
| 14 | Total liabilities measured at fair value on a recurring basis (sum of items 8 through 13) | G531 | G532 | G533 | G534 | G535 |

### Memoranda (Page 59)

**M.1**: All other assets — itemize and describe amounts included in RC-Q item 6 that are >$100,000 and exceed 25% of item 6:

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| M.1.a | Mortgage servicing assets | G536 | G537 | G538 | G539 | G540 |
| M.1.b | Nontrading derivative assets | G541 | G542 | G543 | G544 | G545 |
| M.1.c-f | User-defined (TEXT fields) | G546-G561 | G547-G562 | G548-G563 | G549-G564 | G550-G565 |

**M.2**: All other liabilities — itemize and describe amounts included in RC-Q item 13 that are >$100,000 and exceed 25% of item 13:

| Item | Description | Col A | Col B | Col C | Col D | Col E |
|------|-------------|-------|-------|-------|-------|-------|
| M.2.a | Loan commitments (not accounted for as derivatives) | F261 | F689 | F697 | F262 | F263 |
| M.2.b | Nontrading derivative liabilities | G566 | G567 | G568 | G569 | G570 |
| M.2.c-f | User-defined (TEXT fields) | G571-G586 | G572-G587 | G573-G588 | G574-G589 | G575-G590 |

### Memoranda — Continued (Page 60)

**M.3**: Loans measured at fair value (included in RC-C, Part I, items 1 through 9):

| Item | Description | RCON |
|------|-------------|------|
| M.3.a.(1) | Loans secured by RE: Secured by 1-4 family residential properties | HT87 |
| M.3.a.(2) | All other loans secured by real estate | HT88 |
| M.3.b | Commercial and industrial loans | F585 |
| M.3.c | Loans to individuals (consumer loans) | HT89 |
| M.3.d | Other loans | F589 |

**M.4**: Unpaid principal balance of loans measured at fair value (reported in M.3):

| Item | Description | RCON |
|------|-------------|------|
| M.4.a.(1) | Loans secured by RE: Secured by 1-4 family residential properties | HT91 |
| M.4.a.(2) | All other loans secured by real estate | HT92 |
| M.4.b | Commercial and industrial loans | F597 |
| M.4.c | Loans to individuals (consumer loans) | HT93 |
| M.4.d | Other loans | F601 |
