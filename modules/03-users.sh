#!/bin/bash
ensure_group() {
    if getent group "$1" >/dev/null; then
        [[ $(getent group "$1" | cut -d: -f3) -ge 1000 ]] || die "Rolle-/brugergruppe $1 har system-GID; afklar manuelt"
        ok "Gruppe findes: $1"
    else groupadd "$1"; ok "Gruppe oprettet: $1"; fi
}
ensure_user() {
    local u=$1
    if getent passwd "$u" >/dev/null; then ok "Konto bevaret: $u (eksisterende password aendres ikke)"
    else
        # Et laast password er IKKE det samme som udloeb af kontoen.
        # Ubuntu/OpenSSH med UsePAM=yes valideres efterfolgende via ekstern key-test.
        ensure_group "$u"
        useradd --create-home --gid "$u" --shell /bin/bash "$u"
        passwd -l "$u" >/dev/null
        chmod 0750 "/home/$u"
        ok "Konto oprettet: $u, intet brugbart lokalt password"
    fi
}
users_setup() {
    local group
    for group in admins developers guests securebase; do ensure_group "$group"; done
    ensure_user "$ADMIN_USER"; ensure_user "$DEVELOPER_USER"; ensure_user "$GUEST_USER"
    add_member "$ADMIN_USER" admins; add_member "$ADMIN_USER" securebase
    add_member "$BOOTSTRAP_USER" securebase
    add_member "$DEVELOPER_USER" developers; add_member "$GUEST_USER" guests
    if [[ $ADMIN_SUDO_NOPASSWD == no ]]; then
        [[ $(passwd -S "$ADMIN_USER" | awk '{print $2}') == P ]] || die 'PASSWD-sudo kraever lokalt admin-password. Saet det med passwd; aldrig i config.env.'
    fi
    info 'Ingen brugere eller grupper slettes; bootstrap-kontoens sudo bevares.'
}
