#!/bin/sh

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI application with Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
