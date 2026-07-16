# Reconstruction validation report — era `1959_1975` (MODL)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715  
**Validation key:** `('id_rssd', 'period_end')`  
**Pre-registered gate (SPEC §7 / D2):** matched share (EXACT+ROUNDING+TOLERANCE) >= 99.9000% AND UNEXPLAINED share <= 0.1000% (NOT-DERIVABLE excluded from the denominator).

## Coverage matrix (per scoped variable)

| variable | published | attempted | matched | EXACT | ROUNDING | TOLERANCE | VINTAGE | METHOD-CHOICE | NOT-DERIVABLE | UNEXPLAINED |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assets | 515149 | 515025 | 515025 | 515025 | 0 | 0 | 0 | 0 | 0 | 124 |
| cash | 515162 | 515038 | 515038 | 515038 | 0 | 0 | 0 | 0 | 0 | 124 |
| deposits | 515149 | 515038 | 515025 | 515025 | 0 | 0 | 0 | 0 | 0 | 137 |
| equity | 601702 | 601553 | 601553 | 601553 | 0 | 0 | 0 | 0 | 0 | 149 |
| ln_cc | 311591 | 311511 | 311511 | 311511 | 0 | 0 | 0 | 0 | 0 | 80 |
| ln_ci | 515162 | 515038 | 515038 | 515038 | 0 | 0 | 0 | 0 | 0 | 124 |
| ln_cons | 601715 | 601566 | 601566 | 601566 | 0 | 0 | 0 | 0 | 0 | 149 |
| ln_fi | 601715 | 601566 | 601566 | 601566 | 0 | 0 | 0 | 0 | 0 | 149 |
| ln_oth | 601715 | 601566 | 601566 | 601566 | 0 | 0 | 0 | 0 | 0 | 149 |
| ln_re | 601715 | 601566 | 601566 | 601566 | 0 | 0 | 0 | 0 | 0 | 149 |
| num_employees | 218480 | 218427 | 218427 | 218427 | 0 | 0 | 0 | 0 | 0 | 53 |
| otherbor_liab | 515165 | 515040 | 515040 | 515040 | 0 | 0 | 0 | 0 | 0 | 125 |
| securities | 601712 | 601564 | 601564 | 601564 | 0 | 0 | 0 | 0 | 0 | 148 |
| ytdint_exp_dep | 218480 | 218427 | 218427 | 218427 | 0 | 0 | 0 | 0 | 0 | 53 |
| ytdint_inc_ln | 218480 | 218427 | 218427 | 218427 | 0 | 0 | 0 | 0 | 0 | 53 |
| ytdllprov | 98502 | 98477 | 98477 | 98477 | 0 | 0 | 0 | 0 | 0 | 25 |
| ytdnetinc | 218480 | 218427 | 218427 | 218427 | 0 | 0 | 0 | 0 | 0 | 53 |
| TOTAL | 7470074 | 7468256 | 7468243 | 7468243 | 0 | 0 | 0 | 0 | 0 | 1844 |

## D2 gate verdict

- Cells (total / derivable / NOT-DERIVABLE): 7470087 / 7470087 / 0
- Matched (EXACT+ROUNDING+TOLERANCE): 7468243 = **99.9753%** of derivable (gate 99.9000%)
- UNEXPLAINED: 1844 = **0.0247%** of derivable (floor 0.1000%)
- **VERDICT: PASS**

## Honest derivability boundary

1959Q4-1975Q4 is a DERIVATION-LAYER reconstruction: their digitized `.dta` is the only machine source, and our open code re-runs their documented 04/05/07 method. Because we run their formula on their input, near-perfect agreement is the bar (gate 99.9%). No step fabricates a value (SPEC §0).
