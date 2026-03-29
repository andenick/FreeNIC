# FFIEC 101 Chunk 3 -- Schedules H, I, J, K

## Schedule H -- Wholesale Exposure: Eligible Margin Loans, Repo-Style Transactions, and OTC Derivatives with Cross-Product Netting (Pages H-1 and H-2)

**Effective Date**: 10/2022 (main table), 03/2016 (memoranda)

### Structure

Schedule H has a dual-column structure with 12 columns split into two groups:

**Exposures with EAD Adjustment** (Columns A-F):
- Column A: Weighted-Average PD (Percentage, rounded to 2 decimal places)
- Column B: Weighted-Average Effective Maturity (Years, rounded to 2 decimal places)
- Column C: EAD (Amount)
- Column D: Weighted-Average LGD (Percentage, rounded to 2 decimal places)
- Column E: Risk-Weighted Assets (Amount) -- not calculated from previous column entries
- Column F: Expected Credit Loss (Amount)

**Exposures Where Collateral Is Reflected in LGD** (Columns G-L):
- Column G: Weighted-Average PD (Percentage)
- Column H: Weighted-Average Maturity (Years)
- Column I: EAD (Amount)
- Column J: Weighted-Average LGD (Percentage)
- Column K: Risk-Weighted Assets (Amount) -- not calculated from previous column entries
- Column L: Expected Credit Loss (Amount)

### PD Ranges (Items 1-14)

1. 0.00 to < 0.03
2. 0.03 to < 0.10
3. 0.10 to < 0.15
4. 0.15 to < 0.25
5. 0.25 to < 0.50
6. 0.50 to < 0.75
7. 0.75 to < 1.35
8. 1.35 to < 2.50
9. 2.50 to < 5.50
10. 5.50 to < 10.00
11. 10.00 to < 100
12. 100.00 (default)
13. Eligible margin loans where a 300% risk weight has been applied (Column C and Column E only)
14. Total (calculated)

### Memoranda

**Exposures subject to a wholesale correlation factor multiplier of 1.25:**
- M.1: Regulated institutions (all 12 columns, MDRM suffix P929)
- M.2: Unregulated institutions (all 12 columns, MDRM suffix P930)

**IMM Margin Period of Risk and Specific Wrong Way Risk:**
- M.3: Exposure amount and risk-weighted assets with 6 columns:
  - Column A: Exposure Amount -- Holding period/margin period of risk set for 20 days (MDRM: AAHM P931)
  - Column B: Risk-Weighted Assets -- Holding period set for 20 days (MDRM: AAHN P931)
  - Column C: Exposure Amount -- Holding period set for at least twice the minimum (due to 3+ disputes) (MDRM: AAHO P931)
  - Column D: Risk-Weighted Assets -- Holding period at least twice minimum (MDRM: AAHP P931)
  - Column E: Exposure Amount -- Exposures with specific wrong-way risk for IMM (MDRM: AAHQ P931)
  - Column F: Risk-Weighted Assets -- Specific wrong-way risk (MDRM: AAHR P931)

### Notes

1. Cells in line 14 are calculated.
2. Report weighted averages rounded to two decimal places.
3. Risk-weighted assets are not calculated from previous column entries.

---

## Schedule I -- Wholesale Exposure: Eligible Margin Loans and Repo-Style Transactions with No Cross-Product Netting (Pages I-1 and I-2)

**Effective Date**: 10/2022 (main table), 03/2016 (memoranda)

### Structure

Schedule I has the same dual-column structure as Schedule H (12 columns: EAD Adjustment side A-F and Collateral Reflected in LGD side G-L).

### PD Ranges (Items 1-14)

Same PD ranges as Schedule H (0.00 to <0.03 through 100.00 default, plus eligible margin loans at 300% risk weight, plus Total).

### Memoranda

**EAD Adjustment Method:**
- M.1: Percent of line 14, column C calculated using:
  - Column A: Collateral Haircut (MDRM: AAIX J038)
  - Column B: Simple VaR (MDRM: AAIX J039)
  - Column C: Internal Models (MDRM: AAIX J040)
  - Note: Report each percentage rounded to one decimal place.

**Exposures subject to a wholesale correlation factor multiplier of 1.25:**
- M.2: Regulated institutions (MDRM suffix P929)
- M.3: Unregulated institutions (MDRM suffix P930)

**IMM Margin Period of Risk and Specific Wrong Way Risk:**
- M.4: Exposure amount and risk-weighted assets (6 columns, MDRM prefix AAIM/AAIN/AAIO/AAIP/AAIQ/AAIR P931)

---

## Schedule J -- Wholesale Exposure: OTC Derivatives with No Cross-Product Netting (Pages J-1 and J-2)

**Effective Date**: 10/2022 (main table), 03/2016 (memoranda)

### Structure

Schedule J has the same dual-column structure as Schedules H and I. Note 4 specifies: "Report exposures for which the bank uses the current exposure methodology to determine EAD and reflects collateral, if any, in LGD."

### PD Ranges (Items 1-13)

1. 0.00 to < 0.03
2. 0.03 to < 0.10
3. 0.10 to < 0.15
4. 0.15 to < 0.25
5. 0.25 to < 0.50
6. 0.50 to < 0.75
7. 0.75 to < 1.35
8. 1.35 to < 2.50
9. 2.50 to < 5.50
10. 5.50 to < 10.00
11. 10.00 to < 100
12. 100.00 (default)
13. Total (calculated)

Note: Schedule J does not include the "300% risk weight" line that Schedules H and I have.

### Memoranda

**EAD Adjustment Method:**
- M.1: Percent of line 13, column C calculated using:
  - Column A: Collateral Haircut (MDRM: AAJX J038)
  - Column B: Internal Models (MDRM: AAJX J040)

**Exposures subject to a wholesale correlation factor multiplier of 1.25:**
- M.2: Regulated institutions (MDRM suffix P929)
- M.3: Unregulated institutions (MDRM suffix P930)

**IMM Margin Period of Risk and Specific Wrong Way Risk:**
- M.4: Exposure amount and risk-weighted assets (MDRM prefix AAJM/AAJN/AAJO/AAJP/AAJQ/AAJR P931)

---

## Schedule K -- Retail Exposure: Residential Mortgage -- Closed-End First Lien Exposures (Pages K-1 and K-2)

**Effective Date**: 10/2022 (main table), 03/2014 (memoranda)

### Structure

Schedule K has 16 columns (A through P):

- Column A: Weighted-Average PD (Percentage, rounded to 2 decimal places)
- Column B: Number of Exposures (Number)
- Column C: Total Balance Sheet Amount (Amount)
- Column D: Total Undrawn Amount (Amount)
- Column E: EAD (Amount)
- Column F: Weighted-Average Age (Months, rounded to 2 decimal places)
- Column G: Weighted-Average LGD (Percentage, rounded to 2 decimal places)
- Column H: Risk-Weighted Assets (Amount) -- not calculated from previous column entries
- Column I: Expected Credit Loss (Amount)
- Column J: LTV Less Than 70% (Amount)
- Column K: LTV At Least 70% but Less Than 80% (Amount)
- Column L: LTV At Least 80% but Less Than 90% (Amount)
- Column M: LTV At Least 90% but Less Than 100% (Amount)
- Column N: LTV Greater than or Equal to 100% (Amount)
- Column O: Weighted-Average Bureau Score (Number, rounded to 1 decimal place, except item 16 rounded to nearest whole number)
- Column P: EAD of Accounts with Updated LTV (Amount)

### LTV Notes

LTV values should be calculated using only first lien exposures. Where LTV information is available for all accounts, the sum of EADs reported in Columns J through N for a given PD range should equal the amount reported in Column E for that same PD range. Otherwise, the sum of EADs reported in Columns J through N for a given PD range will be less than the EAD reported in Column E for that same PD range.

### PD Ranges (Items 1-16)

1. 0.00 to < 0.05
2. 0.05 to < 0.10
3. 0.10 to < 0.15
4. 0.15 to < 0.20
5. 0.20 to < 0.25
6. 0.25 to < 0.35
7. 0.35 to < 0.50
8. 0.50 to < 0.75
9. 0.75 to < 1.35
10. 1.35 to < 2.50
11. 2.50 to < 5.50
12. 5.50 to < 10.00
13. 10.00 to < 20.00
14. 20.00 to < 100
15. 100.00 Default
16. Total (calculated, except for Column O)

### Memoranda

- **M.1**: Risk-weighted assets associated with non-material portfolios not included above (MDRM: AAKX J036)
- **M.2**: Credit scores shown in Column O are from which credit scoring system(s)? (MDRM: AAKX J041) -- text field

### Notes

1. Cells in line 16 are calculated, except for Column O.
2. Report weighted averages in Columns A, F, and G rounded to two decimal places.
3. Risk-weighted assets are not calculated from previous column entries.
4. LTV values should be calculated using only first lien exposures.
5. Report weighted averages in Column O rounded to one decimal place, except in item 16, which should be rounded to the nearest whole number.
