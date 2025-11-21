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

echo "Database is ready. Starting application..."

uvicorn main:app --host 0.0.0.0 --port 8100 --log-level debug
