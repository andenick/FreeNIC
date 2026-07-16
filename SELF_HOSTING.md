# Self-Hosting FreeNIC Data

FreeNIC's code ships on GitHub; the **data** (~6 GB Parquet, optional compact DuckDB) is hosted
**by you** (e.g. a personal mini PC) rather than on Zenodo/HF. This guide covers serving it and
pointing the Python/R/MCP readers at it.

> Data files to host: everything in `Outputs/parquet/*.parquet` (the 37 tables), plus optionally the
> compact `freenic.duckdb`. Always ship `Outputs/PROVENANCE.csv` and `DATA_LICENSE.md` alongside.

---

## Option A — Local / LAN mount (simplest)

Put the parquet dir on the mini PC and expose it as a folder (SMB/NFS share, synced folder, or just a
local path on the same machine). Then point the package at it — **no code change needed**, the reader
is already configurable:

```python
import freenic
freenic.set_data_dir(r"\\MINIPC\freenic\parquet")   # or a local/mounted path
# or set once in the environment:  FREENIC_DATA_DIR=/mnt/freenic/parquet
freenic.list_tables()
```
```r
library(freenic); freenic_set_data_dir("/mnt/freenic/parquet")
```
```bash
export FREENIC_DATA_DIR=/mnt/freenic/parquet
python Technical/freenic_mcp/server.py
```

## Option B — Serve over HTTP from the mini PC

On the mini PC, serve the parquet directory:

```bash
# quick/dev:
cd /path/to/Outputs && python -m http.server 8080
# durable: put nginx in front of /path/to/Outputs/parquet (enable range requests = default)
```

DuckDB reads Parquet directly over HTTP(S) (httpfs), so clients can query without downloading whole
files:

```python
import duckdb
con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs;")
BASE = "http://minipc.local:8080/parquet"
con.execute(f"SELECT COUNT(*) FROM read_parquet('{BASE}/institutions.parquet')").fetchone()
```

For the `freenic` package over HTTP, either (a) mount the share (Option A), or (b) use the helper
`freenic.set_data_dir("http://minipc.local:8080/parquet")` once the optional remote-URL reader is
enabled (planned in R3 — it wraps `read_parquet` over httpfs). Until then, prefer Option A for the
package and Option B for ad-hoc DuckDB/SQL access.

## Option C — One-time download then local

Mirror the parquet dir to the client once (rsync/robocopy/`huggingface_hub`-style), then use Option A
against the local copy. Best when the client is offline or wants fastest repeated queries.

---

## Hardening / notes
- **Read-only.** Serve the data read-only; nothing in FreeNIC writes back to it.
- **Integrity.** Publish a `SHA256SUMS` next to the parquet so clients can verify
  (`certutil -hashfile` / `sha256sum`). Generate after the final export.
- **Bandwidth.** Enable HTTP range requests (nginx default) so DuckDB fetches only needed row groups.
- **Reachability.** A LAN hostname (`minipc.local`) or a static IP is enough; for WAN, put it behind a
  reverse proxy / tunnel you control. Record the final base URL in README + `QUICK_START.md`.
- **License travels with data.** Always co-host `PROVENANCE.csv` + `DATA_LICENSE.md` (NY Fed ToU for
  the Luck 1959–1975 slice; CC0 for the OCC historical layer; all else public regulatory).

---

## What FreeNIC needs from you to finalize the release (R-step)
1. The mini PC's reachable **base path or URL** for the parquet dir.
2. Whether to also host the compact `freenic.duckdb`.
Once provided, the exact endpoint is wired into README + QUICK_START and a post-release smoke test
(clean install → query against your host) confirms it.
