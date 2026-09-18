# Ændringslog

## 1.2.0 — 18. september 2026 · Ubuntu-verifikation tilføjet

- Ny fresh-install-test af `scripts/`-strukturen er dokumenteret med 16 originale screenshots.
- Første apply rapporterer 12 ændrede administrerede filer; anden apply 0. Healthcheck kaldt af setup giver 19 OK / 1 WARN / 0 FAIL i begge kørsler.
- Statisk netværk, SSH ved sikkerhedsstop og afsluttende identitet/sudo er beskrevet med deres faktiske beviser og afgrænsninger.
- Modul 6, VM-testrapport, README, START_HER, testplan og evidens-/kildeindekser er opdateret. Den gamle VM-testrapport er bevaret som `docs/VM_TEST_REPORT_2026-09-17.md`.
- Word-rapporten, de oprindelige 87 figurer, deploymentkode, tests og konfigurationsstandarder er uændrede. Dokumentationsopdateringen udgør ikke en ny deploymentversion.
- Nye billeder har eget kilde-/hashindeks; SHA256SUMS er opdateret til det samlede filindhold.

## 1.2.0 — 18. september 2026 · GitHub-struktur

- Root-README er nu overblik med links til seks selvstændige modulfiler.
- 87 eksisterende figurer er udtrukket fra den uændrede Word-rapport til evidence/.
- Bash-deployment, moduler og runtime-hjælpere flyttes samlet til scripts/.
- setup.sh kender nu både SCRIPT_DIR (scripts/) og REPO_DIR (roden). Default config.env og key-fil opløses fra repo-roden, uanset terminalens aktuelle mappe.
- Den versionerede skabelon ligger i config/config.env.example; den lokale config.env forbliver i roden og er ikke med i Git eller checksums.
- Den historiske Modul 5-monitor afleveres særskilt under scripts/history/ og installeres ikke af setup.
- Testene bruger den versionerede skabelon; de kræver ikke, at en ignoreret lokal config.env er med i et Git-klon.
- Git-tekstfiler bruger LF. Screenshot- og Word-filer behandles som binære.
- Migrationen bevarer .git og config.env, tager backup og foretager ikke commit, push eller ændring af repoets synlighed.
- Nye lokale kontroller og migrationssimulering er beskrevet separat fra den historiske VM-test.

Der er ikke ændret SSH-port, sudo-politik, firewallpolitik eller monitorberegning. Ved den oprindelige strukturudgivelse var en ny Ubuntu-test endnu ikke udført; den senere verifikation er registreret ovenfor.

## 1.1.0 — efter den dokumenterede VM-test

Startside, README og teststatus blev opdateret med den faktiske fresh-install-test, 19 OK / 1 WARN / 0 FAIL og genkørslen med 0 ændrede administrerede filer.

## 1.0 — oprindelig deployment-pakke

Modulopdelt opsætning, selvstændigt healthcheck og monitorering. Fresh-install-testen 17. september 2026 blev udført med denne kode.
