# Deployment — SecureBase 1.3.2

[Overblik](../README.md) · [Modul 6 og VM-beviser](06-scripting.md) · [Testplan](TESTPLAN.md)

Programmerne ligger under `scripts/`; lokal `config.env` og `keys/` ligger i repo-roden. Det verificerede servergrundlag og dets begrænsninger fremgår af [VM-testrapporten](VM_TEST_REPORT.md).

## 1. Forudsætninger og ansvar

Målplatformen er Ubuntu Server 26.04.x i en bootet systemd-installation med internet, Python 3 og iproute2. Ved netværksændring understøttes den enkle single-NIC Netplan/networkd-model. Flere interfaces, bridges/VLAN, visse eksisterende privilegerede grupper eller konkurrerende firewalltjenester kræver manuel vurdering og kan stoppe preflight.

Bootstrap-kontoen skal allerede eksistere, have fungerende lokalt password og være medlem af sudo. Skabelonen bruger vboxuser. secureadmin, developer1 og guest1 oprettes ved behov. Bootstrap-kontoens rettigheder og password ændres ikke af opsætningen.

**Brug en test-VM, et snapshot og den lokale VirtualBox-konsol før apply.** Et script kørt som root er betroet kode. --console-confirmed er din bekræftelse på en afprøvet vej tilbage, ikke en automatisk kontrol af konsollen.

## 2. Adgangsvej og offentlig nøgle

| Felt | Værdi i det dokumenterede lab |
|---|---|
| VirtualBox | Adapter 1 = almindelig NAT |
| Host IP / port | 127.0.0.1 / 2222 |
| Guest IP / port | 10.0.2.15 / 22 |
| SSH-kilde set af Ubuntu | 10.0.2.2 |

Forwarding konfigureres på Windows-værten, ikke inde i Ubuntu. Kører den gamle VM samtidig med samme hostport, bruges eksempelvis 2223 til test-VM'en; ret SSH-klientkommandoen tilsvarende. Guest-porten er stadig 22.

keys/secureadmin.pub indeholder den **offentlige** Ed25519-nøgle anvendt i labbet. Udskift den med den ønskede administrators public key før et nyt deployment. Den private nøgle må aldrig lægges i repoet eller overføres til serveren.

Setup administrerer hele admin-kontoens authorized_keys. Eksisterende indhold sikkerhedskopieres første gang og kan blive erstattet. Det er ikke automatisk multi-key-rotation. Serverens egne hostnøgler er en anden kategori; eksisterende hostidentitet bevares.

## 3. Hent og udpak uden eksisterende SSH

Websitets downloadsektion tilbyder en komplet kildepakke uden `.git` eller lokal `config.env`. På en frisk Ubuntu-konsol med internet kan den hentes uden eksisterende SSH:

```bash
wget https://khr-spec.github.io/SecureBase-Linux101/downloads/SecureBase-1.3.2.zip
# Installer unzip, hvis det ikke allerede findes:
sudo apt-get update
sudo apt-get install -y unzip
unzip SecureBase-1.3.2.zip
cd SecureBase-Linux101
sha256sum -c SHA256SUMS
```

Kildearkivet indeholder ikke `.git` eller lokal `config.env`. De dokumenterede VM-tests anvendte HTTP-overførsel fra Windows; HTTPS-downloaden ovenfor er vejledning til nye installationer.

Med Git installeret kan projektet også hentes som et klon:

```bash
git clone https://github.com/khr-spec/SecureBase-Linux101.git
cd SecureBase-Linux101
```

### Rettigheder efter udpakning

Preflight kræver, at kode og projektmappe ikke kan ændres af gruppe/andre. I den **udpakkede repo-rod** kan det kontrolleres og om nødvendigt rettes med:

```bash
pwd
chmod -R go-w .
```

Kør ikke denne rettelse fra `/` eller fra hjemmemappens rod. Brug `bash scripts/setup.sh`, så start ikke afhænger af et bevaret executable-bit. En checksum i pakken er integritetskontrol, ikke en uafhængig digital signatur.

## 4. Gennemgå konfigurationen

Fra repo-roden:

```bash
# Bevar en allerede eksisterende lokal konfiguration.
cp -n config/config.env.example config.env
nano config.env
```

config.env er bevidst ignoreret af Git og udeladt af SHA256SUMS. Skabelonen bruger literal KEY="værdi"; den bliver ikke udført med source. Ukendte/dobbelte nøgler og ugyldige værdier afvises.

| Felt | Standard / forklaring |
|---|---|
| HOSTNAME | securebase-server |
| BOOTSTRAP_USER / ADMIN_USER | vboxuser / secureadmin |
| DEVELOPER_USER / GUEST_USER | developer1 / guest1 |
| PROJECT_DIR | /srv/securebase |
| SSH_PUBLIC_KEY_FILE | keys/secureadmin.pub, relativt til repo-roden |
| SSH_PORT / SSH_ALLOWED_SOURCE | 22 / 10.0.2.2 |
| ADMIN_SUDO_NOPASSWD | yes, kun de tre konkrete SSH-kommandoer |
| UPDATE_SYSTEM | yes; apt-get update og upgrade, ikke automatisk reboot |
| CONFIGURE_NETWORK | no som sikker standard |
| INTERFACE / STATIC_IP | enp0s3 / 10.0.2.15/24 |
| GATEWAY / DNS1 / DNS2 | 10.0.2.2 / 10.0.2.3 / 1.1.1.1 |
| NETWORK_APPLY | try, kræver bekræftelse i den oprindelige konsol |
| DISK_THRESHOLD / MEMORY_THRESHOLD | 85 / 90 |
| MONITOR_INTERVAL / LOGROTATE_KEEP | 5 minutter / 7 rotationer |

Den dokumenterede fresh-install-test brugte CONFIGURE_NETWORK="yes". Vælg det kun efter at have kontrolleret netværksværdierne. Netplan køres til sidst i setup; start ikke en konkurrerende netplan try i en anden session.

## 5. Preflight, installation og sikkerhedsstop

Som bootstrap-kontoen i konsollen:

```bash
sudo bash scripts/setup.sh --check
# Først efter vurdering af planen:
sudo bash scripts/setup.sh --apply --console-confirmed
```

--check ændrer ikke systemkonfigurationen, men er ikke en fuld dry-run. Apply opdaterer pakker, kontrollerer og konfigurerer roller, ACL, SSH, sudo, UFW og monitorering og kan til sidst migrere det understøttede netværk.

Ved KEY-OK-stoppet testes fra Windows i et nyt terminalvindue:

```powershell
ssh -o PasswordAuthentication=no -p 2222 secureadmin@127.0.0.1
```

Kør whoami i SSH-sessionen. Bekræft først KEY-OK i deployment-konsollen, når nøglen faktisk virker. Ved netplan try: kontrollér ny adgang og bekræft i **den samme oprindelige konsol**.

Eksisterende vboxuser-adgang bevares. secureadmin får kun:

```sudoers
%admins ALL=(root) NOPASSWD: /usr/sbin/sshd -t
%admins ALL=(root) NOPASSWD: /usr/bin/systemctl reload ssh.service
%admins ALL=(root) NOPASSWD: /usr/bin/journalctl --no-pager -u ssh.service -n 30
```

Ingen NOPASSWD: ALL. Eksisterende passwords ændres ikke. ADMIN_SUDO_NOPASSWD="no" kræver et allerede brugbart lokalt adminpassword.

## 6. Kontrol og genkørsel

```bash
sudo bash scripts/healthcheck.sh
# Selvstændig installeret udgave:
sudo /usr/local/sbin/securebase-healthcheck
```

Returkode 0 = PASS, 1 = WARN, 2 = FAIL. Både den historiske test og v1.2-testen viste én who/utmp-advarsel og 0 FAIL. I den nye test er healthcheck-outputtet vist som del af setup; en separat manuel kørsel er ikke vist. Gennemgå altid en ny advarsel; antag ikke, at den er identisk med den gamle.

Genkørsel på samme VM og samme input:

```bash
sudo bash scripts/setup.sh --apply --console-confirmed
```

En mere præcis, supplerende regression kan sammenligne konfigurationsmanifestet:

```bash
sudo bash scripts/tools/evidence.sh | tee ~/securebase-before.txt
sudo bash scripts/setup.sh --apply --console-confirmed
sudo bash scripts/tools/evidence.sh | tee ~/securebase-after.txt
diff -u ~/securebase-before.txt ~/securebase-after.txt
```

Denne manifestdiff er en foreslået test, ikke en påstået historisk VM-kørsel. Logs og målinger ændres normalt; pakkeversioner er ikke pinned. Idempotens gælder den ønskede konfiguration, ikke en bit-identisk disk.

## 7. Monitor og efterprøvning

```bash
# Læsende måling uden logskrivning eller journal-warning:
bash scripts/monitor.sh --sample
# Isoleret kontrol af grænseværdier:
bash scripts/monitor.sh --self-test
```

Den aktive monitor bruger `/proc/stat`-delta over cirka ét sekund, `MemAvailable` fra `/proc/meminfo` og `df` på `/`. Den tidligere `top`/`free`-version er kun historisk dokumentation og installeres ikke. Se [testplanen](TESTPLAN.md) for den samlede efterprøvning.

## 8. Backup og afgrænsning

Fejlstop er ikke en fuld transaktion. Tidligere moduler kan være udført, hvis et senere trin fejler. Førstegangsbackups findes under /var/backups/securebase/before-first-change. Deploymentlogs ligger under /var/log/securebase og har ikke automatisk samme syv rotationer som monitorloggen.

UFW bevarer sine indbyggede regler og accepterer kun den specificerede SSH-brugerregel; ukendte regler stoppes til manuel vurdering. Eksisterende projektfiler omskrives ikke rekursivt. Logrotate gælder monitorloggen, ikke en ny størrelsespolitik for hele journalen.

[Aktuelle v1.2-VM-resultater](VM_TEST_REPORT.md), [historisk VM-test](VM_TEST_REPORT_2026-09-17.md) beskriver gennemførte kørsler. [Testplanen](TESTPLAN.md) bruges ved efterfølgende ændringer.
