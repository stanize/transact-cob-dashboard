#!/bin/bash
#
# Purpose: Resolve EB.EOD.ERROR records where DATE.RESOLVED is blank/null-ish
#

set -u

# --------------------------------------------------
# Config
# --------------------------------------------------

DB_HOST="${DB_HOST:-T24-DB}"
DB_USER="${DB_USER:-t24}"
DB_NAME="${DB_NAME:-BANCA}"
TABLE='public."F_EB_EOD_ERROR"'

PROCESS_REF="${PROCESS_REF:-IGGI01/123123123}"
RESOLVED_DATE="${RESOLVED_DATE:-$(date +%Y%m%d)}"

OFS_URL="${OFS_URL:-http://localhost:8080/TAFJRestServices/resources/ofs}"
AUTH_HEADER="${AUTH_HEADER:-Authorization: Basic dGFmai5hZG1pbjpBWElAZ3RwcXJYNC==}"

# --------------------------------------------------
# Logging
# --------------------------------------------------

log() {
    echo "[STAGE] $1"
}

done_msg() {
    echo "[DONE] $1"
}

fail() {
    echo "[ERROR] $1"
    exit 1
}

# --------------------------------------------------
# OFS processor
# --------------------------------------------------

process_ofs_line() {
    local ofs_line="$1"
    local response
    local ofs_response
    local status_code

    response=$(curl --silent --request POST \
        --url "$OFS_URL" \
        --header "$AUTH_HEADER" \
        --header 'cache-control: no-cache' \
        --header 'content-type: application/json' \
        --data "{\"ofsRequest\":\"$ofs_line\"}")

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        echo "[ERROR] curl failed or empty response"
        return 1
    fi

    ofs_response=$(echo "$response" | sed -n 's/.*"ofsResponse":"\([^"]*\)".*/\1/p')

    if [ -z "$ofs_response" ]; then
        echo "[ERROR] Could not extract ofsResponse. Raw response: $response"
        return 1
    fi

    status_code=$(echo "$ofs_response" | sed -n 's#.*//\([-0-9][0-9]*\),.*#\1#p')

    if [ "$status_code" != "1" ]; then
        echo "[ERROR] OFS failed. Response: $ofs_response"
        return 1
    fi

    return 0
}

# --------------------------------------------------
# SQL to generate OFS lines
# --------------------------------------------------

SQL="
WITH candidates AS (
  SELECT
    recid,
    CASE
      WHEN NOT (xmlrecord::jsonb ? '7') THEN ARRAY[1]
      WHEN (xmlrecord::jsonb->'7') = 'null'::jsonb THEN ARRAY[1]
      WHEN jsonb_typeof(xmlrecord::jsonb->'7') = 'array'
        THEN ARRAY(
          SELECT ord
          FROM jsonb_array_elements(xmlrecord::jsonb->'7') WITH ORDINALITY AS e(val, ord)
          WHERE val = 'null'::jsonb
          ORDER BY ord
        )
      ELSE ARRAY[]::int[]
    END AS null_positions
  FROM ${TABLE}
),
needs_fix AS (
  SELECT recid, null_positions
  FROM candidates
  WHERE array_length(null_positions, 1) > 0
)
SELECT
  'EB.EOD.ERROR,/I/PROCESS//0,${PROCESS_REF},' ||
  recid || ',' ||
  (
    SELECT string_agg(
      'DATE.RESOLVED:' || pos::text || ':1=${RESOLVED_DATE}',
      ','
      ORDER BY pos
    )
    FROM unnest(null_positions) AS pos
  )
FROM needs_fix
ORDER BY recid;
"

# --------------------------------------------------
# Main
# --------------------------------------------------

log "Resolving EB.EOD.ERROR records"

ofs_lines=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -At -c "$SQL" 2>&1)
rc=$?

if [ $rc -ne 0 ]; then
    echo "$ofs_lines"
    fail "Failed to generate OFS lines from PostgreSQL"
fi

if [ -z "$ofs_lines" ]; then
    done_msg "No EB.EOD.ERROR records required remediation"
    exit 0
fi

fail_count=0
processed_count=0

while IFS= read -r ofs_line; do
    [ -z "$ofs_line" ] && continue

    processed_count=$((processed_count + 1))
    recid=$(printf '%s\n' "$ofs_line" | cut -d',' -f4)

    log "Resolving EB.EOD.ERROR recid=${recid}"

    if process_ofs_line "$ofs_line"; then
        done_msg "Resolved recid=${recid}"
    else
        echo "[ERROR] Failed recid=${recid}"
        fail_count=$((fail_count + 1))
    fi
done <<< "$ofs_lines"

if [ $fail_count -ne 0 ]; then
    fail "EB.EOD.ERROR remediation finished with ${fail_count} failure(s) out of ${processed_count}"
fi

done_msg "EB.EOD.ERROR remediation finished successfully for ${processed_count} record(s)"
exit 0
