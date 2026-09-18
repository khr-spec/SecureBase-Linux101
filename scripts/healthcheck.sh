#!/bin/bash
# FORMÅL: Selvstændig, læsende kontrol af firewall, disk, sessioner, UID 0, SSH og monitorering.
# KØRSEL: sudo bash scripts/healthcheck.sh  (eller installeret: sudo /usr/local/sbin/securebase-healthcheck)
# DIREKTE: Ja. Exit 0=OK, 1=WARN, 2=FAIL; scriptet ændrer ikke systemkonfigurationen.

set -Eeuo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin LC_ALL=C
ADMIN_USER=secureadmin DEVELOPER_USER=developer1 GUEST_USER=guest1
SSH_PORT=22 SSH_ALLOWED_SOURCE=10.0.2.2 DISK_THRESHOLD=85 MONITOR_INTERVAL=5
CONFIG=/etc/securebase/healthcheck.conf
if [[ ${1:-} == --help ]]; then
    echo 'sudo bash healthcheck.sh [--config FIL]'; echo 'Laesende kontrol: firewall, disk, sessions, UID 0, SSH og monitorering.'; exit 0
fi
if [[ ${1:-} == --config && $# == 2 ]]; then CONFIG=$2
elif (($#)); then echo 'Ukendt argument' >&2; exit 2; fi
[[ $EUID == 0 ]] || { echo '[FAIL] Koer som root via bootstrap-kontoens sudo for en komplet laesekontrol.' >&2; exit 2; }
GREEN='' YELLOW='' RED='' CYAN='' RESET=''
if [[ -t 1 && -z ${NO_COLOR:-} && ${TERM:-dumb} != dumb ]]; then
    GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; CYAN=$'\033[36m'; RESET=$'\033[0m'
fi
PASS=0 WARN=0 FAIL=0
ok() { PASS=$((PASS+1)); printf '  %s[OK]%s   %s\n' "$GREEN" "$RESET" "$*"; }
warn() { WARN=$((WARN+1)); printf '  %s[WARN]%s %s\n' "$YELLOW" "$RESET" "$*"; }
fail() { FAIL=$((FAIL+1)); printf '  %s[FAIL]%s %s\n' "$RED" "$RESET" "$*"; }
heading() { printf '\n%s── %s ──%s\n' "$CYAN" "$*" "$RESET"; }
printf '\n┌──────────────────────────────────────────────────┐\n│  SECUREBASE  /  HEALTH CHECK                      │\n│  Laesende kontrol - ingen systemaendringer        │\n└──────────────────────────────────────────────────┘\n'
printf '  Vaert: %s   Tid: %s\n' "$(hostname)" "$(date -u +%FT%TZ)"
if [[ -f $CONFIG && ! -L $CONFIG ]]; then
    while IFS= read -r line || [[ -n $line ]]; do
        [[ $line =~ ^[[:space:]]*(#.*)?$ ]] && continue
        if [[ $line =~ ^(ADMIN_USER|DEVELOPER_USER|GUEST_USER|SSH_ALLOWED_SOURCE|SSH_PORT|DISK_THRESHOLD|MONITOR_INTERVAL)=\"([a-zA-Z0-9_./-]+)\"$ ]]; then
            printf -v "${BASH_REMATCH[1]}" '%s' "${BASH_REMATCH[2]}"
        else fail 'Ugyldig healthcheck-konfiguration'; exit 2; fi
    done < "$CONFIG"
else warn 'Ingen installeret healthcheck.conf; bruger de dokumenterede lab-standardvaerdier'; fi
[[ $DISK_THRESHOLD =~ ^[0-9]{1,3}$ && $MONITOR_INTERVAL =~ ^[0-9]{1,2}$ && $SSH_PORT =~ ^[0-9]+$ ]] || { fail 'Ugyldige numeriske vaerdier'; exit 2; }
DISK_THRESHOLD=$((10#$DISK_THRESHOLD)); MONITOR_INTERVAL=$((10#$MONITOR_INTERVAL))
((DISK_THRESHOLD>=1 && DISK_THRESHOLD<=100 && MONITOR_INTERVAL>=1 && MONITOR_INTERVAL<=30)) || { fail 'Konfiguration uden for interval'; exit 2; }

heading '1 / Firewall'
if command -v ufw >/dev/null; then
    if fw=$(ufw status verbose 2>&1); then
        printf '%s\n' "$fw" | sed 's/^/    /'
        if grep -q '^Status: active' <<< "$fw"; then ok 'UFW aktiv'; else fail 'UFW inaktiv'; fi
        if grep -q 'deny (incoming), allow (outgoing)' <<< "$fw"; then ok 'Indgaaende deny / udgaaende allow'; else fail 'Standardpolitikken afviger'; fi
        if rules=$(ufw show added 2>&1); then
            count=0; wrong=0
            while IFS= read -r line; do
                [[ $line == ufw\ * ]] || continue
                count=$((count+1)); line=${line%% comment *}; line=${line//\/32/}
                if [[ $line != "ufw allow from ${SSH_ALLOWED_SOURCE%/32} to any port $SSH_PORT proto tcp" &&
                      $line != "ufw allow proto tcp from ${SSH_ALLOWED_SOURCE%/32} to any port $SSH_PORT" ]]; then wrong=$((wrong+1)); fi
            done <<< "$rules"
            if [[ $count == 1 && $wrong == 0 ]]; then ok 'Kun den forventede kildebegraensede SSH-brugerregel'
            else fail 'UFW-brugerregler afviger fra den ene forventede SSH-regel'; fi
        else fail 'Kunne ikke laese UFW-regler'; fi
        if grep -q '^IPV6=yes' /etc/default/ufw; then ok 'IPv6 behandles ogsaa af UFW'; else warn 'UFW IPv6-konfiguration skal afklares'; fi
    else fail "UFW-kontrol fejlede: $fw"; fi
else fail 'ufw mangler'; fi

heading '2 / Ledig diskplads'
if disk=$(df -P /) && human=$(df -hP /); then
    printf '%s\n' "$human" | sed 's/^/    /'
    used=$(awk 'NR==2 {gsub(/%/,"",$5); print $5}' <<< "$disk")
    if [[ $used =~ ^[0-9]+$ ]]; then
        if ((used>=DISK_THRESHOLD)); then warn "Rootdisk: $used% >= $DISK_THRESHOLD%"; else ok "Rootdisk: $used% < $DISK_THRESHOLD%"; fi
    else fail 'Diskprocent kunne ikke laeses'; fi
else fail 'df fejlede'; fi

heading '3 / Aktive og loggede ind brugere'
if sessions=$(who); then
    if [[ -n $sessions ]]; then printf '%s\n' "$sessions" | sed 's/^/    /'; ok 'who: registrerede login-sessioner vist'
    else warn 'who viser ingen utmp-login; dette beviser ikke fravaer af SSH-sessioner'; fi
else fail 'who fejlede'; fi
if command -v loginctl >/dev/null; then
    if sessions=$(loginctl list-sessions --no-legend --no-pager 2>/dev/null); then
        printf '    systemd-logind-sessioner:\n%s\n' "${sessions:-    Ingen registrerede sessioner}"
    else warn 'loginctl kunne ikke laese sessions'; fi
fi
printf '    Proces-ejere (inkl. servicekonti; ikke lig med login-sessioner):\n'
ps -eo user= | sort | uniq -c | sed 's/^/    /'

heading '4 / UID 0-audit'
if accounts=$(getent passwd); then
    root_accounts=$(awk -F: '$3==0 {print $1}' <<< "$accounts")
    printf '    UID 0-konti: %s\n' "${root_accounts:-INGEN}"
    extra=$(awk -F: '$3==0 && $1!="root" {print $1}' <<< "$accounts")
    if [[ -n $extra ]]; then fail "Ekstra UID 0-konti: $extra"
    elif [[ $root_accounts == root ]]; then ok 'Kun root har UID 0 i den tilgaengelige NSS-opslagning'
    else fail 'Forventet root-konto med UID 0 mangler'; fi
else fail 'getent passwd fejlede'; fi

heading '5 / SSH og administratorrolle'
if systemctl is-active --quiet ssh.service || systemctl is-active --quiet ssh.socket; then ok 'SSH service/socket aktiv'; else fail 'SSH ikke aktiv'; fi
if [[ -x /usr/sbin/sshd ]] && cfg=$(/usr/sbin/sshd -T 2>/dev/null); then
    for expected in 'permitrootlogin no' 'passwordauthentication no' 'kbdinteractiveauthentication no' 'pubkeyauthentication yes' 'authenticationmethods publickey'; do
        if grep -Fxq "$expected" <<< "$cfg"; then ok "$expected"; else fail "SSH afvigelse: $expected"; fi
    done
else fail 'Effektiv SSH-konfiguration kunne ikke laeses'; fi
if groups=$(id -nG "$ADMIN_USER" 2>/dev/null); then
    printf '    %s grupper: %s\n' "$ADMIN_USER" "$groups"
    if tr ' ' '\n' <<< "$groups" | grep -Fxq sudo; then fail 'Admin er stadig medlem af den brede sudo-gruppe'; else ok 'Admin er ikke i sudo-gruppen'; fi
    if permissions=$(sudo -l -U "$ADMIN_USER" 2>&1); then
        printf '%s\n' "$permissions" | sed 's/^/    /'
        if grep -Eq '\(ALL[[:space:]:A-Z]*\).*ALL' <<< "$permissions"; then fail 'Bred sudo-regel fundet'; fi
    else warn 'Admin sudo-politik kunne ikke listes'; fi
else fail "Admin mangler: $ADMIN_USER"; fi

heading '6 / Monitorering og rotation'
for unit in cron.service logrotate.timer; do
    if systemctl is-active --quiet "$unit"; then ok "$unit aktiv"; else fail "$unit ikke aktiv"; fi
done
expected="*/$MONITOR_INTERVAL * * * * root /usr/local/sbin/securebase-monitor.sh"
if [[ -f /etc/cron.d/securebase-monitor ]] && grep -Fxq "$expected" /etc/cron.d/securebase-monitor; then ok 'Forventet cron-job findes'; else fail 'Cron-job mangler/afviger'; fi
if [[ -f /etc/logrotate.d/securebase-monitor ]]; then ok 'Logrotate-regel findes'; else fail 'Logrotate-regel mangler'; fi
if [[ -s /var/log/securebase-monitor.log ]]; then
    tail -n 1 /var/log/securebase-monitor.log | sed 's/^/    /'
    age=$(( $(date +%s) - $(stat -c %Y /var/log/securebase-monitor.log) ))
    if ((age<0 || age>MONITOR_INTERVAL*120+60)); then warn "Monitorlog er ikke frisk (alder $age sekunder)"; else ok 'Monitorlog indeholder en frisk maaling'; fi
    if tail -n 1 /var/log/securebase-monitor.log | grep -q 'STATUS=OK$'; then ok 'Seneste ressourcestatus OK'; else warn 'Seneste loglinje viser warning eller mangler status'; fi
else warn 'Aktiv monitorlog tom/mangler; kan vaere nyrotation foer naeste cron-koersel'; fi
[[ ! -f /var/run/reboot-required ]] || warn 'Pakkeopdateringer kraever manuel genstart'
heading 'RESULTAT'
printf '  %s OK   %s WARN   %s FAIL\n' "$PASS" "$WARN" "$FAIL"
if ((FAIL)); then printf '  RESULTAT: FAIL\n'; exit 2
elif ((WARN)); then printf '  RESULTAT: WARN - gennemgaa bemærkningerne\n'; exit 1
else printf '  RESULTAT: PASS - de viste kontroller bestaaet\n'; exit 0; fi
