FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml /app/
COPY src /app/src
RUN pip install --upgrade pip && \
    pip install -e .
COPY examples /app/examples
COPY catalog.yaml /app/catalog.yaml

ENTRYPOINT ["python", "-m", "agentic_datasets.cli"]