# Regressionstestplan

[Overblik](../README.md) · [Historiske VM-resultater](VM_TEST_REPORT.md) · [Lokale strukturtests](RESTRUCTURE_TEST_REPORT.md)

**Dette er en plan for en ny kørsel.** De historiske billeder beviser den tidligere VM-test. Ikke alle supplerende testtrin nedenfor er udført på den VM, og planen er ikke mærket samlet "bestået".

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

Gem ændringstælleren, ny SSH-session og healthcheck. Logs må vokse. Den historiske test viste 0 ændrede administrerede filer, men omfattede ikke et uploadet evidence.sh-diffbevis.

## F. Aflevering og udviklingshistorik

Dokumentation, scripts, tests, offentlige nøgler og evidence følger samme repo. Ingen private nøgler, passwords eller lokale config.env-filer committes. Commit nye ændringer og de tilsvarende docs sammen; lav ikke falske bagudrettede commits for tidligere arbejde.
