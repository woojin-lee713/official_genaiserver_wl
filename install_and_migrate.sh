#!/bin/sh

# Install dependencies
pip install -r requirements.txt

# Migrate the database
alembic upgrade head
