#!/bin/bash
# FORMÅL: Måler CPU, RAM og disk, logger status og sender user.warning ved valgte grænser.
# KØRSEL: bash scripts/monitor.sh --sample | --self-test; i drift kaldes den installerede kopi af cron som root.
# DIREKTE: Ja til sample/self-test. Normal drift installeres af setup.sh og køres via /etc/cron.d/securebase-monitor.

set -Eeuo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin LC_ALL=C
umask 027
CONFIG=/etc/securebase/monitor.conf
LOGFILE=/var/log/securebase-monitor.log
DISK_THRESHOLD=85 MEMORY_THRESHOLD=90
MODE=run
while (($#)); do
    case $1 in
        --sample) MODE=sample;; --self-test) MODE=selftest;;
        --config) (($#>=2)) || { echo 'config-fil mangler' >&2; exit 2; }; CONFIG=$2; shift;;
        --help) echo 'monitor.sh [--sample | --self-test] [--config FIL]'; exit 0;;
        *) echo "Ukendt argument: $1" >&2; exit 2;;
    esac; shift
done
status_for() {
    local disk=$1 memory=$2 dlimit=$3 mlimit=$4 result=OK
    if ((disk>=dlimit)); then result=DISK_WARNING; fi
    if awk -v m="$memory" -v t="$mlimit" 'BEGIN {exit !(m>=t)}'; then
        if [[ $result == OK ]]; then result=MEMORY_WARNING; else result+=,MEMORY_WARNING; fi
    fi
    printf '%s\n' "$result"
}
if [[ $MODE == selftest ]]; then
    failures=0
    while read -r disk memory want; do
        got=$(status_for "$disk" "$memory" 85 90)
        printf '[TEST] disk=%s memory=%s -> %s (forventet %s)\n' "$disk" "$memory" "$got" "$want"
        [[ $got == "$want" ]] || failures=$((failures+1))
    done <<'EOF'
16 14.0 OK
84 89.9 OK
85 14.0 DISK_WARNING
16 90.0 MEMORY_WARNING
95 92.0 DISK_WARNING,MEMORY_WARNING
EOF
    [[ $failures == 0 ]]; exit $?
fi
if [[ -f $CONFIG ]]; then
    while IFS= read -r line || [[ -n $line ]]; do
        [[ $line =~ ^[[:space:]]*(#.*)?$ ]] && continue
        if [[ $line =~ ^(DISK_THRESHOLD|MEMORY_THRESHOLD)=\"([0-9]{1,3})\"$ ]]; then
            key=${BASH_REMATCH[1]}; value=$((10#${BASH_REMATCH[2]}))
            ((value>=1 && value<=100)) || { echo 'Threshold uden for 1-100' >&2; exit 2; }
            printf -v "$key" '%s' "$value"
        else echo 'Ugyldig monitor-konfiguration' >&2; exit 2; fi
    done < "$CONFIG"
fi
if [[ $MODE == run ]]; then
    [[ $EUID == 0 ]] || { echo 'Normal logning kraever root. Brug --sample for laesende test.' >&2; exit 2; }
    [[ -d /var/lib/securebase && ! -L /var/lib/securebase ]] || { echo 'Koer setup foerst' >&2; exit 2; }
    [[ $(stat -c '%u:%a' /var/lib/securebase) == 0:700 ]] || { echo 'Usikker state-mappe' >&2; exit 2; }
    [[ -f $LOGFILE && ! -L $LOGFILE && $(stat -c '%u:%a' "$LOGFILE") == 0:640 ]] || { echo 'Logfil mangler/har usikre rettigheder' >&2; exit 2; }
    exec 9>/var/lib/securebase/monitor.lock
    flock -n 9 || exit 0
    trap 'rc=$?; logger -p user.err -t securebase-monitor "Monitor ERROR rc=$rc line=$LINENO" || true; exit "$rc"' ERR
fi
cpu_counters() {
    # Foerste otte CPU-felter; guest/guest_nice er allerede inkluderet i user/nice.
    awk '/^cpu / {total=0; for(i=2;i<=9;i++) total+=$i; printf "%.0f %.0f\n",total,$5+$6; exit}' /proc/stat
}
read -r total1 idle1 < <(cpu_counters)
sleep 1
read -r total2 idle2 < <(cpu_counters)
delta=$((total2-total1)); idle_delta=$((idle2-idle1))
((delta>0)) || { echo 'CPU-sample kunne ikke beregnes' >&2; exit 2; }
CPU=$(awk -v t="$delta" -v i="$idle_delta" 'BEGIN {v=100*(t-i)/t; if(v<0)v=0; if(v>100)v=100; printf "%.1f",v}')
# MemAvailable tager hoejde for genanvendelig cache; ikke blot MemFree.
MEMORY=$(awk '/^MemTotal:/ {t=$2} /^MemAvailable:/ {a=$2; seen=1}
    END {if(t<=0 || !seen)exit 1; printf "%.1f",100*(t-a)/t}' /proc/meminfo)
DISK=$(df -P / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
[[ $DISK =~ ^[0-9]+$ && $MEMORY =~ ^[0-9]+\.[0-9]+$ ]] || { echo 'Ugyldigt maaleresultat' >&2; exit 2; }
STATUS=$(status_for "$DISK" "$MEMORY" "$DISK_THRESHOLD" "$MEMORY_THRESHOLD")
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
LINE="$TIMESTAMP CPU=${CPU}% MEMORY=${MEMORY}% DISK=${DISK}% STATUS=$STATUS"
if [[ $MODE == sample ]]; then printf '%s\n' "$LINE"; exit 0; fi
# Genåbn logfilen hver gang. Logrotate kraever derfor ikke copytruncate/postrotate.
printf '%s\n' "$LINE" >> "$LOGFILE"
if [[ $STATUS != OK ]]; then
    logger -p user.warning -t securebase-monitor "MEMORY=${MEMORY}% DISK=${DISK}% STATUS=$STATUS"
fi
