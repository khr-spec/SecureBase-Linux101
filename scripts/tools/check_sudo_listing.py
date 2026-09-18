#!/usr/bin/env python3
"""Fail closed, hvis sudo -l viser andre admin-kommandoer end de tre valgte."""
# KØRSEL: Kaldes automatisk af scripts/modules/06-sudo.sh med output fra `sudo -l` på stdin.
# MANUEL TEST: sudo -l -U secureadmin | python3 scripts/tools/check_sudo_listing.py

import re, sys
EXPECTED={
    '/usr/sbin/sshd -t',
    '/usr/bin/systemctl reload ssh.service',
    '/usr/bin/journalctl --no-pager -u ssh.service -n 30',
}
def check(text):
    entries=[]; current=None
    for line in text.splitlines():
        match=re.match(r'^\s*\(([^)]+)\)\s+(.*)$',line)
        if match:
            current=[match[1], match[2].strip()]; entries.append(current)
        elif current and line.startswith('        ') and line.strip():
            # Sudo kan ombryde lange kommandoer. Saml fortsættelsen før sammenligning.
            current[1]+=' '+line.strip()
    found=set()
    for runas, commands in entries:
        if runas.replace(' ','') not in ('root','root:root'):
            raise ValueError('Anden run-as end root: '+runas)
        for command in commands.split(','):
            command=re.sub(r'^(?:NOPASSWD:|PASSWD:)\s*','',command.strip())
            if command not in EXPECTED: raise ValueError('Uventet sudo-tilladelse: '+command)
            found.add(command)
    if found!=EXPECTED: raise ValueError('De tre forventede sudo-tilladelser kunne ikke bekræftes')
    return True
if __name__=='__main__':
    try:
        check(sys.stdin.read()); print('Sudo-politik: præcis de tre forventede driftskommandoer')
    except ValueError as e:
        print('SUDO POLICY ERROR:', e, file=sys.stderr); sys.exit(1)
