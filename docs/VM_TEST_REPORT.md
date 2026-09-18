# Historisk VM-test — SecureBase-deployment

**Testdato:** 17. september 2026  
**Platform:** Oracle VirtualBox · frisk Ubuntu Server 26.04.1 LTS VM  
**Netværk:** VirtualBox NAT · `enp0s3` · statisk `10.0.2.15/24` · gateway `10.0.2.2`  
**Bootstrap-konto:** `vboxuser` med lokal sudo  
**Daglig administrator:** `secureadmin` med public-key SSH og tre afgrænsede sudo-kommandoer

> VM-testen vedrører den oprindelige 1.0-kode, senere dokumenteret i 1.1. Repo-omstruktureringen til 1.2 er lokalt testet separat. Det er ikke en ny fresh-install-kørsel.

## Gennemført

- Arkivet blev overført til en frisk VM uden eksisterende SecureBase-konfiguration.
- `sudo bash ./setup.sh --check` bestod preflight.
- `CONFIGURE_NETWORK="yes"` blev anvendt i den faktiske fresh-install test.
- Første `--apply --console-confirmed` etablerede brugere/grupper, ACL, OpenSSH/public key, SSH-hardening, sudoers, UFW, monitoring, cron, logrotate og Netplan.
- Ny key-only SSH-session fra Windows blev verificeret før/efter hærdning via VirtualBox-portforward.
- Netplan-sluttilstanden blev kontrolleret med `ip -br a`, `ip route` og `/etc/netplan/99-securebase.yaml`.
- `healthcheck.sh` på den færdige server gav **19 OK, 1 WARN, 0 FAIL**.
- WARN skyldtes, at `who`/utmp ikke viste sessionerne, mens systemd-logind gjorde; den blev derfor bevaret som observationsadvarsel.
- Deploymentet blev kørt igen med samme ønskede tilstand. Brugere/grupper blev bevaret, managed configs var uændrede, UFW-reglen fandtes allerede, Netplan krævede ingen genindlæsning, og outputtet viste **0 ændrede administrerede filer**.
- Healthcheck bestod igen med **19 OK, 1 WARN, 0 FAIL**.
- Afsluttende Windows SSH-login virkede som `secureadmin@securebase-server`.
- `sudo -l` viste kun de tre forventede driftskommandoer for `secureadmin`; den brede sudo-gruppe var ikke en del af den daglige adminrolle.

## SSH / VirtualBox

Serverens SSH-service bruger fortsat guest-port **22**. VirtualBox videresender i labbet `127.0.0.1:2222` på Windows til `10.0.2.15:22` i Ubuntu. Dette er et bevidst designvalg: ikke-standard SSH-port på selve Ubuntu er valgfri hardening/støjreduktion og var ikke nødvendig for Linux 101-kravene.

## Idempotensbevis

Den vigtigste observerede slutlinje på anden kørsel var:

```text
[OK] Ændrede administrerede filer i denne kørsel: 0
```

Idempotens betyder her, at den deklarerede SecureBase-konfiguration ikke blev duplikeret eller unødvendigt omskrevet ved samme input. Driftslogs og pakkearkiver kan naturligt ændre sig over tid.

## Afleveringsbevis

De faktiske screenshots findes nu i [evidence/06-scripting](../evidence/06-scripting/README.md) og i den [samlede Word-rapport](../reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx). Denne fil er en tekstlig statusopsummering og erstatter ikke screenshotsene.
