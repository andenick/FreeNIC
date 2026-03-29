# FR 2052a Instructions - Chunk 012
## Appendix VI: LCR to FR 2052a Mapping (Pages 1-10 of Enclosure)

---

## Introduction

Staff of the Board of Governors of the Federal Reserve System (Board) has developed this document to assist reporting firms subject to the liquidity coverage ratio rule (LCR Rule[^1]) in mapping the provisions of the LCR Rule to the unique data identifiers reported on FR 2052a. This mapping document is not a part of the LCR Rule nor a component of the FR 2052a report. Firms may use this mapping document solely at their discretion. From time to time, to ensure accuracy, an updated mapping document may be published and reporting firms will be notified of these changes.

### Key

| Symbol | Meaning |
|---|---|
| * | Values relevant to the LCR |
| # | Values not relevant to the LCR |
| NULL | Should not have an associated value |

---

## LCR Calculation[^2]

**LCR = HQLA amount / Total Net Cash Outflows**

### HQLA Amount

HQLA amount = (Level 1 HQLA additive values - Level 1 HQLA subtractive values)
+ .85(Level 2A HQLA additive values - Level 2A HQLA subtractive values)
+ .5(Level 2B HQLA additive values - Level 2B HQLA subtractive values)
- MAX[Unadjusted excess HQLA, Adjusted excess HQLA]

**Unadjusted excess HQLA** = Level 2 cap excess amount + Level 2B cap excess amount

**Level 2 cap excess amount** = MAX[0,
.85(Level 2A HQLA additive values - Level 2A HQLA subtractive values)
+ .5(Level 2B HQLA additive values - Level 2B HQLA subtractive values)
- .6667(Level 1 HQLA additive values - Level 1 HQLA subtractive values)]

**Level 2B cap excess amount** = MAX[0,
.5(Level 2B HQLA additive values - Level 2B HQLA subtractive values)
- Level 2 cap excess amount
- .1765((Level 1 HQLA additive values - Level 1 HQLA subtractive values)
+ .85(Level 2A HQLA additive values - Level 2A HQLA subtractive values))]

### Adjusted HQLA Components

**Adjusted level 1 HQLA additive values**
= Level 1 HQLA additive values + Secured lending unwind maturity amounts
- Secured lending unwind collateral values with Level 1 collateral class
+ Secured funding unwind collateral values with Level 1 collateral class
+ Asset exchange unwind maturity amounts with Level 1 subproduct
- Asset exchange unwind collateral values with Level 1 collateral class

**Adjusted level 2A HQLA additive values**
= Level 2A HQLA additive values
- Secured lending unwind collateral values with Level 2A collateral class
+ Secured funding unwind collateral values with Level 2A collateral class
+ Asset exchange unwind maturity amounts with Level 2A subproduct
- Asset exchange unwind collateral values with Level 2A collateral class

**Adjusted level 2B HQLA additive values**
= Level 2B HQLA additive values
- Secured lending unwind collateral values with Level 2B collateral class
+ Secured funding unwind collateral values with Level 2B collateral class
+ Asset exchange unwind maturity amounts with Level 2B subproduct
- Asset exchange unwind collateral values with Level 2B collateral class

**Adjusted excess HQLA** = Adjusted level 2 cap excess amount + Adjusted level 2B cap excess amount

(Adjusted level 2 and 2B cap excess amounts follow the same formulas as unadjusted but using adjusted values.)

### Total Net Cash Outflows

Total Net Cash Outflows = Outflow Adjustment Percentage * [Outflow values * Respective outflow rates
- MIN[Inflow values * Respective inflow rates, .75(Outflow values * Respective outflow rates)]
+ Maturity mismatch add on]

**Maturity mismatch add on**
= MAX[0, Largest net cumulative maturity outflow amount]
- MAX[0, Net day 30 cumulative maturity outflow amount]

**Largest net cumulative maturity outflow amount** = MAX over m in {1,2,...,30} of:
SUM(n=1 to m) of [(Outflow values corresponding to .32(g),(h)(1),(h)(2),(h)(5),(j),(k), and (l) with maturity bucket of n * Respective outflow rates) - (Inflow values corresponding to .33(c),(d),(e), and (f) with maturity bucket of n * Respective inflow rates)]

**Net day 30 cumulative maturity outflow amount** =
SUM(n=1 to 30) of [(Outflow values corresponding to .32(g),(h)(1),(h)(2),(h)(5),(j),(k), and (l) with maturity bucket of n * Respective outflow rates) - (Inflow values corresponding to .33(c),(d),(e), and (f) with maturity bucket of n * Respective inflow rates)]

---

## Outflow Adjustment Percentage

Banking organizations subject to LCR requirements should determine their category of standards under the LCR rule and apply the appropriate outflow adjustment percentage.

| Organization Type | Outflow Adjustment Percentage |
|---|---|
| Global systemically important BHC or GSIB depository institution | 100 percent |
| Category II Board-regulated institution | 100 percent |
| Category III Board-regulated institution with $75 billion or more in average weighted short-term wholesale funding and any Category III Board-regulated institution that is a consolidated subsidiary of such a Category III Board-regulated institution | 100 percent |
| Category III Board-regulated institution with less than $75 billion in average weighted short-term wholesale funding and any Category III Board-regulated institution that is a consolidated subsidiary of such a Category III Board-regulated institution | 85 percent |
| Category IV Board-regulated institution with $50 billion or more in average weighted short-term wholesale funding | 70 percent |

### Collateral Class Definitions for LCR Mapping

- **HQLA** refers to all asset classes listed in Appendix III with a "-Q" suffix.
- **Non-HQLA** refers to all asset classes listed in Appendix III that are not included in "Other" or HQLA.
- **Other** includes the following collateral classes only: C-1, P-1, P-2, LC-1, LC-2 and Z-1.

---

## HQLA Amount Values

### HQLA Additive Values

#### (1) High-Quality Liquid Assets (Subpart C, S.20-.22)
- Reporting Entity: LCR Firm
- PID: I.A.1, 2, and 3
- Sub-Product: Not Currency and Coin
- Market Value: * (LCR relevant)
- Maturity Bucket: Open for I.A.3, # otherwise
- Collateral Class: HQLA (except A-0-Q for I.A.2)
- Treasury Control: Y

#### (2) Rehypothecatable Collateral (Subpart C, S.20-.22) - Inflows Secured
- Reporting Entity: LCR Firm
- PID: I.S.1, 2, 3, 4, 5, and 6
- Collateral Class: HQLA securities (not A-0-Q)
- Collateral Value: * (LCR relevant)
- Unencumbered: Y
- Treasury Control: Y

#### (3) Rehypothecatable Collateral (Subpart C, S.20-.22) - Supplemental D&C
- Reporting Entity: LCR Firm
- PID: S.DC. 7 and 10
- Sub-Product: Rehypothecatable - Unencumbered
- Treasury Control: Y
- Market Value: * (LCR relevant)
- Collateral Class: HQLA securities (not A-0-Q)

### HQLA Subtractive Values

#### (4) Excluded Sub HQLA (S.22(b)(3) and (4))
- PID: S.L.1; Market Value: *; Collateral Class: HQLA

#### (5) Early Hedge Termination Outflows (S.22(a)(3))
- PID: S.L.3; Market Value: *; Collateral Class: HQLA

#### (6) Excess Collateral (S.22(b)(5))
- PID: S.DC.15; Treasury Control: Y; Market Value: *; Collateral Class: HQLA

### Unwind Transactions

#### (7) Secured Lending Unwind (Subpart C, S.21)
- PID: I.S.1, 2, 3, 5, and 6
- Maturity Amount: * (LCR relevant)
- Maturity Bucket: <= 30 calendar days
- Effective Maturity Bucket: NULL or <= 30 calendar days, but not Open
- Collateral Class: HQLA; Collateral Value: *
- Unencumbered: Y if Effective Maturity Bucket is NULL, otherwise #
- Treasury Control: Y

#### (8) Secured Funding Unwind (Subpart C, S.21)
- PID: O.S.1, 2, 3, 5, 6, 7 and 11
- Sub-Product: For O.S.7, cannot be Unsettled (Regular Way) or Unsettled (Forward), # otherwise
- Maturity Amount: *; Maturity Bucket: <= 30 calendar days
- Collateral Class: HQLA; Collateral Value: *
- Treasury Control: Y

#### (9) Asset Exchange Unwind (Subpart C, S.21)
- PID: I.S.4
- Sub-Product: Level 1 HQLA, Level 2A HQLA, and Level 2B HQLA
- Maturity Amount: *; Maturity Bucket: <= 30 calendar days
- Effective Maturity Bucket: NULL or <= 30 calendar days, not Open
- Collateral Class: HQLA; Collateral Value: *
- Unencumbered: Y if Effective Maturity Bucket is NULL, otherwise #
- Treasury Control: Y

---

## Outflow Values

#### (10) Stable Retail Deposits (S.32(a)(1))
- PID: O.D.1 and 2; Counterparty: Retail or Small Business; Insured: FDIC

#### (11) Other Retail Deposits (S.32(a)(2))
- PID: O.D.1, 2, and 3; Counterparty: Retail or Small Business
- Insured: Not FDIC for PID = 1 and 2, and # for PID = 3

#### (12) Insured Placed Retail Deposits (S.32(a)(3))
- PID: O.D.14; Counterparty: Retail or Small Business; Insured: FDIC

#### (13) Non-Insured Placed Retail Deposits (S.32(a)(4))
- PID: O.D.14; Counterparty: Retail or Small Business; Insured: Not FDIC

#### (14) Other Retail Funding (S.32(a)(5)) - Deposits
- PID: O.D.15; Counterparty: Retail or Small Business

#### (15) Other Retail Funding (S.32(a)(5)) - Other Cash Outflows
- PID: O.O.22; Counterparty: Retail or Small Business

#### (16) Other Retail Funding (S.32(a)(5)) - Secured
- PID: O.S.1, 2, 7 and 11; Counterparty: Retail or Small Business
- Sub-Product: For O.S.7, cannot be Unsettled (Regular Way) or Unsettled (Forward)

#### (17) Other Retail Funding (S.32(a)(5)) - Wholesale
- PID: O.W.18; Counterparty: Retail or Small Business
- Maturity Bucket: <= 30 calendar days

#### (18) Structured Transaction Outflow Amount (S.32(b))
- PID: O.O.21 (adds the incremental amount)
- Maturity Bucket: <= 30 calendar days
- Note: The total amount for 32(b) is the relevant commitment amounts plus the incremental increase from O.O.21

#### (19) Net Derivatives Cash Outflow Amount (S.32(c))
- PID: O.O.20; Maturity Bucket: <= 30 calendar days

---

[^1]: Refer to LCR Rule as defined as specified in section 10(c) of the LRM standards.
[^2]: For the maturity mismatch add-on, please note that Open maturity should still be reported in FR 2052a, and the LCR calculation will convert Open to day 1 pursuant to section 31(a)(4) of the LCR Rule.
