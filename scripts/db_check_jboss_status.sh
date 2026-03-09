#!/bin/bash

JBOSS_HOME="/mnt/temenos/3rdParty/AS/jboss-eap-7.4"
DEPLOY_DIR="$JBOSS_HOME/standalone/deployments"

JBOSS_PID=$(pgrep -f "jboss-modules")

if [ -z "$JBOSS_PID" ]; then
    echo "STOPPED"
    exit 0
fi

failed=$(find "$DEPLOY_DIR" -maxdepth 1 -name "*.failed" | wc -l)
deploying=$(find "$DEPLOY_DIR" -maxdepth 1 -name "*.isdeploying" | wc -l)
pending=$(find "$DEPLOY_DIR" -maxdepth 1 -name "*.dodeploy" | wc -l)

if [ "$failed" -gt 0 ]; then
    echo "ERROR"
    exit 0
fi

if [ "$deploying" -gt 0 ] || [ "$pending" -gt 0 ]; then
    echo "LOADING"
    exit 0
fi

echo "RUNNING"
exit 0
