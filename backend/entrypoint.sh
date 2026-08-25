#!/bin/sh
set -e

echo "=== [Lenny Assistant Backend] Initializing Services ==="

# Execute database migrations if Alembic is configured
if [ -f "alembic.ini" ]; then
    echo "Running Alembic database migrations..."
    alembic upgrade head || echo "Migration skipped or already up to date."
fi

echo "Starting FastAPI Production Uvicorn Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
