# FR Y-14Q Instructions - Chunk 013
## Schedule F - Trading (continued): F.22 through F.25

---

## F.22 -- IDR-Corporate Credit

### General

See the *Regional Groupings* tab for the definition of Advanced Economies. Please consider Emerging Markets to encompass all countries not defined as Advanced Economies on the *Regional Groupings* worksheet.

1. The exposures in this tab should include only corporate credit. Other structured products reported on the Securitized Products worksheet (i.e. RMBS, CMBS or ABS) should not be reported on this tab.

2. The exposures in Tables A (Single Name Products), B (Index Products) and C (Other/Unspecified) should be exposures without any decomposition/unbundling of index or structured products.

3. The single name positions in Table A should include only actual single name products such as bonds, loans, and single name CDS.

4. Table B should include all index, index tranche and bespoke products. Emerging Market CDX and iTraxx exposures should be reported in the CDX Other and iTraxx Other categories, respectively. Sovereign CDS index exposures should not be included here, they must be decomposed by country and entered on the Sovereign Credit worksheet.

5. Exposures on Tables A through C should be reported only once (with no double counting).

6. Long and short exposures should be reported from the perspective of long or short the underlying credit -- i.e. positions for which a default in the underlying credit would cause a loss are considered long and should be reported with positive sign while positions that would incur gains on default are considered short and should be reported with negative sign. To further illustrate, note that the following are considered long positions:
   - sold protection in a CDS
   - sold Put option on a bond
   - bought Call option on a bond
   - sold Payer CDS index option
   - bought Receiver CDS index option

7. The exposures to be reported in each of the long and short categories should be netted against like exposures as described below:

   Firms should conduct all netting at the firm-wide level, not at the business or desk level. MV-longs, and MV-shorts, should be the sum of exposures to obligors (issuers) to which the firm has net MV long, and net MV short, positions respectively. To arrive at the net Long or net Short position, exposures to the same obligor should be netted (if JTD exposures to that obligor are offsetting) before aggregation across obligors.

   Notional-long, and Notional-short, should be the corresponding sum of the notional values of obligors with net long MV, and net short MV, respectively.

   For index products, for the exact same index family (e.g. NA IG), series (e.g. series 18), and tranche (e.g. 0-3%), positions should be netted across maturities.

   Different tranches of the same index or series may not be netted, different series of the same index may not be netted, and different index families may not be netted.

8. Market value should be reported in bond equivalent terms. The objective of the reported market value is to reflect the maximum potential jump-to-default impact of underlying obligor defaults (before considering any recovery).

   CDS MV should be reported as the notional amount plus the mark-to-market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond), i.e. report as follows (with |*| representing absolute value):

   MV = MTM + S * |Notional|, where S=1 for sold protection and S=-1 for bought protection.

   For example $100M bought CDS protection with positive MTM of $5M should contribute MV=-$95M to MV-shorts.

   Options should also be reported on the basis of bond equivalent market value, and not in terms of the MTM of the option.

   Bond options in particular should be reported as specified below in (i), or if that is not feasible then as in the alternative method (ii). In both cases, the long/short reporting should be on the basis of long or short the underlying credit exposure (i.e. not bought vs. sold option).

   (i) MV of exposure for an Option on a bond should be reported as follows:
   - Sold Put: MV = Strike - |Option MTM|
   - Bought Put: MV = |Option MTM| - Strike
   - Sold Call: MV = -|Option MTM|
   - Bought Call: MV = |Option MTM|

   Where the strike is in terms of the bond price (not the yield). Note that for bond call options, notional should be reported as zero.

   (ii) As an alternative, if the firm's data systems cannot report as above, then the firm should report using the delta adjusted notional plus the option value.

   Index options should have MV of exposure reported as follows:
   - Sold Payer: MV = |Notional| - |Option MTM|
   - Bought Payer: MV = |Option MTM| - |Notional|
   - Sold Receiver: MV = -|Option MTM|
   - Bought Receiver: MV = |Option MTM|

9. If unable to separate into emerging markets and advanced economies, then report under corporate credit advanced economies. If unable to report separately, clearly indicate this in supporting documentation.

10. Table D should include detail on any issuer represented in Table A to which aggregate single name product exposures exceed $50M (in absolute value terms, based on bond equivalent market value). Indicate which of these issuers feature as constituents in index positions currently held and provide the RED Code for these issuers if available.

11. Table E should include the remaining positions in Table A (issuers smaller than $50M) that are not included in Table D.

12. Use Table F to provide a breakout by series of the index positions represented in Table B. Payer Index Options should be bucketed by moneyness based on (1 - strike spread / index spread) in percentage points. For CDX IG, CDX HY, iTraxx Main and iTraxx XO report aggregate bond equivalent market value and notional for all series to which exposure is non-zero (following the same positive/negative number convention for long/short positions utilized in Table B). For CDX Other, iTraxx Other and Loan index exposures, similarly detail exposure by series but only in respect of indices to which the gross market value of positions exceeds $100M.

13. In Table G for each index/seniority bucket populated on the Credit Correlation tab (for example, CDX IG/Equity) report the number of bespoke tranche products represented along with the average credit spread of the constituents they reference (standardizing to the 5-year tenor) as well as the average number of constituents per product.

---

## F.23 -- IDR-Jump to Default

### General

The decomposition of index and structured products into single name equivalents should be done on a JTD equivalent basis - i.e. the difference in MV of the structured security assuming that the single name does and does not default, with zero recovery.

Please enter information for any issuer for which the jump to default (using the firm's standard recovery assumptions) exceeds $25MM.

Exposures listed in this table should include debt and equity related instruments, for corporate exposures, including exposures to standalone nonpublic companies. Exposures to Sovereigns, Agencies, Munis, ARS, and counterparty credit exposures from derivative contracts should not be reported here.

Insert additional rows if needed. Unused rows should be left blank.

The Totals section at the bottom should be the firm-wide total JTD by rating for all issuers, not just those listed here.

Exposures should include unbundled exposures from index and structured products if such unbundling is used in the reporting firm's exposures measurement or internal models.

If unbundled exposures are included, clearly indicate this in the firm's supporting documentation.

---

## F.24 -- Private Equity

### General

This worksheet is meant to capture the carry value of Private Equity investments across regions and **aggregated** by GICS code. Report the carry value of Private Equity investments reported at fair value and NAV in section (A). Report the carry value of Private Equity investments measured using accounting methods other than fair value, i.e. cost or equity methods, in section (B).

Real estate, minority interest in hedge funds, fund seed capital, infrastructure funds and investments where the GICS code is not clearly defined should be entered in the separate sections below the Data by GICS code section.

The row labelled "Unspecified Sector/Industry" is meant to capture the carry value of investments not easily categorized into one of the specified industries and sectors, investments in several sectors and for which there is insufficient detail to break out the carry value of the holdings into component sectors. An example would be a fund that invests in several sectors and for which there is insufficient detail to break out the carry value of the holdings into component sectors.

Report non-tax oriented private equity investments in affordable housing that qualify as public welfare investments (PWI) only in the "Affordable Housing PWI" line items provided (for both funded exposures and unfunded commitments). Do not include such positions in any non-PWI line items, to avoid double counting.

Tax oriented PWI should not be included anywhere on F.24-Private Equity (though note that if held at fair value, such investments are reportable in the Tax Credits section of F.25-Other Fair Value Assets).

### Unfunded Commitments

All unfunded commitment balances are expected to be included, regardless of accounting and regulatory approaches used by the firms. This applies whether the institution holds a limited or general partner position.

Report unfunded commitments to affordable housing PE investments qualifying as PWI, in the Affordable Housing PWI line item provided only.

### Regional Definitions

- **Western Europe**: Austria, Belgium, France, Germany, Greece, Ireland, Italy, Luxembourg, Monaco, Netherlands, Portugal, Spain, Sweden, Switzerland, UK.
- **Other Developed Markets**: All "Advanced Economies" defined on the *Regional Groupings* worksheet, excluding those in Western Europe defined above.
- **Emerging Markets**: All other countries.
- **Unspecified Geography**: Use in cases where current systems do not allow for the geographical source to be easily identified.

---

## F.25 -- Other Fair Value Assets

### General

This worksheet is meant to capture the fair value of investments other than private equity which are subject to fair-value accounting **aggregated** by GICS code.

These entries should be broken out into whether they are equity or debt instruments and whether they are US-based or not.

Investments where the sector/industry is not clearly defined should be entered on the Unspecified Sector/Industry line.

Tax credit investment information should be entered in the separate Tax Credits section below the Data by NAICS code section.

### Definition of Other Fair Value Assets

Please see the general instructions for this schedule.

### BOLI, COLI, and Stable Value Wraps

The maximum instantaneous (post-shock) amount receivable under wrapped BOLI/COLI policies owned (directly or indirectly through the insurance carrier) by BHCs and IHC should be entered on the row labeled "BOLI, COLI and Stable Value Wraps" in the column for US Debt.

Similarly, the maximum instantaneous (post-shock) amount payable under wraps written by BHCs and IHCs should be entered in the same cell. These should be entered as a negative asset (i.e. a negative fair value).

Firms that have a combination of unwrapped separate account COLI/BOLI, written stable value wraps and purchased stable value wraps should net the respective entries and enter them in the same cell.

In no case should exposures related to BOLI, COLI or stable value wraps on these policies be entered anywhere else in this schedule.
