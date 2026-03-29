# FR Y-14M Instructions - Chunk 006
## Schedule A: Domestic First Lien Closed-End 1-4 Family Residential Mortgage Loan Data Dictionary (Continued)

### A.1 Loan Level Table (Continued)

This chunk continues the Schedule A.1 Loan Level Table data dictionary, covering Line Items 91 through 119. These items address loss mitigation conversions, credit deterioration status, involuntary termination financials, modification parameters, property valuation methods, regulatory flags, and credit scoring metadata.

#### Line Items 91-92: Loss Mitigation Conversion and Credit Status

**Item 91 - Interest Type Conversion Duration (M233):** Reports whether the interest type was converted from ARM to Fixed through loss mitigation, and the duration of the fixed rate period. Should only be populated for loans with a value in Line Item 74 (Modification Type) indicating that a loan has been modified. Values range from 0 (Not converted) through 4 (Converted to Fixed Rate for Greater than 120 Months).

**Item 92 - Purchased Credit Deteriorated Status (M234):** Reports whether any loans are accounted for as purchased credit-deteriorated. If the loan is a PCD loan, code "Y"; otherwise "N". None of the records should be left blank.

#### Line Items 93-95: Involuntary Termination Financial Data

**Item 93 - Total Debt at Time of any Involuntary Termination (M235):** Reports total debt at the time of any involuntary termination at gross (not net) values, comprising: (1) Unpaid Principal Balance; (2) Interest pass through Amount; (3) Total Corporate Advance (incl. Property Preservation and Attorney's fees); (4) Total Escrow Advance (taxes and insurance paid). Any involuntary termination includes REO, Short Sale, Deed-in-lieu of foreclosure, Third Party Sale or Charge-off. This is a required line item for Investor Type code values 4 (Private Securitized) and 7 (Portfolio) and best efforts for all others. Values reported as whole numbers using banker's rounding.

**Item 94 - Net Recovery Amount (M236):** Reports the sales price net of costs of sales (e.g., sales commissions and buyer concessions). Net proceeds should be the same as Net Recovery Amount; report net proceeds in Line item 94 for short sales and third party sales, along with all other involuntary terminations. Since the net recovery amount cannot be computed until the loan has been sold (or charged off), the sales price of the property should also be placed in Line item 121. Required for Investor Type code values 4 and 7, best efforts for all others.

**Item 95 - Credit Enhanced Amount (M237):** Reports the total amount of credit enhancement received that offset the loss, which could come from mortgage insurance proceeds, pool arrangements in deals, or other features of securities structures. Required for Investor Type code values 4 and 7, best efforts for all others.

#### Line Items 96-97: Regulatory and Accounting Flags

**Item 96 - Troubled Debt Restructure Flag (M238):** Reports whether a loan was modified as a Troubled Debt Restructuring (TDR), as defined in the FR Y-9C Glossary entry for "Troubled Debt Restructuring." All TDRs should be evaluated for credit losses as part of the Allowance for Credit Losses on Loans and Leases (ACL) analysis. This field only applies to portfolio loans; for non-portfolio loans leave blank.

**Item 97 - Reported as Bank Owned Flag (M239):** Reports whether the serviced-for-others loan is recorded on the bank's own balance sheet for accounting purposes. Applies only to loans with an Investor Code other than "Portfolio." Should be coded as Y for: (1) GNMA Eligible Repurchases -- In accordance with FAS 140, GNMA loans subject to Removal of Accounts Provisions (ROAPs) and eligible for repurchase; (2) Other Loans Reported On-Balance Sheet under FAS 140 -- to reflect bank-supported securitizations and/or other indemnifications.

#### Line Items 98-99: Interest Rate Modification Items

**Item 98 - Interest Rate Reduced (M262):** Retired September 2022.

**Item 99 - Interest Rate Frozen (M232):** Reports whether the interest rate was frozen and at a lower rate than if allowed to adjust through loss mitigation. For example, if a loan resetting from 4% to 6% is frozen at the 4% rate, the BHC or IHC or SLHC would report "Y". Should only be populated for loans with a value in Line item 74 (Modification Type).

#### Line Items 100-108: Modification Before/After Comparison Items

**Item 100 - Term Extended (M929):** Retired September 2022.

**Item 101 - P&I Amount Before Modification (M930):** Retired September 2022.

**Item 102 - P&I Amount After Modification (M931):** Retired September 2022.

**Item 103 - Interest Rate Before Modification (M932):** Reports the interest rate in the month prior to loan modification. Should only be populated for loans with a value in Line item 74 (Modification Type). Provided as a decimal (e.g., 0.0575 for 5.75%).

**Item 104 - Interest Rate After Modification (M933):** Reports the interest rate in the month after loan modification. Should only be populated for loans with a value in Line item 74 (Modification Type). Provided as a decimal.

**Item 105 - Remaining Term Before Modification (M934):** Retired September 2022.

**Item 106 - Remaining Term After Modification (M935):** Retired September 2022.

**Item 107 - Escrow Amount Before Modification (M936):** Retired March 2020.

**Item 108 - Escrow Amount After Modification (M937):** Retired March 2020.

#### Line Items 109-111: Loss Mitigation and Property Valuation

**Item 109 - Alternative Home Liquidation Loss Mitigation Date (M938):** Retired March 2020.

**Item 110 - Alternative Home Retention Loss Mitigation Date (M939):** Retired March 2020.

**Item 111 - Original Property Valuation Method (appraisal method) (M940):** Reports the method by which the value of the property was determined at the time the loan was originated. Options are:
- 1 = Full Appraisal -- Prepared by a certified appraiser involving both interior and exterior inspections of the subject property by a licensed appraiser
- 2 = Limited Appraisal -- Prepared by a certified appraiser that obtains characteristics of the property without the licensed appraiser performing a full interior and exterior inspection
- 3 = Broker Price Opinion "BPO" -- Prepared by a real estate broker or agent
- 4 = Desktop Valuation -- Prepared by bank employee
- 5 = Automated Valuation Model "AVM"
- 6 = Unknown

#### Line Items 112-116: Foreclosure, Escrow, and Insurance

**Item 112 - Third Party Sale Flag (M941):** Identification of Third Party Sales at time of Foreclosure Sale. Reports any loan where the title has transferred to a party other than the servicer at the time of foreclosure sale. If the loan was not sold to a third party or is not currently in foreclosure, code with zero.

**Item 113 - Escrow Amount Current (M268):** Reports the scheduled escrow amount (including taxes and insurance) due from the borrower scheduled for the reporting month. For non-escrow loans, report a value of zero.

**Item 114 - Escrow Amount at Origination (M942):** Retired March 2020.

**Item 115 - Remodified Flag (M943):** Reports whether the loan has been modified more than once in the last 24 months. Code with "Y" if the loan has been modified more than once in the last 24 months.

**Item 116 - Mortgage Insurance Company (M944):** Reports the mortgage insurance company. If the mortgage is insured against loss in any way, either through primary or pool-level insurance, report the company providing that insurance. If more than one company is insuring, give preference to the company providing the primary MI. MI Company Coding: 1=GE, 2=MGIC, 3=PMI, 4=UGIC, 5=RMIC, 6=Radian, 7=Integon, 8=Triad, 9=CMG, 10=Essent, 11=No MI, 12=Has MI - Company Other/Unknown, 13=National Mortgage Insurance, 14=Arch MI, 99=Unknown whether has MI. List subject to change for new MI Company entrants.

#### Line Items 117-119: Interest Type, Entity, and Loss Items

**Item 117 - Interest Type at Origination (M244):** Reports the interest type at origination. Fixed (1) -- loans where the interest rate is fixed for the entire term. Variable (2) -- loans where the interest rate fluctuates based on a spread to an index, including all variable rate loans regardless of whether there is an initial fixed period.

**Item 118 - Entity Serviced (M945):** Reports the federal regulator of the BHC or IHC or SLHC subsidiary that is servicing the loan. If the loan is a commercial loan secured by residential real estate loans, report the Federal Regulator of the entity servicing the commercial loan. Examples: national bank = OCC (code 2); state nonmember bank = FDIC (code 3); state member bank or subsidiary of BHC/IHC/SLHC that is not a federally insured bank = FRB (code 1).

**Item 119 - Loss/Write down Amount (M241):** Retired March 2020.
