#!/bin/bash

# Initialize app
python3 seed.py

# Start server
echo "Starting server"
flask --app app/server run --host=0.0.0.0 -p 8000 --debug