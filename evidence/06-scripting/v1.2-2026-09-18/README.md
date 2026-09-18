# Evidence — v1.2 på Ubuntu, 18. september 2026

[Til Modul 6](../../../docs/06-scripting.md#vm-test-v12) · [VM-testrapport](../../../docs/VM_TEST_REPORT.md) · [Modul 6-indeks](../README.md)

Denne mappe indeholder **16 nye screenshots** fra v1.2-testen. De oprindelige 18 Modul 6-figurer fra 17. september og de øvrige Word-figurer ligger fortsat på deres eksisterende stier.

Billederne er kopieret uændret fra de uploads, der indgik i det nye testforløb: ingen beskæring, sammenskrivning eller ændring af terminaloutput. [index.json](index.json) registrerer kildefilnavn, dimensioner og SHA-256 for hvert billede. Det er filproveniens, ikke en signeret attest fra VM'en.

**Testgrundlag:** repo-udgave 1.2.0, Git-reference `54734b9` fra arbejdsforløbet; arkivet hed `SecureBase-Linux101-v1.2-test.zip`. VM'en modtog et arkiv uden `.git`. En særskilt sammenligning af arkivets hash med Git-committen er ikke vist i screenshots.

| Bevis | Indhold |
|---|---|
| [V12-01](01-foer-hostname-dhcp.png) | Før deployment: hostname Ubuntu-Server1, enp0s3 med 10.0.2.15/24 og default route via 10.0.2.2 med proto dhcp. |
| [V12-02](02-hentet-git-arkiv.png) | 18. september 2026 kl. 08:46:33 UTC: SecureBase-Linux101-v1.2-test.zip hentes med HTTP 200 og 6.340.751 bytes. |
| [V12-03](03-udpakket-repostruktur.png) | Den udpakkede repo-rod indeholder config/, docs/, evidence/, reports/, scripts/, tests/ og tools/. |
| [V12-04](04-valgt-labkonfiguration.png) | Editorvisning af v1.2-konfigurationen med CONFIGURE_NETWORK="yes", STATIC_IP="10.0.2.15/24" og NETWORK_APPLY="try". Den efterfølgende preflight viser den indlæste netværksplan. |
| [V12-05](05-preflight-scripts-sti.png) | sudo bash ./scripts/setup.sh --check: konfiguration, public key, syntaks og single-NIC-scope accepteres. sshd og setfacl skal installeres ved apply; Netplan er tilvalgt. |
| [V12-06](06-foerste-apply-kommando.png) | Første deployment startes fra den nye scripts/-struktur med sudo bash ./scripts/setup.sh --apply --console-confirmed. |
| [V12-07](07-foerste-apply-roller-noegle.png) | Første apply opretter konti og grupper, sætter projekt-ACL og installerer authorized_keys. ssh.service er aktiv, og forløbet venter på den eksterne SSH-test ved KEY-OK. |
| [V12-08](08-ssh-ved-bootstrap.png) | 18. september kl. 09:07:52 UTC: ny SSH-forbindelse fra Windows med PasswordAuthentication=no på klienten lykkes som secureadmin@securebase-server. |
| [V12-09](09-foerste-apply-resultat.png) | Første apply afsluttes med 12 ændrede administrerede filer og healthcheck 19 OK / 1 WARN / 0 FAIL. Monitor-linjen er tidsstemplet 09:10:02Z. |
| [V12-10](10-netplan-sluttilstand.png) | Netværkskontrol efter første apply: 10.0.2.15/24, default via 10.0.2.2 med proto static, dhcp4/dhcp6 false og DNS 10.0.2.3 samt 1.1.1.1. |
| [V12-11](11-genkoersel-roller-noegle.png) | Anden apply fra scripts/setup.sh: ingen pakkeopgraderinger, eksisterende konti bevares, ACL er allerede korrekt, authorized_keys er uændret, og KEY-OK bekræftes. |
| [V12-12](12-ssh-under-genkoersel.png) | 18. september kl. 09:14:25 UTC: SSH-login som secureadmin lykkes under anden kørsel. Klientkommandoen er ssh -p 2222; den tvinger ikke selv en autentifikationsmetode. |
| [V12-13](13-genkoersel-sudo-firewall.png) | Anden apply: effektiv SSH-hærdning, uændret sudoers med tre afgrænsede NOPASSWD-kommandoer og eksisterende UFW-regel for TCP/22 fra 10.0.2.2. Nederst vises Logrotate-debug. |
| [V12-14](14-genkoersel-netplan-healthcheck.png) | Anden apply kl. 09:14:38Z: Netplan genindlæses ikke; healthcheck og konfiguration er uændrede. UFW er aktiv, disken er 17 % brugt, og who/utmp-advarslen ses sammen med logind-sessioner. |
| [V12-15](15-genkoersel-nul-aendringer.png) | Anden apply afsluttes med 0 ændrede administrerede filer, 19 OK / 1 WARN / 0 FAIL, publickey påkrævet, ingen ekstra UID 0-konti i opslaget og en frisk monitor-linje. |
| [V12-16](16-afsluttende-identitet-sudo.png) | Afsluttende sessionskontrol: whoami viser secureadmin, hostname viser securebase-server, og sudo -l viser kun de tre forventede NOPASSWD-kommandoer. |

## Hvad beviserne viser — og ikke viser

Første apply rapporterer 12 ændrede administrerede filer; anden apply rapporterer 0. Healthchecket, som setup kalder, viser 19 OK / 1 WARN / 0 FAIL i begge kørsler. Netplan kontrolleres separat, og den afsluttende session viser identitet og sudo-politik.

SSH-loginbilledet kl. 09:14:25 er fra sikkerhedsstoppet **under** anden kørsel. Det afsluttende identitetsbillede viser ikke selve forbindelseskommandoen. Det registreres derfor som sessions-/rollekontrol, ikke som et selvstændigt skærmbevis på en ny forbindelse efter afsluttet genkørsel.

Der er ikke tilføjet konstruerede rå serverlogs. Fuld genstartstest, selvstændig hash-diff via evidence.sh og en separat invocation af healthcheck.sh i dette nye forløb er ikke vist. De lange, gentagne Logrotate-udskrifter er debug-vurderinger, ikke nye tvungne rotationer.
