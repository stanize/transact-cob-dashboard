#!/bin/bash

set -e

echo "--------------------------------------"
echo "Launching Transact COB Dashboard"
echo "--------------------------------------"

echo "Pulling latest version from GitHub..."
git fetch origin
git reset --hard origin/main

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Streamlit dashboard..."
streamlit run app.py --server.port 8800
