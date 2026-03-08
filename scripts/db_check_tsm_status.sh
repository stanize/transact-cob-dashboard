#!/bin/bash

STATUS=$(psql -h T24-DB -U t24 -d BANCA -t -A -c \
"SELECT COALESCE((xmlrecord::json)->>'6','')
 FROM public.\"F_TSA_SERVICE\"
 WHERE recid = 'TSM';")

STATUS=$(echo "$STATUS" | xargs)

case "$STATUS" in
    START|AUTO)
        echo "RUNNING"
        ;;
    STOP)
        echo "STOPPED"
        ;;
    *)
        echo "STOPPED"
        ;;
esac
