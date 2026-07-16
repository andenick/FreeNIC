# RECONSTRUCTION_SPEC.md — Luck / finhist From-Raw Construction, Citation-Anchored

**Campaign:** FREENIC11_RECONSTRUCTION_20260715 · **Deliverable:** R2 (the spec) · **Date:** 2026-07-15
**Scope (D1 core-first):** the crosswalk's 35 Luck vars + the QJE analysis variables + everything
`30_build_public_luck_panel.py` validates — **62 scoped economic concepts** across three eras, plus the
five panel-construction rule sections (entity spine, failure, dedup, sample filters, deflator).
**Machine-readable twin:** `variable_map.csv` (this directory). **Pre-registered divergence taxonomy:** §7.

> **How to read a variable cell.** Every formula is CITED to one of: a CLV do-file line
> (`04_create-historical-dataset.do L61`), a dictionary row (`variable_map_extract.csv:28`, i.e. the
> `historical_call_data_dictionary.xlsx` `balance sheet`/`income statement` sheet), a freeNIC builder
> (`30_build …AGG_SQL`, `45_build …pivot_modc`), or the reverse-engineering notes
> (`CONSTRUCTION_NOTES.md §3`). Where **only the published paper/appendix would settle a point**, the
> cell is marked **`SOURCE-PENDING(paper)`** for the R2 adversarial checker / R1 corpus agent. Inference
> that is not literally in a cited source is labeled **`INFERRED`** — never presented as verbatim.

**Source-of-truth precedence (plan §R2):** CLV do-files (we hold `00/common/02/04/05/06/07/08`) >
online appendix > paper > our `CONSTRUCTION_NOTES.md` + DPRs > inference (labeled). Do-files are
**READ-ONLY reference**: this spec *describes* their logic and quotes at most short expressions with a
line cite; **no do-file code is copied into public artifacts** (plan D3). All paths absolute.

**Primary sources consulted for this spec (absolute paths):**
- Do-files (extracted read-only to scratchpad from `Inputs/luck_database/qje-repkit.zip`):
  `00_master.do`, `common.do`, `02_import_GFD_CPI.do`, `04_create-historical-dataset.do`,
  `05_create-modern-dataset.do`, `06_create-outflows-receivership-data.do`,
  `07_combine-historical-modern-datasets-panel.do`, `08_data_for_coefplots.do`.
- Dictionary: `Technical/luck_appendix/docs/variable_map_extract.csv`
  (737 rows = the `historical_call_data_dictionary.xlsx` balance-sheet + income sheets, era-segmented).
- Prior work: `Technical/luck_appendix/docs/CONSTRUCTION_NOTES.md` + `docs/dprs/*`.
- Builders: `Technical/freenic_ingestion/scripts/{08_ingest_luck,20_build_crosswalks,30_build_public_luck_panel,45_build_clean_bank_panel}.py`.

---

## 0. The derivability boundary (the honesty contract — enforced per cell)

| Era | Reconstruction meaning | Machine source | Ceiling |
|---|---|---|---|
| **1976–2026** (MODC) | TRUE independent re-derivation from Fed-direct raw MDRM | `call_report_filings` (1.95B rows; Chicago Fed + FFIEC CDR) | `securities` ~94% pre-1994 (public-data ceiling; §5) |
| **1959Q4–1975Q4** (MODL) | DERIVATION-LAYER: their digitized `.dta` (the *only* machine source) → published schema, our open code re-running their documented `04/05/07` method | `luck_call_reports`/`luck_wide` (from the two Jan2026 `.dta`) | near-exact (we run their formula on their input) |
| **1863–1941** (HIST/finhist) | DERIVATION-LAYER: `historical-call.dta` (their OCR) → published derivation | `occ_historical` (`source='occ_historical_clv'`) | OCR itself NOT-DERIVABLE (physical archives) |
| **1942–1958** | GENUINE GAP — kept **absent**, never synthetically filled | — | n/a |

No step ever fabricates a value. Cells outside the boundary are classed **NOT-DERIVABLE** (§7), never
imputed. Four irreducibly non-reproducible items (from `CONSTRUCTION_NOTES.md §4`, verified against the
do-files): (1) raw-microdata→`.dta` import `1/2/3-*.do` (never shipped); (2) OCC microfilm/OCR + QC (only
flag columns ship); (3) pre-1994 `deposits_time` bulk-vintage; (4) manual cause-of-failure labels
(`cause_of_failure_labels_manual_SL.xlsx`).

---

## 1. Construction chain (what the do-files actually do) — the map for the coder

CLV master chain (`00_master.do L55-63`): `01/02/03` (macro: GDP, CPI, yields) → `04` (historical) →
`05` (modern) → `06` (outflows/receivership) → `07` (combine + deflate + ratios) → `08` (analysis panel).
`21–99` are figures/regressions and **do not build the panel**. **NB (G-SPEC):** `07` appends
`call-reports-historical-edited.dta` — the **`06`-produced** run-dummy-augmented file (`06 L156`), NOT
`04`'s direct `call-reports-historical.dta`; `06` also rewrites `call-reports-modern.dta` with the run
dummy (`06 L207`). The reconstruction must inject the `06` run-merge before the `07` append.

```
HIST 1863-1941                         MODERN 1959-2026
  occ_historical (source=              luck .dta 1959-2024 (id_rssd+date, thousands)   Fed-direct raw MDRM
  'occ_historical_clv')                  = sources/call-reports-modern.dta               (call_report_filings)
        │ 04: id-versioning,                    │ 05: FDIC-failure merge, id hygiene,          │ 30_build: era-aware
        │ egen rowtotal era-rebuilds,           │ pseudo-ids, ×1000, liquid=cash+sec+ffpurch    │ cf(code)=COALESCE(RCFD,RCON)
        ▼                                       ▼                                              ▼  → public_luck_panel
   $temp/call-reports-historical.dta      $temp/call-reports-modern.dta               (independent 1976+ re-derivation)
        └──────────────── 07: append (NOT join); deflate ~30 vars by cpi_gfd; build all ratios; outlier clips ┐
                                                     ▼
                                          dataclean/combined-data.dta  → 08 analysis panel
```

**freeNIC parallels already on disk:** `45_build_clean_bank_panel.py` implements the HIST/MODL/MODC
strata union in Python (unit-gated, nominal+real twins base 1990=100). `30_build_public_luck_panel.py`
implements the independent 1976+ Fed-direct re-derivation (25 aggregates, 99.70%). The reconstruction
module **extends these**, it does not restart (§8, D5).

**Unit conventions (critical):** modern `.dta` = **thousands of dollars**; `05 L111-115` multiplies a
named varlist ×1000 to reach dollars. Historical OCC `.dta` = **raw dollars as-is** (`04` does no unit
convert). `07 L26-34` then CPI-deflates ~30 nominal vars **uniformly** (both eras) by `cpi_gfd`.

---

## 2. SCOPED VARIABLES — Part A: Balance-sheet levels (modern + reconstructed)

Notation: **cf(C)** = `COALESCE(MAX RCFD C, MAX RCON C)` (consolidated→domestic fallback for 034/041/051
domestic-only filers; `30_build …def cf`). Era predicates are on `period_end`/`dt`. "Luck name" = the
harmonized `.dta`/`luck_call_reports` column; the same name serves the 1959–75 era (read directly from
the `.dta`) and the 1976+ era (re-derived from Fed-direct via the dictionary recipe).

### 2.1 assets — Total assets
- **Concept:** total assets. Coverage: HIST 1863–1941; MODL 1959–75; MODC 1976+.
- **Source 1976+:** `cf("2170")` — `30_build AGG_SQL:"assets"`; dictionary `variable_map_extract.csv:26`
  (`RCFD 2170, dt≥19591231`). **exact.**
- **Source 1959–75:** `.dta` column `assets` (`luck_wide.assets`; `45_build pivot_modl`). **exact.**
- **Source HIST:** `occ_historical` `variable_id='assets'` (`45_build pivot_hist L156`). **exact.**
- **Splice:** append, disjoint entity ranges (§6). **Deflator:** deflated in `07` varlist (`07 L26`).
- **Units:** modern ×1000 (`05 L111`); HIST raw dollars. **Edge:** README caveat — assets net of
  loan-loss reserves **after 1976 but not before** (`CONSTRUCTION_NOTES §2c`) → VINTAGE-class across the
  1976 boundary, document. Unit gate anchors: JPM 2008Q4 ≈ $1.75T, SVB last ≈ $209B, OCC-1929 ≈ $1.8B
  (`45_build report_gates`).

### 2.2 deposits — Total deposits
- **1976+:** `cf("2200")` (`30_build`; dict `:31` `RCFD2200 dt≥19591231`). **exact.**
- **freeNIC MODC variant (`45_build pivot_modc L221`):** `COALESCE(rcon2200,0)+COALESCE(rcfn2200,0)`
  (domestic + foreign-office) — a **METHOD-CHOICE** vs `cf(2200)` (RCFD2200 already consolidates foreign);
  document which the reconstruction adopts. Recommend `cf("2200")` for Luck parity.
- **1959–75:** `.dta` `deposits`. **HIST:** reconstructed — see §2.14 `total_deposits`. Deflated (`07 L26`).

### 2.3 domestic_dep / foreign_dep
- **domestic_dep:** `MAX(RCON2200)` only (domestic offices) — `30_build AGG_SQL`; crosswalk `RCON2200 exact`.
- **foreign_dep:** `RCFN2200` (foreign-office deposits) — crosswalk `20_build LUCK` **probable**; used by
  `45_build pivot_modc` deposits sum. Coverage 1976+ only (RCFN filed by big-bank 031 filers).

### 2.4 demand_deposits — Total demand deposits
- `cf("2210")` (`30_build`; dict `:27` `RCFD2210 dt≥19591231`). **exact.** 1959–75 `.dta` `demand_deposits`
  / modern `.dta` `deposits_demand` (05 keep-list name). **HIST (G-SPEC correction):** demand_deposits is a **raw OCC line
item** (`occ_historical variable_id='demand_deposits'`, pivoted `45_build pivot_hist L160`), NOT a
reconstruction — `04 L100-106` *consume* it (with time_deposits) to override the `deposits` **total** for
1915-28 (see §2.14). Do not class HIST demand_deposits as reconstructed_agg.

### 2.5 time_deposits (a.k.a. deposits_time) — **ERA-SPLIT, key edge case**
- **1976+ recipe (`30_build AGG_SQL`):**
  `CASE WHEN period_end < 1984-01-01 THEN cf("2514") ELSE cf("2604")+cf("6648") END`.
- **Dictionary (verbatim, `variable_map_extract.csv:28-30`):**
  `RCON2514` for `19610331 ≤ dt < 19840331`; `RCON 2604+6648` for `19840331 ≤ dt < 20100331`;
  `RCON J473+J474+6648` for `dt ≥ 20100331`. **Reconstruction MUST add the post-2010 J473/J474 arm** —
  `30_build` currently stops at `2604+6648`; that is a **known under-recipe for 2010+** (flag for B-phase).
- **Confidence:** crosswalk labels `time_deposits` **probable**. **1959–75:** `.dta` `time_deposits`.
- **Edge / NOT-DERIVABLE:** pre-1994 distributed `deposits_time` diverges from any public
  `RCON2604+6648` build (RCON6648 only filed from 1984) — FFIEC **bulk-vintage** difference, not a recipe
  error (`CONSTRUCTION_NOTES §4.3`). Class **VINTAGE/NOT-DERIVABLE** pre-1994.

### 2.6 securities — Total securities — **ERA-SPLIT, the public-data ceiling**
- **Dictionary chain (verbatim, `variable_map_extract.csv:3-6`):**
  `RCON 0400+0600+0900+0950` for `19591231 ≤ dt < 19690630`;
  `RCFD 0400+0600+0900+0950` for `19690630 ≤ dt < 19940331`;
  `RCFD0390` alt for `19830930 ≤ dt < 19940331` ("0390 = 0400+0600+0900+0950", used when components null);
  `RCFD 1754+1773` (HTM amort cost + AFS fair value) for `dt ≥ 19940331`.
- **1976+ recipe (`30_build AGG_SQL`):** `CASE WHEN period_end<1994-01-01 THEN cf("0390") ELSE cf("1754")+cf("1773") END`.
- **Confidence:** crosswalk **probable**. **1959–75:** `.dta` `securities`. **HIST:** `occ_historical`
  `variable_id='securities'` (a distinct OCC line item; also `securities_other`, `securities_usgov`).
- **Published Table C.1 (arXiv 2506.06082 p.112, authoritative) era boundaries:** `RCON 0400+0600+0900+0950`
  **1959-06-10→1976-03-31**; `RCON0390` **1976-03-31→1993-12-31**; `RCON 1754+1773` **1994-03-31+**. These
  differ from the dictionary boundaries quoted above (0400-sum to 1994, 0390 "alt from 1983"); the published
  table is cleaner. `30_build`'s `cf("0390") for <1994` MATCHES the published table across its 1976+ scope
  (0390 is valid 1976→1994), so this is a documentation sharpen, **not a code defect**.
- **Ceiling (documented, not a defect — `30_build` header, `CONSTRUCTION_NOTES §5`):** overall ~94% vs
  Luck for 1976+; **post-1994 = 99.96%** (1754+1773 optimal, 5 variants tested); residual is entirely
  **pre-1994 = 86.81%**, concentrated in FFIEC-010/011 era. Upstream raw-MDRM build lives in the
  un-shipped `3-create-variables.do`; distributed `.dta` ships it pre-built → class **NOT-DERIVABLE**
  pre-1994, **TOLERANCE/EXACT** post-1994.

### 2.7 cash — Cash and balances due
- **Dictionary (`variable_map_extract.csv:1-2`):** `RCFD0010` for `19591231 ≤ dt < 19840331`;
  `RCFD 0081+0071` for `dt ≥ 19840331`. **`30_build` uses only `cf("0010")`** → a **known under-recipe
  post-1984** (add `0081+0071` arm). Crosswalk `RCFD0010 exact`. 1959–75 `.dta` `cash`.

### 2.8 loans: ln_tot / ln_tot_gross and subcomponents
- **ln_tot (Total loans, net of unearned income):** dict `:9` `RCFD2122 dt≥19760331`; `30_build`
  `cf("2122")`. Pre-1976 the net concept uses `RCFD1400` (gross) — see ln_tot_gross. **exact** 1976+.
  `45_build pivot_modc L222` `cf("2122")` for `loans`. Crosswalk maps `ln_tot→RCFD1400 exact` (the older
  single-code mapping; the era-correct net series is 2122 for 1976+ per dict `:7-9`).
- **ln_tot_gross:** dict `:7-8` `RCFD1400` (`19591231 ≤ dt < 19760331`) then `RCFD 2122+2123` (`dt≥19760331`).
- **ln_re (real estate):** `cf("1410")` (`30_build`; dict `:70` `RCFD1410 dt≥19591231`). **exact.**
- **ln_ci (C&I) — ERA-SPLIT:** dict `:89-91` `RCFD1600` (`19591231≤dt<19840331`) then `RCFD1766`
  (`dt≥19840331`), fallback `RCFD 1763+1764` when 1766 null. `30_build` `cf("1766")`; **add the pre-1984
  `1600` arm** for MODL/early-MODC. Crosswalk `RCFD1766 exact`.
- **ln_cons (consumer):** `cf("1975")` (`30_build`; dict `:92` `RCFD1975 dt≥19591231`). Crosswalk maps
  `ln_cons→RCFDB538 probable` — **METHOD-CHOICE:** dict says 1975, crosswalk says B538; cite both,
  prefer dict `1975`.
- **ln_agr (agricultural):** `cf("1590")` (`30_build`; dict `:100` `RCFD1590 dt≥19591231`). Crosswalk **probable**.
- **ln_cc / ln_oth / ln_fi (modern loan buckets):** modern `.dta` columns used only for `07 L125-127`
  loan-mix ratios (`ln_*_ratio = ln_*/loans`), 1976+ only. **RESOLVED from published Table C.1
  (arXiv 2506.06082 p.112, all RCON):** **ln_cc (Credit Card)** = `RCON2008` (1967-12-31→2000-12-31) →
  `RCON B538` (2001-03-31+); **ln_fi (Financial Loans)** = `RCON1495` (1959-06-10→1983-12-31) →
  `RCON 1505+1510+1517+1756+1757` (1976-03-31→2000-12-31) → `RCON B531+B534+B535` (2001-03-31+).
  **ln_oth (Other)** has **no published Table C.1 row** → stays a `.dta`-column/residual, honest INFERRED.

### 2.9 llres — Allowance for loan and lease losses
- Dict `:10-11` `RCFD3120` (`19591231≤dt<19760331`) then `RCFD3123` (`dt≥19760331`). `30_build`
  `cf("3123")` → **add pre-1976 `3120` arm**. Crosswalk `RCFD3123 exact`.

### 2.10 oreo — Other real estate owned
- `cf("2150")` (`30_build`; dict `:21` `RCFD2150 dt≥19591231`). Crosswalk **exact**. **HIST:** `04 L61`
  `rename oreo_and_mortgages oreo` (`occ_historical` `variable_id='oreo_and_mortgages'`).

### 2.11 equity — Total equity capital
- `cf("3210")` (`30_build`; dict `:69` `RCFD3210 dt≥19591231`). Crosswalk **exact**. `45_build pivot_modc`
  `l27_a_rcon3210`.
- **HIST reconstruction (`04 L84-85`):** `equity = rowtotal(capital, surplus, undivided_profits,
  surplus_and_undivided_profits)`, set missing iff all four missing. `45_build build_panel L267-269`
  replicates with a COALESCE guard (only add `surplus_and_undivided_profits` when both surplus and
  undivided_profits are null — the 1900–1933 equity/deposit COALESCE fix). **METHOD-CHOICE:** CLV's
  `egen rowtotal` sums all four unconditionally; freeNIC's guard avoids double-count in overlap years —
  cite both; the guard is the correct arithmetic where the combined item duplicates the split items.

### 2.12 surplus / undivided_profits / surplus_profit / capital
- **surplus:** dict `:64-65` `RCFD3240` (`19591231≤dt<19900331`) then `RCFD3839` (`dt≥19900331`).
  `30_build` `cf("3839")` → **add pre-1990 `3240` arm**. Crosswalk maps `surplus→RCFD3230 exact` **and**
  `comm_stock→RCFD3230 probable` (collision — 3230 vs 3240/3839; **METHOD-CHOICE**, prefer dict 3240/3839).
- **undivided_profits:** HIST `occ_historical` item; modern via RIAD/RCFD retained-earnings
  (crosswalk `retain_earn→RCFD3632 exact`). Used in `07 L74` `profits_ratio`.
- **surplus_profit (HIST, `04 L87-90`):** `rowtotal(surplus, undivided_profits)`, missing iff both
  missing; **replaced** by `surplus_and_undivided_profits` for `inrange(year,1918,1928)` and
  `inrange(year,1905,1907)` (era-specific line-item pooling). Feeds `surplus_ratio` (§4).
- **capital (HIST):** OCC paid-in capital line item; used for `leverage_capital` (`07 L69`).

### 2.13 interbank (HIST) — **era-pooled, footnote-9 caveat**
- **`04 L68`:** `interbank = rowtotal(due_to_nb, due_to_other_nb, due_to_sb, due_to_tc_and_sb,
  due_to_banks, due_to_banks_and_other_liabs)`.
- **Edge (footnote 9, quoted `04 L63-67`):** 1905–1920 pools unsecured interbank funding **with** other
  liabilities in one line item → interbank over-states / noncore under-reports for those years. Class
  **METHOD-CHOICE** with the caveat documented. 1976+ has no interbank concept (folded into deposits).

### 2.14 total_deposits / deposits (HIST) — **era-by-era reconstruction**
- **`04 L98`:** `total_deposits = rowtotal(us_deposits, usdo_deposits, individual_deposits,
  demand_deposits, time_deposits, deposits)`.
- **`04 L100-106`:** `deposits` overridden = `demand_deposits+time_deposits` for `inrange(year,1915,1928)`
  (set missing if that sum is 0); `deposits = individual_deposits` for `inrange(year,1905,1914)`.
- **freeNIC HIST (`45_build build_panel L274-280, L298-300`):** `total_deposits_hist` = individual (or
  deposits) + us + usdo + all six `due_to_*`; `deposits_clean` = COALESCE(deposits, individual_deposits,
  demand+time+us+usdo). **METHOD-CHOICE** vs CLV's exact override chain — cite both.

### 2.15 liquid (HIST + modern) — **era-overridden**
- **HIST (`04 L72-82`):** `liquid = rowtotal(bills_nb, bills_sb, checks_and_other, currency,
  legal_tender, specie, due_from_nb, due_from_ra, due_from_other_nb, due_from_other_nb_and_sb,
  due_from_sb, bonds_dep, bonds_hand, cash_exchange_and_reserve, cash_and_exchange)`; set missing iff all
  15 missing; then **overridden** for `inrange(year,1905,1935)` to
  `rowtotal(cash_and_exchange, frb_reserve, cash_exchange_and_reserve)`.
- **Modern (`05 L108`):** `liquid = rowtotal(cash, securities, ffpurch)`. **NB the ffpurch sign** — CLV
  includes fed-funds *purchased* (a liability) in the liquid-asset rowtotal as-coded. **RESOLVED (G-SPEC):**
  the *published* modern (1959+) liquid definition (arXiv 2506.06082 figure note **p.81**) = "currency and
  reserves held, balances with other banks, cash items in collection, and security holdings (government +
  private label)" — **fed funds do NOT appear**. `ffpurch` (=`cf(0278)`) is an unremarked do-file inclusion
  beyond the paper's concept; the sign question is moot. **Reproduce `05 L108` verbatim** for cell-match, but
  class **METHOD-CHOICE / documented-quirk** (published concept excludes fed funds). Deflated (`07 L26`).

### 2.16 emergency / bills_payable / rediscounts (HIST wholesale funding)
- **`04 L94-95`:** `emergency = rowtotal(bills_payable, rediscounts)`, missing iff both missing
  ("after 1929 both reported as one; take the sum throughout"). Feeds `emergency_borrowing` (§4).
  bills_payable, rediscounts are OCC line items; deflated (`07 L28`).

### 2.17 bonds_circ / notes_nb (HIST national-bank circulation)
- **bonds_circ (`04 L111-112`):** approximated = `lawful_money` when `bonds_circ` missing & lawful_money
  present; else `securities_usgov`. ("bonds to secure circulation".)
- **notes_nb:** national-bank notes outstanding (OCC item); used in `res_funding` and the HIST
  asset-growth adjustment (`06 L107`). Deflated (`07 L28`).

### 2.18 res_funding (HIST noncore proxy) — **the historical wholesale-funding measure**
- **`04 L116-122`:** `capital_deposits_notes = rowtotal(equity, total_deposits, interbank, notes_nb)`
  (missing iff capital & notes_nb & deposits & interbank all missing); `res_funding = assets −
  capital_deposits_notes`; **floored at 0** (`replace res_funding=0 if res_funding<0`).
- **freeNIC HIST (`45_build build_panel L294`):** `noncore_funding = (assets − total_deposits_hist −
  equity_raw − notes_nb)/assets` — same residual, expressed as a ratio. Feeds `noncore_ratio` (§4).

### 2.19 modern liability/income levels used by CLV analysis (1976+ / 1959–75 `.dta`)
- **otherbor_liab (a.k.a. othbor_liab):** other borrowed money; modern noncore input
  (`07 L91-92`). `45_build pivot_modc L223` `cf("3190")`. Deflated (`07 L27`).
- **subdebt:** `cf("3200")` (`30_build`; crosswalk `RCFD3200 exact`).
- **liab_tot:** `cf("2948")` (`30_build`; crosswalk `RCFD2948 exact`).
- **ffsold / ffpurch — DEFINITIONAL, PURE fed funds:** `30_build` `cf("0276")` / `cf("0278")`
  (dict `:16` `ffsold=RCFD0276, 19880331≤dt<19970331`; `ffpurch=RCFD0278`). **These are the PURE
  series** — the crosswalk's `ffsold→RCFD1350 / ffpurch→RCFD2800` are Luck's **COMBINED** `ffrepo_ass`
  / `ffrepo_liab` (fed funds + repos, dict `:14` `RCFD1350 19651231≤dt<20020331`). **METHOD-CHOICE**
  resolved in `30_build` A2 (item 4): use 0276/0278 for the pure Luck `ffsold`/`ffpurch`; 1350/2800 →
  rename `ffrepo_ass`/`ffrepo_liab`. Post-2002 pure arm = `RCONB987` (dict `:17`).
- **brokered_dep:** `RCON2365` (dict `:94` `dt≥19830930`; crosswalk CDR `RCON2365 exact`). 1976+.
- **insured_deposits:** dict `:95-96` `RCON2702` (`19830630≤dt<20060630`, Q2-only pre-1991) then
  `RCON F049+F045` (`dt≥20060630`). Edge: reported **Q2 only 1983–1990**, quarterly from 1991.

---

## 3. SCOPED VARIABLES — Part B: Income-statement levels (YTD)

All income items are **YTD** (year-to-date, reset each Q1). CLV analysis restricts income ratios to **Q4**
(`07 L120-122` sets income_ratio/prov_ratio/int_inc_ratio/int_exp_ratio missing when `quarter_number!=4`).
Annual builders (MODL/MODC, `45_build`) take the Dec/Q4 observation (`pivot_modl`/`pivot_modc QUALIFY`).

| Luck name | Concept | 1976+ recipe & cite | 1969–75 legacy | Confidence |
|---|---|---|---|---|
| **ytdnetinc** | Net income | `riad("4340")` (`30_build`; dict `:306`) | `IADX5106` 1960–68 (dict `:305`) | exact |
| **ytdint_inc** | Total interest income | `riad("4107")` (`30_build`; crosswalk `RIAD4107 exact`) | — | exact |
| **ytdint_exp** | Total interest expense | `riad("4073")` (`30_build`; crosswalk `RIAD4073 exact`) | — | exact |
| **ytdint_inc_ln** | Interest income on loans | dict `:229-230` `IADX5006` (1960–68) → `RIAD4010` (`dt≥19691231`) | IADX5006 | exact |
| **ytdint_exp_dep** | Interest expense on deposits | dict `:259-262` `IADX5032`→`RIAD4170`→(alt `4174+4176+4172`)→(2017+ `4508+0093+HK03+HK04+4172`) | IADX5032 | exact (era-chained) |
| **ytdllprov** | Loan-loss provision | `riad("4230")` (`30_build`; dict `:270` `RIAD4230 dt≥19691231`) | — | exact |
| **npl_tot** | Non-performing loans total | `cf("1403")+cf("1407")` (`30_build`; dict `:93` `RCFD 1403+1407 dt≥19821231`) | none (1982+ only) | exact from 1982 |
| **num_employees** | Full-time employees | `riad("4150")` — **RESOLVED** published Table C.1 (arXiv 2506.06082 p.112, "Number of Full-Time Employees") | — | cited |

**Deflator:** the dollar income items (ytdnetinc, ytdllprov, ytdint_exp_dep, ytdint_inc_ln) are in the
`07 L26-31` deflate varlist; npl_tot too. **ytdint_inc/ytdint_exp** (aggregate) are used by `30_build`
but not by CLV's ratio set — scoped for the Fed-direct panel parity, not the analysis panel.

---

## 4. SCOPED VARIABLES — Part C: Derived ratios (all from `07`, on the combined + deflated panel)

Ratios are built in `07_combine-historical-modern-datasets-panel.do` **after** CPI deflation, on the
appended HIST+MODERN panel. Every ratio below is EXACT-derivable once the input levels match. Outlier
handling (`07 L134-147`): income_ratio & nim clipped to [−0.5, 0.5]; int_exp_ratio & int_inc_ratio
clipped to [0, 1]; and a validity filter sets `{leverage, surplus_profit, liquid_ratio, oreo_ratio,
deposit_ratio, noncore_ratio, time_ratio, profits_ratio, profit_shortfall, demand_ratio}` **missing if >1
or <0**. Reproduce these clips verbatim (they are part of the published values).

| Ratio | Formula (verbatim locus) | Notes / era |
|---|---|---|
| **leverage** | `equity/assets` (`07 L66`) | book equity; modern≠hist interpretation (loss provisioning) — README/`07 L65` |
| **leverage_capital** | `capital/assets` (`07 L68`) | HIST paid-in capital |
| **surplus_ratio** | `surplus_profit/equity` (`07 L71`) | HIST solvency proxy (`common.do` `$solvency_hist`) |
| **equity_shortfall** | `surplus_ratio<=0.25` (`07 L73`) | dummy |
| **profits_ratio** | `undivided_profits/equity` (`07 L74`) | |
| **profit_shortfall** | `profits_ratio<0.01` (`07 L75`) | NB/GD solvency add (`common.do`) |
| **oreo_ratio** | `oreo/(loans+oreo)` (`07 L79`) | npl proxy (HIST) |
| **loan_ratio** | `loans/assets` (`07 L82`) | |
| **deposit_ratio** | `deposits/assets` (`07 L83`); **deposit_ratio_alt** `total_deposits/assets` (`07 L84`) | |
| **noncore_ratio** | `res_funding/assets` (`07 L88`); **overridden** for `year>1941` to `noncore_funding/assets` where `noncore_funding=rowtotal(deposits_time, otherbor_liab)` (`07 L91-92`) | THE headline funding regressor; hist vs modern definitions differ by construction — document |
| **emergency_borrowing** | `emergency/assets` (`07 L96`), **set missing for `inrange(year,1905,1928)`** (`07 L97`) | wholesale funding, NB & GD only |
| **interbank_ratio** | `interbank/assets` (`07 L100`) | |
| **liquid_ratio** | `liquid/assets` (`07 L62`), `liquid` set missing if 0 (`07 L61`) | |
| **time_ratio** | `time_deposits/assets` (`07 L102`), missing if time_deposits=0; `= deposits_time/assets` for `year>1945` (`07 L104-105`) | era-split |
| **demand_ratio** | `demand_deposits/assets` (`07 L107`), missing if 0 | |
| **income_ratio** | `ytdnetinc/assets` (`07 L113`), Q4 only, clip [−0.5,0.5] | modern solvency (`$solvency_mod`) |
| **npl_ratio** | `npl_tot/loans` (`07 L114`) | 1982+ |
| **prov_ratio** | `ytdllprov/loans` (`07 L115`), Q4 only | |
| **int_exp_ratio** | `ytdint_exp_dep/assets` (`07 L116`), Q4 only, clip [0,1] | |
| **int_inc_ratio** | `ytdint_inc_ln/assets` (`07 L117`), Q4 only, clip [0,1] | |
| **nim** | `(ytdint_inc_ln − ytdint_exp_dep)/assets` (`07 L118`), clip [−0.5,0.5] | net interest margin |
| **loan-mix ratios** | `ln_{cons,cc,ci,oth,fi,re}/loans` (`07 L125-127`) | modern only |
| **funding ratios** | `{deposits_time, deposits_demand, otherbor_liab, brokered_dep, insured_deposits}/assets` (`07 L130-132`) | modern only |
| **size** | `log(assets)` (`07 L47`); **log_age** `log(age)` (`07 L44`); **size_cat** `xtile(assets,4) by(year)` (`07 L49`) | on deflated assets |
| **crisisBVX** | 1 for year∈{1873,1884,1890,1893,1907,1930,1984,1990,2007} (`07 L52-55`) | BVX crisis dummy |
| **asset_growth (event-study)** | `log(assets)` levels differenced over event time in `08`; freeNIC `asset_growth_dlog3` = Δlog(assets_real) t vs t−3 + qcut(5) (`45_build add_growth`) | METHOD-CHOICE: `08` uses `reghdfe` event-time dummies, freeNIC uses a 3-yr dlog — document |

---

## 5. The 1976+ Fed-direct re-derivation (independent tier) — full recipe reference

`30_build_public_luck_panel.py` builds one row per `rssd_id × period_end`, 25 aggregates, single
conditional-aggregation scan of `call_report_filings`, era-aware. Verified `d1b_reconcile.json`: **24/25
vars ≥99%, overall 99.70%**; assets 99.875% over 1,487,666 bank-quarters, 0 sign flips vs FDIC-SDI. The
`AGG_SQL` dict (§2 cites individual cells) is the canonical recipe. **Known recipe gaps to close in the
B-phase (from the dictionary rows above, not yet in `30_build`):** time_deposits post-2010 J473/J474 arm;
cash post-1984 `0081+0071`; ln_ci pre-1984 `1600`; llres pre-1976 `3120`; surplus pre-1990 `3240`. Each
is a documented VINTAGE/recipe extension, not a fabrication. `securities` ~94% is the immovable ceiling
(§2.6). **Materialization status:** `public_luck_panel.parquet` **not currently on disk** — Batch-1 must
re-run `30_build` (the recipe was validated via `coverage_analysis/d1_reconcile.*` + `d1b_reconcile.*`).

---

## 6. PANEL-CONSTRUCTION RULES (the hard part — entity spine, failure, dedup, filters)

### 6.1 Entity spine — how IDs are formed and linked across eras

**Three era-specific rules; the eras are APPENDED, not joined — no entity persists across the
1942–1958 gap.** (`07 L11-12` `use historical; append using modern`.)

**HIST spine (OCC charter, receiver-restart versioning) — `04 L10-20`:**
- Base id = OCC `bank_id` (5-digit charter-derived). `04 L14-18` mints `version = sum(end_date !=
  end_date[_n-1])` over `(bank_id, year)` and `id = 10*bank_id + version`; `xtset id year`.
- **G-SPEC CORRECTION — the version-id does NOT persist.** `id` is **dropped** (it is not in the `04
  L133-139` keep-list; `bank_id` is kept), and no time-series operator runs between `xtset id` and the drop.
  Downstream, `failed_bank` is `by(bank_id)` (`04 L33`) and `06`/`07` `xtset bank_id quarter`. So the
  **delivered combined panel keys on `bank_id` (charter)** and a bank that re-enters receivership is
  **POOLED under one charter entity, NOT treated as a distinct entity** — the earlier "distinct entity"
  framing describes only the transient `04` xtset, which has no downstream effect. HIST bank_ids are the
  5-digit charter range (`07 L111`).

**MODERN spine (FDIC certificate, post-failure pseudo-ids) — `05 L53-81`:**
- Primary linking key = **`id_fdic_cert`** (FDIC certificate). ID hygiene: zero ids → missing
  (`05 L54-55`); missing `id_fdic_cert` **filled with `−id_rssd`** (negative RSSD surrogate, `05 L58`) so
  the FDIC-failure merge is complete; drop rows still missing id_fdic_cert (`05 L59`).
- **Pseudo-id after failure (`05 L66-67`):** `bank_id = id_fdic_cert*10 + (qofd(fail_day)<=quarter) +
  (qofd(fail_day2)<=quarter)` — quarters *after* a failure event get a bumped id, so an acquirer that
  later fails is a **new entity**; handles the rare multiple-failure case (`05 L64-74`).
- **Range-disjointness (`05 L77`):** `bank_id = bank_id*1e5` so modern ids (≥1e6 scale) **cannot
  collide with 5-digit OCC charter numbers**. This lets HIST and MODERN append into one `bank_id` space
  without linking — disjoint numeric ranges by construction. **G-SPEC notes:** (a) `id_fdic_cert` is the
  FDIC-failure *merge* key (`05 L62`) but is **dropped at `05 L134`** (`isid bank_id quarter` L135) — the
  persistent modern panel key is `bank_id`, not id_fdic_cert. (b) Cert-missing banks carry a **negative**
  surrogate `id_fdic_cert=-id_rssd`, which flows through `L67` to a **negative bank_id** (L66's `abs()` is
  overwritten by L67) — still disjoint from positive HIST charters and positive modern certs.

**freeNIC spine (METHOD-CHOICE vs CLV — document):** `45_build` keys HIST on `bank_id` (occ) and MODERN
on **`rssd_id`** (not FDIC cert): `entity_key = "H"+bank_id` for HIST else `"M"+src_vintage+"_"+rssd_id`
(`45_build add_growth L495-498`). Consequence: **freeNIC entity ids will NOT equal CLV's FDIC-cert
`bank_id`.** For **cell-level validation** align on the natural key **`(id_rssd, period_end)`** (both the
`.dta` and `call_report_filings` carry `id_rssd`/`rssd_id`); for reproducing CLV's **entity-level
regressions** the reconstruction must replicate the FDIC-cert `bank_id` rule (`05 L66-77`) exactly.
**Recommendation:** validation aligns on `(id_rssd, period_end)`; a separate `clv_bank_id` column
implements `05`'s rule for the tri-engine anchor (Part V).

### 6.2 Failure definitions
- **HIST (`04 L22-33`):** failed ⇔ OCC appoints a receiver; `receivership_date = end_date if
  end_has_receivership==1` (`04 L29`). Includes banks that later **exit** receivership and continue, or
  wind down in orderly voluntary liquidation with no creditor loss (paper quote, `04 L25-28`).
  `failed_bank = max(!mi(receivership_date)) by bank_id` (`04 L33`).
- **MODERN (`05 L93`):** `failed_bank = !mi(fail_day)`; `fail_day` from FDIC `public-bank-data.dta`.
  **Exclusions (`05 L18-23`):** drop open-bank-assistance/TARP (`restype1=="OBAM"` — Citi/BofA 2008 are
  **not** failures); drop thrifts (`chclass1∈{SL,SA}`).
- **time_to_fail (both):** `-ceil(days_to_failure/365)` (`04 L47`, `05 L98`) — **negative** sign
  convention (years until failure). Also days/months/quarters variants.

### 6.3 Dedup / consolidation / row-selection
- **HIST drops (`04 L37-54`):** voluntary-liquidation rows (`in_vl==1`, ~28 obs); bank-years with no
  findable call report (`bs_merge==1`); rows filed **after** the receiver was appointed
  (`days_to_failure<=0`).
- **MODERN drops (`05 L59, L104`):** rows missing id_fdic_cert; rows reporting **after** failure
  (`days_to_failure<0`). `isid bank_id quarter` (`05 L135`) — one row per entity-quarter.
- **freeNIC annualization (`45_build`):** MODL/MODC take one row per entity×year via
  `QUALIFY ROW_NUMBER() … ORDER BY (MONTH=12 first), period_end DESC, assets DESC` — **prefer the
  December (Q4) call, else the latest quarter** (`pivot_modl L191-195`, `pivot_modc L208-213`).
- **freeNIC Luck-vs-Fed-direct dedup (`08b_slim_luck.py`, `CONSTRUCTION_NOTES §5`):** KEEP all pre-1976
  Luck rows + 1976+ rows absent from `call_report_filings` (genuine gap-fill, e.g. trust companies); DROP
  1976+ rows present in `call_report_filings` (99.88% redundant, 99.89% value-reconciled). Idempotent.

### 6.4 Sample filters (analysis-panel level, `08`)
- Event-study/analysis (`08 L14-17`): `keep if inrange(time_to_fail,-10,-1)`; for quarterly data keep
  only the **last quarter** in each year before failure. Era conditions (`08 L49-115`): national_bank
  1863–1913, early_fed 1914–1928, great_depression 1929–1934, modern1 1960–81, modern2 1982–2006,
  modern3 2007–2015; JST crisis windows enumerated (`08 L108-114`). These bound the *regression* sample,
  not the constructed panel — the reconstruction builds the full panel; filters are applied downstream.

### 6.5 CPI deflator treatment (the base-year question)
- **CLV (`02_import_GFD_CPI.do` + `07 L25-34`):** deflator = **`cpi_gfd`** from Global Financial Data,
  file `sources/GFD/US_CPI_GFD_202504.csv`, keeping the **Dec-31 annual** value per year
  (`02 L23 keep if month==12 & day==31`). `07 L32-34` applies **`var = var / cpi_gfd`** to the ~30-var
  nominal list (`07 L26-31`). **Base year — RESOLVED (G-SPEC):** the paper states **no base year** — it says
  only "deflated by (the) CPI" (arXiv 2506.06082 figure notes, **p.81** and passim). The deflator is GFD's
  native index divided directly; real *ratios/rankings* are base-invariant, real *levels* index-relative.
  Reproduce the exact `/cpi_gfd` division bit-for-bit (we hold the CSV → `US_CPI_GFD_annual.dta` in `02`); the
  nominal base label is immaterial and simply not published. Macro merges: `jst_cpi_crisis.dta`,
  `US_CPI_GFD_annual.dta`, `GFD_US_Yields.dta` on `year` (`07 L16-18`).
- **freeNIC (`45_build build_cpi`, `CPI_BASE_YEAR=1990`):** re-bases to **1990=100** using
  `cpi_panel.cpi` (1870–2020) with `cpi_gfd`-rescaled tails; emits nominal + real twins. This is a
  **METHOD-CHOICE** re-basing distinct from CLV's raw-`cpi_gfd` division — real *levels* differ by a
  constant scale factor, real *ratios/rankings* are identical. **Document both; reconstruction should
  reproduce CLV's raw `cpi_gfd` division for cell-matching against `combined-data.dta`, and separately
  offer the 1990=100 twin for freeNIC consumers.**

---

## 7. PRE-REGISTERED DIVERGENCE TAXONOMY + THRESHOLDS (registered BEFORE any validation code runs)

Copied from plan §R3 + §D2, verbatim, so the harness cannot be tuned to pass. Every overlapping
published↔built cell is classified into exactly one class.

**Classification is deterministic (G-SPEC, added so a harness coder needs no judgment):** the numeric
classes overlap (a bit-identical cell also satisfies ROUNDING and TOLERANCE; a close cell may also be a
known VINTAGE case), so evaluate in **strict first-match precedence**:
`EXACT → ROUNDING → TOLERANCE → VINTAGE → METHOD-CHOICE → NOT-DERIVABLE → UNEXPLAINED` (first satisfied class
wins). The three "documented" classes (**VINTAGE, METHOD-CHOICE, NOT-DERIVABLE**) may be assigned **only when
a pre-registered reason key exists** for that cell/case — a cell may **not** be relabeled into them post hoc
to make an UNEXPLAINED mismatch disappear. Any non-EXACT/ROUNDING/TOLERANCE cell lacking a registered reason
is **UNEXPLAINED** by definition.

| Class | Definition |
|---|---|
| **EXACT** | Built value == published value (bit-identical after type normalization). |
| **ROUNDING** | `|Δ| ≤ 0.5` units-of-last-digit (display/precision rounding only). |
| **TOLERANCE** | `|relative Δ| ≤ 1e-4` (float/accumulation-order differences). |
| **VINTAGE** | Their Dec-2025 (Jan2026 `.dta`) snapshot vs our quarter refreshes / FFIEC bulk-vintage differences — documented per case (e.g. pre-1994 `deposits_time`, assets-net-of-reserves pre/post-1976). |
| **METHOD-CHOICE** | A documented fork where their code and their docs (or the crosswalk) disagree, or where freeNIC adopts a defensible alternative — **cite both loci** (e.g. equity rowtotal vs COALESCE guard §2.11; ffsold pure vs combined §2.19; spine FDIC-cert vs RSSD §6.1; CPI base §6.5). |
| **NOT-DERIVABLE** | Outside the boundary (§0): pre-1994 `securities`/`deposits_time` raw build, OCC OCR, manual failure labels. Reported honestly, never imputed. |
| **UNEXPLAINED** | Anything that survives none of the above — **counts against the gate.** |

**Match gates (plan §B2/§D2 defaults):**
- **1976+ era (independent re-derivation):** `EXACT+ROUNDING+TOLERANCE` **≥ 99.5%** on scoped vars, with
  **UNEXPLAINED > 0.1% blocks**.
- **1959–1975 (derivation layer, their formula on their input):** **≥ 99.9%** (near-perfect is the bar).
- **1863–1941 finhist (derivation layer):** **≥ 99.5%**.
- Every **UNEXPLAINED** cell above the 0.1% floor blocks G-MATCH → investigate → reclassify or report
  honestly and hold the claim.

---

## 8. D5 RECOMMENDATION — finhist table shape

**Recommendation: EXTEND `clean_bank_panel`'s strata machinery; do NOT build a parallel
`finhist_equivalent_panel` table.** Reasoning from what the code shows: `45_build_clean_bank_panel.py`
already materializes the finhist era (HIST, 1863–1941) and the Luck era (MODL 1959–75 + MODC 1976+) as
`era_group × src_vintage` strata **unioned by name into one row-per-(entity,year) table**, with the exact
machinery this campaign needs — the CPI nominal/real twin, the `unit_basis` tag, the 1942–1958 gap-honesty
assertion, and the disjoint HIST/MODERN entity-key scheme. The finhist-equivalent panel **is** the HIST
stratum; the Luck-equivalent panel **is** MODL+MODC. A parallel table would duplicate the `pivot_hist`
long→wide, the CPI block, and the union logic, and would drift from the unit gate. The reconstruction
should therefore add the CLV-**derived** aggregates that `45_build` does not yet carry (interbank,
res_funding/noncore_funding, emergency, surplus_profit, total_deposits, and the §4 ratios) as **additional
columns on the same (era_group, entity, year) spine** — a "derived layer" over the existing strata — and
keep `30_build`'s independent 1976+ Fed-direct panel as the *validation counterpart* for the MODC cells.
One table, extended, with a `src_vintage`/`era_group` discriminator and a `reconstruction_tier`
provenance column (`independent` | `derivation-layer` | `not-derivable`). This matches the plan's stated
preference ("prefer extending clean_bank_panel's machinery over parallel tables where schemas coincide",
§B3) and the D5 default.

---

## 9. Scope ledger (honest scoped/total)

- **Scoped economic concepts: 62** — Part A balance-sheet levels (26: assets, deposits, domestic_dep,
  foreign_dep, demand_deposits, time_deposits, securities, cash, ln_tot, ln_tot_gross, ln_re, ln_ci,
  ln_cons, ln_agr, loan-mix subcomponents, oreo, llres, equity, surplus, undivided_profits, surplus_profit,
  capital, subdebt, liab_tot, otherbor_liab, ffsold/ffpurch, brokered_dep, insured_deposits), Part A HIST
  reconstructed (10: interbank, liquid, total_deposits, deposits(hist), emergency, bills_payable,
  rediscounts, bonds_circ, notes_nb, res_funding), Part B income (8), Part C ratios + derived (18).
- **Panel-construction rule sections: 5** (entity spine, failure, dedup, sample filters, CPI deflator).
- **Total harmonized dictionary universe: 227** (158 balance-sheet + 69 income) — the un-scoped remainder
  is the **v1.2 expansion** (plan D1). This spec reports scoped **62 / 227** honestly.
- **Citation coverage (see `variable_map.csv`):** the vast majority of scoped formulas are cited to a
  do-file line or a dictionary row. **All 4 `SOURCE-PENDING(paper)` cells are now RESOLVED (G-SPEC
  2026-07-15, from the newly-landed arXiv 2506.06082 appendix; see `SPEC_CHECK_20260715.md`):** CPI base =
  not published (reproduce-by-division, p.81); num_employees = `RIAD4150` (Table C.1 p.112); ln_cc/ln_fi =
  cited to Table C.1 p.112 (ln_oth has no published row → stays honest INFERRED); liquid ffpurch = an
  unremarked do-file inclusion beyond the published concept (p.81) → METHOD-CHOICE/quirk. Remaining
  `INFERRED` cells (ln_oth; securities pre-1994; time_deposits pre-1994; npl pre-1982) are labeled in the
  `confidence` column and stay honestly non-derivable.

---

*Authored 2026-07-15 (R2 spec agent, campaign FREENIC11_RECONSTRUCTION_20260715). Do-files are read-only
reference; no CLV code is reproduced here — this spec describes their documented method with per-line
citations so a coder who has never seen the do-files can implement each formula. Machine twin:
`variable_map.csv`. Gate G-SPEC: adversarial checker re-derives 10 sampled vars before any B-phase code.*

---

## 10. AMENDMENT (2026-07-15, MODERN-ERA REMEDIATION) — form-arm completions + encoding normalization

**Scope.** Post-`G-MATCH` remediation of the CORRECTED published-data modern gate (our Fed-direct
`luck_equivalent_1976_2026` vs CLV's PUBLISHED `sources/call-reports-modern.dta`). The real gate FAILed
honestly at **matched 90.9747% / UNEXPLAINED 4.1941%**, with only **0.097%** two-sided value divergence —
i.e. the miss is **coverage/encoding**, not value error. This amendment closes the three named
form-arm coverage gaps the original spec/builder missed (each added ONLY with a dictionary + empirical
citation) and pre-registers a symmetric zero-vs-NULL encoding-normalization class **BEFORE** the
builder/harness changes. **No thresholds change. All arms are coverage EXTENSIONS, never fabrication.**
Primary source for every arm: the dictionary
`Technical/luck_appendix/docs/variable_map_extract.csv` (the
`historical_call_data_dictionary.xlsx` sheets), corroborated by a READ-ONLY warehouse span/identity probe.

### 10.1 ffpurch — post-2002 pure arm (CORRECTS the campaign brief's "RCONB987")

- **Finding:** the dictionary's pure fed-funds *purchased* series is `ffpurch` = **RCFD0278** for
  `19880331 ≤ dt < 19970331` (dict `:34`) → **RCON B993** for `dt ≥ 20020331` (dict `:35`). The
  campaign brief named "RCONB987" for the ffpurch post-2002 arm; **that is `ffsold`, not `ffpurch`**
  (dict `:18` `ffsold = RCON B987, dt ≥ 20020331`; dict `:17` `ffsold = RCFD0276, 1988–1997`). The
  correct ffpurch post-2002 code is **B993** (RCON `:35`; the ffrepo-liability combined twin is RCON B993
  + RCFD B995, dict `:33`). Recorded as a documented correction.
- **Recipe (MODC), era-split:** `ffpurch = era_pick{ [·,1997Q1): cf("0278"); [2002Q1,·): cf("B993") }`.
  The **1997Q1–2001Q4 window has no pure ffpurch arm** (0278 ends 1996Q4; B993 starts 2002Q1) → NULL,
  honest gap (the combined `ffrepo_liab` RCFD2800/RCONB993+B995 covers it but is a DIFFERENT concept).
- **Symmetric completion:** `ffsold = era_pick{ [·,1997Q1): cf("0276"); [2002Q1,·): cf("B987") }` added
  in the same edit (ffsold is a `public_luck_panel` twin; same 1997–2002 gap).
- **Warehouse probe (READ-ONLY):** `cf(B993)` present 2002Q1–2026Q1 (640,670 bank-quarters);
  `cf(B987)` 2002Q1–2026Q1 (640,649). Cited: dict `:34,:35,:17,:18,:33`; SPEC §2.19.

### 10.2 otherbor_liab — pre-1994 predecessor arm (fully determinable, NOT a gap)

- **Finding:** the builder used `cf("3190")` only (RCFD3190 filed 1994Q1+ in the warehouse), leaving
  1976–1993 NULL. The dictionary gives the **full era chain** (dict `:39–44`):
  `2850+2910` for `[19591231,19940331)` → `2332+2333+2910` `[19940331,19970331)` →
  `2332+2333` `[19970331,19970630)` → `2332+A547+A548` `[19970630,20010331)` → `3190` `[20010331,·)`.
  Raw codes: **2850** = "Other Borrowed Money" (`:533`, filed ≤1993) and **2910** = "Mortgage
  Indebtedness and Obligations under Capitalized Leases" (`:534`, filed ≤1996Q4).
- **Recipe adopted (minimal, faithful):** keep `cf("3190")` for `[1994Q1,·)` **unchanged** (currently
  matched; the maturity-component chain reproduces 3190 for only 120,302/128,831 = 93.4% of the
  1994–1996 overlap, so 3190 is the better modern match); **ADD** the pre-1994 arm
  `[·,1994Q1): rowtotal(cf("2850"), cf("2910"))` (`rowtotal` = NaN iff both null, matching CLV `egen`
  semantics — 2850 and 2910 have different filing populations, so a NULL-propagating `+` would erase
  coverage). This extends built coverage to 1976Q1 without disturbing the 1994+ matched cells.
- **Warehouse probe:** `cf(2850)`/`cf(2910)` both present from 1976Q1. Cited: dict `:39–40,:533,:534`;
  SPEC §2.19.

### 10.3 ln_cons — post-2011 successor arm (empirically identity-validated)

- **Finding:** `ln_cons = cf("1975")` (dict `:92`, `RCFD1975 dt≥19591231`, no documented successor) —
  but **RCFD1975/RCON1975 are discontinued after 2011Q4** in the warehouse (both span 1976Q1–2011Q4
  exactly), so CLV's published `ln_cons` post-2011 (their harmonized panel carries values 2012+) uses an
  **undocumented FFIEC RC-C item-6 successor** the dictionary omits. The successor is the four
  consumer-loan sub-items: **B538** (credit cards, `:566`) + **B539** (other revolving) + **K137**
  (automobile loans, 2011+) + **K207** (other consumer, 2011+).
- **Empirical identity validation (READ-ONLY, the citation anchor):** across all **27,408** 2011
  bank-quarters where both are present, `rowtotal(cf B538, cf B539, cf K137, cf K207) == cf(1975)`
  **EXACTLY (27,408 / 27,408; zero within-1% and zero >1% residual)** — a perfect identity that pins the
  successor. B538/B539 are the 2001+ credit-card / other-revolving items; K137/K207 (auto / other
  consumer) supply the item-6 components that were folded into 1975 until its 2011Q4 retirement.
- **Recipe adopted:** `ln_cons = era_pick{ [·,2012Q1): cf("1975"); [2012Q1,·):
  rowtotal(cf B538, cf B539, cf K137, cf K207) }`. The pre-2012 cells are **unchanged** (still `cf 1975`);
  only 2012Q1+ (where 1975 is retired) takes the successor. Cited: dict `:92,:566,:467–468,:566`; the
  2011 identity probe; SPEC §2.8.

### 10.4 Comparison normalization: encoding philosophy (symmetric, pre-registered) — MC_ZEROFILL_ENCODING

**The encoding fork (documented, both-sided).** CLV's harmonized published panel is **dense**: a
balance-sheet/income item a bank did not file is written as an explicit **`0.0`** (zero-fill). Our
Fed-direct re-derivation is **sparse**: a non-filed MDRM item is preserved as **MDRM NULL** (we never
impute a zero the bank did not report). This is a genuine, symmetric construction fork — it appears in
BOTH directions (CLV `0.0` vs our NULL where CLV zero-fills; our `0.0` vs CLV NULL in the rarer reverse).

**Pre-registered rule (VALIDATION ONLY — never touches the built or published data).** In the harness
comparison layer, a cell in which **exactly one side is the float `0.0` and the other side is absent
(NULL/NaN)** is classified **METHOD-CHOICE** under the single bounded registry row **`MC_ZEROFILL_ENCODING`**,
applied to **all variables** and **both sidednesses**, via a registry **predicate** (not a per-variable
period window). The exact predicate:

> `MC_ZEROFILL_ENCODING` matches iff `(published == 0.0 AND built is NULL) OR (built == 0.0 AND published is NULL)`
> — for every scoped variable, in the `1976_2026` era. Bounds: `variable = *` (wildcard), `predicate =
> ZERO_VS_NULL`, `klass = METHOD-CHOICE`, no period window.

**Honesty properties (why this is classification, not score inflation):**
- These cells are **NOT counted as matches** (METHOD-CHOICE ∉ `MATCH_CLASSES`) and are **NOT dropped from
  the derivable denominator** (unlike NOT-DERIVABLE). So `match_share` is **not raised** by this row — it
  only moves a documented encoding fork **out of UNEXPLAINED into a named, bounded class**. The gate
  verdict cannot flip because of it.
- It is **symmetric** (both `pub=0/blt=NULL` and `blt=0/pub=NULL`) and **variable-agnostic** — it cannot
  be tuned to a convenient variable.
- **Precedence:** it is applied **LAST**, after every specific pre-registered reason row (a
  securities-pre-1994 cell that is also 0-vs-NULL stays **NOT-DERIVABLE**, its more-specific documented
  boundary; a two-sided value divergence never matches the predicate and stays whatever the numeric
  classifier said). First-match precedence (SPEC §7) is preserved.

**Registry mechanics.** `divergence_reasons.csv` gains an 8th column `predicate` (blank for the existing
period-window rows; `ZERO_VS_NULL` for `MC_ZEROFILL_ENCODING`). The harness honours `variable = *` as a
wildcard and evaluates predicate rows after all variable-specific rows. Test-covered
(`test_validate_reconstruction.py`: symmetric predicate, wildcard, last-precedence vs NOT-DERIVABLE).

### 10.5 Retirement of the three interim coverage-fork rows

The pre-remediation registry carried three METHOD-CHOICE rows that classified the *published-only*
coverage forks the OLD builder produced: `MC_FFPURCH_PUREARM_MOD`, `MC_OTHERBOR_PRE1994_MOD`,
`MC_LNCONS_POST2011_MOD`. Now that §§10.1–10.3 **actually build** those arms, the omissions no longer
exist: the previously published-only cells become genuine matches (where the bank filed) or fall to
`MC_ZEROFILL_ENCODING` (where CLV zero-filled a non-filer), and any residual two-sided difference is
honestly UNEXPLAINED. The three interim rows are therefore **RETIRED** (removed from the registry) — not
relabelled — because the coverage fork they documented has been closed at the builder, which is the
honest fix. This retirement is recorded here and in `REGISTRY_ADDITIONS_MODERN_REMEDIATION_20260715.md`.

*Amendment authored 2026-07-15 (modern-era remediation agent, campaign FREENIC11_RECONSTRUCTION_20260715).
Every arm cites a dictionary row + a READ-ONLY warehouse probe; the encoding-normalization class is
symmetric, denominator-preserving, and cannot raise `match_share`. Thresholds untouched (non-negotiable).*

### 10.6 ln_re — post-2011 RC-C Part I component-sum successor (B3 agent, 2026-07-15)

- **Finding:** `ln_re = cf("1410")` (dict `:70` `RCFD1410 dt≥19591231`, no documented successor) — but
  the **RCON1410 domestic aggregate is RETIRED after 2011Q4** in the warehouse (span 1976Q1–2011-12-31
  exactly, 0 filers 2012+); RCFD1410 continues only for ~121 large FFIEC-031 consolidated filers. So
  `cf("1410")` collapses for the ~7,400-bank domestic-filer population from 2012Q1 — the same
  retirement pattern as ln_cons/RCFD1975 (§10.3). CLV's published `ln_re` post-2011 uses the FFIEC
  **RC-C Part I real-estate component sum** the dictionary omits.
- **Successor components (all cf(), fork-aware where the form split granularity):**
  construction = `rowtotal(cf F158, cf F159)` else `cf(1415)` (2008Q3+ F-split vs legacy aggregate);
  farmland = `cf(1420)`; 1–4 family = `rowtotal(cf 1797, cf 5367, cf 5368)` (revolving HELOC + first
  liens + junior liens); multifamily = `cf(1460)`; nonfarm-nonres = `rowtotal(cf F160, cf F161)` else
  `cf(1480)`. Sum via `rowtotal` (NaN iff all arms NaN).
- **Empirical identity validation (READ-ONLY probes, the citation anchors):** (1) overlap window
  2007Q1–2011Q4: component sum == `cf(1410)` for **150,516 / 152,417** bank-quarters (98.75% exact;
  the residual is dominated by transition-quarter partial filings); (2) decisive: against CLV's
  **published** ln_re on the post-2011 pub-only cells, the component sum reproduces the published
  value for **290,234 / 290,322 (99.97% EXACT**, 70 cells |Δ|>1, 14 unrecoverable).
- **Recipe adopted:** `ln_re = era_pick{ [·,2012Q1): cf("1410"); [2012Q1,·): COALESCE(cf("1410"),
  component_sum) }` — pre-2012 cells unchanged; post-2011 prefers the still-filed RCFD1410 (big-bank
  cells stay matched) and fills the retired-aggregate population with the component sum.
  Cited: dict `:70,:493` (1410), FFIEC RC-C Part I item structure (MDRM codes 1415/1420/1460/1480/
  1797/5367/5368/F158–F161 present in warehouse + MDRM dictionary), the two identity probes above.
- **Gate effect (measured):** modern value-fidelity gate matched 95.7063% → **96.4338%**, UNEXPLAINED
  2.9387% → **2.2258%**; ln_re pub-only UNEXPLAINED 284,862 → 367. Verdict remains **FAIL** honestly
  (coverage/encoding structure elsewhere); thresholds untouched.
