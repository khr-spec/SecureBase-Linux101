#!/usr/bin/env python3
"""Guard the handover focus, report guidance and original evidence after editing."""
from pathlib import Path
import json
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
FORBIDDEN=('Kaspers public key','Kaspers eksempel','brugerens screenshots',
           'brugerens egne resultater','brugerens uploadede',
           'Brugerens uploadede','Brugerens indsatte','den i samtalen udleverede')

class EditorialTests(unittest.TestCase):
    def test_submission_has_no_internal_publication_pages(self):
        for name in ('PUBLICERING.md','WEBSITE.md','TESTRESULTATER.md','MIGRERING.md'):
            self.assertFalse((ROOT/'docs'/name).exists(),name)
        self.assertTrue((ROOT/'site/README.md').is_file())

    def test_narrative_and_evidence_use_author_neutral_language(self):
        paths=[ROOT/'README.md',ROOT/'CHANGELOG.md']+list((ROOT/'docs').glob('*.md'))
        paths+=list((ROOT/'evidence').rglob('*.md'))+list((ROOT/'evidence').rglob('*.json'))
        for p in paths:
            text=p.read_text(encoding='utf-8')
            for phrase in FORBIDDEN:
                self.assertNotIn(phrase,text,str(p.relative_to(ROOT)))

    def test_readme_is_focused_on_linux_handover(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertNotIn('## Website og vedligeholdelse',text)
        self.assertNotIn('tools/build_site.py',text)
        self.assertIn('scripts/README.md',text)
        self.assertIn('19 OK / 1 WARN / 0 FAIL',text)

    def test_word_has_all_script_paths_and_actual_healthcheck_excerpt(self):
        info=json.loads((ROOT/'tests/report-release.json').read_text(encoding='utf-8'))
        with ZipFile(ROOT/info['file']) as z:
            xml=ET.fromstring(z.read('word/document.xml'))
            paragraphs=[''.join(p.itertext()) for p in xml.findall('.//w:p',NS)]
            text='\n'.join(paragraphs)
            for p in (ROOT/'scripts').rglob('*'):
                if p.suffix in {'.sh','.py'}:
                    self.assertIn(p.relative_to(ROOT).as_posix(),text)
            for expected in ('19 OK   1 WARN   0 FAIL','20. Aktuel scriptvejledning','ikke direkte','18. september 2026'):
                self.assertIn(expected,text)
            for phrase in FORBIDDEN:
                self.assertNotIn(phrase,text)
            self.assertEqual(len([n for n in z.namelist() if n.startswith('word/media/')]),87)

    def test_removed_pages_not_in_navigation_or_document_map(self):
        builder=(ROOT/'tools/build_site.py').read_text(encoding='utf-8')
        for retired in ('docs/WEBSITE.md','docs/PUBLICERING.md','docs/TESTRESULTATER.md','tests.html'):
            self.assertNotIn(retired,builder)
        self.assertIn("'deployment.html'",builder)
        self.assertIn("'scriptvejledning.html'",builder)

if __name__=='__main__':
    unittest.main(verbosity=2)
