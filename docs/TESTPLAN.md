# Regressionstestplan

[Overblik](../README.md) · [Aktuelle VM-resultater](VM_TEST_REPORT.md)

**Dette er fortsat en regressionstestplan, ikke et ubetinget PASS for alle testtrin.** V1.2 blev afprøvet den 18. september 2026. Tabellen angiver, hvad de nye billeder faktisk dækker; de supplerende trin nedenfor står fortsat som anvisninger til en senere kørsel.

| Kontrol | Status i v1.2-testen | Bevis |
|---|---|---|
| Bootstrap, ny struktur og preflight | Dokumenteret | [V12-01–07](../evidence/06-scripting/v1.2-2026-09-18/README.md) |
| Første apply og statisk IP/route | Dokumenteret; 12 ændrede administrerede filer | [V12-09](../evidence/06-scripting/v1.2-2026-09-18/09-foerste-apply-resultat.png), [V12-10](../evidence/06-scripting/v1.2-2026-09-18/10-netplan-sluttilstand.png) |
| SSH og afsluttende identitet/sudo | Login ved sikkerhedsstop og slutrolle dokumenteret | [V12-08/12/16](../evidence/06-scripting/v1.2-2026-09-18/README.md) |
| Healthcheck kaldt af setup | Dokumenteret; 19 OK / 1 WARN / 0 FAIL | [V12-14](../evidence/06-scripting/v1.2-2026-09-18/14-genkoersel-netplan-healthcheck.png), [V12-15](../evidence/06-scripting/v1.2-2026-09-18/15-genkoersel-nul-aendringer.png) |
| Anden fulde apply | Dokumenteret; 0 ændrede administrerede filer | [V12-15](../evidence/06-scripting/v1.2-2026-09-18/15-genkoersel-nul-aendringer.png) |
| Separat healthcheck-start / planlagt cron-start efter deployment | Ikke vist som separate kontroller i det nye screenshotforløb | Supplerende trin D |
| Nye developer/guest-funktionstests på v1.2-VM | Ikke særskilt vist | Supplerende trin C |
| Manifestdiff, arkivhash og genstartstest | Ikke særskilt dokumenteret i de nye billeder | Supplerende kontrol; ingen PASS-påstand |


## A. Pakke og preflight

Fra repo-roden, på en understøttet Ubuntu-test-VM med testet bootstrap-konsol:

```bash
sha256sum -c SHA256SUMS
cp -n config/config.env.example config.env
nano config.env
sudo bash scripts/setup.sh --check
```

Kontrollér public key, konto, interface, netværksvalg og pakker. --check er en læsende forudsætningskontrol, ikke en fuld ændringssimulation.

## B. Første deployment

```bash
sudo bash scripts/setup.sh --apply --console-confirmed
```

Bevar konsoladgang. Test nyt SSH-login ved KEY-OK-stoppet; Netplan try bekræftes i den oprindelige konsol. Tag screenshots af konti, politik og slutresultat, ikke alle pakkedownloadlinjer.

## C. Roller og adgang

I ny secureadmin-session:

```bash
id
sudo -l
sudo /usr/sbin/sshd -t
sudo /usr/bin/id
```

Sidste kommando skal afvises. De tre tilladte kommandoer skal fremgå uden generel ALL-adgang.

Fra bootstrap-konsollen, kun mod den dedikerede testfil:

```bash
sudo -u developer1 sh -c 'printf "Test\n" > /srv/securebase/regression-test.txt'
sudo -u guest1 cat /srv/securebase/regression-test.txt
sudo -u guest1 sh -c 'printf "Afvis\n" >> /srv/securebase/regression-test.txt'
getfacl -p /srv/securebase/regression-test.txt
```

Forvent developer-oprettelse og guest-læsning tilladt, guest-skrivning afvist. Denne separate fresh-VM-nyfiltest er en supplerende kontrol, ikke et påstået historisk screenshot.

## D. Healthcheck og overvågning

```bash
sudo bash scripts/healthcheck.sh
echo "Healthcheck-returkode: $?"
sudo tail -n 5 /var/log/securebase-monitor.log
sudo journalctl -u cron.service --since "10 minutes ago" --no-pager | grep securebase-monitor
```

Afvent mindst ét planlagt cron-tidspunkt. Beskriv WARN, og skeln mellem et cron-startsignal og et faktisk måleresultat.

## E. Genkørsel og supplerende manifestdiff

```bash
sudo bash scripts/tools/evidence.sh | tee ~/securebase-before.txt
sudo bash scripts/setup.sh --apply --console-confirmed
sudo bash scripts/tools/evidence.sh | tee ~/securebase-after.txt
diff -u ~/securebase-before.txt ~/securebase-after.txt
```

Gem ændringstælleren, ny SSH-session og healthcheck. Logs må vokse. Både den historiske og den nye v1.2-test viste 0 ændrede administrerede filer. Ingen af billedserierne indeholder et særskilt evidence.sh-diffbevis.

## F. Automatiske kode- og dokumentationskontroller

Fra repo-roden, i et aktiveret Python-miljø med afhængighederne fra `requirements-site.txt`:

```bash
python -m unittest discover -s tests -v
```

Kontrollerne omfatter Bash-syntaks, konfigurationsvalidering, filinstallation, scriptvejledning, billedintegritet og lokale links. De starter ikke et deployment mod serveren. Linux-/root-specifikke tests kan blive markeret `skipped` på Windows eller uden de krævede rettigheder; fravalg er ikke beståede funktionstests.

De dokumenterede VM-resultater er **19 OK / 1 WARN / 0 FAIL** og **0 ændrede administrerede filer ved genkørsel**. Den kendte `who`/utmp-advarsel skal fortsat vurderes ud fra logind-sessionerne. Nye testkørsler registreres med dato og version og erstatter ikke de oprindelige billedbeviser.
