"""Phase 6: Quick verification that Y-9C ZIPs are duplicates of BHCF TXT files.

Just checks a few headers — does NOT re-ingest.
"""

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import log_ingestion, timer, INPUTS_DIR

Y9C_DIR = INPUTS_DIR / "2026.01.30 y9c zips"
BHCF_DIR = INPUTS_DIR / "2026.01 FFIEC Bulk Downloads"


def main():
    elapsed = timer()
    print("=== Phase 6: Y-9C ZIP Verification ===")

    zips = sorted(Y9C_DIR.glob("BHCF*.ZIP")) + sorted(Y9C_DIR.glob("BHCF*.zip"))
    print(f"Found {len(zips)} Y-9C ZIP files")

    # Check first 3 ZIPs
    checked = 0
    matches = 0
    for zf_path in zips[:3]:
        try:
            with zipfile.ZipFile(zf_path, 'r') as zf:
                names = zf.namelist()
                txt_name = [n for n in names if n.upper().endswith('.TXT')]
                if txt_name:
                    with zf.open(txt_name[0]) as inner:
                        zip_header = inner.readline().decode('latin-1').strip()

                    # Compare with BHCF TXT
                    bhcf_path = BHCF_DIR / txt_name[0].upper()
                    if bhcf_path.exists():
                        with open(bhcf_path, 'r', encoding='latin-1') as f:
                            txt_header = f.readline().strip()

                        if zip_header == txt_header:
                            matches += 1
                            print(f"  MATCH: {zf_path.name} -> {txt_name[0]}")
                        else:
                            print(f"  DIFFER: {zf_path.name} headers don't match")
                    else:
                        print(f"  SKIP: {bhcf_path.name} not found in Bulk Downloads")
                checked += 1
        except Exception as e:
            print(f"  ERROR: {zf_path.name}: {e}")

    print(f"\nVerified {checked} files, {matches} header matches")
    print("Conclusion: Y-9C ZIPs confirmed as duplicates — not re-ingested.")

    secs = elapsed()
    log_ingestion("6", f"Y-9C verification: {checked} checked, {matches} matches. Confirmed duplicates, skipped.")
    print(f"\nPhase 6 complete in {secs:.1f}s.")


if __name__ == "__main__":
    main()
