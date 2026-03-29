# FR 2052a Instructions - Chunk 004
## Field Definitions (continued) and Product Definitions (I.A, I.U, I.S begins)

### Collateral Level (continued)

#### Fully Collateralized
Refers to derivative asset and liability values and any associated balances of variation margin posted and received where the value of margin exchanged is equal to the derivative asset or liability value for the transaction or associated derivative transaction or qualifying master netting agreement netting set. Derivative asset and liability values may be considered "fully collateralized" to the extent there are short-term timing mismatches between margin calls and margin settlement that result in temporarily undercollateralized exposures or minimum transfer amounts are set at de minimis levels (e.g., $1 million).

#### Overcollateralized
Refers to derivative asset and liability values and the portion of variation margin posted and received where the value of margin exchanged is greater than the derivative asset or liability value for the transaction or associated derivative transaction or qualifying master netting agreement netting set. For variation margin posted and received, use this value to designate only the portion of margin that exceeds the derivative asset or liability value.

### Accounting Designation

*This field is only applicable to the Inflows-Assets table.* Use this field to identify the accounting designation applicable to each asset reported under products I.A.1: Unencumbered Assets and I.A.2: Capacity. Use the following values:

- **Available-for-Sale**
- **Held-to-Maturity**
- **Trading Asset**
- **Not Applicable**: For example, use this designation to the extent assets received via a secured lending transaction are reported under I.A.2: Capacity.

### Loss Absorbency

*This field is only applicable to the Wholesale table.*

U.S. firms that are identified as Category IV banking organizations with average weighted short-term wholesale funding of less than $50 billion and FBOs that are identified as Category IV foreign banking organizations with average weighted short-term wholesale funding of less than $50 billion are not required to report on this field.

Use this field to identify the extent to which instruments reported in the Outflows-Wholesale table qualify as capital or Total Loss Absorbing Capacity (TLAC) instruments under 12 CFR 217 Subpart C or 12 CFR 252 Subparts G and P, respectively. Use the following values:

- **Capital**
- **TLAC**

### G-SIB

*This field is applicable in all cases where the Counterparty field is populated.*

U.S. firms that are identified as Category I banking organizations are required to report this field.

Use this field to identify data elements where the underlying counterparty is a G-SIB according to the most recent list of G-SIBs published by the Financial Stability Board (FSB). Report in this field the G-SIB name, as it appears on the FSB list.

### Maturity Optionality

*This field is applicable to the Inflows-Secured, Inflows-Unsecured, Outflows-Deposits, Outflows-Secured and Outflows-Wholesale tables.* Use this field to identify transactions with the following types of embedded optionality:

- **Evergreen**: Refers to transactions that require either or both parties to provide a minimum number of days' notice before the transaction can contractually mature.
- **Extendible**: Refers to transactions that include options to extend the maturity beyond its originally scheduled date.
- **Accelerated-Counterparty**: Refers to transactions where the counterparty holds an option to accelerate maturity (e.g., a liability with a put option), and the maturity is assumed to be accelerated as per the requirements for reporting of the [Maturity Bucket] field. Include transactions where the counterparty's exercise of the option would require the reporting entity's mutual consent.
- **Accelerated-Firm**: Refers to transactions where the reporting entity holds an option to accelerate maturity (e.g., a liability with a call option), and the maturity is assumed to be accelerated as per the requirements for reporting of the [Maturity Bucket] field.
- **Not Accelerated**: Refers to all other transactions with embedded optionality that could accelerate the maturity of an instrument, but that maturity is not assumed to be accelerated as per the requirements for reporting of the [Maturity Bucket] field.

---

## Product Definitions

## I.A: Inflows-Assets

### I.A.1: Unencumbered Assets

Refers to assets that are owned outright that are (i) free of legal, regulatory, contractual, or other restrictions on the ability of the reporting entity to monetize the assets; and (ii) not pledged, explicitly or implicitly, to secure or to provide credit enhancement to any transaction. Exclude all unencumbered assets that are pledged to a central bank or a U.S. government-sponsored enterprise that meet the specifications of, and should be reported under, product I.A.2: Capacity. Exclude transactions involving the purchase of securities that have been executed, but not yet settled as those transactions should be reported in lines I.A.5: Unsettled Asset Purchases or I.A.6: Forward Asset Purchases, depending on the timing of settlement. Any amounts due to the reporting institution with respect to any associated hedges should not be added or subtracted from the fair value of the asset. Include unencumbered loans and leases even though these loans and leases must also be reported under the appropriate Inflows-Unsecured and Inflows-Secured products. Do not exclude assets that are owned outright at a subsidiary of the reporting entity, but have been pledged to secure a transaction with another subsidiary of the reporting entity; to the extent these assets remain unencumbered.

### I.A.2: Capacity

Refers to the available credit extended by central banks or GSEs that is secured by acceptable collateral, where (i) potential credit secured by the assets is not currently extended to the reporting entity or its consolidated subsidiaries; and (ii) the pledged assets are not required to support access to the payment services of a central bank. The amount of available capacity should be reported net of any advances that have already been drawn upon or other forms of encumbrance (e.g., FHLB LOCs). The [Market Value] field should indicate the market value of collateral pledged, while the [Lendable Value] field should indicate the residual capacity available to draw against this collateral. For the purpose of reporting available capacity and encumbrance, under circumstances where draws are not assessed against specific individual assets, but rather the entire pool of collateral generally, assume that the lowest quality assets are encumbered first followed by higher quality assets (quality in terms of high-quality liquid asset categories under the LRM Standards). Include unencumbered loans, even though these loans must also be reported under the appropriate Inflows-Unsecured and Inflows-Secured products.

Use the [Sub-Product] field to identify the specific source of the capacity according to the following choices:

- FRB (Federal Reserve Bank)
- SNB (Swiss National Bank)
- BOE (Bank of England)
- ECB (European Central Bank)
- BOJ (Bank of Japan)
- RBA (Reserve Bank of Australia)
- BOC (Bank of Canada)
- OCB (Other Central Bank)
- FHLB (FHLB System)
- Other GSE

### I.A.3: Unrestricted Reserve Balances

Refers to reserve bank balances maintained at a Federal Reserve Bank, less the reserve balance requirement as defined in section 204.5(a)(1) of Regulation D (12 CFR 204.5(a)(1)), foreign withdrawable reserves maintained at other central banks, and Federal Reserve term deposits that are not held to satisfy reserve requirements.

Reserve Bank balances has the meaning set forth in the LRM Standards. For those accounts that explicitly and contractually permit withdrawal upon demand prior to the expiration of the term or that may be pledged as collateral for term or automatically renewing overnight advances from the Federal Reserve Bank, report the [Maturity Bucket] value as "Open". For other accounts, report the [Maturity Bucket] value that corresponds with the contractual maturity.

Foreign withdrawable reserves have the meaning set forth in the LRM Standards.

Use the [Sub-Product] field to further identify the specific central bank account according to the following choices, or "Currency and Coin" for currency and banknotes:

- FRB (Federal Reserve Bank)
- SNB (Swiss National Bank)
- BOE (Bank of England)
- ECB (European Central Bank)
- BOJ (Bank of Japan)
- RBA (Reserve Bank of Australia)
- BOC (Bank of Canada)
- OCB (Other Central Bank)
- Currency and Coin[^10]

[^10]: Report U.S. and foreign currency and coin owned and held in all offices of the consolidated holding company; currency and coin in transit to a Federal Reserve Bank or to any other depository institution for which the reporting holding company's subsidiaries have not yet received credit; and currency and coin in transit from a Federal Reserve Bank or from any other depository institution for which the accounts of the subsidiaries of the reporting holding company have already been charged.

### I.A.4: Restricted Reserve Balances

Refers to balances held at central banks that are not immediately withdrawable and currency and banknotes, including the reserve balances and term deposits that are held to satisfy reserve requirements.

Use the [Sub-Product] field to further identify the specific central bank account according to the following choices, or "Currency and Coin" for currency and banknotes:

- FRB (Federal Reserve Bank)
- SNB (Swiss National Bank)
- BOE (Bank of England)
- ECB (European Central Bank)
- BOJ (Bank of Japan)
- RBA (Reserve Bank of Australia)
- BOC (Bank of Canada)
- OCB (Other Central Bank)
- Currency and Coin

### I.A.5: Unsettled Asset Purchases

Refers to transactions involving the purchase of securities that have been executed, but have not yet settled; and for which the settlement contractually occurs within the period of time (after the trade date) generally established by regulations or conventions in the marketplace or exchange in which the transaction is being executed (i.e., regular-way security trades). Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities purchased. Report failed settlements with a [Forward Start Bucket] value of "Open".

### I.A.6: Forward Asset Purchases

Refers to transactions involving the purchase of securities that have been executed, but not yet settled; and for which the settlement contractually occurs outside the period of time (after the trade date) generally established by regulations or conventions in the marketplace or exchange in which the transaction is being executed (i.e., not a regular-way security trade). Use the [Forward Start Amount] and [Forward Start Bucket] fields to indicate the settlement amount and settlement date of the securities purchased. These transactions must also be included in the calculation of products I.O.7: Net 30-day Derivative Receivables and O.O.20: Net 30-day Derivative Payables. Report failed settlements with a [Forward Start Bucket] value of "Open".

### I.A.7: Encumbered Assets

Refers to encumbered assets, of which the reporting entity is the beneficial owner (i.e., the assets are represented on the accounting balance sheet), that are not otherwise captured under other FR 2052a balance sheet products in the I.A, I.U or I.S tables.

---

## I.U: Inflows-Unsecured

**General Guidance:** Report aggregated principal cash inflows for all fully performing loans and placements. Exclude non-performing loans (i.e., 90 days past due or non-accrual) which are reported in Supplemental-Balance Sheet table. Do not make any assumptions about amortizations or pre-payments. If an amortizing loan is underwritten on a forward-starting basis, the amount reported in the [Forward Start Amount] field, representing the initial disbursement of the loan, should be split across all associated products and should match the corresponding maturity amount (i.e., the principal payment received for that period). For syndicated loans, only report the portion of the loan that is due to the reporting entity. Include overdrafts as well as instruments classified as loans based on GAAP in this section.

For all products, use the [Counterparty] field to further identify the type of borrower as one of the following:

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

### I.U.1: Onshore Placements

Refers to unsecured placements of the domestic currency between eligible domestic institutions made in the wholesale inter-bank or inter-dealer broker market (e.g., fed funds[^11] sold, domestic sterling sold, domestic euro, domestic yen).

[^11]: See: http://www.newyorkfed.org/aboutthefed/fedpoint/fed15.html for definition.

### I.U.2: Offshore Placements

Refers to unsecured placements of the domestic currency outside of the onshore market, but still placed through the wholesale inter-bank or inter-dealer broker market (e.g., Eurodollars, EuroSterling, EuroYen, EuroEuro).

### I.U.3: Required Operational Balances

Refers to the minimum balances held at other financial counterparties necessary to maintain ongoing operational activities, such as clearing and settlement. These balances may not be mandated by the counterparty, but could include, for example, a minimum balance maintained by the reporting entity to avoid intraday or end-of-day overdraft fees.

### I.U.4: Excess Operational Balances

Refers to balances placed at other financial counterparties not reported in I.U.3: Required Operational Balances. If a reporting entity cannot reasonably identify excess balances, do not report any balance as excess and report the entire balance in I.U.3: Required Operational Balances.

### I.U.5: Outstanding Draws on Unsecured Revolving Facilities

Refers to the existing loan arising from the drawn portion of any unsecured revolving facility (e.g., a general working capital facility) extended by the reporting entity.

### I.U.6: Other Loans

Refers to all other unsecured loans not otherwise included in I.U products. Include any subordinated lending to affiliates that do not fall within the reporting entity's scope of consolidation. Use the comments table to provide a general description of other loans included in this product on at least a monthly basis and in the event of a material change in reported values.

### I.U.7: Cash Items in the Process of Collection

Refers to (1) checks or drafts in process of collection that are drawn on another depository institution (or a Federal Reserve Bank) and that are payable immediately upon presentation in the country where the covered company's office that is clearing or collecting the check or draft is located, including checks or drafts drawn on other institutions that have already been forwarded for collection but for which the reporting entity has not yet been given credit (known as cash letters), and checks or drafts on hand that will be presented for payment or forwarded for collection on the following business day; (2) government checks drawn on the Treasury of the United States or any other government agency that are payable immediately upon presentation and that are in process of collection; and (3) such other items in process of collection that are payable immediately upon presentation and that are customarily cleared or collected as cash items by depository institutions in the country where the covered company's office which is clearing or collecting the item is located.

### I.U.8: Short-Term Investments

Refers to balances, including, but not limited to time deposits, that are held as short-term investments (e.g., reported in schedule HC-B on the FR Y-9C) at external financial counterparties.

---

## I.S: Inflows-Secured

**General Guidance:** Report the contractual principal payments to be received. Exclude non-performing loans (i.e., 90-days past due or non-accrual), which are instead reported in Supplemental-Balance Sheet table. Report the fair (market) value of the pledged securities using the Collateral Value field. Report on a gross basis; do not net borrowings against loans unless the transactions contractually settle on a net basis. FIN 41 does not apply for this report. If an amortizing loan is underwritten on a forward-starting basis, the amount reported in the [Forward Start Amount] field, representing the initial disbursement of the loan, should be split across all associated products and should match the corresponding maturity amount (i.e., the principal payment received for that period).

**Asset Category:** For transactions that allow for collateral agreement amendments, report the transaction based on the actual stock of collateral held as of the as-of date (T).

For all products, use the [Counterparty] field to further identify the type of borrower as one of the following:

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

### I.S.1: Reverse Repo

Refers to all reverse repurchase agreements (including under Master Repurchase Agreement or Global Master Repurchase Agreements).

### I.S.2: Securities Borrowing

Refers to all securities borrowing transactions (including under Master Securities Loan Agreements).

### I.S.3: Dollar Rolls

Refers to transactions using "To Be Announced" (TBA) contracts with the intent of providing financing for a specific security or pool of collateral. Report transactions where the reporting entity has agreed to buy the TBA contract and sell it back at a later date.

### I.S.4: Collateral Swaps

Refers to transactions where non-cash assets are exchanged (e.g., collateral upgrade/downgrade trades) at the inception[^12] of the transaction, or a non-cash asset is borrowed and no collateral is posted (i.e., an unsecured borrowing of collateral), and the assets will be returned at a future date.

[^12]: Collateral swap transactions that are remargined with cash payments should continue to be reported under this product.
