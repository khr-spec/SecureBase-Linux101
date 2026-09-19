# Evidence — Modul 6

[Til dokumentationen](../../docs/06-scripting.md) · [Samlet evidensoversigt](../README.md)

Modulet har nu **34 billedbeviser**: de 18 oprindelige Word-figurer nedenfor og [16 nye v1.2-screenshots fra 18. september 2026](v1.2-2026-09-18/README.md). De to forløb har hver sit kildeindeks og omdateres ikke.

## Aktuel v1.2-test

Se [nye billeder og deres beskrivelser](v1.2-2026-09-18/README.md), [kildehash](v1.2-2026-09-18/index.json) og [VM-testrapporten](../../docs/VM_TEST_REPORT.md). Første apply rapporterer 12 ændrede administrerede filer; anden apply 0; begge healthchecks 19 OK / 1 WARN / 0 FAIL.

<a id="historiske-figurer"></a>

## Historiske figurer — 17. september 2026

Billederne nedenfor er udtrukket fra den samlede Word-rapport. De viser de oprindelige terminalresultater, ikke v1.2-kørslen. Eventuelle udsnit fremgår af billedteksterne.

| Figur | Indhold |
|---|---|
| [6.1](figur-6-01.png) | Arkivet hentes med HTTP 200, gemmes med 38.017 bytes og udpakkes. Mappen indeholder blandt andet setup.sh, healthcheck.sh, config.env, keys og modules. (Udsnit af terminal-screenshot.) |
| [6.2](figur-6-02.png) | Første preflight godkender konfiguration og nøgle. sshd og setfacl skal installeres ved apply; CONFIGURE_NETWORK=no bevarer netværket i denne første plan. |
| [6.3](figur-6-03.png) | Den anvendte config.env: netværksopsætning er tilvalgt, NETWORK_APPLY=try, og administratorrollen har NOPASSWD kun til de definerede driftskommandoer. |
| [6.4](figur-6-04.png) | Anden preflight viser Netplan: yes og godkender scope som ét networkd-interface. Pakker, konfiguration og public key er kontrolleret før apply. |
| [6.5](figur-6-05.png) | Første apply starter med godkendt preflight og går videre til pakkeopdatering. Ubuntu-arkiverne kontaktes før den øvrige konfiguration. |
| [6.6](figur-6-06.png) | Første kørsel opretter roller og brugere, konfigurerer ACL og installerer authorized_keys. Derefter stopper scriptet ved den planlagte eksterne SSH-test. (Udsnit af terminal-screenshot.) |
| [6.7](figur-6-07.png) | Efterkontrollen viser enp0s3 med 10.0.2.15/24, default route via 10.0.2.2 med proto static samt den genererede YAML med DHCP slået fra. |
| [6.8](figur-6-08.png) | Første apply afsluttes med 12 ændrede administrerede filer og healthcheck-resultatet 19 OK, 1 WARN, 0 FAIL. Log- og backupplacering oplyses. (Udsnit af terminal-screenshot.) |
| [6.9](figur-6-09.png) | Selvstændigt healthcheck: aktiv UFW, kildebegrænset SSH-regel, ca. 20G ledig diskplads, sessionsoplysninger og kun root med UID 0 i NSS-opslaget. |
| [6.10](figur-6-10.png) | Samme selvstændige kontrol viser SSH-hærdning, admin uden sudo-gruppemedlemskab, de tre NOPASSWD-regler samt aktiv cron/logrotate og en frisk monitor-linje. Resultat: 19 OK, 1 WARN, 0 FAIL. |
| [6.11](figur-6-11.png) | Anden apply: ingen pakker opgraderes eller installeres, /etc/hosts er uændret, grupperne findes, og de eksisterende konti bevares. |
| [6.12](figur-6-12.png) | Projekt-ACL er allerede korrekt; authorized_keys, SSH-konfiguration og sudoers er uændrede. KEY-OK er indtastet ved sikkerhedsstoppet, og sudo-politikken er de tre forventede kommandoer. (Udsnit af terminal-screenshot.) |
| [6.13](figur-6-13.png) | UFW-kildereglen findes allerede; kun TCP/22 fra 10.0.2.2 står som eksplicit brugerregel. Monitor-script og monitor.conf er uændrede. (Udsnit af terminal-screenshot.) |
| [6.14](figur-6-14.png) | Cronfilen er uændret; cron, logrotate og rsyslog er aktive. En ny monitor-måling tilføjes uden at slette loghistorik. (Udsnit af terminal-screenshot.) |
| [6.15](figur-6-15.png) | Netplan er allerede konfigureret og genindlæses ikke. Den installerede healthcheck og dens konfiguration er også uændrede. (Udsnit af terminal-screenshot.) |
| [6.16](figur-6-16.png) | Anden kørsel afsluttes med 19 OK, 1 WARN, 0 FAIL og Aendrede administrerede filer i denne koersel: 0. En ny deployment-log er oprettet; førstegangsbackups bevares. (Udsnit af terminal-screenshot.) |
| [6.17](figur-6-17.png) | Windows opretter en ny ssh -p 2222-forbindelse. Login lykkes på Ubuntu 26.04.1 LTS efter den anden apply-kørsel. |
| [6.18](figur-6-18.png) | Sidste direkte kontrol: whoami viser secureadmin, hostname viser securebase-server, og sudo -l viser kun de tre specifikke NOPASSWD-kommandoer. |
