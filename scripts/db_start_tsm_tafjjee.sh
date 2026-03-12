#!/bin/bash

URL="http://localhost:8080/TAFJRestServices/resources/trun"
AUTH_HEADER="Authorization: Basic dGFmai5hZG1pbjpBWElAZ3RwcXJYNC=="
CONTENT_TYPE="Content-Type: application/x-www-form-urlencoded"

echo "[STAGE] Sending START.TSM via TAFJJEE"

response=$(curl -s --request POST "$URL" \
  --header "$AUTH_HEADER" \
  --header "$CONTENT_TYPE" \
  --data-urlencode "command=START.TSM 1" \
  --data-urlencode "inParameters=param=OUT.PARAM")

if [ $? -ne 0 ] || [ -z "$response" ]; then
  echo "[ERROR] Failed to connect to TAFJJEE service"
  exit 1
fi

status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d':' -f2 | tr -d '"')

if [ "$status" = "SUCCESS" ]; then
  echo "[DONE] START.TSM executed successfully via TAFJJEE"
  exit 0
fi

echo "[ERROR] START.TSM failed. Full response:"
echo "$response"
exit 1
