#!/bin/bash

START_TIME=$(systemctl show jboss --property=ActiveEnterTimestamp --value | xargs)

if [ -z "$START_TIME" ]; then
    echo "N/A"
    exit 0
fi

date -d "$START_TIME" "+%Y-%m-%d %H:%M:%S"
