#!/bin/bash
# FORMÅL: Fælles funktioner til validering, status, backup, filinstallation og medlemskab.
# KØRSEL: Køres ikke direkte. Sources af scripts/setup.sh før modul-funktionerne kaldes.
# DIREKTE: Nej. Indlæsning alene udfører ingen systemændringer.

C_RESET='' C_OK='' C_WARN='' C_ERR='' C_INFO=''
if [[ -t 1 && -z ${NO_COLOR:-} && ${TERM:-dumb} != dumb ]]; then
    C_RESET=$'\033[0m'; C_OK=$'\033[32m'; C_WARN=$'\033[33m'
    C_ERR=$'\033[31m'; C_INFO=$'\033[36m'
fi
ok()      { printf '  %s[OK]%s %s\n' "$C_OK" "$C_RESET" "$*"; }
info()    { printf '  %s[INFO]%s %s\n' "$C_INFO" "$C_RESET" "$*"; }
warn()    { printf '  %s[WARN]%s %s\n' "$C_WARN" "$C_RESET" "$*" >&2; }
die()     { printf '  %s[FAIL]%s %s\n' "$C_ERR" "$C_RESET" "$*" >&2; exit 1; }
section() { printf '\n%s── %s ──%s\n' "$C_INFO" "$*" "$C_RESET"; }
banner()  { printf '\n┌──────────────────────────────────────────────────┐\n│  SECUREBASE  /  MODUL 6                           │\n│  Reproducerbar Linux-serverkonfiguration          │\n└──────────────────────────────────────────────────┘\n'; }
need() { command -v "$1" >/dev/null 2>&1 || die "Kommando mangler: $1"; }
require_root() { [[ $EUID -eq 0 ]] || die 'Koer med sudo fra opsaetningskontoen.'; }

# Parseren udfoerer IKKE config.env som Bash. $(), backticks etc. afvises.
load_config() {
    local file=$1 line key value number=0
    declare -A seen=()
    [[ -f $file && ! -L $file ]] || die "Konfiguration mangler eller er symlink: $file"
    while IFS= read -r line || [[ -n $line ]]; do
        number=$((number+1)); line=${line%$'\r'}
        [[ $line =~ ^[[:space:]]*(#.*)?$ ]] && continue
        if [[ $line =~ ^([A-Z][A-Z0-9_]*)=\"([a-zA-Z0-9_./,:@%+\ -]*)\"$ ]]; then
            key=${BASH_REMATCH[1]}; value=${BASH_REMATCH[2]}
        else die "Ugyldig literal paa linje $number i $file (brug KEY=\"vaerdi\")."; fi
        case "$key" in
            HOSTNAME|BOOTSTRAP_USER|ADMIN_USER|DEVELOPER_USER|GUEST_USER|PROJECT_DIR|SSH_PUBLIC_KEY_FILE|SSH_PORT|SSH_ALLOWED_SOURCE|ADMIN_SUDO_NOPASSWD|UPDATE_SYSTEM|CONFIGURE_NETWORK|INTERFACE|STATIC_IP|GATEWAY|DNS1|DNS2|NETWORK_APPLY|DISK_THRESHOLD|MEMORY_THRESHOLD|MONITOR_INTERVAL|LOGROTATE_KEEP) ;;
            *) die "Ukendt config-noegle: $key" ;;
        esac
        [[ ! -v seen[$key] ]] || die "Dobbelt config-noegle: $key"
        seen[$key]=1
        printf -v "$key" '%s' "$value"
    done < "$file"
    local required
    for required in HOSTNAME BOOTSTRAP_USER ADMIN_USER DEVELOPER_USER GUEST_USER PROJECT_DIR SSH_PUBLIC_KEY_FILE SSH_PORT SSH_ALLOWED_SOURCE ADMIN_SUDO_NOPASSWD UPDATE_SYSTEM CONFIGURE_NETWORK INTERFACE STATIC_IP GATEWAY DNS1 DNS2 NETWORK_APPLY DISK_THRESHOLD MEMORY_THRESHOLD MONITOR_INTERVAL LOGROTATE_KEEP; do
        [[ -v seen[$required] && -n ${!required} ]] || die "Manglende config-noegle: $required"
    done
}

# Udskift en fil atomisk og KUN naar indhold/metadata afviger.
# Originaler gemmes en gang med root-only adgang. Ingen append-dubletter.
CHANGED=0
CHANGES=0
BACKUP_ROOT=${BACKUP_ROOT:-/var/backups/securebase/before-first-change}
backup_once() {
    local target=$1 backup="$BACKUP_ROOT$1"
    [[ -e $target ]] || return 0
    [[ ! -L $target ]] || die "Afviser symlink: $target"
    if [[ ! -e $backup ]]; then
        install -d -m 0700 "$(dirname "$backup")"
        cp -p -- "$target" "$backup"
    fi
}
install_managed() {
    local source=$1 target=$2 mode=${3:-0644} owner=${4:-root} group=${5:-root}
    local parent temp wanted uid gid old
    CHANGED=0
    [[ -f $source && ! -L $source ]] || die "Ugyldig kildefil: $source"
    [[ ! -L $target ]] || die "Afviser symlink som destination: $target"
    parent=$(dirname "$target")
    [[ -d $parent && ! -L $parent ]] || die "Destinationsmappe mangler/er symlink: $parent"
    uid=$(id -u "$owner"); gid=$(getent group "$group" | cut -d: -f3)
    wanted="${mode#0}:$uid:$gid"
    if [[ -f $target ]] && cmp -s -- "$source" "$target"; then
        old=$(stat -c '%a:%u:%g' "$target")
        if [[ $old == "$wanted" ]]; then ok "Uaendret: $target"; return 0; fi
        backup_once "$target"
        chown "$owner:$group" "$target"; chmod "$mode" "$target"
    else
        [[ ! -e $target || -f $target ]] || die "Destination er ikke en fil: $target"
        backup_once "$target"
        temp=$(mktemp "$parent/.securebase.XXXXXXXX")
        install -m "$mode" -o "$owner" -g "$group" -- "$source" "$temp"
        mv -fT -- "$temp" "$target"
    fi
    CHANGED=1; CHANGES=$((CHANGES+1)); ok "Opdateret: $target"
}
ensure_service() {
    local unit=$1
    if ! systemctl is-enabled --quiet "$unit"; then systemctl enable "$unit"; fi
    if ! systemctl is-active --quiet "$unit"; then systemctl start "$unit"; fi
    ok "Aktiv: $unit"
}
member_of() { id -nG "$1" | tr ' ' '\n' | grep -Fxq -- "$2"; }
add_member() {
    if ! member_of "$1" "$2"; then usermod -aG "$2" "$1"; ok "$1 -> $2"; fi
}
# UFW normaliserer regler. Denne pakke accepterer kun sit ene SSH-formaal.
# Ukendte regler stoppes til manuel vurdering; aldrig ufw reset.
check_ufw_rules() {
    local output line a b found=0
    output=$(ufw show added) || return 1
    a="ufw allow from ${SSH_ALLOWED_SOURCE%/32} to any port $SSH_PORT proto tcp"
    b="ufw allow proto tcp from ${SSH_ALLOWED_SOURCE%/32} to any port $SSH_PORT"
    while IFS= read -r line; do
        [[ $line == ufw\ * ]] || continue
        line=${line%% comment *}; line=${line//\/32/}
        if [[ $line != "$a" && $line != "$b" ]]; then
            printf 'Ikke-administreret/afvigende UFW-regel: %s\n' "$line" >&2; return 1
        fi
        found=$((found+1))
    done <<< "$output"
    [[ $found -le 1 ]] || { printf 'Dublerede SSH-regler; gennemgaa UFW manuelt.\n' >&2; return 1; }
}
