# FreeNIC — Data Serving Plan (`data.freenic.org`)

**Date:** 2026-07-14 (counts regenerated from the live served dir) · **Status:** LIVE
**Scope:** serve the full FreeNIC v1.0 parquet release read-only with HTTP byte-range + CORS so
DuckDB `httpfs` clients can query it remotely.

> **Single source of truth.** The counts below are the TRUTH of the live served dir
> (`~/freenic-data` on the box), regenerated in the CDF pass. The site's `/data` catalog,
> the homepage copy, and every triad sublabel render from the same generated manifest
> (`app/data/freenic_counts.json` + `release_manifest.json`, produced by
> `make_freenic_counts.py`). Keep `DATA_SERVING.md`, `SHA256SUMS.txt`, the served dir, and
> `manifest.json` at the SAME count in one atomic pass — the FN-3 drift lesson.

---

## 1. What gets served

The full **v1.0 parquet release** from the FreeNIC warehouse `Outputs/parquet/` export dir plus
the replicated 163-year spine `long_bank_aggregates_1863_2026.parquet` (from `Outputs/`).

| | |
|---|---|
| Parquet files | **61** (`*.parquet`) |
| Total size | **13.2 GiB** (14,133,652,322 bytes ≈ 14.1 GB decimal) |
| Integrity | `SHA256SUMS.txt` (covers all 61 files) |
| Provenance | `PROVENANCE.csv` (per-table tier/era/provider/citation) |
| License | `DATA_LICENSE.md` (MIT code; CC0 finhist layer; NY-Fed-ToU Luck slice; rest public) |
| Discovery | `manifest.json` + `llms.txt` at the served root (agent/LLM discovery — DFN-7) |

> **The 60→61 decision (DFN-5).** The 60 files in `Outputs/parquet/` are the base release;
> the source `SHA256SUMS.txt` carried a 61st entry, `long_bank_aggregates_1863_2026.parquet`
> (the 163-year replicated bank-aggregate spine, ~11 KB), which was NOT previously served.
> It is now **served** (copied into the served dir) because it is the spine the /explorer
> flagship chart is built on — publishing it makes the featured series directly downloadable.
> The served dir, `SHA256SUMS.txt`, `manifest.json`, and this doc all agree at **61**.

**Includes the finhist / OCC historical CC0 layer** as `occ_historical.parquet` (report_date
min/max **1863–1941**, public domain; the companion `occ_historical_clv.parquet` is the same
1863–1941 span) — hosting the release hosts the finhist data.

### Host `freenic.duckdb` too?
**No — parquet is enough** (per the request: "parquet is enough"). The compact `freenic.duckdb` is
~13.8 GB (the on-disk file is currently ~29.6 GB pre-vacuum) and duplicates the parquet content.
DuckDB `httpfs` queries the parquet files directly, so the single-file DB adds bandwidth/storage cost
with no new capability for remote users. **Optional later:** if a "one-file local copy" path is
wanted, publish a vacuumed `freenic.duckdb` as an additional download — but it is explicitly out of
scope for launch.

---

## 2. Serving design — Caddy, read-only, byte-range, CORS

A single stock `caddy:2-alpine` container (`freenic-data`) bind-mounts the parquet dir read-only and
serves it with `file_server`. Caddy's `file_server` honours `Range` headers natively (emits
`Accept-Ranges: bytes` + `206 Partial Content`), which is exactly what DuckDB `httpfs` needs to fetch
only the row-groups a query touches — no full-file download.

Files in this directory:

| File | Purpose |
|---|---|
| `data-serving/Caddyfile` | `file_server` + range + `Access-Control-Allow-Origin *` + CORS preflight + `application/octet-stream` for `.parquet` + `Permissions-Policy` deny + `browse` index |
| `data-serving/docker-compose.data.yml` | the `freenic-data` service (compose addition) |

**Key Caddyfile behaviours** (see file for the full config):
- `file_server { browse }` — native range requests + a human-readable directory index.
- `Access-Control-Allow-Origin "*"` + `Allow-Methods GET, HEAD, OPTIONS` + `Allow-Headers Range` +
  `Expose-Headers Content-Range, Accept-Ranges` — browser DuckDB-Wasm / `fetch` clients work
  cross-origin, including the 206 range responses.
- `OPTIONS → 204` so CORS preflight is answered directly.
- `.parquet → Content-Type application/octet-stream`; `.txt/.csv/.md → text/plain` so
  `SHA256SUMS.txt` / `PROVENANCE.csv` / `DATA_LICENSE.md` read in a browser.
- `Permissions-Policy "geolocation=(), microphone=(), camera=(), browsing-topics=()"` deny header +
  `X-Content-Type-Options nosniff`.
- TLS is terminated **upstream** (Cloudflare Tunnel / NPM), same as `freenic-web`; Caddy listens on
  `:80` inside the container, no host ports.

### Intended route
```
data.freenic.org  ->  freenic-data:80     (Cloudflare Tunnel public hostname / NPM proxy host)
freenic.org       ->  freenic-web:8080    (existing; the web app)
```
Both services sit on the external `homelab_default` network. Add the public hostname
`data.freenic.org → http://freenic-data:80` in the tunnel/NPM config when DNS is pointed.

---

## 3. Box-side deploy steps (operator)

> Run on the mini PC. The parquet release is **not** in the repo (gitignored, size) — it ships via
> rsync/scp from the build host, not through git.

**a. Stage the release directory on the host.**
> **Note:** if the host has no passwordless sudo for `/srv`, the release can live at
> **`~/freenic-data`** instead of `/srv/freenic-data`; `docker-compose.data.yml` binds that
> path. The steps below show the `/srv` layout for reference — substitute `~/freenic-data`
> throughout if using a home-directory path.
```bash
mkdir -p ~/freenic-data   # (original plan: sudo mkdir -p /srv/freenic-data + chown)
```

**b. rsync the ~13 GB release from the build host** (`D:\Arcanum\Projects\freenic\Outputs\`).
From a shell that can reach both (adjust host/paths):
```bash
# parquet payload (~13 GB)
rsync -avh --progress \
  /mnt/d/Arcanum/Projects/freenic/Outputs/parquet/*.parquet \
  user@minipc:/srv/freenic-data/

# integrity + provenance + license (co-host alongside the data)
rsync -avh \
  /mnt/d/Arcanum/Projects/freenic/Outputs/SHA256SUMS.txt \
  /mnt/d/Arcanum/Projects/freenic/Outputs/PROVENANCE.csv \
  /mnt/d/Arcanum/Projects/freenic/DATA_LICENSE.md \
  user@minipc:/srv/freenic-data/
```
Windows alternative (PowerShell, from the build host): `scp` the same files, or `robocopy` to a share
the box mounts. Either way the box ends up with `/srv/freenic-data/*.parquet` + the three meta files.

**c. Verify integrity on the box** (must be clean before going live):
```bash
cd /srv/freenic-data
sha256sum -c SHA256SUMS.txt        # expect: every file "OK"
ls *.parquet | wc -l               # expect: 61
```

**d. Bring up the data service** (from the `site/` directory):
```bash
docker compose \
  -f docker-compose.yml \
  -f data-serving/docker-compose.data.yml \
  up -d freenic-data
```

**e. Smoke-test byte-range + httpfs** (from any client once the route is live):
```bash
# range support present?
curl -sI -H "Range: bytes=0-99" https://data.freenic.org/bank_failures.parquet | grep -i "206\|content-range\|accept-ranges"

# DuckDB queries it in place
python - <<'PY'
import duckdb
c = duckdb.connect(); c.execute("INSTALL httpfs; LOAD httpfs;")
print(c.execute("SELECT COUNT(*) FROM 'https://data.freenic.org/occ_historical.parquet'").fetchone())
PY
```

---

## 4. Hand-back to the freeNIC project owner

Once `data.freenic.org` resolves and the smoke test passes, the base URL is:
```
https://data.freenic.org
```
The freeNIC owner then wires that into FreeNIC's `README.md` + `QUICK_START.md` and re-runs the
self-host smoke test (`SELF_HOSTING.md` R-step).

---

## 5. Operational notes
- **Read-only.** The bind mount is `:ro`; nothing writes back to the data.
- **Bandwidth.** Range requests mean a typical analytical query transfers MBs, not GBs — the 13 GB
  is the catalog ceiling, not the per-query cost.
- **Updates.** A new release = re-rsync the changed parquet + the regenerated `SHA256SUMS.txt`, then
  `sha256sum -c`. No container rebuild needed (stock Caddy image).
- **`browse` index** lets humans (and crawlers) see the file list at `https://data.freenic.org/`;
  the site's `/data` page is the curated, provenance-annotated catalog over the same files.

---

## 6. Telemetry — Layer-3 + local `/__track` 204 sink

FreeNIC runs the `carson_telemetry` ASGI middleware (`main.py`, `service="freenic"`), so **every**
request is recorded as a Layer-3 `usage_events` row (per `standards/TELEMETRY_STANDARD.md §4`). The
shared chrome (`base.html`, `action-footer.html`) sets `window.ARK_TRACK.endpoint = "/__track"`, and
`ark-triad.js` fires a same-origin beacon on each Research-Triad (Data/Code/Outputs) click.

Previously there was **no `/__track` route**, so those triad beacons 404'd (no-op). Fix (2026-07-14):
a local **`POST /__track`** route that drains the advisory body and returns **`204`** (see
`app/main.py::track_beacon`). The middleware captures the beacon as a normal L3 event; the client gets
a clean 204. This mirrors the sibling FastAPI site `deploy/shaikh`. We chose the **same-origin 204
sink** over repointing `ark-track` at the hub Layer-2 collector because freenic has a backend that
already ingests L3 events — the sink keeps telemetry same-origin with no cross-origin/CORS dependency.
No cookies, no PII; honors DNT/GPC (the kit `ark-track.js`/`ark-triad.js` bail on Do-Not-Track).
