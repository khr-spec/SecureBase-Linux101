# Modul 6 — scripts, kommentarer og kørsel

[Overblik](../README.md) · [Modul 6-dokumentation](../docs/06-scripting.md) · [Deploymentvejledning](../docs/DEPLOYMENT.md)

Denne mappe er den komplette scriptleverance til Modul 6. **Alle 18 scriptfiler har en kommentar ved toppen, som forklarer formål og hvordan filen anvendes.** De filer, der er interne moduler eller biblioteker, skal ikke køres direkte; deres dokumenterede kørsel er gennem `scripts/setup.sh`.

## Direkte indgange

| Fil | Formål | Sådan køres den |
|---|---|---|
| `scripts/setup.sh` | Orkestrerer preflight og deployment. | `sudo bash scripts/setup.sh --check` og efter gennemgang `sudo bash scripts/setup.sh --apply --console-confirmed` |
| `scripts/healthcheck.sh` | Selvstændig, læsende slutkontrol. | `sudo bash scripts/healthcheck.sh` eller installeret `sudo /usr/local/sbin/securebase-healthcheck` |
| `scripts/monitor.sh` | Ressourcemåling, thresholds og journal-warning. | Test: `bash scripts/monitor.sh --sample` og `bash scripts/monitor.sh --self-test`. Normal drift køres automatisk af cron efter installation. |
| `scripts/tools/evidence.sh` | Valgfrit læsende konfigurationsmanifest. | `sudo bash scripts/tools/evidence.sh \| tee securebase-evidence.txt` |

## Interne deploymentmoduler

Disse filer **sources af `scripts/setup.sh` og køres ikke enkeltvis**. Det sikrer, at de får valideret konfiguration, arbejdsmappe, fejlhåndtering og den rigtige rækkefølge fra orkestratoren.

| Fil | Funktion | Kørsel |
|---|---|---|
| `scripts/modules/00-preflight.sh` | Platform-, config-, konto- og konfliktkontrol. | Automatisk via `scripts/setup.sh --check` og før `--apply`. |
| `scripts/modules/01-system.sh` | Pakker, hostname og administreret `/etc/hosts`-linje. | Automatisk via `scripts/setup.sh --apply --console-confirmed`. |
| `scripts/modules/02-network.sh` | Single-NIC Netplan; anvendes til sidst. | Automatisk via setup, kun når `CONFIGURE_NETWORK="yes"`. |
| `scripts/modules/03-users.sh` | Rollegrupper, konti og medlemskaber. | Automatisk via setup. |
| `scripts/modules/04-storage-acl.sh` | `/srv/securebase`, SGID og access/default ACL. | Automatisk via setup. |
| `scripts/modules/05-ssh.sh` | Public key, ekstern key-test og SSH-hardening. | Automatisk via setup; kræver den dokumenterede `KEY-OK`-bekræftelse. |
| `scripts/modules/06-sudo.sh` | Tre præcise sudo-regler og negativ kontrol. | Automatisk via setup. |
| `scripts/modules/07-firewall.sh` | UFW default deny og kildebegrænset SSH. | Automatisk via setup. |
| `scripts/modules/08-monitoring.sh` | Installerer monitor, cron, logrotate og services. | Automatisk via setup. |

## Fælles bibliotek og valideringsværktøjer

| Fil | Formål | Kørsel |
|---|---|---|
| `scripts/lib/common.sh` | Fælles config-parser, status, backup og idempotent filinstallation. | Køres ikke direkte; `source`-indlæses af `scripts/setup.sh`. |
| `scripts/tools/validate_config.py` | Validerer literal `config.env` og Ed25519-public key. | Automatisk i preflight. Manuel kontrol: `python3 scripts/tools/validate_config.py config.env .` |
| `scripts/tools/netplan_scope.py` | Afviser netværksmodeller uden for den understøttede single-NIC-model. | Automatisk i preflight/netværksmodulet. Manuel læsekontrol: `python3 scripts/tools/netplan_scope.py enp0s3` |
| `scripts/tools/check_sudo_listing.py` | Kontrollerer at admin kun har de tre forventede sudo-kommandoer. | Automatisk fra sudo-modulet med `sudo -l` på stdin. |

## Historisk script

| Fil | Formål | Kørsel |
|---|---|---|
| `scripts/history/monitor-modul5.sh` | Bevarer den tidligere `top`/`free`-baserede Modul 5-monitor som historik. | Kun syntakskontrol anbefales: `bash -n scripts/history/monitor-modul5.sh`. Den installeres ikke af Modul 6. |

## Eksempel: healthcheck på færdigt system

Det fulde observerede resultat er dokumenteret i [Modul 6](../docs/06-scripting.md) og VM-beviserne. Den afsluttende kørsel gav **19 OK / 1 WARN / 0 FAIL**. WARN er den kendte `who`/utmp-observation; `systemd-logind` viste sessionerne.

```text
── 4 / UID 0-audit ──
  UID 0-konti: root
  [OK]   Kun root har UID 0 i den tilgaengelige NSS-opslagning

── 5 / SSH og administratorrolle ──
  [OK]   SSH service/socket aktiv
  [OK]   permitrootlogin no
  [OK]   passwordauthentication no
  [OK]   kbdinteractiveauthentication no
  [OK]   pubkeyauthentication yes
  [OK]   authenticationmethods publickey
  [OK]   Admin er ikke i sudo-gruppen

── 6 / Monitorering og rotation ──
  [OK]   cron.service aktiv
  [OK]   logrotate.timer aktiv
  [OK]   Forventet cron-job findes
  [OK]   Logrotate-regel findes
  [OK]   Monitorlog indeholder en frisk maaling
  [OK]   Seneste ressourcestatus OK

── RESULTAT ──
19 OK   1 WARN   0 FAIL
RESULTAT: WARN - gennemgaa bemaerkningerne
```

Healthchecket er læsende. Exitkode `1` betyder her WARN, ikke at deploymentet fejlede; exitkode `2` bruges ved registreret FAIL.
