#!/bin/bash
set -e

echo "Starting SymbioAI Backend..."

# Check if Python version is correct
python --version

# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}