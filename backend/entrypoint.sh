#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U postgres > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python -m app.seed

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
