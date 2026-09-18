#!/bin/bash

set -euo pipefail

LOGFILE="/var/log/securebase-monitor.log"

DISK_THRESHOLD=85
MEMORY_THRESHOLD=90

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

CPU=$(LC_ALL=C top -bn1 | awk '/^%Cpu/ {printf "%.1f", 100 - $8}')
MEMORY=$(free | awk '/Mem:/ {printf "%.1f", ($3/$2) * 100}')
DISK=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')

STATUS="OK"

if (( DISK >= DISK_THRESHOLD )); then
    STATUS="DISK_WARNING"
fi

if awk -v mem="$MEMORY" -v threshold="$MEMORY_THRESHOLD" \
    'BEGIN {exit !(mem >= threshold)}'; then
    if [[ "$STATUS" == "OK" ]]; then
        STATUS="MEMORY_WARNING"
    else
        STATUS="${STATUS},MEMORY_WARNING"
    fi
fi

if [[ "$STATUS" != "OK" ]]; then
    logger -p user.warning -t securebase-monitor \
        "MEMORY=${MEMORY}% DISK=${DISK}% STATUS=${STATUS}"
fi

printf '%s CPU=%s%% MEMORY=%s%% DISK=%s%% STATUS=%s\n' \
    "$TIMESTAMP" "$CPU" "$MEMORY" "$DISK" "$STATUS" >> "$LOGFILE"
