#!/bin/bash

set -e

# Si no viene PORT (por ejemplo, corriendo local), usa 8100 por defecto
PORT=${PORT:-8100}

echo "App port: $PORT"
echo "DB: ${DB_HOST:-<no DB_HOST>}:${DB_PORT:-<no DB_PORT>}"

# Si hay DB_HOST y DB_PORT, espera a que PostgreSQL esté listo
if [[ -n "$DB_HOST" && -n "$DB_PORT" ]]; then
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  until pg_isready -h "$DB_HOST" -p "$DB_PORT"; do
    echo "Waiting for PostgreSQL..."
    sleep 5
  done
else
  echo "DB_HOST o DB_PORT no definidos, saltando espera de PostgreSQL."
fi

# Migraciones opcionales
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
    --workers 1 \
    --threads 1 \
    --timeout 180 \
    --max-requests 100 \
    --max-requests-jitter 20 \
    --bind 0.0.0.0:"$PORT"

