# SecureBase — Linux 101

**Ubuntu Server · sikker fjernadgang · rollebaseret administration · reproducerbart Bash-deployment**

SecureBase dokumenterer, hvordan en Linux-server blev opbygget, sikret og overvåget manuelt i seks moduler, og derefter genskabt på en separat Ubuntu Server 26.04.1-test-VM. Repoet er både aflevering og teknisk overdragelse til den næste administrator.

## Dokumentation

| Modul | Indhold | Beviser |
|---|---|---|
| [01 · VM og netværk](docs/01-vm-netvaerk.md) | Statisk IP, hostname og nøglebaseret SSH | [4 figurer](evidence/01-vm-netvaerk/README.md) |
| [02 · Filsystem og adgang](docs/02-filsystem.md) | Permissions, SGID og midlertidig ACL | [3 figurer](evidence/02-filsystem/README.md) |
| [03 · Brugere og grupper](docs/03-brugere-grupper.md) | Roller, projektadgang og begrænset sudo | [17 figurer](evidence/03-brugere-grupper/README.md) |
| [04 · Firewall](docs/04-firewall.md) | UFW, kildebegrænsning og HTTP-før/efter-test | [19 figurer](evidence/04-firewall/README.md) |
| [05 · Monitorering](docs/05-monitorering.md) | Cron, logrotation, loginanalyse og grænseværdier | [26 figurer](evidence/05-monitorering/README.md) |
| [06 · Scripting](docs/06-scripting.md) | Fresh deployment, healthcheck og idempotens | [18 historiske](evidence/06-scripting/README.md#historiske-figurer) + [16 nye v1.2-beviser](evidence/06-scripting/v1.2-2026-09-18/README.md) |

[Samlet Word-rapport](reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx) · [Evidensgrundlag](evidence/README.md) · [Visuel startside](START_HER.html)

## Sådan køres scripts

Læs først [deploymentvejledningen](docs/DEPLOYMENT.md). Brug en understøttet Ubuntu-test-VM, et snapshot og den eksisterende bootstrap-konto med fungerende lokal sudo. Kør fra **repo-roden**:

```bash
# Opret kun den lokale konfiguration, hvis den ikke allerede findes.
cp -n config/config.env.example config.env
nano config.env
sudo bash scripts/setup.sh --check
# Kun efter gennemgang af preflight og testet konsoladgang:
sudo bash scripts/setup.sh --apply --console-confirmed
sudo bash scripts/healthcheck.sh
```

Netværksændringer er fravalgt som standard. Sæt kun `CONFIGURE_NETWORK="yes"` efter kontrol af interface/IP/gateway. Din egen public key placeres i `keys/secureadmin.pub`; den private nøgle skal blive på klienten. Pakken administrerer hele `authorized_keys` for admin-kontoen.

## Dokumenteret teststatus

**Repo 1.2 er afprøvet på en frisk Ubuntu Server 26.04.1 / VirtualBox NAT den 18. september 2026**, med deployment fra `scripts/` og tilvalgt statisk netværk. Git-reference fra arbejdsforløbet: `54734b9`.

| Kontrol | Observeret resultat |
|---|---|
| Preflight | `scripts/setup.sh --check` accepterer den valgte konfiguration |
| Første deployment | **12 ændrede administrerede filer** |
| Anden fulde kørsel | **0 ændrede administrerede filer**; Netplan genindlæses ikke |
| Healthcheck kaldt af setup | **19 OK / 1 WARN / 0 FAIL** i begge kørsler |
| SSH-adgang | Login fra Windows virker ved sikkerhedsstop; effektiv konfiguration kræver public key |
| Afsluttende adminrolle | `secureadmin` på `securebase-server`, tre eksakte `NOPASSWD`-kommandoer |

WARN skyldes tomt `who`/utmp-output, mens systemd-logind viser sessioner. Resultatet er ikke omskrevet til PASS. Slutbilledet viser identitet/sudo; det daterede SSH-login er fra under anden kørsel.

Se [aktuel VM-testrapport](docs/VM_TEST_REPORT.md), [16 nye screenshots](evidence/06-scripting/v1.2-2026-09-18/README.md), [historisk test fra 17. september](docs/VM_TEST_REPORT_2026-09-17.md) og [lokale strukturtests](docs/RESTRUCTURE_TEST_REPORT.md).

De oprindelige **87 Word-figurer er bevaret**; der er nu **103 billedbeviser i alt**. Word-rapporten under `reports/` er den uændrede historiske rapport. Det nye v1.2-tillæg læses i Markdown og evidence. Denne opdatering ændrer ikke deployment-scripts eller konfigurationsstandarder.

## Struktur

```text
docs/       Én fil pr. modul samt deployment- og testvejledninger
evidence/   Originale dokumentationsfigurer fordelt på moduler
scripts/    Setup, healthcheck, monitor, moduler og hjælpefunktioner
config/     Versioneret skabelon; config.env i roden er lokal og ignoreret
keys/       Offentlig SSH-nøgle — aldrig privat nøgle
tests/      Isolerede kode-, sti- og repositorytests
tools/      Repo-migration og checksumværktøj
reports/    Den oprindelige samlede Word-rapport
```

## Vedligeholdelse og aflevering

[Opdatér det eksisterende Git-repo uden ny historik](docs/MIGRERING.md) · [Regressionstestplan](docs/TESTPLAN.md) · [Kilder og versionsafgrænsning](docs/GRUNDLAG.md)

Repoets privatlivsindstilling ændres ikke af disse filer. Del det private repo gennem eksplicit GitHub-adgang. Udviklingshistorikken bevares; der fremstilles ikke bagudrettede commits for de tidligere moduler.
