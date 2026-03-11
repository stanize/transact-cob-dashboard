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

    echo "[DEBUG] OFS Request: TSA.SERVICE,STOP/I/PROCESS,${OFS_USER}/${OFS_PASS},${service}"


    service_ofs="${service//\//^}"

    ofs="TSA.SERVICE,STOP/I/PROCESS,${OFS_USER}/${OFS_PASS},${service_ofs} "

    response=$(curl --silent --fail --request POST \
      --url "$OFS_URL" \
      --header "Authorization: $OFS_AUTH" \
      --header 'cache-control: no-cache' \
      --header 'content-type: application/json' \
      --data "{\"ofsRequest\":\"$ofs\"}")

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        echo "[ERROR] Failed to connect to OFS service for $service"
        failed=1
        continue
    fi

    ofs_response=$(echo "$response" | sed -n 's/.*"ofsResponse":"\([^"]*\)".*/\1/p')
    status_code=$(echo "$ofs_response" | sed -n 's#.*//\([-0-9][0-9]*\),.*#\1#p')

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
