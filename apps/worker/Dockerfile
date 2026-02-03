FROM python:3.12-slim

WORKDIR /app/apps/worker

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
  && pip install --no-cache-dir uv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY apps/worker/pyproject.toml /app/apps/worker/pyproject.toml
COPY apps/worker/src /app/apps/worker/src
COPY apps/api /app/apps/api

RUN uv pip install --system -e /app/apps/api \
  && uv pip install --system -e /app/apps/worker

CMD ["python", "-m", "eventcart_worker.main"]
