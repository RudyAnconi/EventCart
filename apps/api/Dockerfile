FROM python:3.12-slim

WORKDIR /app/apps/api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
  && pip install --no-cache-dir uv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY apps/api/pyproject.toml /app/apps/api/pyproject.toml
COPY apps/api/src /app/apps/api/src
COPY apps/api/alembic /app/apps/api/alembic
COPY apps/api/alembic.ini /app/apps/api/alembic.ini
COPY apps/api/scripts /app/apps/api/scripts

RUN uv pip install --system -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "eventcart.main:app", "--host", "0.0.0.0", "--port", "8000"]
