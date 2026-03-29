# FR 2052a Instructions - Chunk 007
## Pages 60-69: Outflows-Other (cont.), Supplemental-Derivatives & Collateral

### O.O.4: Credit Facilities (continued)

Use the O.O.[Maturity Bucket] field to indicate the earliest date the commitment could be drawn.

Use the O.O.[Counterparty] field to distinguish between facilities to different counterparties:

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

### O.O.5: Liquidity Facilities

Refers to committed liquidity facilities, as defined in the LRM Standards; however, exclude unfunded term margin, which should be reported under O.O.18: Unfunded Term Margin.

If facilities have aspects of both credit and liquidity facilities, the facility must be classified as a liquidity facility.

Use the O.O.[Maturity Bucket] field to indicate the earliest date the commitment could be drawn.

Use the O.O.[Counterparty] field to distinguish between facilities to different counterparties:

- Retail
- Small Business
- Non-Financial Corporate
- Sovereign
- Central Bank
- GSE
- PSE, except Municipalities for VRDN structures
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
- Municipalities for VRDN structures
  - Includes standby purchase agreements that backstop remarketing obligations, as well as direct-pay LOCs that provide credit enhancement. If a VRDN is not supported by an SBPA or LOC, then the remarketing obligation should also be considered as a liquidity facility under this product.
- Other

### O.O.6: Retail Mortgage Commitments

Refers to contractual commitments made by the reporting entity to originate retail mortgages. Use the O.O.[Maturity Bucket] field to indicate the earliest date the commitment could be drawn.

### O.O.7: Trade Finance Instruments

Refers to documentary trade letters of credit, documentary and clean collection, import bills and export bills, and guarantees directly related to trade finance obligations, such as shipping guarantees.

Lending commitments, such as direct import or export financing for non-financial firms, should be included in O.O.4: Credit Facilities and O.O.5: Liquidity Facilities, as appropriate.

### O.O.8: MTM Impact on Derivative Positions

Refers to the absolute value of the largest 30-consecutive calendar day cumulative net mark-to-market collateral outflow or inflow realized during the preceding 24 months resulting from derivative transaction valuation changes, as set forth in the LRM Standards. The cumulative collateral outflow or inflow should be measured on a portfolio basis, which should include both 3rd party and affiliated transactions (for subsidiary reporting entities) that are external to the reporting entity's scope of consolidation. However, as this product should be measured on a portfolio basis, the [Internal] and [Internal Counterparty] flags should not be used. The absolute amount should be determined across all currencies and reported in USD.

### O.O.9: Loss of Rehypothecation Rights Due to a 1 Notch Downgrade

Refers to the total fair value of the collateral over which the reporting entity would lose rehypothecation rights due to a 1 notch credit rating downgrade.

### O.O.10: Loss of Rehypothecation Rights Due to a 2 Notch Downgrade

Refers to the total fair value of the collateral over which the reporting entity would lose rehypothecation rights due to a 2 notch credit rating downgrade.

### O.O.11: Loss of Rehypothecation Rights Due to a 3 Notch Downgrade

Refers to the total fair value of the collateral over which the reporting entity would lose rehypothecation rights due to a 3 notch credit rating downgrade.

### O.O.12: Loss of Rehypothecation Rights Due to a Change in Financial Condition

Refers to the total fair value of the collateral over which the reporting entity would lose rehypothecation rights due to a change in financial condition, which includes a downgrade of the reporting entity's rating up to but not including default.

### O.O.13: Total Collateral Required Due to a 1 Notch Downgrade

Refers to the total cumulative fair value of additional collateral the reporting entity's counterparties will require the reporting entity to post as a result of a 1-notch credit rating downgrade. Report figures based on contractual commitments. Collateral required includes, but is not limited to, collateral called from OTC derivative transactions and exchanges. Include outflows due to additional termination events, but do not include inflows from netting sets that are in a net receivable position. Do not double count balances reported in O.O.9.

### O.O.14: Total Collateral Required Due to a 2 Notch Downgrade

Refers to the total cumulative fair value of additional collateral the reporting entity's counterparties will require the reporting entity to post as a result of a 2-notch credit rating downgrade. Report figures based on contractual commitments. Collateral required includes, but is not limited to, collateral called from OTC derivative transactions and exchanges. Include outflows due to additional termination events, but do not include inflows from netting sets that are in a net receivable position. Do not double count balances reported in O.O.10.

### O.O.15: Total Collateral Required Due to a 3 Notch Downgrade

Refers to the total cumulative fair value of additional collateral the reporting entity's counterparties will require the reporting entity to post as a result of a 3-notch credit rating downgrade. Report figures based on contractual commitments. Collateral required includes, but is not limited to, collateral called from OTC derivative transactions and exchanges. Include outflows due to additional termination events, but do not include inflows from netting sets that are in a net receivable position. Do not double count balances reported in O.O.11.

### O.O.16: Total Collateral Required Due to a Change in Financial Condition

Refers to the total cumulative fair value of additional collateral the reporting entity's counterparties will require the reporting entity to post as a result of a change in the reporting entity's financial condition, which includes a downgrade of the reporting entity's rating up to but not including default. Report figures based on contractual commitments. Collateral required includes, but is not limited to, collateral called from OTC derivative transactions and exchanges. Include outflows due to additional termination events, but do not include inflows from netting sets that are in a net receivable position. Do not double count balances reported in O.O.12.

### O.O.17: Excess Margin

Refers to the total capacity of the reporting entity's customer to generate funding for additional purchases or short sales of securities (i.e., the reporting entity's obligation to fund client positions) for the following day based on the net equity in the customer's margin account. This capacity can generally be revoked or reduced on demand (i.e., uncommitted).

### O.O.18: Unfunded Term Margin

Refers to any unfunded contractual commitment to lend to a brokerage customer on margin for a specified duration greater than one day. Report the minimum contractually committed term that would be in effect upon a customer draw from the margin facility using the O.O.[Maturity Bucket] field.

### O.O.19: Interest & Dividends Payable

Refers to interest and dividends contractually payable on the reporting entity's liabilities and equity. For equity dividends, report a [Collateral Class] of "Y-4". Do not include payables related to unsecured derivative transactions, which should be reported under product O.O.1: Derivatives Payables and which should be included in the calculation of O.O.20: Net 30-day Derivative Payables. Under circumstances where the interest and dividend payments receivable are uncertain (e.g., floating rate payment has not yet been set), forecast payables for a minimum of 30 calendar days beyond the as-of date (T). Exclude interest payable on Covered Federal Reserve Facility Funding.

### O.O.20: Net 30-Day Derivative Payables

Refers to the net derivative cash outflow amount, as set forth in the LRM Standards.

### O.O.21: Other Outflows Related to Structured Transactions

Refers to any incremental potential outflows under 32(b) of the LRM Standards related to structured transactions sponsored but not consolidated by the reporting entity that are not otherwise reported in O.O.4 or O.O.5.

### O.O.22: Other Cash Outflows

Refers to any other material cash outflows not reported in any other line that can impact the liquidity of the reporting entity. Do not report 'business as usual' expenses such as rents, salaries, utilities and other similar payments. Include cash needs that arise out of an extraordinary situation (e.g., a significant cash flow needed to address a legal suit settlement or pending transaction). Use the comments table to provide a general description of other cash outflows included in this product on at least a monthly basis and in the event of a material change in reported values.

---

## S.DC: Supplemental-Derivatives & Collateral

**General Guidance:** The following list defines the scope of products to be reported in the Supplemental-Derivatives & Collateral table. U.S. firms that are identified as Category IV banking organizations with average weighted short-term wholesale funding of less than $50 billion and FBOs that are identified as Category IV foreign banking organizations with average weighted short-term wholesale funding of less than $50 billion have the option of not reporting these products.

Products S.DC.3 through S.DC.10 below refer to the stock of collateral held or posted by the reporting entity related to certain transactions (e.g., derivatives). For these products only, the [Sub-Product] must also be reported to distinguish the stock of collateral according to the following categories:

- Rehypothecatable -- Unencumbered
- Rehypothecatable -- Encumbered
- Non-Rehypothecatable
- Segregated Cash
- Non-Segregated Cash

If the total collateral reported under Products S.DC.5 through S.DC.10 is less than $2 billion, the reporting entity may use the sub-product "Non-Rehypothecatable" as a default for these products.

For products S.DC.1 through S.DC.10, use the [Sub Product 2] field to further distinguish derivative assets, liabilities and the stock of collateral according to the following categories:

- **OTC - Bilateral** -- Refers to collateral posted or received in relation to derivatives activities for which the transactions are executed over-the-counter (OTC) and settled bilaterally.
- **OTC -- Centralized (Principal)** -- Refers to collateral posted or received in relation to derivatives transactions for which transactions are executed OTC, but cleared via a centralized financial market utility (e.g., a central counterparty), where the reporting entity remains principal to the transaction, or for client transactions, guarantees the performance of the centralized financial market utility to the client.
- **OTC -- Centralized (Agent)** -- Refers to collateral posted or received in relation to derivatives transactions for which transactions are executed OTC, but cleared via a centralized financial market utility (e.g., a central counterparty), where the reporting entity acts as agent on behalf of clients and does not guarantee the performance of the centralized financial market utility to the client.
- **Exchange-traded (Principal)** -- Refers to collateral posted or received in relation to derivatives transactions for which transactions are not executed OTC (e.g., executed through an exchange or central trading platform) and are cleared via a centralized financial market utility (e.g., a central counterparty), where the reporting entity remains principal to the transaction, or for client transactions, guarantees the performance of the centralized financial market utility to the client.
- **Exchange-traded (Agent)** -- Refers to collateral posted or received in relation to derivatives transactions for which transactions are not executed OTC (e.g., executed through an exchange or central trading platform) and are cleared via a centralized financial market utility (e.g., a central counterparty), where the reporting entity acts as agent on behalf of clients and does not guarantee the performance of the centralized financial market utility to the client.

### S.DC.1: Gross Derivative Asset Values

Refers to the aggregate value of derivative transactions not subject to qualifying master netting agreements that are assets and the net value of derivative transactions within qualifying master netting agreements where the netting sets are assets. In both cases, the asset amount must be calculated as if no variation margin had been exchanged.

### S.DC.2: Gross Derivative Liability Values

Refers to the aggregate value of derivative transactions not subject to qualifying master netting agreements that are liabilities and the net value of derivative transactions within qualifying master netting agreements where the netting sets are liabilities. In both cases, the liability amount must be calculated as if no variation margin had been exchanged.

### S.DC.3: Derivative Settlement Payments Delivered

Refers to the cumulative value of payments delivered as variation margin on outstanding derivative contracts for the purpose of settling a change in the market value of the contract (e.g., "settled-to-market" derivatives).

### S.DC.4: Derivative Settlement Payments Received

Refers to the cumulative value of payments received as variation margin on outstanding derivative contracts for the purpose of settling a change in the market value of the contract (e.g., "settled-to-market" derivatives).

### S.DC.5: Initial Margin Posted - House

Refers to the fair value of collateral that the reporting entity has posted (total stock by applicable [Collateral Class]) to its counterparties as initial margin on its own proprietary derivatives positions. Include any independent amount pledged that must be maintained by contract, where the independent amount pledged does not also serve as variation margin by offsetting a derivative liability as-of the reporting date.

### S.DC.6: Initial Margin Posted - Customer

Refers to the fair value of collateral that the reporting entity has posted (total stock by applicable [Collateral Class]) to its counterparties as initial margin on behalf of customers. Include initial margin related to customer transactions to which the reporting entity is acting as either principal or agent. Use the [Sub-Product 2] field to distinguish initial margin posted where the reporting entity is acting as agent and does not guarantee the performance of the counterparty to its customer from all other initial margin posted on behalf of customers.

### S.DC.7: Initial Margin Received

Refers to the fair value of collateral that the reporting entity has received (total stock by applicable [Collateral Class]) from its counterparties as initial margin against both house and customer positions. Include any independent amount received that must be maintained by contract, where the independent amount received does not also serve as variation margin by offsetting a derivative asset as-of the reporting date. Use the [Sub-Product 2] field to distinguish initial margin received from customers where the reporting entity is acting as agent and does not guarantee the performance of the counterparty to its customer from all other initial margin received from customers.

### S.DC.8: Variation Margin Posted - House

Refers to the fair value of collateral that the reporting entity has posted (total stock by applicable [Collateral Class]) to its counterparties as variation margin on its own proprietary derivatives positions. Exclude variation margin delivered on outstanding contracts in the form of settlement payments, which must be reported under S.DC.3.

### S.DC.9: Variation Margin Posted - Customer

Refers to the fair value of collateral that the reporting entity has posted (total stock by applicable [Collateral Class]) to its counterparties as variation margin on behalf of customers. Include variation margin related to customer transactions to which the reporting entity is acting as either principal or agent. Use the [Sub-Product 2] field to distinguish variation margin posted where the reporting entity is acting as agent and does not guarantee the performance of the counterparty to its customer from all other variation margin posted on behalf of customers.

### S.DC.10: Variation Margin Received

Refers to the fair value of collateral that the reporting entity has received (total stock by applicable [Collateral Class]) from its counterparties as variation margin against both house and customer positions. Exclude variation margin received on outstanding contracts in the form of settlement payments, which must be reported under S.DC.4. Use the [Netting Eligible] field to identify the value of collateral that meets the criteria referenced in section 107(f)(1) of the LRM Standards.

### S.DC.11: Derivative CCP Default Fund Contribution

Refers to the reporting entity's contributions to a central counterparty's mutualized loss sharing arrangement, where the reporting entity's clearing activity with the central counterparty includes derivative transactions. Report the fair value of assets contributed, regardless of whether the contribution is included on the reporting entity's balance sheet.

### S.DC.12: Other CCP Pledges and Contributions

Refers to the reporting entity's asset pledges (e.g., in the form of initial margin) and contributions to a central counterparty's mutualized loss sharing arrangement, where the reporting entity's clearing and/or settlement activity with the central counterparty does not include derivative transactions. Report the fair value of assets contributed, regardless of whether the contribution is included on the reporting entity's balance sheet.

### S.DC.13: Collateral Disputes Deliverables

Refers to the fair value of collateral called by the reporting entity's counterparties that the reporting entity has yet to deliver due to a dispute. Disputes include, but are not limited to, valuation of derivative contracts. If the total amount that would have been reported related to distinct disputes over the previous year for products S.DC.13 and S.DC.14 is less than $500 million, the reporting firm need not report this product.

### S.DC.14: Collateral Disputes Receivables

Refers to the fair value of collateral that the reporting entity has called from its counterparties, but has not yet received due to a dispute. Disputes include, but are not limited to, valuation of derivative contracts. If the total amount that would have been reported related to distinct disputes over the previous year for products S.DC.13 and S.DC.14 is less than $500 million, the reporting firm need not report this product.

### S.DC.15: Sleeper Collateral Deliverables

Refers to the fair value of unsegregated collateral that the reporting entity may be required by contract to return to a counterparty because the collateral currently held by the reporting entity exceeds the counterparty's current collateral requirements under the governing contract.

### S.DC.16: Required Collateral Deliverables

Refers to the fair value of collateral that the reporting entity is contractually obligated to post to a counterparty, but has not yet posted as it has not yet been called by the reporting entity's counterparty.

### S.DC.17: Sleeper Collateral Receivables

Refers to the fair value of collateral that the reporting entity could call for or otherwise reclaim under legal documentation, but has not yet been called. U.S. firms that are identified as Category III banking organizations with average weighted short-term wholesale funding of less than $75 billion; U.S. firms that are identified as Category IV banking organizations; FBOs that are identified as Category III foreign banking organizations with average weighted short-term wholesale funding of less than $75 billion; and FBOs that are identified as Category IV foreign banking organizations have the option of not reporting this product.

### S.DC.18: Derivative Collateral Substitution Risk

Refers to the potential funding risk arising from the reporting entity's derivative counterparties having the contractual ability to substitute collateral with higher liquidity value currently held by the reporting entity with collateral of lower liquidity value or collateral that the reporting entity cannot monetize either due to liquidity or operational constraints. Report only a single value in USD per reporting entity, representing the difference between the fair value of the collateral held and the fair value of collateral that could be received, after applying the haircut factors prescribed in the LRM Standards.

### S.DC.19: Derivative Collateral Substitution Capacity

Refers to the potential funding capacity arising from the reporting entity's contractual ability to substitute collateral with higher liquidity value currently posted to a derivatives counterparty with collateral of lower liquidity value. Report only a single value in USD per reporting entity, representing the difference between the fair value of the collateral held and the fair value of the collateral that could be posted, after applying the haircut factors prescribed in the LRM Standards. U.S. firms that are identified as Category III banking organizations with average weighted short-term wholesale funding of less than $75 billion; U.S. firms that are identified as Category IV banking organizations; FBOs that are identified as Category III foreign banking organizations with average weighted short-term wholesale funding of less than $75 billion; and FBOs that are identified as Category IV foreign banking organizations have the option of not reporting this product.
