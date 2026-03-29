# FR Y-14Q Instructions -- Chunk 029

## Schedule L -- Counterparty (continued): Sub-schedules L.2, L.3, L.4

### L.2 -- EE Profile by Counterparty

Note that unique identifiers and names reported in this sub-schedule must be consistent across all sub-schedules L.1, L.2, L.3, and L.5 on Consolidated/Parent Counterparty ID, Counterparty Legal Entity Identifier (LEI), Netting Set ID, and Sub-Netting Set ID, if applicable.

#### Column Instructions (L.2.a -- L.2.b)

**Rank (CACBM899):** Rank of consolidated/parent counterparty by unstressed CVA (L.2.a) or Federal Reserve Severely Adverse Scenario stressed CVA (L.2.b).

**Consolidated/Parent Counterparty Name (CACBM900):** Consolidated group/parent level name, alphabetically recognizable. Consistent across all sub-schedules L.1-L.5.

**Consolidated/Parent Counterparty ID (CACBM901):** Official LEI or unique alphanumeric identifier. Consistent across all sub-schedules L.1-L.5.

**Counterparty Legal Entity Name (CACB9017):** Unique counterparty legal entity name. Consistent across all sub-schedules L.1-L.5.

**Counterparty Legal Entity Identifier (LEI) (CACB9224):** Official LEI or unique identifier. Consistent across all sub-schedules L.1-L.5.

**Netting Set ID (CACBM902):** Unique identifier for netting set, mapping to ISDA master netting agreements. "NA" if not applicable.

**Sub-netting Set ID (CACBM903):** Unique identifier for sub-netting set if CVA calculated below netting set level. "NA" if not applicable.

**Counterparty Legal Entity Industry Code (CACBR620):** Four to six digit NAICS code (six digit for financial counterparties).

**Counterparty Legal Entity Country (CACBM905):** Country of domicile using ISO two-letter codes. "XX" for supranational entities.

**Counterparty Legal Entity Internal Rating (CACBM906):** Internal rating of counterparty legal entity. Use mean or median if multiple ratings for different netting sets.

**Counterparty Legal Entity External Rating (CACBM907):** External rating equivalent from NRSRO.

**Tenor bucket in years (CACBM928):** Time provided should be as granular as possible. Use years as the unit (e.g., 6 months = "0.5"). Tenor buckets are defined as the time between time t and time t-1. Typically EE is calculated at time t (the endpoint). The level of granularity should be at the level used to calculate CVA.

**Expected Exposure (EE) - BHC/IHC/SLHC specification (CACBP799):** The (unstressed) EE metric used to calculate CVA for each tenor bucket. Along each simulation path, exposure at time t should be non-negative (negatives set to 0 before calculating expected value). The EE reference point refers to the end-point of the time bucket. EE (unstressed) should be calculated using the BHC's/IHC's/SLHC's own specification.

**Marginal Probability of Default (PD) (CACBQ451):** Interpolated unilateral marginal PD for each time bucket between t and t-1. Typically equivalent to the difference between cumulative PDs. PDs should not be conditioned on the survival of the BHC/IHC/SLHC.

**Loss Given Default (LGD) (CVA) (CACBQ667):** Loss Given Default (1-Recovery Rate) used to calculate CVA.

**Discount factor (CACBR486):** Discount factor used to calculate unstressed CVA. Should be roughly equal to e^(-zt) or (1+z)^(-t).

**Stressed EE - FR scenario & FR specification (Severely Adverse - CACBR487):** Stressed EE under the FR specification with a 10 day margin period of risk (MPOR) for all collateralized counterparties. Exclude collection of additional collateral due to downgrade triggers.

**Stressed EE - BHC/IHC/SLHC scenario & specification (CACBR491):** Stressed EE under the BHC's/IHC's own specification.

**Stressed Marginal PD (Severely Adverse - CACBR492; BHC/IHC/SLHC - CACBR494):** Unilateral marginal PD associated with stressed spread. PDs should not be conditioned on survival.

**Stressed LGD (CVA) (Severely Adverse - CACBR495; BHC/IHC/SLHC - CACBR497):** LGD used to calculate CVA in the applicable stressed scenario.

**Stressed LGD (PD) (Severely Adverse - CACBR498; BHC/IHC/SLHC - CACBR500):** LGD used to calculate PD in the applicable stressed scenario.

**Stressed Discount Factor (Severely Adverse - CACBR523; BHC/IHC/SLHC - CACBR525):** Discount factor used to calculate CVA in the applicable stressed scenario.

---

### L.3 -- Credit Quality by Counterparty

Note that unique identifiers and names must be consistent across all sub-schedules and mergeable on Consolidated/Parent Counterparty ID, LEI, Netting Set ID, and Sub-Netting Set ID.

#### Column Instructions (L.3.a -- L.3.b)

**Rank (CACQM899):** Rank by unstressed CVA (L.3.a) or by Federal Reserve Severely Adverse Scenario stressed CVA (L.3.b).

**Consolidated/Parent Counterparty Name (CACQM900):** Consolidated group/parent level name. Consistent across L.1-L.5.

**Consolidated/Parent Counterparty ID (CACQM901):** Official LEI or unique identifier. Consistent across L.1-L.5.

**Counterparty Legal Entity Name (CACQ9017):** Unique legal entity name. Consistent across L.1-L.5.

**Counterparty Legal Entity Identifier (LEI) (CACQ9224):** Official LEI or unique identifier. Consistent across L.1-L.5.

**Netting Set ID (CACQM902):** Unique identifier mapping to ISDA master netting agreements. "NA" if not applicable.

**Sub-netting Set ID (CACQM903):** Unique identifier for sub-netting set. "NA" if not applicable.

**Counterparty Legal Entity Industry Code (CACQR620):** Four to six digit NAICS code (six digit for financial counterparties).

**Counterparty Legal Entity Country (CACQM905):** ISO two-letter country code. "XX" for supranational entities.

**Counterparty Legal Entity Internal Rating (CACQM906):** Internal rating. Use mean or median if multiple ratings.

**Counterparty Legal Entity External Rating (CACQM907):** External rating equivalent from NRSRO.

**Time period (CACQR501):** Date for which the CDS (or other input) applies. For grid pricing, enter only dates with market data available.

**Market spread (bps) (CACQR502):** Market value from CDS or proxy grid. Report as all-in-cost spread with upfront costs incorporated.

**Spread adjustment (bps) (CACQR503):** Amount and operator (e.g., "*" and "+") of adjustments. Blank if no add-on used.

**Spread (bps) used in CVA calculation (CACQR504):** Value used in CVA calculation. May be blank if market spread of single name or proxy used without adjustment.

**Stressed spreads (Severely Adverse - CACQR505; BHC/IHC/SLHC - CACQR507):** Stressed CDS spreads used in stressed CVA calculation.

**Mapping approach (CACQR508):** Either "Single name own" or "Proxy".

**Proxy mapping approach (CACQR509):** If not single name own, report one of: Single name-related party, Industry, Ratings class, Industry-rating, Industry-geography, Industry-rating-geography, Rating-geography, or Other. May be blank when mapping approach is Single name own.

**Proxy name (CACQR510):** Identify the specific proxy used.

**Market input type (CACQR511):** CDS spreads, Bond spreads, KMV-EDFs, or Other.

**Ticker / identifier (CACQR512):** Ticker number used (e.g., CDX IG AA, single name ticker).

**Report date (CACQR513):** Date of the market data.

**Source (CACQR514):** Source of market data (e.g., Bloomberg, Markit).

**Comments (CACQR515):** Any relevant comments.

---

### L.4 -- Aggregate and Top 10 CVA Sensitivities by Risk Factor

This schedule collects sensitivity information of aggregate asset-side CVA based on changes in underlying risk factors. A sensitivity refers to a 1 unit change in the risk factor, and a slide refers to a larger change. Report an increase in CVA as a positive figure. Reported figures should be gross of CVA hedges.

Sensitivities are collected in aggregate (across all CVA positions) and for the 10 consolidated counterparties with the largest sensitivities to a given risk factor. Report at the consolidated group/parent level, 10 entries per risk factor.

#### Aggregate CVA sensitivities by risk factor
The BHC/IHC/SLHC may provide their own values for slides. At least one slide must be consistent with the size of the shock under the FR scenario. All slides should be based on full revaluation (not linear scaling). At minimum, include significant positive and negative moves. For credit, basis point moves refer to absolute moves; percentage moves refer to relative moves.

#### Top 10 CVA sensitivities by risk factor
For each risk factor, report the change in CVA for each of the top 10 parent/consolidated counterparties most sensitive to a 1bp or 1% increase. Report as positive for CVA increase. Gross of CVA hedges.

#### Other material sensitivities
Material sensitivities are other large/important risk factors. Reported across all counterparties (no requirement to report top 10 for "other material sensitivity"). Label must clearly identify the risk factor.

#### Item Instructions (L.4.a -- L.4.b)

**Risk factor category (CACUR526):** Risk factor category (specified factors from report form plus other material sensitivities).

**Risk factor description (CACUW899):** Brief description of the risk factor.

**Consolidated/Parent Counterparty Name (CACQM900):** Consistent across L.1-L.5.

**Consolidated/Parent Counterparty ID (CACQM901):** Consistent across L.1-L.5.

**Risk factor slide (CACUR527):** Movement of the risk factor.

**Risk sensitivity (CACUR528):** Change in asset-side CVA for a given change in the underlying risk factor, gross of CVA hedges.
