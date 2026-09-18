#!/usr/bin/env python3
"""Check generated HTML links, anchors, evidence hashes and publication boundaries."""
from __future__ import annotations
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.links=[];self.ids=set();self.duplicate_ids=[];self.images=[];self.resources=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'):
            if attrs['id'] in self.ids:self.duplicate_ids.append(attrs['id'])
            self.ids.add(attrs['id'])
        for attr in ['href','src']:
            if attrs.get(attr):self.links.append((tag,attr,attrs[attr]))
        if tag=='img' and attrs.get('src'):self.images.append(attrs)
        if tag in {'script','img','iframe'} and attrs.get('src'):self.resources.append(attrs['src'])
        if tag=='link' and attrs.get('rel') in {'stylesheet','icon'}:self.resources.append(attrs.get('href',''))


def inspect_site(output=OUT):
    output=Path(output).resolve();errors=[];parsers={};link_count=0
    for p in sorted(output.rglob('*.html')):
        parser=Links();parser.feed(p.read_text(encoding='utf-8'));parsers[p.resolve()]=parser
        if parser.duplicate_ids:errors.append(f'{p.relative_to(output)}: duplicate IDs {parser.duplicate_ids}')
        for img in parser.images:
            if not img.get('alt','').strip():errors.append(f'{p.relative_to(output)}: image without alt')
        for res in parser.resources:
            if urlsplit(res).scheme or res.startswith('//'):errors.append(f'{p.relative_to(output)}: external resource {res}')
    for p,parser in parsers.items():
        for tag,attr,url in parser.links:
            parts=urlsplit(url)
            if parts.scheme or url.startswith('//'):continue
            target=(p.parent/unquote(parts.path)).resolve() if parts.path else p
            if target.is_dir():target=target/'index.html'
            link_count+=1
            if not target.is_relative_to(output):
                errors.append(f'{p.relative_to(output)}: link leaves _site: {url}');continue
            if not target.exists():errors.append(f'{p.relative_to(output)}: missing target {url}');continue
            if parts.fragment and target.suffix=='.html':
                if unquote(parts.fragment) not in parsers.get(target,Links()).ids:
                    errors.append(f'{p.relative_to(output)}: missing anchor {url}')
    old=json.loads((ROOT/'evidence/index.json').read_text(encoding='utf-8'))
    new=json.loads((ROOT/'evidence/06-scripting/v1.2-2026-09-18/index.json').read_text(encoding='utf-8'))['items']
    for i in old+new:
        p=output/i['file']
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=i['sha256']:errors.append('Evidence changed: '+i['file'])
    report='reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx'
    doc=output/'downloads/SecureBase-Linux101-Dokumentation.docx'
    if not doc.exists() or doc.read_bytes()!=(ROOT/report).read_bytes():errors.append('Word download differs from original')
    version=(ROOT/'VERSION').read_text().strip()
    archive=output/f'downloads/SecureBase-{version}.zip'
    if not archive.exists():errors.append('Missing source archive')
    else:
        with ZipFile(archive) as z:
            for name in z.namelist():
                rel=name.removeprefix('SecureBase-Linux101/')
                if '.git' in Path(rel).parts or '_site' in Path(rel).parts or rel=='config.env':errors.append('Excluded file in archive: '+name)
            if 'SecureBase-Linux101/scripts/setup.sh' not in z.namelist():errors.append('Source ZIP has no setup script')
            try:
                manifest=z.read('SecureBase-Linux101/SHA256SUMS').decode('utf-8')
                for row in manifest.splitlines():
                    sha,rel=row.split('  ',1)
                    if hashlib.sha256(z.read('SecureBase-Linux101/'+rel)).hexdigest()!=sha:errors.append('Source ZIP checksum mismatch: '+rel)
            except (KeyError,ValueError):errors.append('Malformed source ZIP manifest')
    # An absolute path/local secret cannot become a website resource by mistake.
    for p in output.rglob('*'):
        if p.name=='config.env' or p.name in {'id_ed25519','id_rsa'} or p.is_symlink():errors.append('Disallowed website file: '+str(p))
    return errors,{'pages':len(parsers),'links':link_count,'evidence':len(old)+len(new)}


def main():
    if not OUT.exists():print('Byg websitet foerst: python tools/build_site.py',file=sys.stderr);return 2
    errors,stats=inspect_site()
    for error in errors:print('[FAIL] '+error)
    if errors:return 1
    print(f'[OK] {stats["pages"]} HTML-sider, {stats["links"]} lokale links/ankre og {stats["evidence"]} billedhash kontrolleret.')
    print('[OK] Word og source-ZIP verificeret; ingen eksterne assets eller lokal config.env publiceret.')
    return 0


if __name__=='__main__':raise SystemExit(main())
