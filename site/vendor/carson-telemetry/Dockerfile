# carson-telemetry — single image serving all three console scripts:
#   carson-telemetry-ingest   (local ingest sidecar; stdlib only)
#   carson-telemetry-dash     (read-only FastAPI dashboard; needs the [fastapi] extra)
#   carson-telemetry-rollup   (nightly raw -> usage_daily aggregation; stdlib only)
#
# The dashboard pulls in the [fastapi] extra (fastapi/starlette/uvicorn/jinja2),
# so we install that extra here; the same image runs ingest + rollup unchanged.
#
# Image is PINNED (digest-pinnable in prod). curl is added for the healthchecks.
# Built against the package in this build context (PublicRepos/carson-telemetry).
FROM python:3.12.7-slim-bookworm

# Run as an unprivileged user; /var/lib/carson is the shared telemetry volume.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CARSON_TELEMETRY_DB=/var/lib/carson/telemetry.db \
    CARSON_TELEMETRY_SALT_DIR=/var/lib/carson/salt

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 carson \
    && mkdir -p /var/lib/carson \
    && chown -R carson:carson /var/lib/carson

WORKDIR /app
COPY . /app
# Install the package with the FastAPI extra (dashboard). pip resolves the
# pinned ranges in pyproject.toml.
RUN pip install --no-cache-dir '.[fastapi]'

USER carson

# Default to the ingest sidecar; compose overrides `command:` per service.
# NOTE: the dashboard refuses to bind 0.0.0.0 without an explicit flag — it is a
# Tailscale-only admin surface (see compose + TELEMETRY_STANDARD.md §5/§6).
ENTRYPOINT []
CMD ["carson-telemetry-ingest", "--host", "0.0.0.0", "--port", "9100"]
