# Self-Hosting FreeNIC Data

FreeNIC's code ships on GitHub; the **data** is hosted on ordinary infrastructure you control
(e.g. a personal mini PC) rather than on Zenodo/HF. The project already runs such a host at
**<https://data.freenic.org>**, which serves the published **v1.1.0** release (2026-07-15) — so
most readers need no setup at all. This guide is for running *your own* mirror, and for pointing
the Python/R/MCP readers at it.

> **Size and file counts — name the measure, never just the number.**
> The v1.1.0 release is **67 Parquet files, 13.9 GiB** (14,955,118,561 bytes). That decomposes as
> **61 files at the served root** — 60 base-table exports from `Outputs/parquet/*.parquet` plus the
> 163-year spine `long_bank_aggregates_1863_2026.parquet` — and a **6-file reconstruction layer**
> under `reconstruction/`. `SHA256SUMS.txt` carries **75** entries: those 67 Parquet plus 8
> reconstruction reports / gate JSONs — that is checksum coverage, not a file count.
> The frozen `release_manifest.json` (`file_count: 67`) is the arbiter; re-derive from it, never
> from a remembered number. Always co-host `PROVENANCE.csv` and `DATA_LICENSE.md`.
> The compact `freenic.duckdb` is **optional** and duplicates the Parquet content.

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
```
(The optional MCP server is part of the internal operational tree and is **not** shipped in this
repository; the Python and R readers above are the supported public entry points.)

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
enabled. That reader is **not implemented yet** — `set_data_dir` currently accepts a filesystem
path only — so for now prefer Option A for the package and Option B for ad-hoc DuckDB/SQL access.

## Option C — One-time download then local

Mirror the parquet dir to the client once (rsync/robocopy/`huggingface_hub`-style), then use Option A
against the local copy. Best when the client is offline or wants fastest repeated queries.

---

## Hardening / notes
- **Read-only.** Serve the data read-only; nothing in FreeNIC writes back to it.
- **Integrity.** Publish `SHA256SUMS.txt` next to the parquet so clients can verify
  (`certutil -hashfile` / `sha256sum`), and ship `release_manifest.json` beside it so a client can
  check the file count and byte total, not just individual hashes.
- **Bandwidth.** Enable HTTP range requests (nginx default) so DuckDB fetches only needed row groups.
- **Reachability.** A LAN hostname (`minipc.local`) or a static IP is enough; for WAN, put it behind a
  reverse proxy / tunnel you control. Record the final base URL in the README.
- **License travels with data.** Always co-host `PROVENANCE.csv` + `DATA_LICENSE.md` (NY Fed ToU for
  the Luck 1959–1975 slice; CC0 for the OCC historical layer; all else public regulatory).

---

## Reference host

The project's own host is already live and is the reference implementation of everything above:

| | |
|---|---|
| Base URL | `https://data.freenic.org` (read-only, byte-range, CORS) |
| Serves | the published **v1.1.0** release — 61 Parquet at the root, 6 under `reconstruction/` (**67** total, 13.9 GiB) |
| Integrity | `https://data.freenic.org/SHA256SUMS.txt` (75 entries — see the note at the top) |
| Manifest | `https://data.freenic.org/release_manifest.json` — the arbiter for `file_count` and per-file bytes |
| Provenance / licence | `PROVENANCE.csv` · `DATA_LICENSE.md`, co-hosted |

The compact `freenic.duckdb` is deliberately **not** hosted: DuckDB `httpfs` queries the Parquet
directly, so the single-file DB adds bandwidth and storage cost with no new capability.

A mirror is "done" when a clean install queries it successfully and its file count and byte total
reconcile to `release_manifest.json`. Assert those counts — a 200 response is not a check.
