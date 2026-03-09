#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/db_check_jboss_status.sh"

echo "Restarting JBoss service..."

if ! sudo systemctl restart jboss; then
    echo "Failed to restart JBoss service"
    exit 1
fi

echo "Waiting for JBoss to become fully available..."

for i in {1..60}
do
    STATUS=$("$CHECK_SCRIPT")

    if [[ "$STATUS" == "RUNNING" ]]; then
        echo "JBoss successfully restarted"
        exit 0
    fi

    sleep 5
done

echo "JBoss restart timeout"
exit 1
