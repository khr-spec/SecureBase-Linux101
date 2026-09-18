# Test af repo-omstruktureringen — 1.2.0

[Overblik](../README.md) · [Historisk VM-test](VM_TEST_REPORT.md) · [Faktisk lokalt testoutput](RESTRUCTURE_TEST_OUTPUT.txt)

**Dato:** 18. september 2026.  
**Miljø:** lokal Linux-container med root, Bash, Python 3.13 og Git.  
**Omfang:** dokumentation, stier, kildeintegritet, isolerede funktioner og Git-migration. Ingen installation mod en Ubuntu-server.

## Resultat

```text
42 tests
0 failures
0 errors
0 skipped
OK
```

| Testgruppe | Antal | Resultat |
|---|---:|---|
| Oprindelige bundletests med nye stier | 20 | Bestået |
| Isoleret migration og konfliktbeskyttelse | 10 | Bestået |
| Struktur, evidence, links og stier | 12 | Bestået |

Testkommando:

```bash
python3 -m unittest discover -s tests -v
```

## Hvad er kontrolleret?

- Bash-syntaks for alle `.sh`-filer og de tre entrypoints' `--help`/fejlargumenter.
- Literal config-parser, ugyldige værdier, ukendte/dobbelte nøgler og afvisning af shell-injektion.
- Public key og det samme dokumenterede fingerprint som før omstruktureringen.
- Monitorens isolerede grænsetest og læsende `--sample`.
- Netplan-scope, UFW-regelkontrol og eksakt sudo-politik uden at aktivere dem på systemet.
- Idempotent installation, metadata og backup på midlertidige testfiler.
- Korrekt lokalisering af konfiguration, public key og hjælpefiler efter flytningen til `scripts/`, også i en mappe med mellemrum.
- Seks konsistente Markdown-moduler, balancerede kodeblokke og eksisterende relative linkmål.
- Alle **87 figurer** er byte-identiske med de tilsvarende indlejrede billeder i Word-rapporten; hash og kilde findes i `evidence/index.json`.
- Den vedlagte Word-rapport er byte-identisk med kildefilen.
- Checksums dækker leverancefilerne og udelader lokal `config.env` og `.git`.
- Ingen OpenSSH-private-key-blok findes i leverancen.

## Begrænset kodeændring

Kildeindholdet er sammenlignet med 1.1.0. Kun tre runtimefiler er ændret:

| Fil efter flytning | Ændring |
|---|---|
| `scripts/setup.sh` | Skelner mellem scripts-mappe og repo-rod; lokal config fra repo-roden; hjælpetekst med nye stier/version. |
| `scripts/modules/00-preflight.sh` | Config/key-validering og pakke-stikontrol bruger repo-roden. |
| `scripts/modules/05-ssh.sh` | Public-key-stien løses fra repo-roden, ikke scripts-mappen. |

De øvrige eksisterende runtimefiler, inklusive `healthcheck.sh`, `monitor.sh`, UFW-/sudo-/netværkslogik og fælles filinstallation, er indholdsmæssigt uændrede. Testfiler er tilpasset til layoutet; repo-migration og historisk monitor er tilføjet separat.

## Migrationstest

De 10 migrationstests kontrollerer blandt andet:

- `--check` ændrer ikke brugerfiler eller Git-HEAD og opretter ingen backup.
- `--apply` tager backup og bevarer eksisterende commits, remote og lokal config.
- Ukendte ekstra brugerfiler bevares.
- Ændrede/ukendte gamle filer og en uren arbejdsmappe medfører stop, ikke blind overskrivning.
- Kildeintegritetsfejl, beskyttede stier, links og overlappende kilde-/målmapper afvises.
- Kendte CRLF-varianter af de gamle tekstfiler genkendes.
- Efter migration og commit giver en ny migration med samme kilde ingen filhandlinger.

Derudover blev **den faktiske 1.1.0-kildepakke** oprettet som et midlertidigt Git-repo og migreret til den nye struktur med `core.autocrlf=true`. Historik, remote og lokal config blev bevaret. Filflytning, staging, LF-normalisering, executable bits og efterfølgende commit blev gennemført lokalt. En ny filplan efter commit var tom.

Dette er en Linux-test af Git-/filforløbet, **ikke** en faktisk kørsel i Kaspers Windows-mappe og ikke en GitHub-push. Begynd derfor med migrationens `--check` på Windows.

## Visuel kontrol

START_HER er renderet i Chromium ved desktop- og mobilbredde. Alle seks modulfiler er desuden renderet fra Markdown til en lokal preview for kontrol af overskrifter, tabeller, kodeblokke og billeder. Alle 87 billeder kunne indlæses; der blev ikke registreret vandret side-overflow i de kontrollerede desktopvisninger. Billeddata blev indlejret i previewet; leverancen bruger almindelige relative billedlinks.

GitHubs faktiske rendering er ikke besøgt i brugerens private repo. Kontrollér et modullink og et screenshot efter din egen push.

## Hvad er ikke testet her?

**Ingen ny fuld Ubuntu-`--apply` er kørt med repo 1.2.0.** De historiske resultater 19 OK / 1 WARN / 0 FAIL og 0 ændrede administrerede filer kommer fra den tidligere VM-test, ikke fra denne omstrukturering. En ny deployment-/regressionstest kan udføres efter [testplanen](TESTPLAN.md).

Denne rapport dokumenterer ikke en sikkerhedscertificering, en fuld analyse af alle brugerfiler eller at andre operativsystemer/netværk understøttes.
