# Ændringslog

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

Der er ikke ændret SSH-port, sudo-politik, firewallpolitik eller monitorberegning. Denne strukturudgave er ikke gen-deployet på en Ubuntu-VM her.

## 1.1.0 — efter den dokumenterede VM-test

Startside, README og teststatus blev opdateret med den faktiske fresh-install-test, 19 OK / 1 WARN / 0 FAIL og genkørslen med 0 ændrede administrerede filer.

## 1.0 — oprindelig deployment-pakke

Modulopdelt opsætning, selvstændigt healthcheck og monitorering. Fresh-install-testen 17. september 2026 blev udført med denne kode.
