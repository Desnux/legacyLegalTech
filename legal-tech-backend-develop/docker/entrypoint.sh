#!/bin/bash

set -e

echo "$DB_HOST:$DB_PORT"

until pg_isready -h "$DB_HOST" -p "$DB_PORT"; do
  echo "Waiting for PostgreSQL..."
  sleep 5
done

if [[ "${MIGRATION_ENABLED}" == "true" ]]; then
  echo "Running migrations"
  alembic upgrade head
fi

if [[ "$(echo "${DEBUG_MODE}" | tr '[:upper:]' '[:lower:]')" == "true" ]]; then
  echo "Database is ready. Starting application in DEBUG mode..."
else
  echo "Database is ready. Starting application..."
fi

exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 4 \
    --threads 2 \
    --timeout 180 \
    --bind 0.0.0.0:8100
