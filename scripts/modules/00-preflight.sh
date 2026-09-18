#!/bin/bash
# FORMÅL: Læsende preflight af platform, konfiguration, bootstrap-konto, netværksscope og konflikter.
# KØRSEL: Køres ikke direkte. Sources af scripts/setup.sh og kaldes som preflight().
# DIREKTE: Nej. --check i setup.sh er den dokumenterede indgang.

preflight() {
    section 'PREFLIGHT / laesende kontrol'
    local os version u entry home uid cmd file group members
    need python3; need systemctl; need getent; need ip; need stat
    os=$(awk -F= '$1=="ID" {gsub(/"/,"",$2); print $2}' /etc/os-release)
    version=$(awk -F= '$1=="VERSION_ID" {gsub(/"/,"",$2); print $2}' /etc/os-release)
    [[ $os == ubuntu && $version == 26.04 ]] || die "Maalplatform er Ubuntu 26.04; fandt $os $version."
    [[ -d /run/systemd/system ]] || die 'Et bootet systemd-system kraeves (ikke chroot/container).'
    python3 "$SCRIPT_DIR/tools/validate_config.py" "$CONFIG_FILE" "$REPO_DIR"
    ok 'Konfiguration og Ed25519-public key valideret'
    [[ -d /sys/class/net/$INTERFACE ]] || die "Netkort findes ikke: $INTERFACE"
    [[ $BOOTSTRAP_USER != "$ADMIN_USER" ]] || die 'Bootstrap og admin maa ikke vaere samme konto'
    getent passwd "$BOOTSTRAP_USER" >/dev/null || die "Bootstrap-konto $BOOTSTRAP_USER mangler; brug installerens eksisterende bruger"
    member_of "$BOOTSTRAP_USER" sudo || die "Bootstrap $BOOTSTRAP_USER skal have sudo-gruppemedlemskab"
    [[ $(passwd -S "$BOOTSTRAP_USER" | awk '{print $2}') == P ]] || die 'Bootstrap skal have et brugbart lokalt password og vaere testet i konsollen'
    if [[ -n ${SUDO_USER:-} && $SUDO_USER != "$BOOTSTRAP_USER" && $SUDO_USER != root ]]; then
        die "Koer fra $BOOTSTRAP_USER, ikke $SUDO_USER. Bevar den begraensede adminrolle."
    fi
    for u in "$ADMIN_USER" "$DEVELOPER_USER" "$GUEST_USER"; do
        if entry=$(getent passwd "$u"); then
            grep -q "^$u:" /etc/passwd || die "Kun lokale konti understottes: $u"
            uid=$(cut -d: -f3 <<< "$entry"); home=$(cut -d: -f6 <<< "$entry")
            [[ $uid -ge 1000 && $home == "/home/$u" && ! -L $home ]] || die "Uventet eksisterende konto/hjemmemappe: $u"
            for group in docker lxd disk shadow wheel admin; do
                if member_of "$u" "$group"; then die "$u har risikabel ekstra gruppe $group; afklar manuelt"; fi
            done
            if [[ $u != "$ADMIN_USER" ]]; then
                for group in sudo admins adm systemd-journal securebase; do
                    if member_of "$u" "$group"; then die "$u har uventet privilegeret gruppe: $group"; fi
                done
            fi
        fi
    done
    for group in admins developers guests securebase "$ADMIN_USER" "$DEVELOPER_USER" "$GUEST_USER"; do
        if entry=$(getent group "$group"); then
            [[ $(cut -d: -f3 <<< "$entry") -ge 1000 ]] || die "Uventet system-GID for $group"
        fi
    done
    if members=$(getent group admins); then
        members=${members##*:}
        [[ -z $members || $members == "$ADMIN_USER" ]] || die 'admins indeholder andre konti; gennemgaa gruppevalget'
    fi
    [[ ! -L $PROJECT_DIR ]] || die 'Projektmappen maa ikke vaere et symlink'
    for file in setup.sh healthcheck.sh monitor.sh; do
        [[ -s $SCRIPT_DIR/$file ]] || die "Tom eller manglende projektfil: $file"
        bash -n "$SCRIPT_DIR/$file"
    done
    for file in "$SCRIPT_DIR"/modules/*.sh "$SCRIPT_DIR"/lib/*.sh; do bash -n "$file"; done
    if [[ -n $(find "$REPO_DIR" -type l -print -quit) ]]; then die 'Pakken indeholder symlinks; brug den originale udpakkede pakke'; fi
    if [[ -n $(find "$REPO_DIR" -perm /022 -print -quit) ]]; then die 'Pakke/mappe er gruppe- eller world-writable; ret rettigheder foer sudo-koersel'; fi
    ok 'Bash-syntaks godkendt; bootstrap bevares' 
    if command -v ufw >/dev/null; then
        check_ufw_rules || die 'Eksisterende UFW-regler passer ikke til den snævre SSH-politik. Ingen regler slettet.'
        ok 'Ingen modstridende brugeroprettede UFW-regler'
    fi
    if [[ -f /etc/ssh/sshd_config ]]; then
        grep -Eiq '^[[:space:]]*Include[[:space:]]+/etc/ssh/sshd_config.d/\*.conf' /etc/ssh/sshd_config || die 'sshd_config mangler standard Include; afklar manuelt foer deployment'
        if grep -Ei '^[[:space:]]*Match[[:space:]]' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null; then
            die 'Eksisterende Match-regler kraever manuel vurdering; pakken antager standard SSH-konfiguration'
        fi
    fi
    for cmd in docker.service containerd.service nftables.service firewalld.service; do
        if systemctl is-active --quiet "$cmd"; then die "Aktiv $cmd: separat firewall-integration er uden for dette labsetup"; fi
    done
    if [[ $CONFIGURE_NETWORK == yes ]]; then
        need netplan
        python3 "$SCRIPT_DIR/tools/netplan_scope.py" "$INTERFACE"
        [[ $NETWORK_APPLY != try || $ACTION == check || -t 0 ]] || die 'netplan try kraever interaktiv konsol'
        warn 'Netvaerk er tilvalgt: kun single-NIC Netplan-konfiguration er understottet'
    else info 'Eksisterende netvaerk bevares (CONFIGURE_NETWORK=no)'; fi
    for cmd in sshd ufw setfacl logrotate cron; do
        if command -v "$cmd" >/dev/null; then ok "$cmd findes"; else info "$cmd installeres ved --apply"; fi
    done
    warn 'Et gyldigt public-key-format beviser ikke, at klienten har den private noegle; SSH-test er stadig noedvendig.'
}
