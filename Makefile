.PHONY: dev build up down logs fmt lint test api-test web-test seed

build:
	docker compose build

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

seed:
	docker compose run --rm api uv run python /app/apps/api/scripts/seed.py

fmt:
	docker compose run --rm api uv run ruff format /app/apps/api

lint:
	docker compose run --rm api uv run ruff check /app/apps/api

api-test:
	docker compose run --rm api uv run pytest -q /app/apps/api/tests

web-test:
	docker compose run --rm web npm test

