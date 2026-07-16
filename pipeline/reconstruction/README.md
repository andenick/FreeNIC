# FreeNIC reconstruction module — Luck / finhist from raw, verified

This module makes the **construction of the Luck (Correia–Luck–Verner call report) and
finhist (OCC historical) data products a first-class, open-source, verified capability of
FreeNIC**: it produces Luck-equivalent and finhist-equivalent panels **from raw FreeNIC
data**, plus a validation harness that proves equivalence against the published datasets
cell-by-cell — the "perfect reverse engineer." Ships as FreeNIC **v1.1.0**.

The human specification is [`RECONSTRUCTION_SPEC.md`](RECONSTRUCTION_SPEC.md); its
machine-readable twin is [`variable_map.csv`](variable_map.csv) (loaded/validated by
`variable_map.py`).

---

## The honest derivability boundary (stated up front, enforced throughout)

*(verbatim from the campaign plan §0 — `FREENIC_11_RECONSTRUCTION_PLAN_20260715.md`; this
is the honesty contract for the whole module)*

| Era | What "from raw" can mean | Basis |
|---|---|---|
| **1976–2026** | TRUE independent re-derivation: build the Luck-schema panel from Fed-direct raw (Chicago Fed + FFIEC CDR in `call_report_filings`) and match their published values | `30_build_public_luck_panel.py` already hits **99.70% on 24/25 vars** vs Fed-direct |
| **1959Q4–1975Q4** | DERIVATION-LAYER re-derivation: their digitized raw (`call-reports-historical.dta`, the only machine source for this era) → their published/analysis panel, via an original open-source implementation of their documented method | We hold their own 04–07 do-files + the exact source .dta |
| **1863–1941 (finhist)** | Same: `historical-call.dta` (their OCR digitization) → published panel derivation; the OCR itself is **NOT-DERIVABLE** (physical archives) | finhist .dta + OCC label docs on disk |

No step ever fabricates a value; cells outside the boundary are classed **NOT-DERIVABLE**,
never imputed. The genuine 1942–1958 gap is kept absent, never synthetically filled.

---

## Citation / licensing posture (D3)

*(from `Technical/reconstruction_spec/LICENSE_POSTURE.md` §2b / §3; G-LIC verdict:
GREEN-with-conditions)*

Every module here is **original Python implementing CLV's documented methodology**, with
**per-function citations to their do-file loci** (e.g. a docstring reading
`implements 05 L66-77`). We do **not** redistribute their do-files — the QJE replication
kit (`qje-repkit.zip`) stays a **local input**; methods/ideas are not copyrightable and
re-implementing a documented methodology in original code infringes nothing. The
Dataverse deposit `doi:10.7910/DVN/Q22XR1` is **CC0 1.0**; the NY Fed modern
call-report content is redistributed under the **NY Fed Terms of Use** (attribution +
keep-source-URL + share-alike + no-endorsement, on that slice only). No OUP/QJE article
text is redistributed — cite only.

---

## Data provenance & citations (ship this block verbatim everywhere)

*(from `LICENSE_POSTURE.md` §4 — reuse in READMEs / codebooks / data package / site footer;
replace `[year]` with the retrieval year for the NY Fed slice, e.g. 2026)*

```text
DATA PROVENANCE & CITATIONS
---------------------------
This release reconstructs and redistributes data from the "Failing Banks" project by
Sergio Correia, Stephan Luck, and Emil Verner. Please cite:

Paper (methodology / dataset of record):
  Correia, Sergio, Stephan Luck, and Emil Verner. "Failing Banks." The Quarterly Journal of
  Economics 141, no. 1 (2026): 147-204. https://doi.org/10.1093/qje/qjaf044

Replication data (Harvard Dataverse, CC0 1.0):
  Correia, Sergio; Luck, Stephan; Verner, Emil, 2026, "Replication Data for: 'Failing Banks'",
  https://doi.org/10.7910/DVN/Q22XR1, Harvard Dataverse, V1.1. Licensed CC0 1.0.

Historical OCC call reports (1867-1904 subset), where used:
  Carlson, Mark, Sergio Correia, and Stephan Luck. 2022. "The Effects of Banking Competition on
  Growth and Financial Stability: Evidence from the National Banking Era." Journal of Political
  Economy 130 (2): 462-520.

Historical data portal:
  finhist.com - Historical Financial Data Project (Correia, Luck, Verner). https://finhist.com

Modern call reports (1959Q4-2025):
  Federal Reserve Bank of New York, "Balance Sheets and Income Statements of Commercial Banks:
  1959 through 2025." https://www.newyorkfed.org/research/banking_research/balance-sheets-income-statements
  Content from the New York Fed is used under the New York Fed Terms of Use
  (https://www.newyorkfed.org/privacy/termsofuse):
  "(c) [year] Federal Reserve Bank of New York. Content from the New York Fed subject to the
  Terms of Use at newyorkfed.org." No guarantee is made about the accuracy of the data; the
  New York Fed does not endorse this reconstruction, and derivative works herein are not
  attributed to the New York Fed.

LICENSES: Dataverse deposit doi:10.7910/DVN/Q22XR1 = CC0 1.0. NY Fed modern call-report content =
NY Fed Terms of Use (attribution + share-alike; not relicensed here). Our original code and
reconstruction outputs are the campaign's own contribution and do not redistribute the authors' code.
```

---

## Module layout

```
pipeline/reconstruction/
  __init__.py                   # package contract + exports
  README.md                     # this file
  RECONSTRUCTION_SPEC.md        # the human spec (added by R2)
  variable_map.csv              # machine-readable spec (shipped copy; see sync note in variable_map.py)
  variable_map.py               # loader + schema validator + scope filter
  entity_spine.py               # era-aware entity keys (shared lib)  [Batch 1]
  taxonomy.py                   # pre-registered divergence classifier [Batch 1]
  build_luck_equivalent.py      # 1976–2026 from Fed-direct raw        [Batch 3]
  build_luck_core.py            # 1959–1975 .dta -> published schema   [Batch 3]
  build_finhist_equivalent.py   # 1863–1941 historical-call.dta        [Batch 3]
  build_clv_analysis_panel.py   # optional combined analysis panel     [Batch 3]
  validate_reconstruction.py    # the cell-by-cell harness             [Batch 4]
  tests/                        # fast, fixture-based, warehouse-free   [Batch 1 +]
```

Numbered warehouse wrappers `50_reconstruct_luck.py` / `51_reconstruct_finhist.py` /
`52_validate_reconstruction.py` land in `Technical/freenic_ingestion/scripts/` (Batch 5)
and **import** this module — the repo is canonical, the scripts are thin shims.

## Batch-1 foundations (this batch — what the era builders share)

- **`variable_map.py`** — `load_variable_map()`, `validate_schema()`, `scoped()`,
  `confidence_counts()`, `assert_in_sync()`. The spec-dir CSV is the working canonical
  copy until v1.1.0 ships; the shipped copy here must be re-synced before release.
- **`entity_spine.py`** — the shared entity library, `SPEC-ANCHOR`-tagged to
  `RECONSTRUCTION_SPEC.md §6.1` for a mechanical Batch-3 refresh:
  - **HIST 1863–1941** — OCC charter. `hist_version`/`hist_entity_id` implement 04's
    transient `10*charter+version` id (`04 L14-18`); per the G-SPEC correction that id is
    dropped and the delivered panel keys on the charter (`hist_panel_key`), pooling a
    re-entering bank under one entity;
  - **MODL 1959–1975** — FDIC-cert keyed with the `-id_rssd` fallback + post-failure
    pseudo-id (`resolve_fdic_cert`, `drop_unkeyed`, `modern_bank_id`; implements `05 L53-81`);
  - **MODC 1976–2026** — RSSD-native (`modc_rssd_key`; `30_build` one-row-per rssd×period);
  - the **append-not-join** era rule + range-disjointness invariant (`assert_eras_disjoint`;
    `07 L11-12`, `05 L77`) and the `(id_rssd, period_end)` validation alignment key
    (`alignment_key`).
- **`taxonomy.py`** — `classify(published, built, units_last_digit)` →
  EXACT/ROUNDING/TOLERANCE/VINTAGE/METHOD-CHOICE/NOT-DERIVABLE/UNEXPLAINED, with the D2
  thresholds as **hard constants** (`ROUNDING_ULP_FACTOR=0.5`, `TOLERANCE_REL=1e-4`,
  gates 0.995 / 0.999 / 0.995, `UNEXPLAINED_FLOOR=0.001`) — **no tunable knobs**, so the
  harness cannot be tuned to pass.

## Runtime dependencies

`duckdb` + `pandas` (`pyarrow`/`numpy` via pandas) — matches the repo's existing
`requirements.txt`. All functions are pure over pandas DataFrames / DuckDB relations; **no
module here writes to or requires an attached warehouse.**

## Tests

`pytest pipeline/reconstruction/tests` — fast, fixture-based, no warehouse. Covers spine
key construction (receivership version bump, missing-cert `-id_rssd` rule, era-boundary
non-join / disjointness), the taxonomy classifier including the exact boundary values
(0.5 ULP, 1e-4 relative), and the variable_map loader/validator.
