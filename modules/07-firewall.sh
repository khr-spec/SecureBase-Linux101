#!/bin/bash
firewall_setup() {
    local output
    check_ufw_rules || die 'Uventede UFW-regler. Ingen ufw reset eller automatisk sletning.'
    # IPv6 forbliver firewalled; ingen IPv6 SSH-undtagelse oprettes.
    awk '/^IPV6=/ {print "IPV6=yes"; found=1; next} {print} END {if(!found) print "IPV6=yes"}' /etc/default/ufw > "$WORK/ufw-default"
    install_managed "$WORK/ufw-default" /etc/default/ufw 0644
    local need_reload=$CHANGED
    output=$(ufw show added)
    if ! grep -q '^ufw ' <<< "$output"; then
        ufw allow from "$SSH_ALLOWED_SOURCE" to any port "$SSH_PORT" proto tcp
    else ok 'SSH-kildereglen findes allerede'; fi
    # Skriv kun politikker ved drift for at undgaa unoedvendige firewall-reloads.
    if ! grep -q '^DEFAULT_INPUT_POLICY="DROP"' /etc/default/ufw; then ufw default deny incoming; fi
    if ! grep -q '^DEFAULT_OUTPUT_POLICY="ACCEPT"' /etc/default/ufw; then ufw default allow outgoing; fi
    if ! grep -q '^DEFAULT_FORWARD_POLICY="DROP"' /etc/default/ufw; then ufw default deny routed; fi
    output=$(ufw status verbose)
    if ! grep -q '^Status: active' <<< "$output"; then ufw --force enable
    elif [[ $need_reload == 1 ]]; then ufw reload; fi
    output=$(ufw status verbose)
    if ! grep -q '^Logging: on (low)' <<< "$output"; then ufw logging low; fi
    ufw status verbose
    ok 'UFW aktiv. Kun den afgraensede IPv4 SSH-undtagelse som brugerregel.'
    info 'UFWs indbyggede loopback/established/ICMP-regler bevares; status er ikke en fuld nftables-audit.'
}
