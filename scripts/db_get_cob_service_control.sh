#!/bin/bash

record=$(psql -h T24-DB -U t24 -d BANCA -t -A -c \
"SELECT (xmlrecord::json)->>'6'
 FROM public.\"F_TSA_SERVICE\"
 WHERE recid = 'COB'
 LIMIT 1;" | xargs)

if [ -z "$record" ]; then
    echo "N/A"
    exit 0
fi

echo "$record"
exit 0
