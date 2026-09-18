# Website og automatisk publicering

[Overblik](../README.md) · [Publicering og privatliv](PUBLICERING.md)

## Én indholdskilde

Faglige rettelser foretages i docs/*.md. Billedbeviser tilføjes i evidence/ med billedtekst og proveniens. Websitebyggeren genererer HTML, indholdsfortegnelse, interne links, søgeindeks og kodevisning fra disse filer. Layoutet ligger under site/.

Den komplette aflevering kan læses uden GitHub-login, når den er publiceret. Links mærket GitHub åbner kildedokumentet eller kildefilen på GitHub og følger repoets adgangsregler.

## Byg lokalt

Python 3.11 eller nyere anbefales til websitebygningen. Brug gerne et isoleret Python-miljø, så websitepakkerne ikke blandes med operativsystemets pakker.

På Windows kan miljøet bruges uden at ændre PowerShells execution policy:

```powershell
python -m venv .venv-site
.\.venv-site\Scripts\python.exe -m pip install -r requirements-site.txt
.\.venv-site\Scripts\python.exe tools/build_site.py
.\.venv-site\Scripts\python.exe tools/check_site.py
.\.venv-site\Scripts\python.exe -m http.server 8000 --directory _site
```

På Ubuntu med python3-venv installeret:

```bash
python3 -m venv .venv-site
source .venv-site/bin/activate
```

Når det isolerede miljø er aktivt, bruges følgende kommandoer:

```bash
python -m pip install -r requirements-site.txt
python tools/build_site.py
python tools/check_site.py
python -m http.server 8000 --directory _site
```

Åbn localhost på port 8000. _site/ er genereret output og ignoreres af Git. Byg ikke websitet i den aktive serverinstallationsmappe, medmindre du har taget stilling til preflightens rettighedskrav. Websitebygningen kræver ikke sudo.

## GitHub Actions

Settings → Pages → Source skal fortsat være GitHub Actions. Det nye workflow tester og bygger på push til main. Deploy-jobbet kræver et vellykket build og publicerer kun _site/, ikke repo-roden. Pull requests kan testes, men publiceres ikke.

Indholdsændringer i docs/, evidence/ og reports/ indgår automatisk ved næste build; forsiden skal ikke kopieres manuelt. Repo-navn og Pages-adresse konfigureres centralt i site/config.json. Den nuværende adresse bevares.

## Hvad bliver offentligt?

Alle genererede modulsider, de 103 registrerede screenshots, testvejledninger, kildevisning, Word-rapport og den kuraterede source-ZIP bliver del af websitet. Det gælder også, når kilde-repoet er privat. Der er ikke loginbeskyttelse i denne statiske løsning.

Builderen anvender en eksplicit liste over mapper og filer til source-downloaden. Lokal config.env, .git, miljøfiler og uregistrerede filer medtages ikke blot fordi de ligger i arbejdsmappen. Nye publikationstyper kræver en bevidst kodeændring og test.

## Vedligeholdelse

```bash
python tools/update_checksums.py
python -m unittest discover -s tests -v
python tools/build_site.py
python tools/check_site.py
```

Se [testresultater](TESTRESULTATER.md). Checksum-manifestet opdateres kun ved bevidste ændringer; det er ikke et sikkerhedsbevis for ukendt indhold. GitHub Actions ændrer ikke automatisk manifestet for at få testen til at bestå.

## Kilder

[GitHub Pages-workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) · [GitHub Pages og offentlighed](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) · [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/using.html)
