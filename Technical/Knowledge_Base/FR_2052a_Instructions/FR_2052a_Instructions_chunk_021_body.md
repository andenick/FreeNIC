# FR 2052a Instructions -- Chunk 021
## Appendix VIII: LRM: NSFR to FR 2052a Mapping (Enclosure Pages 7-16)

### NSFR Liabilities Assigned a 90 Percent ASF Factor (SS.104(c)) (continued)

#### (10) Not FDIC Insured Transactional and Non-Relationship Retail Deposits, Excluding Sweeps and Brokered Deposits (SS.104(c)(1))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.1, 2
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Insured**: Not FDIC
- All other fields: # (any value) or * (aggregated amount)

#### (11) Non-Relationship Retail Deposits, Excluding Sweeps and Brokered Deposits (SS.104(c)(1))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.3, O.D.14
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Insured**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (12) Insured Reciprocal Brokered Deposits (SS.104(c)(2))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.13
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Insured**: FDIC
- All other fields: # (any value) or * (aggregated amount)

#### (13) Not FDIC Insured Affiliated Relationship Sweep Deposits (SS.104(c)(3))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.9
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Insured**: Not FDIC
- All other fields: # (any value) or * (aggregated amount)

#### (14) Less Stable Affiliated Retail Sweep Deposits (SS.104(c)(3))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.10
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- All other fields: # (any value) or * (aggregated amount)

#### (15) Non-Reciprocal Brokered Deposits Maturing in >= 1 Year (SS.104(c)(4))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.8
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Maturity Bucket**: >= 1 Year
- All other fields: # (any value) or * (aggregated amount)

### NSFR Liabilities Assigned a 50 Percent ASF Factor (SS.104(d))

#### (16) Unsecured Wholesale Non-Deposit Funding from Non-Financials Maturing in < 1 Year (SS.104(d)(1))

- **Reporting Entity**: NSFR Entity
- **PID**: O.W.9, 10, 17, 18, 19
- **Product**: Matches PID
- **Counterparty**: Non-Financial Wholesale Entity
- **Maturity Bucket**: < 1 Year [^1]
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Loss Absorbency**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

[^1]: In general, a Maturity Bucket condition of "less than" a certain time horizon without an explicit lower bound includes the "Open" maturity bucket unless stated otherwise (i.e., with the exclusion "but not Open").

#### (17) Unsecured Wholesale Deposit Funding from Non-Financials Maturing in < 1 Year (SS.104(d)(1))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.5, 6, 8, 10, 11, 13, 14, 15
- **Product**: Matches PID
- **Counterparty**: Non-Financial Wholesale Entity
- **Maturity Bucket**: < 1 Year
- **Collateral Class**: NULL
- All other fields: # (any value) or * (aggregated amount)

#### (18) Securities Financing Transactions with Non-Financials Maturing in < 1 Year (SS.104(d)(2))

- **Reporting Entity**: NSFR Entity
- **PID**: O.S.1, 2, 3, 5, 7, 11
- **Product**: Matches PID
- **Sub-Product**: # (any value)
- **Counterparty**: Non-Financial Wholesale Entity
- **Maturity Bucket**: < 1 Year
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Treasury Control**: # (any value)
- **Settlement**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (19) Collateralized Deposits from Non-Financials Maturing in < 1 Year (SS.104(d)(2))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.5, 6, 8, 10, 11, 13, 14, 15
- **Product**: Matches PID
- **Counterparty**: Non-Financial Wholesale Entity
- **Maturity Bucket**: < 1 Year
- **Collateral Class**: Not NULL
- All other fields: # (any value) or * (aggregated amount)

#### (20) Unsecured Wholesale Non-Deposit Funding from Financials and Central Banks Maturing in >= 6 Months, but < 1 Year (SS.104(d)(3))

- **Reporting Entity**: NSFR Entity
- **PID**: O.W.9, 10, 17, 18, 19
- **Product**: Matches PID
- **Counterparty**: Financial Sector Entity, Central Bank
- **Maturity Bucket**: >= 6 Months, < 1 Year
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Loss Absorbency**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (21) Unsecured Wholesale Deposit Funding from Financials and Central Banks Maturing in >= 6 Months, but < 1 Year (SS.104(d)(3))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.5, 6, 8, 10, 11, 13, 14, 15
- **Product**: Matches PID
- **Counterparty**: Financial Sector Entity, Central Bank
- **Maturity Bucket**: >= 6 Months, < 1 Year
- **Collateral Class**: NULL
- All other fields: # (any value) or * (aggregated amount)

#### (22) Securities Financing Transactions with Financials and Central Banks Maturing in >= 6 Months, but < 1 Year (SS.104(d)(4))

- **Reporting Entity**: NSFR Entity
- **PID**: O.S.1, 2, 3, 6, 11
- **Product**: Matches PID
- **Sub-Product**: Not FRFF
- **Counterparty**: Financial Sector Entity, Central Bank
- **Maturity Bucket**: >= 6 Months, < 1 Year
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Treasury Control**: # (any value)
- **Settlement**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (23) Secured Wholesale Deposit Funding from Financials and Central Banks Maturing in >= 6 Months, but < 1 Year (SS.104(d)(4))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.5, 6, 8, 10, 11, 13, 14, 15
- **Product**: Matches PID
- **Counterparty**: Financial Sector Entity, Central Bank
- **Maturity Bucket**: >= 6 Months, < 1 Year
- **Collateral Class**: Not NULL
- All other fields: # (any value) or * (aggregated amount)

#### (24) Securities Issued Maturing in >= 6 Months, but < 1 Year (SS.104(d)(5))

- **Reporting Entity**: NSFR Entity
- **PID**: O.W.1-8, 11-16
- **Product**: Matches PID
- **Counterparty**: # (any value)
- **Maturity Bucket**: >= 6 Months, < 1 Year
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Loss Absorbency**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (25) Operational Deposits (SS.104(d)(6))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.4, 7
- **Product**: Matches PID
- **Counterparty**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (26) Non-Reciprocal Brokered Retail Deposits in Transactional Accounts and Non-Reciprocal Brokered Retail Deposits Maturing in >= 6 Months, but < 1 Year (SS.104(d)(7))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.8
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Maturity Bucket**: Open or >= 6 Months, < 1 Year
- All other fields: # (any value) or * (aggregated amount)

#### (27) Non-Affiliated Retail Sweep Deposits (SS.104(d)(8))

- **Reporting Entity**: NSFR Entity
- **PID**: O.D.11
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- All other fields: # (any value) or * (aggregated amount)

#### (28) Other Unsecured Funding from Retail Customers (SS.104(d)(9))

- **Reporting Entity**: NSFR Entity
- **PID**: O.W.18, 19
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Loss Absorbency**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (29) Other Secured Funding from Retail Customers (SS.104(d)(9))

- **Reporting Entity**: NSFR Entity
- **PID**: O.S.1, 2, 3, 7, 11
- **Product**: Matches PID
- **Sub-Product**: # (any value)
- **Counterparty**: Retail, Small Business
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- **Treasury Control**: # (any value)
- **Settlement**: # (any value)
- All other fields: # (any value) or * (aggregated amount)

#### (30) Interest Payable to Retail Customers (SS.104(d)(9))

- **Reporting Entity**: NSFR Entity
- **PID**: O.O.19
- **Product**: Matches PID
- **Counterparty**: Retail, Small Business
- **Forward Start Amount**: NULL
- **Forward Start Bucket**: NULL
- All other fields: # (any value) or * (aggregated amount)
