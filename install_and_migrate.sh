#!/bin/sh

# Install dependencies
pixi install || true

# Migrate the database
pixi migrate

# Re-run install to ensure all dependencies are in place
pixi install
