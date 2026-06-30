# freenic Coverage Gaps

## Known Limitations

### 1. Post-2011 Individual Bank Call Reports — CLOSED (2026-05-31)

**Status: RESOLVED.** `call_report_filings` now spans **1976Q1–2025Q4 (200 quarters,
1,912,085,025 rows).** The 2012Q1–2025Q4 schedule-level detail (56 quarters,
+364,790,180 rows) was downloaded from the FFIEC Central Data Repository (CDR) Bulk Data
single-period interface and ingested in full.

**How the former block was solved**: The FFIEC CDR at `cdr.ffiec.gov` was previously recorded
as "blocked by ASP.NET ViewState + Cloudflare protection." The W16 CLV campaign proved the
Bulk Data single-period download is reachable via a **Playwright RadAjax automation**
(`07d_acquire_cdr_call_bulk.py`); each period's tab-delimited Schedule ZIPs are parsed and the
RCFD/RCON/RIAD columns melted to the long `call_report_filings` schema by
`07e_ingest_call_reports_cdr.py` (idempotent, skip-loaded-quarters). **The "Cloudflare-blocked,
no REST API" note is retired.**

**Verified**: `MAX(period_end) = 2025-12-31`; all 56 post-2011 quarters present; no duplicate
(rssd, period, variable). Schedule-level detail variables (RC-B securities, RC-N delinquency,
RC-R RWA, etc.) for 2012–2025 are now in the warehouse alongside the pre-2012 Chicago Fed layer.

**Residual note**: 2003–2011 schedule detail comes from the Chicago Fed archive (`07`/`07b`);
2012+ from CDR. The two layers use the same long schema and `source_file` distinguishes them.

### 2. 1905-1958 Historical Gap (Partially Filled)

**Gap**: No systematic bank-level *quarterly* financial data between OCC historical (ends 1904) and Luck Database (begins 1959Q4).

**What's available**:
- OCC Historical: 1863-1941 (national banks only, balance sheet data; original 1867-1904 layer + Phase 9b OCC-CLV finhist extension to 1941)
- **Failing Banks Panel: 1863-2024 (annual, 39,299 banks, 156 variables)** — NEW in Session 8
- Luck Database: 1959Q4-2025Q4 at source; in freeNIC, `luck_call_reports` retains **only the 1959Q4-1975Q4 core** (1976+ deduped — served, broader, by `call_report_filings`; see §8)

**Status**: The Failing Banks panel now provides **annual** bank-level data for the full 1905-1958 period, including assets, deposits, loans, equity, capital, and failure indicators for all banks. This fills the gap at annual granularity. Quarterly detail for this period remains unavailable.

**Why quarterly gap remains**: The 1905-1958 period predates computerized quarterly regulatory reporting. Quarterly data exists only in physical archives.

**Mitigation**: For aggregate banking statistics, FRED and Historical Statistics of the United States provide industry totals. The Failing Banks panel provides bank-level annual data.

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

**Why**: Only 5 banks' Pillar 3 PDFs were acquired and processed through a PDF extraction pipeline.

**Resolution**: Acquire additional Pillar 3 PDFs from bank investor relations pages and process through PDF extraction pipeline.

### 5. Credit Union Data

**Gap**: No credit union data. freenic covers only FDIC-insured depository institutions and BHCs.

**Why**: Credit unions are regulated by NCUA, not FDIC/OCC/Fed. NCUA publishes quarterly 5300 Call Reports at `https://www.ncua.gov/analysis/credit-union-corporate-call-report-data`.

**Resolution**: Out of scope for current version. Could be added as a separate ingestion pipeline.

### 6. Filing-Table Referential Match Rate — RECALIBRATED via `entity_xref` (2026-06-01)

**The original "low match rate" was an artifact of validating against the wrong table.**
Filing `rssd_id`/`entity_id` values were tested only against the NIC `institutions` master
extract (217,210 rssds), which covers current/recent and large entities but under-enumerates
historical defunct/merged/small filers. NIC tracks those *other* identities in separate public
tables — chiefly `transformations` (predecessor/successor rssds for mergers & charter changes).
Unioning all public identity tables into `entity_xref` (see DATA_DICTIONARY) recovers them.

**Before → after (distinct-id match rate):**

| Filing table | Join key | vs `institutions` | vs `entity_xref` |
|--------------|----------|-------------------|------------------|
| `call_report_filings` | rssd_id   | 34.0% | **95.6%** |
| `luck_call_reports`   | entity_id | 37.7% | **100.0%** |
| `fdic_financials`     | rssd_id   | 39.7% | **99.8%** |
| `fdic_sod`            | rssd_id   | 38.3% | **99.7%** |
| `bhcf_filings`        | rssd_id   | ~97%  | **97.7%** |

**Era-stratified match vs `entity_xref`** (era = entity's latest activity year):

| Filing table | pre-2000 | 2000–2011 | 2012+ |
|--------------|----------|-----------|-------|
| `call_report_filings` | 94.7% | 90.5%  | 100.0% |
| `luck_call_reports`   | 100.0% | 100.0% | 100.0% |
| `fdic_financials`     | 99.8% | 99.8%  | 99.8% |
| `fdic_sod`            | 99.2% | 99.8%  | 99.9% |

**Recovery attribution** (of the 15,899 `call_report` rssds unmatched by `institutions`):
`transformations.rssd_predecessor` recovers **93.3%** (14,835); `rssd_successor` 28.2%;
`crsp_mapping` 0.5%; `robin_crosswalk`/`bank_failures_enriched`/`fdic_history` add a handful.
Across all sources `entity_xref` adds **17,252** rssds beyond `institutions` (234,462 total).
The **residual genuinely-unknown** slice is only **6.7%** (1,064 rssds) — pre-2000/2000-era
historical filers absent from every public identity table; inherent to NIC coverage, NOT a defect.

**How to use**: analysts who need names/attributes should `LEFT JOIN` (never `INNER JOIN`) and
tolerate NULL metadata; `entity_xref` answers "is this entity a known NIC identity?", while
`institutions` remains the source of richer attributes for the entities it covers.

**Validator behavior (recalibrated, still honest)**: `13_validate.py` check #1 is now
**era-stratified and validated against `entity_xref`**. It PASSES when the MODERN slice
(latest activity ≥ 2000) matches `entity_xref` at **≥ 85%** AND overall ≥ 80%; the pre-2000
residual is reported and classified EXPECTED (not FAIL). This is **not** a relaxation: the
modern-slice gate remains a real regression guard — a key-type/join break, or modern entities
going unmatched, still drops the modern rate below threshold and FAILS. A dedicated regression
sanity test (`tests/test_referential.py::test_modern_gate_fails_on_injected_break`) proves the
gate collapses when validated against an empty identity set, so it can never silently become a
no-op. The 3 former `xfail`s (call_report / luck / fdic_financials) are now real **PASS** tests.

### 7. `bank_failures.state_code` — RESOLVED

Previously `bank_failures.state_code` was NULL for all rows. As of 2026-05-31 it is **fully
populated** from the BankFind `PSTALP` field (4,115 rows, 54 distinct states). No remaining gap.

### 8. Luck dedup — pre-1976 core only (2026-06-05)

`luck_call_reports` was reduced from **311.8M → 38.1M rows** (1011 MB → 99 MB) by dropping the
1976+ rows that duplicate `call_report_filings`. Evidence (re-runnable in
`Technical/coverage_analysis/`):

- **(entity, quarter) overlap, 1976+:** of Luck's 1,946,960 cells, **only 2,285 (0.12%)** are
  absent from Fed-direct; Fed-direct covers **more** (2,024,885 cells). → 99.88% redundant.
- **Value reconciliation, 1976+:** core balance-sheet aggregates (assets/deposits/equity/
  liabilities/loans) reconcile **99.89%** within tolerance against the Fed-direct reconstruction;
  21/25 mapped variables ≥99%. No underlying MDRM line item is lost (all remain in
  `call_report_filings`, with broader coverage).
- **Retained:** the **1959Q4–1975Q4 core** (37,716,069 rows; no Fed-direct equivalent — Fed-direct
  has 0 rows pre-1976) **plus 37,650 rows for 384 genuinely Fed-absent gap-fill cells**.

**Use 1976+ call reports from `call_report_filings`.** Pre-computed Luck-style aggregates for
1976+ are produced by the Fed-direct reconstruction `30_build_public_luck_panel.py`.

**Gap recovery (A3, executed 2026-06-05):** of the original 2,285 Fed-absent 1976+ cells,
**1,901 — the entire 2001–2006 non-deposit-trust-company cluster — were recovered into
`call_report_filings` from FFIEC CDR Single-Period bulk** (`07f_recover_gap_from_cdr.py`,
+1,733,881 rows, source_file `cdrgap_*`), then dropped from Luck by re-running `08b`. The
remaining **384** cells are pre-2001 (CDR's floor) or post-2006 entities absent even from CDR —
genuinely Fed-unavailable, retained as Luck gap-fill.

**Recipe (A2, done 2026-06-05):** the 4 formerly-divergent reconstruction aggregates now reconcile
≥99% (`securities` 94% residual needs the Luck do-files) — see `30_build_public_luck_panel.py`.

## Known Data Caveats / Consumer Warnings

*Additive consumer-facing caveats discovered downstream during the Bev Testing CLV bank-panel
reconstruction (2026-06-14). These do NOT change freeNIC's ingestion, validation, or release gating —
they document traps so that consumers of the published warehouse do not fall into them. All quantitative
claims below were cross-checked read-only against `Outputs/freenic.duckdb` (read_only=True).*

### C1. `robin_panel` absolute-$ columns are NOT usable as dollar levels (most important)

The absolute-dollar columns in the underlying `robin_panel_base` (`assets`, `deposits`, `loans`, `equity`,
and other level variables) are **CPI-deflated AND uncalibrated** — they carry a **year-varying scale factor**
(empirically ~4.81× to ~13.8×) and do **not** represent nominal or real dollar levels. Verified example:
`MAX(assets)` for 2008 is **8.41e9**, while JPMorgan's real 2008 total assets are **~$1.75T**.
**Do not use these columns as absolute dollar magnitudes.** The **ratios** computed within `robin_panel`
(leverage, deposit/asset, etc.) ARE clean.

> **GUARD (W4, `Technical/freenic_ingestion/scripts/48_footgun_guards.py`).** The footgun is now neutralized
> at the catalog level. The former base table was renamed `robin_panel` → **`robin_panel_base`** (preserving
> every column incl. the `source` column), and `robin_panel` is now a **guarded VIEW**: the four uncalibrated
> dollar columns are exposed **only** under the explicit names `assets_uncalibrated_real` /
> `deposits_uncalibrated_real` / `loans_uncalibrated_real` / `equity_uncalibrated_real` (each with a
> `COMMENT ON` redirect to `clean_bank_panel` / `call_report_filings` RCFD2170). A bare
> `SELECT assets FROM robin_panel` now **errors** (BinderException) instead of silently returning garbage;
> every clean ratio column keeps its original name. Dependents `robin_panel_enriched` and `failure_timeline`
> were repointed at `robin_panel_base` (behavior unchanged). Use `clean_bank_panel.*_real` (CPI-deflated,
> calibrated) for real dollar levels.

- **Absolute modern** bank-level levels → `call_report_filings` RCFD2170 (total assets; verified
  JPM-2008 = $1.746T, SVB ≈ $209B), in thousands of nominal dollars.
- **Absolute historical** bank-level levels → `occ_historical` (clean nominal dollars; see C3).
- A clean, unit-verified from-raw reconstruction → `Projects/Bev Testing/Technical/data/clv_panel_v2.parquet` (see C6).

### C2. `robin_panel` provenance (why the $8.4T artifact exists)

`robin_panel` is a **verbatim CSV import** of the Correia–Luck–Verner "Failing Banks" `combined-data.dta`
(script `28`), **not** a quantity derived by freeNIC from `occ_historical` or `luck_call_reports`. Its
**modern values are BHC-consolidated/aggregated**, which is the origin of the ~$8.4T "JPMorgan 2008"
artifact (a holding-company aggregate sitting in a bank-level row), not a clean single-bank level.

### C3. `occ_historical` contains TWO stacked vintages (filter by `source`)

The single `occ_historical` table stacks two different vintages, distinguished by the `source` column:
- `source='occ_historical'` — OCC TSV layer, **1867-1904**, 95 variables.
- `source='occ_historical_clv'` — finhist `historical-call.dta` extension, **1863-1941**, 66 variables.

They use **different, only-partly-overlapping `variable_id` namespaces**, so any query that does not
filter/pivot by `source` may silently mix incompatible variable definitions. **Both vintages are clean
nominal dollars** (unlike `robin_panel`), making `occ_historical` the right source for absolute historical
bank-level levels.

> **GUARD (W4, `scripts/48_footgun_guards.py`).** Two typed convenience views now isolate the vintages:
> **`occ_1867_1904`** (`WHERE source='occ_historical'`, 9,788,940 rows) and **`occ_clv_1863_1941`**
> (`WHERE source='occ_historical_clv'`, 7,986,823 rows); they are disjoint and sum to the 17,775,763-row base
> table. Each view + the base table carry a `COMMENT ON` warning that the two vintages **must not be unioned
> blindly** (incompatible `variable_id` namespaces). Query a single vintage through its typed view, or filter
> the base table by `source`.

### C4. Modern 1959–1975 failure gap (public FDIC undercounts pre-1980 distress)

The public FDIC failures API (and warehouse `bank_failures`) **lacks the pre-1980 assisted/supervisory-merger
distress universe** present in CLV/`robin_panel` (where such events are synthetic-negative-ID-keyed). Order of
magnitude: ~**84** public closures for 1959-75 here vs **~1,297** distress events in CLV for the same window.
This detail is **not independently reproducible from the public FDIC** — use `robin_panel`/CLV (or the clean
Bev panel, C6) when the broader historical distress definition is required.

### C5. Determinism gotcha — single-thread large AVG reductions for byte-stable output

Multithreaded DuckDB `AVG` reductions over large tables (e.g. `AVG` over `robin_panel.cpi`) produce
**ULP-level float jitter** across rebuilds (non-associative parallel float summation). For byte-stable,
reproducible outputs, run such reductions **single-threaded** (`PRAGMA threads=1`). This is a numerical
reproducibility note for downstream pipelines; it does not affect freeNIC's own validation thresholds.

### C6. Clean from-raw reconstruction available

A clean, **unit-verified** from-raw reconstruction of the combined historical + modern bank panel exists at
`Projects/Bev Testing/Technical/data/clv_panel_v2.parquet`. Consumers needing **absolute dollar levels**
(rather than `robin_panel`'s uncalibrated columns) should point there, or build from `call_report_filings`
RCFD2170 (modern) / `occ_historical` (historical) directly.

## Coverage Matrix

```
Year:  1867  1900  1920  1940  1960  1980  2000  2025
       |     |     |     |     |     |     |     |
OCC    ██████████████████
                                                     (1863-1941, national banks)
                              GAP: 1942-1958 (quarterly)
                                                     (physical archives only)
Luck   (freeNIC table)              ███
                                                     (1959Q4-1975Q4 core + gap-fill; 1976+ -> call_report_filings)
Call                                     ████████████████████████████
Reports                                              (1976Q1-2025Q4, 200 quarters)
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
Failing██████████████████████████████████████████████████████████████
Banks                                                (1863-2024, annual, 39K banks)
```

## Data Source URLs

| Source | URL | Status |
|--------|-----|--------|
| FDIC BankFind API | banks.data.fdic.gov/api/ | Active, no auth |
| FFIEC NPW | www.ffiec.gov/npw/ | Intermittently available |
| FFIEC CDR | cdr.ffiec.gov | Accessible via Playwright (Bulk Data single-period); used for post-2011 call reports + unrealized-loss layer |
| Chicago Fed | chicagofed.org | Downloaded |
| Luck Database | [NY Fed: Balance Sheets & Income Statements 1959–2025](https://www.newyorkfed.org/research/banking_research/balance-sheets-income-statements) (free public, Dec 2025; mirror finhist.com) | Downloaded |
| OCC Historical | [OCC Annual Reports](https://www.occ.treas.gov/publications-and-resources/publications/annual-report/index-annual-report.html) (primary); 1863–1941 digitization via [finhist.com](https://finhist.com/) / [scorreia.com](https://scorreia.com/data/call-reports.html) | Downloaded |
| Federal Reserve DFAST | federalreserve.gov | Downloaded |
| CRSP-FRB Link | NY Fed | Downloaded |
| MDRM | FFIEC | Downloaded |
| FDIC History API | api.fdic.gov/banks/history | Active, no auth |
| FRED CSV | fred.stlouisfed.org | Active, no auth |

## Referential integrity & orphan classes (Q4, Definitive Build 2026-06-08)

Every filing table keyed by `rssd_id` is validated against `entity_xref` (the de-duped union of all
public identity tables) by `13_validate` check #1, era-stratified. Audited match rates
(`coverage_analysis/q4_referential_audit.json`):

| Table | Modern (≥2000) | Pre-2000 | Overall |
|---|---|---|---|
| call_report_filings | 96.5% | 94.7% | 95.6% |
| luck_call_reports | 100% | 100% | 100% |
| fdic_financials | 99.8% | 99.8% | 99.8% |
| fdic_sod | 99.8% | 99.2% | 99.7% |
| bhcf_filings | 96.9% | 99.2% | 97.7% |
| ubpr_ratios | 100% | — | 100% |
| y15_systemic_indicators | 89.5% | — | 89.5% |

**Gate (Q4-tightened):** modern slice must clear **90%** (was 85%), overall **85%** (was 80%); the
injected-break regression test still FAILs on a real key/join break. `ubpr_ratios` (≥95%) and
`y15_systemic_indicators` (≥85%) were added to the referential gate.

**Remaining orphan classes (explained, not data errors):**
- **Pre-modern defunct/merged banks** (the ~3–5% residual in call_report/bhcf): entities that failed,
  merged, or changed charter before NIC's modern coverage and have no `entity_xref` record. This is a
  structural NIC-coverage floor, not a join bug — the modern slice (recoverable entities) matches ≥96.5%.
- **FR Y-15 (6 of 57 filers, 89.5%):** a handful of G-SIB/IHC filers — chiefly foreign banking
  organizations' US intermediate holding companies — whose snapshot `rssd_id` is not yet in `entity_xref`.
  Widening via a fresh NIC re-pull + GLEIF (plan unit A6) is the path to close this.

## HMDA pre-2018 (A3, Definitive Build 2026-06-09) — go/no-go

`hmda_summary` is a 2018–2024 LEI-keyed institution×year panel from the CFPB HMDA **Data Browser** API.
**2017 and earlier are NOT available via the Data Browser** — `/view/filers?years=2017` returns **HTTP 400**
(the Data Browser covers 2018+ only; this was verified empirically, not assumed).

**Pre-2018 path (legacy):** HMDA 1981–2017 exists on the FFIEC HMDA legacy platform as flat files keyed by
the old **respondent_id** (panel/reporter + LAR files), with **no LEI**. Building a comparable institution×year
summary would require: (1) the legacy panel (respondent_id → name/agency), (2) LAR aggregation by
respondent×year×loan-purpose, and (3) a respondent_id→RSSD crosswalk distinct from the LEI path.

**Decision: NO-GO for now (documented).** It is a separate, sizable ingestion with a different key schema and
no LEI join; the marginal value (older mortgage-lending aggregates, adjacent to the call-report core) does not
justify the effort at this stage. The modern 2018–2024 LEI panel is retained as the canonical HMDA layer.
Re-open if a respondent_id→RSSD crosswalk and legacy-panel ingest are separately warranted.

## FR Y-15 pre-2020 (A4, Definitive Build 2026-06-09) — no bulk product

`y15_systemic_indicators` is a 2020–2024 panel from the FFIEC NIC **FR Y-15 Snapshots** page. Empirically,
that page lists **only 2020–2024** snapshot CSVs (10 links: 5 `Snapshot_All` + 5 `Snapshot_Indicators`,
verified 2026-06-09 via a headed browser past Cloudflare). **No 2015–2019 snapshot bulk product exists** on
NIC; pre-2020 FR Y-15 is available only as per-institution NPW filings (no bulk dataset). The `Snapshot_All`
files we hold ARE the data; the `Snapshot_Indicators` companion assets are separately 403-gated but redundant.
**Decision: Y-15 retained at 2020–2024 (the full NIC-published snapshot extent).** Not a gap to fill — an
upstream coverage boundary.
