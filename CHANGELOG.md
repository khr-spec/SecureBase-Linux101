# Ændringslog

## 1.3.1 · 18. september 2026 — eksplicit Modul 6-scriptdokumentation

- Alle 18 scriptfiler under `scripts/` har eksplicit topkommentar med formål og dokumenteret kørsel.
- `scripts/README.md` samler fil-for-fil-vejledning og markerer tydeligt, hvilke moduler der ikke køres direkte.
- Modul 6 indeholder den samme komplette kørselsmatrix og et forkortet faktisk `healthcheck.sh`-output fra den færdige VM: 19 OK / 1 WARN / 0 FAIL.
- Kun fulde kommentarlinjer er tilføjet til den verificerede deploymentkode; en normaliseret logik-hash-test bekræfter, at de eksekverbare linjer svarer til v1.2-referencen.
- Ingen ny Ubuntu-deployment påstås for 1.3.1; VM-beviserne fra 18. september 2026 er fortsat den testede serverreference.

## 1.3.0 · 18. september 2026 — samlet aflevering

- GitHub Pages bliver den primære læseindgang: seks modulsider, VM-verifikation, søgning, evidensgalleri og download af Word-rapport og kildekode.
- HTML genereres fra repoets Markdown. Ingen separat vedligeholdt kopi af moduldokumentationen.
- README linker til websitet først. START_HER.html viderestiller til den eksisterende Pages-adresse.
- Overgangsvejledninger, engangsværktøjer og tilhørende interne testfiler er fjernet fra den aktuelle struktur.
- Alle 103 originale billedfiler og den historiske Word-rapport er bevaret uændret.
- Deployment-koden under scripts/, konfigurationsskabelonen og public key er byte-identiske med den verificerede 1.2-kode. Derfor står den oprindelige versionsbetegnelse i scriptets help-tekst stadig korrekt.
- Websitebygning, kildelinks, downloadindhold, billedintegritet og privatlivsafgrænsning kontrolleres lokalt og i Pages-workflowet.
- Ingen ny fuld Ubuntu-installation er udført for 1.3-præsentationsudgaven. Repo-synlighed og faktisk Pages-publicering foretages af ejeren.

## 1.2.0 · 18. september 2026 — dokumentation og ny VM-test

- Dokumentation fordelt på seks Markdown-moduler; kode under scripts/ og konfiguration under config/.
- 87 figurer fra den uændrede Word-rapport er lagt i evidence/.
- Ny fresh-install-test af scripts/-strukturen dokumenteret med 16 yderligere screenshots.
- Første apply: 12 ændrede administrerede filer. Genkørsel: 0. Healthcheck: 19 OK / 1 WARN / 0 FAIL.
- Statiske netværksværdier, SSH ved sikkerhedsstop og afsluttende sudo-rolle verificeret.
- Python-tests tilpasset Windows; Linux-/root-specifikke kontroller kan markeres skipped dér.

## 1.1.0 · efter den første VM-test

Dokumentationen blev ajourført med den faktiske Ubuntu-test og dens afgrænsninger.

## 1.0 · 17. september 2026 — oprindelig kodepakke

Modulopdelt Bash-opsætning, selvstændigt healthcheck og monitorering afprøvet på en separat Ubuntu Server-VM.
