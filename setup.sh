#!/bin/bash
# SecureBase orchestrator: --check er laesende; --apply aendrer serveren.
set -Eeuo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
umask 027
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"
ACTION=check; CONFIG_FILE="$SCRIPT_DIR/config.env"
CONSOLE_CONFIRMED=no; KEY_CONFIRMED=no; SKIP_UPGRADE=no
usage() {
    cat <<'EOF'
SecureBase 1.1  |  Ubuntu Server 26.04
  sudo bash setup.sh --check
  sudo bash setup.sh --apply --console-confirmed
Valg:
  --config FIL              Alternativ literal config.env
  --skip-upgrade            Spring update/upgrade over; manglende pakker installeres
  --key-login-confirmed     Kun efter fungerende ekstern SSH-key-test; spring prompt over
  --console-confirmed       Du har testet lokal sudo-adgang som bootstrap-brugeren
  --help                    Vis denne tekst
--check aendrer ingen systemkonfiguration. Det er preflight, IKKE en fuld dry-run.
Netplan aendres kun med CONFIGURE_NETWORK="yes". Ingen automatisk reboot.
EOF
}
while (($#)); do
    case $1 in
        --check) ACTION=check;; --apply) ACTION=apply;;
        --config) (($#>=2)) || die '--config mangler fil'; CONFIG_FILE=$2; shift;;
        --console-confirmed) CONSOLE_CONFIRMED=yes;;
        --key-login-confirmed) KEY_CONFIRMED=yes;;
        --skip-upgrade) SKIP_UPGRADE=yes;;
        -h|--help) usage; exit 0;; *) usage; die "Ukendt argument: $1";;
    esac; shift
done
require_root
trap 'rc=$?; printf "\n[FAIL] Linje %s, returkode %s. Deployment ikke gennemfoert.\n" "$LINENO" "$rc" >&2; exit "$rc"' ERR
load_config "$CONFIG_FILE"
for module in "$SCRIPT_DIR"/modules/*.sh; do source "$module"; done
banner
preflight
if [[ $ACTION == check ]]; then
    section 'PLAN / ingen systemaendringer'
    printf '  System: %s | Admin: %s | Projekt: %s\n' "$HOSTNAME" "$ADMIN_USER" "$PROJECT_DIR"
    printf '  SSH: TCP/%s fra %s | Netplan: %s\n' "$SSH_PORT" "$SSH_ALLOWED_SOURCE" "$CONFIGURE_NETWORK"
    printf '  Overvaagning: hvert %s. minut | Disk >= %s%% | RAM >= %s%%\n' "$MONITOR_INTERVAL" "$DISK_THRESHOLD" "$MEMORY_THRESHOLD"
    info 'Naeste: snapshot, konsoladgang, og derefter --apply --console-confirmed.'
    exit 0
fi
[[ $CONSOLE_CONFIRMED == yes ]] || die 'Bekraeft testet lokal bootstrap/sudo-adgang med --console-confirmed.'
if [[ $KEY_CONFIRMED != yes && ! -t 0 ]]; then die 'Interaktiv SSH-key-kontrol kraever en terminal.'; fi
install -d -m 0700 /var/lib/securebase /var/backups/securebase /var/log/securebase
exec 9>/var/lib/securebase/setup.lock
flock -n 9 || die 'Et andet setup koerer allerede.'
WORK=$(mktemp -d /var/lib/securebase/work.XXXXXXXX)
trap 'rm -rf -- "$WORK"' EXIT
DEPLOY_LOG="/var/log/securebase/deploy-$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
exec > >(tee -a "$DEPLOY_LOG") 2>&1
section '1 / System og pakker'; system_setup
section '2 / Brugere og grupper'; users_setup
section '3 / Projekt og ACL'; storage_setup
section '4 / Public key og SSH'; ssh_setup
section '5 / Begraenset sudo'; sudo_setup
section '6 / Firewall'; firewall_setup
section '7 / Monitorering'; monitoring_setup
section '8 / Netvaerk (valgfrit og til sidst)'; network_setup
section '9 / Uafhaengig afsluttende kontrol'
# Installation af en selvstaendig checker; ingen source-afhaengighed ved koersel.
install_managed "$SCRIPT_DIR/healthcheck.sh" /usr/local/sbin/securebase-healthcheck 0750
cat > "$WORK/healthcheck.conf" <<EOF
ADMIN_USER="$ADMIN_USER"
DEVELOPER_USER="$DEVELOPER_USER"
GUEST_USER="$GUEST_USER"
SSH_ALLOWED_SOURCE="$SSH_ALLOWED_SOURCE"
SSH_PORT="$SSH_PORT"
DISK_THRESHOLD="$DISK_THRESHOLD"
MONITOR_INTERVAL="$MONITOR_INTERVAL"
EOF
install_managed "$WORK/healthcheck.conf" /etc/securebase/healthcheck.conf 0644
rc=0
/usr/local/sbin/securebase-healthcheck || rc=$?
if ((rc>=2)); then die 'Afsluttende healthcheck fejlede. Se ovenfor; ingen paastand om fuld succes.'; fi
section 'DEPLOYMENT AFSLUTTET'
ok "Aendrede administrerede filer i denne koersel: $CHANGES"
info "Log: $DEPLOY_LOG"
info "Backup af foerste overskrevne filer: $BACKUP_ROOT"
info 'Test NY SSH-forbindelse fra Windows, og koer setup igen for idempotensbevis.'
[[ ! -f /var/run/reboot-required ]] || warn 'Genstart kraeves. Scriptet genstarter IKKE serveren.'
[[ $rc == 0 ]] || warn 'Healthcheck har advarsler. Gennemgaa dem foer aflevering.'
exit "$rc"
