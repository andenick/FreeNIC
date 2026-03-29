# FFIEC 031 — Chunk 007: Schedule RC-R — Regulatory Capital

**Pages**: 61-70 of 88 (RC-46 through RC-55)

---

## Schedule RC-R — Regulatory Capital

### Part I. Regulatory Capital Components and Ratios (Pages 61-65, RC-46 through RC-50)

Part I is to be completed on a consolidated basis.

#### Common Equity Tier 1 (CET1) Capital (RCFA)

| Item | Description | Code |
|------|-------------|------|
| 1 | Common stock plus related surplus, net of treasury stock and unearned ESOP shares | P742 |
| 2 | Retained earnings | KW00 |
| 2.a | CECL transition election in effect (0=No, 1=Yes 3-year, 2=Yes 5-year 2020) | RCOA JJ29 |
| 3 | Accumulated other comprehensive income (AOCI) | B530 |
| 3.a | AOCI opt-out election (1=Yes, 0=No; advanced approaches must enter 0) | RCOA P838 |
| 4 | Common equity tier 1 minority interest includable in CET1 | P839 |
| 5 | CET1 capital before adjustments and deductions (sum of items 1 through 4) | P840 |

#### CET1 Adjustments and Deductions (RCFA)

| Item | Description | Code |
|------|-------------|------|
| 6 | LESS: Goodwill net of associated DTLs | P841 |
| 7 | LESS: Intangible assets (other than goodwill and MSAs) net of DTLs | P842 |
| 8 | LESS: DTAs from net operating loss and tax credit carryforwards, net of valuation allowances and DTLs | P843 |
| 9.a | LESS: Net unrealized gains (losses) on AFS debt securities (if AOCI opt-out Yes) | P844 |
| 9.c | LESS: Accumulated net gains (losses) on cash flow hedges | P846 |
| 9.d | LESS: Amounts in AOCI from defined benefit postretirement plans | P847 |
| 9.e | LESS: Net unrealized gains (losses) on HTM securities in AOCI | P848 |
| 9.f | LESS: Accumulated net gain (loss) on cash flow hedges in AOCI related to non-FV items (if AOCI opt-out No) | P849 |
| 10.a | LESS: Unrealized net gain (loss) from changes in FV of liabilities due to own credit risk | Q258 |
| 10.b | LESS: All other deductions from (additions to) CET1 before threshold-based deductions | P850 |

#### Threshold-Based Deductions (Two-Column: Non-Advanced Column A RCFA, Advanced Column B RCFW)

| Item | Description | Col A (RCFA) | Col B (RCFW) |
|------|-------------|-------------|-------------|
| 11 | LESS: Non-significant investments in capital of unconsolidated FIs exceeding 10% threshold | — | P851 |
| 12 | Subtotal (item 5 minus items 6-10.b or 6-11) | P852 | P852 |
| 13.a | LESS: Investments in capital of unconsolidated FIs exceeding 25% of item 12 | LB58 | — |
| 13.b | LESS: Significant investments in capital of unconsolidated FIs in common stock exceeding 10% CET1 threshold | — | P853 |
| 14.a | LESS: MSAs net of DTLs exceeding 25% of item 12 | LB59 | — |
| 14.b | LESS: MSAs net of DTLs exceeding 10% CET1 threshold | — | P854 |
| 15.a | LESS: DTAs from temporary differences exceeding 25% of item 12 | LB60 | — |
| 15.b | LESS: DTAs from temporary differences exceeding 10% CET1 threshold | — | P855 |
| 16 | LESS: Amount of significant investments, MSAs, and DTAs exceeding 15% CET1 threshold | — | P856 |
| 17 | LESS: Deductions applied to CET1 due to insufficient additional tier 1 and tier 2 capital | P857 | P857 |
| 18 | Total adjustments and deductions for CET1 | P858 | P858 |
| 19 | Common equity tier 1 capital (item 12 minus item 18) | P859 | P859 |

Non-advanced: item 18 = sum of items 13.a, 14.a, 15.a, and 17. Advanced: item 18 = sum of items 13.b, 14.b, 15.b, 16, and 17.

#### Additional Tier 1 Capital (RCFA)

| Item | Description | Code |
|------|-------------|------|
| 20 | Additional tier 1 capital instruments plus related surplus | P860 |
| 21 | Non-qualifying capital instruments subject to phase-out | P861 |
| 22 | Tier 1 minority interest not included in CET1 | P862 |
| 23 | Additional tier 1 capital before deductions (sum of 20, 21, 22) | P863 |
| 24 | LESS: Additional tier 1 capital deductions | P864 |
| 25 | Additional tier 1 capital (greater of item 23 minus item 24, or zero) | P865 |

#### Tier 1 Capital and Leverage Ratio (RCFA)

| Item | Description | Code |
|------|-------------|------|
| 26 | Tier 1 capital (item 19 + item 25) | 8274 |
| 27 | Average total consolidated assets | KW03 |
| 28 | LESS: Deductions from CET1 and additional tier 1 capital | P875 |
| 29 | LESS: Other deductions from (additions to) assets for leverage ratio | B596 |
| 30 | Total assets for the leverage ratio (item 27 minus items 28 and 29) | A224 |
| 31 | Leverage ratio (item 26 / item 30) — percentage | 7204 |
| 31.a | CBLR framework election in effect (1=Yes, 0=No) | RCOA LE74 |
| 31.b | SA-CCR opt-in election (1=Yes, blank=No) — non-advanced only | RCOA NC99 |

If CBLR Yes: complete items 32-37 and 38.a-38.c, skip items 39-55.b and Part II.
If CBLR No: skip items 32-38.c, complete items 39-55.b and Part II.

#### CBLR Qualifying Criteria (Items 32-38) (RCFA)

| Item | Description | Code |
|------|-------------|------|
| 32 | Total assets (must be less than $10 billion) | 2170 |
| 33 | Trading assets and trading liabilities (5% limit) | KX77 (amount) / KX78 (%) |
| 34.a | Unused portion of conditionally cancellable commitments | KX79 |
| 34.b | Securities lent and borrowed | KX80 |
| 34.c | Other off-balance sheet exposures | KX81 |
| 34.d | Total off-balance sheet exposures (25% limit) | KX82 (amount) / KX83 (%) |
| 35 | Unconditionally cancellable commitments | S540 |
| 36 | Investments in tier 2 capital of unconsolidated FIs | LB61 |
| 37 | Allocated transfer risk reserve | 3128 |
| 38.a | Allowances for credit losses on PCD assets — Loans and leases HFI | JJ30 |
| 38.b | Allowances for credit losses on PCD assets — HTM debt securities | JJ31 |
| 38.c | Allowances for credit losses on PCD assets — Other financial assets at amortized cost | JJ32 |

#### Tier 2 Capital (Items 39-46) (RCFA, RCFW for advanced)

| Item | Description | RCFA Code | RCFW Code |
|------|-------------|-----------|-----------|
| 39 | Tier 2 capital instruments plus related surplus | P866 | — |
| 40 | Non-qualifying capital instruments subject to phase-out | P867 | — |
| 41 | Total capital minority interest not in tier 1 | P868 | — |
| 42.a | AACL includable in tier 2 capital | 5310 | — |
| 42.b | Eligible credit reserves includable in tier 2 (advanced only) | — | 5310 |
| 44.a | Tier 2 capital before deductions (sum of 39-42.a) | P870 | — |
| 44.b | Tier 2 capital before deductions (advanced: 39-41 plus 42.b) | — | P870 |
| 45 | LESS: Tier 2 capital deductions | P872 | — |
| 46.a | Tier 2 capital (greater of 44.a minus 45, or zero) | 5311 | — |
| 46.b | Tier 2 capital (advanced) | — | 5311 |

#### Total Capital, Risk-Weighted Assets, and Ratios

| Item | Description | RCFA Code | RCFW Code |
|------|-------------|-----------|-----------|
| 47.a | Total capital (sum of items 26 and 46.a) | 3792 | — |
| 47.b | Total capital (advanced) | — | 3792 |
| 48.a | Total risk-weighted assets (from RC-R Part II, item 31) | A223 | — |
| 48.b | Total risk-weighted assets (advanced approaches rule) | — | A223 |

#### Risk-Based Capital Ratios (Percentage, RCFA Column A / RCFW Column B)

| Item | Description | Code |
|------|-------------|------|
| 49 | Common equity tier 1 capital ratio | P793 |
| 50 | Tier 1 capital ratio | 7206 |
| 51 | Total capital ratio | 7205 |

#### Capital Buffer and Supplementary Leverage Ratio

| Item | Description | Prefix | Code |
|------|-------------|--------|------|
| 52.a | Capital conservation buffer | RCFA | H311 |
| 52.b | Total applicable capital buffer (advanced/Category III only) | RCFW | H312 |
| 53 | Eligible retained income | RCFA | H313 |
| 54 | Distributions and discretionary bonus payments during the quarter | RCFA | H314 |
| 55.a | Total leverage exposure (advanced/Category III only) | RCFA | H015 |
| 55.b | Supplementary leverage ratio | RCFA | H036 |

### Part II. Risk-Weighted Assets (Pages 66-70, RC-51 through RC-55)

Institutions that entered "1" for Yes in RC-R Part I item 31.a (CBLR) do not have to complete Part II.

Risk-weight categories span 19 columns: A (Totals from Schedule RC), B (Adjustments), C-J (0%, 2%, 4%, 10%, 20%, 50%, 100%, 150%), K-Q (250%, 300%, 400%, 600%, 625%, 937.5%, 1250%), R-S (Other risk-weighting approaches: Exposure Amount, Risk-Weighted Asset Amount).

#### Balance Sheet Asset Categories (Items 1-8)

| Item | Description | Col A Code | Col B Code |
|------|-------------|-----------|-----------|
| 1 | Cash and balances due from depository institutions | RCFD D957 | RCFD S396 |
| 2.a | Held-to-maturity securities (net of ACL) | RCFD D961 | RCFD S399 |
| 2.b | Available-for-sale debt securities and equity securities | RCFD JA21 | RCFD S402 |
| 3.a | Federal funds sold in domestic offices | RCON D971 | — |
| 3.b | Securities purchased under agreements to resell | RCFD H171 | RCFD H172 |
| 4.a | Loans and leases HFS — Residential mortgage exposures | RCFD S413 | RCFD S414 |
| 4.b | Loans and leases HFS — High volatility CRE exposures | RCFD S419 | RCFD S420 |
| 4.c | Loans and leases HFS — Exposures past due 90+ days or nonaccrual | RCFD S423 | RCFD S424 |
| 4.d | Loans and leases HFS — All other exposures | RCFD S431 | RCFD S432 |
| 5.a | Loans and leases HFI — Residential mortgage exposures | RCFD S439 | RCFD S440 |
| 5.b | Loans and leases HFI — High volatility CRE exposures | RCFD S445 | RCFD S446 |
| 5.c | Loans and leases HFI — Exposures past due 90+ days or nonaccrual | RCFD S449 | RCFD S450 |
| 5.d | Loans and leases HFI — All other exposures | RCFD S457 | RCFD S458 |
| 6 | LESS: Allowance for credit losses on loans and leases | RCFD 3123 | RCFD 3123 |
| 7 | Trading assets | RCFD D976 | RCFD S466 |
| 8 | All other assets | RCFD D981 | RCFD S469 |
| 8.a | Separate account bank-owned life insurance | — | — |
| 8.b | Default fund contributions to central counterparties | — | — |

See table CSV for the full multi-column risk-weight allocation codes (columns C through S).
