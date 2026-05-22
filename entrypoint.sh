#!/bin/sh
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Running database seeders..."
uv run python -m src.services.seed_service

exec "$@"
