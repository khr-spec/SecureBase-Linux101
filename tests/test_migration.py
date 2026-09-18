#!/usr/bin/env python3
"""Migrationstests i midlertidige lokale Git-repos; ingen GitHub-kontakt."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('migration',ROOT/'tools/migrate_repo.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def g(target,*args,check=True):
    r=subprocess.run(['git','-C',str(target),*args],text=True,capture_output=True,timeout=20)
    if check and r.returncode:
        raise RuntimeError((r.stdout+r.stderr).strip() or f'git returnerede {r.returncode}')
    return r.stdout


def make_checksums(source):
    lines=[]
    for p in sorted(source.rglob('*')):
        if p.is_file() and p.name!='SHA256SUMS':
            lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(source).as_posix())
    (source/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf-8')


@unittest.skipUnless(shutil.which('git'),'Git er paakraevet til isolerede migrationstests')
class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
        self.source=self.base/'new repo';self.target=self.base/'old repo'
        self.source.mkdir();self.target.mkdir()
        self.old={'.gitignore':'config.env\n','README.md':'old README\n','setup.sh':'#!/bin/bash\necho old\n'}
        for name,value in self.old.items():(self.target/name).write_text(value,encoding='utf-8')
        (self.target/'personal-notes.md').write_text('user content retained\n',encoding='utf-8')
        g(self.target,'init','-b','main');g(self.target,'config','user.name','Isolated test')
        g(self.target,'config','user.email','test@example.invalid');g(self.target,'config','core.autocrlf','false')
        g(self.target,'remote','add','origin','https://example.invalid/private/repo.git')
        self.commit()
        (self.target/'config.env').write_text('HOSTNAME="custom-kept"\n',encoding='utf-8')
        (self.source/'tools').mkdir();(self.source/'scripts').mkdir()
        (self.source/'.gitignore').write_text('config.env\n__pycache__/\n',encoding='utf-8')
        (self.source/'README.md').write_text('new README\n',encoding='utf-8')
        (self.source/'scripts/setup.sh').write_text(self.old['setup.sh'],encoding='utf-8')
        (self.source/'tools/migration-baseline.json').write_text(json.dumps({'files':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in self.old.items()}}),encoding='utf-8')
        make_checksums(self.source)
        self.head=g(self.target,'rev-parse','HEAD')

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self):
        g(self.target,'add','--all');g(self.target,'commit','-m','fixture')

    def test_check_is_read_only(self):
        before={p.relative_to(self.target).as_posix():p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        actions,_=m.plan_migration(self.source,self.target)
        self.assertIn(('REMOVE-OLD-PATH','setup.sh'),actions)
        after={p.relative_to(self.target).as_posix():p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        self.assertEqual({k:v for k,v in before.items() if not k.startswith('.git/')},{k:v for k,v in after.items() if not k.startswith('.git/')})
        self.assertEqual(g(self.target,'rev-parse','HEAD'),self.head)
        self.assertEqual(len(list(self.base.glob('old repo-backup-*'))),0)

    def test_apply_preserves_history_config_and_extra_files(self):
        backup,actions=m.apply_plan(self.source,self.target)
        self.assertTrue((backup/'.git').is_dir())
        self.assertEqual((backup/'setup.sh').read_text(encoding='utf-8'),self.old['setup.sh'])
        self.assertEqual(g(self.target,'rev-parse','HEAD'),self.head)
        self.assertEqual(g(self.target,'remote','get-url','origin').strip(),'https://example.invalid/private/repo.git')
        self.assertEqual((self.target/'config.env').read_text(encoding='utf-8'),'HOSTNAME="custom-kept"\n')
        self.assertEqual((self.target/'personal-notes.md').read_text(encoding='utf-8'),'user content retained\n')
        self.assertTrue((self.target/'scripts/setup.sh').is_file())
        self.assertFalse((self.target/'setup.sh').exists())
        self.assertIn(('REMOVE-OLD-PATH','setup.sh'),actions)

    def test_committed_custom_change_is_not_overwritten(self):
        (self.target/'README.md').write_text('own README\n',encoding='utf-8');self.commit()
        with self.assertRaisesRegex(m.MigrationError,'egne/ukendte'):
            m.plan_migration(self.source,self.target)
        self.assertEqual((self.target/'README.md').read_text(encoding='utf-8'),'own README\n')
        self.assertEqual(len(list(self.base.glob('old repo-backup-*'))),0)

    def test_uncommitted_change_stops(self):
        (self.target/'setup.sh').write_text('uncommitted\n',encoding='utf-8')
        with self.assertRaisesRegex(m.MigrationError,'ikke ren'):
            m.plan_migration(self.source,self.target)

    def test_integrity_failure_stops(self):
        (self.source/'README.md').write_text('tampered\n',encoding='utf-8')
        with self.assertRaisesRegex(m.MigrationError,'Integritetskontrol'):
            m.plan_migration(self.source,self.target)

    def test_known_crlf_baseline_is_accepted(self):
        (self.target/'README.md').write_bytes(self.old['README.md'].replace('\n','\r\n').encode())
        # Nogle Windows/Git-installationer normaliserer CRLF allerede i indexet. I saa fald
        # findes der ingen separat byte-variant at committe, og testen er ikke meningsfuld paa vaerten.
        if not g(self.target,'status','--porcelain').strip():
            self.skipTest('Git normaliserede CRLF-varianten paa denne vaert')
        self.commit()
        actions,_=m.plan_migration(self.source,self.target)
        self.assertIn(('UPDATE','README.md'),actions)

    def test_nested_or_same_source_is_rejected(self):
        with self.assertRaisesRegex(m.MigrationError,'adskilte'):
            m.plan_migration(self.target,self.target)
        with self.assertRaisesRegex(m.MigrationError,'adskilte'):
            m.plan_migration(self.target/'nested',self.target)

    def test_link_in_target_stops(self):
        try:
            (self.target/'outside').symlink_to(self.base/'elsewhere')
        except OSError as exc:
            if os.name=='nt':
                self.skipTest(f'Windows tillader ikke symlink i denne session: {exc}')
            raise
        self.commit()
        with self.assertRaisesRegex(m.MigrationError,'Symlink'):
            m.plan_migration(self.source,self.target)

    def test_after_commit_second_migration_has_no_actions(self):
        m.apply_plan(self.source,self.target);self.commit()
        actions,_=m.plan_migration(self.source,self.target)
        self.assertEqual(actions,[])

    def test_protected_manifest_path_is_rejected(self):
        manifest=json.loads((self.source/'tools/migration-baseline.json').read_text(encoding='utf-8'))
        manifest['files']['.git/config']='0'*64
        (self.source/'tools/migration-baseline.json').write_text(json.dumps(manifest),encoding='utf-8');make_checksums(self.source)
        with self.assertRaisesRegex(m.MigrationError,'Beskyttet'):
            m.plan_migration(self.source,self.target)


if __name__=='__main__':
    unittest.main(verbosity=2)
