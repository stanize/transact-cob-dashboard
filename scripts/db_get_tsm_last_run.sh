#!/bin/bash

result=$(psql -h T24-DB -U t24 -d BANCA -t -A -c \
"SELECT (xmlrecord::json)->>'3' AS field3
 FROM public.\"F_TSA_STATUS\"
 WHERE (xmlrecord::json)->>'2' = 'RUNNING'
   AND (xmlrecord::json)->>'5' = 'TSM'
 LIMIT 1;" | xargs)

if [ -z "$result" ]; then
    echo "N/A"
else
    echo "$result"
fi
