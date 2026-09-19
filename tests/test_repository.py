#!/usr/bin/env python3
"""Tests af repo-layout og dokumentationsintegritet, ikke Ubuntu-deployment."""
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlparse
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
MODULES=['01-vm-netvaerk','02-filsystem','03-brugere-grupper','04-firewall','05-monitorering','06-scripting']


def text(path):
    """Repository text files are UTF-8 on every platform."""
    return Path(path).read_text(encoding='utf-8')


def find_bash():
    candidates=[]
    if os.name=='nt':
        for base in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
            if base:
                candidates.extend([Path(base)/'Git/bin/bash.exe', Path(base)/'Git/usr/bin/bash.exe'])
    found=shutil.which('bash')
    if found:
        candidates.append(Path(found))
    seen=set()
    for candidate in candidates:
        candidate=str(candidate)
        if candidate in seen or not Path(candidate).exists():
            continue
        seen.add(candidate)
        try:
            r=subprocess.run([candidate,'--version'],text=True,capture_output=True,timeout=5)
        except OSError:
            continue
        if r.returncode==0:
            return candidate
    return None


BASH=find_bash()


def shell_path(path):
    return Path(path).resolve().as_posix()


def run(*cmd,cwd=None):
    return subprocess.run(cmd,text=True,capture_output=True,timeout=20,cwd=cwd)


class RepositoryTests(unittest.TestCase):
    def test_six_modules_have_consistent_sections(self):
        for mod in MODULES:
            content=text(ROOT/'docs'/f'{mod}.md')
            for section in ['## Formål','## Udførte opgaver','## Sikkerhedsmæssig begrundelse','## Dokumentation / bevis','## Overvejelser og fravalg']:
                self.assertIn(section,content,mod)
            without_code=re.sub(r'^```[^\n]*\n.*?^```\s*$', '', content, flags=re.M|re.S)
            self.assertEqual(len(re.findall(r'^# ',without_code,re.M)),1,mod)

    def test_evidence_count_and_hashes(self):
        items=json.loads(text(ROOT/'evidence/index.json'))
        self.assertEqual(len(items),87)
        counts=collections.Counter(i['module'] for i in items)
        self.assertEqual([counts[x] for x in range(1,7)],[4,3,17,19,26,18])
        for i in items:
            self.assertEqual(hashlib.sha256((ROOT/i['file']).read_bytes()).hexdigest(),i['sha256'],i['file'])
            self.assertIn(Path(i['file']).name,text(ROOT/'docs'/f"{MODULES[i['module']-1]}.md"))

    def test_figures_identical_to_report_media(self):
        items=json.loads(text(ROOT/'evidence/index.json'))
        with ZipFile(ROOT/items[0]['source']) as report:
            for i in items:
                self.assertEqual(report.read(i['word_media'].lstrip('/')),(ROOT/i['file']).read_bytes(),i['file'])

    def test_report_matches_documented_release(self):
        release=json.loads(text(ROOT/'tests/report-release.json'))
        report=ROOT/release['file']
        self.assertEqual(hashlib.sha256(report.read_bytes()).hexdigest(),release['sha256'])
        self.assertEqual(release['version'],text(ROOT/'VERSION').strip())

    def test_markdown_local_links(self):
        for p in ROOT.rglob('*.md'):
            content=re.sub(r'^```[^\n]*\n.*?^```\s*$', '',text(p),flags=re.M|re.S)
            for url in re.findall(r'\]\(([^)]+)\)',content):
                url=url.strip().strip('<>')
                parsed=urlparse(url)
                if parsed.scheme or not parsed.path:
                    continue
                self.assertTrue((p.parent/unquote(parsed.path)).exists(),f'{p.relative_to(ROOT)} -> {url}')

    def test_html_local_links(self):
        content=text(ROOT/'START_HER.html')
        for url in re.findall(r'(?:href|src)="([^"]+)"',content):
            parsed=urlparse(url)
            if parsed.scheme or not parsed.path:
                continue
            self.assertTrue((ROOT/unquote(parsed.path)).exists(),url)
        self.assertNotIn('<script src="http',content)

    def test_fenced_blocks_balanced(self):
        for p in ROOT.rglob('*.md'):
            fences=re.findall(r'^```.*$',text(p),re.M)
            self.assertEqual(len(fences)%2,0,str(p))

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_setup_help_from_another_working_directory(self):
        with tempfile.TemporaryDirectory(prefix='securebase cwd ') as d:
            r=run(BASH,shell_path(ROOT/'scripts/setup.sh'),'--help',cwd=d)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertIn('scripts/setup.sh --check',r.stdout)

    def test_relative_assets_resolve_with_spaces(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo with spaces';root.mkdir()
            shutil.copytree(ROOT/'scripts',root/'scripts')
            shutil.copytree(ROOT/'keys',root/'keys')
            shutil.copy(ROOT/'config/config.env.example',root/'config.env')
            # Brug samme Python-fortolker som startede testen; "python3" findes ikke altid paa Windows.
            r=run(sys.executable,str(root/'scripts/tools/validate_config.py'),str(root/'config.env'),str(root))
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            if not BASH:
                self.skipTest('Python-stidelen bestod; Bash/Git Bash er ikke tilgaengelig til shell-help-testen')
            for name in ['setup.sh','healthcheck.sh','monitor.sh']:
                r=run(BASH,shell_path(root/'scripts'/name),'--help',cwd=d)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_project_paths_are_split_explicitly(self):
        setup=text(ROOT/'scripts/setup.sh')
        pre=text(ROOT/'scripts/modules/00-preflight.sh')
        ssh=text(ROOT/'scripts/modules/05-ssh.sh')
        self.assertIn('CONFIG_FILE="$REPO_DIR/config.env"',setup)
        self.assertIn('"$CONFIG_FILE" "$REPO_DIR"',pre)
        self.assertIn('"$REPO_DIR/$SSH_PUBLIC_KEY_FILE"',ssh)
        self.assertFalse((ROOT/'setup.sh').exists())

    def test_checksums_match_repository(self):
        spec=importlib.util.spec_from_file_location('checksums',ROOT/'tools/update_checksums.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in module.included_files(ROOT)}
        manifest={rel:sha for sha,rel in (line.split('  ',1) for line in text(ROOT/'SHA256SUMS').splitlines())}
        self.assertEqual(actual,manifest)
        self.assertNotIn('config.env',manifest)

    def test_historical_and_current_monitors_are_separate(self):
        old=text(ROOT/'scripts/history/monitor-modul5.sh')
        current=text(ROOT/'scripts/monitor.sh')
        self.assertIn('top -bn1',old)
        self.assertIn('/proc/stat',current)
        self.assertIn('HISTORISK',text(ROOT/'scripts/history/README.md').upper())


if __name__=='__main__':
    unittest.main(verbosity=2)
