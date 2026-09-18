# Kildegrundlag og versionsafgrænsning

[Til overblikket](../README.md)

## Dokumentationen bygger på

1. Den godkendte [Word-rapport](../reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx) fra det manuelle Modul 1–5-forløb og den særskilte Modul 6-test (87 sider).
2. Kildepakken `SecureBase_Modul6_v1.1.0.zip`, herunder README, kommenterede scripts og lokal teststatus.
3. De 16 nye screenshots fra v1.2-testen den 18. september 2026, registreret i [det nye evidensindeks](../evidence/06-scripting/v1.2-2026-09-18/index.json).
4. Brugerens indsatte GitHub-guide: én Markdown-fil pr. modul, relative links, scripts adskilt fra dokumentation og et kort root-README. Guidens mappestruktur er en anbefaling, ikke en påstået ny obligatorisk bedømmelsesregel.

Rapporten er kopieret uændret. De seks Markdown-filer genbruger dens terminologi, kommandoer, resultater og begrænsninger og samler dem under den aftalte modultemplate. Nye strukturvalg, migration og lokale tests beskrives særskilt.

## Proveniens

```text
Word SHA-256: 000aae50a0b68a76568091704d73fc4bd9c9b466de074e94bcda9bea8cc49512
Kildearkiv 1.1.0 ZIP SHA-256: ccf910597d1ab7306244e1b73b9839c99bb8ac4916f6c478740441911d2d60e3
```

Billedrelationer og billedhash for Word-figurer findes i [evidence/index.json](../evidence/index.json). Det [nye v1.2-indeks](../evidence/06-scripting/v1.2-2026-09-18/index.json) henviser til direkte screenshot-uploads, ikke Word-medier. De nye filer er byte-identiske med disse uploads. Git-reference `54734b9` kommer fra arbejdsforløbet; den er ikke genlæst fra en `.git`-mappe på VM'en. Billedteksterne angiver eksisterende udsnit. En indledende kapitelnummerering er tilpasset Markdown; det ændrer ikke de observerede resultater.

## Tre tilstande må ikke blandes sammen

| Tilstand | Hvad den omfatter |
|---|---|
| Manuel VM, Modul 1–5 | Konto-/fil-/netværksopsætning udført og dokumenteret undervejs. Modul 3 bruger passwordkrævende, begrænset sudo. Modul 5 bruger den historiske top/free-monitor. |
| Deployment-test 17. september 2026 | Frisk test-VM med tre NOPASSWD-kommandoer, /proc-baseret monitor, Netplan og idempotent genkørsel. Resultat 19 OK / 1 WARN / 0 FAIL. |
| Repo 1.2.0, 18. september 2026 | Dokumentation/evidence struktureret, kode flyttet til scripts/, stier og tests tilpasset. Efterfølgende afprøvet på ny Ubuntu-test-VM: første apply 12 ændrede administrerede filer, anden apply 0, healthcheck 19 OK / 1 WARN / 0 FAIL. |

Den fulde historiske monitor ligger i [scripts/history/monitor-modul5.sh](../scripts/history/monitor-modul5.sh). Den nye deployment-monitor ligger i [scripts/monitor.sh](../scripts/monitor.sh).

## Afgrænsninger beholdt fra rapporten

- Tomt `who`-output er ikke bevis for, at der ikke er SSH-sessioner. Healthcheckets WARN er bevaret.
- 0 ændrede administrerede filer gælder genkørslen med samme input. Logs må vokse, og pakkearkiver kan ændre sig.
- En før/efter-manifestdiff med evidence.sh er foreslået til fremtidig regression; den er ikke vist i VM-beviserne.
- Den midlertidige webservices UFW-regel og proces blev fjernet. Sletning af VirtualBox-forwarden er ikke vist.
- Threshold-logikken og journal-kanalen i Modul 5 blev testet hver for sig. Ingen faktisk 85/90-belastning blev fremprovokeret.

## Redaktionelle tilpasninger

Modulerne har fået faste topoverskrifter, navigationslinks og billedstier. Word-henvisninger til næste side er omskrevet til næste afsnit. Word-specifikke gentagelser og en sætning om en fejlslagen mellemkommando er udeladt; konfigurationer, planlagte negative tests og observerede slutresultater er bevaret. Historiske kommandoer i Modul 6 beholder de gamle stier; den aktuelle [deploymentvejledning](DEPLOYMENT.md) bruger scripts/.

Tekniske referencer fra den oprindelige pakke findes i [SOURCES.md](SOURCES.md). Henvisninger om den nye Git-/Markdown-struktur står i en særskilt sektion dér.
