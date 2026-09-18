#!/bin/bash
sudo_setup() {
    local tag='' dest=/etc/sudoers.d/securebase-admins existed=no
    [[ $ADMIN_SUDO_NOPASSWD != yes ]] || tag='NOPASSWD: '
    cat > "$WORK/sudoers" <<EOF
# Managed by SecureBase. Kun disse PRAECISE kommandoer som root.
%admins ALL=(root) ${tag}/usr/sbin/sshd -t
%admins ALL=(root) ${tag}/usr/bin/systemctl reload ssh.service
%admins ALL=(root) ${tag}/usr/bin/journalctl --no-pager -u ssh.service -n 30
EOF
    chmod 0440 "$WORK/sudoers"
    visudo -cf "$WORK/sudoers"
    [[ ! -f $dest ]] || { cp -p "$dest" "$WORK/sudo.previous"; existed=yes; }
    install_managed "$WORK/sudoers" "$dest" 0440
    if ! visudo -c; then
        if [[ $existed == yes ]]; then cp -p "$WORK/sudo.previous" "$dest"; else rm -f "$dest"; fi
        die 'Sudoers-konflikt; tidligere fil gendannet'
    fi
    if member_of "$ADMIN_USER" sudo; then gpasswd -d "$ADMIN_USER" sudo; fi
    # En faktisk uskadelig negativ test opdager bl.a. andre brede sudo-regler.
    if runuser -u "$ADMIN_USER" -- sudo -n /usr/bin/id > "$WORK/sudo-negative" 2>&1; then
        cat "$WORK/sudo-negative"; die 'Admin kan stadig koere id som root via en anden regel; afklar manuelt'
    fi
    if [[ $ADMIN_SUDO_NOPASSWD == yes ]]; then
        runuser -u "$ADMIN_USER" -- sudo -n /usr/sbin/sshd -t
    fi
    COLUMNS=1000 sudo -l -U "$ADMIN_USER" > "$WORK/sudo.final"
    cat "$WORK/sudo.final"
    python3 "$SCRIPT_DIR/tools/check_sudo_listing.py" < "$WORK/sudo.final"
    ok 'Admin begrænset. Bootstrap beholder fuld sudo. Gamle login-sessioner skal lukkes.'
}
