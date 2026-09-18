# VM-testrapport — SecureBase 1.2

[Overblik](../README.md) · [Modul 6 med billeder](06-scripting.md#vm-test-v12) · [Evidensindeks](../evidence/06-scripting/v1.2-2026-09-18/README.md) · [Historisk test 17. september](VM_TEST_REPORT_2026-09-17.md)

**Testdato:** 18. september 2026  
**Platform:** frisk Ubuntu Server 26.04.1 LTS test-VM · Oracle VirtualBox NAT  
**Kodestruktur:** repo 1.2.0, programmer under `scripts/`  
**Git-reference:** `54734b9` fra det dokumenterede commit-/arkivforløb  
**Bootstrap:** `vboxuser` med lokal sudo  
**Admin:** `secureadmin`, public-key SSH og tre afgrænsede `NOPASSWD`-kommandoer

## Resultat

| Kontrol | Observeret resultat | Direkte bevis |
|---|---|---|
| Før-tilstand | Hostname Ubuntu-Server1 og default route med proto dhcp | [V12-01](../evidence/06-scripting/v1.2-2026-09-18/01-foer-hostname-dhcp.png) |
| Overførsel og nye stier | ZIP hentes med HTTP 200; scripts/, config/ og dokumentation findes | [V12-02](../evidence/06-scripting/v1.2-2026-09-18/02-hentet-git-arkiv.png), [V12-03](../evidence/06-scripting/v1.2-2026-09-18/03-udpakket-repostruktur.png) |
| Preflight | scripts/setup.sh --check accepterer input, public key og Netplan-scope | [V12-05](../evidence/06-scripting/v1.2-2026-09-18/05-preflight-scripts-sti.png) |
| Første apply | Roller, ACL, nøgle og SSH etableres; **12 ændrede administrerede filer** ved afslutningen | [V12-07](../evidence/06-scripting/v1.2-2026-09-18/07-foerste-apply-roller-noegle.png), [V12-09](../evidence/06-scripting/v1.2-2026-09-18/09-foerste-apply-resultat.png) |
| SSH-bootstrap | Vellykket Windows-login med PasswordAuthentication=no på klienten | [V12-08](../evidence/06-scripting/v1.2-2026-09-18/08-ssh-ved-bootstrap.png) |
| Netplan | 10.0.2.15/24; default via 10.0.2.2 med proto static; DNS i YAML | [V12-10](../evidence/06-scripting/v1.2-2026-09-18/10-netplan-sluttilstand.png) |
| Gentagen apply | Kendte konti og regler bevares; **0 ændrede administrerede filer** | [V12-11](../evidence/06-scripting/v1.2-2026-09-18/11-genkoersel-roller-noegle.png), [V12-15](../evidence/06-scripting/v1.2-2026-09-18/15-genkoersel-nul-aendringer.png) |
| Healthcheck i setup | **19 OK / 1 WARN / 0 FAIL** i begge kørsler | [V12-09](../evidence/06-scripting/v1.2-2026-09-18/09-foerste-apply-resultat.png), [V12-14](../evidence/06-scripting/v1.2-2026-09-18/14-genkoersel-netplan-healthcheck.png), [V12-15](../evidence/06-scripting/v1.2-2026-09-18/15-genkoersel-nul-aendringer.png) |
| SSH under genkørsel | Ny forbindelse lykkes ved anden kørsels sikkerhedsstop | [V12-12](../evidence/06-scripting/v1.2-2026-09-18/12-ssh-under-genkoersel.png) |
| Afsluttende sessionskontrol | secureadmin; securebase-server; kun tre forventede sudo-kommandoer | [V12-16](../evidence/06-scripting/v1.2-2026-09-18/16-afsluttende-identitet-sudo.png) |

## Konfiguration under testen

```conf
BOOTSTRAP_USER="vboxuser"
ADMIN_USER="secureadmin"
SSH_PORT="22"
SSH_ALLOWED_SOURCE="10.0.2.2"
ADMIN_SUDO_NOPASSWD="yes"
UPDATE_SYSTEM="yes"
CONFIGURE_NETWORK="yes"
INTERFACE="enp0s3"
STATIC_IP="10.0.2.15/24"
GATEWAY="10.0.2.2"
DNS1="10.0.2.3"
DNS2="1.1.1.1"
NETWORK_APPLY="try"
DISK_THRESHOLD="85"
MEMORY_THRESHOLD="90"
MONITOR_INTERVAL="5"
LOGROTATE_KEEP="7"
```

Dette er et uddrag af den viste lokale konfiguration, ikke en ændring af skabelonens sikre standard `CONFIGURE_NETWORK="no"`. Konfigurationsbilledet er [V12-04](../evidence/06-scripting/v1.2-2026-09-18/04-valgt-labkonfiguration.png); preflight og netværkskontrollen dokumenterer den efterfølgende anvendelse. Projektmappens gruppe-/others-skriverettigheder blev fjernet efter ZIP-udpakning før sudo-kørsel. Kildekoden blev ikke rettet for at skrive denne rapport.

## Kørsler og tidsangivelser

De tidsstempler, som fremgår direkte af terminalmaterialet, bruger UTC/Z:

| Hændelse | Vist tidspunkt eller reference |
|---|---|
| ZIP-download | 2026-09-18 08:46:33 UTC; 6.340.751 bytes |
| SSH ved første sikkerhedsstop | 2026-09-18 09:07:52 UTC |
| Monitorlinje i første slutoutput | 2026-09-18T09:10:02Z |
| SSH ved anden kørsels stop | 2026-09-18 09:14:25 UTC |
| Healthcheck/monitor i anden afslutning | 2026-09-18T09:14:38Z |

Første deployment oplyser logstien `/var/log/securebase/deploy-20260918T090157Z-7715.log`; anden kørsel oplyser `/var/log/securebase/deploy-20260918T091339Z-15312.log`. Stierne er aflæst fra screenshots. Der er ikke vedlagt konstruerede eller fuldstændige tekstkopier af disse serverlogs.

## Healthcheckets ene WARN

```text
[WARN] who viser ingen utmp-login; dette beviser ikke fravaer af SSH-sessioner
```

`systemd-logind` viser samtidig vboxuser- og secureadmin-sessioner i [V12-14](../evidence/06-scripting/v1.2-2026-09-18/14-genkoersel-netplan-healthcheck.png). Advarslen er derfor dokumenteret som begrænsning i utmp-visningen, ikke skjult eller omdøbt til PASS. De øvrige viste kontroller omfatter aktiv UFW, disk under 85 %, kun root med UID 0 i opslaget, SSH-hærdning og aktiv monitorering.

## Idempotens

```text
[OK] Aendrede administrerede filer i denne koersel: 0
```

Anden fulde apply genkendte den ønskede tilstand. Både unchanged-filer, eksisterende UFW-regel, allerede korrekt ACL og Netplan uden genindlæsning ses i materialet. En ny monitorlinje og deploymentlog er forventede driftsdata. Ændringstælleren er ikke en hash-sammenligning af hele operativsystemet.

## SSH og administratorrolle

Adgangsvejen er `127.0.0.1:2222 → 10.0.2.15:22`. SSH-porten inde i Ubuntu er fortsat 22. Healthcheck viser `permitrootlogin no`, `passwordauthentication no`, `kbdinteractiveauthentication no`, `pubkeyauthentication yes` og `authenticationmethods publickey`.

Den afsluttende sessionskontrol viser kun:

```text
(root) NOPASSWD: /usr/sbin/sshd -t
(root) NOPASSWD: /usr/bin/systemctl reload ssh.service
(root) NOPASSWD: /usr/bin/journalctl --no-pager -u ssh.service -n 30
```

## Bevisernes rækkevidde

- Git-revisionen er reference fra det oplyste arbejdsforløb; ZIP-udgaven på VM'en indeholder ikke `.git`. En uafhængig commit-/arkivhash-kontrol er ikke vist.
- Det selvstændige healthcheck-program er kørt af setup i v1.2-testen. En separat manuel start i dette nye forløb er ikke vist.
- SSH-billedet kl. 09:14:25 er fra **under** anden apply. Den efterfølgende identitetskontrol viser ikke sin egen forbindelseskommando. Den kaldes derfor ikke et selvstændigt billede af et nyt login efter afslutningen.
- Der er ikke dokumenteret fuld genstart, `evidence.sh`-manifestdiff, andre netværksmodeller eller samtlige supplerende rolle-/alarmtests på den nye VM.
- De oprindelige 87 Word-figurer bevares. De 16 nye v1.2-screenshots er et særskilt, dateret tillæg, ikke omskrevne historiske beviser.

**Konklusion:** Den gamle afgrænsning om, at 1.2 kun er testet lokalt, er erstattet af en faktisk fresh-install- og genkørselstest af `scripts/`-strukturen. Resultatet er gennemført deployment med den beskrevne WARN — ikke en fuld sikkerhedscertificering.
