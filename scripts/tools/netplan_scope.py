#!/usr/bin/env python3
"""Fail closed ved komplekst netvaerk. Læser kun; ingen filsletning her."""
import pathlib, subprocess, sys

def check(data, interface):
    net=data.get('network',data)
    if set(net)-{'version','renderer','ethernets'}:
        raise ValueError('Bridges, Wi-Fi, VLAN og andre nettyper haandteres ikke automatisk')
    if net.get('renderer','networkd')!='networkd': raise ValueError('Forventer networkd')
    eths=net.get('ethernets',{})
    if set(eths)!={interface}: raise ValueError(f'Forventer praecis et netkort med YAML-ID {interface}')
    e=eths[interface]
    allowed={'dhcp4','dhcp6','addresses','nameservers','routes','gateway4','gateway6','match','set-name','optional','link-local','accept-ra','renderer'}
    if set(e)-allowed: raise ValueError('Ukendte interface-egenskaber: '+str(set(e)-allowed))
    if e.get('renderer','networkd')!='networkd': raise ValueError('Forventer networkd paa interfacet')
    if e.get('set-name',interface)!=interface: raise ValueError('Andet set-name kraever manuel vurdering')
    return True
if __name__=='__main__':
    try:
        import yaml
        for d in ('/run/netplan','/lib/netplan'):
            if list(pathlib.Path(d).glob('*.yaml')):
                raise ValueError('Ekstern Netplan-konfiguration i '+d)
        for p in pathlib.Path('/etc/netplan').glob('*.yaml'):
            if p.is_symlink(): raise ValueError('Netplan-symlink afvises: '+str(p))
        out=subprocess.check_output(['netplan','get'],text=True)
        check(yaml.safe_load(out) or {},sys.argv[1])
        print('Netplan scope OK: enkelt networkd-interface')
    except (ValueError,ImportError,subprocess.SubprocessError,IndexError) as e:
        print('NETPLAN SCOPE ERROR:',e,file=sys.stderr); sys.exit(1)
