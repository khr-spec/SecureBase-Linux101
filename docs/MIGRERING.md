# Opdatér dit eksisterende Git-repo

[Overblik](../README.md) · [Ændringslog](../CHANGELOG.md)

Du skal **ikke** oprette repoet igen. Din nuværende mappe er:

```text
C:\Users\Kasper\Desktop\securebase-deployment
```

Den indeholder allerede .git og remote til dit private GitHub-repo. Den nye leverance kopieres ind dér som en ny reel ændring; historikken bevares.

## 1. Pak den nye ZIP ud et andet sted

Pak `SecureBase_Linux101_v1.2.0.zip` ud under Downloads. Det skal give en **separat** mappe `SecureBase-Linux101`, som indeholder den nye README, scripts/, docs/, evidence/ og tools/migrate_repo.py.

Brug aldrig den eksisterende repo-mappe som udpakningsmål direkte. Migrationen skal kunne kontrollere de gamle filer, før den erstatter dem.

Eksempel i PowerShell:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\SecureBase_Linux101_v1.2.0.zip" -DestinationPath "$env:USERPROFILE\Downloads\SecureBase-v1.2"
$source = "$env:USERPROFILE\Downloads\SecureBase-v1.2\SecureBase-Linux101"
$target = "$env:USERPROFILE\Desktop\securebase-deployment"
```

Vælg en anden tom udpakningsmappe, hvis SecureBase-v1.2 allerede eksisterer. Brug ikke -Force til at skjule en gammel eller blandet leverance.

## 2. Se planen før ændringer

```powershell
python "$source\tools\migrate_repo.py" --target "$target" --check
```

Kontrollen kræver Git og Python på Windows. Den kontrollerer en ren Git-arbejdsmappe, kildepakkens checksums og kendte filer fra 1.1.0. Egne ændringer eller filkonflikter medfører stop; de overskrives ikke bare.

Mangler Python-kommandoen, anvendes den Python-installation, du brugte til HTTP-overførslen. Installer ikke yderligere serverkomponenter blot for migrationen.

## 3. Anvend den kontrollerede filopdatering

```powershell
python "$source\tools\migrate_repo.py" --target "$target" --apply
```

Værktøjet tager først en fuld backup ved siden af repoet, inklusive .git. Derefter kopieres de nye filer, og kun uændrede kendte gamle stier fjernes. Det ændrer **ikke** repoets .git, din lokale config.env, GitHub-privatliv, commits eller remote.

Hvis det stopper med en konflikt, skal du læse den konkrete filsti. Commit eller gennemgå egne ændringer og sammenflet manuelt; slet ikke historik eller egne filer for at tvinge migrationen igennem.

## 4. Gennemgå og stage

```powershell
Set-Location $target
git status
git diff --stat
git add --all
git add --renormalize .
git ls-files "*.sh" | ForEach-Object { git update-index --chmod=+x -- $_ }
git diff --cached --stat
git diff --cached --summary
```

.gitattributes fastholder LF i tekstfiler, mens PNG/DOCX forbliver binære. chmod i Git-indekset gør Bash-filer eksekverbare ved et Linux-klon, selv om flytningen foretages på Windows. Det giver ikke ekstra sudo-rettigheder.

Kontrollér især, at dokumentation, screenshots og scripts er med, at de gamle placeringer flyttes, og at **config.env og private nøgler ikke er staged**. keys/secureadmin.pub er offentlig og må gerne være med.

## 5. Lav én ærlig ændringscommit og push

```powershell
git commit -m "Organize Linux 101 documentation, scripts and evidence"
git push
git status
```

Ingen force-push, ingen git init og ingen konstrueret historik. Branching er ikke et krav i den besked, du har fået; ændringen kan foretages på den eksisterende main.

Åbn README på GitHub efter push og prøv et modullink og et screenshot. Et lokalt HTML-dokument er en ekstra startside; README og .md-filer er den normale GitHub-indgang. Repoet forbliver privat, medmindre du selv ændrer synligheden.

## Konfiguration og checksums efter migration

Den gamle lokale config.env bevares i roden. Et nyt Git-klon indeholder den **ikke**; kopiér config/config.env.example til config.env før setup. Den offentlige nøgles sti er stadig relativ til repo-roden: keys/secureadmin.pub.

SHA256SUMS omfatter de leverede repo-filer, men ikke config.env eller .git. Efter senere bevidste ændringer til versionerede filer kan manifestet opdateres:

```powershell
python tools/update_checksums.py
```

Gennemgå ændringerne før commit. En checksum er integritetskontrol, ikke en digital signatur eller erstatning for kodegennemgang.

## Teststatus for migrationsværktøjet

Kontrollen og filoperationerne afprøves i midlertidige Git-repositories i den lokale Linux-testsuite. En faktisk migration i din Windows-mappe er ikke udført her. Begynd derfor med --check og behold backup, indtil GitHub-visningen er kontrolleret.
