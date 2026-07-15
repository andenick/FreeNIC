"""Phase 24: Ingest Pillar 3 disclosures from Knowledge Base CSVs.

Source: Technical/Knowledge_Base/{bank}_Pillar3_{quarter}/ CSV files
Target: pillar3_disclosures table

Parses extracted CSV tables from extracted from Pillar 3 quarterly disclosures
for 5 G-SIBs (JPM, BAC, WFC, C, MS). Focuses on capital, RWA, ratios, SLR, TLAC.
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, TECHNICAL_DIR

KB_DIR = TECHNICAL_DIR / "Knowledge_Base"

# Bank mapping: directory prefix -> (rssd_id, full_name)
BANK_MAP = {
    "JPM": (1039502, "JPMorgan Chase & Co."),
    "BAC": (1073757, "Bank of America Corporation"),
    "C":   (1951350, "Citigroup Inc."),
    "WFC": (1120754, "Wells Fargo & Company"),
    "MS":  (2162966, "Morgan Stanley"),
    # C2 (2026-06-05): the 3 remaining US G-SIBs. RSSDs verified vs institutions (FHD top-tier).
    "GS":  (2380443, "The Goldman Sachs Group, Inc."),
    "BK":  (3587146, "The Bank of New York Mellon Corporation"),
    "STT": (1111435, "State Street Corporation"),
}

# Quarter-end date mapping
QUARTER_ENDS = {
    "Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31",
}

# Keywords for classifying table type
TYPE_KEYWORDS = {
    "capital": ["capital composition", "capital component", "components of capital",
                "capital structure", "stockholders' equity", "tier 1", "tier 2",
                "cet1", "total capital", "capital reconciliation"],
    "rwa": ["risk-weighted assets", "rwa", "risk weighted"],
    "ratios": ["capital ratio", "capital adequacy", "regulatory capital metric",
               "binding ratio"],
    "slr": ["supplementary leverage", "slr", "leverage ratio", "leverage exposure"],
    "tlac": ["total loss-absorbing", "tlac", "long-term debt", "eligible ltd"],
    "credit_risk": ["credit risk exposure", "credit risk rwa", "retail credit",
                    "wholesale credit"],
    "market_risk": ["market risk", "value-at-risk", "var", "stressed var"],
    "operational_risk": ["operational risk"],
}


def classify_table(table_title):
    """Classify a table based on its title."""
    title_lower = table_title.lower()
    for dtype, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                return dtype
    return "other"


def parse_period(dirname):
    """Extract (bank_prefix, period_end_date) from directory name like JPM_Pillar3_2024Q1."""
    match = re.match(r"([A-Z]+)_Pillar3_(\d{4})(Q[1-4])", dirname)
    if match:
        prefix = match.group(1)
        year = match.group(2)
        quarter = match.group(3)
        return prefix, f"{year}-{QUARTER_ENDS[quarter]}"
    return None, None


def clean_value(val):
    """Try to parse a numeric value from a string. Handles $, commas, parens, %."""
    if not val or not val.strip():
        return None, None

    s = val.strip()

    # Skip footnote markers, asterisks, dashes
    if s in ("-", "—", "–", "N/A", "n/a", "NM", "nm", "*"):
        return None, None

    # Detect percentage
    is_pct = "%" in s
    unit = "percent" if is_pct else "millions"

    # Clean the string
    s = s.replace("$", "").replace(",", "").replace("%", "").replace("*", "").strip()

    # Handle parentheses as negative
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]

    try:
        return float(s), unit
    except ValueError:
        return None, None


def parse_csv_table(filepath):
    """Parse a Pillar 3 CSV table. Returns (table_title, rows_of_data)."""
    rows = []
    table_title = ""

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    if not all_rows:
        return "", []

    # First row often contains "Table:" or "Table," prefix with the title
    first = all_rows[0]
    if first and (first[0].startswith("Table:") or first[0].startswith("Table,")):
        table_title = first[0].replace("Table:", "").replace("Table,", "").strip()
        if len(first) > 1 and not table_title:
            table_title = first[1].strip()
        all_rows = all_rows[1:]
    elif first and len(first) >= 1:
        # Sometimes the title IS the first cell
        table_title = first[0].strip()

    if not all_rows:
        return table_title, []

    # Second row (after title) is usually column headers
    headers = all_rows[0] if all_rows else []
    data_rows = all_rows[1:] if len(all_rows) > 1 else []

    # Determine how many numeric columns there are
    num_cols = len(headers)

    for row in data_rows:
        if not row or not row[0].strip():
            continue

        label = row[0].strip()

        # Skip rows that are clearly not data (footnotes, notes, etc.)
        if label.startswith("(") and len(label) < 5:
            continue
        if label.startswith("Source:") or label.startswith("Note:"):
            continue
        if label.startswith("* ") or label.startswith("(a)"):
            continue

        # Try to extract values from remaining columns
        for col_idx in range(1, min(len(row), num_cols)):
            val, unit = clean_value(row[col_idx])
            if val is not None:
                col_label = headers[col_idx].strip() if col_idx < len(headers) else f"col_{col_idx}"
                rows.append({
                    "variable_id": label,
                    "value": val,
                    "unit": unit,
                    "column_label": col_label,
                })

    return table_title, rows


def main():
    elapsed = timer()
    print("=== Phase 24: Pillar 3 Disclosures Ingestion ===\n")

    con = get_db()

    # Create table
    con.execute("DROP TABLE IF EXISTS pillar3_disclosures")
    con.execute("""
        CREATE TABLE pillar3_disclosures (
            rssd_id         INTEGER,
            bank_name       VARCHAR,
            period_end      DATE,
            disclosure_type VARCHAR,
            table_name      VARCHAR,
            variable_id     VARCHAR,
            value           DOUBLE,
            unit            VARCHAR,
            source_file     VARCHAR
        )
    """)

    # Find all Pillar 3 directories
    pillar3_dirs = sorted([d for d in KB_DIR.iterdir()
                          if d.is_dir() and "Pillar3" in d.name])

    total_rows = 0
    total_tables = 0
    skipped_tables = 0

    for pdir in pillar3_dirs:
        prefix, period_end = parse_period(pdir.name)
        if not prefix or prefix not in BANK_MAP:
            print(f"  SKIP: Cannot parse {pdir.name}")
            continue

        rssd_id, bank_name = BANK_MAP[prefix]
        print(f"  {pdir.name} -> {bank_name} ({period_end})")

        # Find all CSV table files
        csv_files = sorted(pdir.glob("*_table_*.csv"))
        dir_rows = 0

        for csv_file in csv_files:
            table_title, data_rows = parse_csv_table(csv_file)
            dtype = classify_table(table_title)

            # Skip disclosure maps and "other" tables
            if dtype == "other":
                if "disclosure map" in table_title.lower() or "map" in table_title.lower():
                    skipped_tables += 1
                    continue
                # Still include "other" if it has numeric data
                if not data_rows:
                    skipped_tables += 1
                    continue

            total_tables += 1

            for row in data_rows:
                con.execute("""
                    INSERT INTO pillar3_disclosures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rssd_id, bank_name, period_end, dtype,
                    table_title[:200], row["variable_id"][:200],
                    row["value"], row["unit"],
                    csv_file.name
                ))
                dir_rows += 1

        total_rows += dir_rows
        print(f"    {len(csv_files)} CSVs -> {dir_rows} observations")

    # Summary
    count = con.execute("SELECT COUNT(*) FROM pillar3_disclosures").fetchone()[0]
    banks = con.execute("SELECT COUNT(DISTINCT rssd_id) FROM pillar3_disclosures").fetchone()[0]
    periods = con.execute("SELECT COUNT(DISTINCT period_end) FROM pillar3_disclosures").fetchone()[0]
    types = con.execute("SELECT disclosure_type, COUNT(*) FROM pillar3_disclosures GROUP BY 1 ORDER BY 2 DESC").fetchall()

    print(f"\n--- Summary ---")
    print(f"  Total observations: {count:,}")
    print(f"  Banks: {banks}")
    print(f"  Periods: {periods}")
    print(f"  Tables parsed: {total_tables}")
    print(f"  Tables skipped: {skipped_tables}")
    print(f"  By type:")
    for dtype, cnt in types:
        print(f"    {dtype}: {cnt:,}")

    con.close()

    secs = elapsed()
    log_ingestion("24", f"Pillar 3: {count:,} obs, {banks} banks, {periods} periods, "
                  f"{total_tables} tables. {secs:.1f}s")
    print(f"\nPhase 24 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
