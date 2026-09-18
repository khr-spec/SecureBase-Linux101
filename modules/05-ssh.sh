#!/bin/bash
ssh_effective_ok() {
    local config=$1 field value actual
    /usr/sbin/sshd -T -f "$config" > "$WORK/sshd.effective" || return 1
    while read -r field value; do
        actual=$(awk -v f="$field" '$1==f {$1=""; sub(/^ /,""); print}' "$WORK/sshd.effective")
        [[ $actual == "$value" ]] || { printf 'SSH afvigelse: %s=%s (forventet %s)\n' "$field" "$actual" "$value" >&2; return 1; }
    done <<'EOF'
permitrootlogin no
passwordauthentication no
kbdinteractiveauthentication no
pubkeyauthentication yes
authenticationmethods publickey
permitemptypasswords no
usepam yes
port 22
authorizedkeysfile .ssh/authorized_keys
EOF
}
ssh_setup() {
    local home="/home/$ADMIN_USER" dest=/etc/ssh/sshd_config.d/00-securebase.conf existed=no
    [[ ! -L $home/.ssh ]] || die 'Admin .ssh maa ikke vaere symlink'
    install -d -m 0700 -o "$ADMIN_USER" -g "$ADMIN_USER" "$home/.ssh"
    tr -d '\r' < "$SCRIPT_DIR/$SSH_PUBLIC_KEY_FILE" | awk 'NF {print}' > "$WORK/authorized_keys"
    ssh-keygen -lf "$WORK/authorized_keys"
    warn "Deployment ejer HELE $home/.ssh/authorized_keys; andre noegler erstattes efter backup."
    install_managed "$WORK/authorized_keys" "$home/.ssh/authorized_keys" 0600 "$ADMIN_USER" "$ADMIN_USER"
    # Hostnoegler er serveridentitet: generer kun manglende, genbrug aldrig kopier.
    ssh-keygen -A
    install -d -m 0755 /run/sshd /etc/ssh/sshd_config.d
    ensure_service ssh.service
    if [[ $KEY_CONFIRMED != yes ]]; then
        section 'SIKKERHEDSSTOP / test en NY SSH-session fra Windows'
        printf '  ssh -o PasswordAuthentication=no -p 2222 %s@127.0.0.1\n' "$ADMIN_USER"
        info 'Brug eksisterende public-key-par og kontroller whoami. Ret hostport ved behov.'
        info 'Dette er en administrativ bekraeftelse, ikke en automatisk test fra serveren.'
        local reply
        read -r -p '  Skriv KEY-OK naar login virker (ellers Enter for at stoppe): ' reply
        [[ $reply == KEY-OK ]] || die 'Stop foer hardening. Public key er installeret; behold konsoladgangen.'
    fi
    cat > "$WORK/ssh.conf" <<'EOF'
# Managed by SecureBase. Public key installeres foer hardening.
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
PermitEmptyPasswords no
UsePAM yes
AuthorizedKeysFile .ssh/authorized_keys
Port 22
EOF
    # Kandidat valideres FOER installation; derefter checkes den faktiske include-raekkefoelge.
    cat "$WORK/ssh.conf" > "$WORK/sshd.candidate"
    printf '\nInclude /etc/ssh/sshd_config\n' >> "$WORK/sshd.candidate"
    /usr/sbin/sshd -t -f "$WORK/sshd.candidate"
    [[ ! -f $dest ]] || { cp -p "$dest" "$WORK/ssh.previous"; existed=yes; }
    install_managed "$WORK/ssh.conf" "$dest" 0644
    local changed=$CHANGED
    if ! /usr/sbin/sshd -t || ! ssh_effective_ok /etc/ssh/sshd_config; then
        if [[ $existed == yes ]]; then cp -p "$WORK/ssh.previous" "$dest"; else rm -f "$dest"; fi
        die 'SSH-konflikt: fil gendannet, ingen reload af fejlagtig konfiguration. Gennemgaa andre SSH-filer.'
    fi
    if [[ $changed == 1 ]]; then systemctl reload ssh.service; fi
    ok 'SSH effective config: root/password afvist, publickey paakraevet'
}
