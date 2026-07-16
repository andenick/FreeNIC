# LICENSE_POSTURE.md — FreeNIC "luck_database" reconstruction

**Campaign:** FREENIC11_RECONSTRUCTION_20260715 · Gate: **G-LIC** (blocks Part S / publish, not the build)
**Author:** G-LIC gate agent · **Date:** 2026-07-15
**Evidence dir (verbatim snapshots):** `Inputs/luck_database/docs/licensing/`

> Rule of this gate: no interpretation without the quote. Every verdict below is anchored to
> verbatim terms fetched live on 2026-07-15 and saved as evidence snapshots. Any posture that is
> not *clearly* permitted by the quoted terms is marked **BLOCKED-pending-user**, never assumed.

---

## 1. Verbatim terms per source

### Source A — Harvard Dataverse deposit `doi:10.7910/DVN/Q22XR1`
*(this deposit IS the QJE "Failing Banks" Replication Kit — Emil Verner's research page labels the
DOI "Replication Kit"; the on-disk `qje-repkit.zip` is this deposit. Sources 1 and 2 of the gate
brief are therefore the SAME deposit.)*

- **Title:** "Replication Data for: 'Failing Banks'"
- **Authors:** Sergio Correia (FRB Richmond); Stephan Luck (FRB New York); Emil Verner (MIT)
- **Version / release:** V1.1, released 2026-01-16T01:45:17Z
- **License (VERBATIM, from Dataverse native API):**
  ```json
  "license": { "name": "CC0 1.0",
               "uri": "http://creativecommons.org/publicdomain/zero/1.0",
               "rightsIdentifier": "CC0-1.0",
               "rightsIdentifierScheme": "SPDX" }
  ```
- **Terms of Use / Terms of Access / restrictions / confidentiality:** **NONE present.** The API
  record contains no `termsOfUse`, `termsOfAccess`, `restrictions`, or `confidentialityDeclaration`
  fields; the file is unrestricted, no access request required.
- **CC0 1.0 substance:** a public-domain dedication — the depositors waive all copyright and related
  rights worldwide. Redistribution, derivatives, and commercial use are permitted **with no
  conditions**. (Citation is a scholarly courtesy, not a legal condition.)
- **Repkit internal docs (extracted from the zip):** `README.md` states, verbatim,
  `- [X] All data **are** publicly available.` No separate `LICENSE` file exists inside the zip; the
  governing license is the deposit-level CC0 1.0. Evidence: `repkit_README.md`, `repkit_README.txt`.
- Evidence: `dataverse_Q22XR1_metadata.json`.

> **NB — the QJE article vs. the data.** The *paper* ("Failing Banks," QJE, doi:10.1093/qje/qjaf044)
> is © Oxford University Press. This gate authorizes **no redistribution of the article or of OUP
> material** — only citation. The *data + code* in the Dataverse deposit are CC0. We never
> redistribute their do-files anyway (posture b, "D3").

### Source B — NY Fed dataset (modern call reports 1959Q4–2025; source of `luck_call_reports.parquet`)
Dataset page: `https://www.newyorkfed.org/research/banking_research/balance-sheets-income-statements`
- **Page Disclaimer (VERBATIM):**
  > "Each of the data sets provided here is covered by the Bank's standard terms-of-use policy.
  > While every effort has been made to eliminate the presence of mistakes, no guarantee is made
  > about the accuracy of the data."
- **Standard Terms of Use** (`https://www.newyorkfed.org/privacy/termsofuse`) — **Permissible Use,
  VERBATIM:**
  > "The New York Fed grants you a non-exclusive license, subject to the Terms, to use, copy, and
  > distribute Content for your personal or business purposes. You may:
  > • Access the Content, manually or through an automated process or device …
  > • Download, store, and use Content in any format or media,
  > • Copy and distribute the Content in any format or media, and
  > • Modify and create derivative works from the Content."
- **Conditions (VERBATIM, abridged to the operative clauses):**
  > (1) "When you copy or distribute any Content, you must include any copyright notice and other
  > source identifiers that the New York Fed includes with that Content. If the Content identifies
  > individual authors, you must also include that information … Otherwise, follow this format:
  > '© [year] Federal Reserve Bank of New York. Content from the New York Fed subject to the Terms
  > of Use at newyorkfed.org.'"
  > (2) "If Content includes a Website address from which the Content may be obtained without charge,
  > you may not remove that citation from the Content."
  > (3) "If you modify any of the Content, you must clearly label the modified Content … You may not
  > attribute any modifications or derivative works to the New York Fed."
  > (4) "You will avoid modifying the Content … in a manner that distorts or misrepresents the
  > Content … You may not modify the title or headline of the Content."
  > (5) "If you distribute the Content, you must make the Content available with the same permissions,
  > conditions, and restrictions set forth in these Terms. You may not impose more restrictive terms
  > or conditions on the Content." **(share-alike)**
  > (6) "You must not state or imply that the New York Fed endorses your use … The New York Fed does
  > not permit the use of its name … for any … commercial purpose."
  > (7) "You are responsible for your use, copying, and distribution of Content, including any errors,
  > modifications, or alterations you introduce …"
- **Net:** the NY Fed **explicitly grants copy + distribute + modify/derivative** rights, subject to
  attribution + keep-source-URL + label-modifications + no-distortion + **share-alike** + no-endorsement.
  This is permissive-with-conditions, not a bar to redistribution.
- Evidence: `nyfed_dataset_page.html`, `nyfed_termsofuse.html`.

### Source C — finhist.com (Historical Financial Data Project; historical OCC call reports 1863–1941)
- **Terms:** **NONE.** finhist.com and its historical-call page carry **no** Terms of Use, License,
  or redistribution statement. WebFetch, verbatim: *"No restrictions on usage or redistribution are
  stated."*
- **Citation request (VERBATIM):** 1863–1866 / 1905–1941 → cite Correia, Luck & Verner 2025 (QJE,
  doi:10.1093/qje/qjaf044); 1867–1904 → cite Carlson, Correia & Luck 2022 (JPE 130(2):462–520).
- **Redistribution basis we rely on:** the *same* historical OCC data is included in the **CC0**
  Dataverse deposit (Source A). Our basis for redistributing finhist-derived OCC tables is therefore
  **CC0 via Q22XR1**, with the finhist citation honored as courtesy. finhist imposes nothing to violate.
- Evidence: `finhist_terms_note.txt`.

---

## 2. The three posture verdicts

### (a) CONTINUED REDISTRIBUTION of `luck_call_reports.parquet` + finhist-derived OCC tables (live in v1.0.0)
**Verdict: GREEN-with-conditions.** Redistribution is unambiguously *permitted* by the verbatim terms;
the conditions are compliance items, not permission gates, so this is not BLOCKED.

- **finhist-derived OCC tables** → basis = **CC0 1.0** (Source A). Redistribution unconditional. **GREEN.**
- **`luck_call_reports.parquet` (modern 1959–2025)** → honest provenance = the NY Fed direct download
  (on-disk `README.html` is the NY Fed dataset README; source zips are the Jan-2026 NY Fed files).
  NY Fed Terms **explicitly permit copy + distribute**, so redistribution is permitted **provided the
  recorded basis carries these conditions**:
  1. Attribution string present: `© [year] Federal Reserve Bank of New York. Content from the New York
     Fed subject to the Terms of Use at newyorkfed.org.`
  2. The source URL (`newyorkfed.org/research/banking_research/balance-sheets-income-statements`) is
     retained in the release and not stripped.
  3. **Share-alike honored:** the NY-Fed-derived slice must be offered under the *same* NY Fed Terms —
     our release must **not** relicense that slice under any more-restrictive license.
  4. No implication of NY Fed endorsement; the accuracy disclaimer is carried through.
- **ACTION FOR PART S (verify before publish):** confirm v1.0.0's recorded provenance for the modern
  slice states the NY Fed basis + carries conditions 1–4. If v1.0.0 currently labels the modern data
  "public domain" or relicenses it under a single restrictive release license, that recorded basis is
  **inaccurate/non-compliant** and must be corrected to the NY-Fed-Terms basis before re-publish. The
  *permission* to redistribute is not in doubt; the *recorded basis* is the thing to fix.

### (b) Publishing ORIGINAL Python that implements their documented methodology, per-function citations to their do-files (D3: their code never redistributed)
**Verdict: GREEN (unconditional).** No source forbids derivative methodology implementations.
- The repkit is **CC0** — even the do-files carry no restriction; we could redistribute them but choose
  not to (D3). Methods/ideas are not copyrightable; re-implementing a documented methodology in original
  code infringes nothing.
- NY Fed Terms **explicitly permit** "Modify and create derivative works." finhist imposes nothing.
- Per-function citation to their do-files is honored as good practice; nothing here is a legal condition.
- (No terms forbidding derivative-methodology implementations were found — as expected, none exist.)

### (c) Publishing RECONSTRUCTED panels + cell-level reconciliation files (a derivative dataset from their data)
**Verdict: GREEN-with-conditions.** Derivative datasets are permitted by every source.
- Portion derived from the **CC0** Dataverse data (OCC historical + repkit inputs) → CC0 permits
  derivatives with **no** conditions. **GREEN.**
- Portion incorporating **NY Fed** modern Content → NY Fed Terms **explicitly permit** derivative works,
  subject to: **label** the reconstruction as ours (not NY Fed's) and do **not** attribute it to the NY
  Fed (condition 3); do **not distort** (condition 4); carry attribution + share-alike (conditions 1/2/5).
  Cell-level reconciliation files that quote small NY-Fed reference values for comparison are fair use /
  within the granted copy license; label them as reconciliation, not as NY Fed's publication.

**No posture is BLOCKED.** All three are clearly permitted by the verbatim terms.

---

## 3. G-LIC VERDICT

**GREEN-with-conditions.** Publish is authorized once the Part-S conditions are met — all of which are
attribution / share-alike / labeling items on the **NY-Fed-derived modern slice only**; everything
sourced from the CC0 Dataverse deposit (OCC historical + repkit) is unconditionally clear.

**Conditions to satisfy before Part S publish:**
1. Ship the mandatory citation block (§4) in every README / codebook / data package / site footer.
2. Carry the NY Fed attribution string + source URL + accuracy disclaimer for the modern-call-reports
   slice; do **not** relicense that slice under any more-restrictive terms (share-alike).
3. Do not attribute our reconstructions/derivatives to the NY Fed; label modifications clearly.
4. Verify v1.0.0's recorded provenance for `luck_call_reports.parquet` reflects the NY-Fed-Terms basis
   (correct it if it currently claims public-domain or a single restrictive release license).
5. Redistribute no OUP/QJE article text — cite only.

---

## 4. Mandatory citation block (reuse verbatim in READMEs / codebooks / site / data package)

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

*(Replace `[year]` with the retrieval year for the NY Fed slice, e.g. 2026.)*

---

## 5. Evidence snapshots on disk
- `dataverse_Q22XR1_metadata.json` — Dataverse native-API record (CC0 1.0 license object; no terms fields)
- `nyfed_dataset_page.html` — NY Fed dataset page (Disclaimer + "standard terms-of-use policy")
- `nyfed_termsofuse.html` — NY Fed standard Terms of Use (Permissible Use + Conditions, verbatim)
- `finhist_terms_note.txt` — finhist verbatim (no terms; citation request; CC0 cross-reference)
- `repkit_README.md`, `repkit_README.txt`, `repkit_README.html`, `repkit_requirements.txt` — extracted
  from `qje-repkit.zip` ("All data are publicly available"; no separate LICENSE file inside the zip)
