# FR 2052a Instructions - Chunk 005
## Product Definitions (continued): I.S (continued), I.O, O.W, O.S begins

### I.S.4: Collateral Swaps (continued)

For collateral swaps where there is an exchange of non-cash assets, split the collateral swap into two separate borrowing and lending transactions and report in both the Inflows-Secured and Outflows-Secured tables. I.S.4 should reflect the borrowing leg of the transaction. Report the [Collateral Class] according to the assets received. Report the fair value under GAAP of the assets received in the [Collateral Value] field. Report the fair value under GAAP of the assets pledged in the [Maturity Amount] field. Use the [Sub-Product] field to identify the type of collateral pledged based on the asset categories defined in the LRM Standards:

- Level 1 Pledged
- Level 2a Pledged
- Level 2b Pledged
- Non-HQLA Pledged
- No Collateral Pledged

For collateral swaps where a non-cash asset is borrowed, report the [Collateral Class] according to the assets received and report the fair value under GAAP of the assets received in the [Collateral Value] field.

### I.S.5: Margin Loans

Refers to credit provided to a client to fund a trading position, collateralized by the client's cash or security holdings. Report margin loans on a gross basis; do not net client debits and credits.

### I.S.6: Other Secured Loans - Rehypothecatable

Refers to all other secured lending that does not otherwise meet the definitions of the Inflows-Secured products listed above and is not drawn from a revolving facility, for which the collateral received is contractually rehypothecatable. Use the comments table to provide a general description of secured loans included in this product on at least a monthly basis and in the event of a material change in reported values.

### I.S.7: Outstanding Draws on Secured Revolving Facilities

Refers to the existing loan arising from the drawn portion of a revolving facility (e.g., a general working capital facility) extended by the reporting entity, where the facility is secured by a lien on an asset or pool of assets.

### I.S.8: Other Secured Loans - Non-Rehypothecatable

Refers to all other secured lending that does not otherwise meet the definitions of the Inflows-Secured products listed above, for which the collateral received is not contractually rehypothecatable. Use the comments table to provide a general description of other loans included in this product on at least a monthly basis and in the event of a material change in reported values.

### I.S.9: Synthetic Customer Longs

Refers to total return swaps booked in client accounts, where the reporting entity is economically short the underlying reference asset and the client is economically long. Use the [Maturity Bucket] to designate the latest date a transaction could be unwound or terminated after taking into account clients' contractual rights to delay termination. Use the [Collateral Class] field to designate the reference asset of the transaction. Use the following [Sub-Product] values to designate how the position is "funded" (i.e., hedged):

- **Physical Long Position**: Refers to transactions hedged with physical long positions. In the event the long position that has been encumbered to another transaction, use the [Effective Maturity Bucket] to indicate the period of the encumbrance. For long positions held unencumbered, set the [Unencumbered] flag to "Y".
- **Synthetic Customer Short**: Refers to transactions where the customer synthetic long is hedged with another customer's synthetic short position reported in O.S.9.
- **Synthetic Firm Financing**: Refers to transactions where the associated hedge meets the definition of O.S.10.
- **Futures**: Refers to transactions hedged with futures contracts.
- **Other**: Refers to all other methods of hedging.
- **Unhedged**: Refers to positions that are not economically hedged with another instrument or transaction.

### I.S.10: Synthetic Firm Sourcing

Refers to total return swaps that are not booked in client accounts, where the reporting entity is economically short the underlying reference asset and the counterparty is economically long. Use the [Maturity Bucket] to designate the earliest date a transaction could be unwound or terminated. Use the [Collateral Class] field to designate the reference asset of the transaction. Use the following [Sub-Product] values to designate how the position is "covered" (i.e., hedged):

- **Physical Long Position**: Refers to transactions hedged with physical long positions. In the event the long position that has been encumbered to another transaction, use the [Effective Maturity Bucket] to indicate the period of the encumbrance. For long positions held unencumbered, set the [Unencumbered] flag to "Y".
- **Synthetic Customer Short**: Refers to transactions hedged with a customer's synthetic short position reported in O.S.9.
- **Synthetic Firm Financing**: Refers to transactions where the associated hedge meets the definition of O.S.10.
- **Futures**: Refers to transactions hedged with futures contracts.
- **Other**: Refers to all other methods of hedging.
- **Unhedged**: Refers to positions that are not economically hedged with another instrument or transaction.

---

## I.O: Inflows-Other

### I.O.1: Derivative Receivables

Refers to the maturing incoming cash flows related to **uncollateralized derivatives** (e.g., interest rate, equity, commodity, and option premiums). Report contractually known receivables for fixed and floating rate payables. If a floating rate has not been set, report the undiscounted anticipated cash flow by maturity. Do not include brokerage commission fees, exchange fees, or cash flows from unexercised in-the-money options. Netting receivables and payables by counterparty and maturity date is allowed if a valid netting agreement is in place, allowing for the net settlement of contractual flows. Do not include receivables related to the exchange of principal amounts for foreign exchange transactions, as these should be reported in the Supplemental-Foreign Exchange table under products S.FX.1 through S.FX.3.

### I.O.2: Collateral Called for Receipt

Refers to the fair value under GAAP of collateral due to the reporting entity as of date T (the collateral flow). This product does not represent the entire stock of collateral held. Collateral calls should be related to outstanding **collateralized** contracts which include but are not limited to derivative transactions with bilateral counterparties, central counterparties, or exchanges. Use the Maturity Bucket field to identify the expected settlement date. For collateral calls with same-day settlement (i.e., the collateral is both called and received on date T), report using the "Open" value in the Maturity Bucket field. If the settlement date or [Maturity Bucket] is unknown, then exclude the transaction from the data collection. If the [Currency] or [Collateral Class] is unknown then default to [Currency] ="USD" and [Collateral Class] = "Z-1" (i.e., the asset category for "all other assets").

### I.O.3: TBA Sales

Refers to all sales of TBA contracts for market making or liquidity providing. Do not include TBA sales which are part of a Dollar Roll, as defined under products I.S.3 or O.S.3.

### I.O.4: Undrawn Committed Facilities Purchased

Refers to legally binding agreements that provide the reporting entity with the ability to draw funds at a future date. Report only facilities that are committed, as defined in the LRM Standards.

### I.O.5: Lock-up Balance

Refers to inflows related to broker-dealer segregated accounts, as set forth in the LRM Standards. The I.O.[Maturity Bucket] value must reflect the date of the next scheduled calculation of the amount required under applicable legal requirements for the protection of customer assets with respect to each broker-dealer segregated account, in accordance with the reporting entity's normal frequency of recalculating such requirements.

### I.O.6: Interest and Dividends Receivable

Refers to contractual interest and dividend payments receivable on securities and loans and leases owned by the reporting entity. Do not include receivables related to unsecured derivative transactions, which should be reported under product I.O.1: Derivatives Receivables and included in the calculation of I.O.7: Net 30-day Derivative Receivables. Use the [Treasury Control] field to identify payments receivable related to securities that are similarly flagged in the Inflows-Assets table. For all interest and dividend payments reported, indicate the corresponding collateral class in the [Collateral Class] field. For interest on loans and leases, use the [Counterparty] field to designate the payer of the interest. Under circumstances where the interest and dividend payments receivable are uncertain (e.g., a floating rate payment has not yet been set), forecast receivables for a minimum of 30 calendar days beyond the as-of date (T). Exclude interest and dividends receivable on assets securing Covered Federal Reserve Facility Funding.

### I.O.7: Net 30-Day Derivative Receivables

Refers to the net derivative cash inflow amount, as set forth in the LRM Standards.

### I.O.8: Principal Payments Receivable on Unencumbered Investment Securities

Refers to contractual principal payments receivable on reporting entity-owned investment securities. For amortizing products for which the principal and interest amounts cannot be readily separated, report aggregated principal and interest cash inflows, and do not report the interest under I.O.6: Interest and Dividends Receivable. For other products, report the contractual principal cash payment to be received, excluding interest payments, which should be reported under product I.O.6: Interest and Dividends Receivable. Do not include principal payments receivable on loans and leases, which should be reported separately under the appropriate product in the Inflows-Unsecured or Inflows-Secured tables. Do not include principal payments receivable on securities that are currently encumbered. Use the [Treasury Control] field to identify payments receivable related to securities that are similarly flagged in the Inflows-Assets table. For all principal payments reported, indicate the corresponding collateral class in the [Collateral Class] field. Under circumstances where the principal payments receivable are uncertain (e.g., an index-linked structured note, where the payout has not yet been determined), forecast receivables for 30 calendar days beyond the as-of date (T).

### I.O.9: Other Cash Inflows

Refers to other contractual cash inflows that do not adhere to the definitions of the products outlined above. Contact the supervisory team to determine if the associated cash flow should be reported. Use the comments table to provide a general description of other cash inflows included in this product on at least a monthly basis and in the event of a material change in reported values.

---

## O.W: Outflows-Wholesale

### Conduit and Asset-Backed Funding

**General Guidance:** For products that typically make use of conduits or SPEs to finance assets for which the reporting entity retains the beneficial interest, use the [Maturity Amount] field to report the contractual liabilities of the conduits based on the remaining maturity of the issuance. Use the [Collateral Class] and [Collateral Value] fields to identify the types and fair value of asset(s) underlying the issuance. For debt instruments issued at a discount, report the final maturity obligation under the [Maturity Amount] field, which will effectively include interest accrued over the term of the instrument and not under product O.O.19 Interest & Dividends Payable. For all other periodic interest payments, report those under product O.O.19 Interest & Dividends Payable.

For non-tradable products (e.g., O.W.9, O.W.10, O.W.17 and O.W.18), use the [Counterparty] field to further identify the type of creditor according to the following:

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

**Reporting Entity:** In most cases, conduits should be reported as if "on-balance sheet" at one of the designated reporting entities (e.g., bank) and the "consolidated" reporting entity, specifically if the entity is consolidated under GAAP. Therefore, if the reporting entity uses a repurchase agreement to facilitate the transfer of assets to or from this conduit, this repo agreement should not be reported in any section of this report in order to avoid double counting.

If the issuance requires an additional guarantee or line of support, only report the line of support if the issuance and corresponding line of support reside in two distinct legal entities. Lines of support for SPEs should be reported in the Outflows-Other table according to the appropriate product instructions. For consolidated entity reporting purposes, only report the conduit issuance and do not include the line of support to avoid double counting.

The following list outlines the products that typically make use of conduits or SPVs to be reported in the Outflows-Wholesale table:

### O.W.1: Asset-Backed Commercial Paper (ABCP) Single-Seller

### O.W.2: Asset-Backed Commercial Paper (ABCP) Multi-Seller

### O.W.3: Collateralized Commercial Paper

### O.W.4: Asset-Backed Securities (ABS)

### O.W.5: Covered Bonds

### O.W.6: Tender Option Bonds

### O.W.7: Other Asset-Backed Financing

Refers to (i) all other asset-backed financing arrangements that make use of conduits; and (ii) all other issuances backed by a lien on an underlying asset or pool of collateral where rights of rehypothecation over the collateral are not conferred to the investor or counterparty.

### Unsecured Funding

**General Guidance:** For products that generate unsecured funding, report the contractual liabilities based on the remaining maturity of the issuance. Do not record book/fair value. To the extent that the interest payable on structured instruments is realized through increases or decreases in the principal balance, this interest/return should be aggregated with the principal maturity amount of the associated product. For debt instruments issued at a discount, report the final maturity obligation under the [Maturity Amount] field, and not under product O.O.19: Interest & Dividends Payable. For all other periodic interest payments report those under product O.O.19 Interest & Dividends Payable.

### O.W.8: Commercial Paper

### O.W.9: Onshore Borrowing

Refers to unsecured borrowing of the domestic currency between eligible domestic institutions made in the wholesale inter-bank or inter-dealer broker market (e.g., fed funds[^13] purchased, domestic sterling purchased, domestic euro, domestic yen).

Onshore borrowing must satisfy the following criteria: (1) the currency denomination of the transaction is matched with the jurisdiction in which the transaction is booked; and (2) the transacting entities (i.e., the legal entities party to the transaction) are both domiciled in the same jurisdiction.

[^13]: For FRBNY definition, see: http://www.newyorkfed.org/aboutthefed/fedpoint/fed15.html

### O.W.10: Offshore Borrowing

Refers to unsecured borrowing of the domestic currency outside of the onshore market, but still placed through the inter-bank or inter-dealer broker market (e.g., Eurodollars, EuroSterling, EuroYen, EuroEuro).

### O.W.11: Unstructured Long Term Debt

Refers to debt issuances with original maturity greater than one year, including plain vanilla floating rate notes linked to standard interest rate indexes and plain vanilla benchmark issuances with standard embedded options (i.e., call/put). Include instruments classified as long-term debt under GAAP. Include subordinated debt issued to affiliates that fall outside the reporting entity's scope of consolidation. Do not include perpetual preferred stock.

### O.W.12: Structured Long Term Debt

Refers to debt instruments with original maturity greater than one year whose principal or interest payments are linked to an underlying asset (e.g., commodity linked notes, equity linked notes, reverse convertible notes, currency linked notes). Include instruments classified as long term debt under GAAP accounting rules that also meet the structured description set forth in this product. Do not include perpetual preferred stock.

### O.W.13: Government Supported Debt

Refers to debt issuances with an explicit guarantee from a sovereign entity or central bank (e.g., TLGP).

### O.W.14: Unsecured Notes

Refers to issuances of unsecured debt with original maturities less than a year, including promissory notes and bank notes, but excluding the other forms of unsecured financing defined elsewhere, and excluding all deposits as defined in the Outflows-Deposits section.

### O.W.15: Structured Notes

Refers to debt instruments with original maturity less than one year whose principal or interest payments are linked to an underlying asset (e.g., commodity linked notes, equity linked notes, reverse convertible notes, currency linked notes).

### O.W.16: Wholesale CDs

Refers to certificates of deposits greater than $250,000 issued to counterparties that are not Retail or Small Business where the certificates of deposit are tradable, negotiable, and typically settle at DTCC.

### O.W.17: Draws on Committed Lines

Refers to the outstanding amount of funds borrowed or drawn from a committed facility provided by another institution.

### O.W.18: Free Credits

Refers to liabilities of a broker or dealer to customers, excluding payables related to customer short positions. Do not net against Lock-up Balances.

### O.W.19: Other Unsecured Financing

Refers to other forms of unsecured financing that are not captured above. Notify the supervisory team of products reported in this category. Use the comments table to provide a general description of other unsecured financing included in this product on at least a monthly basis and in the event of a material change in reported values.

---

## O.S: Outflows-Secured

**General Guidance:** For all products outlined in this table, report the contractual principal cash payment to be paid at maturity, excluding interest payments (which should be reported under product O.O.19, using the Maturity Amount field). Report the fair value under GAAP of the pledged securities using the Collateral Value field. Report on a gross basis; do not net borrowings against loans. FIN 41 does not apply for this report.

For collateral class, report the type of collateral financed according to the Asset Category Table (Appendix III). For transactions that allow for collateral agreement amendments, report the transaction based on the collateral pledged as of date T.

Use the [Counterparty] field to indicate the type of counterparty for each data element:

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

### O.S.1: Repo

Refers to all repurchase agreements (including under Master Repurchase Agreements or Global Master Repurchase Agreements).

### O.S.2: Securities Lending

Refers to all securities lending transactions (including under Master Securities Loan Agreements).

### O.S.3: Dollar Rolls

Refers to transactions using TBA contracts with the intent of financing a security or pool of collateral. Report transactions where the reporting entity has agreed to sell the TBA contract and buy it back at a later date.

### O.S.4: Collateral Swaps

Refers to transactions where non-cash assets are exchanged (e.g., collateral upgrade/downgrade trades) at the inception[^14] of the transaction, or a non-cash asset is lent and no collateral is received (i.e., an unsecured loan of collateral), and the assets will be returned at a future date.

[^14]: Collateral swap transactions that are remargined with cash payments should continue to be reported under this product.

For collateral swaps where non-cash assets are exchanged, split the collateral swap into two separate lending and borrowing transactions and report in both the Outflows-Secured and Inflows-Secured tables. *(Continues in next chunk)*
