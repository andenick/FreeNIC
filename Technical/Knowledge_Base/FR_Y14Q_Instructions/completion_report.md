# FR Y-14Q Instructions - Extraction Completion Report

## Document Information
- **Document**: FR Y-14Q Quarterly Capital Assessments and Stress Testing Instructions
- **Source**: Federal Reserve Board
- **Modified Date**: March 31, 2024
- **OMB No.**: 7100-0341
- **Expiration Date**: March 31, 2026

## Processing Summary
- **Chunks Processed**: 001-032 (32/32) -- COMPLETE
- **Processing Date**: 2026-03-22
- **Processor**: HDARP v4.5 Document Processor Agent
- **Status**: COMPLETE

## Content Coverage

### Chunk 001 (Pages 1-11): General Instructions
- Title page and legal authority citations
- Table of Contents (full document)
- General Instructions including:
  - Who Must Report (reporting criteria, $100B threshold, materiality thresholds, Category I-IV standards)
  - Exemptions
  - Where to Submit the Reports
  - When to Submit the Reports (filing schedule table)
  - How to Prepare the Reports (GAAP, consolidation, technical details)
  - Other Instructional Guidance
  - Confidentiality
  - Legal Considerations for International Exposures
  - Amended Reports
  - Questions and Requests for Interpretations
  - Attestation requirements
  - Definition of Commercially Available Credit Bureau Score
  - Most Recent Capital Framework

### Chunk 002 (Pages 12-18): Schedule A - Retail (A.1, A.2 partial)
- **A.1 - International Auto Loan**: Complete section including segment variables (product type, credit score, delinquency status, geography = 216 segments) and 24 summary variables
- **A.2 - US Auto Loan**: Complete section including segment variables (product type, age, original LTV, credit score, geography, delinquency status = 12,960 segments) and summary variables 1-16

### Chunk 003 (Pages 19-30): Schedule A - Retail (A.2 continued, A.3, A.4)
- **A.2 - US Auto Loan** (continued): Summary variables 17-34
- **A.3 - International Credit Card**: Complete section (360 segments, 15 summary variables, portfolio ID "IntCard")
- **A.4 - International Home Equity**: Complete section (480 segments, 18 summary variables, portfolio ID "IntHE")

### Chunk 004 (Pages 31-40): Schedule A - Retail (A.5, A.6, A.7)
- **A.5 - International First Lien Mortgage**: Complete section (480 segments, 14 summary variables, portfolio ID "IntFM")
- **A.6 - International Other Consumer Schedule**: Complete section (600 segments, 9 summary variables, portfolio ID "IntlOthCons")
- **A.7 - US Other Consumer**: Complete section (225 segments, 9 summary variables, portfolio ID "USOthCons")

### Chunk 005 (Pages 41-51): Schedule A - Retail (A.8, A.9, A.10)
- **A.8 - International Small Business**: Complete section (720 segments, 12 summary variables, portfolio ID "IntSB")
- **A.9 - US Small Business**: Complete section (180 segments, 12 summary variables, portfolio ID "USSB"). Note: PPP loans excluded.
- **A.10 - Student Loan**: Complete section (600 segments, 20+ summary variables, portfolio ID "Student")

### Chunk 006: Schedule A (end) and Schedule B - Securities (B.1)
- Schedule A summary variables 21-23 (Net Charge-offs, Adjustment factor, Weighted Average Life)
- **Schedule B - Securities**: Introduction, scope, exclusions (trading securities, FVO, unsettled)
- **B.1 - Securities 1 (Main Schedule)**: Complete field instructions for Unique ID, Identifier Type/Value (CUSIP/ISIN/SEDOL/INTERNAL), Private Placement, Security Description (19 categories: Agency MBS, Auction Rate Securities, CDO, CLO, CMBS, Common Stock, Auto/Credit Card/Student Loan/Other ABS, Corporate Bond, Covered Bond, Domestic Non-Agency RMBS, Foreign RMBS, Municipal Bond with 13 sector subcategories, Mutual Fund, Preferred Stock, Sovereign Bond, US Treasuries & Agencies, Other), Exposure fields (Amortized Cost, Market Value, Current/Original Face Value), Allowance for Credit Losses, Writeoffs, Accounting Intent (AFS/HTM/EQ), Price, Pricing Date, Book Yield, Purchase Date, Currency (ISO 4217)

### Chunk 007: Schedule B.2 - Securities 2 (Hedging)
- **B.2 - Securities 2 (Investment Securities with Designated Accounting Hedges)**: Complete instructions for reporting qualified hedging relationships on AFS/HTM securities
- One-to-many relationship reporting guidance (multiple hedges per security, portfolio hedges across securities)
- Field specification table with 15 fields covering hedge type (fair value/cash flow), hedged risk (11 categories), hedge interest rate benchmarks, hedge percentage, horizon, cash flow type, sidedness, instrument fair value, cumulative gains/losses, ASU 2017-12 designations

### Chunk 008: Schedule C - Regulatory Capital Instruments (C.1, C.2)
- **Schedule C - General Guidance**: CUSIP-level data on regulatory capital and subordinated debt instruments; all subordinated debt required regardless of regulatory capital inclusion
- **C.1 - Quarter End**: Column-by-column instructions (B through S) covering CUSIP, instrument type (16 types), regulatory capital treatment (12 CFR 217), notional amount, carrying value, unamortized discounts/premiums, swap fair values, currency, interest expense (3 variants), fair value adjustments
- **C.2 - Repurchases/Redemptions During Quarter**: Column instructions (B through K); all values reported as negative; exclusions for amortizations, APIC from employee stock compensation; IHC foreign parent remittance reporting conventions

### Chunk 009: Schedule C (C.3) and Schedule D - Regulatory Capital (lines 1-12)
- **C.3 - Issuances During Quarter**: Column instructions (B through KK) covering CUSIP/ISIN, instrument type, conversion details, issuance date, perpetual/dated, call features, fixed/floating coupon, index/spread details, step-up provisions, convertibility, swap index/spread
- **Schedule D - Regulatory Capital**: General guidance referencing FR Y-9C Schedule HC-R
- Lines 1-9 (Category I and II firms only): Non-significant and significant investments in unconsolidated financial institutions, 10% CET1 deduction thresholds
- Lines 10-12 (Category III and IV firms only): 25% threshold for investments in unconsolidated financial institutions

### Chunk 010: Schedule D (lines 13-M1), Schedule E - Operational Risk, Schedule F - Trading (partial)
- **Schedule D continued**: Mortgage servicing assets (lines 13-17), DTAs from temporary differences (lines 18-23), 15% aggregate limit (lines 24-28, Category I/II only), common stock issuance/repurchase (lines 29-30), Memoranda item M1
- **Schedule E - Operational Risk**: Complete instructions for E.1 Operational Loss History (18-field data collection schedule), E.2 Internal Business Line mapping, E.3 Unit-of-Measure, E.4 Threshold Information, E.5 Legal Reserves Frequency
- Reference Table E.1.a: 7 Basel Level 1 Event-Types with 20 Level 2 subcategories and definitions
- Reference Table E.1.b: 9 Basel Level 1 Business Lines with 21 Level 2 subcategories and activity groups
- **Schedule F - Trading**: Purpose (trading book, private equity, FVO hedges, AL hedges, other fair value assets), general instructions (CVA/XVA exclusions, ETF treatment), glossary (30+ terms), regional groupings (6 regions, 190+ countries)
- Sub-schedule instructions: F.1 Equity by Geography, F.2 Equity Spot-Vol Grid, F.3 Other Equity, F.4 FX Spot Sensitivities, F.5 FX Vega, F.6 Rates DV01 (including basis risk reporting examples and sovereign bond treatment)

### Chunk 011: Schedule F - Trading (continued): F.7 through F.15
- **F.7 - Rates Vega**: General instructions (normal volatility convention, $MM/+10% relative or $MM/+10 bps absolute), Regional Groupings references, customizable tenor points
- **F.8 - Other Rates**: Cross-currency vs. USD basis definition (USD vs. CCY + x Basis Swap ($K)), customizable tenor columns
- **F.9 - Energy**: Commodity delta ($MM dollarized), Total Gamma/Vega definitions (unweighted sum across tenors), vega reporting options (absolute vs. relative, consistent across all commodity worksheets), storage/model exclusion rules (<$50mm materiality), Structured Products column, monthly tenor for first 12 months, Informational section as SUBSETS of total exposures
- **F.10 - Metals**: Same commodity sensitivity framework as Energy (delta, gamma, vega, storage exclusion, tenor rules)
- **F.11 - Ags & Softs**: Same commodity sensitivity framework as Energy
- **F.12 - Commodity Indices**: Same commodity sensitivity framework; decompose diversified indices into Energy/Metals/Ags & Softs where possible; Long/Short Commodity Indices column for alpha strategies
- **F.13 - Commodity Spot-Vol Grids**: Full revaluation methodology, shock entire vol surface and spot prices; Diversified Commodity Indices grid corresponds to Commodity Indices worksheet only; spot shocks span -75% to +75% (min 5 down/3 up, max 25% gap); vol shocks span 0 to +50 vol pts (min 4 shocks >0, max 15 pts gap); relative vol shock conversion guidance
- **F.14 - Securitized Products**: Notional and MV by rating and vintage; CDS MV = notional + MTM (bond-equivalent); current ratings (not original); vintage = submission date minus issue/effective date; agency forward loans on Agencies worksheet; warehouse = first-loss-protected exposure only; CLO warehouse = traded amount; European RMBS separate category
- **F.15 - Agencies**: US Agency sensitivities (top section); non-US Agencies without explicit sovereign guarantee (lower section, includes bonds and CDS); non-US with explicit guarantee = government bonds on Rates DV01/Sovereign Credit; loans only if in forward contract or FHA review; OAS spread sensitivities; OAS shocks span 100-400+ bps (min 4 distinct shocks >1 bp)

### Chunk 012: Schedule F - Trading (continued): F.16 through F.21
- **F.16 - Munis**: All Municipals regardless of geography/currency; <B rating bucket split into defaulted/non-defaulted/unknown; no credit widening sensitivities for <B defaulted; full revaluation P/L calculation (single simulation across all credit products); spread shocks via relative (%) or absolute (bps) only, not both; do not modify existing gray slide points; customizable tenor rows
- **F.17 - Auction Rate Securities (ARS)**: Basic ARS sensitivities; customizable tenor rows
- **F.18 - Corporate Credit-Advanced**: Advanced Economies per Regional Groupings; notional/MV by rating and tenor; "On-the-Run" = two most recent index series; <B rating 3-category split; CDX Other/Itraxx Other for unlisted indices; Index Options by option maturity; Bespoke CDOs/Credit Baskets decomposed to Single Name CDS; Indices/Tranches/Options NOT decomposed; full revaluation P/L; relative spread shocks: 50%/100%/200% required, one >=400%, 3 above 200% max 100% apart; absolute: +50/+100/+500/+1000 bps required, one >=+2500 bps, 3 above +1000 max 1000 bps apart
- **F.19 - Corporate Credit-Emerging Markets**: Same framework as F.18 for Emerging Markets (all non-Advanced Economy countries); same spread shock constraints
- **F.20 - Sovereign Credit**: Central governments and explicitly guaranteed quasi-sovereigns; sub-sovereigns on Munis worksheet; columns (A)/(B) for base-currency instruments, (C)/(D) for foreign-currency; SovX indices decomposed to individual countries; relative spread shocks: 50%/100%/200% required, one >=300%, 2 above 200%; absolute: +50/+100/+500/+1000 bps required, one >=+2000 bps, 2 additional >=+1500 bps
- **F.21 - Credit Correlation**: Base correlation sensitivities of structured credit indices by tenor; detachment point = attachment point of next tranche; Equity = 0% attachment, Super Senior = 60%+ detachment, Mezzanine = all others; non-standard tranches mapped to closest; firm-wide netting (MV and notional by long/short); perfect replication offsetting rules; netting across maturities within same index family/series/tranche; no cross-tranche, cross-series, or cross-index netting

### Chunk 013: Schedule F - Trading (end): F.22 through F.25
- **F.22 - IDR-Corporate Credit**: Corporate credit only (no RMBS/CMBS/ABS); Tables A (Single Name), B (Index), C (Other/Unspecified) without decomposition; Table D for issuers >$50M single name exposure; Table E for remaining <$50M issuers; Table F for index position breakout by series (CDX IG/HY/iTraxx Main/XO for all non-zero, others for >$100M gross MV); Table G for bespoke tranche product detail by index/seniority bucket; bond-equivalent MV formulas for CDS (MV=MTM+S*|Notional|), bond options (Sold Put=Strike-|MTM|, etc.), index options (Sold Payer=|Notional|-|MTM|, etc.); long/short from underlying credit perspective
- **F.23 - IDR-Jump to Default**: JTD equivalent basis (difference in MV assuming default vs. no default with zero recovery); $25MM JTD threshold; debt and equity corporate exposures including nonpublic companies; exclude Sovereigns/Agencies/Munis/ARS/counterparty credit; Totals = firm-wide total JTD by rating for all issuers
- **F.24 - Private Equity**: Carry value by GICS code and region; Section (A) fair value/NAV, Section (B) cost/equity method; separate sections for real estate, hedge fund minority interest, fund seed capital, infrastructure funds; Affordable Housing PWI line items (non-tax oriented only); all unfunded commitments included; Regional definitions: Western Europe (15 countries), Other Developed Markets, Emerging Markets, Unspecified Geography
- **F.25 - Other Fair Value Assets**: Non-PE fair value investments by GICS code; equity vs. debt, US vs. non-US; Tax Credits section by NAICS code; BOLI/COLI/Stable Value Wraps: maximum instantaneous post-shock amounts in US Debt column, wraps written as negative fair value, net combination positions

### Chunk 014: Schedule G -- PPNR (General Technical Details, Terms, G.1 Submission Worksheet)
- **Schedule G General Technical Details**: PPNR Schedule = 4 worksheets (Cover Sheet, Submission, NII, Metrics); consistent line item definitions between FR Y-14A and FR Y-14Q; quarterly reporting (not YTD); zero-fill numerical blanks, "N/A" for descriptive blanks; reconciliation formula to FR Y-9C Schedule HI items 3 + 5.m - 7.e + 7.c.(1) - item 40 FVO
- **Materiality Thresholds**: 5% of total revenue threshold for business segment reporting; 5% international revenue threshold for regional breakouts; 5% International Retail/Small Business for related metrics
- **Net Interest Income Primary/Supplementary Designation**: NII worksheet = "Primary" if required; Submission worksheet = "Supplementary" by default (or vice versa)
- **Commonly Used Terms**: PPNR definition (NII + noninterest income - noninterest expense, adjusted for FVO, goodwill impairment, trading shock, operational risk); Revenues; Run-Off/Liquidating Businesses
- **G.1 PPNR Submission Worksheet**: Standardized business segment/line reporting; Revenue Components (NII and noninterest income reconciling to FR Y-9C adjusted); FTP-based segment allocation; DVA/CVA disclosure encouraged
- **Business Segment Definitions**: Small business <$10M sales, medium $10M-$2B, large >$2B; public funds allocation guidance
- **NII by Business Segment (Line items 1-13)**: Retail & Small Business (1A Domestic: 1B Credit/Charge Cards, 1C Mortgages, 1D Home Equity, 1E Deposits, 1F Other Lending; 1G International); Commercial Lending (2); Investment Banking (3); Merchant Banking/PE (4); Sales & Trading (5A Prime Brokerage, 5B Other); Investment Management (6); Investment Services (7); Treasury Services (8); Insurance Services (9); Retirement/Corporate Benefits (10); Corporate/Other (11); Optional Immaterial (12, max 10% of revenue); Total NII (13)
- **Noninterest Income by Business Segment (Line items 14-27)**: Same segment structure with detailed sub-items for Retail (14C/14D Credit Card interchange/other, 14E-14N Mortgage/HE production/servicing/MSR/repurchase reserve, 14O-14R Deposits NSF/Overdraft/Debit interchange, 14S Other Lending, 14T International); Investment Banking (16A-D Advisory/ECM/DCM/Syndicated); Merchant Banking (17A-C MTM/Fees/Other); Sales & Trading (18A-M Equities/FI/Commodities/Prime Brokerage with Commission/Other splits); Investment Management (19A-B AM/WM-PB); Investment Services (20A-E); Treasury (21); Insurance (22); Retirement (23); Corporate/Other (24); Optional Immaterial (25)

### Chunk 015: Schedule G -- PPNR (continued): G.1 Expense Components, G.2 NII Worksheet
- **G.1 Noninterest Expense Components (Line items 28-42)**: Compensation Expense (28A-E: Salary, Benefits, Commissions, Stock Based per ASC 718, Cash Variable Pay); Operational Risk Expense (29, includes all operational losses, litigation reserves for sold mortgages, settlements/penalties); Repurchase Reserve provisions (30); Professional/Outside Services (31); Premises/Fixed Assets (32); Intangible Amortization/Impairment (33); Marketing (34A Domestic Credit Card, 34B Other); OREO Expense (35); Provision for Unfunded Off-BS Credit Exposures (36); Other Noninterest Expense (37, breakout required so no more than 5% unreported); Total Noninterest Expense (38); Actual PPNR (39); FVO Valuation Adjustment (40); Goodwill Impairment (41, ASC 350-20-35-30); Trading Shock Loss (42)
- **G.2 PPNR Net Interest Income (NII) Worksheet**: All BHCs/IHCs/SLHCs required; average asset/liability balances and average yields; NII must equal PPNR Submission item 13; rates = product level (gross, no FTP); Average Assets (Line items 1-17): First Lien Mortgages, Second/Junior Liens (Closed-End/HELOCs), C&I, CRE, Credit Cards, Other Consumer (Auto/Student/Other), RE Loans not in domestic offices, Other Loans/Leases, Nonaccrual Loans, Securities AFS/HTM (Treasuries-Agency/Agency RMBS/Other), Trading Assets, Deposits with Banks, Other Interest-Bearing Assets, Other Assets, Total; Average Rates Earned (Line items 18-33): corresponding rates for each asset category, Total Interest Income; Average Liability Balances (Line items 34-41): Deposits Domestic (Demand/MMA/Savings/NOW-ATS/Time), Deposits Foreign, Fed Funds/Repos/Other ST Borrowing, Trading Liabilities, TruPS, Other Interest-Bearing Liabilities, Other Liabilities, Total; Average Liability Rates (Line items 42-49): corresponding rates, Total Interest Expense, Total Net Interest Income

### Chunk 016: Schedule G -- PPNR (continued): G.3 PPNR Metrics (Sections A, B, C)
- **G.3 PPNR Metrics**: General instructions (all metrics required subject to thresholds, third party data permitted, alternative metrics guidance, proprietary trading disclosure)
- **Section A -- Metrics by Business Segment/Line** (all numbers global unless specified):
  - Retail & Small Business Domestic: Credit/Charge Cards (items 1-3: open accounts, purchase volume, rewards/partner sharing expense); Mortgages & Home Equity (items 4-7: avg 3rd party serviced, industry market size volume, sold during quarter, servicing expenses); Deposits (items 8-9: open checking/MMA accounts, debit card transactions)
  - International Retail & Small Business (item 10: credit/charge card revenues, 5% threshold)
  - Investment Banking (items 11-26, >$100M threshold): Employees/compensation (11-13); Advisory (14-17: deal volume, industry market size fees/volume, backlog); Equity Capital Markets (18-20); Debt Capital Markets (21-23); Syndicated Lending (24-26)
  - Sales & Trading (items 27-34): Employees/compensation (27-29); Average asset balances for Equities (30), Fixed Income (31), Commodities (32); Prime Brokerage (33-34: avg client balances, transaction volume)
  - Investment Management (items 35-39): AUM Total/Equities/FI/Other (35/35A-C), Net Inflows/Outflows (36); Wealth Management/Private Banking (37/37A-C Fee Earning Client Assets, 38 Net Inflows, 39 Financial Advisors)
  - Investment Services (item 40: Assets under Custody and Administration)
- **Section B -- Firm Wide Metrics: PPNR Projections Worksheet** (items 41-49): Employees (41); International Revenues by region (42A APAC, 42B EMEA, 42C LatAm, 42D Canada, 5% threshold); Domestic Revenues (43); Severance Costs (44); Operating Lease Collateral (45/45A Auto/45B Other); OREO Balance (46/46A Commercial/46B Residential/46C Farmland); Non-Recurring PPNR Items (47); Trading Revenue (48); Net Gains/Losses on OREO Sales (49)
- **Section C -- Firm Wide Metrics: NII Worksheet** (items 50-85, required only for NII Worksheet filers): Purchased Credit Deteriorated Loans (50); Net Accretion of Discount (51); Loans HFS -- First Lien Residential avg balance/rate (52-53); Quarter End WAL of Assets -- 17 categories (items 54-70: First Lien Mortgages, Closed-End Junior Liens, HELOCs, C&I, CRE, Credit Cards, Auto, Student, Other Consumer, Residential Mortgages non-domestic, Other RE non-domestic, Other Loans & Leases, Securities AFS/HTM Treasuries-Agency/Agency RMBS/Other, Trading Assets, All Other Earning Assets); Quarter End WAL of Liabilities -- 8 categories (items 71-78: Domestic Deposits Time, Foreign Deposits Time, Fed Funds, Repos, Other ST Borrowing, Trading Liabilities, TruPS, All Other Interest Bearing Liabilities); Average Domestic Deposit Repricing Beta (items 79-82: Money Market, Savings, NOW/ATS/Transaction, Time Deposits -- reported in bp per 100bp rate move); Average Foreign Deposit Repricing Beta (items 83-84: Foreign Deposits, Foreign Deposits-Time); New Domestic Business Pricing for Time Deposits (85/85A Curve/85B Index Rate/85C Spread)

### Chunk 017: Schedule H -- Wholesale Risk: H.1 Corporate Loan Data Schedule (Introduction)
- **H.1 Corporate Loan Data Schedule**: Two sections -- (1) Loan and Obligor Description (Fields 1-51 and 83-108), (2) Obligor Financial Data (Fields 52-82); loan-level detail
- **Loan Population**: HFI and HFS corporate loans and leases (including fair value option); exclude trading loans and PPP loans; include unused commitments from HC-L; include syndicated pipeline (single-signed commitment letters); include disposed loans during reporting period; **$1 million committed balance threshold**
- **11 FR Y-9C HC-C categories** considered corporate loans: US depository institutions (2.a), foreign banks (2.b), agricultural production (3), C&I US (4.a), C&I non-US (4.b), foreign governments (7), nondepository financial institutions (9.a), other loans excl consumer (9.b(2)), other leases excl consumer (10.b), owner-occupied nonfarm nonresidential domestic (1.e(1)), owner-occupied nonfarm nonresidential non-domestic (item 1)
- **Owner-occupied nonfarm nonresidential**: Report on Corporate Loans Schedule (primary repayment from operations, not rental income <50%)
- **Small business exclusion**: Differentiated by credit evaluation method (graded/rated = corporate; scored/delinquency managed = small business)
- **Credit facility level reporting**: One record per credit agreement; $1M threshold on aggregate commitment; multiple draws consolidated; separate facilities reported separately; cross-schedule allocation for multi-type facilities
- **Reporting Specifications**: Amortized cost for HFI; lower of cost/fair value for HFS; fair value for FVO elections; pro-rata portions for syndicated/participated loans; fronting exposure reporting (Option 18 Field 20); all amounts in USD
- **Obligor Financial Data Section** (Fields 52-82): Required for all except obligors domiciled outside US, NAICS 52/5312/551111, nonprofits/governments, natural persons; relates to primary source of repayment entity; GAAP standards; TTM reporting for income fields; financial spreading system definitions
- **Data Format**: Single XML file, one record per active loan, no quotation marks, no header row, datetime fields use T00:00:00

### Chunk 018: Schedule H.1 Corporate Loan Data Fields (Fields 1-27)
- **H.1 Field Specifications Part 1**: Loan and Obligor Description section covering obligor identification, geographic information, industry classification, internal risk rating, external identifiers, credit facility identifiers, dates, facility type (20 types from Other to Commitment to Commit), facility purpose (31 purposes from Other to Capital Call Subscription), exposure amounts (committed and utilized), FR Y-9C line mapping (11 HC-C categories), and line of business
- Fields include: Customer ID (1), Internal ID (2), Original Internal ID (3), Obligor Name (4), City (5), Country (6), Zip Code (7), Industry Code NAICS/SIC/GICS (8-9), Obligor Internal Risk Rating (10), TIN (11), Stock Exchange (12), Ticker Symbol (13), CUSIP (14), Internal Credit Facility ID (15), Original Internal Credit Facility ID (16), DO NOT USE (17), Origination Date (18), Maturity Date (19), Credit Facility Type (20), Other CF Type Description (21), Credit Facility Purpose (22), Other CF Purpose Description (23), Committed Exposure Global (24), Utilized Exposure Global (25), Line Reported on FR Y-9C (26), Line of Business (27)

### Chunk 019: Schedule H.1 Corporate Loan Data Fields (Fields 28-51)
- **H.1 Field Specifications Part 2**: Remaining Loan and Obligor Description section covering charge-off history, delinquency, participation/syndication, collateral/lien, interest rate characteristics, tax status, guarantor information, and primary source of repayment entity
- Fields include: Cumulative Charge-offs (28), DO NOT USE (29-31), Days Past Due (32), Non-Accrual Date (33), Participation Flag with SNC (34), Lien Position (35), Security Type (36), Interest Rate Variability (37), Interest Rate (38), Interest Rate Index incl SOFR (39), Interest Rate Spread (40), Interest Rate Ceiling (41), Interest Rate Floor (42), Interest Income Tax Status (43), Guarantor Flag (44), Guarantor Internal ID (45), Guarantor Name (46), Guarantor TIN (47), Guarantor Internal Risk Rating (48), Entity Internal ID (49), Entity Name (50), Entity Internal Risk Rating (51)

### Chunk 020: Schedule H.1 Corporate Loan Data Fields (Fields 52-80)
- **H.1 Field Specifications Part 3 -- Obligor Financial Data Section**: Financial health data for the obligor or primary source of repayment entity, required for US-domiciled non-financial non-government corporate obligors
- Fields include: Date of Financials (52), Date of Last Audit (53), Net Sales Current TTM (54), Net Sales Prior Year TTM (55), Operating Income TTM (56), Depreciation & Amortization TTM (57), Interest Expense TTM (58), Net Income Current TTM (59), Net Income Prior Year TTM (60), Cash & Marketable Securities (61), A/R Current (62), A/R Prior Year (63), Inventory Current (64), Inventory Prior Year (65), Current Assets Current (66), Current Assets Prior Year (67), Tangible Assets (68), Fixed Assets (69), Total Assets Current (70), Total Assets Prior Year (71), A/P Current (72), A/P Prior Year (73), Short Term Debt (74), Current Maturities of LT Debt (75), Current Liabilities Current (76), Current Liabilities Prior Year (77), Long Term Debt (78), Minority Interest (79), Total Liabilities (80)

### Chunk 021: Schedule H.1 Corporate Loan Data Fields (Fields 81-99)
- **H.1 Field Specifications Part 4**: Remaining Obligor Financial Data fields (81-82: Retained Earnings, Capital Expenditures), SPE identification (83), reserved fields (84-85), accounting flags (86 LOCOM), SNC linkage (87), advanced IRB risk parameters (88 PD, 89 LGD, 90 EAD), renewal and currency (91-92), collateral valuation (93), prepayment provisions (94), entity industry code (95), participation interest (96), leveraged loan flag (97), disposition tracking (98 Disposition Flag with 9 options, 99 Disposition Schedule Shift)

### Chunk 022: Schedule H.1 Fields 100-112 (end), Schedule H.2 CRE Introduction and Fields 1-18
- **H.1 Field Specifications Part 5**: Syndicated loan pipeline fields (100 Syndicated Loan Flag with 5 options, 101 Target Hold), CECL fields (102 ASC326-20, 103 PCD Noncredit Discount), fair value fields (104 Current Maturity Date, 105-108 Committed/Utilized Exposure Global Par Value and Fair Value), reserved (109-110), LEI fields (111 Obligor LEI, 112 Primary Source of Repayment LEI)
- **H.2 Commercial Real Estate Schedule Introduction**: Loan population (HFI/HFS CRE loans, $1M threshold, 4 HC-C categories, owner-occupied exclusion to Corporate Loans, credit facility level reporting with cross-schedule allocation example), cross-collateralized loan instructions (limited data collection for <$1M: Fields 1/3/5/44 only), reporting specifications (amortized cost/LOCOM/FVO, pro-rata, USD), data format (XML)
- **H.2 CRE Fields 1-18**: Loan Number (1), Obligor Name (2), Outstanding Balance (3), Line Reported on FR Y-9C (4, 7 CRE categories), Committed Exposure Global (5), Cumulative Charge-offs (6), Participation Flag (7, 5 SNC options), Lien Position (8, includes B-Note), Property Type (9, 12 types incl Healthcare and Warehouse/Distribution), Origination Date (10), Location (11, ZIP/country/Multiple), NOI at Origination (12), Value at Origination (13), Value Basis (14), Internal Rating (15, code:fraction format), PD (16), LGD (17), EAD (18)

### Chunk 023: Schedule H.2 CRE Data Fields (Fields 19-39)
- **H.2 CRE Fields 19-39**: Maturity Date (19, inclusive of borrower-discretion extensions), Amortization (20, months/-1 for non-standard), Recourse (21, Full/Partial/None), Line of Business (22, optional), Current Occupancy (23, % of net rentable sq ft), Anchor Tenant (24, optional), Loan Purpose (25, 9 types incl Mini-Perm), Interest Rate Variability (26, incl Entirely fee based), Interest Rate (27, dollar weighted avg), Interest Rate Index (28, incl SOFR), Interest Rate Spread (29), Interest Rate Ceiling (30), Interest Rate Floor (31), Frequency of Rate Reset (32), Interest Reserves (33), Origination Amount (34), Original/Previous Loan Number (35), Acquired Loan (36), Days Past Due (37), Non-Accrual Date (38), Property Size (39, by type: sq ft/rooms/units/lots/acreage)

### Chunk 024: Schedule H.2 CRE Data Fields (Fields 40-58)
- **H.2 CRE Fields 40-58**: NOI Current (40), Last NOI Date (41), Current Value (42), Last Valuation Date (43), Cross Collateralized Loan Numbers (44), Additional Collateral (45, optional), reserved (46-48), Troubled Debt Restructuring (49), reserved (50-51), LOCOM Flag (52), SNC Internal Credit ID (53), Renewal Date (54), Credit Facility Currency (55, ISO 4217), Current Occupancy Date (56), Current Value Basis (57, As Is/Stabilized/Completed), Prepayment Penalty Flag (58)

### Chunk 025: Schedule H.2 CRE Data Fields (Fields 59-67)
- **H.2 CRE Fields 59-67**: Participation Interest (59, decimal), Leveraged Loan Flag (60), Disposition Flag (61, 8 options: Active through Expired Commitment to Commit), Disposition Schedule Shift (62), ASC326-20 (63), PCD Noncredit Discount (64), Current Maturity Date (65, exclusive of extensions), Committed Exposure Global Par Value (66, HFS/FVO only), Outstanding Balance Par Value (67, HFS/FVO only)

### Chunk 026: Schedule H.2 CRE Fields 68-72, H.3 Line of Business, H.4 Internal Risk Rating, Schedule J Retail FVO/HFS
- **H.2 CRE Fields 68-72**: Current Value Fair Value (68), DO NOT USE (69-71), Obligor LEI (72)
- **H.3 - Line of Business Schedule**: 2 fields (LineOfBusinessName, LineOfBusinessDescription); XML format
- **H.4 - Internal Risk Rating Schedule**: 5 fields (InternalRating, InternalRatingDescription, MinimumPD, MaximumPD, PD Calculation Method)
- **Schedule J - Retail FVO/HFS**: Table 1 with 12 line items (residential first lien/junior lien/HELOCs, non-residential CLD/multifamily/owner-occupied/non-owner-occupied/farmland, other C&I/consumer/other loans/total); Table 2 vintage-based carrying value matrix (9 columns by origination year)

### Chunk 027: Schedule K Supplemental, Reference Table K.1, Schedule L Counterparty Introduction
- **Schedule K - Supplemental**: Columns A-F (Immaterial Portfolios, Cumulative Gross Charge-offs, Retired, CRE/Corporate <$1M, Unplanned Overdrafts, Scored Loans)
- **Reference Table K.1**: Full loan category definitions with FR Y-9C HC-C line mappings (30+ categories: Student Loans, Other Consumer, First Lien, Junior Lien, Bank/Charge Cards, Auto, CRE subcategories, Farmland, C&I, Graded Other Loans)
- **Schedule L - Counterparty**: Introduction covering 18 sub-schedules overview, data formatting, counterparty exposure universe for L.1-L.4 and L.5, identification requirements, consolidation rules, CCP reporting, submission deadlines

### Chunk 028: Schedule L -- Counterparty (L.1.a, L.1.b, L.1.e, L.1.f)
- **L.1.a**: Top 95% unstressed CVA counterparties; detailed item instructions for all fields with MDRM codes (Rank, Counterparty Name/ID/LEI, Netting Set/Sub-netting Set IDs, Industry Code, Country, Internal/External Rating, Gross CE, Net CE, Total Notional, New Notional, Weighted Average Maturity, Position MtM, Total Net Collateral, CVA, CSA indicator, Single Name Credit Hedges)
- **L.1.b**: Top 95% stressed CVA (Federal Reserve Severely Adverse Scenario); Stressed Gross CE, Stressed Net CE, Stressed CVA
- **L.1.e**: Aggregate CVA data (4 tables with 6 additional/offline reserve categories)
- **L.1.f**: Residual counterparty metrics (6 regional groupings)
- No structured tables extracted (field-by-field instructions in body text)

### Chunk 029: Schedule L -- Counterparty (L.2, L.3, L.4)
- **L.2 - EE Profile by Counterparty**: Column instructions (L.2.a-L.2.b) including tenor bucket, Expected Exposure, Marginal PD, LGD, Discount Factor, Stressed EE/PD/LGD/Discount Factor with all MDRM codes (CACB-prefix)
- **L.3 - Credit Quality by Counterparty**: Column instructions (L.3.a-L.3.b) including time period, market spread, spread adjustment, spread used in CVA, stressed spreads, mapping approach, proxy mapping, proxy name, market input type, ticker, report date, source, comments (CACQ-prefix)
- **L.4 - Aggregate and Top 10 CVA Sensitivities by Risk Factor**: Risk factor category, description, slides, sensitivity; aggregate and top 10 parent/consolidated counterparties (CACU-prefix)
- No structured tables extracted (field-by-field instructions in body text)

### Chunk 030: Schedule L -- Counterparty (L.5) and Schedule M Balances
- **L.5 - Derivatives and SFT Profile**: General instructions (ranking methodologies for CCAR/non-CCAR quarters, netting agreement reporting rules)
- **L.5.1**: Derivative and SFT information by counterparty legal entity and netting set (30+ fields: Rank Methodology, Agreement Type with 9 allowable entries, Agreement Role, Legal Enforceability, Initial Margin, Non-Cash Collateral Type, Excess Variation Margin, Default Fund, Thresholds, MTAs, Margining Frequency, CSA features, Wrong Way Risk, Net CE fields, MtM fields unstressed/stressed, Cash Collateral by currency, CDS fields)
- **L.5.2**: SFT assets posted and received by asset category (9 categories, 30 sub-categories with 4 MDRM codes each)
- **L.5.3**: Aggregate SFTs by Internal Rating
- **L.5.4**: Derivative position detail (14 derivative types with Unstressed/Stressed MtM MDRM codes)
- **Schedule M - Balances**: M.1 Quarter-end Balances (Columns A-D for HFI/HFS domestic/international, line items 1.a through 1.c covering first mortgages, HELOANs, HELOCs, CLD, multifamily, nonfarm nonresidential, farmland)

### Chunk 031 (Pages ~continued): Schedule M.1 Line Items (continued), M.2, M.3
- **M.1 Line Items 2.a-6**: Graded C&I loans, Small business loans, SME/corporate cards, Bank cards, Charge cards, Auto loans, Student loans, Non-purpose lending, Auto leases, Other consumer loans/leases, Loans to foreign governments, Agricultural loans, Securities lending, Loans to financial institutions, Other commercial loans/leases, Purchased credit card relationships and nonmortgage servicing assets
- **Schedule M.2 - FR Y-9C Reconciliation**: Small business loans (lines 1.a-1.g), SME cards/corporate cards (lines 2.a-2.i), Charge cards (lines 3.a-3.b), Student loans (lines 4.a-4.b), Non-purpose consumer lending (lines 5.a-5.b) -- all mapped to HC-C line items, Columns A (HFI at AC) and B (HFS/FVO)
- **Schedule M.3 - Principal Balance of Retail Loans**: Part I Book Value and UPB by PCD status (Columns A-D for non-PCD/PCD book value and UPB): First mortgages, First lien HELOANs, Junior lien HELOANs, HELOCs, Bank cards, Charge cards, Auto loans, All other consumer loans/leases; Part II Cumulative Interim Loan Losses: 6 retail loan categories (domestic and international) with definition of cumulative interim loan losses

### Chunk 032 (Pages ~continued): Appendix A -- FR Y-14Q Supporting Documentation
- **Schedule C Supporting Docs**: Capital instrument prospectus/certificate/indenture requirements
- **Schedule D Supporting Docs**: Planned Action quarterly update requirements (file naming: BHCRSSD_BHCMNEMONIC_REGCAPTRANS_QTRLYUPDATE_ACTION#_YYMMDD)
- **Schedule L Supporting Docs**: Counterparty risk methodology documentation (file naming: BHCRSSD_BHCMNEMONIC_CCR_METHODOLOGY_MODELTYPE_YYMMDD), Executive Summary requirements
- **Trading Issuer Default Losses (Trading IDL)**: 8 methodology areas (Data/systems, PD methodology, Correlation, LGD methodology, Liquidity horizon, EAD, Treatment of gains, Model validation)
- **CVA Losses**: 6 methodology areas (Divergence from instructions, Data/systems with 13 sub-questions, LGD methodology, EAD, Application of shocks, Model validation)
- **Counterparty Default Losses (CDL)**: 9 methodology areas (Data/systems, PD, Correlation, LGD, Liquidity horizon, EAD, Treatment of gains, Model validation, Other firm-wide losses)
- **Supplemental Data Collection**: Description requirements for supplemental data tables

## Output Files Generated

### Body Text Files (Markdown)
| File | Size | Content |
|------|------|---------|
| FR_Y14Q_Instructions_chunk_001_body.md | Full | General Instructions, TOC, all preparatory guidance |
| FR_Y14Q_Instructions_chunk_002_body.md | Full | Schedule A: A.1 International Auto Loan, A.2 US Auto Loan |
| FR_Y14Q_Instructions_chunk_003_body.md | Full | Schedule A: A.3 International Credit Card, A.4 International Home Equity |
| FR_Y14Q_Instructions_chunk_004_body.md | Full | Schedule A: A.5 Int'l First Lien Mortgage, A.6 Int'l Other Consumer, A.7 US Other Consumer |
| FR_Y14Q_Instructions_chunk_005_body.md | Full | Schedule A: A.8 Int'l Small Business, A.9 US Small Business, A.10 Student Loan |
| FR_Y14Q_Instructions_chunk_006_body.md | Full | Schedule A summary vars 21-23 (end), Schedule B Securities intro, B.1 Main Schedule field instructions |
| FR_Y14Q_Instructions_chunk_007_body.md | Full | Schedule B.2 Securities 2 (Investment Securities with Designated Accounting Hedges) instructions |
| FR_Y14Q_Instructions_chunk_008_body.md | Full | Schedule C Regulatory Capital Instruments: General guidance, C.1 Quarter End columns, C.2 Repurchases/Redemptions |
| FR_Y14Q_Instructions_chunk_009_body.md | Full | Schedule C.3 Issuances During Quarter columns, Schedule D Regulatory Capital lines 1-12 |
| FR_Y14Q_Instructions_chunk_010_body.md | Full | Schedule D lines 13-M1, Schedule E Operational Risk (E.1-E.5), Schedule F Trading (general, glossary, F.1-F.6) |
| FR_Y14Q_Instructions_chunk_011_body.md | Full | Schedule F Trading continued: F.7 Rates Vega, F.8 Other Rates, F.9 Energy, F.10 Metals, F.11 Ags & Softs, F.12 Commodity Indices, F.13 Commodity Spot-Vol Grids, F.14 Securitized Products, F.15 Agencies |
| FR_Y14Q_Instructions_chunk_012_body.md | Full | Schedule F Trading continued: F.16 Munis, F.17 ARS, F.18 Corporate Credit-Advanced, F.19 Corporate Credit-Emerging Markets, F.20 Sovereign Credit, F.21 Credit Correlation |
| FR_Y14Q_Instructions_chunk_013_body.md | Full | Schedule F Trading end: F.22 IDR-Corporate Credit, F.23 IDR-Jump to Default, F.24 Private Equity, F.25 Other Fair Value Assets |
| FR_Y14Q_Instructions_chunk_014_body.md | Full | Schedule G PPNR: General Technical Details, Materiality Thresholds, Terms, G.1 PPNR Submission Worksheet (Revenue/NII/Noninterest Income by segment) |
| FR_Y14Q_Instructions_chunk_015_body.md | Full | Schedule G PPNR continued: G.1 Noninterest Expense Components (items 28-42), G.2 PPNR Net Interest Income Worksheet (average assets/liabilities/rates, items 1-49) |
| FR_Y14Q_Instructions_chunk_016_body.md | Full | Schedule G.3 PPNR Metrics: Section A Metrics by Business Segment/Line (items 1-40), Section B Firm Wide Metrics PPNR Projections (items 41-49), Section C Firm Wide Metrics NII (items 50-85 incl WAL assets/liabilities, deposit repricing betas, time deposit pricing) |
| FR_Y14Q_Instructions_chunk_017_body.md | Full | Schedule H Wholesale Risk: H.1 Corporate Loan Data Schedule introduction, loan population (11 HC-C categories, $1M threshold), reporting specifications, obligor financial data section instructions, data format (XML) |
| FR_Y14Q_Instructions_chunk_018_body.md | Full | Schedule H.1 Corporate Loan Data Fields 1-27: Obligor identification, industry codes, risk rating, external identifiers, credit facility IDs/dates/type (20 types)/purpose (31 purposes), exposure amounts, FR Y-9C line mapping, line of business |
| FR_Y14Q_Instructions_chunk_019_body.md | Full | Schedule H.1 Corporate Loan Data Fields 28-51: Charge-offs, delinquency, participation/SNC, lien position, security type, interest rate (variability/rate/index incl SOFR/spread/ceiling/floor), tax status, guarantor info, primary repayment entity |
| FR_Y14Q_Instructions_chunk_020_body.md | Full | Schedule H.1 Corporate Loan Data Fields 52-80: Obligor Financial Data Section (financials dates, net sales current/prior, operating income, D&A, interest expense, net income current/prior, cash/A-R/inventory/current assets current/prior, tangible/fixed/total assets, A-P/current liabilities current/prior, ST/LT debt, minority interest, total liabilities) |
| FR_Y14Q_Instructions_chunk_021_body.md | Full | Schedule H.1 Corporate Loan Data Fields 81-99: Retained Earnings, Capital Expenditures, SPE Flag, LOCOM, SNC Credit ID, PD/LGD/EAD, Renewal Date, Currency, Collateral Market Value, Prepayment Penalty, Entity Industry Code, Participation Interest, Leveraged Loan Flag, Disposition Flag/Schedule Shift |
| FR_Y14Q_Instructions_chunk_022_body.md | Full | Schedule H.1 Fields 100-112 (Syndicated Loan Flag/Target Hold, ASC326-20/PCD, Fair Value fields, LEIs) + Schedule H.2 CRE intro (Loan Population/Cross-Collateralized/Reporting Specs/Data Format) + H.2 Fields 1-18 |
| FR_Y14Q_Instructions_chunk_023_body.md | Full | Schedule H.2 CRE Fields 19-39: Maturity Date, Amortization, Recourse, Occupancy, Anchor Tenant, Loan Purpose, Interest Rate fields, Interest Reserves, Origination Amount, Acquired Loan, Days Past Due, Non-Accrual, Property Size |
| FR_Y14Q_Instructions_chunk_024_body.md | Full | Schedule H.2 CRE Fields 40-58: NOI Current, Valuation fields, Cross-Collateralization, TDR, LOCOM, SNC, Renewal Date, Currency, Occupancy Date, Value Basis, Prepayment Penalty |
| FR_Y14Q_Instructions_chunk_025_body.md | Full | Schedule H.2 CRE Fields 59-67: Participation Interest, Leveraged Loan Flag, Disposition Flag/Schedule Shift, ASC326-20/PCD, Current Maturity Date, Par Value fields |
| FR_Y14Q_Instructions_chunk_026_body.md | Full | Schedule H.2 CRE Fields 68-72, H.3 Line of Business (2 fields), H.4 Internal Risk Rating (5 fields), Schedule J Retail FVO/HFS (12 line items + vintage matrix) |
| FR_Y14Q_Instructions_chunk_027_body.md | Full | Schedule K Supplemental (Columns A-F), Reference Table K.1 (30+ loan categories with HC-C mappings), Schedule L Counterparty introduction (18 sub-schedules, exposure universe, CCP rules) |
| FR_Y14Q_Instructions_chunk_028_body.md | Full | Schedule L Counterparty: L.1.a/L.1.b (top 95% unstressed/stressed CVA, all field instructions with MDRM codes), L.1.e aggregate CVA (4 tables), L.1.f residual metrics (6 regions) |
| FR_Y14Q_Instructions_chunk_029_body.md | Full | Schedule L Counterparty: L.2 EE Profile (tenor/EE/PD/LGD/DF), L.3 Credit Quality (spreads/mapping/proxy), L.4 CVA Sensitivities (aggregate + top 10 by risk factor) |
| FR_Y14Q_Instructions_chunk_030_body.md | Full | Schedule L Counterparty: L.5 Derivatives/SFT Profile (L.5.1-L.5.4, 30+ fields, 14 derivative types, 30 SFT asset sub-categories), Schedule M Balances M.1 Quarter-end (HFI/HFS lines 1.a-1.c) |
| FR_Y14Q_Instructions_chunk_031_body.md | Full | Schedule M.1 Line Items 2.a-6 (C&I, small business, cards, consumer, commercial), M.2 FR Y-9C Reconciliation (5 portfolio types), M.3 Principal Balance by PCD Status (Part I Book Value/UPB, Part II Cumulative Interim Loan Losses) |
| FR_Y14Q_Instructions_chunk_032_body.md | Full | Appendix A: Supporting Documentation for Schedules C, D, L (Trading IDL 8 areas, CVA Losses 6 areas, CDL 9 areas, Supplemental Data Collection) |

### Table Files (CSV)
| File | Content |
|------|---------|
| FR_Y14Q_Instructions_chunk_001_table_001.csv | FR Y-14Q Filing Schedule (Risk Factors, Firm Category, Frequency, Data as-of-date, Submission deadlines) |
| FR_Y14Q_Instructions_chunk_007_table_001.csv | Schedule B.2 Securities 2 Field Specifications (15 fields: Identifier Type/Value, Amortized Cost, Market Value, Accounting Intent, Hedge Type/Risk/Rate/Percentage/Horizon/Cash Flow, Sidedness, Instrument Fair Value, Cumulative Gains/Losses, ASU 2017-12 Designations) |
| FR_Y14Q_Instructions_chunk_010_table_001.csv | Schedule E.1 Operational Loss Data Collection Schedule (18 fields: A-R including Unique ID, Reference Number, Dates, Thresholds, Gross Loss, Recovery, Basel Event-Types, Business Lines, UOM, Description) |
| FR_Y14Q_Instructions_chunk_010_table_002.csv | Reference Table E.1.a: Level 1 and Level 2 Event-Types (7 Level 1 categories with 20 Level 2 subcategories and definitions) |
| FR_Y14Q_Instructions_chunk_010_table_003.csv | Reference Table E.1.b: Level 1 and Level 2 Business Lines (9 Level 1 categories with 21 Level 2 subcategories and activity groups) |
| FR_Y14Q_Instructions_chunk_010_table_004.csv | Schedule F Regional Groupings (6 regions, 190+ countries with currency codes for Trading schedule geographic categorization) |
| FR_Y14Q_Instructions_chunk_018_table_001.csv | Schedule H.1 Corporate Loan Data Fields 1-27 (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values) |
| FR_Y14Q_Instructions_chunk_019_table_001.csv | Schedule H.1 Corporate Loan Data Fields 28-51 (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values) |
| FR_Y14Q_Instructions_chunk_020_table_001.csv | Schedule H.1 Corporate Loan Data Fields 52-80: Obligor Financial Data Section (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values) |
| FR_Y14Q_Instructions_chunk_021_table_001.csv | Schedule H.1 Corporate Loan Data Fields 81-99 (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values) |
| FR_Y14Q_Instructions_chunk_022_table_001.csv | Schedule H.1 Corporate Loan Data Fields 100-112 (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values) |
| FR_Y14Q_Instructions_chunk_022_table_002.csv | Schedule H.2 CRE Data Fields 1-18 (Field No, Field Name, Technical Field Name, MDRM (CRED), Description, Allowable Values, Mandatory/Optional) |
| FR_Y14Q_Instructions_chunk_023_table_001.csv | Schedule H.2 CRE Data Fields 19-39 (Field No, Field Name, Technical Field Name, MDRM (CRED), Description, Allowable Values, Mandatory/Optional) |
| FR_Y14Q_Instructions_chunk_024_table_001.csv | Schedule H.2 CRE Data Fields 40-58 (Field No, Field Name, Technical Field Name, MDRM (CRED), Description, Allowable Values, Mandatory/Optional) |
| FR_Y14Q_Instructions_chunk_025_table_001.csv | Schedule H.2 CRE Data Fields 59-67 (Field No, Field Name, Technical Field Name, MDRM (CRED), Description, Allowable Values, Mandatory/Optional) |
| FR_Y14Q_Instructions_chunk_026_table_001.csv | Schedule H.2 CRE Data Fields 68-72 (Field No, Field Name, Technical Field Name, MDRM, Description, Allowable Values, Mandatory/Optional) |
| FR_Y14Q_Instructions_chunk_026_table_002.csv | Schedule H.3 Line of Business Field Specifications (2 fields: LineOfBusinessName, LineOfBusinessDescription) |
| FR_Y14Q_Instructions_chunk_026_table_003.csv | Schedule H.4 Internal Risk Rating Field Specifications (5 fields: InternalRating, InternalRatingDescription, MinimumPD, MaximumPD, PD Calculation Method) |
| FR_Y14Q_Instructions_chunk_027_table_001.csv | Reference Table K.1: Loan Categories with FR Y-9C HC-C line references (30+ categories: Student Loans, Other Consumer, First Lien, Junior Lien, Cards, Auto, CRE, Farmland, C&I, Other) |
| FR_Y14Q_Instructions_chunk_030_table_001.csv | Schedule L.5.4 Derivative Types (14 types: Vanilla IR/FX/Commodity/Credit/Equity, Structured IR/FX/Credit, Exotic Equity, Hybrids, Structured Products, Other -- with Unstressed/Stressed MtM MDRM codes) |
| FR_Y14Q_Instructions_chunk_030_table_002.csv | Schedule L.5.2 SFT Asset Categories (30 sub-categories across 9 asset categories: Central Debt, Equity, Corporate Bonds, ETFs, Agency MBS/CMBS, Non-Agency, Cash, Other -- with 4 MDRM codes each for Unstressed/Stressed Posted/Received) |

## Key Regulatory Details Extracted

### Reporting Thresholds
- **General**: $100 billion total consolidated assets (4-quarter average)
- **Trading/Counterparty**: Category I-III firms with $50B+ aggregate trading assets/liabilities or 10%+ of total consolidated assets
- **Category IV materiality**: $5B or 10% of Tier 1 capital
- **Category I-III materiality**: $5B or 5% of Tier 1 capital

### Portfolio IDs Reference
| Schedule | Portfolio ID | Segments |
|----------|-------------|----------|
| A.1 Int'l Auto Loan | IntAuto | 216 |
| A.2 US Auto Loan | Auto | 12,960 |
| A.3 Int'l Credit Card | IntCard | 360 |
| A.4 Int'l Home Equity | IntHE | 480 |
| A.5 Int'l First Lien Mortgage | IntFM | 480 |
| A.6 Int'l Other Consumer | IntlOthCons | 600 |
| A.7 US Other Consumer | USOthCons | 225 |
| A.8 Int'l Small Business | IntSB | 720 |
| A.9 US Small Business | USSB | 180 |
| A.10 Student Loan | Student | 600 |

## Quality Notes
- All text extracted from text-layer PDFs (no OCR needed)
- No content-filter blocks encountered
- All 32 chunks fully processed with complete body text and table extraction
- All chunk body files contain complete, accurate extraction of the source content
- Chunk 016 contains no structured tables (all line item instructions in body text)
- Chunks 018-020 each contain one large field specification table for H.1 Corporate Loan Data
- Chunk 021 contains one field spec table continuing H.1 (Fields 81-99)
- Chunk 022 contains two tables: H.1 Fields 100-112 and H.2 Fields 1-18
- Chunks 023-025 each contain one field spec table for H.2 CRE Data
- Chunk 026 contains three tables: H.2 Fields 68-72, H.3 Line of Business, H.4 Internal Risk Rating
- Chunk 027 contains one table: Reference Table K.1 loan categories
- Chunks 028-029 contain no structured tables (field-by-field instructions in body text)
- Chunk 030 contains two tables: L.5.4 Derivative Types and L.5.2 SFT Asset Categories with MDRM codes

## Extraction Quality: COMPLETE (32/32)
- **Hollow chunks**: 0
- **Tables extracted**: 21
- **Body text files**: 32
- **Total output files**: 54 (including this report)
