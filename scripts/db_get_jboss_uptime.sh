#!/bin/bash

SERVICE_STATUS=$(systemctl is-active jboss 2>/dev/null)

if [ "$SERVICE_STATUS" != "active" ]; then
    echo "N/A"
    exit 0
fi

START_TIME=$(systemctl show jboss --property=ActiveEnterTimestamp --value 2>/dev/null | xargs)

if [ -z "$START_TIME" ]; then
    echo "N/A"
    exit 0
fi

START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null)
NOW_EPOCH=$(date +%s)

if [ -z "$START_EPOCH" ]; then
    echo "N/A"
    exit 0
fi

DIFF=$((NOW_EPOCH - START_EPOCH))

DAYS=$((DIFF / 86400))
HOURS=$(((DIFF % 86400) / 3600))
MINS=$(((DIFF % 3600) / 60))

if [ "$DAYS" -gt 0 ]; then
    echo "${DAYS}d ${HOURS}h ${MINS}m"
elif [ "$HOURS" -gt 0 ]; then
    echo "${HOURS}h ${MINS}m"
else
    echo "${MINS}m"
fi
