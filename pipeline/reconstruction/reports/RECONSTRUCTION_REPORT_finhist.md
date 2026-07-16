# Reconstruction validation report — era `finhist` (HIST)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715  
**Validation key:** `('bank_id', 'year')`  
**Pre-registered gate (SPEC §7 / D2):** matched share (EXACT+ROUNDING+TOLERANCE) >= 99.5000% AND UNEXPLAINED share <= 0.1000% (NOT-DERIVABLE excluded from the denominator).

## Coverage matrix (per scoped variable)

| variable | published | attempted | matched | EXACT | ROUNDING | TOLERANCE | VINTAGE | METHOD-CHOICE | NOT-DERIVABLE | UNEXPLAINED |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assets | 366088 | 365984 | 365984 | 365984 | 0 | 0 | 0 | 0 | 0 | 104 |
| demand_deposits | 110604 | 110604 | 110604 | 110604 | 0 | 0 | 0 | 0 | 0 | 0 |
| deposits | 365654 | 359892 | 359892 | 359892 | 0 | 0 | 0 | 5759 | 0 | 3 |
| equity | 367372 | 365847 | 365847 | 365847 | 0 | 0 | 0 | 1525 | 0 | 0 |
| leverage | 365547 | 365240 | 365240 | 365240 | 0 | 0 | 0 | 0 | 0 | 307 |
| notes_nb | 332095 | 332056 | 332056 | 332056 | 0 | 0 | 0 | 0 | 0 | 39 |
| securities | 96899 | 96899 | 96899 | 96899 | 0 | 0 | 0 | 0 | 0 | 0 |
| surplus | 258235 | 258235 | 258235 | 258235 | 0 | 0 | 0 | 0 | 0 | 0 |
| time_deposits | 110558 | 110558 | 110558 | 110558 | 0 | 0 | 0 | 0 | 0 | 0 |
| undivided_profits | 259388 | 259388 | 259388 | 259388 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL | 2632440 | 2624703 | 2624703 | 2624703 | 0 | 0 | 0 | 7284 | 0 | 453 |

## D2 gate verdict

- Cells (total / derivable / NOT-DERIVABLE): 2632440 / 2632440 / 0
- Matched (EXACT+ROUNDING+TOLERANCE): 2624703 = **99.7061%** of derivable (gate 99.5000%)
- UNEXPLAINED: 453 = **0.0172%** of derivable (floor 0.1000%)
- **VERDICT: PASS**

## Honest derivability boundary

1863-1941 (finhist) is a DERIVATION-LAYER reconstruction from `historical-call.dta` (their OCC OCR) to the published derivation. The OCR itself is NOT-DERIVABLE (physical archives); 1942-1958 is a genuine gap, kept absent, never synthetically filled (SPEC §0).
