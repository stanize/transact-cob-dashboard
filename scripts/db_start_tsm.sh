#!/bin/bash

set -o pipefail

DB_HOST="T24-DB"
DB_USER="t24"
DB_NAME="BANCA"

TSM_URL="http://localhost:8080/TAFJRestServices/resources/ofs"
AUTH_HEADER="Authorization: Basic dGFmai5hZG1pbjpBWElAZ3RwcXJYNC=="

SERVICE_RECID="TSM"
STATUS_FIELD="6"
EXPECTED_STATUS="START"

echo "[STAGE] Checking TSM status"

not_started=$(
  psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -At \
    -c "SELECT 1
        FROM public.\"F_TSA_SERVICE\"
        WHERE recid = '$SERVICE_RECID'
          AND COALESCE((xmlrecord::json)->>'$STATUS_FIELD','') <> '$EXPECTED_STATUS'
        LIMIT 1;"
)
rc=$?

if [ $rc -ne 0 ]; then
  echo "[ERROR] Failed to query F_TSA_SERVICE for TSM status"
  exit 1
fi

if [ -z "$not_started" ]; then
  echo "[DONE] TSM already in START status"
  exit 0
fi

echo "[STAGE] Sending START for TSM"

response=$(curl --silent --request POST \
  --url "$TSM_URL" \
  --header "$AUTH_HEADER" \
  --header 'cache-control: no-cache' \
  --header 'content-type: application/json' \
  --data '{"ofsRequest":"TSA.SERVICE,START/I/PROCESS,AUTO01/123123,TSM "}')

if [ $? -ne 0 ] || [ -z "$response" ]; then
  echo "[ERROR] Failed to connect to OFS service for TSM START"
  exit 1
fi

ofs_response=$(echo "$response" | sed -n 's/.*"ofsResponse":"\([^"]*\)".*/\1/p')
status_code=$(echo "$ofs_response" | sed -n 's#.*//\([-0-9][0-9]*\),.*#\1#p')

if [ "$status_code" != "1" ]; then
  echo "[ERROR] TSM START failed. OFS response: $ofs_response"
  exit 1
fi

echo "[DONE] TSM START command accepted"
exit 0
