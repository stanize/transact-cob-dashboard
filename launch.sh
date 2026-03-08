#!/bin/bash

# Dashboard directory
DASHBOARD_DIR="/mnt/temenos/T24/bnk/t24scripts/transact-cob-dashboard"

echo "--------------------------------------"
echo "Launching Transact COB Dashboard"
echo "--------------------------------------"

cd "$DASHBOARD_DIR" || exit 1

echo "Pulling latest version from GitHub..."
git pull

echo "Starting Streamlit dashboard..."
streamlit run app.py --server.port 8800

