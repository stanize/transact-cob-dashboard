#!/bin/bash

JBOSS_HOME="/mnt/temenos/3rdParty/AS/jboss-eap-7.4"
DEPLOY_DIR="$JBOSS_HOME/standalone/deployments"

# 1. Check if JBoss process is running
JBOSS_PID=$(pgrep -f "jboss-modules")

if [ -z "$JBOSS_PID" ]; then
    echo "STOPPED"
    exit 1
fi

# 2. Check deployment folder
failed=$(ls $DEPLOY_DIR/*.failed 2>/dev/null | wc -l)
deploying=$(ls $DEPLOY_DIR/*.isdeploying 2>/dev/null | wc -l)
pending=$(ls $DEPLOY_DIR/*.dodeploy 2>/dev/null | wc -l)

if [ "$failed" -gt 0 ]; then
    echo "LOADING"
    exit 2
fi

if [ "$deploying" -gt 0 ] || [ "$pending" -gt 0 ]; then
    echo "LOADING"
    exit 2
fi

echo "RUNNING"
exit 0
