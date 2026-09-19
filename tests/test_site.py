#!/usr/bin/env python3
"""Static website regressions; never run the Ubuntu deployment."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from public_files import included_files
from check_site import inspect_site, Links


def text(path):return Path(path).read_text(encoding='utf-8')


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec('markdown_it') is None or importlib.util.find_spec('bs4') is None:
            raise unittest.SkipTest('Installer requirements-site.txt for websitebygning')
        result=subprocess.run([sys.executable,str(ROOT/'tools/build_site.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        cls.output=ROOT/'_site'

    def test_generated_links_anchors_and_downloads(self):
        errors,stats=inspect_site(self.output)
        self.assertEqual(errors,[])
        self.assertEqual(stats['evidence'],103)
        self.assertGreaterEqual(stats['pages'],40)

    def test_all_six_module_pages(self):
        pages=list((self.output/'moduler').glob('*.html'))
        self.assertEqual(len(pages),6)
        for p in pages:
            content=text(p)
            for expected in ['Sikkerhedsmæssig begrundelse','Dokumentation / bevis','language-','data-zoom']:
                self.assertIn(expected,content,p.name)

    def test_new_vm_evidence_hashes(self):
        items=json.loads(text(ROOT/'evidence/06-scripting/v1.2-2026-09-18/index.json'))['items']
        self.assertEqual(len(items),16)
        for i in items:
            self.assertEqual(hashlib.sha256((ROOT/i['file']).read_bytes()).hexdigest(),i['sha256'])

    def test_deployment_executable_logic_matches_verified_baseline(self):
        # 1.3.1 adds full-line documentation comments only. Strip blank/full-line comments
        # before hashing so documentation can improve without claiming a new VM-tested implementation.
        baseline=json.loads(text(ROOT/'tests/deployment-logic-baseline.json'))
        def logic_digest(path):
            rows=[]
            for line in text(path).splitlines():
                stripped=line.lstrip()
                if not stripped or stripped.startswith('#'):
                    continue
                rows.append(line.rstrip())
            return hashlib.sha256(('\n'.join(rows)+'\n').encode()).hexdigest()
        for filename,digest in baseline.items():
            self.assertEqual(logic_digest(ROOT/filename),digest,filename)
        actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').rglob('*') if p.is_file() and p.suffix in {'.sh','.py'} and '__pycache__' not in p.parts}
        self.assertEqual(actual,set(baseline))
        exact=json.loads(text(ROOT/'tests/deployment-baseline.json'))
        for filename in ('config/config.env.example','keys/secureadmin.pub'):
            self.assertEqual(hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),exact[filename],filename)

    def test_module6_script_documentation_is_explicit(self):
        scripts=sorted(p for p in (ROOT/'scripts').rglob('*') if p.is_file() and p.suffix in {'.sh','.py'})
        self.assertEqual(len(scripts),18)
        guide=text(ROOT/'scripts/README.md')
        module=text(ROOT/'docs/06-scripting.md')
        for p in scripts:
            rel=p.relative_to(ROOT).as_posix()
            source=text(p)
            self.assertIn('KØRSEL:',source,rel)
            self.assertIn(f'`{rel}`',guide,rel)
            self.assertIn(f'`{rel}`',module,rel)
        self.assertIn('19 OK   1 WARN   0 FAIL',module)
        self.assertIn('19 OK   1 WARN   0 FAIL',guide)

    def test_word_download_matches_release(self):
        original=ROOT/'reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx'
        download=self.output/'downloads/SecureBase-Linux101-Dokumentation.docx'
        self.assertEqual(original.read_bytes(),download.read_bytes())

    def test_start_here_points_to_existing_pages_url(self):
        config=json.loads(text(ROOT/'site/config.json'))
        self.assertIn('url='+config['pages_url'],text(ROOT/'START_HER.html'))
        self.assertIn(config['pages_url'],text(ROOT/'README.md'))

    def test_publication_allowlist_rejects_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for filename in ['README.md','config.env','.env','notes.txt','.git/config','_site/index.html','keys/id_ed25519','config/config.env','config/config.env.example','keys/secureadmin.pub']:
                p=root/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('test',encoding='utf-8')
            names={p.relative_to(root).as_posix() for p in included_files(root)}
            self.assertEqual(names,{'README.md','config/config.env.example','keys/secureadmin.pub'})

    def test_source_archive_is_safe_and_complete(self):
        version=text(ROOT/'VERSION').strip()
        with ZipFile(self.output/f'downloads/SecureBase-{version}.zip') as z:
            names=set(z.namelist())
            self.assertIn('SecureBase-Linux101/scripts/setup.sh',names)
            self.assertIn('SecureBase-Linux101/docs/06-scripting.md',names)
            self.assertEqual(len([n for n in names if n.startswith('SecureBase-Linux101/evidence/') and n.endswith('.png')]),103)
            self.assertNotIn('SecureBase-Linux101/config.env',names)
            self.assertFalse(any('/.git/' in n or '/_site/' in n for n in names))

    def test_search_index_has_module_and_code_content(self):
        items=json.loads(text(self.output/'assets/search.json'))
        self.assertGreater(len(items),20)
        self.assertTrue(any(i['url']=='moduler/03-brugere-grupper.html' and 'sudo' in i['text'].lower() for i in items))
        for i in items:
            self.assertTrue((self.output/i['url']).is_file(),i['url'])

    def test_html_resources_are_local(self):
        for p in self.output.rglob('*.html'):
            parsed=Links();parsed.feed(text(p))
            for url in parsed.resources:
                self.assertFalse(url.startswith(('https:','http:','//')),f'{p}: {url}')

    def test_real_vm_limits_remain_visible(self):
        content=text(self.output/'verifikation.html')
        for expected in ['19 OK','1 WARN','0 FAIL','utmp','54734b9']:
            self.assertIn(expected,content)
        self.assertIn('ikke en sikkerhedscertificering',text(self.output/'index.html'))

    def test_version_and_source_date_are_distinct(self):
        self.assertEqual(text(ROOT/'VERSION').strip(),'1.3.2')
        self.assertIn('SecureBase 1.2',text(ROOT/'scripts/setup.sh'))
        self.assertIn('1.3',text(ROOT/'docs/GRUNDLAG.md'))

    def test_website_source_has_no_duplicate_index(self):
        self.assertFalse((ROOT/'site/index.html').exists())
        self.assertTrue((ROOT/'tools/build_site.py').exists())

    def test_workflow_only_uploads_generated_site(self):
        workflow=text(ROOT/'.github/workflows/pages.yml')
        self.assertIn('path: _site',workflow)
        self.assertIn('needs: build',workflow)
        self.assertIn('pages: write',workflow)
        self.assertIn('python tools/build_site.py',workflow)
        self.assertNotIn('path: .\n',workflow)


if __name__=='__main__':unittest.main(verbosity=2)
