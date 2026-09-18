# Modul 6 · testplan og screenshots

**Status 17. september 2026:** Planen er gennemført på en frisk Ubuntu Server 26.04.1 VM. Dokumentet bevares som regressionstestplan til senere genkørsler. De observerede hovedresultater er opsummeret i `VM_TEST_REPORT.md`; screenshots ligger i den samlede Word-rapport.

## A. Preflight – første trin

Som bootstrap-brugeren, fra pakkens mappe:

```bash
whoami
sudo bash ./setup.sh --check
```

Upload outputtet. Det dokumenterer inputvalidering og forudsætninger; ingen systemkonfiguration skal være ændret. Kontrollér, om `CONFIGURE_NETWORK` bevidst er yes eller no, og om den korrekte installationsbruger er valgt.

## B. Første deployment

```bash
sudo bash ./setup.sh --apply --console-confirmed
```

Tag screenshots af resultatet pr. modul og den afsluttende oversigt, ikke alle pakkedownloadlinjer. Ved SSH-prompten: test en ny key-only forbindelse fra Windows og `whoami`, før du bekræfter. Ved Netplan try: kontrollér en ny forbindelse og bekræft på konsollen.

Et stop er et stop, ikke et bestået deployment. Fejl afklares før videre ændringer.

## C. Sluttilstand og adskilte roller

Fra en ny SSH-session som secureadmin:

```bash
id
sudo -l
sudo /usr/sbin/sshd -t
echo "Returkode: $?"
sudo /usr/bin/id
echo "Returkode: $?"
```

Forvent de tre præcise NOPASSWD-kommandoer, ingen sudo-gruppe, succes ved sshd-kontrollen og afvisning ved sudo id. Nye sessioner kræves for at undgå gamle gruppelister.

Fra bootstrap-konsollen på standardkonfigurationen:

```bash
sudo -u developer1 sh -c 'printf "Modul 6 developer-test\n" > /srv/securebase/modul6-test.txt'
sudo -u guest1 cat /srv/securebase/modul6-test.txt
sudo -u guest1 sh -c 'printf "Skal afvises\n" >> /srv/securebase/modul6-test.txt'
getfacl -p /srv/securebase/modul6-test.txt
```

Forvent developer-oprettelse og guest-læsning tilladt; guest-skrivning afvist. Brug kun den dedikerede testfil. Der genoprettes ingen usikre chmod 777-øvelser.

## D. Healthcheck og overvågning

```bash
sudo bash ./healthcheck.sh
echo "Returkode: $?"
```

Gem hele outputtet i et eller flere læsbare screenshots. En WARN beskrives; den omdøbes ikke til PASS.

Efter mindst ét planlagt cron-tidspunkt:

```bash
sudo tail -n 5 /var/log/securebase-monitor.log
sudo journalctl -u cron.service --since "10 minutes ago" --no-pager | grep securebase-monitor
```

Kontrollér friske UTC-tidsstempler og den faktiske cron-hændelse. `monitor.sh --self-test` kan separat dokumentere tærsklernes logik; det er en simulation, ikke et virkeligt disk-/RAM-pres.

## E. Idempotens – anden kørsel

```bash
sudo bash ./tools/evidence.sh | tee ~/securebase-before.txt
sudo bash ./setup.sh --apply --console-confirmed --key-login-confirmed --skip-upgrade
sudo bash ./tools/evidence.sh | tee ~/securebase-after.txt
diff -u ~/securebase-before.txt ~/securebase-after.txt
echo "Diff-returkode: $?"
```

Forvent ingen konfigurationsforskel ved samme input. Diff-returkode 0 betyder identisk output. 1 betyder forskelle, som skal forstås; det er ikke automatisk en fejl i selve diff-værktøjet. Tidsstempler og driftslogs er bevidst udeladt af manifestet.

Kontrollér derefter endnu et SSH-login og kør healthcheck. Det er disse faktiske resultater, der bliver beviserne for genkørbarhed på Ubuntu, ikke de lokale unit tests i pakken.

## F. Aflevering

Denne del er gennemført. Aflever hele pakken inklusive scripts, kommentarer, config-skabelon, public key og README – aldrig den private nøgle – sammen med den samlede Word-rapport. Den faktiske test blev udført på en frisk Ubuntu Server 26.04.1 VM med statisk Netplan aktiveret, afgrænset NOPASSWD for tre SSH-driftskommandoer og `vboxuser` bevaret som bootstrap-/gendannelseskonto. Se `VM_TEST_REPORT.md`.
