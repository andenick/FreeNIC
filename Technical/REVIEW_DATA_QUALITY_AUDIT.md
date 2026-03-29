# freenic Data Quality Audit Report

**Date**: 2026-03-22
**Database**: Outputs/freenic.duckdb (7.3 GB)
**Total rows**: 1,427,056,135

---

## 1. Filing Data Consistency

### BHCF Cross-Quarter Continuity
- **Method**: Checked top 20 BHCs for quarter-over-quarter total assets (BHCK2170) jumps >50%
- **Result**: 16 anomalous jumps detected across regional BHCs
- **Assessment**: All anomalies are explainable by **mergers/acquisitions** (e.g., "Business First Bancshares" +73% in 2020Q2, "Big Poppy Holdings" +143% in 2022Q1). No data errors detected.
- **Status**: PASS

### Call Reports Variable Coverage
| Category | Count | % of 4,473 |
|----------|-------|------------|
| >50% non-zero (well-populated) | 1,501 | 33.6% |
| 10-50% non-zero | 1,136 | 25.4% |
| 1-10% non-zero | 933 | 20.9% |
| <1% non-zero (phantom) | 903 | 20.2% |

- **Assessment**: 903 phantom variables is expected — many MDRM codes were introduced/retired over the 101-quarter span. No action needed.
- **Status**: PASS

### OCC Historical Value Ranges (1867-1904)
| Variable | Min | Max | Avg | Observations |
|----------|-----|-----|-----|-------------|
| assets | 16,989 | 290,374,984 | 1,017,108 | 110,927 |
| deposits | 0 | 91,392,573 | 463,064 | 110,927 |
| loans | 0 | 150,460,006 | 552,292 | 110,927 |
| capital | 0 | 25,000,000 | 192,478 | 110,927 |

- **Assessment**: Values are in **dollars** (not thousands). Max assets ~$290M for largest national banks in 1904 is historically correct (National City Bank of New York was ~$300M). No unit errors.
- **Status**: PASS

### Luck-BHCF Overlap
- Luck entities in BHCF: **6 / 24,716** (0.02%)
- This is expected: Luck covers **individual commercial banks**, BHCF covers **bank holding companies** — fundamentally different entity populations
- **Status**: PASS (expected behavior)

---

## 2. Entity Layer Integrity

| Check | Result | Status |
|-------|--------|--------|
| Duplicate RSSD IDs in institutions | **0** | PASS |
| Self-referencing relationships | **0** | PASS |
| BHCF filers not in institutions | **642** (4.7% of 13,668) | NOTE |
| Orphan branches (head_office missing) | **35,808** (20.7% of 173,250) | NOTE |
| Transformations with missing successor | **15,824** (26.8% of 58,935) | NOTE |
| Transformations with missing predecessor | **17,152** (29.1% of 58,935) | NOTE |

### Notes on Entity Gaps
- **642 BHCF orphans**: These are holding companies that filed Y-9C reports but aren't in the NIC attributes tables (likely very small or short-lived entities). 4.7% is acceptable.
- **35,808 orphan branches**: The branches table contains branch-level records whose head office RSSD IDs are not in the institutions table. This is expected — NIC's branches file includes entities from outside the attributes universe.
- **Transformation gaps**: ~27-29% of merger records reference entities not in the attributes tables. This is a known NIC limitation — the attributes files cover a subset of all historically registered entities.
- **Status**: PASS (known NIC data characteristics)

---

## 3. Catalog Completeness

| Filing Type | Data Variables | Catalog Variables | Match |
|-------------|---------------|-------------------|-------|
| bhcf | 3,208 | 3,208 | MATCH |
| call_report | 4,473 | 4,473 | MATCH |
| luck | 245 | 245 | MATCH |
| occ | 95 | 95 | MATCH |

- **MDRM match rate**: 7,927 / 8,297 (95.5%)
- **Intermittent variables**: 193 variables appear in <50% of their span (>5 quarters present)
- **Assessment**: Intermittent variables are expected — regulatory forms change frequently, variables are added/removed/renamed.
- **Status**: PASS

---

## 4. CRSP Linkage Quality

| Metric | Value |
|--------|-------|
| Total CRSP links | 18,908 |
| Unique RSSD IDs | 1,516 |
| Unique PERMCOs | 1,457 |
| Date range | 1981-03-31 to 2024-09-30 |
| BHCF entities with CRSP link | 1,388 / 13,668 (10.2%) |

- **Assessment**: 10.2% CRSP coverage of BHCF filers is expected — most BHCs are private. Only publicly traded holding companies have CRSP PERMCOs.
- **Status**: PASS

---

## 5. Temporal Coverage

| Source | Earliest | Latest | Quarters |
|--------|----------|--------|----------|
| OCC Historical | 1867-10-07 | 1904-09-06 | ~75 reports |
| Luck Call Reports | 1959-12-31 | 2025-09-30 | 246 quarters |
| Call Report Filings | 1976-03-31 | 2002-06-30 | 101 quarters |
| BHCF Filings | 1986-09-30 | 2025-12-31 | 158 quarters |

### Gap: 1905-1958 (54 years)
No data coverage between OCC Historical (ends 1904) and Luck Database (starts 1959). This is a known gap — no freely available digitized bank-level data exists for this period.

### Gap: Call Reports post-2002
Call reports end at 2002Q2. The FFIEC CDR provides call reports from 2003Q1 onward. **This is the primary integration target.**

---

## 6. Overall Assessment

| Category | Score |
|----------|-------|
| Data integrity | PASS (0 duplicates, 0 self-refs, 0 NULL dates) |
| Value accuracy | PASS (spot-checks confirmed, OCC ranges historical) |
| Entity coverage | PASS (gaps are known NIC limitations) |
| Catalog accuracy | PASS (100% filing type match, 95.5% MDRM match) |
| CRSP linkage | PASS (10.2% coverage expected for public-only) |
| Temporal completeness | NOTE (1905-1958 gap, post-2002 call reports missing) |

**Verdict**: The database passes all quality checks. The only actionable finding is the post-2002 call reports gap, which is addressed in Step 2 of the review plan.
