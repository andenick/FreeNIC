# FR Y-14Q Instructions -- Chunk 030

## Schedule L -- Counterparty (continued): Sub-schedule L.5 and Schedule M -- Balances

### L.5 -- Derivatives and Securities Financing Transactions (SFT) Profile

This sub-schedule collects information about G-7 sovereigns, CCPs, and IHC's affiliates and other top counterparties associated with SFTs and/or derivative positions at the level of position netting.

**G7 includes:** Canada, France, Germany, Italy, Japan, the United Kingdom, and the United States (sovereign exposure per 12 CFR 217, section .2).

**CCP includes:** Both qualifying central counterparties (QCCP) and non-QCCP (per 12 CFR 217, section .2).

**IHC affiliate:** Parent company of the counterparty and any firm consolidated with the counterparty under applicable accounting standards (US GAAP or IFRS).

#### Ranking Methodologies

**For non-CCAR (unstressed) quarter:** All G-7 sovereigns, CCPs, and IHC's affiliates plus Top 25 non-G7/non-CCP/IHC's non-affiliate counterparties ranked by:
1. Total Net CE (excluding client cleared derivatives)
2. Total Net CE (limited to client cleared derivatives)

**For as-of-CCAR (stressed) quarter:** Same structure but ranked by:
1. Total Stressed Net CE under Federal Reserve Severely Adverse Scenario (excluding client cleared derivatives)
2. Total Stressed Net CE (limited to client cleared derivatives)

If a counterparty is captured in both ranking methodologies (1 & 2), report only under methodology 1.

For derivatives, exposure amounts should be calculated using the same netting methodology as sub-schedules L.1a-L.1d. For SFTs, mark-to-market amounts (posted and received) should be reported as positive values. Purchased single-name CDS hedge notional = negative; sold = positive.

In cases of specific wrong-way risk in collateral (counterparty and issuer are the same entity), the received collateral benefit should be assumed zero for Net CE and Stressed Net CE.

#### Netting Agreement Reporting
Report for each netting agreement, even if Net CE is zero. Where no bilateral close-out netting agreement exists, aggregate and report as a single record with Legal Enforceability = "N", Agreement Type = "None", and Netting Set ID = "NA". When aggregating without netting, only aggregate positive MtM amounts. For positions with non-enforceable agreements, treat as no legal agreement for exposure reporting.

---

### L.5.1 -- Derivative and SFT information by counterparty legal entity and netting set/agreement

**Column Instructions:**

**Rank Methodology (CACNJD60):** Allowable entries: 1, 2, QCCP, NQCCP, G7, AF, and NA.

**Rank (CACNM899):** Rank per the indicated methodology. For CCPs: "QCCP"/"NQCCP"; G7 sovereigns: "G7"; IHC affiliates: "AF".

**Consolidated/Parent Counterparty Name (CACNM900):** Alphabetically recognizable name. Consistent across L.1-L.5.

**Consolidated/Parent Counterparty ID (CACNM901):** LEI or unique identifier. Consistent across L.1-L.5.

**Counterparty Legal Entity Name (CACN9017):** Name of the legal entity with whom the netting agreement was executed.

**Counterparty Legal Entity Identifier (LEI) (CACNR621):** Official LEI or unique identifier.

**Netting Set ID (CACNM902):** Maps to ISDA master netting agreements. "NA" if not applicable.

**Counterparty Legal Entity Industry Code (CACNR620):** Four to six digit NAICS code (six digit for financial).

**Counterparty Legal Entity Country (CACNM905):** ISO two-letter country code. "XX" for supranational.

**Counterparty Legal Entity Internal Rating (CACNM906):** Internal rating. Mean or median if multiple.

**Counterparty Legal Entity External Rating (CACNM907):** NRSRO equivalent of internal rating.

**Agreement Type (CACNR529):** Allowable entries for SFTs: "SFT Repo", "SFT Sec Lending", "SFT Cross-product". For derivatives with CSA: "Derivatives 1-way CSA", "Derivatives 2-way SCSA", "Derivatives 2-way old CSA", "Derivatives Centrally Cleared". Without CSA: "Derivatives no CSA". Cross-product: "SFT Derivatives Cross-product". No agreement: "None". Other: "Other".

**Agreement Role (CACNR530):** For SFTs: "Principal", "Agent", or "Client". For derivatives (clearing member with client exposure): "Principal", "Agent", or "NA".

**Legal Enforceability (CACNR534):** "Y" or "N". No close-out netting agreement = "N".

**Initial Margin (CACSR551):** Net amount of initial margin posted by counterparty (considering bankruptcy remote status). Report aggregate MtM value of cash and securities. Only actually exchanged margin.

**Non-Cash Collateral Type (CACSR552):** "U.S. Debt", "Non-U.S. Sovereign Debt", "Investment Grade Corporate Debt", "Public Equity", "Public Convertibles", or "Other" (comma separated if multiple).

**Excess Variation Margin (for CCPs) (CACSR553):** Excess variation margin posted to CCP (not in bankruptcy remote account).

**Default Fund (for CCPs) (CACSR554):** Required default fund contribution. Must be reported for all CCPs including those with no active trades.

**Threshold CP (CACSR555):** Threshold amount for the counterparty at netting set level.

**Threshold BHC/IHC/SLHC (CACSR556):** Threshold amount for the reporting entity.

**Minimum Transfer Amount CP (CACSR557):** Minimum transfer to counterparty (USD equivalent).

**Minimum Transfer Amount BHC/IHC/SLHC (CACSR558):** Minimum transfer to reporting entity (USD equivalent).

**Margining Frequency (CACSR559):** Frequency of margin calls in business days.

**CSA contractual features (non-vanilla) (CACSR560):** "Downgrade Trigger", "Break Clause - Mandatory", "Break Clause - Optional", "Other", or "NA" (comma separated if multiple).

**Wrong Way Risk Position (CACNR535):** "Specific", "General", or "None".

**Total Net Current Exposure (Net CE) (Unstressed - CACNR550):** Total net current exposure at legal-entity level. Reported once per legal entity, not repeated across Netting Set IDs.

**Total Stressed Net Current Exposure (Net CE) (Severely Adverse - CACNR536):** CCAR as-of date only. Full revaluation under FR stressed market. Reported once at legal entity level.

**Net CE SFTs (CACNM912):** Current exposure for the netting set for SFTs.

**Stressed Net CE SFTs (Severely Adverse - CACNR538):** Full revaluation for SFTs under FR stressed market.

**Net CE Derivatives (CACSJF40):** Current exposure for the netting set for derivatives.

**Stressed Net CE Derivatives (Severely Adverse - CACSR564):** Full revaluation under FR stressed market.

**Unstressed Mark-to-Market (Derivatives) (CACSR566):** MtM of derivative positions, not including collateral, including netting where legally binding. Can be positive or negative. Aggregate of positive amounts should equal Gross CE on L.1a-d.

**Unstressed MtM Posted (SFTs) (CACNR544):** Gross cumulative MtM of cash and assets posted. Reported as positive.

**Unstressed MtM Received (SFTs) (CACNR545):** Gross cumulative MtM of cash and assets received. Reported as positive.

**Stressed MtM (Derivatives) (Severely Adverse - CACSR567):** Full revaluation under global market shock scenarios.

**Stressed MtM Posted (SFTs) (Severely Adverse - CACNR540):** Full revaluation of posted assets. Positive value.

**Stressed MtM Received (SFTs) (Severely Adverse - CACNR542):** Full revaluation of received assets. Positive value.

**Unstressed MtM Cash Collateral (Derivatives):** Net cash collateral by currency:
- USD (CACSJF43), EUR (CACSJF44), GBP (CACSJF45), JPY (CACSJF46), Other (CACSJF47)

**Total Unstressed MtM Collateral (Derivatives) (CACSR575):** Net MtM of all eligible financial collateral.

**Stressed MtM Cash Collateral (Derivatives) (Severely Adverse):** USD (CACSJF48), EUR (CACSJF49), GBP (CACSJF50), JPY (CACSJF51), Other (CACSJF52).

**Total Stressed MtM Collateral (Derivatives) (Severely Adverse - CACSR578):** All collateral revalued under stressed conditions.

**CDS Reference Entity Type (CACNR546):** "CP Legal Entity", "CP Parent", or "Proxy".

**5Y CDS Spread (bp) (CACNR547):** Five-year CDS spread for the reference entity.

**Wrong Way Risk Hedge (CACSR583):** "Y" or "N" indicating if CDS hedges are wrong-way risk positions.

**CDS Hedge Notional (CACSR584):** Net notional of eligible single-name and non-tranched index credit derivatives. Purchased = negative; sold = positive.

**Stressed CVA (Severely Adverse - CACSR590):** CVA evaluated under supervisory global market shock scenarios.

---

### L.5.2 -- SFT assets posted and received by counterparty legal entity and netting set/agreement and asset category

Information reported at the level of netting agreements. Must correspond to netting agreements in L.5.1.

**Asset Categories (by sub-category with Unstressed Posted/Received and Stressed Posted/Received):**

**Central Debt** (sovereign or GSE obligations, excluding inflation-indexed): United States, Germany, United Kingdom & France, Other Eurozone, Japan, Other

**Equity** (publicly traded and privately issued): United States, Canada, United Kingdom, Eurozone, Other Economies

**Corporate Bonds -- Advanced Economies** (non-sovereign debt, excluding commercial paper): Investment Grade (IG), Sub-Investment Grade (Sub-IG)

**Corporate Bonds -- Other Economies** (non-advanced economy issuers): Investment Grade (IG), Sub-Investment Grade (Sub-IG)

**Exchange-Traded Funds** (ETF equity shares): Equity, Fixed Income

**U.S. Agency MBS/CMBS** (agency/GSE issued): Pass-throughs, Other

**Non-Agency RMBS/ABS/CMBS** (non-agency issued): Investment Grade (IG), Sub-Investment Grade (Sub-IG)

**Cash** (any currency): USD, EUR, GBP, JPY, Other

**Other** (all other asset types): Inflation-Indexed Securities, Commercial Paper, Municipal Bonds, Other

---

### L.5.3 -- Aggregate SFTs by Internal Rating

Information reported for all counterparties grouped by internal rating, one line per rating.

**Internal Rating (CACNM906):** Internal rating associated with the group of counterparties.

**External Rating (CACNM907):** External rating equivalent from NRSRO.

**Net CE (CACNM912):** Aggregate Net CE for the rating bucket.

**Stressed Net CE (Severely Adverse - CACNFD73; BHC/IHC/SLHC - CACNFD75):** Full revaluation under stressed conditions.

**Asset Categories (by Repo Posted/Received and Sec. Lending Posted/Received):**
- US Treasury & Agency
- Agency MBS
- Equities
- Corporate Bonds
- Non-Agency (ABS, RMBS)
- Sovereigns (non-US)
- Other (excludes cash)
- Cash
- Indemnified Securities Lent (Notional Balance)
- Indemnified Cash Collateral Reinvestment (Notional Balance)

---

### L.5.4 -- Derivative position detail by counterparty legal entity and netting set/agreement and asset category

Report for all CCPs, G-7 sovereign countries, and top 25 counterparties with derivative positions.

**Derivative Types (Unstressed MtM and Stressed MtM):**

| Derivative Type | Unstressed MtM | Stressed MtM (Severely Adverse) |
|----------------|---------------|-------------------------------|
| Vanilla Interest Rate | CACSR592 | CACSR606 |
| Vanilla FX | CACSR593 | CACSR607 |
| Vanilla Commodity (Cash) | CACSR594 | CACSR608 |
| Vanilla Credit | CACSR595 | CACSR609 |
| Vanilla Equity | CACSR596 | CACSR610 |
| Structured Interest Rate | CACSR597 | CACSR611 |
| Flow Exotic and Structured FX | CACSR598 | CACSR612 |
| Other Cash & Physical Commodity | CACSR599 | CACSR613 |
| Other (Single Name) Credit | CACSR600 | CACSR614 |
| Structured (Multi-Name) Credit | CACSR601 | CACSR615 |
| Exotic Equity | CACSR602 | CACSR616 |
| Hybrids | CACSR603 | CACSR617 |
| Structured Products (MBS, ABS, TBAs) | CACSR604 | CACSR618 |
| Other | CACSR605 | CACSR655 |

For derivative contracts with optionality, "vanilla" means American or European style with no additional contract features. All others are classified as "structured" or "exotic." Contracts without optionality are "vanilla."

---

## Schedule M -- Balances

### Schedule M.1 -- Quarter-end Balances

For each line item, report all loans and leases held for investment (HFI) or held for sale (HFS). Include the fair value of FVO loans.

**Columns:**
- **Column A:** Loans HFI at amortized cost in domestic offices
- **Column B:** Loans HFS or FVO in domestic offices
- **Column C:** Loans HFI at amortized cost in international offices
- **Column D:** Loans HFS or FVO in international offices

Report all dollar amounts in millions. Balances should be consistent with FR Y-9C Schedule HC-C, except PPP loan balances should be excluded.

### Line Items

**1.a.(1).(a) First mortgages:** First mortgage loans per FR Y-9C HC-C line 1.c.(2).(a). Do not include first lien closed-end home equity loans.

**1.a.(1).(b) First lien HELOANs:** First lien closed-end home equity loans per FR Y-9C HC-C line 1.c.(2).(a). Do not include first mortgages.

**1.a.(2).(a) Junior lien HELOANs:** Junior lien closed-end home equity loans per FR Y-9C HC-C line 1.c.(2).(b).

**1.a.(2).(b) HELOCs:** Home equity lines of credit per FR Y-9C HC-C line 1.c.(1).

**1.b.(1) Construction and land development:** CLD loans per FR Y-9C HC-C lines 1.a.(1) and 1.a.(2).

**1.b.(2) Multifamily real estate:** Multifamily loans per FR Y-9C HC-C line 1.d.

**1.b.(3).(a) Owner-occupied nonfarm nonresidential:** Per FR Y-9C HC-C line 1.e.(1).

**1.b.(3).(b) Non-owner-occupied nonfarm nonresidential:** Per FR Y-9C HC-C line 1.e.(2).

**1.c Secured by farmland:** Per FR Y-9C HC-C line 1.b.
