"""Read-only state check before incremental ingest."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db

con = get_db(read_only=True)
print("=== call_report_filings ===")
r = con.execute("SELECT COUNT(*), MIN(period_end), MAX(period_end), COUNT(DISTINCT period_end) FROM call_report_filings").fetchone()
print(f"rows={r[0]:,}  min={r[1]}  max={r[2]}  quarters={r[3]}")
print("=== filing_metadata (CALL) source_files ===")
r2 = con.execute("SELECT COUNT(*) FROM filing_metadata WHERE filing_type='CALL'").fetchone()
print(f"CALL metadata rows={r2[0]}")
print("sample:", con.execute("SELECT source_file, period_end FROM filing_metadata WHERE filing_type='CALL' ORDER BY period_end DESC LIMIT 5").fetchall())
print("=== filing_metadata schema ===")
print(con.execute("DESCRIBE filing_metadata").fetchall())
con.close()
