"""Shared bootstrap for the FreeNIC Anu replication drivers.

Sets the pipeline environment so every canonical phase script (pipeline/scripts/)
writes inside this anu/ package, and provides run_phase() to invoke them.

Relative paths only — no absolute host locations anywhere in this package.

Environment (all optional; defaults point inside anu/data/):
  FREENIC_INPUTS    raw acquisition cache   (default: <repo>/anu/data/raw)
  FREENIC_OUTPUTS   warehouse export dir    (default: <repo>/anu/data/outputs)
  FREENIC_WAREHOUSE warehouse DuckDB file   (default: <repo>/anu/data/outputs/freenic.duckdb)
  FRED_API_KEY      free FRED API key (https://fred.stlouisfed.org/docs/api/api_key.html)
                    needed only for the full disaggregated H.8 release (phase 27b)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# anu/scripts/_bootstrap.py -> anu/ -> <repo root>
REPO_ROOT = Path(__file__).resolve().parents[2]
ANU_DIR = REPO_ROOT / "anu"
PHASE_DIR = REPO_ROOT / "pipeline" / "scripts"

RAW_DIR = Path(os.environ.get("FREENIC_INPUTS", ANU_DIR / "data" / "raw"))
OUT_DIR = Path(os.environ.get("FREENIC_OUTPUTS", ANU_DIR / "data" / "outputs"))
WAREHOUSE = Path(os.environ.get("FREENIC_WAREHOUSE", OUT_DIR / "freenic.duckdb"))


def pipeline_env() -> dict[str, str]:
    """Environment for canonical phase scripts, rooted inside anu/data/."""
    env = os.environ.copy()
    env.setdefault("FREENIC_INPUTS", str(RAW_DIR))
    env.setdefault("FREENIC_OUTPUTS", str(OUT_DIR))
    env.setdefault("FREENIC_WAREHOUSE", str(WAREHOUSE))
    return env


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_phase(script: str, *args: str, check: bool = True) -> int:
    """Run a canonical pipeline phase script (e.g. '16_ingest_fdic_failures.py').

    The pipeline (pipeline/scripts/) is the construction method of record; the
    anu/ layer organizes, documents, and validates it. This helper just invokes
    the canonical phase scripts with the anu-rooted environment.
    """
    target = PHASE_DIR / script
    if not target.exists():
        print(f"[anu] pipeline phase not found: pipeline/scripts/{script}", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(target), *args]
    print(f"[anu] {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(PHASE_DIR), env=pipeline_env())
    if check and proc.returncode != 0:
        print(f"[anu] phase {script} FAILED (exit {proc.returncode})", file=sys.stderr)
    return proc.returncode


def require_input(relpath: str, source_url: str, note: str = "") -> Path:
    """Honest input gate: no silent fallbacks.

    Bulk historical products that have no keyless public bulk download are
    documented, not fabricated. If the file is missing we point at the exact
    public source and exit non-zero.
    """
    path = RAW_DIR / relpath
    if not path.exists():
        print(
            f"[anu] MISSING INPUT: {relpath}\n"
            f"       Get it from: {source_url}\n"
            f"       Place it at:  anu/data/raw/{relpath}\n"
            + (f"       Note: {note}\n" if note else ""),
            file=sys.stderr,
        )
        raise SystemExit(1)
    return path
