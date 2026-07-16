# Data License & Attribution

FreeNIC's **source code** is released under the MIT License (see `LICENSE`).

The **data** redistributed in this package originates from external sources with
their own terms. This file states those terms and the attribution FreeNIC
carries forward. Two non-trivially-licensed sources remain after deduplication;
both expressly permit redistribution of derived subsets, and FreeNIC complies
with their attribution requirements below.

Nothing here restricts FreeNIC's MIT-licensed code. Where data terms and the MIT
license could appear to conflict, the data terms govern the *data* only.

> **Verified June 2026** against primary sources (see `Outputs/PROVENANCE.csv`).
> All other ingested sources are public US regulatory data (FFIEC, FDIC, Federal
> Reserve, OCC, FRED) carrying no redistribution restriction.

---

## 1. `luck_call_reports` — NY Fed Call Reports, 1959–2025
**FreeNIC redistributes the 1959Q4–1975Q4 slice** (the pre-Chicago-Fed window with no
Fed-direct bulk equivalent; 1976+ is served by `call_report_filings`).

**Source.** Federal Reserve Bank of New York, "Balance Sheets and Income
Statements of Commercial Banks: 1959 to 2025."
<https://www.newyorkfed.org/research/banking_research/balance-sheets-income-statements>

**Terms.** Governed by the New York Fed website Terms of Use
(<https://www.newyorkfed.org/privacy/termsofuse>). The NY Fed grants a
non-exclusive license to "use, copy, and distribute Content," to "Download,
store, and use Content in any format or media," and to "Modify and create
derivative works from the Content." Redistribution of a derived subset (as
FreeNIC does) is therefore permitted.

**Conditions FreeNIC observes.**
- We retain the NY Fed source identification and the attribution below.
- FreeNIC is in no way endorsed by, or affiliated with, the Federal Reserve
  Bank of New York. The NY Fed name is not used here for advertising or endorsement.
- The data is provided "as is"; the NY Fed disclaims all liability for any use.

**Required attribution / citation.**
> Sergio Correia, Tiffany Fermin, Stephan Luck, and Emil Verner,
> "A New Public Data Source: Call Reports from 1959 to 2025,"
> Federal Reserve Bank of New York *Liberty Street Economics*,
> December 22, 2025. https://doi.org/10.59576/lse.20251222

Underlying research paper:
> Sergio Correia, Stephan Luck, and Emil Verner, "Failing Banks,"
> *Quarterly Journal of Economics* 141(1), February 2026, 147–204.
> https://doi.org/10.1093/qje/qjaf044

> **Note (cleanest path):** the *same* underlying replication data is also deposited
> on Harvard Dataverse under **CC0 1.0** (DOI 10.7910/DVN/Q22XR1). Sourcing the
> 1959+ slice from that CC0 deposit would place this table in the public domain too
> and remove the website-ToU attribution dependency. Considered for a future release.

---

## 2. `occ_historical` (`source = occ_historical_clv`) — Historical Call Reports, 1863–1941

**Source.** Correia, Sergio; Luck, Stephan; Verner, Emil, 2025,
"Replication Data for: Failing Banks," Harvard Dataverse, V1.
<https://doi.org/10.7910/DVN/Q22XR1>
Mirror: <https://scorreia.com/data/call-reports.html>
Digitized from primary U.S. Office of the Comptroller of the Currency (OCC)
*Annual Report to Congress* volumes (<https://www.occ.gov>).

**License.** **CC0 1.0 Universal (Public Domain Dedication)** —
<http://creativecommons.org/publicdomain/zero/1.0/>. The Harvard Dataverse
deposit is published under CC0 1.0 with no access restrictions. Redistribution,
modification, and commercial use are permitted with no legal conditions. The
underlying OCC Annual Reports are U.S. federal government works and are in the
public domain under U.S. copyright law, independently confirming there is no
copyright barrier to this slice.

**Attribution (requested as courtesy, not legally required under CC0).**
> Correia, Sergio; Luck, Stephan; Verner, Emil, 2025,
> "Replication Data for: Failing Banks," Harvard Dataverse, V1.
> https://doi.org/10.7910/DVN/Q22XR1

Methodology references the compilers ask that you cite:
> Mark Carlson, Sergio Correia, and Stephan Luck, "The Effects of Banking
> Competition on Growth and Financial Stability: Evidence from the National
> Banking Era," *Journal of Political Economy* (2022).
>
> Sergio Correia and Stephan Luck, "Digitizing Historical Balance Sheet Data:
> A Practitioner's Guide," *Explorations in Economic History* (2023).

---

## Summary

| Table | Slice shipped | Source | License | Redistribute? | Attribution |
|---|---|---|---|---|---|
| `luck_call_reports` | 1959Q4–1975Q4 | NY Fed | NY Fed Terms of Use (permissive, non-exclusive) | Yes, with attribution | Required |
| `occ_historical` | 1863–1941 | Harvard Dataverse (CLV) / OCC | CC0 1.0 (public domain) | Yes, unconditionally | Courtesy only |
| all other tables | — | FFIEC / FDIC / Fed / OCC / FRED (public regulatory) | public, no restriction | Yes | Source noted in `PROVENANCE.csv` |

*Terms verified against primary sources, June 2026. If you redistribute FreeNIC
further, carry these notices forward.*
