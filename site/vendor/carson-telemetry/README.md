# carson-telemetry

Shared, privacy-first **usage telemetry** for every Carson-hosted API / MCP / website.
Reference implementation of the **Carson Telemetry Standard v1.0**
(the Carson telemetry standard). This is the Layer-3 contract:
every hosted endpoint emits exactly one `usage_events` row per invocation into a
single SQLite DB.

> No service ships on the Carson box without Layer-3 telemetry. This is a deploy gate.

## What it gives you

- **Per-MCP-tool / per-endpoint / per-download counts** the edge (Caddy/GoAccess) can't see inside.
- **Privacy by construction:** client identity is a *daily-salted, truncated SHA-256 hash* of the IP — **no raw IP, no PII, no cookies** (§6). Unlinkable across days.
- **Zero daemon storage:** one WAL-mode SQLite file (`/var/lib/carson/telemetry.db`).
- A read-only **dashboard** (Tailscale-only), a **rollup** (raw → `usage_daily`, 400-day retention), and a local **ingest sidecar** (HTTP + JSONL) for non-Python services.

Core library is **stdlib-only** (`sqlite3`, `hashlib`, `http.server`, `json`, `datetime`).
FastAPI/MCP integration are optional extras.

## Install

```bash
pip install carson-telemetry                 # core: middleware, MCP wrap, ingest, rollup (stdlib only)
pip install 'carson-telemetry[fastapi]'      # + the read-only dashboard / FastAPI apps
pip install 'carson-telemetry[mcp]'          # + FastMCP
```

## The 2-line integration (TELEMETRY_STANDARD §4)

```python
from carson_telemetry import telemetry          # shared module, vendored or pip-installed

# FastAPI / Starlette
app.add_middleware(telemetry.ASGIMiddleware, service="gerhard")     # auto-emits rest/download events

# FastMCP — wrap tool registration so every tool call is recorded
mcp = telemetry.instrument_mcp(mcp, service="methodex")             # auto-emits surface="mcp", endpoint=<tool>
```

That's it. The middleware records `surface` (`download` for `/download` & `/api/download`,
else `rest`), `endpoint` (route template, not argument values), `status`, `latency_ms`,
`bytes`, and a hashed client id from `X-Forwarded-For`/peer. `instrument_mcp` wraps the
FastMCP `tool` decorator so each tool call emits `surface="mcp"`, `endpoint=<tool name>`.

**Downloads / non-Python services:**

```python
from carson_telemetry import telemetry
telemetry.record_download("methodex", "/download/bundle.zip", bytes=10_485_760, status="ok")
```
or POST the event JSON to `http://127.0.0.1:9100/ingest`, or write JSONL to
`$CARSON_TELEMETRY_INGEST_DIR/*.jsonl` (the ingest sidecar tails it).

## Configuration (env vars)

| Var | Default | Purpose |
|---|---|---|
| `CARSON_TELEMETRY_DB` | `/var/lib/carson/telemetry.db` (temp fallback on Windows/non-writable) | SQLite path |
| `CARSON_TELEMETRY_SALT_DIR` | `/var/lib/carson/salt` (temp fallback) | per-day salt files |
| `CARSON_TELEMETRY_INGEST_DIR` | _(unset)_ | dir of `*.jsonl` the ingest sidecar tails |

## Console scripts

```bash
carson-telemetry-ingest      # local sidecar: POST /ingest on 127.0.0.1:9100 + JSONL tailer
carson-telemetry-dash        # read-only dashboard (TAILSCALE-ONLY — refuses 0.0.0.0)
carson-telemetry-rollup      # aggregate raw -> usage_daily, prune raw > 400 days (idempotent)
```

Run the rollup nightly (systemd timer / cron). Bind the dashboard to the box's
**Tailscale IP** (`100.x.y.z`), never a public address — it is an admin surface.

## The event contract (§3)

| Field | Type | Notes |
|---|---|---|
| `ts` | str | ISO-8601 UTC `…Z` |
| `service` | str | registry name |
| `surface` | str | `mcp` \| `rest` \| `web` \| `download` |
| `endpoint` | str | tool name / route / file path — **names only, never argument values** |
| `client_id` | str | `sha256(client_ip + daily_salt)[:16]` — **no raw IP ever** |
| `status` | str | `ok` \| `error` \| HTTP code |
| `latency_ms` | int | server-side duration |
| `bytes` | int | response size (0 if n/a) |
| `meta` | json | small, PII-free (identifiers/keys, not free text), cap 1 KB |

Stored in SQLite `usage_events`, WAL, indexed `(service, ts)` and `(service, endpoint)`.

## Edge & web layers (convenience; Layer 3 is the contract)

- `configs/goaccess.conf` — GoAccess parser for Caddy JSON access logs (Layer 1).
- `configs/umami.compose.yml` — Umami (pinned) for cookieless web analytics (Layer 2),
  with a lighter **GoatCounter** (single Go binary + SQLite) alternative documented inline.

## Privacy posture (non-negotiable, §6)

- No raw IPs, no PII. Client id is a daily-salted truncated hash only.
- `meta` carries identifiers, not user free-text — `sanitize_meta` drops banned keys
  (ip/email/query/prompt/…) and long free-text values, and enforces the 1 KB cap.
- Dashboards are private (Tailscale).

## Tests

```bash
python -m pytest -q
```

Covers DB roundtrip, hash stability/rotation, the ASGI middleware, `instrument_mcp`,
the ingest HTTP + JSONL paths, the rollup (aggregate + prune), and an explicit
assertion that **no raw IP is ever stored**. Optional-extra paths (FastAPI/MCP) skip
cleanly when those packages aren't installed.
