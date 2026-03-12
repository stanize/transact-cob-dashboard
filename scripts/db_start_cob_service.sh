#!/bin/bash

COB_SERVICE="COB"
AUTH_HEADER="Authorization: Basic dGFmai5hZG1pbjpBWElAZ3RwcXJYNC=="
OFS_URL="http://localhost:8080/TAFJRestServices/resources/ofs"

echo "[STAGE] Sending START for COB"

response=$(curl --silent --request POST \
  --url "$OFS_URL" \
  --header "$AUTH_HEADER" \
  --header 'cache-control: no-cache' \
  --header 'content-type: application/json' \
  --data "{\"ofsRequest\":\"TSA.SERVICE,START/I/PROCESS,AUTO01/123123,$COB_SERVICE \"}")

if [ $? -ne 0 ] || [ -z "$response" ]; then
  echo "[ERROR] Failed to connect to OFS service for COB START"
  exit 1
fi

ofs_response=$(echo "$response" | sed -n 's/.*"ofsResponse":"\([^"]*\)".*/\1/p')
status_code=$(echo "$ofs_response" | sed -n 's#.*//\([-0-9][0-9]*\),.*#\1#p')

if [ "$status_code" != "1" ]; then
  echo "[ERROR] COB START command failed. Response: $ofs_response"
  exit 1
fi

echo "[DONE] COB START command accepted"
exit 0
