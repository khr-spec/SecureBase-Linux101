#!/bin/bash
# FORMÅL: Konfigurerer /srv/securebase med root:securebase, SGID samt access/default ACL.
# KØRSEL: Køres ikke direkte. Sources af scripts/setup.sh og kaldes som storage_setup() ved --apply.
# DIREKTE: Nej. Eksisterende projektfiler omskrives ikke rekursivt.

storage_setup() {
    [[ ! -L $PROJECT_DIR ]] || die 'Projektmappen er symlink'
    mkdir -p "$PROJECT_DIR"
    if [[ $(stat -c '%U:%G:%a' "$PROJECT_DIR") != root:securebase:2770 ]]; then
        chown root:securebase "$PROJECT_DIR"; chmod 2770 "$PROJECT_DIR"
    fi
    # Erstat KUN ACL paa projektroden. Ingen rekursiv omskrivning af brugerdata.
    cat > "$WORK/project.acl" <<'EOF'
user::rwx
group::rwx
group:developers:rwx
group:guests:r-x
mask::rwx
other::---
default:user::rwx
default:group::rwx
default:group:developers:rwx
default:group:guests:r-x
default:mask::rwx
default:other::---
EOF
    getfacl -cp "$PROJECT_DIR" | sed '/^$/d' > "$WORK/project.old-acl"
    if cmp -s "$WORK/project.old-acl" "$WORK/project.acl"; then ok 'Projekt-ACL allerede korrekt'
    else
        getfacl -p "$PROJECT_DIR" > "$WORK/project.before"
        if [[ ! -f /var/backups/securebase/project-before.acl ]]; then install -m 0600 "$WORK/project.before" /var/backups/securebase/project-before.acl; fi
        setfacl --set-file="$WORK/project.acl" "$PROJECT_DIR"
        ok 'Mappe-ACL og default ACL konfigureret'
    fi
    info 'Eksisterende filer bevares. Default ACL gaelder nyoprettede objekter, ikke automatisk gamle filer.'
}
