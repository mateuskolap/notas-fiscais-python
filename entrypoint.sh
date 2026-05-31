#!/bin/sh
set -e

# Pula migrations e seeds quando executado como celery worker/beat
case "$1" in
  uv)
    case "$2" in
      run)
        case "$3" in
          celery)
            echo "Starting Celery process — skipping migrations and seeds."
            exec "$@"
            ;;
        esac
        ;;
    esac
    ;;
esac

echo "Running database migrations..."
uv run alembic upgrade head

echo "Running database seeders..."
uv run python -m src.services.seed_service

exec "$@"
