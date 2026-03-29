# FR 2052a Instructions - Chunk 006
## Pages 50-59: Outflows-Secured (cont.), Outflows-Deposits, Outflows-Other (begins)

### O.S.4: Collateral Swaps (continued from Chunk 005)

Inflows-Secured tables. O.S.4 should be reported based on the collateral **pledged**. Report the [Collateral Class] according to the assets pledged. Report the fair value of these assets pledged in the [Collateral Value] field. Report the fair value of assets received in the [Maturity Amount] field. Use the [Sub-Product] field to identify the type of collateral **received** based on the asset categories defined in the LRM Standards:

- Level 1 Received
- Level 2a Received
- Level 2b Received
- Non-HQLA Received
- No Collateral Received

For collateral swaps where a non-cash asset is lent, report the [Collateral Class] according to the assets pledged and report the fair value of these assets pledged in the [Collateral Value] field.

### O.S.5: FHLB Advances

Refers to outstanding secured funding sourced from the FHLBs. The amount borrowed and the fair value of collateral pledged to secure the borrowing should not be included under product I.A.2: Capacity with [Counterparty] field set to "GSE".

### O.S.6: Exceptional Central Bank Operations

Refers to outstanding secured funding from central banks for exceptional central bank operations. Do not include transactions related to normal open market operations, which should be reported based on the transaction type (e.g., O.S.1: Repo) with the [Counterparty] field set to "Central Bank". The amount borrowed and the fair value of collateral pledged to secure the borrowing should not be included under product I.A.2: Capacity.

Use the [Sub-Product] field to further identify the specific source of secured funding provided according to the following groupings:

- FRB (Federal Reserve Bank)
- SNB (Swiss National Bank)
- BOE (Bank of England)
- ECB (European Central Bank)
- BOJ (Bank of Japan)
- RBA (Reserve Bank of Australia)
- BOC (Bank of Canada)
- OCB (Other Central Bank)
- FRFF (Covered Federal Reserve Facility Funding)

### O.S.7: Customer Shorts

Refers to a transaction where the reporting entity's customer sells a physical security it does not own, and the entity subsequently obtains the same security from an internal or external source to make delivery into the sale. External refers to a transaction with a counterparty that falls outside the scope of consolidation for the reporting entity. Internal refers to securities sourced from within the scope of consolidation of the reporting entity.

Use the [Sub-Product] field to further identify the appropriate source for delivery into the sale according to the following categories:

- **External Cash Transactions** -- Refers to securities sourced through a securities borrowing, reverse repo, or like transaction in exchange for cash collateral.
- **External Non-Cash Transactions** -- Refers to securities sourced through a collateral swap or like transaction in exchange for non-cash collateral.
- **Firm Longs** -- Refers to securities sourced internally from the reporting entity's own inventory of collateral where the sale does not coincide with an offsetting performance-based swap derivative.
- **Customer Longs** -- Refers to securities sourced internally from collateral held in customer accounts at the reporting entity.
- **Unsettled - Regular Way** -- Refers to sales that meet the definition of regular-way securities trades under GAAP, that have been executed, but not yet settled and therefore have not been covered. Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities sold. Report failed settlements with a [Forward Start Bucket] value of "Open".
- **Unsettled - Forward** -- Refers to sales that do not meet the definition of regular-way securities trades, that have been executed, but not yet settled and therefore have not been covered. Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities sold. Report failed settlements with a [Forward Start Bucket] value of "Open".

Note that the [Sub-Product] designation may differ between the Consolidated Firm reporting entity and a subsidiary reporting entity if the collateral delivered into the short is sourced from, for example, an affiliate's long inventory. For the subsidiary reporting entity, collateral sourced from an affiliate should be represented as sourced from an external transaction; however for the consolidated firm, this would be represented as sourced from a "Firm Long" position.

### O.S.8: Firm Shorts

Refers to a transaction where the reporting entity sells a security it does not own, and the entity subsequently obtains the same security from an internal or external source to make delivery into the sale. External refers to a transaction with a counterparty that falls outside the scope of consolidation for the reporting entity. Internal refers to securities sourced from within the scope of consolidation of the reporting entity.

Use the [Sub-Product] field to further identify the appropriate source for delivery into the sale according to the following categories:

- **External Cash Transactions** -- Refers to securities sourced through a securities borrowing, reverse repo, or like transaction in exchange for cash collateral.
- **External Non-Cash Transactions** -- Refers to securities sourced through a collateral swap or like transaction in exchange for non-cash collateral.
- **Firm Longs** -- Refers to securities sourced internally from the reporting entity's own inventory of collateral where the sale does not coincide with an offsetting performance-based swap derivative.
- **Customer Longs** -- Refers to securities sourced internally from collateral held in customer accounts at the reporting entity.
- **Unsettled - Regular Way** -- Refers to sales that meet the definition of regular-way securities trades under GAAP, that have been executed, but not yet settled and therefore have not been covered. Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities sold. Report failed settlements with a [Forward Start Bucket] value of "Open".
- **Unsettled - Forward** -- Refers to sales that do not meet the definition of regular-way securities trades, that have been executed, but not yet settled and therefore have not been covered. These transactions should also be included in the calculation of products I.O.7: Net 30-day Derivative Receivables and O.O.20: Net 30-day Derivative Payables. Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities sold. Report failed settlements with a [Forward Start Bucket] value of "Open".

Note that the [Sub-Product] designation may differ between the Consolidated Firm reporting entity and a subsidiary reporting entity if the collateral delivered into the short is sourced from, for example, an affiliate's long inventory. For the subsidiary reporting entity, collateral sourced from an affiliate should be represented as sourced from an external transaction; however for the consolidated firm, this would be represented as sourced from a "Firm Long" position.

### O.S.9: Synthetic Customer Shorts

Refers to total return swaps booked in client accounts, where the reporting entity is economically long the underlying reference asset and the client is economically short. Use the [Maturity Bucket] to designate the earliest date a transaction could be unwound or terminated. Use the [Collateral Class] field to designate the reference asset of the transaction. Use the following [Sub-Product] values to designate how the position is "covered" (i.e., hedged):

- **Firm Short** -- Refers to transactions where the associated hedge is a short sale by the reporting entity of the physical security (i.e., transactions reportable under O.S.8, excluding those with a [Sub-Product] of "Firm Longs".
- **Synthetic Customer Long** -- Refers to transactions where the customer synthetic short is hedged with another customer's synthetic long position reported in I.S.9.
- **Synthetic Firm Sourcing** -- Refers to transactions where the associated hedge meets the definition of I.S.10.
- **Futures** -- Refers to transactions hedged with futures contracts.
- **Other** -- Refers to all other methods of hedging.
- **Unhedged** -- Refers to positions that are not economically hedged with another instrument or transaction.

### O.S.10: Synthetic Firm Financing

Refers to a total return swaps that are not booked in client accounts, where the reporting entity is economically long the underlying reference asset and the counterparty is economically short. Use the [Maturity Bucket] to designate the earliest date a transaction could be unwound or terminated. Use the [Collateral Class] field to designate the reference asset of the transaction.

Use the following [Sub-Product] values to designate how the position is "covered" (i.e., hedged):

- **Firm Short** -- Refers to transactions where the associated hedge is a short sale by the reporting entity of the physical security (i.e., transactions reportable under O.S.8, excluding those with a [Sub-Product] of "Firm Longs".
- **Synthetic Customer Long** -- Refers to transactions hedged with a customer's synthetic long position reported in I.S.9.
- **Synthetic Firm Sourcing** -- Refers to transactions where the associated hedge meets the definition of I.S.10.
- **Futures** -- Refers to transactions hedged with futures contracts.
- **Other** -- Refers to all other methods of hedging.
- **Unhedged** -- Refers to positions that are not economically hedged with another instrument or transaction.

### O.S.11: Other Secured Financing Transactions

Refers to all other secured financing transactions that do not otherwise meet the definitions of Outflows-Secured products listed above, and for which rehypothecation rights over the collateral pledged are conferred to the reporting entity's counterparty. Use the comments table to provide a general description of other secured financing transactions included in this product on at least a monthly basis and in the event of a material change in reported values.

---

## O.D: Outflows-Deposits

**Collateralized Deposits** has the same meaning as it does under the LRM Standards.

For collateralized deposits, report the type of collateral using the [Collateral Class] field using the asset categories listed in the Asset Category Table (Appendix III). Report the fair value of collateral held against these deposits using the [Collateral Value] field.

**Insured Deposits:** Use the [Insured] field to distinguish between balances that are FDIC-insured, foreign deposits insured by a non-US local-jurisdiction government insurance system, and uninsured deposits as described in the field definitions section.

- FDIC
- Other
- Uninsured

**Instructions on reporting by counterparty:** Deposit products must be reported by the type of counterparty that made the deposit. Certain deposit products apply only to a subset of counterparty types. The lists of reportable counterparty types are identified by product in the following section.

- Retail
- Small Business
- Non-Financial Corporate
- Sovereign
- Central Bank
- GSE
- PSE
- MDB
- Other Supranational
- Pension Fund
- Bank
- Broker-Dealer
- Investment Company or Advisor
- Financial Market Utility
- Other Supervised Non-Bank Financial Entity
- Debt Issuing SPE
- Non-Regulated Fund
- Other

### O.D.1: Transactional Accounts

For purposes of this report, the term "Transactional Accounts" includes demand deposits as defined under Regulation D 12 CFR section 204 (Reserve Requirements of Depository Institutions); however this product only includes demand deposits placed by Retail and Small Business customers.

### O.D.2: Non-Transactional Relationship Accounts

Refers to Retail and Small Business deposits in accounts that are not transactional accounts under O.D.1, but where the underlying depositors have other established relationships with the reporting entity such as another deposit account, a loan, bill payment services, or any similar service or product provided to the depositor that the reporting entity has demonstrated to the satisfaction of the supervisory team would make deposit withdrawal highly unlikely during a liquidity stress event. Do not report brokered, sweep or reciprocal deposits using this product, as they should be reported using products O.D.8 through O.D.13.

### O.D.3: Non-Transactional Non-Relationship Accounts

Refers to Retail and Small Business deposits in accounts that are not transactional accounts under O.D.1 where the underlying depositors do not have other established relationships with the reporting entity that would otherwise make deposit withdrawal highly unlikely. Do not report brokered, sweep or reciprocal deposits using this product, as they should be reported using products O.D.8 through O.D.13.

### O.D.4: Operational Account Balances

Refers to deposits from counterparties that are not Retail or Small Business customers that are operational deposits as defined in the LRM Standards, except operational escrow deposits reported under product O.D.7: Operational Escrow Accounts.

### O.D.5: Excess Balances in Operational Accounts

Refers to deposits from counterparties that are not Retail or Small Business customers that are excluded from the reporting entity's operational deposit amount based on the reporting entity's methodology for identifying excess balances pursuant to section 249.4(b)(5). These balances must be in accounts that meet all other provisions of section 249.4(b).

### O.D.6: Non-Operational Account Balances

Refers to all deposits balances from counterparties that are not Retail or Small Business customers where the underlying account does not meet the criteria for operational deposits (i.e., exclude excess balances in operational accounts, reported under O.D.5).

### O.D.7: Operational Escrow Accounts

Refers to deposits from counterparties that are operational deposits as defined in the LRM Standards in the form of operational escrow deposits. Operational escrow deposits refers to an account that a designated third party (e.g., a servicer) establishes or controls on behalf of another party to process transactions such as the payment of taxes, insurance premiums (including flood insurance), or other charges with respect to a loan or transaction, including charges that the borrower and servicer have voluntarily agreed that the servicer should collect and pay. The definition encompasses any account established for this purpose, including a "trust account", "reserve account", "impound account", or other term in different localities.

With respect to, e.g., mortgage escrow accounts, an "escrow account" includes any arrangement where the servicer adds a portion of the borrower's payments to principal and subsequently deducts from principal the disbursements for escrow account items. For purposes of this section, the term "escrow account" excludes any account that is under the servicer's total control (e.g., payments collected by depository institution secured by real estate and other loans serviced for others that have not yet been remitted to owners of the loans).

### O.D.8: Non-Reciprocal Brokered Accounts

Refers to any deposit held at the reporting entity that is obtained, directly or indirectly, from or through the mediation or assistance of a deposit broker as that term is defined in section 29 of the Federal Deposit Insurance Act (12 U.S.C. 1831f(g)), not including a reciprocal brokered deposit or a sweep account. This definition does not include wholesale negotiable CDs (see O.W.16), listing service deposits, where the only function of a deposit listing service is to provide information on the availability and terms of accounts, unless they were obtained from a deposit broker.

### O.D.9: Stable Affiliated Sweep Account Balances

Refers to stable deposit balances held at the reporting entity by a customer or counterparty through a contractual feature that automatically transfers to the reporting entity from an affiliated financial company at the close of each business day amounts identified under the agreement governing the account from which the amount is being transferred. To qualify as stable, the deposit balance must satisfy the requirement in section 104(b)(2)(iii) of the LRM Standards. Note: This includes sweep balances that fall under a primary purpose exemption and are not reported as brokered for Call Report purposes.

### O.D.10: Less Stable Affiliated Sweep Account Balances

Refers to all other deposit balances, excluding those reported under O.D.9: Stable Affiliated Sweep Account Balances, that are held at the reporting entity by a customer or counterparty as a result of a contractual feature that automatically transfers to the reporting entity from an affiliated financial company at the close of each business day amounts identified under the agreement governing the account from which the amount is being transferred. Note: This includes sweep balances that fall under a primary purpose exemption and are not reported as brokered for Call Report purposes.

### O.D.11: Non-Affiliated Sweep Accounts

Refers to a deposit held at the reporting entity by a customer or counterparty through a contractual feature that automatically transfers to the reporting entity from an unaffiliated financial company at the close of each business day amounts identified under the agreement governing the account from which the amount is being transferred. These accounts involve ongoing activity, rather than one deposit transaction.

### O.D.12: Other Product Sweep Accounts

Refers to balances swept from deposit accounts into other products (e.g., CP, Fed Funds, Repo), including other deposit products at the same reporting entity. These balances should also be reported under the product that corresponds with the reporting entity's close-of-business liability.

### O.D.13: Reciprocal Accounts

Refers to any deposit held at the reporting entity that is obtained, directly or indirectly, from or through the mediation or assistance of a deposit broker as that term is defined in section 29 of the Federal Deposit Insurance Act (12 U.S.C. 1831f(g)), where the deposits are received through a deposit placement network on a reciprocal basis, such that: (1) for any deposit received, the reporting entity (as agent for depositors) places the same amount with other insured depository institutions through the network; and (2) each member of the network sets the interest rate to be paid on the entire amount of funds it places with other network members.

### O.D.14: Other Third-Party Deposits

Refers to deposit accounts that are placed by a third party on behalf of counterparties that do not otherwise meet the definitions of O.D.8 through O.D.12. Use the comments table to provide a general description of deposits included in this product on at least a monthly basis and in the event of a material change in reported values.

### O.D.15: Other Accounts

Refers to other deposit accounts that do not meet any of the definitions outlined above. Examples include but are not limited to cashier's checks, money orders, other official checks, merchant credits, and lock box. Notify the supervisory team of any balance reported in this category. Use the comments table to provide a general description of other deposits included in this product on at least a monthly basis and in the event of a material change in reported values.

---

## O.O: Outflows-Other

**Collateralized facilities:** For products O.O.4 through O.O.7 use the [Collateral Value] and [Collateral Class] fields to report both the amount and type of collateral that has been posted by the counterparty to secure the used portions of committed facilities according to the appropriate instructions for these fields or where the counterparty is contractually obligated to post collateral when drawing down the facility (e.g., if a liquidity facility is structured as a repo facility). Only report collateral if the bank is legally entitled and operationally capable to re-use the collateral in new cash raising transactions once the facility is drawn. If the range of acceptable collateral spans multiple categories as defined in the Asset Category Table (Appendix III), report using the lowest possible category.

### O.O.1: Derivative Payables

Refers to the maturing outgoing cash flows related to **uncollateralized derivatives** (e.g., interest rate, equity, commodity, and option premiums). Report contractually known payables for fixed and floating rate payables. If a floating rate has not been set, report the undiscounted anticipated cash flow by maturity. Do not include brokerage commission fees, exchange fees, or cash flows from unexercised in the money options. Netting receivables and payables by counterparty and maturity date is allowed if a valid netting agreement is in place, allowing for the net settlement of contractual flows. Do not include payables related to the exchange of principal amounts for foreign exchange transactions, as these should be reported in the Supplemental-Foreign Exchange table under products S.FX.1 through S.FX.3.

### O.O.2: Collateral Called for Delivery

Refers to the fair value of collateral due to the reporting entity's counterparties that has been called as of date T (i.e., the collateral flow). This product does not represent the entire stock of collateral posted. Collateral called for delivery should be related to the outstanding **collateralized** contracts which include, but are not limited to, derivative transactions with bilateral counterparties, central counterparties, or exchanges. Use the Maturity Bucket field to identify the expected settlement date. For collateral calls with same-day settlement (i.e., the collateral is both called and received on the as-of date T), report using the "Open" value in the Maturity Bucket field.

### O.O.3: TBA Purchases

Refers to all purchases of TBA contracts for market making or liquidity providing. Do not include TBA purchases which are part of a Dollar Roll, as defined under products I.S.3 or O.S.3.

### O.O.4: Credit Facilities

Refers to committed credit facilities, as defined in the LRM Standards. Do not include committed liquidity facilities, as defined in the LRM Standards, which should be reported using product O.O.5: Liquidity Facility or O.O.18: Unfunded Term Margin. Do not include excess margin, which should be reported using product O.O.17: Excess Margin, or retail mortgage commitments, which should be reported using product O.O.6: Retail Mortgage Commitments.
