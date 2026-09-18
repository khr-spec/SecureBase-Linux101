#!/bin/bash
monitoring_setup() {
    local logfile=/var/log/securebase-monitor.log
    bash -n "$SCRIPT_DIR/monitor.sh"
    install_managed "$SCRIPT_DIR/monitor.sh" /usr/local/sbin/securebase-monitor.sh 0750
    cat > "$WORK/monitor.conf" <<EOF
DISK_THRESHOLD="$DISK_THRESHOLD"
MEMORY_THRESHOLD="$MEMORY_THRESHOLD"
EOF
    install_managed "$WORK/monitor.conf" /etc/securebase/monitor.conf 0644
    [[ ! -L $logfile ]] || die 'Logfil er symlink'
    # Opret KUN hvis mangler. Brug aldrig install/cp /dev/null paa en eksisterende log.
    if [[ ! -e $logfile ]]; then install -m 0640 -o root -g adm /dev/null "$logfile"; fi
    [[ -f $logfile ]] || die 'Logstien er ikke en normal fil'
    chown root:adm "$logfile"; chmod 0640 "$logfile"
    cat > "$WORK/logrotate" <<EOF
/var/log/securebase-monitor.log {
    su root adm
    daily
    rotate $LOGROTATE_KEEP
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
}
EOF
    logrotate -d "$WORK/logrotate"
    install_managed "$WORK/logrotate" /etc/logrotate.d/securebase-monitor 0644
    # Valider den SAMLEDE konfiguration for dubletter og global arv.
    logrotate -d /etc/logrotate.conf
    cat > "$WORK/cron" <<EOF
# Managed by SecureBase; system-cron inkluderer feltet root.
SHELL=/bin/bash
PATH=/usr/sbin:/usr/bin:/sbin:/bin
LC_ALL=C
MAILTO=""
*/$MONITOR_INTERVAL * * * * root /usr/local/sbin/securebase-monitor.sh
EOF
    install_managed "$WORK/cron" /etc/cron.d/securebase-monitor 0644
    ensure_service cron.service
    ensure_service logrotate.timer
    ensure_service rsyslog.service
    /usr/local/sbin/securebase-monitor.sh
    tail -n 1 "$logfile"
    ok 'Monitor installeret. Tidligere loghistorik bevaret. Cron genstarter ikke ved uaendrede filer.'
}
