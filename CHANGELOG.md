# Ændringslog

## 1.3.2 · 19. september 2026

- README, moduldokumentation og Word-rapport samlet i neutral teknisk rapportstil.
- Kortere navigation med fokus på moduler, beviser, deployment og rapport.
- Interne publicerings- og overgangsvejledninger fjernet fra afleveringen.
- Alle 103 billedbeviser og alle 18 kommenterede scripts bevaret.
- Word-rapporten suppleret med den aktuelle scriptoversigt og teststatus; oprindelige testdatoer bevares.
- Ingen ændring af deploymentkode, konfigurationsstandarder eller offentlig SSH-nøgle.

## 1.3.1 · 18. september 2026

- Formål og kørsel dokumenteret i alle 18 scriptfiler og i en samlet scriptvejledning.
- Modul 6 udvidet med kørselsmatrix og eksempeloutput fra healthcheck.
- Scriptændringerne var begrænset til kommentarer; eksekverbar logik bevaret.

## 1.3.0 · 18. september 2026

- Afleveringssite med modulsider, billedgalleri, søgning og rapportdownload.
- Markdown anvendes som fælles indholdskilde for repo og website.
- Deploymentkoden bevaret fra den verificerede 1.2-udgave.

## 1.2.0 · 18. september 2026

- Dokumentation opdelt efter modul; kode samlet under `scripts/`.
- Fresh-install-test af scriptstrukturen gennemført med 16 nye billedbeviser.
- Første apply: 12 filændringer. Genkørsel: 0. Healthcheck: 19 OK / 1 WARN / 0 FAIL.

## 1.1.0 · 17. september 2026

- Dokumentation ajourført efter den første VM-test.

## 1.0 · 17. september 2026

- Modulopdelt Bash-opsætning, selvstændigt healthcheck og monitor afprøvet på en separat Ubuntu Server-VM.
