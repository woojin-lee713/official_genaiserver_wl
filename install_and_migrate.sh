#!/bin/sh

# Install dependencies
pixi sync

# Migrate the database
pixi migrate

# Re-run install to ensure all dependencies are in place
pixi sync
