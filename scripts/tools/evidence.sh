#!/bin/bash
# Print kun konfiguration til stdout. Brug tee som bootstrap til at gemme.
# Logfiler/mtime medtages ikke i hash-manifestet: de aendrer sig normalt i drift.
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin LC_ALL=C
[[ $EUID == 0 ]] || { echo 'Koer med sudo' >&2; exit 2; }
printf '=== SecureBase - konfigurationsmanifest ===\n'
for file in /etc/hostname /etc/hosts /etc/ssh/sshd_config.d/00-securebase.conf \
 /etc/sudoers.d/securebase-admins /etc/cron.d/securebase-monitor \
 /etc/logrotate.d/securebase-monitor /etc/securebase/monitor.conf \
 /etc/securebase/healthcheck.conf /usr/local/sbin/securebase-monitor.sh \
 /usr/local/sbin/securebase-healthcheck /etc/netplan/99-securebase.yaml; do
    if [[ -f $file ]]; then sha256sum "$file"; stat -c 'MODE=%a OWNER=%U:%G %n' "$file"; fi
done
printf '\n=== Rollegrupper ===\n'
getent group admins developers guests securebase
printf '\n=== UFW ===\n'
ufw status verbose
printf '\n=== Projekt-ACL ===\n'
getfacl -p /srv/securebase
printf '\n=== Cron-definitioner for monitor ===\n'
grep -R -n 'securebase-monitor.sh' /etc/cron.d /etc/crontab 2>/dev/null || true
