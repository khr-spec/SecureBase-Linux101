#!/bin/bash
# Kaldes SIDST, efter pakkeinstallation og efter SSH/firewall er paa plads.
network_setup() {
    [[ $CONFIGURE_NETWORK == yes ]] || { info 'Netplan ikke aendret (CONFIGURE_NETWORK=no).'; return 0; }
    python3 "$SCRIPT_DIR/tools/netplan_scope.py" "$INTERFACE"
    local target=/etc/netplan/99-securebase.yaml cloud=/etc/cloud/cloud.cfg.d/99-securebase-disable-network.cfg
    local cloud_existed=no file result=0
    cat > "$WORK/netplan.yaml" <<EOF
# Managed by SecureBase; kun den eksplicit valgte single-NIC labmodel.
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: false
      dhcp6: false
      addresses:
        - $STATIC_IP
      routes:
        - to: default
          via: $GATEWAY
      nameservers:
        addresses: [$DNS1, $DNS2]
EOF
    if [[ -f $target ]] && cmp -s "$WORK/netplan.yaml" "$target" &&
       [[ $(find /etc/netplan -maxdepth 1 -name '*.yaml' | wc -l) -eq 1 ]] &&
       ip -4 -o addr show dev "$INTERFACE" | grep -Fq " $STATIC_IP " &&
       ip -4 route show default | grep -Fq "via $GATEWAY dev $INTERFACE" &&
       [[ $(stat -c '%u:%a' "$target") == 0:600 ]] &&
       { [[ ! -d /etc/cloud/cloud.cfg.d ]] || { [[ -f $cloud ]] && grep -Fxq 'network: {config: disabled}' "$cloud"; }; }; then
        ok 'Netplan er allerede konfigureret; ingen netvaerksgenindlaesning'; return 0
    fi
    mkdir -p "$WORK/netplan-stage/etc/netplan" "$WORK/netplan-before"
    install -m 0600 "$WORK/netplan.yaml" "$WORK/netplan-stage/etc/netplan/99-securebase.yaml"
    netplan generate --root-dir "$WORK/netplan-stage"
    for file in /etc/netplan/*.yaml; do
        [[ -f $file ]] || continue
        backup_once "$file"; cp -p "$file" "$WORK/netplan-before/"
    done
    if [[ -d /etc/cloud/cloud.cfg.d ]]; then
        [[ ! -f $cloud ]] || { cp -p "$cloud" "$WORK/cloud.previous"; cloud_existed=yes; }
        printf 'network: {config: disabled}\n' > "$WORK/cloud.cfg"
        install_managed "$WORK/cloud.cfg" "$cloud" 0644
    fi
    # Scope er kontrolleret: migrer kun denne enkle VM's yaml-filer, med backup.
    for file in /etc/netplan/*.yaml; do [[ ! -f $file ]] || rm -- "$file"; done
    install_managed "$WORK/netplan.yaml" "$target" 0600
    if ! netplan generate; then result=1
    elif [[ $NETWORK_APPLY == try ]]; then
        warn 'Kontroller nyt SSH-login fra Windows under netplan try; bekraeft i konsollen.'
        netplan try --timeout 120 || result=1
    else
        warn 'NETWORK_APPLY=apply er valgt: ingen interaktiv netplan-bekraeftelse.'
        netplan apply || result=1
    fi
    if ! ip -4 -o addr show dev "$INTERFACE" | grep -Fq " $STATIC_IP "; then result=1; fi
    if ! ip -4 route show default | grep -Fq "via $GATEWAY dev $INTERFACE"; then result=1; fi
    if ((result)); then
        warn 'Netvaerkskontrol fejlede; gendanner yaml-filer fra denne koersel.'
        rm -f "$target"
        for file in "$WORK/netplan-before"/*.yaml; do [[ ! -f $file ]] || cp -p "$file" /etc/netplan/; done
        if [[ -d /etc/cloud/cloud.cfg.d ]]; then
            if [[ $cloud_existed == yes ]]; then cp -p "$WORK/cloud.previous" "$cloud"; else rm -f "$cloud"; fi
        fi
        netplan generate && netplan apply || warn 'Automatisk gendannelse kunne ikke bekræftes. Brug VirtualBox-konsol og backup.'
        die 'Netvaerksdeployment ikke godkendt'
    fi
    ok "Statisk IPv4: $STATIC_IP via $GATEWAY ($INTERFACE)"
    info 'Ingen IPv6-adresse er statisk sat. UFW er konfigureret til ogsaa at filtrere IPv6.'
}
