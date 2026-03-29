# FFIEC 051 — Chunk 005: Schedule RC-R (Regulatory Capital)

## Schedule RC-R — Regulatory Capital

### Part I. Regulatory Capital Components and Ratios

Part I is to be completed on a **consolidated basis**.

---

### Common Equity Tier 1 (CET1) Capital

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 1 | Common stock plus related surplus, net of treasury stock and unearned ESOP shares | P742 |
| 2 | Retained earnings | KW00 |
| 2.a. | CECL transition election (0=No; 1=Yes 3-year; 2=Yes 5-year 2020) | JJ29 |
| 3 | Accumulated other comprehensive income (AOCI) | B530 |
| 3.a. | AOCI opt-out election (1=Yes; 0=No) | P838 |
| 4 | Common equity tier 1 minority interest includable in CET1 capital | P839 |
| 5 | CET1 capital before adjustments and deductions (sum of items 1 through 4) | P840 |

### CET1 Capital: Adjustments and Deductions

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 6 | LESS: Goodwill net of associated deferred tax liabilities (DTLs) | P841 |
| 7 | LESS: Intangible assets (other than goodwill and MSAs), net of associated DTLs | P842 |
| 8 | LESS: DTAs from net operating loss and tax credit carryforwards, net of valuation allowances and DTLs | P843 |
| 9.a. | LESS: Net unrealized gains (losses) on AFS debt securities (if AOCI opt-out=Yes) | P844 |
| 9.c. | LESS: Accumulated net gains (losses) on cash flow hedges (if AOCI opt-out=Yes) | P846 |
| 9.d. | LESS: AOCI amounts from defined benefit postretirement plans (if AOCI opt-out=Yes) | P847 |
| 9.e. | LESS: Net unrealized gains (losses) on HTM securities in AOCI (if AOCI opt-out=Yes) | P848 |
| 9.f. | LESS: Accumulated net gain (loss) on cash flow hedges for non-fair-value items (if AOCI opt-out=No) | P849 |
| 10.a. | LESS: Unrealized net gain (loss) from changes in own credit risk | Q258 |
| 10.b. | LESS: All other deductions from CET1 before threshold-based deductions | P850 |
| 12 | Subtotal (item 5 minus items 6 through 10.b) | P852 |
| 13 | LESS: Investments in unconsolidated financial institutions exceeding 25% of item 12 | LB58 |
| 14 | LESS: MSAs exceeding 25% of item 12 | LB59 |
| 15 | LESS: DTAs from temporary differences exceeding 25% of item 12 | LB60 |
| 17 | LESS: Deductions applied to CET1 due to insufficient AT1 and Tier 2 capital | P857 |
| 18 | Total adjustments and deductions for CET1 (sum of items 13 through 17) | P858 |
| 19 | Common equity tier 1 capital (item 12 minus item 18) | P859 |

### Additional Tier 1 Capital

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 20 | Additional tier 1 capital instruments plus related surplus | P860 |
| 21 | Non-qualifying capital instruments subject to phase-out | P861 |
| 22 | Tier 1 minority interest not included in CET1 capital | P862 |
| 23 | Additional tier 1 capital before deductions (sum of items 20, 21, 22) | P863 |
| 24 | LESS: Additional tier 1 capital deductions | P864 |
| 25 | Additional tier 1 capital (greater of item 23 minus item 24, or zero) | P865 |

### Tier 1 Capital

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 26 | Tier 1 capital (sum of items 19 and 25) | 8274 |

### Total Assets for the Leverage Ratio

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 27 | Average total consolidated assets | KW03 |
| 28 | LESS: Deductions from CET1 and AT1 capital | P875 |
| 29 | LESS: Other deductions from assets for leverage ratio purposes | B596 |
| 30 | Total assets for the leverage ratio (item 27 minus items 28 and 29) | A224 |

### Leverage Ratio

| Item | Description | RCOA Code | Type |
|------|-------------|-----------|------|
| 31 | Tier 1 leverage ratio (item 26 / item 30) | 7204 | Percentage |

### Community Bank Leverage Ratio (CBLR) Framework

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 31.a. | CBLR framework election in effect (1=Yes; 0=No) | LE74 |
| 31.b. | SA-CCR opt-in election (1=Yes; blank=No) | NC99 |

**If CBLR = Yes**: Complete items 32-37 (and 38.a-c if applicable); skip items 39-54 and Part II.
**If CBLR = No**: Skip items 32-38.c; complete items 39-54 and Part II.

### CBLR Qualifying Criteria

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 32 | Total assets (must be less than $10 billion) | 2170 |
| 33 | Trading assets and trading liabilities (5% limit of total assets) | KX77/KX78 |
| 34.a. | Unused portion of conditionally cancellable commitments | KX79 |
| 34.b. | Securities lent and borrowed | KX80 |
| 34.c. | Other off-balance sheet exposures | KX81 |
| 34.d. | Total off-balance sheet exposures (25% limit of total assets) | KX82/KX83 |
| 35 | Unconditionally cancellable commitments | S540 |
| 36 | Investments in tier 2 capital of unconsolidated financial institutions | LB61 |
| 37 | Allocated transfer risk reserve | 3128 |
| 38.a. | Allowance for credit losses on purchased credit-deteriorated assets: Loans and leases | JJ30 |
| 38.b. | Allowance for credit losses on purchased credit-deteriorated assets: HTM debt securities | JJ31 |
| 38.c. | Allowance for credit losses on purchased credit-deteriorated assets: Other financial assets at amortized cost | JJ32 |

### Tier 2 Capital (for non-CBLR institutions)

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 39 | Tier 2 capital instruments plus related surplus | P866 |
| 40 | Non-qualifying capital instruments subject to phase-out | P867 |
| 41 | Total capital minority interest not included in Tier 1 capital | P868 |
| 42 | Adjusted allowances for credit losses (AACL) includable in Tier 2 capital | 5310 |
| 44 | Tier 2 capital before deductions (sum of items 39 through 42) | P870 |
| 45 | LESS: Tier 2 capital deductions | P872 |
| 46 | Tier 2 capital (greater of item 44 minus item 45, or zero) | 5311 |
| 47 | Total capital (sum of items 26 and 46) | 3792 |

### Total Risk-Weighted Assets and Ratios

| Item | Description | RCOA Code | Type |
|------|-------------|-----------|------|
| 48 | Total risk-weighted assets (from Part II, item 31) | A223 | Amount |
| 49 | Common equity tier 1 capital ratio (item 19 / item 48) | P793 | Percentage |
| 50 | Tier 1 capital ratio (item 26 / item 48) | 7206 | Percentage |
| 51 | Total capital ratio (item 47 / item 48) | 7205 | Percentage |

### Capital Buffer

| Item | Description | RCOA Code |
|------|-------------|-----------|
| 52 | Institution-specific capital conservation buffer | H311 |
| 53 | Eligible retained income (if item 52 <= 2.5%) | H313 |
| 54 | Distributions and discretionary bonus payments during the quarter (if prior quarter item 52 <= 2.5%) | H314 |

**Note**: Report each ratio as a percentage, rounded to four decimal places (e.g., 12.3456).

---

### Part II. Risk-Weighted Assets

Institutions that elected CBLR (item 31.a = Yes) do not complete Part II.

Items 1 through 25 (columns A through U, as applicable) are to be completed **semiannually in the June and December reports only**.

#### Risk-Weight Categories (Columns)

| Column | Weight |
|--------|--------|
| A | Totals From Schedule RC |
| B | Adjustments to Totals |
| C | 0% |
| D | 2% |
| E | 4% |
| F | 10% |
| G | 20% |
| H | 50% |
| I | 100% |
| J | 150% |
| K | 250% |
| L | 300% |
| M | 400% |
| N | 600% |
| O | 625% |
| P | 937.5% |
| Q | 1250% |
| R | Exposure Amount (Other Risk-Weighting Approaches) |
| S | Risk-Weighted Asset Amount (Other Risk-Weighting Approaches) |

#### Balance Sheet Asset Categories for Risk-Weighting

| Item | Description |
|------|-------------|
| 1 | Cash and balances due from depository institutions |
| 2.a. | Held-to-maturity securities (net of allowances for credit losses) |
| 2.b. | Available-for-sale debt securities and equity securities with readily determinable fair values not held for trading |
| 3.a. | Federal funds sold |
| 3.b. | Securities purchased under agreements to resell |
| 4.a. | Loans and leases held for sale: Residential mortgage exposures |
| 4.b. | Loans and leases held for sale: High volatility commercial real estate exposures |
| 4.c. | Loans and leases held for sale: Exposures past due 90 days or more or on nonaccrual |
| 4.d. | Loans and leases held for sale: All other exposures |
| 5.a. | Loans and leases held for investment: Residential mortgage exposures |
| 5.b. | Loans and leases held for investment: High volatility commercial real estate exposures |
| 5.c. | Loans and leases held for investment: Exposures past due 90 days or more or on nonaccrual |
| 5.d. | Loans and leases held for investment: All other exposures |
| 6 | LESS: Allowance for credit losses on loans and leases |
| 7 | Trading assets |
| 8 | All other assets |
| 8.a. | Separate account bank-owned life insurance |
| 8.b. | Default fund contributions to central counterparties |

**Key rules**:
- All securitization exposures held as on-balance-sheet assets are excluded from items 1 through 8 and reported in item 9.
- Institutions are required to assign 100% risk weight to all assets not specifically assigned a risk weight under Subpart D and not deducted from tier 1 or tier 2 capital.
- For held-for-investment loans (items 5.a-5.d), report allowances for credit losses on purchased credit-deteriorated assets as a positive number in column B.
