# SecureBase · Linux 101

## [Åbn den visuelle aflevering →](https://khr-spec.github.io/SecureBase-Linux101/)

**Kasper · Ubuntu Server 26.04.1 LTS · Modul 1–6**

SecureBase dokumenterer en Linux-server fra manuel grundopsætning til reproducerbart deployment. Projektet omfatter nøglebaseret SSH, rollebaseret adgang, firewall, monitorering og Bash-automatisering.

## Dokumentation

| Modul | Indhold |
|---|---|
| [01 · VM og netværk](docs/01-vm-netvaerk.md) | Ubuntu Server, statisk IP og nøglebaseret SSH |
| [02 · Filsystem og adgang](docs/02-filsystem.md) | Filrettigheder, SGID og midlertidig ACL |
| [03 · Brugere og grupper](docs/03-brugere-grupper.md) | Adskilte roller og begrænset sudo |
| [04 · Firewall](docs/04-firewall.md) | Default deny, kildebegrænsning og HTTP-test |
| [05 · Monitorering](docs/05-monitorering.md) | Cron, logrotation, loginanalyse og grænseværdier |
| [06 · Shell og Bash](docs/06-scripting.md) | Scripts, kørselsvejledning, healthcheck og idempotens |

## Verificeret resultat

Deploymentet blev afprøvet på en frisk Ubuntu Server-VM den **18. september 2026**. Første kørsel rapporterede **12 ændrede administrerede filer**; genkørslen rapporterede **0**. Healthcheck viste **19 OK / 1 WARN / 0 FAIL**. Advarslen skyldes tomt `who`/utmp-output; `systemd-logind` viste de aktive sessioner.

[VM-testrapport](docs/VM_TEST_REPORT.md) · [103 billedbeviser](evidence/README.md) · [Samlet Word-rapport](reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx)

## Kørsel

Læs [deploymentvejledningen](docs/DEPLOYMENT.md) først. Brug en understøttet test-VM, lokal bootstrap-/sudo-adgang og et snapshot. Tilpas konfigurationen og den offentlige SSH-nøgle før installation.

```bash
# Fra repo-roden. Bevar en eksisterende lokal konfiguration.
cp -n config/config.env.example config.env
nano config.env
sudo bash scripts/setup.sh --check
# Først efter gennemgang af planen og kontrol af konsoladgang:
sudo bash scripts/setup.sh --apply --console-confirmed
sudo bash scripts/healthcheck.sh
```

[Scriptvejledningen](scripts/README.md) beskriver formål og kørsel for **alle 18 scripts**. Interne moduler køres gennem `setup.sh`, ikke enkeltvis. Private nøgler og lokal `config.env` hører ikke til i Git.

## Videre drift og efterprøvning

[Testplan](docs/TESTPLAN.md) · [Kilde- og testgrundlag](docs/GRUNDLAG.md) · [Tekniske referencer](docs/SOURCES.md) · [Ændringslog](CHANGELOG.md)

Version **1.3.2** samler den redigerede dokumentation; deploymentlogikken er uændret fra det verificerede servergrundlag.
