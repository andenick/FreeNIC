"""Shared utilities for freenic ingestion pipeline."""

import duckdb
import hashlib
import os
import time
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path("D:/Arcanum/Projects/freenic")
INPUTS_DIR = PROJECT_ROOT / "Inputs"
TECHNICAL_DIR = PROJECT_ROOT / "Technical"
OUTPUTS_DIR = PROJECT_ROOT / "Outputs"
DB_PATH = OUTPUTS_DIR / "freenic.duckdb"

# Canonical input paths (A4: centralized after folder rename)
INPUT_PATHS = {
    'mdrm': INPUTS_DIR / 'ffiec_bulk_bhcf' / 'MDRM_CSV.csv',
    'bhcf_txt': INPUTS_DIR / 'ffiec_bulk_bhcf',
    'bhcf_csv': INPUTS_DIR / 'bhcf_csv_pre2000',
    'attributes': INPUTS_DIR / 'nic_attributes',
    'call_reports': INPUTS_DIR / 'chicago_fed_call_reports',
    'crsp': INPUTS_DIR / 'crsp_frb_link',
    'luck': INPUTS_DIR / 'luck_database',
    'occ': INPUTS_DIR / 'luck_database' / 'occ_historical',
    'fdic_failures': INPUTS_DIR / 'fdic_failures_api.json',
    'fdic_financials': INPUTS_DIR / 'fdic_financials',
    'fdic_sod': INPUTS_DIR / 'fdic_sod',
    'dfast': INPUTS_DIR / 'dfast',
    'filing_instructions': INPUTS_DIR / 'filing_instructions',
}

INGESTION_DIR = TECHNICAL_DIR / "freenic_ingestion"
SCRIPTS_DIR = INGESTION_DIR / "scripts"
LOG_PATH = INGESTION_DIR / "INGESTION_LOG.md"

def get_db(read_only=False):
    """Get a DuckDB connection."""
    return duckdb.connect(str(DB_PATH), read_only=read_only)

def log_ingestion(phase, message):
    """Append a timestamped entry to the ingestion log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"| {ts} | Phase {phase} | {message} |\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

def init_log():
    """Initialize the ingestion log file."""
    if not LOG_PATH.exists():
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("# freenic Ingestion Log\n\n")
            f.write("| Timestamp | Phase | Message |\n")
            f.write("|---|---|---|\n")

def file_checksum(filepath, algorithm="sha256"):
    """Compute SHA-256 checksum of a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def file_size_mb(filepath):
    """Get file size in MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

def count_lines(filepath):
    """Count lines in a text file efficiently."""
    count = 0
    with open(filepath, "rb") as f:
        for _ in f:
            count += 1
    return count

def timer():
    """Simple context-manager-style timer. Returns a callable that gives elapsed seconds."""
    start = time.time()
    return lambda: time.time() - start

def print_table_stats(con, table_name, schema=None):
    """Print row count and column count for a table."""
    qualified = f"{schema}.{table_name}" if schema else table_name
    row_count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
    col_count = len(con.execute(f"SELECT * FROM {qualified} LIMIT 0").description)
    print(f"  {qualified}: {row_count:,} rows, {col_count} columns")
    return row_count
