# FreeNIC — public DRAFT data explorer. FastAPI + DuckDB + Plotly, stock stack.
# Ships only a ~5 MB curated real slice (app/data/freenic_slice.duckdb), never the full DB/Parquet.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Deps: carson-telemetry is VENDORED (not on PyPI). Install everything else from the
# pinned requirements, then pip-install the local vendored package. Mirrors leontief.
COPY app/requirements.txt /app/requirements.txt
COPY vendor /app/vendor
RUN grep -v '^carson-telemetry' /app/requirements.txt > /tmp/req.txt && \
    pip install --no-cache-dir -r /tmp/req.txt && \
    pip install --no-cache-dir "/app/vendor/carson-telemetry[fastapi]"

COPY app /app/app

EXPOSE 8080
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", "-w", "2", \
     "-b", "0.0.0.0:8080", "--timeout", "120"]
