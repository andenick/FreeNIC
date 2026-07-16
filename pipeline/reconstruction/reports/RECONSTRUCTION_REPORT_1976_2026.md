# Reconstruction validation report — era `1976_2026` (MODC)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715  
**Validation key:** `('id_rssd', 'period_end')`  
**Pre-registered gate (SPEC §7 / D2):** matched share (EXACT+ROUNDING+TOLERANCE) >= 99.5000% AND UNEXPLAINED share <= 0.1000% (NOT-DERIVABLE excluded from the denominator).

## Coverage matrix (per scoped variable)

| variable | published | attempted | matched | EXACT | ROUNDING | TOLERANCE | VINTAGE | METHOD-CHOICE | NOT-DERIVABLE | UNEXPLAINED |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assets | 1928837 | 1996742 | 1925861 | 1925638 | 0 | 223 | 0 | 2466 | 0 | 68796 |
| brokered_dep | 1487021 | 1487328 | 1486601 | 1486599 | 0 | 2 | 0 | 589 | 0 | 291 |
| cash | 1928840 | 1991079 | 1922555 | 1922538 | 0 | 17 | 0 | 6364 | 0 | 67989 |
| demand_deposits | 1928839 | 1987464 | 1927790 | 1927777 | 0 | 13 | 0 | 17584 | 0 | 42471 |
| deposits | 1928840 | 1953108 | 1925652 | 1925468 | 0 | 184 | 0 | 5378 | 0 | 22459 |
| equity | 1928837 | 1946803 | 1925544 | 1925515 | 0 | 29 | 0 | 4876 | 0 | 16764 |
| ffpurch | 1037044 | 1046293 | 1036875 | 1036875 | 0 | 0 | 0 | 6181 | 0 | 3302 |
| insured_deposits | 1175181 | 1191641 | 1174604 | 1174548 | 0 | 56 | 0 | 732 | 0 | 16367 |
| ln_cc | 1920181 | 1908407 | 1904310 | 1904248 | 0 | 62 | 0 | 6517 | 0 | 12858 |
| ln_ci | 1926600 | 1981901 | 1925405 | 1925095 | 0 | 310 | 0 | 10288 | 0 | 46589 |
| ln_cons | 1923386 | 1934647 | 1920670 | 1920658 | 0 | 12 | 0 | 7996 | 0 | 8218 |
| ln_fi | 471311 | 895987 | 468268 | 468267 | 0 | 1 | 0 | 339856 | 0 | 88135 |
| ln_re | 1928820 | 1982857 | 1925852 | 1925816 | 0 | 36 | 0 | 27886 | 0 | 31351 |
| ln_tot | 1928840 | 1996630 | 1927568 | 1927418 | 0 | 150 | 0 | 9431 | 0 | 60012 |
| npl_tot | 1411977 | 1379479 | 1275950 | 1275945 | 0 | 5 | 0 | 30555 | 0 | 208412 |
| num_employees | 1637612 | 1637862 | 1637315 | 1637315 | 0 | 0 | 0 | 14 | 0 | 759 |
| otherbor_liab | 1928848 | 1963141 | 1919698 | 1919626 | 0 | 72 | 0 | 20662 | 0 | 23172 |
| securities | 1928840 | 1701167 | 1564006 | 1562559 | 0 | 1447 | 0 | 9855 | 368796 | 16651 |
| time_deposits | 1928838 | 1931700 | 1920548 | 1920418 | 0 | 130 | 18874 | 155 | 0 | 215 |
| ytdint_exp_dep | 1727505 | 1594124 | 1586234 | 1586222 | 0 | 12 | 0 | 3686 | 0 | 138024 |
| ytdint_inc_ln | 1725007 | 1722245 | 1718143 | 1718136 | 0 | 7 | 0 | 2719 | 0 | 7108 |
| ytdllprov | 1727505 | 1730154 | 1726318 | 1726317 | 0 | 1 | 0 | 1899 | 0 | 2206 |
| ytdnetinc | 1726962 | 1729862 | 1724188 | 1724179 | 0 | 9 | 0 | 178 | 0 | 5764 |
| TOTAL | 39185671 | 39690621 | 38469955 | 38467177 | 0 | 2778 | 18874 | 515867 | 368796 | 887913 |

## D2 gate verdict

- Cells (total / derivable / NOT-DERIVABLE): 40261405 / 39892609 / 368796
- Matched (EXACT+ROUNDING+TOLERANCE): 38469955 = **96.4338%** of derivable (gate 99.5000%)
- UNEXPLAINED: 887913 = **2.2258%** of derivable (floor 0.1000%)
- **VERDICT: FAIL**

## Honest derivability boundary

1976-2026 is a TRUE independent re-derivation from Fed-direct raw MDRM (`call_report_filings`, Chicago Fed + FFIEC CDR). The `securities` series carries a documented ~94% public-data ceiling pre-1994 (the raw-MDRM build lives in the un-shipped `3-create-variables.do`); those cells are pre-registered NOT-DERIVABLE, reported honestly and never imputed (SPEC §0, §2.6).

> Every UNEXPLAINED cell above the floor blocks G-MATCH. Investigate each: reclassify with a pre-registered reason key, or report it honestly and hold the claim. No UNEXPLAINED cell is silently absorbed into a documented class (SPEC §7).

## G-MATCH disposition (POST-REMEDIATION, corrected published-data gate) — honest verdict

> **ARTIFACT KIND: PUBLISHED_DATA_GATE (the REAL headline independent gate).** Reference = CLV's PUBLISHED modern panel `sources/call-reports-modern.dta` (their data). Overlap 1976Q1..2024Q3, 23 published-twin variables. This run is AFTER the SPEC §10 form-arm completions (ffpurch B993 / otherbor pre-1994 2850+2910 / ln_cons post-2011 successor) and the symmetric `MC_ZEROFILL_ENCODING` zero-vs-NULL normalization; the 3 interim coverage-fork rows are RETIRED.

**PRE-REGISTERED D2 GATE VERDICT: FAIL** — matched (EXACT+ROUNDING+TOLERANCE) = 96.4338% of derivable (gate 99.5000%); UNEXPLAINED = 2.2258% (floor 0.1000%). Thresholds untouched (non-negotiable).

Class counts (derivable 39,892,609 / NOT-DERIVABLE 368,796): EXACT 38,467,177 · ROUNDING 0 · TOLERANCE 2,778 · VINTAGE 18,874 · METHOD-CHOICE 515,867 (incl. `MC_ZEROFILL_ENCODING`) · NOT-DERIVABLE 368,796 · UNEXPLAINED 887,913.

### SUPPLEMENTARY value-fidelity metrics (NOT the pre-registered gate — clearly labelled)

- **matched-share-where-both-present (ND-inclusive denominator): 99.6247%** (38,469,955 matched of 38,614,887 bank-quarter cells where BOTH panels report a value; this denominator INCLUDES 106,129 NOT-DERIVABLE both-present cells).
- **matched-share-where-both-present-and-derivable (ND-excluded denominator): 99.8992%** (38,469,955 of 38,508,758) — value fidelity where coverage overlaps AND the cell is inside the derivability boundary (V2-MODERN qualification a, 2026-07-15).
- **two-sided value-divergence rate: 0.0972% of derivable** (38,783 cells both-present-and-differing; 0.1004% of both-present).

**Reading:** the pre-registered cell-match gate FAILs honestly — our sparse Fed-direct panel and CLV's dense harmonized panel differ materially in coverage/encoding, and METHOD-CHOICE (incl. the zero-fill encoding fork) stays in the denominator so it cannot raise `match_share`. But **value fidelity where coverage overlaps is very high** and two-sided disagreement is a small fraction of derivable. The claim that the rebuild reproduces CLV's published modern panel *cell-for-cell* is NOT supported and is held; the claim that it reproduces the values *where both panels report* is supported by the supplementary metrics. Warehouse READ-ONLY.
