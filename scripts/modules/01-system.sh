#!/bin/bash
system_setup() {
    local apt_opts=(-o DPkg::Lock::Timeout=120 -o Acquire::Retries=3
                    -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)
    local pkg missing=() packages=(openssh-server ufw acl logrotate cron rsyslog procps iproute2 util-linux sudo python3 netplan.io)
    for pkg in "${packages[@]}"; do
        if [[ $(dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null || true) != 'install ok installed' ]]; then missing+=("$pkg"); fi
    done
    export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
    if [[ $UPDATE_SYSTEM == yes && $SKIP_UPGRADE != yes ]]; then
        apt-get "${apt_opts[@]}" update
        apt-get "${apt_opts[@]}" -y upgrade
    elif ((${#missing[@]})); then apt-get "${apt_opts[@]}" update
    else info 'Pakkeopgradering sprunget over efter eksplicit valg'; fi
    if ((${#missing[@]})); then apt-get "${apt_opts[@]}" install -y "${missing[@]}"; else ok 'Alle noedvendige pakker er installeret'; fi
    [[ $(hostname) == "$HOSTNAME" ]] || hostnamectl set-hostname "$HOSTNAME"
    # Bevar andre hosts-linjer; administrer kun 127.0.1.1.
    awk -v host="$HOSTNAME" '
        $1=="127.0.1.1" {if(!done++) print "127.0.1.1\t"host; next}
        {print} END {if(!done) print "127.0.1.1\t"host}
    ' /etc/hosts > "$WORK/hosts"
    install_managed "$WORK/hosts" /etc/hosts 0644
    install -d -o root -g root -m 0755 /etc/securebase
    systemctl daemon-reload
    ok "Hostname: $HOSTNAME. Ingen automatisk reboot."
}
