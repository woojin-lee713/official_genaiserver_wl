#!/bin/bash

# Install dependencies
pixi install

# Initialize and run migrations
pixi run init
pixi run migrate

# Any additional commands if needed
