#!/usr/bin/env python3
"""Build the static submission from Markdown and registered evidence.

No server setup is run. Only explicitly published source files enter downloads.
The generated _site folder is disposable and never an input to the next build.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote, unquote, urlsplit
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

try:
    from bs4 import BeautifulSoup
    from markdown_it import MarkdownIt
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
except ImportError as exc:
    raise SystemExit('Installer websiteafhaengigheder: python -m pip install -r requirements-site.txt\n' + str(exc))

from public_files import included_files

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
CONFIG = json.loads((ROOT / 'site/config.json').read_text(encoding='utf-8'))
REPO = CONFIG['repository_url'].rstrip('/')
BRANCH = CONFIG['branch']
VERSION = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
REPORT = 'reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx'
REPORT_OUT = 'downloads/SecureBase-Linux101-Dokumentation.docx'
MODULES = [
    ('01-vm-netvaerk', 'VM og netværk', 'Statisk IP, hostname og nøglebaseret SSH. Et kontrolleret udgangspunkt for serveren.', '4 figurer'),
    ('02-filsystem', 'Filsystem og adgang', 'Unix-rettigheder, SGID og ACL. Adgang tildeles efter behov — ikke med chmod 777.', '3 figurer'),
    ('03-brugere-grupper', 'Brugere og grupper', 'Administrator, udvikler og gæst. Forskellige rettigheder, afprøvet med faktiske handlinger.', '17 figurer'),
    ('04-firewall', 'Firewall og netværk', 'Default deny og en præcis SSH-undtagelse. HTTP-test viser forskellen på lukket og åben adgang.', '19 figurer'),
    ('05-monitorering', 'Monitorering og logs', 'Ressourcemålinger, cron, logrotation og loginanalyse. Både normaltilstand og warnings afprøves.', '26 figurer'),
    ('06-scripting', 'Shell og Bash', 'Den manuelle opsætning bliver reproducerbar. Fresh deployment, healthcheck og idempotens.', '18 + 16 figurer'),
]
DOC_MAP = {
    'README.md': 'index.html', 'CHANGELOG.md': 'changelog.html',
    'docs/DEPLOYMENT.md': 'deployment.html', 'docs/VM_TEST_REPORT.md': 'verifikation.html',
    'docs/VM_TEST_REPORT_2026-09-17.md': 'historik/vm-test-2026-09-17.html',
    'docs/TESTPLAN.md': 'testplan.html', 'docs/GRUNDLAG.md': 'grundlag.html',
    'docs/SOURCES.md': 'kilder.html', 'docs/WEBSITE.md': 'website.html',
    'docs/PUBLICERING.md': 'publicering.html', 'docs/TESTRESULTATER.md': 'tests.html',
    'scripts/README.md': 'scriptvejledning.html',
    'scripts/history/README.md': 'historik/monitor-modul5.html',
    'evidence/README.md': 'beviser/grundlag.html',
    'evidence/06-scripting/v1.2-2026-09-18/README.md': 'beviser/v1.2-2026-09-18.html',
}
for slug, *_ in MODULES:
    DOC_MAP[f'docs/{slug}.md'] = f'moduler/{slug}.html'
    DOC_MAP[f'evidence/{slug}/README.md'] = f'beviser/{slug}.html'
CODE_FILES = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts').rglob('*') if p.suffix in {'.sh', '.py'})
CODE_FILES += ['config/config.env.example', 'keys/secureadmin.pub']
CODE_MAP = {p: 'kildekode/' + p + '.html' for p in CODE_FILES}
OLD_EVIDENCE = json.loads((ROOT / 'evidence/index.json').read_text(encoding='utf-8'))
NEW_INDEX = json.loads((ROOT / 'evidence/06-scripting/v1.2-2026-09-18/index.json').read_text(encoding='utf-8'))
EVIDENCE = [dict(i, series='original', label='Figur ' + str(i['figure'])) for i in OLD_EVIDENCE]
EVIDENCE += [dict(i, module=6, series='v12', label=i['id']) for i in NEW_INDEX['items']]
SEARCH: list[dict] = []


def esc(value):
    return html.escape(str(value), quote=True)


def href(target: str, current: str):
    path, sep, fragment = target.partition('#')
    rel = os.path.relpath(path or current, str(Path(current).parent)).replace(os.sep, '/')
    return quote(rel, safe='/.-_') + ('#' + quote(unquote(fragment), safe='-_.~') if sep else '')


def gh(path: str):
    return REPO + '/blob/' + BRANCH + '/' + quote(path, safe='/.-_')


def write_file(relative: str, content: str):
    p = OUT / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8', newline='\n')


def page(title: str, content: str, current: str, description='', active=''):
    root = os.path.relpath('.', str(Path(current).parent)).replace(os.sep, '/') + '/'
    if root == './':
        root = './'
    def u(p): return esc(href(p, current))
    nav = ''.join(f'<a href="{u(dest)}"' + (' aria-current="page"' if active == key else '') + f'>{label}</a>' for key, label, dest in [
        ('modules', 'Moduler', 'index.html#moduler'), ('validation', 'Verifikation', 'verifikation.html'),
        ('evidence', 'Beviser', 'beviser.html'), ('scripts', 'Scripts', 'scriptvejledning.html'), ('downloads', 'Downloads', 'downloads.html')])
    canonical = CONFIG['pages_url'].rstrip('/') + '/' + current
    return f'''<!doctype html>
<html lang="da" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · SecureBase</title><meta name="description" content="{esc(description or 'SecureBase · Linux 101. Seks moduler, kildekode og dokumenterede VM-resultater.')}">
<meta name="theme-color" content="#0b121a"><meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="canonical" href="{esc(canonical)}"><link rel="icon" href="{u('assets/favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{u('assets/styles.css')}"><script defer src="{u('assets/site.js')}"></script>
</head><body data-root="{esc(root)}" id="top"><a class="skip" href="#main">Spring til indhold</a>
<header class="topbar"><div class="container nav-row"><a class="brand" href="{u('index.html')}" aria-label="SecureBase forside"><span class="brand-mark">SB</span><span><strong>SECUREBASE</strong><small>LINUX 101 / AFLEVERING</small></span></a><span class="version">v{esc(VERSION)}</span>
<nav class="top-links" aria-label="Hovednavigation" id="top-links">{nav}<a href="{esc(REPO)}" rel="noopener">GitHub ↗</a></nav>
<div class="nav-tools"><button class="icon-button search-button" data-search aria-label="Søg i afleveringen"><span>Søg</span>⌕<kbd>Ctrl K</kbd></button><button class="icon-button theme-button" data-theme-toggle aria-label="Skift mellem lyst og mørkt tema">◐</button><button class="icon-button menu-button" data-menu aria-label="Åbn navigation" aria-expanded="false" aria-controls="top-links">☰</button></div></div><div class="reading-progress" aria-hidden="true"></div></header>
{content}
<footer class="footer"><div class="container"><div class="footer-inner"><div><strong>SecureBase</strong> · Kasper · Linux 101 · {esc(VERSION)}</div><div><a href="{u('grundlag.html')}">Kildegrundlag</a><a href="{u('kilder.html')}">Referencer</a><a href="{u('changelog.html')}">Versionshistorik</a><a href="{esc(REPO)}">GitHub ↗</a></div></div><p class="footer-note">Dokumenteret labforløb — ikke en sikkerhedscertificering. Ubuntu-verifikation: 18. september 2026 · Præsentationsudgave 1.3.1; deploymentets eksekverbare logik matcher den verificerede 1.2-reference, mens scriptkommentarer er udbygget. Ingen eksterne fonte, analyseværktøjer eller JavaScript-CDN'er.</p></div></footer>
<a class="back-top" href="#top" aria-label="Til toppen">↑</a>
<dialog id="search-dialog" class="search-dialog" aria-labelledby="search-title"><div class="dialog-head"><h2 id="search-title">Søg i SecureBase</h2><button class="dialog-close" data-close aria-label="Luk søgning">×</button></div><input class="search-input" type="search" placeholder="SSH, rettigheder, Netplan…" aria-label="Søgetekst" autocomplete="off"><p class="search-status" aria-live="polite">Søg i dokumentationen.</p><div class="search-results"></div></dialog>
<dialog id="lightbox" class="lightbox" aria-labelledby="image-title"><div class="dialog-head"><h2 id="image-title">Dokumentationsbevis</h2><button class="dialog-close" data-close aria-label="Luk billede">×</button></div><div class="lightbox-body"><img alt=""></div><div class="lightbox-caption"></div><div class="lightbox-controls"><button class="icon-button" data-previous aria-label="Forrige billede">←</button><button class="icon-button" data-next aria-label="Næste billede">→</button><a data-image-download download>Åbn originalfil</a></div></dialog>
</body></html>'''


def nav_links(current):
    links = '<div class="nav-group"><div class="nav-label">De seks moduler</div>'
    for index, (slug, title, *_rest) in enumerate(MODULES, 1):
        target = f'moduler/{slug}.html'
        links += f'<a class="{"current" if current == target else ""}" href="{esc(href(target,current))}">{index:02d} &nbsp; {esc(title)}</a>'
    links += '</div><div class="nav-group"><div class="nav-label">Overtag projektet</div>'
    for title, target in [('Deployment', 'deployment.html'), ('VM-verifikation', 'verifikation.html'), ('Alle billedbeviser', 'beviser.html'), ('Scriptvejledning', 'scriptvejledning.html'), ('Kildekode', 'kildekode.html'), ('Downloads', 'downloads.html'), ('Testplan', 'testplan.html'), ('Lokale testresultater','tests.html')]:
        links += f'<a class="{"current" if current == target else ""}" href="{esc(href(target,current))}">{title}</a>'
    return links + '</div>'


def slugify(text):
    return re.sub(r'\s+', '-', re.sub(r'[^\w\s-]', '', text.strip().lower(), flags=re.UNICODE))


def highlight_code(code, language, _attrs=None):
    language = {'text':'text', 'conf':'ini', 'sudoers':'text', 'powershell':'powershell'}.get(language, language or 'text')
    try:
        lexer = get_lexer_by_name(language)
        return highlight(code, lexer, HtmlFormatter(nowrap=True))
    except ClassNotFound:
        return esc(code)


MD = MarkdownIt('commonmark', {'html': True, 'highlight': highlight_code}).enable(['table','strikethrough'])


def source_target(url, source, current):
    parts = urlsplit(url)
    if parts.scheme or url.startswith('//'):
        return url
    if not parts.path:
        return url
    target = (ROOT / Path(source).parent / unquote(parts.path)).resolve()
    try:
        relative = target.relative_to(ROOT).as_posix()
    except ValueError:
        raise ValueError(f'Link leaves repository: {source} -> {url}')
    if relative in DOC_MAP:
        dest = DOC_MAP[relative]
    elif relative in CODE_MAP:
        dest = CODE_MAP[relative]
    elif relative == REPORT:
        dest = REPORT_OUT
    elif relative == 'START_HER.html':
        dest = 'index.html'
    elif target.suffix in {'.png', '.json'} and relative.startswith('evidence/'):
        dest = relative
    else:
        # Source references remain available in the source browser or on GitHub.
        if not target.exists():
            raise ValueError(f'Broken source link: {source} -> {url}')
        return gh(relative) + ('#' + parts.fragment if parts.fragment else '')
    return href(dest + ('#' + parts.fragment if parts.fragment else ''), current)


def render_document(source: str, current: str):
    raw = (ROOT / source).read_text(encoding='utf-8')
    soup = BeautifulSoup(MD.render(raw), 'html.parser')
    if soup.find(['script','iframe','object','embed']):
        raise ValueError(f'Active HTML is not allowed in docs: {source}')
    first = soup.find('h1')
    title = first.get_text(' ', strip=True) if first else Path(source).stem
    if first:
        first.decompose()
    # Replace repetitive Markdown top-navigation with the shared site navigation.
    first_p = soup.find('p')
    if first_p and (first_p.get_text().startswith(('← Overblik','Overblik','Til overblikket','Tilbage til'))):
        first_p.decompose()
    ids = {t.get('id') for t in soup.find_all(id=True)}
    toc = []
    for heading in soup.find_all(re.compile('^h[2-6]$')):
        label = heading.get_text(' ', strip=True)
        base = slugify(label) or 'afsnit'; name = base; count = 0
        while name in ids:
            count += 1; name = f'{base}-{count}'
        heading['id'] = name; ids.add(name)
        if heading.name in {'h2','h3'}:
            toc.append((name, label, heading.name))
        a = soup.new_tag('a', href='#' + quote(name)); a['class'] = 'anchor-link'; a['aria-label'] = 'Link til ' + label; a.string = '#'; heading.append(a)
    for a in soup.find_all('a', href=True):
        a['href'] = source_target(a['href'], source, current)
        if str(a['href']).startswith(('https://','http://')):
            a['rel'] = 'noopener noreferrer'
    for img in list(soup.find_all('img', src=True)):
        img['src'] = source_target(img['src'], source, current)
        img['loading'] = 'lazy'; img['decoding'] = 'async'
        parent = img.parent
        if parent.name == 'a':
            parent['data-zoom'] = ''
            continue
        # Original alt texts and captions are kept, with zoom as an enhancement.
        fig = soup.new_tag('figure')
        a = soup.new_tag('a', href=img['src']); a['class'] = 'evidence-frame'; a['data-zoom'] = ''; a['data-caption'] = img.get('alt','')
        p = img.parent
        next_p = p.find_next_sibling('p') if p.name == 'p' else None
        caption = None
        if next_p and next_p.find('em') and len(next_p.find_all(recursive=False)) == 1:
            caption = next_p.get_text(' ',strip=True); next_p.decompose()
        if p.name == 'p' and len(p.find_all(recursive=False)) == 1:
            p.replace_with(fig)
        else:
            img.insert_before(fig)
        img.extract(); a.append(img); fig.append(a)
        cap = soup.new_tag('figcaption'); cap.string = caption or img.get('alt','Dokumentationsbillede'); fig.append(cap)
    for table in list(soup.find_all('table')):
        wrap=soup.new_tag('div');wrap['class']='table-scroll';wrap['tabindex']='0';wrap['role']='region';wrap['aria-label']='Tabel — rul vandret ved behov';table.wrap(wrap)
        for th in table.find_all('th'): th['scope']='col'
    for pre in list(soup.find_all('pre')):
        code=pre.find('code'); classes=code.get('class',[]) if code else []; lang=next((x[9:] for x in classes if x.startswith('language-')),'text')
        wrapper=soup.new_tag('div');wrapper['class']='code-block';pre.wrap(wrapper);pre['class']='hl'
        toolbar=soup.new_tag('div');toolbar['class']='code-toolbar';span=soup.new_tag('span');span.string=lang;toolbar.append(span)
        copy=soup.new_tag('button');copy['class']='copy-button';copy['data-copy']='';copy['type']='button';copy.string='Kopiér';toolbar.append(copy);wrapper.insert(0,toolbar)
    plain = soup.get_text(' ',strip=True)
    SEARCH.append({'title': title, 'url': current, 'text': plain})
    return title, str(soup), toc


def document_page(source, current):
    title, body, toc = render_document(source,current)
    number = next((i for i,(slug,*_) in enumerate(MODULES,1) if source == f'docs/{slug}.md'),None)
    eyebrow = f'MODUL {number:02d} / LINUX 101' if number else 'DOKUMENTATION / SECUREBASE'
    description = MODULES[number-1][2] if number else 'Kildebaseret dokumentation, begrundelser og afgrænsede testresultater.'
    source_btn = f'<a class="button small secondary" href="{esc(gh(source))}">Markdown på GitHub ↗</a>'
    toc_html = ''.join(f'<a href="#{quote(i)}">{esc(label)}</a>' for i,label,level in toc if level == 'h2')
    if not toc_html:
        toc_html=''.join(f'<a href="#{quote(i)}">{esc(label)}</a>' for i,label,level in toc[:20])
    end = ''
    if number:
        previous = 'index.html#moduler' if number == 1 else 'moduler/'+MODULES[number-2][0]+'.html'
        following = 'verifikation.html' if number == 6 else 'moduler/'+MODULES[number][0]+'.html'
        end=f'<nav class="page-end" aria-label="Modulnavigation"><a href="{esc(href(previous,current))}">← {"Alle moduler" if number==1 else "Forrige modul"}</a><a href="{esc(href(following,current))}">{"Se VM-verifikation" if number==6 else "Næste modul"} →</a></nav>'
    content=f'''<main id="main"><div class="page-top"><div class="container"><div class="breadcrumbs"><a href="{esc(href('index.html',current))}">SecureBase</a><span>/</span>{esc('Moduler' if number else 'Dokumentation')}</div><div class="eyebrow">{eyebrow}</div><h1>{esc(title)}</h1><p class="page-description">{esc(description)}</p><div class="actions">{source_btn}<a class="button small secondary" href="{esc(href('beviser.html',current))}">Billedbeviser ↗</a></div></div></div>
<div class="doc-layout"><aside class="side-nav" aria-label="Dokumentationsnavigation">{nav_links(current)}</aside><div class="doc-content"><details class="mobile-outline"><summary>Moduler og vejledninger</summary>{nav_links(current)}</details><article class="prose">{body}</article>{end}</div><aside class="toc" aria-label="På denne side"><div class="nav-label">På denne side</div>{toc_html}</aside></div></main>'''
    write_file(current,page(title,content,current,description,'modules' if number else 'validation' if current=='verifikation.html' else ''))


def homepage():
    current='index.html'
    cards=''
    for i,(slug,title,description,evidence) in enumerate(MODULES,1):
        cards += f'<a class="module-card" href="moduler/{slug}.html"><div class="module-meta"><b>{i:02d}</b><span>LINUX 101</span></div><h3>{esc(title)}</h3><p>{esc(description)}</p><span class="more"><span>{evidence}</span><span>Læs modulet →</span></span></a>'
    proof1=NEW_INDEX['items'][14];proof2=NEW_INDEX['items'][15]
    proofs=''
    for label,item,title,summary in [('GENKØRSEL',proof1,'Samme input. Ingen nye filændringer.','Anden fulde apply rapporterer 0 ændrede administrerede filer. Logs må fortsat vokse.'),('ADGANGSKONTROL',proof2,'En administrator — ikke ubegrænset root.','secureadmin har kun de tre navngivne NOPASSWD-kommandoer. Bootstrap-kontoen bevares separat.')]:
        proofs+=f'<div class="feature-proof"><a class="proof-image" data-zoom data-caption="{esc(item["caption"])}" href="{esc(item["file"])}"><img src="{esc(item["file"])}" alt="{esc(item["caption"])}" loading="lazy"></a><div class="proof-caption"><div class="eyebrow">{label}</div><h3>{title}</h3><p>{summary}</p></div></div>'
    content=f'''<main id="main"><section class="hero"><div class="container hero-grid"><div><div class="eyebrow">INFRASTRUKTUR / SIKKERHED / DOKUMENTATION</div><h1>En sikker base.<br><span>Bygget til at<br>blive overtaget.</span></h1><p class="lead">Fra en ren Ubuntu-server til dokumenteret adgangskontrol, overvågning og genkørbar opsætning. Her er hele Linux 101-forløbet — med kode, begrundelser og beviser.</p><div class="actions"><a class="button" href="#moduler">Udforsk de seks moduler <span>↓</span></a><a class="button secondary" href="{REPORT_OUT}" download>Download Word <span>↗</span></a></div><a class="text-link" href="{esc(REPO)}">Se kildekode og versionshistorik på GitHub ↗</a></div>
<div><div class="terminal"><div class="terminal-bar"><span class="dots"><i></i><i></i><i></i></span><span>LAB-RESULTAT / 18.09.2026</span><span>BASH</span></div><div class="terminal-body"><div class="terminal-cmd"><span>$</span> bash scripts/setup.sh --apply …</div><div class="terminal-line"><span>SSH / public key</span><b class="ok">VERIFICERET</b></div><div class="terminal-line"><span>UFW / deny incoming</span><b class="ok">AKTIV</b></div><div class="terminal-line"><span>Monitor / cron / logrotate</span><b class="ok">KONFIGURERET</b></div><div class="terminal-line"><span>Genkørsel / filændringer</span><b class="ok">0</b></div><div class="result-row"><strong>19 OK</strong><strong class="warn">1 WARN</strong><strong>0 FAIL</strong></div></div><div class="terminal-foot">OPSÆTNING 1.2 &nbsp;·&nbsp; PRÆSENTATION 1.3 &nbsp;·&nbsp; IKKE LIVE MONITORERING</div></div><p class="terminal-note">Status er et resumé af den dokumenterede VM-test. <a href="verifikation.html">Se rå beviser og forklaring af advarslen →</a></p></div></div></section>
<div class="container"><div class="stats"><div class="stat"><b>06</b><span>moduler med faglige begrundelser</span></div><div class="stat"><b>103</b><span>originale billedbeviser</span></div><div class="stat"><b>87</b><span>sider i den historiske Word-rapport</span></div><div class="stat"><b>0</b><span>ændrede filer ved genkørsel</span></div></div>
<section class="section" id="moduler"><div class="section-heading"><div><div class="eyebrow">01 / DOKUMENTATION</div><h2>Følg hele opbygningen.</h2></div><p>Læs direkte på sitet. Hvert modul samler udførelse, sikkerhedsvalg, kommandoer og de konkrete testbeviser.</p></div><div class="module-grid">{cards}</div></section>
<section class="section" id="arkitektur"><div class="section-heading"><div><div class="eyebrow">02 / SIKKERHEDSLAG</div><h2>Adgang er et bevidst valg.</h2></div><p>Firewall, autentifikation og filrettigheder løser forskellige opgaver. Ingen enkelt kontrol står alene.</p></div><div class="architecture"><div class="arch-step"><span class="mono">01 / NETVÆRK</span><b>Afgrænset indgang</b><p>Windows 127.0.0.1:2222 → NAT → Ubuntu TCP/22.</p></div><div class="arch-step"><span class="mono">02 / FIREWALL</span><b>Default deny</b><p>Eksplicit SSH-tilladelse fra den observerede NAT-kilde 10.0.2.2.</p></div><div class="arch-step"><span class="mono">03 / IDENTITET</span><b>Nøglebaseret SSH</b><p>Ingen SSH-passwords eller direkte root-login. Private key forbliver på klienten.</p></div><div class="arch-step"><span class="mono">04 / RETTIGHEDER</span><b>Roller med grænser</b><p>Admin, developer og guest med afgrænset sudo og separate ACL-regler.</p></div></div><div class="callout"><strong>Drift efter opsætning.</strong> En cron-plan skriver CPU, RAM og disk til monitor-loggen. Logrotate håndterer historikken; et selvstændigt healthcheck viser firewall, disk, sessioner og UID 0-konti. <a href="deployment.html">Se deploymentmodellen →</a></div></section>
<section class="section"><div class="section-heading"><div><div class="eyebrow">03 / VERIFIKATION</div><h2>Konfiguration er ikke nok.</h2></div><p>En frisk VM, første deployment og en fuld genkørsel. Resultaterne er dokumenteret, ikke blot forventet output.</p></div><div class="two-columns">{proofs}</div><div class="callout warning"><strong>19 OK / 1 WARN / 0 FAIL — ikke et rent PASS.</strong> <code>who</code>/utmp viste ingen logins, mens systemd-logind viste sessionerne. Advarslen er bevaret. Genkørselsresultatet gælder administrerede filer, ikke hele disken. <a href="verifikation.html">Læs testens afgrænsning →</a></div><div class="actions"><a class="button secondary" href="verifikation.html">Se fresh-VM-verifikationen →</a><a class="button secondary" href="beviser.html">Udforsk alle 103 billeder →</a></div></section>
<section class="section"><div class="section-heading"><div><div class="eyebrow">04 / OVERDRAGELSE</div><h2>Læs den. Kør den. Efterprøv den.</h2></div><p>Kildekode og dokumentation følger hinanden. Start med vejledningen, ikke med at køre et privilegeret script.</p></div><div class="download-card"><div class="download-icon">DOCX<br>87 SIDER</div><div><h3>Den samlede projektrapport</h3><p>Modul 1–6 · historisk rapport fra 17. september 2026.<br>Den nyere v1.2-verifikation læses her på sitet.</p></div><a class="button" href="{REPORT_OUT}" download>Download Word ↓</a></div><div class="actions"><a class="button secondary" href="deployment.html">Deploymentvejledning →</a><a class="button secondary" href="kildekode.html">Gennemgå scripts →</a><a class="button secondary" href="downloads.html">Alle downloads →</a></div></section>
<section class="section"><div class="section-heading"><div><div class="eyebrow">05 / VERSIONER</div><h2>Et dokumenteret forløb.</h2></div><p>Testdatoer bevares. En ny præsentation omskriver ikke historiske VM-resultater.</p></div><div class="timeline"><div class="timeline-item"><small>17. SEPTEMBER 2026 / 1.0–1.1</small><h3>Fra manuel opsætning til deployment</h3><p>Modul 1–5 og den første automatiserede test samles i Word-rapporten.</p></div><div class="timeline-item"><small>18. SEPTEMBER 2026 / 1.2</small><h3>Modulopdelt repo, afprøvet på ny VM</h3><p>Kode under scripts/. 16 nye screenshots dokumenterer fresh-install og genkørsel.</p></div><div class="timeline-item"><small>18. SEPTEMBER 2026 / 1.3</small><h3>Afleveringen samlet på ét website</h3><p>Samme testede deployment-kode. Ny præsentation, fuld dokumentation, galleri og downloads.</p></div></div><a href="changelog.html" class="text-link">Læs hele ændringsloggen →</a></section></div></main>'''
    write_file(current,page('Fra serveropsætning til reproducerbart deployment',content,current,'SecureBase · Linux 101. Seks moduler, 103 billedbeviser, Bash-deployment og verificeret genkørsel.'))


def gallery_page():
    cur='beviser.html'
    buttons='<button class="filter-button" data-filter="all" aria-pressed="true">Alle 103</button>'
    for n in range(1,7):
        buttons+=f'<button class="filter-button" data-filter="{n}" aria-pressed="false">Modul {n}</button>'
    buttons+='<button class="filter-button" data-filter="v12" aria-pressed="false">Ny v1.2-test · 16</button>'
    cards=''
    for i in EVIDENCE:
        cards+=f'<div class="gallery-card" data-module="{i["module"]}" data-series="{i["series"]}"><a class="evidence-frame" href="{esc(i["file"])}" data-zoom data-caption="{esc(i["caption"])}"><img src="{esc(i["file"])}" alt="{esc(i["caption"])}" loading="lazy" decoding="async"></a><div class="caption"><b>{esc(i["label"])} / MODUL {i["module"]}</b><p>{esc(i["caption"])}</p></div></div>'
    content=f'<main id="main"><div class="page-top"><div class="container"><div class="eyebrow">DOKUMENTATION / 103 ORIGINALE BILLEDER</div><h1>Beviserne bag resultatet.</h1><p class="page-description">87 figurer fra Word-rapporten og 16 nye v1.2-beviser. Billedernes originalfiler og deres testdatoer er bevaret. Filtrér efter modul, og åbn et billede i fuld størrelse.</p><a href="beviser/grundlag.html">Læs billedgrundlag og proveniens →</a></div></div><div class="wide-content"><div class="gallery-filters" role="group" aria-label="Filtrer billeder">{buttons}</div><p class="gallery-count" data-gallery-count aria-live="polite">103 billeder vist</p><div class="gallery">{cards}</div></div></main>'
    write_file(cur,page('Billedbeviser',content,cur,active='evidence'))


def downloads_page():
    cur='downloads.html'
    content=f'''<main id="main"><div class="page-top"><div class="container"><div class="eyebrow">OVERDRAGELSE / DOWNLOADS</div><h1>Tag materialet med.</h1><p class="page-description">Samlet rapport, fuld kildepakke og direkte adgang til testgrundlaget. Hentning starter ikke scripts eller deployment.</p></div></div><div class="wide-content"><div class="download-grid"><div class="download-card"><div class="download-icon">DOCX</div><div><h3>Word-rapport · Modul 1–6</h3><p>87 sider · historisk rapport fra 17. september 2026 · uændret original.<br>Den nyere test fra 18. september er dokumenteret i websitets verifikation.</p></div><a class="button" href="{REPORT_OUT}" download>Download Word ↓</a></div><div class="download-card"><div class="download-icon">ZIP</div><div><h3>SecureBase {esc(VERSION)} · komplet kildepakke</h3><p>Scripts, Markdown, billeder, tests, webkilde og Word-rapport.<br>Ingen .git-historik, private nøgler eller lokal config.env.</p></div><a class="button" href="downloads/SecureBase-{esc(VERSION)}.zip" download>Download kildekode ↓</a></div><div class="download-card"><div class="download-icon">SHA256</div><div><h3>Kontrolsummer til downloads</h3><p>Sammenlign filernes integritet. En checksum fra samme website er ikke en digital signatur.</p></div><a class="button secondary" href="downloads/SHA256SUMS.txt" download>Hent SHA-256 ↓</a></div></div><div class="callout warning"><strong>Før du kører setup:</strong> Public key i pakken er Kaspers eksempel. Installer din egen nøgle og kontrollér konfigurationen. Deployment køres på en understøttet Ubuntu-test-VM med snapshot og fungerende bootstrap-konsol — ikke på Windows eller i GitHub Actions.</div><div class="actions"><a class="button secondary" href="deployment.html">Læs deploymentvejledningen →</a><a class="button secondary" href="verifikation.html">Se hvad der er testet →</a><a class="button secondary" href="{esc(REPO)}">Åbn repository ↗</a></div></div></main>'''
    write_file(cur,page('Downloads',content,cur,active='downloads'))


def code_pages():
    cur='kildekode.html'
    rows=''
    for p in CODE_FILES:
        rows+=f'<tr><td><a href="{esc(href(CODE_MAP[p],cur))}"><code>{esc(p)}</code></a></td><td>{"Historisk — installeres ikke" if "/history/" in p else "Offentlig eksempel-nøgle" if p.endswith(".pub") else "Konfigurationsskabelon" if p.startswith("config/") else "Testet deployment-kilde fra 1.2"}</td></tr>'
        current=CODE_MAP[p]
        code=(ROOT/p).read_text(encoding='utf-8')
        language='bash' if p.endswith('.sh') else 'python' if p.endswith('.py') else 'ini' if 'config/' in p else 'text'
        code_html=highlight_code(code,language)
        body=f'''<main id="main"><div class="page-top"><div class="container"><div class="breadcrumbs"><a href="{esc(href('kildekode.html',current))}">Kildekode</a><span>/</span>{esc(Path(p).name)}</div><div class="eyebrow">{esc(language.upper())} / KOMPLET KILDEFIL</div><h1>{esc(Path(p).name)}</h1><p class="page-description"><code>{esc(p)}</code></p><div class="actions"><a class="button small secondary" href="{esc(gh(p))}">Kilde på GitHub ↗</a><a class="button small secondary" href="{esc(href('source/'+p,current))}" download>Hent fil ↓</a></div></div></div><div class="doc-layout"><aside class="side-nav">{nav_links(current)}</aside><article class="doc-content prose"><div class="source-info">Afleveringsudgave 1.3 gengiver denne fil uændret fra 1.2. Læs <a href="{esc(href('deployment.html',current))}">deploymentvejledningen</a> før kørsel. Den historiske monitor er kun dokumentation.</div><div class="code-block"><div class="code-toolbar"><span>{language} / {len(code.splitlines())} linjer</span><button class="copy-button" data-copy>Kopiér</button></div><pre class="hl"><code>{code_html}</code></pre></div></article></div></main>'''
        write_file(current,page(Path(p).name,body,current))
        copy_to(p,'source/'+p)
        SEARCH.append({'title':p,'url':current,'text':code})
    content=f'<main id="main"><div class="page-top"><div class="container"><div class="eyebrow">KILDEKODE / LÆS FØR KØRSEL</div><h1>Det, der bygger serveren.</h1><p class="page-description">Fuld kildevisning, ikke kun uddrag. Alle viste scripts er bevaret fra den testede 1.2-kode. Websiteudgave 1.3 ændrer ikke serverens SSH-, sudo-, firewall- eller monitoreringslogik.</p></div></div><div class="wide-content"><div class="callout"><strong>Kontrol og ændring er adskilt.</strong> Setup konfigurerer serveren. Healthcheck rapporterer den aktuelle tilstand uden automatisk reparation.</div><div class="table-scroll"><table><thead><tr><th>Fil</th><th>Rolle / afgrænsning</th></tr></thead><tbody>{rows}</tbody></table></div><a class="button secondary" href="deployment.html">Sådan køres deployment →</a></div></main>'
    write_file(cur,page('Kildekode',content,cur))


def copy_to(source,dest):
    source=ROOT/source
    if source.is_symlink():
        raise ValueError(f'Cannot publish symlink: {source}')
    p=OUT/dest;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,p)


def source_zip():
    dest=OUT/f'downloads/SecureBase-{VERSION}.zip';dest.parent.mkdir(parents=True,exist_ok=True)
    files=list(included_files(ROOT))+[ROOT/'SHA256SUMS']
    with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            relative=p.relative_to(ROOT).as_posix()
            info=ZipInfo('SecureBase-Linux101/'+relative,date_time=(2026,9,18,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.create_system=3
            info.external_attr=(0o100755 if p.suffix=='.sh' else 0o100644)<<16
            z.writestr(info,p.read_bytes())
    hashes=[]
    for name in [Path(REPORT_OUT).name,dest.name]:
        path=OUT/'downloads'/name
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
    write_file('downloads/SHA256SUMS.txt','\n'.join(hashes)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    if OUT.exists():
        if OUT.is_symlink() or not (OUT/'.securebase-site').is_file():
            raise SystemExit('Refusing to replace an unmarked _site directory. Move it aside first.')
        shutil.rmtree(OUT)
    OUT.mkdir();write_file('.securebase-site','Generated by SecureBase tools/build_site.py\n')
    for name in ['styles.css','site.js','favicon.svg']:
        copy_to('site/'+name,'assets/'+name)
    for item in EVIDENCE:
        p=ROOT/item['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError(f'Changed evidence: {item["file"]}')
        copy_to(item['file'],item['file'])
    for p in (ROOT/'evidence').rglob('*.json'):
        copy_to(p.relative_to(ROOT).as_posix(),p.relative_to(ROOT).as_posix())
    copy_to(REPORT,REPORT_OUT)
    homepage()
    for source, current in DOC_MAP.items():
        if source!='README.md':document_page(source,current)
    code_pages();gallery_page();downloads_page();source_zip()
    write_file('assets/search.json',json.dumps(SEARCH,ensure_ascii=False,separators=(',',':')))
    write_file('.nojekyll','')
    # 404 uses absolute project-relative navigation to work on arbitrarily deep URLs.
    address=esc(CONFIG['pages_url'])
    write_file('404.html',f'<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Side ikke fundet · SecureBase</title><body style="background:#0b121a;color:#edf4f8;font:18px/1.8 system-ui;padding:8vw"><h1>Side ikke fundet</h1><p>Indholdet kan være flyttet.</p><a style="color:#81e4cd" href="{address}">Til SecureBase-afleveringen →</a></body></html>')
    pages=len(list(OUT.rglob('*.html')))
    print(f'[OK] Bygget {pages} HTML-sider, {len(EVIDENCE)} originale billeder, Word og source-ZIP.')
    print('[INFO] Kun lokalt output i _site/. Ingen push, serverdeployment eller synlighedsaendring.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
