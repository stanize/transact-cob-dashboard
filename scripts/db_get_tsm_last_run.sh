#!/bin/bash

record=$(psql -h T24-DB -U t24 -d BANCA -t -A -c \
"SELECT (xmlrecord::json)->>'7'
 FROM public.\"F_TSA_STATUS\"
 WHERE (xmlrecord::json)->>'5' = 'TSM'
 LIMIT 1;" | xargs)

if [ -z "$record" ]; then
    echo "N/A"
    exit 0
fi

datetime=$(echo "$record" | sed -E 's/^_*[0-9]+_([0-9]{2} [A-Z]{3} [0-9]{4})_([0-9]{2}:[0-9]{2}:[0-9]{2}):[0-9]{3}.*/\1 \2/')

last_run=$(date -d "$datetime" +%s 2>/dev/null)

if [ -z "$last_run" ]; then
    echo "ERROR"
    exit 0
fi

now=$(date +%s)
delta=$((now - last_run))

hours=$((delta / 3600))
minutes=$(((delta % 3600) / 60))
seconds=$((delta % 60))

if [ "$hours" -gt 0 ]; then
    echo "$hours hour(s) $minutes minute(s) $seconds second(s) ago"
elif [ "$minutes" -gt 0 ]; then
    echo "$minutes minute(s) $seconds second(s) ago"
else
    echo "$seconds second(s) ago"
fi
