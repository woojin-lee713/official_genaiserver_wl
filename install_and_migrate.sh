#!/bin/bash

# Install dependencies using pixi
pixi install

# Check if Alembic is initialized, if not, initialize it
if [ ! -d "serverdatabase/migrations" ]; then
  pixi run alembic init serverdatabase/migrations
fi

# Run database migrations
pixi run alembic upgrade head || { echo "Alembic upgrade failed"; exit 1; }

echo "Install and migration completed successfully."
