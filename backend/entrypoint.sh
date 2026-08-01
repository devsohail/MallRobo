#!/bin/bash
set -e

# Convert postgresql:// to postgresql+asyncpg:// for SQLAlchemy async driver
if [ -n "$DATABASE_URL" ]; then
  export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"

  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p')
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
  echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
  until pg_isready -h "${DB_HOST}" -p "${DB_PORT:-5432}" > /dev/null 2>&1; do
    sleep 1
  done
  echo "PostgreSQL is ready."
fi

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python -m app.seed

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
