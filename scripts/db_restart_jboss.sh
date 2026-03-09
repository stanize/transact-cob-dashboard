#!/bin/bash

# Resolve the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JBOSS_HOME=/opt/jboss-eap-7.4
CHECK_SCRIPT="$SCRIPT_DIR/db_check_jboss_status.sh"

echo "Stopping JBoss..."

$JBOSS_HOME/bin/jboss-cli.sh --connect command=:shutdown

sleep 5

echo "Starting JBoss..."

nohup $JBOSS_HOME/bin/standalone.sh > /tmp/jboss_start.log 2>&1 &

echo "Waiting for deployments..."

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
