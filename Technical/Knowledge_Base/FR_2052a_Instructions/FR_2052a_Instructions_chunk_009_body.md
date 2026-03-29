# FR 2052a Instructions - Chunk 009
## Pages 80-89: Appendix I (Data Format, Tables, Fields), Appendix II-a (Product/Sub-Product Requirements), Appendix II-b (Counterparty Requirements)

## Appendix I: FR 2052a Data Format, Tables, and Fields

### Layout of the Data Collection

The technical architecture for the data collection of the FR 2052a report subdivides the three general categories of inflows, outflows, and supplemental items into 13 distinct data tables and includes a mechanism for tracking comments. These tables are designed to stratify the assets, liabilities, and supplemental components of a firm's liquidity risk profile based on common data structures, while still maintaining a coherent framework for liquidity risk reporting.

#### Diagram 1 -- FR 2052a Tables and Information Hierarchy

**Inflows:** Assets, Unsecured, Secured, Other inflows

**Outflows:** Deposits, Wholesale, Secured, Other outflows

**Supplemental:** Derivatives & Collateral, Liquidity Risk Measurement, Balance Sheet, Informational, Foreign exchange, Comments

### The FR 2052a Data Element

Each table is comprised of a set of fields (i.e., columns) that define the requisite level of aggregation or granularity for each data element (i.e., row, or record).[^15] The FR 2052a framework is a "flat" or tabular structure with predefined columns and an unconstrained number of rows. The volume of data elements reported should therefore change dynamically as the size and complexity of the reporting firm's funding profile changes.

[^15]: Appendix I details the structure of each table.

- All notional currency-denominated values should be reported in millions of that currency (e.g., U.S. dollar-denominated transactions in USD millions, sterling-denominated transactions in GBP millions, etc.)
- Example: The holding company has four outstanding issuances of plain vanilla long-term debt:
  - 500mm USD-denominated bond maturing in 4 years and 6 months,
  - 1,000mm USD-denominated bond maturing in 5 years,
  - 2,000mm GBP-denominated bond maturing in 10 years, and
  - 250mm GBP-denominated bond maturing in 1 year and 6 months.
- Assume the USD-denominated liabilities are issued in New York, while the GBP-denominated liabilities are issued in London, and all three issuances qualify as TLAC. In this case, the two USD-denominated bonds should be summed up and reported as a single FR 2052a data element, as they exhibit the same values in all non-numeric fields (note that although the maturities are different, they both fall within the ">4 years <=5 years" maturity bucket). The two GBP issuances, however should not be aggregated, as they fall in separate and distinct maturity buckets (">1 year <= 2 years" versus "> 5 years").

See Table 2 (extracted as CSV: FR_2052a_Instructions_chunk_009_table_001.csv) for data element aggregation example.

### Naming Conventions and Field Types

This document uses a standard syntax to refer to specific tables, fields and products in the FR 2052a data hierarchy.

- **Prefixes** are the first component of the FR 2052a data reference syntax. There are three distinct prefixes: I, O and S, which correspond to the first letter of each specific section in the FR 2052a data hierarchy: Inflows, Outflows and Supplemental.
- **Tables** are referenced using the appropriate prefix, followed by the first letter of the table (with the exceptions of derivatives & collateral and foreign exchange, which are referenced as "DC" and "FX", respectively).
  - Example: the "Assets" table, which relates to inflows, is referenced as I.A, while the "Deposits" table, which relates to outflows, is referenced as O.D.
- **Products** are referenced using the table syntax and the corresponding product number.
  - Note: The [Product] field designation is omitted to simplify the reference syntax. A number following the table designation always refers to the product number for that table.
  - Example: "Unencumbered Assets" (product #1) in the "Assets" table is referred to as I.A.1.

See Table 3 (extracted as CSV: FR_2052a_Instructions_chunk_009_table_002.csv) for the product reference syntax structure.

### Field Types

The data fields in each FR 2052a table fall into two categories:

1. **Mandatory fields** (May vary for each product, colored red in Table 4)
2. **Dependent fields** (colored blue in Table 4)
   - Required for certain transaction types.
     - Example: the [Forward Start Bucket] field is generally only required for forward starting transactions.
     - Example: the [Internal Counterparty] field is only required for intercompany transactions.
   - [Sub-Product] required for certain products.
     - Example: The "Capacity" product in the Assets table (I.A.2) requires a [Sub-Product] designation.

See Table 4 (extracted as CSV: FR_2052a_Instructions_chunk_009_table_003.csv) for required versus dependent fields example.

### Data Tables

Note that the Currency and Converted attributes are required for each value field in accordance with the Field Definitions. These fields have been omitted from these figures to simplify the illustration of the FR 2052a data structure.

The complete data table field listings for all 13 FR 2052a tables are extracted as CSV files: FR_2052a_Instructions_chunk_009_table_004.csv (Inflows and Outflows table structures) and FR_2052a_Instructions_chunk_009_table_005.csv (Supplemental table structures).

---

## Appendix II-a: FR 2052a Product/Sub-Product Requirements

The product/sub-product requirements table is extracted as CSV: FR_2052a_Instructions_chunk_009_table_006.csv

---

## Appendix II-b: FR 2052a Counterparty Requirements (begins)

The counterparty requirements table begins on page 88 and continues into Chunk 010. See FR_2052a_Instructions_chunk_009_table_007.csv for the portion in this chunk.
