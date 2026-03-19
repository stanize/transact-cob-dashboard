#!/bin/bash

echo "Restarting JBoss service..."

if sudo systemctl restart jboss; then
    echo "JBoss restarted successfully"
    exit 0
else
    echo "Failed to restart JBoss service"
    exit 1
fi
