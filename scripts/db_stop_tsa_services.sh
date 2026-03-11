#!/bin/bash

DB_HOST="T24-DB"
DB_USER="t24"
DB_NAME="BANCA"

OFS_URL="http://localhost:8080/TAFJRestServices/resources/ofs"
OFS_AUTH="Basic dGFmai5hZG1pbjpBWElAZ3RwcXJYNC=="

OFS_USER="AUTO01"
OFS_PASS="123123"

echo "[STAGE] Stopping TSA services"

services=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -At -F '|' -c "
SELECT recid
FROM public.\"F_TSA_SERVICE\"
WHERE COALESCE((xmlrecord::json)->>'6','') <> 'STOP'
ORDER BY recid;
")
rc=$?

if [ $rc -ne 0 ]; then
    echo "[ERROR] Failed to query F_TSA_SERVICE"
    exit 1
fi

if [ -z "$services" ]; then
    echo "[DONE] No TSA services needed stopping"
    exit 0
fi

failed=0

while IFS= read -r service; do
    [ -z "$service" ] && continue

    echo "[STAGE] Stopping TSA service: $service"

    response=$(curl --silent --fail --request POST \
      --url "$OFS_URL" \
      --header "Authorization: $OFS_AUTH" \
      --header 'cache-control: no-cache' \
      --header 'content-type: application/json' \
      --data "{\"ofsRequest\":\"TSA.SERVICE,STOP/I/PROCESS,${OFS_USER}/${OFS_PASS},${service} \"}")

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        echo "[ERROR] Failed to connect to OFS service for $service"
        failed=1
        continue
    fi

    ofs_response=$(echo "$response" | sed -n 's/.*"ofsResponse":"\([^"]*\)".*/\1/p')
    status_code=$(echo "$ofs_response" | awk -F'/' '{print $3}' | cut -d',' -f1)

    if [ "$status_code" = "1" ]; then
        echo "[DONE] STOP successful for $service"
    else
        echo "[ERROR] STOP failed for $service. Full response: $ofs_response"
        failed=1
    fi
done <<< "$services"

if [ $failed -ne 0 ]; then
    echo "[ERROR] One or more TSA services failed to stop"
    exit 1
fi

echo "[DONE] All TSA services stopped successfully"
exit 0
