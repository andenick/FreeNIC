# FR 2052a Instructions - Chunk 003
## Field Definitions (continued)

### Counterparty Types (continued)

#### Investment Company or Advisor
Refers to a person or company registered with the SEC under the Investment Company Act of 1940 (15 U.S.C. 80a-1 et seq.); a company registered with the SEC as an investment adviser under the Investment Advisers Act of 1940 (15 U.S.C. 80b-1 et seq.); or foreign equivalents of such persons or companies. An investment company or advisor does not include small business investment companies, as defined in section 102 of the Small Business Investment Act of 1958 (15 U.S.C. 661 et seq.).

#### Financial Market Utility
Refers to a designated financial market utility, as defined in section 803 of the Dodd-Frank Act (12 U.S.C. 5462) and any company not domiciled in the United States (or a political subdivision thereof) that is supervised and regulated in a similar manner.

#### Other Supervised Non-Bank Financial Entity
1. A company that the Financial Stability Oversight Council has determined under section 113 of the Dodd-Frank Act (12 U.S.C. 5323) shall be supervised by the Board of Governors of the Federal Reserve System and for which such determination is still in effect;
2. A company that is not a bank, broker-dealer, investment company or advisor or financial market utility, but is included in the organization chart of a bank holding company or savings and loan holding company on the Form FR Y-6, as listed in the hierarchy report of the bank holding company or savings and loan holding company produced by the National Information Center (NIC) Web site;
3. An insurance company; and
4. Any company not domiciled in the United States (or a political subdivision thereof) that is supervised and regulated in a manner similar to entities described in paragraphs (1) through (3) of this definition (e.g., a non-bank subsidiary of a foreign banking organization, foreign insurance company, etc.).
5. A supervised non-bank financial entity does not include:
   - a. U.S. government-sponsored enterprises;
   - b. Entities designated as Community Development Financial Institutions (CDFIs) under 12 U.S.C. 4701 et seq. and 12 CFR part 1805; or
   - c. Central banks, the Bank for International Settlements, the International Monetary Fund, or multilateral development banks.

#### Debt Issuing Special Purpose Entity (SPE)
Refers to an SPE[^9] that issues or has issued commercial paper or securities (other than equity securities issued to a company of which the SPE is a consolidated subsidiary) to finance its purchases or operations. This counterparty type should only be used to identify stand-alone SPEs that issue debt and are not consolidated on an affiliated entity's balance sheet for purposes of financial reporting, except for exposures reported in the Outflows-Other table under products O.O.4: Credit Facilities and O.O.5: Liquidity Facilities. All debt issuing SPEs should be identified as Debt Issuing SPEs for products O.O.4 and O.O.5, regardless of whether they are consolidated by an affiliate for financial reporting.

[^9]: An SPE refers to a company organized for a specific purpose, the activities of which are significantly limited to those appropriate to accomplish a specific purpose, and the structure of which is intended to isolate the credit risk of the SPE.

#### Non-Regulated Fund
Refers to a hedge fund or private equity fund whose investment advisor is required to file SEC Form PF (Reporting Form for Investment Advisers to Private Funds and Certain Commodity Pool Operators and Commodity Trading Advisors), other than a small business investment company as defined in section 102 of the Small Business Investment Act of 1958 (15 U.S.C. 661 et seq.).

#### Other
Refers to any counterparty that does not fall into any of the above categories. Consult with your supervisory team before reporting balances using this counterparty type. Use the comments table to provide description of the counterparty on at least a monthly basis and in the event of a material change in reported values.

### Collateral Class

Use the asset category table in Appendix III to identify the type of collateral for all relevant inflows, outflows, and informational items.

- For securities that have multiple credit risk profiles, report the transaction or asset based on the lowest quality.
- Use the standardized risk weightings as specified under subpart D of Regulation Q (12 CFR part 217).
- Work with supervisory teams to address questions on the categorization of specific assets.

### Collateral Value

Refers to the fair value under GAAP of the referenced asset or pool of collateral, gross of any haircuts, according to the close-of-business marks on the as-of date. For pledged loans that are accounted for on an accrual basis, report the most recent available fair valuation.

### Maturity Bucket

Report the appropriate maturity time bucket value for each data element, based on the listing provided in Appendix IV.

- Report all information based on the contractual maturity of each data element.
  - In general, report maturities based upon the actual settlement of cash flows. For example, if a payment is scheduled to occur on a weekend or bank holiday, but will not actually settle until the next good business day, the maturity bucket must correspond to the date on which the payment will actually settle.
  - Do not report based on behavioral or projected assumptions.
- "Day" buckets refer to the number of calendar days following the as-of date (T). For example, "Day 1" (Calendar Day 1) represents balances on T+1 (maturing the next calendar day from T).
- Report transactions and balances that do not have a contractual maturity, but could be contractually realized on demand (e.g., demand deposits) as "Open".
- Report transactions and balances as "Perpetual" to the extent that they do not have a contractual maturity (or where the maturity is explicitly defined as perpetual), could not be contractually realized on demand or with notice at the inception of the transaction, and would not be subject to the maturity acceleration requirements of sections 31(a)(1)(i) or (iii) of the LRM Standards. For example, common equity included in regulatory capital should be reported with a [Maturity Bucket] value of "Perpetual".
- For transactions and balances with embedded optionality, report the maturity in accordance with sections 31(a)(1) and 31(a)(2) of the LRM Standards. For deferred tax liabilities, report the maturity in accordance with section 101(d) of the LRM Standards.
  - For transactions and balances with embedded optionality that are executed between affiliated reporting entities, where neither reporting entity is subject to the LRM Standards on a standalone basis, report the maturity according to the earliest possible date the transaction or balance could contractually be repaid.
- In the case of forward starting transactions with an open maturity, report the [Maturity Bucket] value equal to the [Forward Start Bucket] value until the forward start date arrives. Do not report the record with a [Maturity Bucket] value of "Open" until the forward starting leg actually settles.
- Report all executed transactions, including transactions that have traded but have not settled.
  - Do not report transactions that are anticipated, but have not yet been executed.
- Further guidance that is only relevant to specific products is provided in the product definitions section.

### Effective Maturity Bucket

*This field is only relevant for data elements in the Inflows-Assets, Inflows-Unsecured, Inflows-Secured, Supplemental-Derivatives & Collateral and Supplemental-Balance Sheet tables.* Report a maturity time bucket value in this field for all Inflows-Secured data elements where the asset has been re-used to secure or otherwise settle another transaction or exposure.

- The effective maturity date must align with the remaining period of encumbrance, irrespective of the original maturity of the transaction or exposure.
- With respect to an asset pledged to a collateral swap, if the asset received in the collateral swap has been rehypothecated to secure another transaction, in accordance with section 106(d)(2) of the LRM Standards, the effective maturity date of the on-balance sheet asset pledged to the collateral swap must align with the longer of the two encumbrances (i.e., either the maturity of the collateral swap, or the maturity of the transaction to which the asset received in the collateral swap has been pledged).
- For transactions where the collateral received has been rehypothecated and delivered into a firm short position, report an effective maturity date of "Open". Do not report an effective maturity date of "Open" if the collateral received has been delivered into any other type of transaction. Under circumstances where the collateral received via a secured lending transaction with an "Open" maturity date has been rehypothecated and delivered into another transaction with an "Open" maturity date that is not a firm short position, report a "Day 1" value in the [Effective Maturity Bucket] field.
- For transactions where the collateral received is generally re-used throughout the day to satisfy intraday collateral requirements for access to payment, clearance and settlement systems, report a "Day 1" value in the [Effective Maturity Bucket] field.

### Maturity Amount

Report the notional amount contractually due to be paid or received at maturity for each data element.

- All notional currency-denominated values should be reported in millions (e.g., U.S. dollar-denominated transactions in USD millions, sterling-denominated transactions in GBP millions).
- This amount represents the aggregate balance of trades, positions or accounts that share common data characteristics (i.e., common non-numerical field values). If the aggregate amount rounds to less than ten thousand currency units (i.e., 0.01 for this report), the record should not be reported.
  - Example: The banking entity has corporate customers with a total of $2.25 billion in operational and non-operational deposits, of which:
    - $1 billion is operational and fully FDIC insured with an open maturity;
    - $500 million is non-operational uninsured with an open maturity; and
    - $750 million is non-operational uninsured maturing on calendar day 5.
  - *(See Table 1 in CSV file: FR_2052a_Instructions_chunk_003_table_001.csv)*

### Forward Start Bucket

*This field is only relevant for data elements with a forward-starting leg (i.e., the trade settles at a future date).* Report the appropriate maturity bucket for the forward-starting settlement date of each applicable data element, based on the maturity buckets provided in Appendix IV. See the Supplemental-Foreign Exchange table guidance in the product definitions section for further instruction on how to report forward-starting foreign exchange transactions.

### Forward Start Amount

*This field is only relevant for data elements with a forward-starting leg.* In conjunction with the forward start bucket, report the notional amount due to be paid or received on the opening trade settlement date of forward starting transactions. See the Supplemental-Foreign Exchange table guidance in the product definitions section for further instruction on how to report forward-starting foreign exchange transactions.

### Internal

*This field is only relevant for data elements reporting transactions between FR 2052a reporting entities and designated internal counterparties (i.e., affiliated transactions).* Flag all data elements representing these transactions with a "Yes" in this field. Affiliated transactions are defined as all transactions between the reporting entity and any other entity external to the reporting entity that falls under the "Scope of the Consolidated Entity" as defined in these instructions (e.g., branches, subsidiaries, affiliates, VIEs, and IBFs).

### Internal Counterparty

*This field is only relevant for data elements reporting affiliated transactions.* Report the internal counterparty for affiliated transactions referenced above in this field.

### Treasury Control

*This field is only applicable to the Inflows-Assets, Inflows-Secured, Inflows-Other, Outflows-Secured and Supplemental-Derivatives & Collateral tables.* Use this field to flag ("Yes") assets, or transactions secured by assets that meet the operational requirements for eligible HQLA in the LRM Standards other than the requirement to be unencumbered, which addresses: the operational capability to monetize; policies that require control by the function of the bank charged with managing liquidity risk; policies and procedures that determine the composition; and not being client pool securities or designated to cover operational costs.

Do not set [Treasury Control]="Yes" in the Secured-Inflows table where the collateral received has been rehypothecated and pledged to secure a collateral swap where the collateral that must be returned at the maturity of the swap transaction does not qualify as HQLA per the FR 2052a Asset Category Table (Appendix III).

### Market Value

*This field is only applicable to the Inflows-Assets, Supplemental-Derivatives & Collateral, Supplemental-LRM, Supplemental-Balance sheet and Supplemental-Informational tables.* Report the fair value under GAAP for each applicable data element.

- In general, report values according to the close-of-business marks on the as-of date. For loans that are accounted for on an accrual basis, report the most recent available fair valuation.

### Lendable Value

*This field is only applicable to the Inflows-Assets table.* Report the lendable value of collateral for each applicable data element in the assets table.

- Lendable value is the value that the reporting entity could obtain for assets in secured funding markets after adjusting for haircuts due to factors such as liquidity, credit and market risks.

### Business Line

*This field is applicable to all tables except the Supplemental-LRM and Comments tables.* U.S. firms that are identified as Category I banking organizations are required to report this field.

Use this field to designate the business line responsible for or associated with all applicable exposures. Coordinate with the supervisory team to determine the appropriate representative values for this field.

### Settlement

*This field is only applicable to the Inflows-Secured, Outflows-Secured and Supplemental-Foreign Exchange tables.* Use this field to identify the settlement mechanisms used for Secured and Foreign Exchange products.

- Products in the **secured tables** should be classified using the following flags:
  - **FICC**: secured financing transactions that are cleared and novated to the Fixed Income Clearing Corporation (FICC)
  - **Triparty**: secured financing transactions settled on the US-based tri-party platform, excluding transactions that originate on the tri-party platform, but are novated to FICC (e.g., the General Collateral Finance repo service).
  - **Other**: secured financing transactions settled on other (e.g., non-US) third-party platforms (includes transactions that are initiated bilaterally, but are subsequently cleared through a CCP)
  - **Bilateral**: secured financing transactions settled bilaterally (excludes transactions that are initiated bilaterally, but subsequently cleared (e.g., FICC delivery-vs-payment transactions))
- Products in the **foreign exchange table** should be classified using the following flags:
  - **CLS**: FX transactions centrally cleared via CLS
  - **Other**: FX transactions settled via other (non-CLS) central clearinghouses
  - **Bilateral**: FX transactions settled bilaterally

### Rehypothecated

*This field is only applicable to the Outflows-Secured and Outflows-Deposits tables.* Use this field to flag ("Yes") data elements representing transactions or accounts secured by collateral that has been rehypothecated. Transactions should not be flagged as rehypothecated if they have not yet settled.

### Unencumbered

*This field is only applicable to the Inflows-Secured table.* Use this field to flag ("Yes") secured transactions where the collateral received is held unencumbered in inventory and: (i) the assets are free of legal, regulatory, contractual, or other restrictions on the ability of the reporting entity to monetize the assets; and (ii) the assets are not pledged, explicitly or implicitly, to secure or to provide credit enhancement to any transaction. Transactions should not be flagged as unencumbered if they have not yet settled. Do not flag secured transactions as unencumbered if the collateral received has been pre-positioned at a central bank or Federal Home Loan Bank (FHLB), as that collateral should also be reported under product I.A.2: Capacity.

### Insured

*This field is only applicable to the Outflows-Deposits table.* Use this field to identify balances that are fully insured by the FDIC or other foreign government-sponsored deposit insurance systems.

- **FDIC**: Refers to deposits fully insured by FDIC deposit insurance.
- **Other**: Refers to deposits that are fully insured by non-US local-jurisdiction government deposit insurance.
- **Uninsured**: Refers to deposits that are not fully insured by FDIC deposit insurance or other non-US local-jurisdiction government deposit insurance.

### Trigger

*This field is only applicable to the Outflows-Deposits table.* Use this field to flag ("Yes") deposit accounts that include a provision requiring the deposit to be segregated or withdrawn in the event of a specific change or "trigger", such as a change in a reporting entity's credit rating.

### Risk Weight

*This field is only applicable to the Inflows-Unsecured, Inflows-Secured and Supplemental-Balance Sheet tables.*

U.S. firms that are identified as Category IV banking organizations with average weighted short-term wholesale funding of less than $50 billion and FBOs that are identified as Category IV foreign banking organizations with average weighted short-term wholesale funding of less than $50 billion are not required to report on this field.

Use this field to designate the standardized risk weight of unsecured and secured lending transactions, as per 12 CFR 217 subpart D, along with any associated adjustments necessary to establish the balance sheet carrying value of these transactions.

### Collection Reference

*This field is only applicable to the Supplemental-Balance Sheet table.* Use this field to indicate the [Collection] (i.e., table) designation applicable to a reported adjustment. Adjustments should be designated using the following values: I.A., I.S, I.U, I.O, O.D, O.S, O.W., O.O and S.DC.

### Product Reference

*This field is only applicable to the Supplemental-Balance Sheet table.* Use this field to indicate the [Product] designation applicable to the reported adjustment.

### Sub-Product Reference

*This field is only applicable to the Supplemental-Balance Sheet table.* Use this field to indicate the [Sub-Product] designation applicable to the reported adjustment.

### Netting Eligible

*This field is only applicable to the Derivatives & Collateral table.* Use this field to identify the balances of variation margin posted and received under S.DC.8 through S.DC.10 that are eligible for netting per the conditions referenced in section 107(f)(1) of the LRM Standards.

### Encumbrance Type

*This field is only applicable to the Inflows-Assets, Inflows-Unsecured, Inflows-Secured and Supplemental-Derivatives & Collateral tables.* Use this field to categorize asset encumbrances according to the following types:

- **Securities Financing Transaction**: Refers to the encumbrance of assets to transactions reportable in the O.D., O.S and O.W tables, except for assets pledged to secure Covered Federal Reserve Facility Funding.
- **Derivative VM**: Refers to the encumbrance of assets delivered to satisfy calls for variation margin in response to change in the value of derivative positions.
- **Derivative IM and DFC**: Refers to the encumbrance of assets delivered to satisfy initial margin, default fund contributions or other comparable requirements, where the activity supported by these encumbrances includes derivatives.
- **Other IM and DFC**: Refers to the encumbrance of assets delivered to satisfy initial margin, default fund contributions or other comparable requirements, where the activity supported by these encumbrances does not include derivatives.
- **Segregated for Customer Protection**: Refers to encumbrances due to the segregation of assets held to satisfy customer protection requirements (e.g., 15c3-3, CFTC residual interest and other customer money protection requirements).
- **Covered Federal Reserve Facility Funding**: Refers to encumbrance reportable using product O.S.6: Exceptional Central Bank Operations with a sub-product of Covered Federal Reserve Facility Funding.
- **Other**: Refers to all other types of encumbrance. Use the comments table to provide additional detail on the underlying type of encumbrance on at least a monthly basis and in the event of a material change in reported values.

### Collateral Level

*This field is only applicable to the Supplemental-Derivatives & Collateral table.* Use this field to differentiate the derivative asset and liability values (S.DC.1 and 2) and the balances of variation margin posted and received (S.DC.8 through 10) for all derivative contracts (e.g., based on the collateralization requirements stipulated in the contractual terms of a derivative's credit support annex (CSA)):

- **Uncollateralized**: Refers to derivative asset and liability values that do not require exchange of variation margin (i.e., the transactions or netting sets are not governed by a CSA or the applicable CSA does not require the out-of-the-money counterparty, based on current market values, to provide variation margin).
- **Undercollateralized**: Refers to derivative asset and liability values and any associated balances of variation margin posted and received where the value of margin exchanged is less than the derivative asset or liability value for the transaction or associated derivative transaction or qualifying master netting agreement netting set (e.g., due to thresholds or minimum transfer amounts).
