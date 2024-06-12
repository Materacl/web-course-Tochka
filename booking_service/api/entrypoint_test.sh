#!/bin/sh

# Apply Alembic migrations
alembic upgrade head

# Run the tests
pytest --maxfail=1 --disable-warnings
