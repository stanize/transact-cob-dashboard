#!/bin/bash

license_date=$(psql -h T24-DB -U t24 -d BANCA -t -A -c \
"SELECT (xmlrecord::json)->>'37'
 FROM public.\"F_SPF\"
 WHERE recid='SYSTEM';" | xargs)

if [ -z "$license_date" ]; then
    echo "N/A"
    exit 0
fi

license_epoch=$(date -d "$license_date" +%s 2>/dev/null)

if [ -z "$license_epoch" ]; then
    echo "ERROR"
    exit 0
fi

now=$(date +%s)

seconds_left=$((license_epoch - now))

if [ "$seconds_left" -lt 0 ]; then
    echo "EXPIRED"
    exit 0
fi

days_left=$((seconds_left / 86400))

months=$((days_left / 30))
days=$((days_left % 30))

if [ "$months" -gt 0 ]; then
    echo "$months month(s) $days day(s)"
else
    echo "$days day(s)"
fi
