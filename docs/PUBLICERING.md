# Publicering og privatliv

[Overblik](../README.md) · [Website](WEBSITE.md)

## Publiceringsbeslutning

1.3 er bygget som en offentlig, selvstændig aflevering. Et push med det nye Pages-workflow kan publicere modultekst, screenshots, kildefiler og Word-rapport — ikke kun den tidligere forside. Et privat repo gør ikke dette Pages-site privat.

Repoet bliver ikke automatisk ændret til public af scripts eller workflows. Ejeren vælger separat synlighed i GitHubs indstillinger. Afklar også med underviseren, at opgavebesvarelsen må deles offentligt.

## Hvad materialet indeholder

Screenshots og rapport indeholder blandt andet navn, lokale brugernavne, Windows-stier, labadresser, servernavne og offentlig SSH-nøgle/fingerprint. Kaspers public key er en deploymentskabelon, ikke en hemmelighed; andre administratorer skal erstatte den før brug. Word-rapporten er bevaret som historisk dokumentation og er ikke anonymiseret.

Kildepakken må ikke indeholde privat SSH-nøgle, passwords, tokens eller lokal config.env. Websitebyggeren ekskluderer lokale miljøfiler, .git og filer uden for de eksplicitte publiceringsmapper.

## Kontrol af den aktuelle kildepakke

```bash
python tools/audit_publication.py
```

Kontrollen finder udvalgte velkendte hemmelighedsformater og kontrollerer publiceringslisten. Den er en hjælpekontrol, ikke en garanti. Den udfører ikke OCR eller visuel kontrol af alle billeder og kan ikke vurdere enhver personoplysning.

## Git-historik før public repo

```bash
python tools/audit_publication.py --history
```

Denne ekstra kontrol kræver Git og undersøger tekstlige Git-objekter, der er nåbare fra lokale refs, efter udvalgte hemmelighedsformater. Den oplyser commit-forfatteres identiteter til din egen gennemgang. Commits kan indeholde en personlig e-mailadresse. Historik, som ikke er hentet lokalt, og ukendte formater er ikke dækket.

Den leverede ZIP indeholder ingen .git-mappe. En fuld kontrol af dit faktiske repos historik er derfor ikke udført ved pakning af 1.3. Ingen historik slettes eller omskrives af denne kontrol. Ved fund af en rigtig hemmelighed skal den tilbagekaldes; blot at slette filen fra main er ikke tilstrækkeligt.

## Kilder

[GitHub: repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility) · [GitHub: offentlighed på Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
