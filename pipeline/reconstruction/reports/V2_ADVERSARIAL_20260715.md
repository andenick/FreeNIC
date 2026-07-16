# V2 Adversarial Review — G-MATCH value-fidelity PASS (eras 1959_1975 + finhist)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715 · **Reviewer:** V2 (independent, adversarial) · **Date:** 2026-07-15
**Claims under attack:** 1959_1975 value-fidelity **99.9753%** PASS; finhist value-fidelity **99.7061%** PASS; both assert **ZERO two-sided value divergences**.
**Posture:** warehouse READ-ONLY; canonical `validation/` artifacts untouched; all re-execution written to a scratchpad out-dir; defects reported, not fixed.

**Bottom line:** **CONFIRMED (qualified).** Every headline number is independently reproduced bit-for-bit, the zero-two-sided claim is proven true for both eras, the denominator excludes nothing, and every divergence is a documented **one-sided coverage** cell. The qualifications are about what the PASS *means* (same-source derivation-layer reproduction, not independent corroboration), one **post-hoc, load-bearing** reclassification that flips finhist to PASS (legitimate but load-bearing), an **over-broad (unbounded) registry reason** that is harmless now but a latent masking risk, and **under-labeled** full-scope FAIL artifacts. **No CONFIRMED DEFECT** (nothing false, fabricated, or masked in the actual data); one **LOW-severity** design weakness.

---

## Attack 1 — Re-run from scratch (determinism)

**Method.** Re-executed `validate_reconstruction.run_era` for BOTH eras, value-fidelity AND full-scope, into a fresh scratchpad out-dir (regenerating the twin variable-maps from the shipped `variable_map`), against the same built + published-ref parquets. Compared gate JSONs field-by-field and fingerprinted the reconciliation parquets (order-insensitive SHA-256 over row hashes).

**Evidence.**
| era | value-fidelity gate reproduced | full-scope gate reproduced | reconciliation parquet content-identical |
|---|---|---|---|
| 1959_1975 | ✅ PASS 99.975315% / unexpl 0.024685% | ✅ FAIL | ✅ (7,470,087×7, sha `b6a1bc9b777d`) |
| finhist | ✅ PASS 99.706090% / unexpl 0.017094% | ✅ FAIL | ✅ (2,632,440×7, sha `6d506bafb312`) |

Every `class_counts`, share, and verdict field matched the canonical `gate_result_*.json` exactly; the reconciliation parquets are content-identical. No wall-clock/timestamps enter artifacts; outputs are sorted deterministically.

**Verdict: CONFIRMED.** Fully deterministic; no nondeterminism.

---

## Attack 2 — The zero-two-sided claim (proven, not asserted)

**Method.** Loaded both canonical reconciliation parquets; for every non-match class, counted sidedness myself (`published` present ∧ `built` present = two-sided value divergence; exactly one present = coverage gap). Sampled and traced 15 cells (8 finhist + 8 MODL).

**Evidence.**
- **finhist (2,632,440 cells):** EXACT 2,624,703 · METHOD-CHOICE 7,287 · UNEXPLAINED 450 · **ROUNDING 0 · TOLERANCE 0**. UNEXPLAINED = **450 published-only, 0 two-sided** (leverage 307, assets 104, notes_nb 39 — dropped/edge rows). METHOD-CHOICE = **7,287 published-only, 0 two-sided**. **Zero two-sided anywhere.**
- **1959_1975 (7,470,087 cells):** EXACT 7,468,243 · UNEXPLAINED 1,844 · **ROUNDING 0 · TOLERANCE 0**. UNEXPLAINED = **1,831 published-only + 13 built-only, 0 two-sided.** Every *matched* cell is bit-EXACT (no near-matches).
- **Traces hold.** finhist deposits 5,762 → built has a **structural gap at year 1905** (override maps to `individual_deposits`, unpopulated there: built deposits non-null 1904=5,414, **1905=0**, 1906=6,139) while the published COALESCE fills it (5,759) — exactly the SPEC §2.14 fork. MODL equity 149 published-only → whole-entity drops (e.g. id_rssd 31303's entire 1959Q4→ run absent from built) consistent with the `05 L59/L104` drop rules.

**Verdict: CONFIRMED.** The "zero two-sided value divergence" claim is literally true for both eras. Every divergence is one-sided coverage.
**Qualified sub-note:** MODL has **13 built-only** UNEXPLAINED cells (all `deposits`, 1962-12-31) — the registry/report language emphasizes "published-only"; these are honestly counted against the gate but are the opposite sidedness. Cosmetic, not a defect.

---

## Attack 3 — Edge-case hunting

**Method.** Read the builders (`build_luck_core.py`, `build_finhist_equivalent.py`) + the reconciliation parquets for each named edge case.

- **Post-failure drops (`05 L104`, days_to_failure<0).** MODL equity 149 UNEXPLAINED are **all published-only** and trace to entities/quarters wholly absent from `luck_core` — consistent with the documented drops. *Qualified:* the exact split between `L104` post-failure and `L59` cert-missing drops isn't labeled per-cell, but **both** are pre-documented drop rules; nothing extra is dropped.
- **Receiver-restart charters (pooled per G-SPEC §6.1).** Built finhist has **0** duplicate `(bank_id, year)` rows; published likewise **0** → each charter-year is a single pooled row, so a within-year restart **cannot** merge two values. Every built cell that overlaps a published cell matched **EXACT**. **No cross-restart value contamination.**
- **Negative surrogate bank_ids.** `luck_core` does carry **28,060 negative pseudo bank_ids** (`-id_rssd` surrogate flowing through `05 L66-77`) — but MODL validation aligns on **`(id_rssd, period_end)`**, and `id_rssd` is strictly positive on both sides (min 37, 0 negatives). The negative pseudo-ids live in the orthogonal `bank_id` space and **never enter the join** — they neither mis-align nor silently fall out.
- **ffpurch method-choice.** `compute_liquid = rowtotal(cash, securities, ffpurch)` per `05 L108` is faithfully reproduced; `ffpurch` is **0% populated** 1959-75 so it contributes 0, and `liquid` has **no published twin** (full-scope only) — so the value-fidelity match is **not** carried by `liquid`. The match is not accidental.

**Verdict: CONFIRMED** (post-failure-vs-cert-missing labeling is a minor QUALIFIED nuance).

---

## Attack 4 — Registry audit: `MC_DEPOSITS_OVERRIDE_HIST`

**Method.** Re-derived the justification from SPEC §2.14 + the do-file cite; queried the parquet for the reclassified cells' sidedness, variable, and year; recomputed the match_share counterfactual.

**Evidence.**
- **Justification is real and pre-documented.** SPEC §2.14 + `04 L100-106` (deposits override windowed to `individual_deposits` 1905-14) vs `clean_bank_panel.deposits_nominal` COALESCE — a genuine construction fork, cited in `variable_map` and the builder `_BUILD_META` before this run. All 5,762 reclassified deposits cells are **published-only (0 two-sided).**
- **match_share provably unchanged.** Counterfactual (revert MC→UNEXPLAINED): match_share stays **99.706090%**; only unexpl_share moves (0.0171% ↔ **0.2939%**). The addition moved cells **out of UNEXPLAINED only**; they remain in the denominator. **Claim verified.**
- **It is load-bearing.** Without the reclassification, finhist FAILS the UNEXPLAINED floor (0.2939% > 0.1%). The addition flips finhist **FAIL→PASS**. The registry doc is transparent about this ("POST-HOC-DISCOVERED … NOT invented to pass").
- **Two robustness concerns.** (a) The registry row has a **blank period window → unbounded**: it reclassifies *every* non-matching finhist `deposits` cell regardless of year/sidedness. It swept **3 cells at year 1865** outside the stated "1900-1905" window, and — critically — it **would silently absorb any future two-sided `deposits` value divergence into METHOD-CHOICE** (verified harmless now: 0 two-sided). The same unbounded scope applies to the pre-existing `MC_EQUITY_ROWTOTAL` (1,525 cells, all published-only, 0 two-sided). (b) "concentrated 1900-1905" is imprecise: **5,759 of 5,762 are at exactly year 1905**, 3 at 1865.
- Shipped and spec-dir `divergence_reasons.csv` are **byte-identical** (md5 `817ea9a3…`); taxonomy constants (GATE 0.999/0.995, FLOOR 0.001) are the pre-registered SPEC §7 values, untouched.

**Verdict: QUALIFIED.** Arithmetically honest, genuinely documented, one-sided, match_share unchanged — but post-hoc, load-bearing, and scoped by an unbounded reason that is a latent masking risk (LOW severity; masks nothing in the current data because 0 two-sided cells exist).

---

## Attack 5 — Denominator honesty

**Method.** Enumerated NOT-DERIVABLE exclusions per era; recomputed a gate share by hand from raw parquet class counts.

**Evidence.** **NOT-DERIVABLE = 0 in BOTH eras** → *nothing* is excluded from the denominator; `derivable == total`. Hand-recompute: finhist `2,624,703 / 2,632,440 = 99.706090%`; MODL `7,468,243 / 7,470,087 = 99.975315%` — both equal the gate JSONs exactly. METHOD-CHOICE cells **stay in the denominator** (they depress match_share, never inflate it). The only genuine scoping is the value-fidelity **twin-variable set** — variables with no published reference are not scored here (they *can't* be cell-matched) and are surfaced honestly in `full_scope/`.

**Verdict: CONFIRMED.** No denominator manipulation.
**Qualified sub-note:** the 99.97%/99.71% is "value fidelity **where a published reference exists**," not of all built cells — full-scope is 54.4%/26.7% because derived aggregates (crisisBVX, ratios, liquid, res_funding, …) have no twin. A reader must not conflate the two.

---

## Attack 6 — Full-scope FAIL artifacts (coverage boundary)

**Method.** Compared the `full_scope/` report + gate JSON against the value-fidelity ones.

**Evidence.** The full-scope FAIL artifacts carry the **same title, schema, and gate description** as the value-fidelity PASS artifacts, distinguished only by (a) the `full_scope/` directory, (b) `verdict: FAIL`, and (c) every failing variable showing `published = 0` (i.e. no twin → pure coverage gap). There is **no explicit in-file "coverage / full-scope, NOT value-fidelity" marker**; only `gmatch_summary.json` labels the two runs (`value_fidelity` vs `full_scope`).

**Verdict: QUALIFIED.** Honest in aggregate (the `published=0` columns make the coverage nature evident, and the boundary paragraph explains it), but a reader opening `full_scope/RECONSTRUCTION_REPORT_*.md` in isolation could misread the 54%/27% FAIL as a value-fidelity failure. **Recommend** an explicit banner in the full-scope report/JSON.

---

## Cross-cutting finding (feeds the overall verdict) — what the PASS actually certifies

Both PASSED eras compare **two freeNIC-side derivations of the SAME underlying CLV source `.dta`**:
- **MODL:** `luck_core` reads `sources/call-reports-modern.dta` directly; the published twin `luck_wide` is the **ingested copy of the same `.dta`**.
- **finhist:** `finhist_equivalent` reads `historical-call.dta` directly; the published twin `clean_bank_panel` HIST stratum was built by `45_build` from `occ_historical` = the **ingested long-format copy of the same `.dta`** (confirmed in the builder's own cross-check note).

The near-perfect **all-EXACT** result (0 ROUNDING, 0 TOLERANCE, 0 two-sided) is exactly what a same-source re-derivation predicts, and the value-fidelity twin set is dominated by **direct passthrough level columns**. This is **disclosed by design** — SPEC §0 states "their `.dta` is the only machine source … we run their formula on their input," and the 99.9% MODL bar is deliberately set to near-perfect for that reason. So it is honest and internally consistent, **not a defect** — but the PASS certifies **re-derivation reproducibility (and the re-implemented scaling/drop transforms), NOT independent corroboration of CLV's published numbers.** The independent tier is MODC (1976_2026), still building.

---

## Verdict summary

| # | Attack | Verdict |
|---|---|---|
| 1 | Re-run determinism | **CONFIRMED** (byte/content-identical both eras) |
| 2 | Zero two-sided | **CONFIRMED** (0 two-sided; all one-sided coverage; 15 traced) |
| 3 | Edge cases | **CONFIRMED** (negative-ids orthogonal to key; restart pooling clean; ffpurch faithful) |
| 4 | Registry `MC_DEPOSITS_OVERRIDE_HIST` | **QUALIFIED** (honest + match_share unchanged; post-hoc/load-bearing; unbounded reason = LOW-severity latent masking risk) |
| 5 | Denominator honesty | **CONFIRMED** (NOT-DERIVABLE=0 both eras; nothing excluded; shares recomputed by hand) |
| 6 | Full-scope FAIL labeling | **QUALIFIED** (honest but under-labeled; add a coverage banner) |

**Defects:** none CONFIRMED. One **LOW-severity** design weakness — unbounded `deposits`/`equity` METHOD-CHOICE registry reasons would absorb a future two-sided value divergence into METHOD-CHOICE without surfacing it. *Repro:* inject a two-sided finhist `deposits` mismatch → it classes METHOD-CHOICE (not UNEXPLAINED) and never trips the floor. Suggested (do not apply here): add a one-sided/coverage guard or a period bound to the two unbounded reason rows.

**V2 VERDICT (both eras): CONFIRMED, qualified.** The 1959_1975 (99.9753%) and finhist (99.7061%) value-fidelity PASS verdicts are reproducible, arithmetically honest, zero-two-sided as claimed, and denominator-clean. The load-bearing finhist reclassification is legitimate and transparent. The material caveat is scope, not fidelity: these gates certify **same-source derivation-layer reproduction**, not independent validation of CLV's numbers.

---

# V2-MODERN Adversarial Review — MODC `1976_2026` post-remediation gate (the REAL independent tier)

**Campaign:** FREENIC11_RECONSTRUCTION_20260715 · **Reviewer:** V2 (independent, adversarial) · **Date:** 2026-07-15
**Claims under attack:** post-remediation D2 gate **FAIL** matched **95.7063%** / UNEXPLAINED **2.9387%**; SUPPLEMENTARY matched-where-both-present **99.6220%**; two-sided divergence **38,717 = 0.0971%** of derivable; `MC_ZEROFILL_ENCODING` = **521,664** cells all genuinely zero-vs-NULL; the three §10 form-arms (ffpurch B993 / otherbor 2850+2910 pre-1994 / ln_cons B538+B539+K137+K207 with the 27,408-cell 2011 identity); the internal-consistency relabeling; registry rows bounded.
**Posture:** warehouse `freenic.duckdb` NEVER opened (concurrent writer this batch); every number below is recomputed with my OWN duckdb SQL over the published `.dta`-derived parquets + the canonical `reconciliation_1976_2026.parquet` (272 MB, 40,261,387 rows). Canonical `validation/` artifacts untouched; re-execution written to a scratchpad out-dir. Defects reported, not fixed.

**Bottom line:** **CONFIRMED (qualified).** Every headline modern-era number reproduces to the digit from the raw reconciliation; the D2 gate FAIL is stated plainly and the thresholds are untouched; the `MC_ZEROFILL_ENCODING` predicate is exactly (0.0 vs NULL) on all 521,664 cells with **zero** two-sided absorption and **zero** leakage into UNEXPLAINED; the sidedness ledger closes to the cell; the three §10 arms are genuinely built and near-perfectly matched; the ln_cons 2011 identity's observable consequences hold exactly. **No CONFIRMED DEFECT.** Qualifications are about *meaning/scope*, not fidelity: (a) the SUPPLEMENTARY both-present denominator is slightly over-inclusive (contains 106,129 NOT-DERIVABLE both-present cells → the 99.62% is a conservative floor, not inflated); (b) the ln_cons raw-component identity itself is a READ-ONLY warehouse probe I cannot re-run this batch (its downstream consequence is fully verified); (c) two-sided divergence concentrates in documented construction-fork/vintage variables (honestly UNEXPLAINED, never masked).

---

## Attack 1 — Re-run the harness fresh (determinism)

**Method.** Re-invoked `validate_reconstruction.run_era("1976_2026", PUBLISHED, BUILT, <scratch>, variable_map=<fresh twin map>)` on the SAME on-disk inputs the canonical run used (`validation/published_refs/published_modern_clv_1976_2024.parquet` + `_work/built_luck_1976_2026_idrssd_real.parquet`), into a scratchpad out-dir. Diffed the resulting `gate_result_1976_2026.json` field-by-field against canonical and compared the reconciliation parquet order-insensitively (EXCEPT both directions in duckdb).

**Evidence.** The re-run `gate_result_1976_2026.json` is **field-by-field identical** to canonical (match_share `0.9570627538331616` = 95.7063%, verdict FAIL, and every `class_counts` entry — EXACT 38,176,943 · ROUNDING 0 · TOLERANCE 2,770 · VINTAGE 18,874 · METHOD-CHOICE 521,664 · NOT-DERIVABLE 368,796 · UNEXPLAINED 1,172,340 — matches). The reconciliation is **content-identical**: 40,261,387 rows on both sides, **0** rows in canon∖rerun, **0** in rerun∖canon. No wall-clock or randomness enters the artifacts; outputs are deterministically sorted.

**Verdict: CONFIRMED.** Fully deterministic — the headline gate and the full 40.3M-cell reconciliation reproduce exactly from the same inputs.

---

## Attack 2 — The zero-vs-NULL predicate (is EVERY MC_ZEROFILL cell exactly 0.0-vs-NULL?)

**Method.** Over the canonical reconciliation, restricted to `class='METHOD-CHOICE'` (521,664 cells) and tested the SPEC §10.4 predicate cell-by-cell; then swept ALL zero-vs-NULL cells across every class to check for leakage into UNEXPLAINED or absorption of a two-sided divergence.

**Evidence.**
- `class='METHOD-CHOICE'` = **521,664**, every one carrying `reason_id='MC_ZEROFILL_ENCODING'` (no other MC reason present).
- Predicate `(published=0.0 AND built IS NULL) OR (built=0.0 AND published IS NULL)` holds for **521,664 / 521,664**; predicate violations = **0**; both-present-in-MC = **0**; `(0.0 vs 0.0)` = **0**; present-side-nonzero = **0** (the present side is *exactly* the float `0.0`, never a nonzero value).
- All zero-vs-NULL cells in the whole panel land as: METHOD-CHOICE 521,664 · VINTAGE 2,967 · NOT-DERIVABLE 2,778 · **UNEXPLAINED 0**. The 2,967 + 2,778 are held by the more-specific pre-registered rows (`VINTAGE_TIMEDEP_PRE1994`, `ND_SECURITIES_PRE1994`) that out-rank the wildcard row applied LAST — exactly the documented first-match precedence. **Zero zero-vs-NULL cells leaked into UNEXPLAINED; zero two-sided nonzero divergences were absorbed** (structurally impossible — a two-sided cell has both sides present, so the mask cannot fire; confirmed empirically = 0).

**Verdict: CONFIRMED.** The 521,664-cell claim and the "all genuinely zero-vs-NULL" claim are exactly true; the predicate is symmetric, denominator-preserving, and non-inflating.

---

## Attack 3 — The SUPPLEMENTARY 99.6220% (recompute by hand; denominator honesty)

**Method.** Recomputed matched-where-both-present from raw counts: numerator = cells with `class ∈ {EXACT,ROUNDING,TOLERANCE}` AND both sides present; denominator = cells with both sides present. Checked what the both-present denominator includes.

**Evidence.**
- both-present (all classes) = **38,324,579**; matched-and-both-present = **38,179,713** → **38,179,713 / 38,324,579 = 0.99622002 = 99.6220%** — reproduces the claim to the digit. (All 38,179,713 matched cells are inherently both-present: matched_all == matched_both.)
- Denominator honesty: the both-present denominator **excludes nothing improper** — it is if anything *over*-inclusive. It contains **106,129 NOT-DERIVABLE both-present cells** (securities pre-1994) counted as *non-matches*. Excluding them (the gate's derivable basis) gives 38,179,713 / 38,218,450 = **99.8987%** — HIGHER. So the reported 99.6220% is the **conservative** figure; the metric never cherry-picks divergent cells out of the denominator.

**Verdict: CONFIRMED.** 99.6220% reproduces exactly and is a conservative floor.
**Qualified sub-note (LOW/cosmetic):** the SUPPLEMENTARY denominator (all both-present) is not the gate's derivable basis (it carries 106,129 ND cells); the direction is conservative, but the two "both-present" bases could be labeled to avoid a reader conflating them.

---

## Attack 4 — The ln_cons post-2011 successor identity

**Method.** The identity `rowtotal(cf B538,B539,K137,K207) == cf(1975)` across all 27,408 2011 bank-quarters is a builder-side READ-ONLY **warehouse** probe over raw MDRM components — NOT re-runnable this batch (warehouse embargoed; the built panel stores only final `ln_cons`, not the four components). I therefore verified its **observable consequences** from the reconciliation + built panel: the 2011 cell count, the 2011 match (built uses `cf 1975` there), and the 2012+ match (built switches to the successor rowtotal), plus 10 spot cells.

**Evidence.**
- `ln_cons` 2011 cells = **27,408** — exactly the count the identity claim names.
- 2011 (built = `cf 1975`): 27,404 both-present, **27,399 EXACT (99.98%)**, only 5 two-sided.
- 2012 (built switches to the successor arm): 29,086 both-present, **29,086 EXACT (100.00%), 0 two-sided**; 2013 likewise **27,916/27,916 EXACT, 0 two-sided**. The successor arm reproduces CLV's published `ln_cons` cell-for-cell with **no discontinuity** at the 2011→2012 seam — precisely what the `cf1975 ≡ successor` identity guarantees. Post-2012 arm coverage overall: 292,315 cells, 292,225 EXACT (99.97%).
- 10/10 spot cells (2011) are EXACT to the dollar (e.g. 63,241/63,241; 368,906/368,906).

**Verdict: CONFIRMED (by consequence).** The identity's count (27,408) and every downstream effect are verified exactly; the successor arm is a genuine, near-perfect match. **Scope caveat:** the raw-component equality itself rides on a warehouse probe I could not independently re-execute this batch — reported honestly, not a defect.

---

## Attack 5 — Two-sided 38,717 (vintage-shaped vs method-shaped; hidden builder bug?)

**Method.** Counted two-sided cells (`class='UNEXPLAINED'` AND both sides present), bucketed by |Δ|/|pub|, and clustered by variable and variable×decade to hunt a builder-bug signature. Drew a variable-stratified sample (~2/variable, 44 cells).

**Evidence.**
- two-sided total = **38,717** (0.0971% of derivable) — reproduces exactly.
- Shape: **11,674 (30%) near-tolerance** (<2% reldiff, vintage restatements) · **26,797 (69%) method-shaped** (≥2%) · 246 with published exactly 0 · 5,596 with built exactly 0.
- Clusters all map to **documented seams/vintage**, none to an undocumented builder bug:
  - `otherbor_liab` 8,759 total, **8,522 in 1994-1996** — the §10.2 arm boundary where the pre-1994 `2850+2910` arm meets `cf(3190)` (SPEC records the component chain reproduces 3190 for only 93.4% of the 1994-96 overlap). Documented seam.
  - `ytdint_exp_dep` 7,451, concentrated **1986-1988** (5,443) and **2012-2016** — the pre-1994 RIAD arm and the `_BUILD_META`-documented 2012-2016 dictionary gap (honest partial from the foreign-office-filer subset). Documented.
  - `ln_fi` 2,771, concentrated **1979-1983** — a heavily construction-forked variable (339,856 MC, 88,135 UNEXPLAINED in the coverage matrix); early-period definitional divergence, honestly UNEXPLAINED.
  - A 2003 spike spans core **levels** (assets median reldiff 0.15%, ln_tot 0.36%, deposits 0.28% — vintage-shaped, Chicago-Fed vintage vs CLV Jan-2026 snapshot restatements) alongside larger relative diffs in **YTD income** items (ytdnetinc median ~15% — small-denominator income noise); neither is a construction error and both are honestly UNEXPLAINED.
- Every two-sided cell is held in **UNEXPLAINED** — none absorbed into MC/VINTAGE/ND (verified in Attack 2). The concentration is honest, not masking.

**Verdict: CONFIRMED.** 38,717 reproduces exactly; two-sided divergence is a mix of vintage restatements + method/seam divergences in variables the spec already flags as construction forks; no cluster indicates an undocumented builder bug, and nothing is masked.

---

## Attack 6 — Sidedness bookkeeping (does the ledger sum to derivable?)

**Method.** Independently computed, per class, the split into both-present / published-only / built-only over the whole reconciliation, and summed the ledger.

**Evidence.** (independent duckdb counts)

| class | n | both | pub_only | blt_only |
|---|---|---|---|---|
| EXACT | 38,176,943 | 38,176,943 | 0 | 0 |
| UNEXPLAINED | 1,172,340 | **38,717** | **563,990** | **569,633** |
| METHOD-CHOICE | 521,664 | 0 | 30,913 | 490,751 |
| NOT-DERIVABLE | 368,796 | 106,129 | 258,120 | 4,547 |
| VINTAGE | 18,874 | 20 | 8,069 | 10,785 |
| TOLERANCE | 2,770 | 2,770 | 0 | 0 |

- UNEXPLAINED sidedness reproduces the claim **exactly**: two-sided 38,717 + pub_only 563,990 + blt_only 569,633 = **1,172,340**.
- Full ledger closes to the cell: matched (EXACT+TOLERANCE = 38,179,713) + MC 521,664 + VINTAGE 18,874 + UNEXPLAINED 1,172,340 = **39,892,591 = derivable**; derivable + NOT-DERIVABLE 368,796 = **40,261,387 = total** = parquet rowcount; cells absent from both panels = **0**.

**Verdict: CONFIRMED.** The sidedness ledger is exactly derivable; the quoted blt_only/pub_only/two-sided figures match the raw counts to the cell.

---

## Attack 7 — Pre-registration integrity (did any rule change AFTER its re-gate ran?)

**Method.** Compared the SPEC §10 amendment + `divergence_reasons.csv` mtimes against the re-gate artifact mtimes; read §10's content vs the realized classification.

**Evidence.** Authoring precedes execution, in order: `RECONSTRUCTION_SPEC.md` §10 **18:28:56** → `build_luck_equivalent.py` 18:30:03 → `validate_reconstruction.py` 18:31:23 → `divergence_reasons.csv` (both shipped + spec-dir copies, byte-identical) **18:33:09** → then the re-gate: published-refs 18:54:33 → built-work 18:54:45 → **reconciliation 18:57:32 → gate_result 18:58:11**. The classification rule (`divergence_reasons.csv`) was frozen **~24 min BEFORE** the reconciliation/gate it governs. §10's text (ffpurch B993 correction of the brief's "RCONB987"; otherbor 2850+2910; ln_cons B538/B539/K137/K207 with the 27,408 identity; the symmetric ZERO_VS_NULL predicate applied LAST) matches the realized `reason_id` distribution exactly. The `REGISTRY_ADDITIONS_MODERN_REMEDIATION` doc (19:34:45) is post-hoc *documentation*, not a rule change.

**Verdict: CONFIRMED.** No classification rule changed after its re-gate ran; rules are pre-registered ahead of execution.
**Qualified sub-note:** the era report + summaries were re-emitted at 19:23 (≈25 min after the 18:58 gate JSON) — a benign report/supplementary regeneration reading the same 18:57 reconciliation; the authoritative gate JSON + reconciliation are the earlier, rule-consistent artifacts.

---

## Attack 8 — FAIL framing honesty (is the language honest; supplementary subordinate?)

**Method.** Read the combined `RECONSTRUCTION_REPORT.md`, the era report `RECONSTRUCTION_REPORT_1976_2026.md`, and `_gmatch_modern_run.json`.

**Evidence.** The combined report's headline table shows `1976_2026 … 95.7063% … **FAIL**` and the section is titled **"Overall: NOT ALL ERAS PASS."** The era report states **"PRE-REGISTERED D2 GATE VERDICT: FAIL"** first, with "Thresholds untouched (non-negotiable)," and confines the 99.6220% / 0.0971% figures to a block explicitly headed **"SUPPLEMENTARY value-fidelity metrics (NOT the pre-registered gate — clearly labelled)."** The reading paragraph says outright: "The claim that the rebuild reproduces CLV's published modern panel *cell-for-cell* is NOT supported and is held." No supplementary number is promoted to a headline; FAIL is never softened to a pass.

**Verdict: CONFIRMED.** The framing is honest: FAIL is stated plainly and primary; the supplementary metrics are clearly subordinate and correctly labeled.

---

## V2-MODERN verdict summary

| # | Attack | Verdict |
|---|---|---|
| 1 | Re-run determinism | **CONFIRMED** (gate JSON field-identical; 40.3M-row reconciliation content-identical) |
| 2 | Zero-vs-NULL predicate | **CONFIRMED** (521,664/521,664 exact; 0 leak, 0 two-sided absorbed) |
| 3 | Supplementary 99.6220% | **CONFIRMED** (reproduced; conservative — denom carries 106,129 ND cells) |
| 4 | ln_cons 2011 identity | **CONFIRMED by consequence** (27,408 count; 2012+ successor 100% EXACT; raw-component identity = un-re-runnable warehouse probe) |
| 5 | Two-sided 38,717 | **CONFIRMED** (exact; vintage+documented-seam shaped; no hidden builder bug; nothing masked) |
| 6 | Sidedness ledger | **CONFIRMED** (closes to the cell; blt/pub/two-sided exact) |
| 7 | Pre-registration integrity | **CONFIRMED** (rules frozen ~24 min before the re-gate) |
| 8 | FAIL framing | **CONFIRMED** (FAIL plain + primary; supplementary clearly subordinate) |

**Defects:** none CONFIRMED. Two LOW/cosmetic qualifications: (a) the SUPPLEMENTARY both-present denominator (38,324,579) is not the gate's derivable basis — it carries 106,129 NOT-DERIVABLE both-present cells, making 99.6220% a conservative floor (label to prevent conflation); (b) the ln_cons raw-component identity rests on a warehouse probe not independently re-runnable this batch (consequence fully verified).

**V2-MODERN VERDICT (1976_2026, post-remediation): CONFIRMED (qualified).** The post-remediation modern gate is arithmetically honest to the cell: FAIL 95.7063% / UNEXPLAINED 2.9387% with untouched thresholds; the MC_ZEROFILL_ENCODING predicate is exactly zero-vs-NULL and cannot raise match_share; the sidedness ledger closes; the three §10 arms are genuinely built and near-perfectly matched; the 99.6220% supplementary is reproduced and conservative; two-sided divergence (38,717) is small, documented, and unmasked. This gate certifies an **honest, well-classified independent Fed-direct re-derivation whose value fidelity where coverage overlaps is very high**, with a transparently-held cell-for-cell claim.
