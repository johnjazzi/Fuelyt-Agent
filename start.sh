#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create a virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip install --upgrade pip
pip install -r agent/requirements.txt

# Run the FastAPI application
uvicorn agent.main:app --reload --port 8000
