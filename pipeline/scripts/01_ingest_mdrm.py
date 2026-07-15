"""Phase 1: Ingest MDRM (Micro Data Reference Manual) into freenic database.

Source: MDRM_CSV.csv — the variable dictionary defining all FFIEC reporting codes.
Format: CSV with "PUBLIC" header line, quoted fields, HTML entities in descriptions.
"""

import csv
import html
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, file_checksum, INPUT_PATHS

# Canonical MDRM location (duplicates removed in Session 7 cleanup)
MDRM_PATHS = [
    INPUT_PATHS['mdrm'],
]

CANONICAL_PATH = MDRM_PATHS[0]


def parse_mdrm_date(date_str):
    """Parse MDRM date format: '9/30/2016 12:00:00 AM' -> 'YYYY-MM-DD'."""
    if not date_str or date_str.strip() == "":
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%m/%d/%Y %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None


def clean_description(desc):
    """Clean HTML entities and normalize whitespace in descriptions."""
    if not desc:
        return desc
    # Decode HTML entities (&#x0D; etc.)
    cleaned = html.unescape(desc)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def verify_duplicates():
    """Check that all 3 MDRM copies are identical."""
    print("Verifying MDRM file duplicates...")
    checksums = {}
    for path in MDRM_PATHS:
        if path.exists():
            cs = file_checksum(path)
            checksums[str(path)] = cs
            print(f"  {path.name} ({path.parent.name}): {cs[:16]}...")
        else:
            print(f"  MISSING: {path}")

    unique = set(checksums.values())
    if len(unique) == 1:
        print(f"  All {len(checksums)} copies are IDENTICAL.")
        return True
    else:
        print(f"  WARNING: {len(unique)} distinct versions found!")
        return False


def main():
    elapsed = timer()
    print("=== Phase 1: MDRM Ingestion ===")

    # Step 1: Verify duplicates
    all_identical = verify_duplicates()

    # Step 2: Parse canonical MDRM
    print(f"\nParsing {CANONICAL_PATH}...")

    rows = []
    skipped_header = False
    unique_mnemonics = set()
    unique_items = set()

    with open(CANONICAL_PATH, "r", encoding="utf-8-sig") as f:
        # Skip "PUBLIC" header line
        first_line = f.readline().strip()
        if first_line == "PUBLIC":
            print("  Skipped 'PUBLIC' header line")
        else:
            f.seek(0)  # Not the expected header, rewind

        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            mnemonic = (row.get("Mnemonic") or "").strip()
            item_code = (row.get("Item Code") or "").strip()

            if not mnemonic or not item_code:
                continue

            variable_id = mnemonic + item_code
            unique_mnemonics.add(mnemonic)
            unique_items.add(item_code)

            rows.append((
                mnemonic,
                item_code,
                variable_id,
                (row.get("Item Name") or "").strip(),
                parse_mdrm_date(row.get("Start Date", "")),
                parse_mdrm_date(row.get("End Date", "")),
                (row.get("Confidentiality") or "").strip(),
                (row.get("ItemType") or "").strip(),
                (row.get("Reporting Form") or "").strip(),
                clean_description(row.get("Description", "")),
                clean_description(row.get("SeriesGlossary", "")),
            ))

            if (i + 1) % 100000 == 0:
                print(f"  Parsed {i + 1:,} rows...")

    print(f"  Total parsed: {len(rows):,} rows")
    print(f"  Unique mnemonics: {len(unique_mnemonics):,}")
    print(f"  Unique item codes: {len(unique_items):,}")
    print(f"  Unique variable_ids: {len(set(r[2] for r in rows)):,}")

    # Step 3: Load into DuckDB
    print("\nLoading into DuckDB...")
    con = get_db()

    # Clear existing data
    con.execute("DELETE FROM mdrm")

    # Batch insert
    con.executemany("""
        INSERT INTO mdrm (mnemonic, item_code, variable_id, item_name,
                          start_date, end_date, confidentiality, item_type,
                          reporting_form, description, series_glossary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    # Verify
    count = con.execute("SELECT COUNT(*) FROM mdrm").fetchone()[0]
    print(f"  Loaded: {count:,} rows")

    # Extract distinct reporting forms
    con.execute("DELETE FROM reporting_forms")
    con.execute("""
        INSERT INTO reporting_forms (form_code, form_name, filing_type)
        SELECT DISTINCT reporting_form, reporting_form,
            CASE
                WHEN reporting_form LIKE '%Y-9C%' THEN 'Y9C'
                WHEN reporting_form LIKE '%Y-9LP%' THEN 'Y9LP'
                WHEN reporting_form LIKE '%Call%' OR reporting_form LIKE '%031%'
                    OR reporting_form LIKE '%041%' OR reporting_form LIKE '%051%' THEN 'CALL'
                WHEN reporting_form LIKE '%101%' THEN 'FFIEC101'
                WHEN reporting_form LIKE '%Thrift%' OR reporting_form LIKE '%SVGL%' THEN 'THRIFT'
                ELSE 'OTHER'
            END
        FROM mdrm
        WHERE reporting_form IS NOT NULL AND reporting_form != ''
    """)
    form_count = con.execute("SELECT COUNT(*) FROM reporting_forms").fetchone()[0]
    print(f"  Extracted {form_count} distinct reporting forms")

    # Quick stats
    print("\nTop 10 mnemonics by row count:")
    top = con.execute("""
        SELECT mnemonic, COUNT(*) as cnt
        FROM mdrm
        GROUP BY mnemonic
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()
    for m, c in top:
        print(f"  {m}: {c:,}")

    print(f"\nItem types distribution:")
    types = con.execute("""
        SELECT item_type, COUNT(*) as cnt
        FROM mdrm
        GROUP BY item_type
        ORDER BY cnt DESC
    """).fetchall()
    for t, c in types:
        print(f"  {t or '(empty)'}: {c:,}")

    # Record in catalog.data_sources
    con.execute("""
        INSERT OR REPLACE INTO catalog.data_sources
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'mdrm_canonical',
        str(CANONICAL_PATH),
        'CSV',
        CANONICAL_PATH.stat().st_size,
        count,
        11,
        'all time',
        'MDRM variable dictionary - defines all FFIEC reporting codes',
        datetime.now().isoformat(),
        '01_ingest_mdrm.py',
        file_checksum(CANONICAL_PATH)[:32],
    ))

    con.close()

    secs = elapsed()
    log_ingestion("1", f"MDRM ingested: {count:,} rows, {len(unique_mnemonics)} mnemonics, {form_count} forms. Duplicates identical: {all_identical}. {secs:.1f}s")
    print(f"\nPhase 1 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
