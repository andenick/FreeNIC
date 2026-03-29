# FR Y-14Q Instructions -- Chunk 028

## Schedule L -- Counterparty (continued): Sub-schedule Instructions L.1.a through L.1.f

### L.1.a -- Top consolidated/parent counterparties comprising 95% of firm unstressed CVA, ranked by unstressed CVA

Report information for the top consolidated/parent counterparties that comprise 95% of firm total unstressed CVA, at the counterparty legal entity level.

### L.1.b -- Top consolidated/parent counterparties comprising 95% of firm stressed CVA, ranked by Federal Reserve Severely Adverse Scenario stressed CVA for the CCAR quarter

Report information for the top consolidated/parent counterparties that comprise 95% of firm total stressed CVA under the Federal Reserve Severely Adverse Scenario, at the counterparty legal entity level. If a counterparty level entity is already reported on sub-schedule L.1.a, do not duplicate information for that counterparty. Report only any additional counterparty legal entities needed to arrive at the counterparties that comprise Top 95% of stressed CVA. Counterparty legal entities should only be reported once across sub-schedules L.1.a-b.

### Item Instructions (L.1.a -- L.1.b)

**Rank (CACVM899):** Report the rank of the consolidated/parent counterparty as ordered by unstressed CVA (for L.1.a) and by the Federal Reserve Severely Adverse Scenario stressed CVA (for L.1.b).

**Consolidated/Parent Counterparty Name (CACVM900):** Report the consolidated group/parent level counterparty name that is alphabetically recognizable rather than an alphanumeric code. Must be consistent across all sub-schedules L.1-L.5.

**Consolidated/Parent Counterparty ID (CACVM901):** Report the official globally recognized legal entity identifier (LEI). If unavailable, report a unique alphanumeric identifier. Must be unique and consistent across all sub-schedules L.1-L.5.

**Counterparty Legal Entity Name (CACV9017):** Report the unique counterparty legal entity name. Must be consistent across all sub-schedules L.1-L.5.

**Counterparty Legal Entity Identifier (LEI) (CACV9224):** Report the official globally recognized LEI of the counterparty legal entity. Must be unique and consistent across all sub-schedules L.1-L.5.

**Netting Set ID (CACVM902):** Report the unique identifier assigned to the netting set. Netting sets should map to ISDA master netting agreements. If not applicable, populate with "NA". Must be consistent across all sub-schedules L.1-L.5.

**Sub-netting Set ID (CACVM903):** Report the unique identifier assigned to the sub-netting set, if a firm calculates CVA below the netting set level. If not applicable, populate with "NA". Must be consistent across all sub-schedules L.1-L.5.

**Counterparty Legal Entity Industry Code (CACVR620):** Report the four to six digit NAICS code. Six digit code required for all financial counterparties. If NAICS unavailable, report GICS; if neither, report SIC.

**Counterparty Legal Entity Country (CACVM905):** Report the country of domicile using ISO two-letter codes. For supranational entities report "XX."

**Counterparty Legal Entity Internal Rating (CACVM906):** Report the BHC's/IHC's/SLHC's internal rating. If multiple ratings exist for different netting sets, use mean or median. Every counterparty must have only one CDS spread associated with it.

**Counterparty Legal Entity External Rating (CACVM907):** Report the external rating equivalent to the internal rating. Provide an external rating scale from an NRSRO.

**Gross Current Exposure (Gross CE) (CACVM908):** Pre-collateral exposure after bilateral counterparty netting. Report when fair value is positive; report zero when negative or zero. Report only for derivatives transactions (leave blank for fair-valued SFTs).

**Stressed Gross CE (Severely Adverse - CACVM909; BHC/IHC/SLHC - CACVM911):** Full revaluation of Gross CE under applicable stressed conditions.

**Net Current Exposure (Net CE) (CACVM912):** Sum of positive Gross CE less value of collateral posted by counterparty. Report after counterparty netting and after collateral. Reflect any excess collateral posted by BHC/IHC/SLHC. Do not reflect collateral called but not yet exchanged. Report for both derivatives and fair-valued SFTs.

**Stressed Net CE (Severely Adverse - CACVM913; BHC/IHC/SLHC - CACVM915):** Full revaluation of Net CE under applicable stressed conditions. Hold collateral constant; assume no additional collection; apply stressed conditions to collateral.

**Total Notional (CACVJF39):** Gross notional amount of all derivatives positions. Include sum of positive and negative market value contracts. For multi-leg derivatives, report maximum notional across all legs.

**New Notional During Quarter (CACVJD56):** Gross notional amount of derivatives originated during the reporting quarter. Exclude positions originated and settled in same period. Include live compression trades at reporting date.

**Weighted Average Maturity (CACVJD57):** Average time to maturity in years, weighted by gross notional. For OET trades, do not take into account early termination. For MET trades, take into account early termination features.

**Position Mark-to-Market (CACVJD58):** Net mark-to-market of all derivatives positions, not including collateral. Can be positive or negative.

**Total Net Collateral (CACVJD59):** Net mark-to-market value of all collateral, computed as amount received less amount posted (net received = positive).

**CVA (CACVM916):** Balance of all CVA, gross of hedges, for asset-side, unilateral CVA. Report as positive value. Different from "Net CVA" (CVA less DVA). Default risk of counterparty should not be conditioned on survival of reporting institution. CVA hedges should be reported separately in FR Y-14Q Trading Schedule F.

**Stressed CVA (Severely Adverse - CACVM917; BHC/IHC/SLHC - CACVM921):** Full revaluation of asset-side CVA incorporating stressed exposure, PD, and LGD.

**Credit Support Annex (CSA) in place? (CACVM922):** "Y" or "N" indicating whether at least one netting set has a legally enforceable collateral agreement.

**% Gross Current Exposure (Gross CE) with CSAs (CACVM923):** Percentage of Gross CE with legally enforceable collateral agreements.

**Downgrade trigger modeled? (CACVM924):** Per existing guidance, report this field NA.

**Single Name Credit Hedges (CACVM925):** Net notional amount of single name CDS hedges on counterparty default. Net bought protection = negative; net sold protection = positive.

---

### L.1.e -- Aggregate CVA Data by Ratings and Collateralization

This sub-schedule is comprised of four tables:
- **e.1** Aggregate CVA data: aggregate line items should equal sum of e.2 + e.3 + e.4
- **e.2** Additional/Offline CVA Reserves (sorted by internal rating, as applicable)
- **e.3** Collateralized netting sets sorted by internal rating (CSA agreement in place)
- **e.4** Uncollateralized netting sets sorted by internal rating (no CSA agreement)

The internal ratings categories reported on L.1.e must be the same as those reported on L.5.3.

**Item Instructions for L.1.e:**

**Internal Rating (CACLM906):** Same definition as CACVM906.

**External Rating (CACLM907):** External rating equivalent from NRSRO.

**Gross CE excluding CCPs (CACVM919):** Pre-collateral exposure after bilateral netting. Derivatives only, not fair-valued SFTs.

**Gross CE to CCPs (CACVM920):** Gross CE from transactions through CCPs.

**Stressed Gross CE excluding CCPs (Severely Adverse - CACLR485):** Full revaluation under stressed conditions.

**Stressed Gross CE to CCPs (Severely Adverse - CACLR489):** Full revaluation under stressed conditions.

**Stressed Gross CE BHC/IHC/SLHC scenario (CACLM911):** Full revaluation under stressed conditions.

**Net CE excluding CCPs (CACLR517):** Sum of positive Gross CE less collateral. Both derivatives and fair-valued SFTs included.

**Net CE to CCPs (CACLR518):** Net CE from transactions through CCPs.

**Stressed Net CE excluding CCPs (Severely Adverse - CACLR519):** Full revaluation under stressed conditions. Hold collateral constant.

**Stressed Net CE to CCPs (Severely Adverse - CACLR520):** Full revaluation under stressed conditions.

**Stressed Net CE BHC/IHC/SLHC scenario (CACLM915):** Full revaluation under stressed conditions.

**CVA (CACLM916):** Asset-side, unilateral CVA, gross of hedges, as positive value.

**Stressed CVA (Severely Adverse - CACLM917; BHC/IHC/SLHC - CACLM921):** Full revaluation incorporating stressed exposure, PD, and LGD.

**Single Name Credit Hedges (CACLM925):** Net notional of single name CDS hedges. Bought protection = negative; sold protection = positive.

**Additional/offline CVA reserves:** Risks Not in CVA, Wrong Way Risk, Offline Reserves, or other non-standard add-ons not included in L.2 or L.3. Must be reported into six categories:
- a) Model/infrastructure limitations
- b) Trades not captured
- b.1) Fair-valued Securities Financing Transactions (SFT)
- c) Offline reserves (held at discretion of Finance)
- d) Funding Valuation Adjustment (FVA) (if applicable)
- e) Other

**Collateralized counterparty:** Counterparty with at least one netting set with a legally enforceable collateral agreement in place.

**Collateralized netting set:** Netting sets with a CSA agreement in place and for which only financial collateral applies.

---

### L.1.f -- Residual counterparty summary metrics by collateralization, industry, region, and ratings

Report information for counterparty legal entities not already reported on sub-schedules L.1.a or L.1.b.

Two tables:
- f.1 Residual counterparties: collateralized netting sets (CSA agreement in place)
- f.2 Residual counterparties: uncollateralized netting sets

**Item Instructions:**

**Industry Code (CACLR620):** Four to six digit NAICS code (six digit for financial counterparties).

**Region (CACLH167):** Regional groupings per FR Y-14Q Trading Schedule F:
- Advanced Economies
- Emerging Europe
- Latin America & Caribbean
- Asia Ex-Japan
- Middle East & North Africa
- Sub-Saharan Africa

All remaining fields (Internal Rating, External Rating, Gross CE excl/to CCPs, Stressed Gross CE, Net CE excl/to CCPs, Stressed Net CE, CVA, Stressed CVA, Single Name Credit Hedges) follow the same definitions as L.1.e.
