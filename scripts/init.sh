#!/bin/bash

# Initialize the database
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Run database migrations
flask db upgrade

# Start the application
python wsgi.py
