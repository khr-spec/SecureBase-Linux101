# SecureBase · Linux 101

## [Åbn den visuelle aflevering →](https://khr-spec.github.io/SecureBase-Linux101/)

**Seks moduler. Én dokumenteret server. Fra manuel opsætning til reproducerbart deployment.**

Afleveringen kan læses direkte på GitHub Pages: alle moduler, 103 screenshots, VM-verifikation og download af den samlede Word-rapport. Dette repo indeholder kildekoden og den Markdown-dokumentation, som websitet bygges fra.

| Dokumentation | Fokus |
|---|---|
| [01 · VM og netværk](docs/01-vm-netvaerk.md) | Ubuntu Server, statisk IP og nøglebaseret SSH |
| [02 · Filsystem og adgang](docs/02-filsystem.md) | Filrettigheder, SGID og midlertidig ACL |
| [03 · Brugere og grupper](docs/03-brugere-grupper.md) | Adskilte roller og begrænset sudo |
| [04 · Firewall](docs/04-firewall.md) | Default deny, kildebegrænsning og HTTP-test |
| [05 · Monitorering](docs/05-monitorering.md) | Cron, logrotation, loginanalyse og thresholds |
| [06 · Shell og Bash](docs/06-scripting.md) | Fresh-install-test, healthcheck og idempotens |

## Verificeret servergrundlag

Ubuntu Server 26.04.1 LTS blev testet i VirtualBox den **18. september 2026** med deployment-koden fra 1.2. Første apply rapporterede **12 ændrede administrerede filer**, anden apply **0**. Healthcheck kaldt af setup viste **19 OK / 1 WARN / 0 FAIL**. Advarslen vedrører `who`/utmp; logind viste sessionerne. Det er en vurderet WARN, ikke et ubetinget PASS.

**1.3.0 er en afleverings- og websiteudgave.** Filerne under `scripts/`, konfigurationsskabelonen og public key er byte-identiske med den afprøvede 1.2-kode. De oprindelige VM-beviser er ikke omdateret eller præsenteret som en ny 1.3-serverinstallation. [Testgrundlag](docs/VM_TEST_REPORT.md) · [Versionsafgrænsning](docs/GRUNDLAG.md).

## Deployment

Læs [deploymentvejledningen](docs/DEPLOYMENT.md) først. Brug en understøttet test-VM, lokal bootstrap-/sudo-adgang og et snapshot. Tilpas `config.env` og **udskift eksempel-public-key med din egen** før apply.

```bash
# Fra repo-roden; overskriv ikke en eksisterende lokal konfiguration.
cp -n config/config.env.example config.env
nano config.env
sudo bash scripts/setup.sh --check
# Først efter kontrolleret konsoladgang og gennemgang af planen:
sudo bash scripts/setup.sh --apply --console-confirmed
sudo bash scripts/healthcheck.sh
```

Public-key-testen og en eventuel Netplan-test bekræftes i den oprindelige konsol. Ingen privat nøgle, password eller lokal `config.env` skal i Git. Bootstrap-kontoen bevarer fuld sudo; den daglige admin får kun tre eksakte SSH-driftskommandoer.

## Kilder, drift og beviser

[VM-testrapport](docs/VM_TEST_REPORT.md) · [Regressionstestplan](docs/TESTPLAN.md) · [103 billedbeviser](evidence/README.md) · [Word-rapport](reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx) · [Tekniske kilder](docs/SOURCES.md)

Word-rapporten er den uændrede historiske rapport på 87 sider fra 17. september. Verifikationen fra 18. september står i Modul 6, VM-testrapporten og de 16 supplerende billeder.

## Repository

```text
docs/       Faglig dokumentation og vejledninger — websitets indholdskilde
evidence/   87 oprindelige figurer + 16 supplerende v1.2-beviser
scripts/    Den testede Bash-deployment, monitor og healthcheck
config/     Versioneret skabelon; config.env oprettes lokalt
keys/       Eksempel på offentlig SSH-nøgle — ingen private nøgler
reports/    Samlet historisk Word-rapport
tests/      Isolerede kode-, dokumentations- og websitetests
site/       Layout, CSS og JavaScript — ikke en kopi af moduldokumentationen
tools/      Websitebygning, checksums og publiceringskontrol
```

## Website og vedligeholdelse

GitHub Actions bygger alle sider fra Markdown og publicerer kun det genererede `_site/`. Dokumentationsændringer og nye screenshots kommer dermed med på websitet ved næste push. `START_HER.html` henviser til den publicerede aflevering.

Brug et isoleret Python-miljø som beskrevet i websitevejledningen. Derefter:

```bash
python -m pip install -r requirements-site.txt
python tools/build_site.py
python tools/check_site.py
python -m http.server 8000 --directory _site
```

[Websitevejledning](docs/WEBSITE.md) · [Publicering og privatliv](docs/PUBLICERING.md) · [Lokale testresultater](docs/TESTRESULTATER.md) · [Ændringslog](CHANGELOG.md)
