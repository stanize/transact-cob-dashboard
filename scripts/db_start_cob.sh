#!/bin/bash

echo "[STAGE] Stopping JBoss"
sleep 3

echo "[STAGE] Clearing TSA.STATUS"
sleep 3

echo "[STAGE] Starting JBoss"
sleep 3

echo "[STAGE] Waiting for full deployment"
sleep 3

echo "[STAGE] Stopping TSA services"
sleep 3

echo "[STAGE] Resolving EB.EOD.ERRORS"
sleep 3

echo "[STAGE] Starting TSM and COB"
sleep 3

echo "[STAGE] Launching TSM via TAFJEE"
sleep 3

echo "[DONE] COB start workflow completed"
exit 0
