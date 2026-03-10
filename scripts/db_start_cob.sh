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
# Dummy stages (to be implemented later)
# --------------------------------------------------

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------

log "TBD - Clearing TSA.STATUS"
sleep 1
done_msg "TBD - TSA.STATUS cleared"

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Starting JBoss"
sleep 1

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Waiting for full deployment"
sleep 1

# --------------------------------------------------
# Stage  - 
# --------------------------------------------------
log "TBD - Stopping TSA services"
sleep 1

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
