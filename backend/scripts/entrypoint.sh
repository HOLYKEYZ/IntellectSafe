#!/bin/bash
set -e

# Wait for database
echo "Waiting for postgres..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 2
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Initialize RAG system (if needed)
echo "Initializing RAG system..."
python init_rag.py

# Start application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
