"""Shared utilities for freenic ingestion pipeline."""

import duckdb
import hashlib
import os
import time
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INPUTS_DIR = PROJECT_ROOT / "Inputs"
TECHNICAL_DIR = PROJECT_ROOT / "Technical"
OUTPUTS_DIR = PROJECT_ROOT / "Outputs"
DB_PATH = OUTPUTS_DIR / "freenic.duckdb"

# DATA_ROOT: where the pipeline reads externally-sourced inputs that are not
# bundled under Inputs/ (e.g. the FFIEC CDR Public bulk ZIPs). Defaults to a
# repo-relative "data" dir. Override with the DATA_ROOT env var.
DATA_ROOT = Path(os.environ.get("DATA_ROOT", str(PROJECT_ROOT / "data")))
# OUTPUT_ROOT: where the pipeline writes derived feature panels (parquet). These
# panels are FreeNIC outputs consumed by downstream modeling work. Defaults to a
# repo-relative "outputs" dir. Override with the OUTPUT_ROOT env var.
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", str(PROJECT_ROOT / "outputs")))

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
    'occ_clv': INPUTS_DIR / 'clv_historical_call' / 'historical-call.dta',
    'fdic_failures': INPUTS_DIR / 'fdic_failures_api.json',
    'fdic_financials': INPUTS_DIR / 'fdic_financials',
    'fdic_sod': INPUTS_DIR / 'fdic_sod',
    'dfast': INPUTS_DIR / 'dfast',
    'filing_instructions': INPUTS_DIR / 'filing_instructions',
    # FFIEC CDR Public bulk Call Report ZIPs (acquired by 32_acquire_cdr_unrealized.py,
    # parsed by 33_parse_cdr_unrealized.py). Downloaded under DATA_ROOT.
    'cdr_raw': DATA_ROOT / 'cdr_raw',
    # WS2a: full FFIEC CDR Public bulk Call Reports -- Single Period ZIPs (2012Q1+)
    # acquired by 07d_acquire_cdr_call_bulk.py, ingested by 07e_ingest_call_reports_cdr.py.
    'cdr_call_bulk': INPUTS_DIR / 'cdr_call_bulk',
}

# Source descriptions for catalog.data_sources provenance (10_build_catalog.py
# materializes these; kept here so all source metadata lives in one place).
# fdic_sdi_features derives from already-crosswalked FDIC SDI variables;
# cdr_unrealized_losses derives from FFIEC CDR Public bulk (RCB/RC/RCE schedules).
SOURCE_DESCRIPTIONS = {
    'fdic_sdi_features': 'FDIC SDI-derived annual feature panel (1984-2025): asset ratios, '
                         'NIM/ROA, log_age, and F1/F3/F5 forward failure flags.',
    'cdr_unrealized_losses': 'FFIEC CDR Public bulk AFS/HTM fair-value, unrealized-loss, AOCI, '
                             'and brokered-deposit layer (2019Q4-2025Q4).',
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
