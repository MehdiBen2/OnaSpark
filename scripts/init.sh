#!/bin/bash

# Run database migrations
python -m flask db upgrade

# Start the application
python wsgi.py
