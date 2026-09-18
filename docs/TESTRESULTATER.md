# Lokale tests af afleveringsudgave 1.3.1

[Overblik](../README.md) · [VM-testgrundlag](VM_TEST_REPORT.md)

**Udgave:** 1.3.1 · **Kontroldato:** 18. september 2026

## Faktiske lokale resultater

| Kontrol | Resultat | Afgrænsning |
|---|---|---|
| Samlet Python-testsuite, isoleret Linux-container med root | 47 tests bestået; ingen fejl eller skips | Kører ikke setup mod værtens serverkonfiguration. Filmetadata-tests bruger midlertidige filer. |
| Samme tests uden root, separat kopi af repoet | 45 bestået, 2 sprunget over, 0 fejl | De to root-afhængige filmetadata-tests springes over; skipped er ikke bestået. |
| Genereret website | 51 HTML-sider bygget; lokale links og ankre kontrolleret | Ikke en måling af det publicerede GitHub Pages-site. |
| Billedintegritet | Alle 103 PNG-filer matcher de dokumenterede hashes | 87 fra den oprindelige Word-rapport og 16 supplerende v1.2-beviser. |
| Word-download | Byte-identisk med den oprindelige 87-siders rapport | Rapporten er historisk; dens testdato og indhold er ikke ændret. |
| Deployment-scripts | Normaliseret eksekverbar logik matcher v1.2-reference; kun fulde kommentarlinjer er tilføjet | Ingen ny 1.3.1-Ubuntu-installation påstås. |
| Konfigurationsskabelon og public key | Byte-identiske med v1.2-referencehashes | Miljøværdier og key-materiale er ikke ændret. |
| Modul 6-dokumentationskrav | 18/18 scripts har topkommentar; alle 18 står i kørselsmatrix; healthcheck-eksempel er indsat | Kontrollerer dokumentationens tilstedeværelse, ikke en ny VM-kørsel. |
| Source-download | ZIP-indhold og det medfølgende checksum-manifest kontrolleret | Indeholder ikke .git, lokal config.env, miljøfiler eller genereret website. |
| Udvalgte secret-mønstre i aktuelle tekstfiler | Ingen match i kontrollen | Ikke en fuldstændig hemmeligheds-, billed- eller historikaudit. |

De 47 tests er fordelt på **20 kodetests**, **12 repository-tests** og **15 website-/publiceringstests**. Testen af den samlede suite blev også gentaget uden root for at kontrollere de forudsætninger, en almindelig build-runner bruger. GitHub Actions-kørslen efter push er stadig en særskilt kontrol.

## Visuel kontrol og brugerfunktioner

Forside og centrale modulsider blev vist i Chromium i både desktop- og mobilstørrelse. Kontrollen dækkede mørkt/lyst tema, mobilmenu, filtrering af de 16 nye billedbeviser, billedvisning i dialog og søgning efter dokumentationsindhold. De afprøvede interaktioner gav ingen JavaScript-fejl. Mobilforsiden og den kontrollerede modulside havde ingen utilsigtet vandret side-overløb ved 390 pixels bredde.

Browserkontrollen anvendte de genererede HTML-dokumenter med de samme lokale CSS-, JavaScript- og billedfiler indlæst direkte i browserens dokument. Søgningen brugte det genererede søgeindeks. Det er en lokal visnings-/interaktionstest, ikke en test af GitHub-domæne, HTTP-adgang eller cloud-deployment.

## Opdatering af et eksisterende repo

Det særskilte engangsværktøj, som følger leveringspakken uden for repoet, er afprøvet mod et midlertidigt Git-repo baseret på 1.2. Kontrollerne dækkede læsende filplan, backup, bevarelse af historik/remote/lokal konfiguration, genkørsel uden nye filændringer og stop ved eksisterende staged ændringer. De afprøvede kontroller bestod. Værktøjet foretager hverken commit, push eller ændring af GitHub-synlighed.

Dette er en lokal simulation; det er ikke en påstand om, at brugerens Windows-mappe allerede er opdateret.

## Gentag kontrollerne

Kør i et Python-miljø med pakkerne fra requirements-site.txt. Se [websitevejledningen](WEBSITE.md) for opsætning af et isoleret miljø.

```bash
python -m unittest discover -s tests -v
python tools/build_site.py
python tools/check_site.py
python tools/audit_publication.py
```

Linux-/root-afhængige tests kan springes over på Windows eller i en ikke-privilegeret runner. De tidligere Windows-rettelser er bevaret, men den samlede 1.3.1-suite er ikke kørt på en faktisk Windows-maskine her.

## Hvad resultatet ikke siger

Dette er test af kode, dokumentation og websitebygning. Det ændrer ikke /etc, brugere, UFW eller Netplan. VM-beviserne fra den 17. og 18. september er fortsat deres egne testfaser. Der er ikke gennemført en ny fuld Ubuntu-deployment eller GitHub Actions-publicering af 1.3.1 ved pakningen.

Afleveringsudgave 1.3.1 ændrer kun scriptkommentarer og dokumentation i forhold til 1.3.0. Den aktuelle pakke indeholder ingen .git-mappe. Derfor er den faktiske Git-historik ikke scannet her. Før et privat repo gøres offentligt, bør ejerens lokale historik og alle billeder/rapporter gennemgås som beskrevet under [Publicering og privatliv](PUBLICERING.md).
