# Evidence — Modul 1

[Til dokumentationen](../../docs/01-vm-netvaerk.md) · [Samlet evidensoversigt](../README.md)

Billederne er udtrukket fra den samlede Word-rapport. De viser de oprindelige terminalresultater; de er ikke nye kørsler af den omstrukturerede kode. Eventuelle udsnit fremgår af billedteksterne.

| Figur | Indhold |
|---|---|
| [1.1](figur-1-01.png) | Terminaloutput med accepteret Netplan-konfiguration, statisk IP, routing, ping-tests og hostname securebase-server. |
| [1.2](figur-1-02.png) | Verifikation af secureadmin, sudo-adgang, aktiv ssh.service, lyttende port 22 og UFW-status. |
| [1.3](figur-1-03.png) | PowerShell-bevis: password-only login afvises med “Permission denied (publickey)”, mens et normalt SSH-login umiddelbart efter lykkes som secureadmin. |
| [1.4](figur-1-04.png) | Effektiv sshd-konfiguration: root-login og password-login er deaktiveret, mens public key er påkrævet. |
