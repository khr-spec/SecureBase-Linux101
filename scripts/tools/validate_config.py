#!/usr/bin/env python3
"""Valider literal config og Ed25519-public key. Ingen systemaendringer."""
# KØRSEL: Kaldes automatisk af preflight med config og repo-rod som argumenter.
# EKSEMPEL: python3 scripts/tools/validate_config.py config.env .

import base64, hashlib, ipaddress, re, struct, sys
from pathlib import Path

def read_config(path):
    result = {}
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'): continue
        m = re.fullmatch(r'([A-Z][A-Z0-9_]*)="([a-zA-Z0-9_./,:@%+ -]*)"', line)
        if not m: raise ValueError(f'Config linje {n}: kun literal KEY="vaerdi"')
        if m[1] in result: raise ValueError(f'Dobbelt noegle: {m[1]}')
        result[m[1]] = m[2]
    return result

def validate(config_path, root):
    c = read_config(config_path)
    for key in ('BOOTSTRAP_USER','ADMIN_USER','DEVELOPER_USER','GUEST_USER'):
        if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,30}', c[key]) or c[key]=='root':
            raise ValueError(f'Ugyldigt brugernavn: {key}')
    if len({c[k] for k in ('BOOTSTRAP_USER','ADMIN_USER','DEVELOPER_USER','GUEST_USER')}) != 4:
        raise ValueError('De fire konti skal vaere forskellige')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',c['HOSTNAME']):
        raise ValueError('Brug et simpelt lowercase hostname uden domaene')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,15}',c['INTERFACE']): raise ValueError('Ugyldigt interface')
    for key in ('UPDATE_SYSTEM','CONFIGURE_NETWORK','ADMIN_SUDO_NOPASSWD'):
        if c[key] not in ('yes','no'): raise ValueError(f'{key}: brug yes eller no')
    if c['NETWORK_APPLY'] not in ('try','apply'): raise ValueError('NETWORK_APPLY: try eller apply')
    if c['SSH_PORT'] != '22': raise ValueError('Version 1 understoetter guest SSH-port 22; hostport er separat')
    addr = ipaddress.IPv4Interface(c['STATIC_IP'])
    gateway = ipaddress.IPv4Address(c['GATEWAY'])
    if gateway not in addr.network or gateway == addr.ip: raise ValueError('Gateway matcher ikke subnet')
    if addr.ip in (addr.network.network_address,addr.network.broadcast_address): raise ValueError('Ugyldig hostadresse')
    for key in ('DNS1','DNS2'): ipaddress.ip_address(c[key])
    source=ipaddress.ip_network(c['SSH_ALLOWED_SOURCE'],strict=False)
    if source.version != 4 or source.prefixlen == 0: raise ValueError('SSH source skal vaere et afgraenset IPv4-net/IP')
    if '/' in c['SSH_ALLOWED_SOURCE'] and str(source)!=c['SSH_ALLOWED_SOURCE']:
        raise ValueError('Brug netadressen i CIDR, fx 10.0.2.0/24, ikke hostbits i subnettet')
    for key in ('DISK_THRESHOLD','MEMORY_THRESHOLD'):
        if not c[key].isdigit() or not 1 <= int(c[key]) <= 100: raise ValueError(f'Ugyldig {key}')
    for key in ('DISK_THRESHOLD','MEMORY_THRESHOLD','MONITOR_INTERVAL','LOGROTATE_KEEP'):
        if not c[key].isdigit() or str(int(c[key]))!=c[key]: raise ValueError(f'{key}: brug heltal uden foranstillede nuller')
    interval=int(c['MONITOR_INTERVAL'])
    if interval not in (1,2,3,4,5,6,10,12,15,20,30): raise ValueError('Interval skal dele 60 og vaere mellem 1 og 30')
    if not 1 <= int(c['LOGROTATE_KEEP']) <= 90: raise ValueError('LOGROTATE_KEEP: 1-90')
    if not re.fullmatch(r'/srv/[a-zA-Z0-9_-]+',c['PROJECT_DIR']): raise ValueError('PROJECT_DIR skal vaere /srv/<navn>')
    rel=Path(c['SSH_PUBLIC_KEY_FILE'])
    if rel.is_absolute() or '..' in rel.parts or rel.suffix != '.pub': raise ValueError('Public key skal vaere en relativ .pub-fil')
    key_path=Path(root)/rel
    if key_path.is_symlink(): raise ValueError('Public key maa ikke vaere symlink')
    lines=[l.strip() for l in key_path.read_text().splitlines() if l.strip()]
    if len(lines)!=1: raise ValueError('Version 1 forventer praecis en public key')
    fields=lines[0].split()
    if len(fields)<2 or fields[0]!='ssh-ed25519': raise ValueError('Forventer ssh-ed25519 public key; aldrig privat noegle')
    blob=base64.b64decode(fields[1],validate=True)
    offset=0; pieces=[]
    for _ in range(2):
        if offset+4>len(blob): raise ValueError('Afkortet SSH-noegle')
        n=struct.unpack('>I',blob[offset:offset+4])[0]; offset+=4
        pieces.append(blob[offset:offset+n]); offset+=n
    if offset!=len(blob) or pieces[0]!=b'ssh-ed25519' or len(pieces[1])!=32:
        raise ValueError('Ugyldigt Ed25519-noegleformat')
    fp=base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')
    print('Public key fingerprint: SHA256:'+fp)
    return c
if __name__=='__main__':
    try: validate(sys.argv[1],sys.argv[2])
    except (ValueError,KeyError,IndexError,OSError) as e:
        print('CONFIG ERROR:',e,file=sys.stderr); sys.exit(1)
