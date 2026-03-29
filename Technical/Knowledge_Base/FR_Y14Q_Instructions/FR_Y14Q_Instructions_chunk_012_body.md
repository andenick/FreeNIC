# FR Y-14Q Instructions - Chunk 012
## Schedule F - Trading (continued): F.16 through F.21

---

## F.16 -- Munis

### General

*MV for CDS should be reported as the notional amount plus the current MTM of the CDS, i.e. the bond-equivalent market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond).

The <B rating bucket for each section is broken into 3 categories - one for defaulted securities, one for non-defaulted securities, and one for "Default Status Unknown". The "Defaulted" category is meant to capture (1) defaulted positions and (2) for Bonds, Single Name CDS and Other/Unspecified categories, positions that do not have associated credit spread sensitivities, e.g. distressed positions or positions for which credit spread sensitivities are not available, regardless of rating. The "Default Status Unknown" row is meant to be used only when firms do not have the ability to categorize a given security as being defaulted or not.

Note that no credit widening sensitivities are requested for <B defaulted securities.

This worksheet should contain exposures to all Municipals, regardless of geography and currency.

Municipals refer to local government entities that do not have an explicit guarantee from the sovereign central government. Issuers with an explicit sovereign guarantee should be treated as government bonds and entered on either the Rates DV01 and/or the Sovereign Credit worksheet.

### Profit/(Loss) Calculation

Profit/(Loss) should be calculated assuming full revaluation where possible. In completing the Profit/(Loss) section, firms should run full revaluations assuming all credit spreads (across all geographies and products -- Munis, Corporates, CDS, etc.) move a given amount and then allocate the resulting P/L to the various rows and sections across all credit worksheets.

For example, firms should run a single full-revaluation simulation in which all spreads widen by 100% regardless of geography/product. P/L from this single simulation would then be allocated among the various rows and worksheets corresponding to different products, countries and indices.

### Spread Shocks

Profit/(Loss) from spread widenings should be entered using either the relative (%) section or the absolute (bps) section, but not in both.

Columns for additional slide points may be inserted, however **do not remove or modify any of the existing slide points shown in gray.**

### Tenors

In the term structure section, replace the tenor points shown in green with those the firm has available.

Insert additional term structure rows as needed. Unused rows should be left blank.

---

## F.17 -- Auction Rate Securities (ARS)

### General

This worksheet is meant to collect basic sensitivities related to Auction Rate Securities (ARS).

### Tenors

In the term structure section, replace the tenor points shown in green with those the firm has available.

Insert additional term structure rows as needed. Unused rows should be left blank.

---

## F.18 -- Corporate Credit-Advanced

### General

Reference the Regional Groupings worksheet for the definition of which countries are included in Advanced Economies.

Notional **and** MV amounts should be reported, by rating and tenor, for all relevant products.

*MV for CDS should be reported as the notional amount plus the current MTM of the CDS, i.e. the bond-equivalent market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond).

"On-the-Run" refers to the two most recent series (i.e. the current and the prior) of the index.

The <B rating bucket for each section is broken into 3 categories - one for defaulted securities, one for non-defaulted securities, and one for "Default Status Unknown". The "Defaulted" category is meant to capture (1) defaulted positions and (2) for Bonds, Single Name CDS, Covered Bonds and Other/Unspecified categories, positions that do not have associated credit spread sensitivities, e.g. distressed positions or positions for which credit spread sensitivities are not available, regardless of rating. The "Default Status Unknown" row is meant to be used only when firms do not have the ability to categorize a given security as being defaulted or not.

Note that no credit widening sensitivities are requested for <B defaulted securities.

The CDX Other and Itraxx Other categories are meant to capture exposures to indices that are not explicitly listed in the 'Corporate Credit-Advanced' tab. For example, CDX HiVol exposures should be reported under the "CDX Other" category and Itraxx HiVol exposures should be reported in the "Itraxx Other" category.

For Index Options, report exposure by tenor based on the maturity of the option and not that of the underlying.

### Decomposition

Bespoke CDOs and Credit Baskets should be decomposed and included by rating on the appropriate Corporate Credit worksheet under the section for "Single Name CDS".

Indices, Index Tranches and Index Options SHOULD NOT BE DECOMPOSED. They should be included by category (IG, HY, Loan Index) in the Indices & Index Tranches and the Index Options sections.

### Profit/(Loss) Calculation

Profit/(Loss) should be calculated assuming full revaluation where possible. In completing the Profit/(Loss) section, firms should run full revaluations assuming all credit spreads (across all geographies and products -- Munis, Corporates, CDS, etc.) move a given amount and then allocate the resulting P/L to the various rows and sections across all credit worksheets.

For example, firms should run a single full-revaluation simulation in which all spreads widen by 100% regardless of geography/product. P/L from this single simulation would then be allocated among the various rows and worksheets corresponding to different products, countries and indices.

### Spread Shocks

Profit/(Loss) from spread widenings should be entered using either the relative (%) section or the absolute (bps) section, but not in both.

The spread widenings listed in the green cells may be modified to fit what the firm has readily available subject to the following constraints:

**If using relative (%) widenings:**
- The 50%, 100% and 200% widenings are required. At least one widening must be 400% or greater.
- At least 3 widenings greater than 200% must be provided and no two adjacent widening %'s may be more than 100% apart.

**If using absolute (bps) widenings:**
- The +50 bps, +100 bps, +500 bps and +1000 bps widenings are required. At least one widening must be +2500 bps or greater.
- At least 3 additional widenings above +1000 bps must be provided. These must be spaced such that no two adjacent widenings are more than 1000 bps apart.

Note that the guidance in absolute space is necessarily a function of spread levels on the effective date and therefore subject to change. Firms are strongly encouraged to provide relative (%) spread sensitivities.

---

## F.19 -- Corporate Credit-Emerging Markets

### General

Emerging Markets encompasses all countries not defined as Advanced Economies on the Regional Groupings worksheet.

Notional **and** MV amounts should be reported, by rating and tenor, for all relevant products.

*MV for CDS should be reported as the notional amount plus the current MTM of the CDS, i.e. the bond-equivalent market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond).

"On-the-Run" refers to the two most recent series (i.e. the current and the prior) of the index.

The <B rating bucket for each section is broken into 3 categories - one for defaulted securities, one for non-defaulted securities, and one for "Default Status Unknown". The "Defaulted" category is meant to capture (1) defaulted positions and (2) for Bonds, Single Name CDS, Covered Bonds and Other/Unspecified categories, positions that do not have associated credit spread sensitivities, e.g. distressed positions or positions for which credit spread sensitivities are not available, regardless of rating. The "Default Status Unknown" row is meant to be used only when firms do not have the ability to categorize a given security as being defaulted or not.

Note that no credit widening sensitivities are requested for <B defaulted securities.

For Index Options, report exposure by tenor based on the maturity of the option and not that of the underlying.

### Decomposition

Bespoke CDOs and Credit Baskets should be decomposed and included by rating on the appropriate Corporate Credit worksheet under the section for "Single Name CDS".

Indices, Index Tranches and Index Options SHOULD NOT BE DECOMPOSED. They should be included by category (CDX, iTraxx, Loan Index) in the Indices, Index Tranches and the Index Options sections.

### Profit/(Loss) Calculation

Profit/(Loss) should be calculated assuming full revaluation where possible. In completing the Profit/(Loss) section, firms should run full revaluations assuming all credit spreads (across all geographies and products -- Munis, Corporates, CDS, etc.) move a given amount and then allocate the resulting P/L to the various rows and sections across all credit worksheets.

For example, firms should run a single full-revaluation simulation in which all spreads widen by 100% regardless of geography/product. P/L from this single simulation would then be allocated among the various rows and worksheets corresponding to different products, countries and indices.

### Spread Shocks

Profit/(Loss) from spread widenings should be entered using either the relative (%) section or the absolute (bps) section, but not in both. The spread widenings listed in the green cells may be modified to fit what the firm has readily available subject to the following constraints:

**If using relative (%) widenings:**
- The 50%, 100% and 200% widenings are required. At least one widening must be 400% or greater.
- At least 3 widenings greater than 200% must be provided and no two adjacent widening %'s may be more than 100% apart.

**If using absolute (bps) widenings:**
- The +50 bps, +100 bps, +500 bps and +1000 bps widenings are required. At least one widening must be +2500 bps or greater.
- At least 3 additional widenings above +1000 bps must be provided. These must be spaced such that no two adjacent widenings are more than 1000 bps apart.

Note that the guidance in absolute space is necessarily a function of spread levels on the effective date and therefore subject to change. Firms are strongly encouraged to provide relative (%) spread sensitivities.

---

## F.20 -- Sovereign Credit

### General

Exposures related to central governments and quasi-sovereigns that are explicitly guaranteed by the central government should be included in this worksheet and bucketed under the central government rating. Sub-sovereign exposures, such as those from municipalities, should be reported on the Munis Worksheet.

Notional **and** MV amounts should be reported for all relevant exposures.

The MV and Notional in columns (A) and (B) are to be used for sovereign bonds and sovereign CDS issued in the same currency as the base currency of the issuing sovereign. The rates sensitivities of these instruments are captured on the *Rates DV01* worksheet.

The MV and Notional in columns (C) and (D), are to be used for sovereign bonds and sovereign CDS denominated in currencies other than the base currency of the issuing sovereign. The rates sensitivities of these instruments are captured on the *Rates DV01* worksheet.

Credit spread sensitivities for sovereign CDS (regardless of currency) and for sovereign bonds denominated in currencies other than the base currency of the issuing sovereign should be entered on this worksheet. The rates sensitivities of these instruments are captured on the *Rates DV01* worksheet.

*MV for CDS should be reported as the notional amount plus the current MTM of the CDS, i.e. the bond-equivalent market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond).

Exposures to SovX indices (including options on SovX indices) should be decomposed and entered on the individual country rows.

Reference the definitions on the *Regional Groupings* worksheet for which countries should be included in rows labeled "Other".

### Profit/(Loss) Calculation

Profit/(Loss) should be calculated assuming full revaluation where possible. In completing the Profit/(Loss) section, firms should run full revaluations assuming all credit spreads (across all geographies and products -- Munis, Corporates, CDS, etc.) move a given amount and then allocate the resulting P/L to the various rows and sections across all credit worksheets.

For example, firms should run a single full-revaluation simulation in which all spreads widen by 100% regardless of geography/product. P/L from this single simulation would then be allocated among the various rows and worksheets corresponding to different products, countries and indices.

### Spread Shocks

Profit/(Loss) from spread widenings should be entered using either the relative (%) section or the absolute (bps) section, but not in both. The spread widenings listed in the green cells may be modified to fit what the firm has readily available subject to the following constraints:

**If using relative (%) widenings:**
- The 50%, 100%, and 200% widenings are required. At least one widening must be 300% or greater.
- At least 2 widenings greater than 200% must be provided and no two adjacent widening %'s may be more than 100% apart.

**If using absolute (bps) widenings:**
- The +50 bps, +100 bps, +500 bps and +1000 bps widenings are required. At least one widening must be +2000 bps or greater.
- At least 2 additional widenings greater than or equal to +1500 bps must be provided.

Note that the guidance in absolute space is necessarily a function of spread levels on the effective date and therefore subject to change. Firms are strongly encouraged to provide relative (%) spread sensitivities.

---

## F.21 -- Credit Correlation

### General

This worksheet is meant to capture the base correlation sensitivities of various structured credit indices by tenor and also notional amounts and MV of these positions.

The percentages in the first column are detachment points for the index tranches, where the attachment point for each tranche is the detachment point of the previous tranche. For example, for the IG index, the second tranche (the 7% row of the table) refers to the 3-7% tranche that absorbs losses beyond the first 3% and up to 7% of losses.

"Equity" tranches are defined as any tranche having a 0% attachment point.

"Super Senior" tranches are defined as any tranche having a detachment point of 60% or higher.

"Mezzanine" tranches are defined as all other tranches; that is any tranche with a non-zero attachment point and a detachment point less than 60%.

Tranches with non-standard attachment points should be mapped to the closest attachment points of the best-matching index category.

### Market Value (MV) and Notionals

*MV for CDS should be reported as the notional amount plus the current MTM of the CDS, i.e. the bond-equivalent market value of the CDS. The notional amount should be positive for cases where CDS protection has been sold (long underlying bond) and negative for cases where CDS protection has been bought (short underlying bond).

The notional / MV of bespoke CDOs and indices should be split between the various indices based upon the geographical location of names in the basket.

The notional / MV of bespoke CDOs and indices should be assigned to the closest current attachment point.

Long and Short exposures should be reported from the perspective of long or short the underlying credit. For CDS contracts, the long and short direction should not be from the perspective of bought or sold credit protection, but from the perspective of long or short the underlying credit exposure. Thus, sold protection in a CDS would be reported as a long credit position.

The exposures to be reported in each of the long and short categories should be netted against like exposures as described below:

Firms should conduct all netting at the firm-wide level, not at the business or desk level. MV-longs, and MV-shorts, should be the sum of exposures to obligors (issuers) to which the firm has net MV long, and net MV short, positions respectively. To arrive at the net Long, or net Short position, exposures to the same obligor should be netted (if JTD exposures to that obligor are offsetting) before aggregation across obligors. In determining the net exposure to an obligor, structured positions that are perfect replications of each other can be offset to arrive at the net position. For instance, long positions in a collection of tranches that when combined perfectly replicate short positions in another collection of tranches or an index can be offset against each other, if all the positions are to the exact same index and series (e.g. all are exposures to the CDX NA IG series 18). (For instance, a long position in a 10-15% tranche can be offset against short positions composed of a 10-12% tranche and a 12-15% tranche, if all the tranches are on the exact same index and series.) When a perfect replication is not possible, then offsetting is not allowed (except in the case of a residual as described in the next sentence). Where the long and short positions are otherwise equivalent except for a residual, the net amount should show the entire residual exposure.

Notional-long, and Notional-short, should similarly be the sum of the notional values of obligors with net long notionals, and net short notionals, positions respectively.

For index products, for the exact same index family (e.g. NA IG), series (e.g. series 18), and tranche (e.g. 0-3%), positions should be netted across maturities.

Different tranches of the same index or series may not be netted (except where replication is possible as specified above), different series of the same index may not be netted, and different index families may not be netted.
