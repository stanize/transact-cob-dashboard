#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/db_check_jboss_status.sh"

echo "Restarting JBoss service..."

if ! sudo systemctl restart jboss; then
    echo "Failed to restart JBoss service"
    exit 1
fi

echo "Waiting for JBoss restart cycle to begin..."

restart_started=0
running_count=0

for i in {1..90}
do
    STATUS=$("$CHECK_SCRIPT")
    echo "Current status: $STATUS"

    if [[ "$STATUS" != "RUNNING" ]]; then
        restart_started=1
    fi

    if [[ "$restart_started" -eq 1 && "$STATUS" == "RUNNING" ]]; then
        running_count=$((running_count + 1))
    else
        running_count=0
    fi

    if [[ "$running_count" -ge 2 ]]; then
        echo "JBoss successfully restarted"
        exit 0
    fi

    sleep 5
done

echo "JBoss restart timeout"
exit 1
