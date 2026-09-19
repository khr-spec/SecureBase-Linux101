# Kilde- og testgrundlag

[Overblik](../README.md) · [VM-testrapport](VM_TEST_REPORT.md) · [Tekniske referencer](SOURCES.md)

## Grundlag

Projektet følger den udleverede **Linux 101-opgave, Modul 1–6**. Dokumentationen bygger på de gennemførte terminalkørsler, konfigurationsfilerne og den kommenterede kode under `scripts/`.

[Word-rapporten](../reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx) samler det manuelle forløb og den oprindelige deployment-test. Den er sprogligt redigeret den 19. september 2026 og suppleret med aktuelle kørselsoplysninger. Testdatoer og de 87 indlejrede billedbeviser er bevaret. Den separate [billedserie fra 18. september](../evidence/06-scripting/v1.2-2026-09-18/README.md) dokumenterer testen af den nuværende scriptstruktur.

## Testforløb

| Forløb | Hvad der er dokumenteret |
|---|---|
| Manuel opsætning · Modul 1–5 | Netværk, SSH, filrettigheder, roller, firewall og monitorering. Modul 3 bruger passwordkrævende sudo; Modul 5 bruger `top`/`free`-monitoren. |
| Deployment · 17. september 2026 | Frisk VM, tre afgrænsede `NOPASSWD`-kommandoer, `/proc`-baseret monitor og genkørsel. |
| Scriptstruktur 1.2 · 18. september 2026 | Frisk VM med kode under `scripts/`: første apply 12 ændrede administrerede filer; anden apply 0; healthcheck 19 OK / 1 WARN / 0 FAIL. |
| Dokumentationsudgave 1.3.2 | Redaktionel oprydning. De 18 scripts er uændrede fra 1.3.1; den eksekverbare logik svarer fortsat til 1.2-referencen. Ingen ny fuld VM-installation er udført for denne udgave. |

Den tidligere monitor bevares i [scripts/history/monitor-modul5.sh](../scripts/history/monitor-modul5.sh). Det aktuelle deployment bruger [scripts/monitor.sh](../scripts/monitor.sh).

## Billedbeviser

Der er **103 screenshots**: 87 figurer fra rapporten og 16 fra den efterfølgende VM-test. Indeksene angiver billedtekst, modul, filsti og SHA-256. Udsnit er markeret; billedfilerne er ikke retoucheret.

[Indeks over rapportfigurer](../evidence/index.json) · [Indeks over v1.2-testen](../evidence/06-scripting/v1.2-2026-09-18/index.json)

## Afgrænsning

- Healthcheckets `who`/utmp-advarsel bevares. Tomt `who`-output er ikke bevis for, at der ingen sessioner er.
- Idempotens gælder administrerede filer ved samme input. Logfiler kan vokse; der er ikke vist en særskilt `evidence.sh`-hashdiff af systemet.
- Modul 5's threshold-logik og journal-kanal blev testet hver for sig, uden at fylde disk eller RAM til driftsgrænserne.
- Webtestens proces og UFW-regel blev fjernet; sletning af den midlertidige VirtualBox-forward er ikke dokumenteret.
- Beviserne dækker de angivne VM'er og testtidspunkter, ikke en sikkerhedscertificering eller drift på alle Ubuntu-netværksmodeller.
