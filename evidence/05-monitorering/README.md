# Evidence — Modul 5

[Til dokumentationen](../../docs/05-monitorering.md) · [Samlet evidensoversigt](../README.md)

Billederne er udtrukket fra den samlede Word-rapport. De viser de oprindelige terminalresultater; de er ikke nye kørsler af den omstrukturerede kode. Eventuelle udsnit fremgår af billedteksterne.

| Figur | Indhold |
|---|---|
| [5.1](figur-5-01.png) | Journald er aktiv og behandler loghændelser. Udsnit med kommando, service- og processtatus. |
| [5.2](figur-5-02.png) | Udsnit af aktuelle journalhændelser fra den indledende kontrol. Kommandoen er gengivet ovenfor; billedet viser system- og sudo-relaterede poster. |
| [5.3](figur-5-03.png) | Oversigt over /var/log og den særskilte kontrol af auth.log. Filen findes og er omkring 98K ved baseline-kontrollen. |
| [5.4](figur-5-04.png) | Logrotate-timeren er enabled og active (waiting) med logrotate.service som udløst tjeneste. Udsnit af statusdelen. |
| [5.5](figur-5-05.png) | Hovedkonfigurationen indeholder weekly, su root adm, rotate 4, create og include /etc/logrotate.d. compress er kommenteret ud i denne globale fil. |
| [5.6](figur-5-06.png) | Logfilen har -rw-r----- og root:adm. Det svarer til mode 0640. |
| [5.7](figur-5-07.png) | Udsnit af den afsluttende debug-kontrol. Monitor-loggen vurderes med den endelige regel; der udføres ingen faktisk rotation i denne test. |
| [5.8](figur-5-08.png) | Den første manuelle kørsel skriver CPU=6.1%, MEMORY=13.9% og DISK=16%. Scriptet er root:root og -rwxr-x---. Status- og journalbeskeder blev tilføjet senere. |
| [5.9](figur-5-09.png) | Den afsluttende scriptversion med logger-blokken før printf. Screenshotet viser editorindhold; den gemte fil blev derefter syntakskontrolleret og kørt. |
| [5.10](figur-5-10.png) | Syntakskontrol af den gemte fil med returkode 0. Kontrollen blev gentaget i terminalen og accepterede scriptets Bash-syntaks. |
| [5.11](figur-5-11.png) | Udsnit af cron-status: tjenesten er enabled og active (running). Det er en servicekontrol; selve monitor-jobbet testes særskilt. |
| [5.12](figur-5-12.png) | Den gemte cronlinje og cronfilens root:root-ejerskab med -rw-r--r--. Kun root har skriveret. |
| [5.13](figur-5-13.png) | Monitor-loggen får en ny måling kl. 13:30:01 efter første manuelle måling kl. 13:25:23. Terminaludsnittet viser kontrol før og omkring næste interval. |
| [5.14](figur-5-14.png) | Cron registrerer (root) CMD (/usr/local/sbin/securebase-monitor.sh) kl. 13:30:01. |
| [5.15](figur-5-15.png) | Windows-klienten får Permission denied (publickey) ved forsøget med fakeuser. |
| [5.16](figur-5-16.png) | Serverens auth.log indeholder Invalid user fakeuser og den afsluttende preauth-linje. Udsnit af de to hændelser; søgekommandoen er gengivet ovenfor. |
| [5.17](figur-5-17.png) | Journaludsnittet viser de samme SSH-hændelser kl. 13:32:50 med proces 2093, fakeuser, kilde 10.0.2.2 og klientport 62721. |
| [5.18](figur-5-18.png) | 0 matchende linjer i 30-minutters vinduet og 3 uden tidsfilter. Resultaterne er linjetællinger, ikke en opgørelse af tre angreb. |
| [5.19](figur-5-19.png) | De tre matchende hændelser: én ældre preauth-afbrydelse for secureadmin og to linjer fra det kontrollerede fakeuser-forsøg. |
| [5.20](figur-5-20.png) | Faktisk output fra threshold-testen kl. 13:47:45: MEMORY=13.9% og DISK=16% udløser begge warnings ved testgrænserne 10/10. |
| [5.21](figur-5-21.png) | Den endelige scriptversion køres manuelt og skriver STATUS=OK. Den viste måling kl. 15:23:22 har MEMORY=14.3% og DISK=16%. |
| [5.22](figur-5-22.png) | Opslag på tagget securebase-monitor i det kontrollerede 10-minutters vindue giver No entries. Det stemmer med de viste OK-målinger. |
| [5.23](figur-5-23.png) | Den manuelt sendte TEST WARNING genfindes i journalen. Tallene 95/92 er testtekst og ikke målte belastninger på serveren. |
| [5.24](figur-5-24.png) | Før/efter ved den tvungne rotation: den tidligere log på ca. 1.4K bliver til .log.1, og en ny tom aktiv log oprettes som root:adm med mode 0640. |
| [5.25](figur-5-25.png) | Efterkontrol: den nye aktive log indeholder CPU=3.3%, MEMORY=14.1%, DISK=16% og STATUS=OK kl. 15:15:01. date viser kontrollen kl. 15:17:06 UTC. |
| [5.26](figur-5-26.png) | Samlet slutbevis: korrekt logsti, diskgrænse 85, hukommelsesgrænse 90, cron hvert femte minut, endelig Logrotate-regel og monitor-linjer med STATUS=OK. |
