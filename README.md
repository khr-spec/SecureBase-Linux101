# SecureBase · Modul 6

**En modulopdelt Bash-deployment til Ubuntu Server 26.04.**

Pakken omsætter den sikre sluttilstand fra Modul 1–5 til genkørbare scripts. Den indeholder den offentlige Ed25519-nøgle, Kasper har leveret; ingen privat nøgle eller passwords. `setup.sh` konfigurerer, `healthcheck.sh` undersøger, og `monitor.sh` indsamler driftsdata.

> **Verificeret teststatus (17. september 2026):** Pakken er både lokalt enhedstestet og afprøvet end-to-end på en frisk Ubuntu Server 26.04.1 VM. Preflight, first-run deployment, statisk Netplan, key-only SSH, begrænset sudo, UFW, monitoring, healthcheck og en gentagen idempotens-kørsel er dokumenteret. Healthcheck gav **19 OK, 1 WARN, 0 FAIL**, og anden deployment-kørsel rapporterede **0 ændrede administrerede filer**. Se `docs/VM_TEST_REPORT.md`.

## 1. Hvad pakken indeholder

```text
securebase-deployment/
├── START_HER.html                Visuel startvejledning, åbnes i browseren
├── README.md                     Denne vejledning
├── VERSION
├── SHA256SUMS                    Integritetskontrol af pakkens filer
├── config.env                    Dine udfyldte labværdier
├── config.env.example            Skabelon med de samme sikre standarder
├── setup.sh                      Preflight, orkestrering og fejlhåndtering
├── healthcheck.sh                Selvstændig, læsende systemkontrol
├── monitor.sh                    CPU/RAM/disk, thresholds og journal-warning
├── keys/secureadmin.pub          KUN offentlig nøgle
├── lib/common.sh                 Fælles config-, fil- og statusfunktioner
├── modules/
│   ├── 00-preflight.sh           Forudsætninger og konflikter
│   ├── 01-system.sh              Opdatering, pakker og hostname
│   ├── 02-network.sh             Valgfri single-NIC Netplan, køres til sidst
│   ├── 03-users.sh               Brugere og rollegrupper
│   ├── 04-storage-acl.sh         Projektrod og standard-ACL
│   ├── 05-ssh.sh                 Nøgleinstallation og SSH-hærdning
│   ├── 06-sudo.sh                Tre specifikke adminrettigheder
│   ├── 07-firewall.sh            UFW med afgrænset SSH-adgang
│   └── 08-monitoring.sh          Monitor, cron, logrotation og services
├── tools/                       Validering og dokumentationsmanifest
├── tests/test_bundle.py          Isolerede enhedstests
└── docs/
    ├── TESTPLAN.md               Ubuntu-tests og screenshots til Modul 6
    ├── LOCAL_TEST_REPORT.txt     Faktisk lokalt testoutput – ikke VM-bevis
    ├── VM_TEST_REPORT.md        Verificeret fresh-install VM-teststatus
    └── SOURCES.md                Primære tekniske referencer
```

Nummeret på et modul er et filnavn, ikke en automatisk kørselsordre. `setup.sh` kalder funktionerne eksplicit. Netværket ændres sidst, så pakkeinstallation og nøgle-/firewallopsætning ikke afhænger af en halvfærdig netværksændring.

## 2. Support og forudsætninger

Målplatformen er **Ubuntu Server 26.04.x**, startet normalt med systemd, en lokal installationsbruger med fungerende sudo og internetadgang til Ubuntu-pakkearkiver. Standardværktøjerne Python 3 og iproute2 forventes at findes. Ved netværksautomatisering kræves Netplan/networkd med ét understøttet Ethernet-interface. Preflight stopper på en anden Ubuntu-version, flere Netplan-interfaces, bridges/VLAN, aktive konkurrerende firewall-/container-services eller uventede UFW-regler.

I den medfølgende konfiguration er installations-/gendannelseskontoen `vboxuser`. På en frisk VM skal denne konto enten oprettes under installationen, eller `BOOTSTRAP_USER` ændres til det faktiske navn. Den skal have et brugbart lokalt password og være medlem af `sudo`. Scriptet opretter **ikke** en skjult gendannelseskonto og ændrer ikke dens password.

Ubuntu-ISO-installation, Windows, VirtualBox og port forwarding er ikke en del af serverens Bash-script. Indstil separat på værten:

| Felt | SSH-forward |
|---|---|
| Netværkstype | NAT på Adapter 1 |
| Protokol | TCP |
| Host IP / port | `127.0.0.1` / `2222` |
| Guest IP / port | `10.0.2.15` / `22` |

På samme Windows-vært skal en separat test-VM bruge en anden hostport, eksempelvis 2223, hvis den gamle VM også kører. To almindelige, separate NAT-VM'er kan hver have guest-adressen 10.0.2.15. Ret klientkommandoens `-p` til den valgte hostport. Opsætningen gælder **almindelig NAT**, ikke nødvendigvis NAT Network eller Bridged.

## 3. Bootstrap og preflight

Arkivmappen hedder `securebase-deployment`. På en eksisterende SecureBase-VM kan arkivet overføres med SCP. På en helt frisk VM uden OpenSSH kan det i stedet hentes via en kortvarig, lokal HTTP-server på Windows gennem VirtualBox NAT; denne bootstrap-metode blev brugt i den verificerede fresh-install test.

### Metode A – eksisterende SSH / SCP

Download `SecureBase_Modul6.tar.gz` til Downloads og overfør arkivet til `secureadmin`:

```powershell
scp -P 2222 "$env:USERPROFILE\Downloads\SecureBase_Modul6.tar.gz" secureadmin@127.0.0.1:
```

`scp` bruger stort `-P` for porten. Kun arkivet overføres; din private nøgle bruges af SSH-klienten og kopieres ikke.

### Metode B – frisk VM uden SSH (verificeret bootstrap)

På Windows i mappen med arkivet:

```powershell
python -m http.server 8000 --bind 0.0.0.0
```

På Ubuntu-konsollen:

```bash
wget http://10.0.2.2:8000/SecureBase_Modul6.tar.gz
tar -xzf SecureBase_Modul6.tar.gz
cd securebase-deployment
```

Stop derefter den midlertidige Windows-server med `Ctrl+C`. `10.0.2.2` er VirtualBox NAT-host/gateway i det dokumenterede lab og skal ikke antages i andre miljøer.

### I VirtualBox-konsollen som bootstrap-brugeren

```bash
sudo install -o vboxuser -g vboxuser -m 0640 \
  /home/secureadmin/SecureBase_Modul6.tar.gz \
  /home/vboxuser/SecureBase_Modul6.tar.gz
cd /home/vboxuser
tar -xzf SecureBase_Modul6.tar.gz
cd securebase-deployment
sha256sum -c SHA256SUMS
sudo bash ./setup.sh --check
```

`--check` læser forudsætninger, validerer config/public key/Bash-syntaks og finder udvalgte konflikter. Det installerer ingen pakker og ændrer ingen systemkonfiguration. Det er **ikke** en fuld simulering af alle senere ændringer eller et bevis på, at en klient kan logge ind.

Tag screenshot af preflight-outputtet, og gennemgå det før næste trin. Kør ikke `--apply` alene for at se, hvad der sker.

## 4. Fresh deployment – kontrolleret fremgangsmåde

1. Installer Ubuntu Server 26.04 med netværk og en lokal bootstrap-konto med sudo. OpenSSH behøver ikke være installeret på forhånd; `setup.sh` installerer det. Overfør arkivet via SCP hvis SSH allerede findes, eller via en betroet lokal bootstrap-metode som den dokumenterede midlertidige HTTP-overførsel. Tag et snapshot **før** deployment.
2. Overfør og udpak hele pakken. Læs koden og konfigurationen; et root-kørt deployment er betroet kode.
3. Ret `config.env`. Kontrollér især bootstrap-konto, interface, IP/gateway og den SSH-kildeadresse serveren faktisk ser.
4. Kør preflight. Udfør først derefter deployment fra en lokal, testet konsol.

```bash
cd ~/securebase-deployment
nano config.env
sudo bash ./setup.sh --check
sudo bash ./setup.sh --apply --console-confirmed
```

`--console-confirmed` er din bekræftelse på, at lokal adgang og sudo fra bootstrap-kontoen faktisk er testet. Det er ikke automatisk gendannelse og gør ikke en forkert konfiguration sikker.

Under deployment installeres public key før SSH-hærdningen. Scriptet stopper ved en kort prompt. Åbn en **ny** Windows-session og test:

```powershell
ssh -o PasswordAuthentication=no -p 2222 secureadmin@127.0.0.1
```

Kontrollér `whoami`. Skriv først `KEY-OK` i deployment-konsollen, når den nye nøglebaserede forbindelse virker. En gyldig public key og `sshd -t` kan ikke bevise, at klienten har den tilsvarende private nøgle.

Ved senere, bevidst automatisering kan prompten springes over:

```bash
sudo bash ./setup.sh --apply --console-confirmed --key-login-confirmed
```

Dette flag er en administrativ erklæring om en allerede udført test – ikke en indbygget fjernlogin-test. Serveren kan ikke udføre din Windows-klients private nøgleoperation.

Efter deployment:

```bash
sudo bash ./healthcheck.sh
# Den installerede checker er uafhængig af projektmappen:
sudo /usr/local/sbin/securebase-healthcheck
```

Exitkode 0 betyder, at de viste kontroller består; 1 betyder advarsler; 2 betyder fejl. En advarsel om genstart eller en tom nyroteret log er ikke det samme som en syntaksfejl. Ingen af scriptsene genstarter VM'en automatisk.

## 5. Konfiguration og bevidste afgrænsninger

`config.env` bruger `KEY="literal"`. Parseren **sourcer ikke filen**, tillader ikke `$()`, backticks eller kommandoer og afviser ukendte/dobbelte nøgler. Gem aldrig passwords, API-tokens eller en privat SSH-nøgle her.

| Indstilling | Standard | Betydning |
|---|---|---|
| `HOSTNAME` | securebase-server | Servernavn; `/etc/hosts` tilpasses også |
| `BOOTSTRAP_USER` | vboxuser | Eksisterende lokal installationskonto; fuld sudo bevares |
| `ADMIN_USER` | secureadmin | Daglig, begrænset administrator |
| `DEVELOPER_USER` / `GUEST_USER` | developer1 / guest1 | Rollebaseret projektadgang |
| `PROJECT_DIR` | /srv/securebase | Mappe under `/srv`; ejerskab root:securebase |
| `SSH_PUBLIC_KEY_FILE` | keys/secureadmin.pub | Én public key i denne version |
| `SSH_ALLOWED_SOURCE` | 10.0.2.2 | NAT-kilde i det dokumenterede lab; også IPv4-CIDR muligt |
| `SSH_PORT` | 22 | Version 1 beholder guest-port 22; hostport 2222 er separat |
| `ADMIN_SUDO_NOPASSWD` | yes | Passwordfrihed kun for tre specifikke kommandoer |
| `UPDATE_SYSTEM` | yes | `apt-get update` + `apt-get upgrade -y` |
| `CONFIGURE_NETWORK` | no | Bevar netværket som sikker standard |
| `NETWORK_APPLY` | try | Interaktiv Netplan-test når netværk er tilvalgt |
| `DISK_THRESHOLD` / `MEMORY_THRESHOLD` | 85 / 90 | Advarsel ved større end eller lig med grænsen |
| `MONITOR_INTERVAL` | 5 | Cron på minut 00, 05, 10 osv. |
| `LOGROTATE_KEEP` | 7 | Antal gamle rotationer, ikke et garanteret antal døgn |

### Netværk på den friske VirtualBox-VM

For at lade deploymentet sætte den statiske IP, ændres:

```text
CONFIGURE_NETWORK="yes"
```

Kontrollér først `INTERFACE`, `STATIC_IP`, `GATEWAY` og DNS. Et enkelt interface med et andet navn kan anvendes ved at tilpasse `INTERFACE`; tidligere VM'ers MAC-adresser genbruges ikke.

Modulet validerer, at den eksisterende Netplan passer til den simple single-NIC-model. En kandidat valideres i en separat rodmappe. Eksisterende YAML-filer sikkerhedskopieres og migreres til én administreret fil, så flere Netplan-filers lister ikke utilsigtet kombineres. Cloud-inits netværksgenerering deaktiveres eksplicit, når Netplan overtages. `NETWORK_APPLY="try"` bruger `netplan try`; kontrollér forbindelsen og bekræft i konsollen. Der foretages efterfølgende IP-/routekontrol. Ved fejl forsøges gendannelse af denne kørsels tidligere filer.

`NETWORK_APPLY="apply"` er kun til et bevidst valgt, automatiseret labmiljø med fungerende konsoladgang. Netplan kan stadig fejle eller miste forbindelsen. Snapshot og konsol er sikkerhedsnettet; automatisk gendannelse er ikke en garanti. Denne version håndterer ikke flere interfaces, cloud netværksmodeller, bridges eller VLAN.

### Passwordfri SSH og sudo er to forskellige ting

**Dette er en bevidst ændring fra Modul 3:** På en frisk installation oprettes de nye konti uden brugbare lokale passwords. `secureadmin` skal derfor ikke mødes af en sudo-prompt for et password, der ikke er sat. De tre eksakte regler får `NOPASSWD:`:

```sudoers
%admins ALL=(root) NOPASSWD: /usr/sbin/sshd -t
%admins ALL=(root) NOPASSWD: /usr/bin/systemctl reload ssh.service
%admins ALL=(root) NOPASSWD: /usr/bin/journalctl --no-pager -u ssh.service -n 30
```

Der gives **ikke** `NOPASSWD: ALL`. `sudo id`, en fri root-shell, pakkeinstallation og firewallændringer tillades ikke af denne rolle. `vboxuser` beholder opsætningsrettighederne.

Eksisterende brugerpasswords ændres ikke. `ADMIN_SUDO_NOPASSWD="no"` kan bruges til den oprindelige passwordkrævende model, men da skal admin-kontoen allerede have et brugbart lokalt password; ellers stopper opsætningen. Ingen passwords skrives ind i projektet.

Kun admin fjernes fra den almindelige `sudo`-gruppe. Uventede privilegerede gruppemedlemskaber håndteres ikke ved tavs massesletning. Sudoers valideres, de faktiske admin-tilladelser sammenlignes med de tre tilladte kommandoer, og et ufarligt `sudo id`-forsøg skal afvises. Gamle login-sessioner kan beholde tidligere gruppelister; luk dem og log ind igen.

### Public key og servernøgler

Din public key er med som `keys/secureadmin.pub`, med fingerprint:

```text
SHA256:YbkaUZmrQBVRwTKYPv4SyJUG0+YHA2jlr3dzN1aV8lU
```

Din private nøgle `C:\Users\Kasper\.ssh\id_ed25519` bliver på Windows. Pakken ejer **hele** admin-kontoens `authorized_keys`: eksisterende indhold sikkerhedskopieres første gang og erstattes med pakkens ønskede public key. Det undgår dubletter, men betyder også, at andre admin-nøgler ikke bevares. Gennemgå dette før brug på en anden server. Multi-key/rotation med overlap er ikke implementeret i version 1.

SSH-serverens egne hostnøgler er en anden nøglekategori. `ssh-keygen -A` opretter kun manglende hostnøgler; eksisterende hostidentitet bevares, og pakken indeholder ingen host-private keys.

### UFW og projektfiler

UFW får den ene specificerede IPv4 SSH-regel, indgående default deny, udgående allow og forward deny. IPv6 behandles også af UFW, men får ingen åben SSH-undtagelse. Ukendte brugerregler medfører stop til manuel gennemgang; scriptet bruger aldrig `ufw reset`. UFWs indbyggede regler for blandt andet loopback, etablerede forbindelser og nødvendig ICMP bevares. `ufw status` er ikke en komplet audit af alle netfilter-/containerregler.

Projektroden får root:securebase, SGID/2770 og præcise access/default ACL'er for developers og guests. Eksisterende indhold omskrives **ikke rekursivt** og slettes ikke. På den eksisterende lab-VM bevares de fil-ACL'er, der allerede blev sat i Modul 3; på en frisk VM arver nye filer default ACL. Et eksisterende datasæt med andre filrettigheder kræver særskilt planlagt migration.

## 6. Monitor og healthcheck

Monitoren beholder logstien `/var/log/securebase-monitor.log`, root:adm/0640, thresholds, cron og logrotation fra forløbet, men forbedrer målingen:

* CPU beregnes fra to `/proc/stat`-aflæsninger med ét sekund mellem dem, på tværs af alle CPU'er. Idle og iowait regnes her ikke som CPU-busy. Det er ikke et femminutters gennemsnit.
* RAM beregnes som `(MemTotal - MemAvailable) / MemTotal`, så genanvendelig cache ikke forveksles med helt utilgængelig RAM.
* Disk måles på `/`; tidsstemplet er eksplicit UTC/ISO 8601.

Normal kørsel tilføjer én linje. Ved threshold-overskridelse tilføjes også en `user.warning` med tagget `securebase-monitor`. Ved scriptfejl forsøges en `user.err`. `flock` forhindrer overlappende monitor-kørsler. Der er ingen mail, SMS, fjern-SIEM eller alarm-dæmpning; en vedvarende overskridelse giver en warning ved hver måling.

```bash
# Ingen logskrivning eller journal-warning:
bash ./monitor.sh --sample
# Fem isolerede tests, inklusive >=-grænserne. Ingen systemændringer:
bash ./monitor.sh --self-test
# Faktiske driftsdata efter installation:
sudo tail -n 5 /var/log/securebase-monitor.log
sudo journalctl -t securebase-monitor --since "15 minutes ago" --no-pager
```

`healthcheck.sh` kan køres selvstændigt eller fra `/usr/local/sbin/securebase-healthcheck`. Den viser aktiv firewall, standardpolitik og SSH-regel; fri diskplads; `who` og systemd-logind-sessioner; proces-ejere særskilt; konti med UID 0 via NSS; SSH-konfiguration; admin-grupper; cron, logrotate og loggens friskhed. Den reparerer eller installerer intet. Fravær af `who`-output beviser ikke, at ingen er forbundet; derfor vises flere observationskilder.

## 7. Idempotens – design og verificeret resultat

Funktionerne kontrollerer grupper og medlemskaber før oprettelse. Administrerede filer sammenlignes før atomisk udskiftning; uændret indhold og metadata skrives ikke igen. Cronfilen og `authorized_keys` erstattes deterministisk frem for at få append-dubletter. UFW-reglen kontrolleres før tilføjelse. Den eksisterende monitor-log tømmes aldrig af setup, og gamle rotationer bevares.

En gentagen kørsel kan naturligt give nye driftsloglinjer, en ny deployment-log og senere pakkeopdateringer. Idempotens gælder den ønskede konfiguration med samme input, ikke stilstand i logs eller fastfrysning af Ubuntu-arkivet. Pakkeversioner er ikke pinned; dette er configuration management, ikke bit-identiske systemimages.

Regressionstesten kan sammenligne tilstanden før og efter genkørsel:

```bash
sudo bash ./tools/evidence.sh | tee ~/securebase-before.txt
sudo bash ./setup.sh --apply --console-confirmed --key-login-confirmed --skip-upgrade
sudo bash ./tools/evidence.sh | tee ~/securebase-after.txt
diff -u ~/securebase-before.txt ~/securebase-after.txt
```

`evidence.sh` bruger standardprojektet `/srv/securebase`; tilpas værktøjet ved et ændret `PROJECT_DIR`. Ingen forskel i manifestet er godt bevis for de medtagne filer/regler, men ikke en komplet sammenligning af alle systemets filer. I den verificerede fresh-install test blev deploymentet kørt igen med samme ønskede tilstand; outputtet viste **0 ændrede administrerede filer**, hvorefter et nyt SSH-login og healthcheck stadig fungerede. Se `docs/VM_TEST_REPORT.md`. Udvidede regressionstrin findes i `docs/TESTPLAN.md`.

## 8. Fejl, backup og ansvarlig gendannelse

Deployment anvender `set -Eeuo pipefail`, men det gør ikke en hel installation atomisk. Hvis et modul fejler, kan tidligere moduler allerede være gennemført. Stop, læs fejlen og deployment-loggen; kør ikke gentagne ændringsforsøg uden at forstå årsagen.

Første overskrevne filer sikkerhedskopieres under `/var/backups/securebase/before-first-change/` med adgang begrænset til root. SSH/sudo-ændringer valideres før aktivering og gendannes ved den relevante kontrolfejl. Netværket har særskilt gendannelsesforsøg. Der rulles ikke automatisk pakker eller konti tilbage, og UFW nulstilles ikke.

Ved tab af SSH: brug VirtualBox-konsollen og bootstrap-kontoen, kontrollér lokal IP, service og firewall. Snapshot-tilbageførsel er den enkleste komplette gendannelse af en lab-VM. De lagrede førstegangsbackups er ikke nødvendigvis den nyeste ønskede konfiguration.

Deployment-logs ligger i `/var/log/securebase/`. De er separate, root-læsbare kørselslogs; de er **ikke** omfattet af monitorens syv rotationer. Arkivér/fjern dem efter din driftsmæssige retentionpolitik ved længere tids brug.

## 9. Dokumentation til aflevering

Modul 6 er nu dokumenteret med både kildekode og faktisk VM-test. Den endelige aflevering bør indeholde:

- hele deployment-pakken med kommenterede scripts, `config.env.example`, public key og README – **aldrig den private nøgle**
- den samlede Word-rapport med fresh-install screenshots, healthcheck, Netplan, SSH/sudo-slutkontrol og idempotensbevis
- `docs/VM_TEST_REPORT.md` som kort maskinlæsbar/tekstlig opsummering af den verificerede VM-test

Den gennemførte fresh-install test viste blandt andet **19 OK, 1 WARN, 0 FAIL** i healthcheck, fungerende key-only SSH som `secureadmin`, statisk `10.0.2.15/24` med gateway `10.0.2.2`, og **0 ændrede administrerede filer** ved anden deployment-kørsel. Den ene WARN skyldtes forskellen mellem `who`/utmp og systemd-logind og blev beholdt som en observationsadvarsel frem for skjult som PASS.

`docs/TESTPLAN.md` er bevaret som regressionstestplan, så deploymentet kan afprøves igen på en ny VM eller efter kodeændringer.
