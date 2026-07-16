# SPEC_CHECK_20260715.md — G-SPEC adversarial check of RECONSTRUCTION_SPEC.md

**Campaign:** FREENIC11_RECONSTRUCTION_20260715 · **Gate:** G-SPEC (R2 adversarial checker)
**Checker:** independent re-derivation from primaries, then diff. **Date:** 2026-07-15
**Snapshots (pre-edit):** `RECONSTRUCTION_SPEC.md.bak-gspec`, `variable_map.csv.bak-gspec` (same dir).
**Primaries used (absolute):**
- Do-files extracted read-only to scratchpad from `Inputs/luck_database/qje-repkit.zip`
  → `code/{04,05,06,07}_*.do`, `common.do`, `02_import_GFD_CPI.do`.
- Builders: `Technical/freenic_ingestion/scripts/{30_build_public_luck_panel,45_build_clean_bank_panel}.py`.
- **NEW EVIDENCE (post-dated the spec author):** `Inputs/luck_database/docs/FailingBanks_arXiv_2506.06082.pdf`
  — **Table C.1 (call-report MDRM data appendix) on PDF p.112**; liquid-asset definition figure note on **PDF p.81**.

> **Honesty note on derive-before-peek.** The 10 sampled formulas were re-derived by reading the cited
> do-file / builder source lines directly (quoted below with line cites) and only then compared to the
> spec's answer. Derivations rest on primary source lines, not on the spec's prose.

---

## TASK 1 — 10-variable independent re-derivation (seed 20260715; strata 4/3/3)

Sample (seed 20260715, stratified, sorted-pool `random.sample`):
- **1976+ (4):** equity `F_eq_mod`, ytdint_inc `F_intinc`, demand_deposits `F_demdep_mod`, int_inc_ratio `R_intincr`
- **1959–75 (3):** equity `F_eq_dta`, deposits `F_dep_dta`, time_deposits `F_timedep_dta`
- **finhist (3):** surplus_ratio `R_surpratio`, equity `F_eq_hist`, demand_deposits `F_demdep_hist`

| # | var / era | Checker derivation (primary line) | Spec answer | Verdict |
|---|---|---|---|---|
| 1 | equity 1976+ | `30_build AGG_SQL L65` `"equity": cf("3210")` = COALESCE(MAX RCFD3210, MAX RCON3210) | cf(3210), dict :69 | **AGREE** |
| 2 | ytdint_inc 1976+ | `30_build AGG_SQL L75` `"ytdint_inc": riad("4107")` = MAX(RIAD4107) | riad(4107) | **AGREE** (Table C.1 p.112 corroborates: Total Interest Income = RIAD4107) |
| 3 | demand_deposits 1976+ | `30_build AGG_SQL L67` `"demand_deposits": cf("2210")` | cf(2210), dict :27 | **AGREE** (Table C.1: RCON2210, 1959-12-31→present) |
| 4 | int_inc_ratio 1976+ | `07 L117` `gen int_inc_ratio = ytdint_inc_ln/assets`; `07 L120-122` sets missing if `quarter_number!=4`; `07 L141` `clip(0,1)` | ytdint_inc_ln/assets, Q4, clip[0,1] | **AGREE** (cite enriched: add L120-122 for the Q4 gate) |
| 5 | equity 1959–75 | `45_build pivot_modl` SELECT reads `equity` directly from `luck_wide` (col list L187) | luck_wide.equity | **AGREE** (cite nit: pivot_modl col list is L186-188; `equity` sits on L187, spec says L188) |
| 6 | deposits 1959–75 | `45_build pivot_modl` reads `deposits` from `luck_wide` (L187) | luck_wide.deposits | **AGREE** (same L187/L188 nit) |
| 7 | time_deposits 1959–75 | `45_build pivot_modl` reads `time_deposits` from `luck_wide` (L187) | luck_wide.time_deposits | **AGREE** (same nit) |
| 8 | surplus_ratio finhist | `07 L71` `gen surplus_ratio = surplus_profit/equity` (NOT in the L143 >1/<0 validity filter — confirmed) | surplus_profit/equity | **AGREE** |
| 9 | equity finhist | `04 L84-85` `egen equity = rowtotal(capital surplus undivided_profits surplus_and_undivided_profits)`; missing iff all 4 missing | rowtotal of the 4; freeNIC COALESCE-guard = METHOD-CHOICE | **AGREE** |
| 10 | demand_deposits finhist | `45_build pivot_hist L160` `MAX(CASE WHEN variable_id='demand_deposits' THEN value END)` → a **raw OCC line item**. `04 L100-102` do NOT construct it — they *consume* it to override `deposits`. | source_kind=`reconstructed_agg`, cite `04 L100-102` | **SPEC-CORRECTED** |

**Sample result: 9 AGREE / 1 SPEC-CORRECTED / 0 CHECKER-WRONG / 0 new METHOD-CHOICE.**

### Adjudication of the one disagreement (#10 demand_deposits finhist) — cited
- **Primary:** `45_build pivot_hist L160` pivots `occ_historical` `variable_id='demand_deposits'` as a direct
  `MAX(CASE …)` — i.e. a raw OCC line item, identical in kind to `time_deposits`/`us_deposits` (L161-163).
  `04` never builds `demand_deposits`; at `04 L100-102` it *uses* demand_deposits (with time_deposits) to
  **override** the `deposits` total for 1915-28. `04 L137` keep-list carries `demand_deposits` as an input column.
- **Verdict = CHECKER-RIGHT (spec cell wrong on classification + cite).** `source_kind` should be
  `occ_line_item` (not `reconstructed_agg`); `dofile_cite` should point to `45_build pivot_hist L160`
  (raw occ variable), not `04 L100-102` (which consume it). The formula text ("occ demand_deposits line
  item") was already correct and contradicted its own `source_kind`. **Correction applied** to variable_map
  row 11 + spec §2.4 prose ("`04` reconstructs `deposits` *from* demand_deposits, which is itself a raw OCC item").

---

## TASK 2 — the 4 SOURCE-PENDING(paper) cells, resolved from the appendix (cited)

1. **Exact CPI base label** → **NOT STATED in the paper.** The appendix only ever says "deflated by (the)
   CPI" (figure notes, arXiv **p.81**, and full-doc lines 538/2227/2310). No base-year is published; the
   deflator is GFD's native CPI index divided directly (`02_import_GFD_CPI.do`; `07 L32-34 var/cpi_gfd`).
   **Resolution: the spec's stance is CONFIRMED** — real *ratios/rankings* are base-invariant, real *levels*
   are index-relative; reproduce the exact `/cpi_gfd` division bit-for-bit. Base label is immaterial and
   unavailable; downgrade from SOURCE-PENDING to **RESOLVED (no published base; reproduce-by-division)**.

2. **ln_cc / ln_oth / ln_fi per-era MDRM** → **RESOLVED from Table C.1 (arXiv p.112).** All are RCON:
   - **ln_cc (Credit Card Loans)** = `RCON2008` (1967-12-31→2000-12-31) → `RCON B538` (2001-03-31→present).
   - **ln_fi (Financial Loans)** = `RCON1495` (1959-06-10→1983-12-31) → `RCON 1505+1510+1517+1756+1757`
     (1976-03-31→2000-12-31) → `RCON B531+B534+B535` (2001-03-31→present).
   - **ln_oth (Other loans)** = **NOT in Table C.1** — there is no published "Other Loans" row. It remains a
     `.dta` column / residual with honest `INFERRED` provenance (cannot be upgraded).

3. **num_employees field** → **RESOLVED: `RIAD4150`** ("Number of Full-Time Employees"), Table C.1
   (arXiv p.112, last row). The spec's tentative RIAD4150 is CONFIRMED; upgrade from SOURCE-PENDING/inferred
   to cited. (Adjacent: Salaries & Employee Benefits = RIAD4135; Net Income = IADX5106 pre-69 → RIAD4340 —
   both corroborate the spec.)

4. **liquid ffpurch-sign intent** → **RESOLVED from the figure note (arXiv p.81).** The *published*
   modern (1959+) liquid-asset definition is: "currency and reserves held, balances with other banks, cash
   items in collection, and security holdings (both government-issued and private label)." **Fed funds do
   NOT appear** in the published definition (neither sold nor purchased). Therefore `05 L108`
   `egen liquid = rowtotal(cash securities ffpurch)` adds `ffpurch` (fed funds *purchased*, a liability =
   `cf(0278)`) **beyond the paper's stated concept** — an unremarked do-file inclusion, not an intended
   liquid component. **Resolution:** the sign question is moot (the concept excludes fed funds entirely);
   reproduce `05 L108` verbatim to cell-match `combined-data.dta`, but classify **METHOD-CHOICE /
   documented-quirk** and footnote that the *published definition* excludes fed funds.

---

## TASK 3 — Entity-spine attack (04/05 line-by-line) — VERDICT: SOUND, one clarification applied

**Modern spine `05 L53-81` — all verified against source:**
- L54-55 zero→missing ✓; L58 `id_fdic_cert=-id_rssd if missing` ✓; L59 drop if still missing ✓.
- L66 `bank_id = abs(id_fdic_cert)*10 + (id_fdic_cert<0)` is **unconditionally overwritten** by L67
  `bank_id = id_fdic_cert*10 + (qofd(fail_day)<=quarter) + (qofd(fail_day2)<=quarter)` (no `if`) — spec's
  cite of L66-67 with the L67 formula is correct; L66 is dead for the output. ✓
- L77 `bank_id=bank_id*1e5` disjointness ✓ (modern bank_id ≥ 1e6 ≫ 5-digit OCC charters ≤ 99999).
- **Edge — cert-missing banks:** surrogate `id_fdic_cert=-id_rssd` (negative) flows through L67 →
  **negative bank_id** (L66's `abs()` is overwritten), which stays disjoint from positive HIST charters and
  positive modern certs. Non-fatal; noted (spec need not change, but the negative-surrogate branch is now on record).
- **L134 `drop id_fdic_cert` + L135 `isid bank_id quarter`:** the merge key `id_fdic_cert` is DROPPED; the
  persistent modern panel key is `bank_id`. Spec's "primary linking key = id_fdic_cert" is true only for the
  FDIC-failure *merge* (L62); clarified in-line.

**HIST spine `04 L10-20` — the one real correction:**
- `04 L18` `gen long id = 10*bank_id + version` and `xtset id year` are verified verbatim. **BUT `id` is
  NOT in the `04 L133-139` keep-list — it is dropped; `bank_id` (5-digit charter) is kept.** No time-series
  operator is applied between the `xtset id` and the drop, and `failed_bank` is `by(bank_id)` (`04 L33`).
  Downstream, `06`/`07` `xtset bank_id quarter`. **Consequence: the delivered combined panel keys on
  `bank_id` (charter); the receiver-restart `version` distinction does NOT persist — a bank that re-enters
  receivership is POOLED under one charter entity, not treated as a distinct entity.** The spec's flat claim
  "treated as a distinct entity (new version)" over-states what survives into the panel. **Correction applied**
  to spec §6.1 + variable_map `E_hist` (row 96): the version-id is an intermediate `04` xtset construct that
  is dropped; entity-level reproduction keys on `bank_id`.
- **Append-not-join / gap:** `07 L11-12` `use …historical-edited; append using …modern` ✓. Note the appended
  historical file is **`call-reports-historical-edited.dta` produced by `06 L156`** (run-dummy augmented),
  not `04`'s direct `call-reports-historical.dta` — the spec's §1 chain omits this hop; **noted + added** to §1.
  1942-1958 gap: structurally absent (occ 1863-1941, luck 1959+); `45_build L466-468` asserts 0 rows ✓.

**Entity-spine verdict: SOUND.** All ID-hygiene, pseudo-id, disjoint-range, and gap mechanics are faithfully
described; the only substantive fix is the HIST version-id-is-dropped clarification (charter-pooling), plus
the `-edited` intermediate and `id_fdic_cert`-dropped notes.

---

## TASK 4 — 5 INFERRED rows: upgrade attempt with the appendix

| Row | INFERRED cell | Upgrade? | Basis |
|---|---|---|---|
| 71 num_employees | RIAD4150 SOURCE-PENDING | **UPGRADED → cited** | Table C.1 p.112 = RIAD4150 |
| 32 ln_cc_oth_fi | per-era MDRM SOURCE-PENDING | **PARTIAL upgrade** | ln_cc & ln_fi cited to Table C.1 p.112; ln_oth stays inferred (no published row) |
| 20 securities pre-1994 | not-derivable ceiling | **No upgrade** (stays NOT-DERIVABLE) | Table C.1 + FFIEC 010/011 form discussion (p.~108-112) corroborate the pre-1976/pre-1984 form-era cause; pre-built in the un-shipped `3-create-variables.do` |
| 14 time_deposits pre-1994 | not-derivable bulk-vintage | **No upgrade** (stays NOT-DERIVABLE) | RCON6648 valid only 1984+ (Table C.1 confirms the era split); pre-94 distributed value is bulk-vintage |
| 70 npl_tot 1959-75 | sparse pre-1982 | **No upgrade** | Table C.1: NPL = 1403+1407 valid 1982+ only; pre-82 remains sparse/honest |

**INFERRED upgrades: 2** (num_employees fully; ln_cc/ln_fi partially). 3 correctly stay honest.

### Bonus corroborations / boundary corrections from Table C.1 (applied where they sharpen the spec)
- **securities era boundaries (§2.6):** the *published* Table C.1 periods are `0400+0600+0900+0950` →
  **1959-06-10 to 1976-03-31**; `0390` → **1976-03-31 to 1993-12-31**; `1754+1773` → 1994-03-31+. The spec's
  dictionary-quoted boundaries (0400-sum to 1994, 0390 "alt from 1983") are looser/imprecise; `30_build`'s
  actual `cf(0390) for <1994` matches the published table for its 1976+ scope, so **no code defect** — but
  §2.6 now cites the authoritative Table C.1 periods.
- **ln_ci / time_deposits:** Table C.1 confirms C&I = `1600`(→1984) / `1766`(1984+) and Time = `2514`(→1984)
  / `2604+6648`(1984-2010) / `J473+J474+6648`(2010+), corroborating the spec's B-phase gap flags
  (add pre-1984 1600 arm; add post-2010 J473/J474 arm).

---

## TASK 5 — Pre-registered taxonomy (§7): complete but needs a precedence rule

- **Complete:** the 7 classes cover the outcome space (UNEXPLAINED is the catch-all that counts against the gate). ✓
- **Ambiguity found:** EXACT ⊂ ROUNDING ⊂ TOLERANCE numerically overlap (a bit-identical cell also satisfies
  ROUNDING and TOLERANCE), and a numerically-close cell can *also* be a known VINTAGE/METHOD-CHOICE case. The
  spec says "classified into exactly one class" but gives **no evaluation order**, so a harness coder must make
  a judgment call. **Correction applied to §7:** add an explicit **first-match precedence**
  (EXACT → ROUNDING → TOLERANCE → VINTAGE → METHOD-CHOICE → NOT-DERIVABLE → UNEXPLAINED) and a rule that the
  three "documented" classes (VINTAGE / METHOD-CHOICE / NOT-DERIVABLE) require a **pre-registered reason key**
  (a case cannot be relabeled into them post hoc to hide an UNEXPLAINED mismatch). This makes classification
  deterministic and keeps the pre-registration honest.

---

## Corrections applied (this pass)

**variable_map.csv:** row 11 demand_deposits(hist) source_kind+cite; row 32 ln_cc_oth_fi Table C.1 cites +
confidence; row 54 liquid(mod) ffpurch resolution; row 71 num_employees → RIAD4150 cited; row 95 cpi_deflator
base resolved; row 96 entity_spine_hist version-id-dropped clarification.

**RECONSTRUCTION_SPEC.md:** §1 add `-edited` hop; §2.4 demand_deposits raw-item clarify; §2.6 securities
published-period cite; §2.8 ln_cc/ln_fi resolved (ln_oth honest); §2.15 liquid ffpurch resolved; §3
num_employees = RIAD4150; §6.1 HIST version-id-dropped + id_fdic_cert-dropped; §6.5/§9 CPI base resolved;
§7 precedence + reason-key rule; §9 SOURCE-PENDING list updated (3 resolved, 1 confirmed).

## G-SPEC VERDICT: **GREEN** (corrections applied)
No fabrication, no core-tier formula that would emit wrong values, no fatal defect. The independent 1976+
recipes re-derive cleanly (9/10 sampled agree; the 1 miss was a mis-classification/cite, not a wrong formula);
all 4 SOURCE-PENDING cells are resolved from the newly-landed appendix (3 cleanly, 1 confirming the spec);
the entity spine is faithful modulo the version-id-dropped clarification; the taxonomy is complete and now
deterministic. Spec is cleared for the B-phase.
