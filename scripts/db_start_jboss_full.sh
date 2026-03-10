#!/bin/bash

JBOSS_HOME="/mnt/temenos/3rdParty/AS/jboss-eap-7.4"
DEPLOY_DIR="$JBOSS_HOME/standalone/deployments"

TIMEOUT=1200
INTERVAL=5
ELAPSED=0

echo "[STAGE] Starting JBoss"

/bin/sudo /bin/systemctl start jboss
RC=$?

if [ $RC -ne 0 ]; then
    echo "[ERROR] Failed to start JBoss (exit code=$RC)"
    exit 1
fi

echo "[STAGE] Waiting for JBoss deployments to complete"

sleep 60

while true; do
    failed_files=$(find "$DEPLOY_DIR" -maxdepth 1 -name "*.failed")

    if [ -n "$failed_files" ]; then
        echo "[ERROR] Deployment failed:"
        echo "$failed_files"
        exit 1
    fi

    deploying_files=$(find "$DEPLOY_DIR" -maxdepth 1 -name "*.isdeploying")

    if [ -z "$deploying_files" ]; then
        echo "[DONE] All JBoss deployments completed"
        exit 0
    fi

    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "[ERROR] Deployment timeout after $TIMEOUT seconds"
        exit 2
    fi

    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done
