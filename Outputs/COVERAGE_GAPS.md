# freenic Coverage Gaps

## Known Limitations

### 1. Post-2002 Individual Bank Call Reports (Schedule-Level Detail)

**Gap**: FFIEC 031/041/051 schedule-level detail variables for 2003-present.

**What's missing**: ~4,228 schedule-level detail variables (RC-B securities breakdowns, RC-N delinquency categories, RC-R risk-weighted assets detail, etc.) for 2003-2025.

**Why**: The FFIEC Central Data Repository (CDR) at `cdr.ffiec.gov` blocks programmatic download via ASP.NET ViewState + Cloudflare protection. Multiple download attempts returned HTTP 192 errors.

**Mitigation**: The most-used call report variables ARE available through overlapping sources:

| Source | Variables | Entities | Coverage |
|--------|-----------|----------|----------|
| Luck Database | 245 | 24,716 | 1959Q4-2025Q4 |
| FDIC SDI | 58 | 24,056 | 1984Q1-2025Q4 |
| Chicago Fed Call Reports | 4,473 | 22,185 | 1976Q1-2002Q2 |

The 245 Luck variables + 58 FDIC SDI variables cover the most commonly used call report items (total assets, deposits, loans, capital, income). The gap is specialist research items like securities subcategories and detailed delinquency breakdowns.

**Resolution**: If the FFIEC CDR ever adds a proper REST API, the gap can be filled with script `07_ingest_call_reports.py` adapted for the new format.

### 2. 1905-1958 Historical Gap (Partially Filled)

**Gap**: No systematic bank-level *quarterly* financial data between OCC historical (ends 1904) and Luck Database (begins 1959Q4).

**What's available**:
- OCC Historical: 1867-1904 (national banks only, balance sheet data)
- **Robin Failing Banks Panel: 1863-2024 (annual, 39,299 banks, 156 variables)** — NEW in Session 8
- Luck Database: 1959Q4-2025Q4 (all insured commercial banks)

**Status**: The Robin panel now provides **annual** bank-level data for the full 1905-1958 period, including assets, deposits, loans, equity, capital, and failure indicators for all banks. This fills the gap at annual granularity. Quarterly detail for this period remains unavailable.

**Why quarterly gap remains**: The 1905-1958 period predates computerized quarterly regulatory reporting. Quarterly data exists only in physical archives.

**Mitigation**: For aggregate banking statistics, FRED and Historical Statistics of the United States provide industry totals. Robin panel provides bank-level annual data.

### 3. FR Y-9LP/Y-9SP (Parent-Only Holding Company Reports)

**Gap**: Unconsolidated parent-only BHC financial data not yet ingested.

**What's missing**: FR Y-9LP (Large BHC Parent Only) and Y-9SP (Small BHC Parent Only) quarterly/semiannual data from 1996-present. These provide parent-only financials that complement the consolidated Y-9C data already in `bhcf_filings`.

**Why**: The FFIEC NPW download site (`www.ffiec.gov/npw/FinancialReport/FinancialDataDownload`) was unresponsive during the integration session. The data format is identical to existing BHCF files (caret-delimited TXT with BHCP-prefix variables).

**Resolution**: Retry download when FFIEC NPW becomes available. Script pattern: clone `04_ingest_bhcf_txt.py` with different input directory and target table.

**Value**: Essential for analyzing double leverage (parent debt / subsidiary equity), intercompany capital flows, and holding company liquidity separate from subsidiaries.

### 4. Pillar 3 Bank Coverage

**Gap**: Pillar 3 disclosures cover only 5 G-SIBs for 6 quarters.

**Current**: JPM, BAC, C, WFC, MS with 2-3 quarters each (2024Q1-2025Q3).

**Missing**: GS (Goldman Sachs), BK (BNY Mellon), STT (State Street) — the other US G-SIBs. Also missing: historical quarters before 2024Q1.

**Why**: Only 5 banks' Pillar 3 PDFs were acquired and processed through HDARP.

**Resolution**: Acquire additional Pillar 3 PDFs from bank investor relations pages and process through HDARP pipeline.

### 5. Credit Union Data

**Gap**: No credit union data. freenic covers only FDIC-insured depository institutions and BHCs.

**Why**: Credit unions are regulated by NCUA, not FDIC/OCC/Fed. NCUA publishes quarterly 5300 Call Reports at `https://www.ncua.gov/analysis/credit-union-corporate-call-report-data`.

**Resolution**: Out of scope for current version. Could be added as a separate ingestion pipeline.

## Coverage Matrix

```
Year:  1867  1900  1920  1940  1960  1980  2000  2025
       |     |     |     |     |     |     |     |
OCC    ████████████
                                                     (1867-1904, national banks)
                              GAP: 1905-1958
                                                     (physical archives only)
Luck                                ███████████████████████████
                                                     (1959Q4-2025Q4, 245 vars)
Call                                     ████████████
Reports                                              (1976Q1-2002Q2, 4,473 vars)
BHCF                                        █████████████████
                                                     (1986Q3-2025Q4, 3,208 vars)
FDIC                                      ███████████████████
SDI                                                  (1984Q1-2025Q4, 58 vars)
FDIC                                           ██████████████
SOD                                                  (1994-2025, branch deposits)
Failures                    ██████████████████████████████████
                                                     (1934-2026)
DFAST                                                   ██████
                                                     (2013-2025)
Pillar 3                                                   ██
                                                     (2024Q1-2025Q3)
FDIC                  ██████████████████████████████████████████
History                                              (All dates)
FRED         █████████████████████████████████████████████████
                                                     (1954-2025, macro context)
Robin  ██████████████████████████████████████████████████████████████
Panel                                                (1863-2024, annual, 39K banks)
```

## Data Source URLs

| Source | URL | Status |
|--------|-----|--------|
| FDIC BankFind API | banks.data.fdic.gov/api/ | Active, no auth |
| FFIEC NPW | www.ffiec.gov/npw/ | Intermittently available |
| FFIEC CDR | cdr.ffiec.gov | Blocked (Cloudflare) |
| Chicago Fed | chicagofed.org | Downloaded |
| Luck Database | Academic distribution | Downloaded |
| OCC Historical | Academic distribution | Downloaded |
| Federal Reserve DFAST | federalreserve.gov | Downloaded |
| CRSP-FRB Link | NY Fed | Downloaded |
| MDRM | FFIEC | Downloaded |
| FDIC History API | api.fdic.gov/banks/history | Active, no auth |
| FRED CSV | fred.stlouisfed.org | Active, no auth |
