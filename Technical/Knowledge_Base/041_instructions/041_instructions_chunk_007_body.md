# FFIEC 041 — Chunk 007 (Pages 61-70)
## Schedule RC-R — Regulatory Capital (Part I and Part II, items 1-8)

---

## Schedule RC-R — Regulatory Capital

### Part I. Regulatory Capital Components and Ratios (Pages 61-64)

Part I is to be completed on a consolidated basis.

#### Common Equity Tier 1 Capital (Page 61)

| Item | Description | RCOA | Notes |
|------|-------------|------|-------|
| 1 | Common stock plus related surplus, net of treasury stock and unearned ESOP shares | P742 | |
| 2 | Retained earnings | KW00 | See footnote 1 |
| 2.a | CECL transition election (0=No; 1=Yes 3-year; 2=Yes 5-year 2020) | JJ29 | |
| 3 | Accumulated other comprehensive income (AOCI) | B530 | |
| 3.a | AOCI opt-out election (1=Yes; 0=No) | P838 | |
| 4 | Common equity tier 1 minority interest includable in CET1 capital | P839 | |
| 5 | CET1 capital before adjustments and deductions (sum of items 1 through 4) | P840 | |

**Footnote 1**: Institutions that have elected to apply the 3-year or the 5-year 2020 CECL transition provision should include the applicable portion of the CECL transitional amount or the modified CECL transitional amount, respectively, in this item.

#### Common Equity Tier 1 Capital: Adjustments and Deductions (Pages 61-62)

| Item | Description | RCOA |
|------|-------------|------|
| 6 | LESS: Goodwill net of associated DTLs | P841 |
| 7 | LESS: Intangible assets (other than goodwill and MSAs), net of associated DTLs | P842 |
| 8 | LESS: DTAs from net operating loss and tax credit carryforwards, net of valuation allowances and net of DTLs | P843 |
| 9.a | LESS: Net unrealized gains (losses) on AFS debt securities (if gain, positive; if loss, negative) | P844 |
| 9.b | Not applicable | — |
| 9.c | LESS: Accumulated net gains (losses) on cash flow hedges | P846 |
| 9.d | LESS: Amounts recorded in AOCI attributed to defined benefit postretirement plans | P847 |
| 9.e | LESS: Net unrealized gains (losses) on HTM securities included in AOCI | P848 |
| 9.f | LESS: Accumulated net gain (loss) on cash flow hedges included in AOCI, net of income taxes, related to hedging of items not recognized at fair value (only for institutions entering "0" for No in item 3.a) | P849 |
| 10.a | LESS: Unrealized net gain (loss) related to changes in fair value of liabilities due to changes in own credit risk | Q258 |
| 10.b | LESS: All other deductions from (additions to) CET1 capital before threshold-based deductions | P850 |
| 11 | Not applicable | — |
| 12 | Subtotal (item 5 minus items 6 through 10.b) | P852 |
| 13 | LESS: Investments in capital of unconsolidated financial institutions, net of DTLs, exceeding 25% of item 12 | LB58 |
| 14 | LESS: MSAs, net of associated DTLs, exceeding 25% of item 12 | LB59 |
| 15 | LESS: DTAs arising from temporary differences that could not be realized through NOL carrybacks, net of valuation allowances and net of DTLs, exceeding 25% of item 12 | LB60 |
| 16 | Not applicable | — |
| 17 | LESS: Deductions applied to CET1 capital due to insufficient amounts of AT1 capital and tier 2 capital to cover deductions | P857 |
| 18 | Total adjustments and deductions for CET1 capital (sum of items 13 through 17) | P858 |
| 19 | Common equity tier 1 capital (item 12 minus item 18) | P859 |

**Footnote**: An institution with a CBLR framework election in effect is neither required to calculate tier 2 capital nor make deductions that would have been taken from tier 2 capital.

#### Additional Tier 1 Capital (Page 62)

| Item | Description | RCOA |
|------|-------------|------|
| 20 | Additional tier 1 capital instruments plus related surplus | P860 |
| 21 | Non-qualifying capital instruments subject to phase-out from AT1 capital | P861 |
| 22 | Tier 1 minority interest not included in CET1 capital | P862 |
| 23 | AT1 capital before deductions (sum of items 20, 21, and 22) | P863 |
| 24 | LESS: AT1 capital deductions | P864 |
| 25 | Additional tier 1 capital (greater of item 23 minus item 24, or zero) | P865 |

#### Tier 1 Capital (Page 62)

| Item | Description | RCOA |
|------|-------------|------|
| 26 | Tier 1 capital (sum of items 19 and 25) | 8274 |

#### Total Assets for the Leverage Ratio (Page 62)

| Item | Description | RCOA | Notes |
|------|-------------|------|-------|
| 27 | Average total consolidated assets | KW03 | See footnote 2 |
| 28 | LESS: Deductions from CET1 capital and AT1 capital (sum of items 6, 7, 8, 10.b, 13-15, 17, and certain elements of item 24) | P875 | |
| 29 | LESS: Other deductions from (additions to) assets for leverage ratio purposes | B596 | |
| 30 | Total assets for the leverage ratio (item 27 minus items 28 and 29) | A224 | |

**Footnote 2**: Institutions with CECL transition provision should include applicable portion of CECL/modified CECL transitional amount in item 27.

#### Leverage Ratio and CBLR Election (Page 63)

| Item | Description | RCOA | Type |
|------|-------------|------|------|
| 31 | Leverage ratio (item 26 / item 30) | 7204 | Percentage (4 decimal places) |
| 31.a | CBLR framework election (1=Yes; 0=No) | LE74 | |
| 31.b | SA-CCR opt-in election (1=Yes; blank=No) | NC99 | Non-advanced approaches only |

**CBLR branching**:
- If item 31.a = 1 (Yes): Complete items 32-37 and if applicable 38.a-38.c; do NOT complete items 39-55.b or Part II.
- If item 31.a = 0 (No): Skip items 32-38.c; complete items 39-55.b as applicable and Part II.

#### Qualifying Criteria for CBLR Institutions (Page 63)

| Item | Description | RCOA (Col A) | RCOA (Col B) | Notes |
|------|-------------|------|------|-------|
| 32 | Total assets (RC item 12); must be < $10 billion | 2170 | — | Amount |
| 33 | Trading assets and trading liabilities (RC items 5+15) | KX77 | KX78 | Amount + % of total assets (5% limit) |
| 34.a | Unused portion of conditionally cancellable commitments | KX79 | — | |
| 34.b | Securities lent and borrowed (RC-L items 6.a+6.b) | KX80 | — | |
| 34.c | Other off-balance sheet exposures | KX81 | — | |
| 34.d | Total off-balance sheet exposures (sum of 34.a-34.c) | KX82 | KX83 | Amount + % of total assets (25% limit) |
| 35 | Unconditionally cancellable commitments | S540 | — | |
| 36 | Investments in tier 2 capital of unconsolidated financial institutions | LB61 | — | |
| 37 | Allocated transfer risk reserve | 3128 | — | |
| 38.a | ACL on purchased credit-deteriorated assets: Loans and leases held for investment | JJ30 | — | |
| 38.b | HTM debt securities | JJ31 | — | |
| 38.c | Other financial assets measured at amortized cost | JJ32 | — | |

#### Tier 2 Capital (Page 64)

For institutions entering "0" for No in item 31.a.

| Item | Description | RCOA | Notes |
|------|-------------|------|-------|
| 39 | Tier 2 capital instruments plus related surplus | P866 | |
| 40 | Non-qualifying capital instruments subject to phase-out from tier 2 capital | P867 | |
| 41 | Total capital minority interest not included in tier 1 capital | P868 | |
| 42 | Adjusted allowances for credit losses (AACL) includable in tier 2 capital | 5310 | See footnote 2 |
| 43 | Not applicable | — | |
| 44 | Tier 2 capital before deductions (sum of items 39 through 42) | P870 | |
| 45 | LESS: Tier 2 capital deductions | P872 | |
| 46 | Tier 2 capital (greater of item 44 minus item 45, or zero) | 5311 | |

**Footnote 2**: Institutions with CECL transition provision should subtract applicable portion of AACL transitional amount from the AACL before determining amount includable in tier 2 capital.

#### Total Capital and Risk-Based Capital Ratios (Page 64)

| Item | Description | RCOA | Type |
|------|-------------|------|------|
| 47 | Total capital (sum of items 26 and 46) | 3792 | Amount |
| 48 | Total risk-weighted assets (from RC-R Part II item 31) | A223 | Amount |
| 49 | Common equity tier 1 capital ratio (item 19 / item 48) | P793 | Percentage |
| 50 | Tier 1 capital ratio (item 26 / item 48) | 7206 | Percentage |
| 51 | Total capital ratio (item 47 / item 48) | 7205 | Percentage |

#### Capital Buffer (Page 64)

| Item | Description | Code | Type |
|------|-------------|------|------|
| 52.a | Capital conservation buffer | RCOA H311 | Percentage |
| 52.b | Total applicable capital buffer (Category III institutions only) | RCOW H312 | Percentage |
| 53 | Eligible retained income | RCOA H313 | Amount |
| 54 | Distributions and discretionary bonus payments during the quarter | RCOA H314 | Amount |

**Footnotes**:
- Item 53: Non-advanced approaches institutions (excl. Category III) complete only if item 52.a <= 2.5000%. Category III institutions complete only if item 52.a <= item 52.b.
- Item 54: Complete only if item 52.a in the previous quarter's Call Report was <= 2.5000% (or <= item 52.b for Category III).

#### Supplementary Leverage Ratio (Page 64)

For Category III institutions only:

| Item | Description | RCOA | Type |
|------|-------------|------|------|
| 55.a | Total leverage exposure | H015 | Amount |
| 55.b | Supplementary leverage ratio | H036 | Percentage |

**Footnote**: Institutions with CECL transition provision should include applicable portion of CECL/modified CECL transitional amount in item 55.a.

---

### Part II. Risk-Weighted Assets (Pages 65-70)

Institutions that entered "1" for Yes in RC-R Part I item 31.a do not have to complete Part II.

Institutions are required to assign a 100% risk weight to all assets not specifically assigned a risk weight under Subpart D of the federal banking agencies' regulatory capital rules and not deducted from tier 1 or tier 2 capital.

**Column structure** (items 1-8): 19 columns total
- Column A: Totals From Schedule RC
- Column B: Adjustments to Totals Reported in Column A
- Columns C-J: Allocation by Risk-Weight Category (0%, 2%, 4%, 10%, 20%, 50%, 100%, 150%)
- Columns K-Q: Additional Risk-Weight Categories (250%, 300%, 400%, 600%, 625%, 937.5%, 1250%)
- Columns R-S: Application of Other Risk-Weighting Approaches (Exposure Amount, Risk-Weighted Asset Amount)

**Important**: All securitization exposures held as on-balance sheet assets are excluded from items 1 through 8 and reported instead in item 9.

#### Balance Sheet Asset Categories (Pages 65-70)

See table CSV file `041_instructions_chunk_007_table_001.csv` for full RCON code matrix.

| Item | Description | Key Notes |
|------|-------------|-----------|
| 1 | Cash and balances due from depository institutions | |
| 2.a | Held-to-maturity securities | Report net of ACL in Col A. Report as negative in Col B those ACL eligible for inclusion in tier 2 capital (excl. ACL on purchased credit-deteriorated assets) |
| 2.b | AFS debt securities and equity securities with readily determinable fair values not held for trading | |
| 3.a | Federal funds sold | |
| 3.b | Securities purchased under agreements to resell | |
| 4.a | Loans and leases held for sale: Residential mortgage exposures | |
| 4.b | Loans and leases held for sale: High volatility commercial real estate exposures | |
| 4.c | Loans and leases held for sale: Exposures past due 90 days or more or on nonaccrual | Exclude residential mortgage, HVCRE, or sovereign exposures |
| 4.d | Loans and leases held for sale: All other exposures | |
| 5.a | Loans and leases held for investment: Residential mortgage exposures | Report as positive in Col B any ACL on purchased credit-deteriorated assets |
| 5.b | Loans and leases held for investment: High volatility commercial real estate exposures | |
| 5.c | Loans and leases held for investment: Exposures past due 90 days or more or on nonaccrual | Exclude residential mortgage, HVCRE, or sovereign exposures |
| 5.d | Loans and leases held for investment: All other exposures | |
| 6 | LESS: Allowance for credit losses on loans and leases | Col A = RCON 3123, Col B = RCON 3123 |
| 7 | Trading assets | |
| 8 | All other assets | Includes premises, fixed assets, OREO, investments in unconsolidated subsidiaries, direct/indirect investments in RE ventures, intangible assets, other assets |
| 8.a | Separate account bank-owned life insurance | |
| 8.b | Default fund contributions to central counterparties | |

**Footnote for item 8**: Institutions with CECL transition provision should report as a positive number in Col B the applicable portion of the DTA transitional amount. Institutions that have reported any assets net of ACL in Col A should report as a negative number in Col B those ACL eligible for inclusion in tier 2 capital (excl. ACL on purchased credit-deteriorated assets).
