#!/bin/bash

set -e

echo "--------------------------------------"
echo "Launching Transact COB Dashboard"
echo "--------------------------------------"

echo "Pulling latest version from GitHub..."
git fetch origin
git reset --hard origin/main

echo "Starting Streamlit dashboard..."
streamlit run app.py --server.port 8800 --server.address 0.0.0.0
