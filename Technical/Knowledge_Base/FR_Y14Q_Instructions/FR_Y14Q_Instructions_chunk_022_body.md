# FR Y-14Q Instructions -- Schedule H.1 Corporate Loan Data Fields (Fields 100-112) and Schedule H.2 Commercial Real Estate (Introduction, Fields 1-18)

## H.1 Field Specifications Part 5 -- Syndicated Loan Pipeline, CECL, Fair Value, and LEI Fields

### Field 100 -- Syndicated Loan Flag (SyndicatedLoanFlag)
- Report whether the syndicated loan commitment is single signed by the BHC or IHC or SLHC, counter signed by the borrower (dual signed), or closed but not yet settled, or closed and settled.
- Closed and settled refers to the final phase where loan documents are fully executed and binding with post-closing selldown to all participants complete.
- Loans which have closed but are still pending execution of final documentation by all syndicate participants should be reported as option 3 (Closed but not settled).
- For loans that are not syndicated, indicate option 0 (NA).
- **Values**: 0 = NA; 1 = Single-signed; 2 = Dual-signed; 3 = Closed but not settled; 4 = Closed and settled

### Field 101 -- Target Hold (TargetHold)
- For loans in the syndicated loan pipeline (Options 1, 2 or 3 in Field 100), report the percentage of the total commitment the BHC or IHC or SLHC intends to hold.
- If the credit facility is reported as option 0 (NA) or option 4 (closed and settled) in Field 100, report NA.
- **Format**: Express as a decimal to 4 decimal places (e.g., 0.05% is 0.0005). Use decimal format; do not use scientific notation.

### Field 102 -- ASC326-20 (ASC32620)
- Report the allowance for credit losses per ASC 326-20.
- Provide at the credit facility level if available, otherwise report a pro-rated allocation from the collective (pool) basis.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar sign, commas, or decimals. Should be 0 if there is no ASC326-20 Reserve for the loan.

### Field 103 -- Purchased Credit Deteriorated Noncredit Discount (PCDNoncreditDiscount)
- If the facility is a purchased credit-deteriorated (PCD) asset, report the noncredit discount (or premium) resulting from its acquisition (ASC 326-20-30-13).
- Provide at the credit facility level if available, otherwise report a pro-rated allocation from the collective (pool) basis.
- Leave blank if the facility is not considered a PCD asset.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimals.

### Field 104 -- Current Maturity Date (CurrentMaturityDate)
- Report the maturity date as the last date upon which the funds must be repaid, exclusive of extension options.
- For demand loan, enter '9999-01-01'.
- For corporate loans in the syndicated pipeline, until the syndicated loan is reported as closed and settled (option 4 in Field 100), report the estimated maturity date based on the tenor stated in the commitment letter.
- For commitments to commit which are not syndicated, report the estimated maturity date based on the tenor in the terms extended to the borrower.
- **Format**: yyyy-mm-dd (e.g., 2005-02-01)

### Field 105 -- Committed Exposure Global Par Value
- For held for sale loans and loans accounted for under a fair value option, report the total commitment amount as the amount the obligor is contractually allowed to borrow according to the credit agreement for the entire credit facility.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.

### Field 106 -- Utilized Exposure Global Par Value
- For held for sale loans and loans accounted for under a fair value option, report the outstanding funded exposure.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.

### Field 107 -- Committed Exposure Global Fair Value
- For held for sale loans and loans accounted for under a fair value option, report the fair value of the entire credit facility.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.

### Field 108 -- Utilized Exposure Global Fair Value
- For held for sale loans and loans accounted for under a fair value option, report the fair value of the outstanding funded exposure.
- If not held for sale or accounted for under a fair value option, report 'NA'.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal. For negative values use a negative sign '-', not parentheses.

### Field 109 -- DO NOT USE

### Field 110 -- DO NOT USE

### Field 111 -- Obligor LEI (ObligorLEI)
- Report the Legal Entity Identifier (LEI) of the obligor identified in Field 4, if available.
- A LEI is a 20 character alphanumeric code that uniquely identifies legally distinct entities that engage in financial transactions. LEIs are issued by Local Operating Units (LOUs) of the Global LEI System.
- If LEI does not apply, enter 'NA'.
- **Format**: Valid 20 character alphanumeric LEI issued by a LOU of the Global LEI System, or 'NA'.

### Field 112 -- Primary Source of Repayment LEI (PSRLEI)
- If the primary source of repayment is provided by an entity that is different from the obligor identified in Field 4, report the Legal Entity Identifier (LEI) of the entity identified in Field 50 if available.
- If LEI does not apply, enter 'NA'.
- Leave blank if the entity is the same as the Obligor identified in Field 2.
- **Format**: Valid 20 character alphanumeric LEI issued by a LOU of the Global LEI System, or 'NA'.

---

## H.2 -- Commercial Real Estate Schedule

### A. Loan Population

The loan population includes Commercial real estate (CRE) loans and leases that are held for investment (HFI) (as defined in the FR Y-9C, Schedule HC-C General Instructions) and held for sale (HFS) as of the report date (e.g. quarter end). Include HFI and HFS loans that the holding company has elected to report at fair value under the fair value option. Exclude all loans and leases classified as trading (reportable on the FR Y-9C, Schedule HC, item 5). Also exclude Paycheck Protection Program (PPP) loans from this schedule.

CRE loans and leases are defined as loan commitments or credit facilities to an obligor as defined in the credit agreement. Include all CRE loans and leases that are at the consolidated BHC, IHC and SLHC level and not just those of the banking subsidiaries, as well as any unused commitments that are reported in Schedule HC-L that would be reported in the relevant FR Y-9C category if such loans were drawn (including all undrawn commitments extended to non-consolidated variable interest entities and commitments to commit as defined in the FR Y-9C).

In addition to CRE loans that are currently active as of the reporting date, the loan population should also include CRE loans that were disposed of during the reporting period. For purposes of this schedule, refer to Field 61 (Disposition Flag) for specific instructions on instances of disposed CRE loans.

Include all CRE loans and leases with a committed balance greater than or equal to **$1 million**.

All CRE loans included in this schedule must be **secured by real estate** (as defined in the FR Y-9C Glossary entry for "loans secured by real estate"). Loans to finance CRE but not secured by CRE do not meet the definition and should not be reported on the CRE Schedule. For example, a line of credit issued for the purpose of acquiring real estate that is not currently secured by real estate would not be considered secured by real estate for purposes of this Schedule.

#### FR Y-9C, Schedule HC-C Categories Considered CRE Loans:
1. **1-4 family residential construction loans** originated in domestic offices (item 1.a(1)) and in non-domestic offices (within item 1)
2. **Other construction loans and all land development and other land loans** originated in domestic offices (item 1.a(2)) and in non-domestic offices (within item 1)
3. **Loans secured by multifamily (5 or more) residential properties** originated in domestic offices (item 1.d) and in non-domestic offices (within item 1)
4. **Loans secured by other nonfarm nonresidential properties** originated in domestic offices (item 1.e(2)) and in non-domestic offices (within item 1)

**Owner-occupied nonfarm nonresidential properties** should be reported on the FR Y-14Q Corporate Loans Schedule (primary source of repayment from ongoing operations, not third-party rental income; rental income < 50% of repayment source).

#### Reporting at Credit Facility Level
- A credit facility is defined as a credit extension to a legal entity under a specific credit agreement.
- The $1 million reportability threshold applies to any set of commitments governed under one common credit agreement.
- Each facility should be reported separately; multiple draws within a facility should be consolidated at the facility level.
- For credit facilities containing loans under multiple FR Y-9C line items, the underlying loans should be aggregated and reported on the respective FR Y-14Q schedules.

**Cross-schedule allocation example**: A credit facility with Loan 1 ($2M on HC-C item 4.a), Loan 2 ($1M on HC-C item 4.b), Loan 3 ($500K on HC-C item 1.e(1)), and Loan 4 ($500K on HC-C item 1.d) -- loans 1-3 aggregate to $3.5M on Corporate Loans schedule, loan 4 reported as $500K on CRE schedule. All loans within the facility are reported including those under the credit facility threshold.

### B. Instructions for Cross Collateralized Loans

CRE loans with balances less than $1 million are subject to a **limited data collection** if they are cross collateralized with a CRE loan with a committed balance >= $1 million. Cross-collateralized loans are those in which the collateral securing one loan is also used as collateral for other loans. A single loan secured by multiple properties is NOT considered cross-collateralized. Lien position does not impact determinations.

**Limited data collection fields** for cross-collateralized CRE loans < $1 million:
1. Field 1, Loan Number
2. Field 3, Outstanding Balance
3. Field 5, Committed Exposure Global
4. Field 44, Cross Collateralized Loan Numbers

All other fields are optional for these loans.

### C. Reporting Specifications

- Report all loan and lease financing receivables consistent with the FR Y-9C instructions.
- **HFI loans**: amortized cost
- **HFS loans**: lower of cost or fair value
- **FVO loans**: fair value
- For acquired loans (see Field 36), report data retrievable from loan accounting systems of record reported on a prospective basis.
- All dollar amounts represent only the consolidated holding company's pro-rata portion of any syndicated or participated loan.
- All amounts in U.S. dollars.

### D. Data Format

- Single extensible markup language file (.xml)
- No quotation marks as text identifiers
- No header or row count
- One record per active loan
- For date fields where XSD specifies datetime, provide T00:00:00 as the time

### E. Commercial Real Estate Data Fields

The following fields should be contained in the submission file. Report all fields with data as of the report date. For disposed CRE loans, report all Fields as of the date of disposition, unless otherwise instructed in individual Field descriptions.

#### Field 1 -- Loan Number (LoanNumber)
- **MDRM (CRED)**: G063
- Report the reporting entity's unique internal identifier for this credit facility record as of the most recent filing date. Must identify the credit facility for its entire life and must be unique.
- If the Loan Number changes (e.g., system migration or acquisition), also provide Original/Previous Loan Number in Field 35.
- **Mandatory**

#### Field 2 -- Obligor Name (ObligorName)
- **MDRM (CRED)**: 9017
- Report the obligor name on the loan. Full legal entity name is desirable. If the borrowing entity is an individual (Natural Person), substitute with "Individual".
- **Mandatory**

#### Field 3 -- Outstanding Balance (OutstandingBalance)
- **MDRM (CRED)**: K448
- Report all loan and lease financing receivables consistent with FR Y-9C instructions. Amortized cost for HFI, lower of cost or fair value for HFS, fair value for FVO.
- For fully undrawn commitments, report 0. For disposed credit facilities, report 0.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar sign, commas, or decimal.
- **Mandatory**

#### Field 4 -- Line Reported on FR Y-9C (LineReportedOnFRY9C)
- **MDRM (CRED)**: K449
- Report the integer code corresponding to the HC-C line number. If multiple loans, report the type with the largest share.
- **Values**:
  - 1 = 1-4 family residential construction, domestic (HC-C item 1.a(1))
  - 2 = Other construction and land development, domestic (HC-C item 1.a(2))
  - 3 = Multifamily (5+) residential, domestic (HC-C item 1.d)
  - 4 = DO NOT USE
  - 5 = Other nonfarm nonresidential, domestic (HC-C item 1.e(2))
  - 6 = DO NOT USE
  - 7 = CRE originated by non-domestic offices (within HC-C item 1), excluding nonfarm nonresidential owner occupied
- **Mandatory**

#### Field 5 -- Committed Exposure Global (CommittedBalance)
- **MDRM (CRED)**: G074
- Report the total commitment amount as the sum of HC-C financing receivables (Field 3) plus unused commitments from HC-F, HC-G, and HC-L. For multiple lenders, only the reporting entity's pro-rata commitment.
- For commitments to commit, report the total commitment amount approved and offered to the borrower.
- **Format**: Rounded whole dollar amount. No dollar sign, commas, or decimal.
- **Mandatory**

#### Field 6 -- Cumulative Charge-offs (CumulativeChargeoffs)
- **MDRM (CRED)**: G076
- Report the cumulative net charge-offs over the life of the credit facility. If charge-offs exceed current commitment but are less than original, report total.
- For disposed loans, report as of date of disposition.
- Should be '0' if no charge-off; 'NA' for HFS or FVO loans.
- **Mandatory**

#### Field 7 -- Participation Flag (ParticipationFlag)
- **MDRM (CRED)**: 6135
- Indicate if the CRE Loan is participated or syndicated among other financial institutions and if it is part of the Shared National Credit Program. For fronting exposures, report 'No'.
- **Values**:
  - 1 = No
  - 2 = Yes, syndicate/participant but not SNC
  - 3 = Yes, agent in syndication but not SNC
  - 4 = Yes, syndicate/participant in SNC
  - 5 = Yes, agent in SNC
- **Mandatory**

#### Field 8 -- Lien Position (LienPosition)
- **MDRM (CRED)**: K450
- First lien, subordinated, mixed (if no property predominates), or B-Note. For partnership interest pledges, indicate subordinate lien.
- **Values**: 1 = First Lien; 2 = Subordinated Lien; 3 = Mixed Liens; 4 = DO NOT USE; 5 = "B-Note"
- **Mandatory**

#### Field 9 -- Property Type (PropertyType)
- **MDRM (CRED)**: K451
- Report predominant property type by highest collateral value. If no single type predominates, report "Mixed". If land and lot development ONLY (no vertical construction), report as such.
- **Values**:
  - 1 = Retail
  - 2 = Industrial (excluding warehouse/distribution)
  - 3 = Hotel/Hospitality/Gaming (including Resorts)
  - 4 = Multi-family for Rent (including low income housing)
  - 5 = Homebuilders except condo
  - 6 = Condo/Co-op
  - 7 = Office (including medical office)
  - 8 = Mixed
  - 9 = Land and Lot Development
  - 10 = Other
  - 11 = Healthcare (including hospitals, assisted living, memory care, skilled nursing)
  - 12 = Warehouse/Distribution
- **Mandatory**

#### Field 10 -- Origination Date (OriginationDate)
- **MDRM (CRED)**: 9912
- Report the contractual date of the credit agreement (date commitment becomes legally binding). Major modifications with new/amended credit agreements use revised date. The following do NOT change origination date: extension options, covenants, waivers, maturity changes, re-pricing, periodic credit reviews, or TDR.
- For commitments to commit, report the date BHC/IHC/SLHC extended terms.
- **Format**: yyyy-mm-dd. Must be before or equal to period end date.
- **Mandatory**

#### Field 11 -- Location (Location)
- **MDRM (CRED)**: K453
- Five-digit ZIP Code for US locations (including territories). Two-letter ISO country code for foreign properties. "Multiple" if secured by multiple properties with none predominating.
- **Mandatory**

#### Field 12 -- Net Operating Income at Origination (NetOperatingIncome)
- **MDRM (CRED)**: K454
- Report NOI at origination (date in Field 10). NOI = all operating income net of operating expenses, except debt service and depreciation. Operating expenses include RE taxes, insurance, CAM, utilities, replacement reserves, management fees, admin/accounting/legal.
- For land and construction loans not generating income and not cross-collateralized with income-generating property, report 'NA'.
- NOI should represent best estimate of actual NOI at origination, not forward-looking projections.
- For participations, prorate based on share. For cross-collateralized loans, report total NOI from underlying collateral pool (same value for each cross-collateralized loan).
- **Format**: Rounded whole dollar amount. Negative values use '-' not parentheses.
- **Mandatory**

#### Field 13 -- Value at Origination (ValueatOrigination)
- **MDRM (CRED)**: M148
- Report property value at origination (from appraisal or evaluation per 12 CFR 34 and bank policy). Value is prorated for bank's ownership interest. For multiple properties, report sum. For cross-collateralization, report sum of all property values.
- **Format**: Rounded whole dollar amount. No dollar signs, commas, or decimals.
- **Mandatory**

#### Field 14 -- Value Basis (ValueBasis)
- **MDRM (CRED)**: K456
- Indicate whether Value in Field 13 was calculated using "as is," "as stabilized" or "as completed" value as defined in SR10-16.
- **Values**: 1 = As Is; 2 = As Stabilized; 3 = As Completed
- **Mandatory**

#### Field 15 -- Internal Rating (InternalRating)
- **MDRM (CRED)**: G080
- Report the bank's internal obligor rating addressing probability of default. Format as rating code:fraction pairs separated by semicolons.
- Example: "AAA:1" for entirely AAA rated; "A:0.5;C:0.5" for split rated. All decimals must sum to 1.
- Must be consistent with Schedule H.4 (Internal Risk Rating Schedule), Field 1.
- **Mandatory**

#### Field 16 -- Probability of Default (PD)
- **MDRM (CRED)**: G082
- Advanced approaches firms: report advanced IRB PD. Defaulted obligor = 1. Non-advanced firms: report PD corresponding to Internal Rating. If no PD assigned, report 'NA'.
- **Format**: Decimal to 4 places (e.g., 50% is 0.5000). No scientific notation.
- **Mandatory**

#### Field 17 -- Loss Given Default (LGD)
- **MDRM (CRED)**: G086
- Advanced approaches firms: report advanced IRB LGD at loan level. Multiple loans: dollar weighted average. Non-advanced firms: report LGD from credit risk management system. If not assigned, report 'NA'.
- **Format**: Decimal to 2 decimal places (e.g., 50% is 0.50). No scientific notation.
- **Mandatory**

#### Field 18 -- Exposure At Default (EAD)
- **MDRM (CRED)**: G083
- Advanced approaches firms: report advanced IRB EAD parameter. Multiple loans: dollar weighted average. Non-advanced firms: report EAD from internal system. If not assigned, report 'NA'.
- **Format**: Rounded whole dollar amount (e.g., 20000000). No dollar sign, commas, or decimal.
- **Mandatory**
