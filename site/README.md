# Websitekilde

Fagligt indhold redigeres i `docs/`, billedtekster i `evidence/` og layout i denne mappe. `tools/build_site.py` bygger `_site/` fra disse kilder; det er ikke en separat kopi af dokumentationen.

## Lokal kontrol

Fra repo-roden, i et aktiveret Python-venv:

```bash
python -m pip install -r requirements-site.txt
python tools/build_site.py
python tools/check_site.py
python -m http.server 8000 --directory _site
```

GitHub Actions kører tests og bygger siden før deployment. Kun `_site/` publiceres. Kildepakken omfatter de tilladte projektfiler, ikke `.git`, lokale miljøfiler eller private nøgler. Bygge- og testkommandoerne starter ikke serverens `setup.sh --apply`.
