#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
    echo "[STAGE] $1"
}

fail() {
    echo "[ERROR] $1"
    exit 1
}

done_msg() {
    echo "[DONE] $1"
}

# --------------------------------------------------
# Stage 1 - Stop JBoss
# --------------------------------------------------

log "Stopping JBoss"

if ! sudo systemctl stop jboss; then
    fail "Failed to stop JBoss"
fi

done_msg "JBoss stop completed"

# --------------------------------------------------
# Stage 2 - Clear TSA.STATUS
# --------------------------------------------------

log "Clearing TSA.STATUS"

output=$(psql -h T24-DB -U t24 -d BANCA -c 'DELETE FROM "public"."F_TSA_STATUS";' 2>&1)
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "$output"
    fail "Failed to clear TSA.STATUS"
fi

deleted_count=$(echo "$output" | grep -oP 'DELETE \K\d+')

if [ -n "$deleted_count" ]; then
    done_msg "TSA.STATUS cleared. Deleted rows: $deleted_count"
else
    echo "$output"
    fail "TSA.STATUS cleanup completed but deleted row count could not be confirmed"
fi

# --------------------------------------------------
# Stage 3 - Start JBoss and wait for deployments
# --------------------------------------------------

log "Starting JBoss and waiting for deployments"

if ! "$SCRIPT_DIR/db_start_jboss_full.sh"; then
    fail "JBoss start or deployment validation failed"
fi

done_msg "JBoss fully deployed"

# --------------------------------------------------
# Stage 4 - Stop TSA services
# --------------------------------------------------

if ! "$SCRIPT_DIR/db_stop_tsa_services.sh"; then
    fail "Failed to stop one or more TSA services"
fi

done_msg "TSA services stopped"

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Resolving EB.EOD.ERRORS"
sleep 1

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Starting TSM and COB"
sleep 1

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Launching TSM via TAFJEE"
sleep 1

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------

done_msg "COB start workflow completed"
exit 0
