#!/usr/bin/env python3
"""Kontrolleret filopdatering af et eksisterende Git-repo; ingen commit/push.

Koer fra den NYE udpakkede pakke, ikke inde fra maalmappen. --check er
laesende. --apply tager en fuld backup ved siden af repoet foer filkopiering.
.git og den lokale config.env bevares. Kun kendte 1.1.0-filer maa overskrives
eller fjernes; egne konflikter medfoerer stop til manuel sammenfletning.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

PROTECTED = {'.git', 'config.env'}
IGNORED_PARTS = {'.git', '__pycache__', '.pytest_cache', '.venv'}

class MigrationError(RuntimeError):
    pass

def digest(path: Path, normalize: bool = False) -> str:
    raw = path.read_bytes()
    if normalize:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()

def beneath(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

def safe_rel(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value or not path.parts:
        raise MigrationError(f'Usikker relativ sti: {value}')
    if path.parts[0] in PROTECTED:
        raise MigrationError(f'Beskyttet sti i filplan: {value}')
    return path

def git(target: Path, *args: str) -> str:
    p = subprocess.run(['git', '-C', str(target), *args], capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=30)
    if p.returncode:
        raise MigrationError(p.stderr.strip() or 'Git-kontrol fejlede')
    return p.stdout

def source_files(source: Path) -> dict[str, Path]:
    out = {}
    for p in source.rglob('*'):
        rel = p.relative_to(source)
        if any(part in IGNORED_PARTS for part in rel.parts):
            continue
        if p.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(p)):
            raise MigrationError(f'Symlink/junction i kilde: {rel}')
        if not p.is_file() or p.suffix == '.pyc':
            continue
        if rel.as_posix() == 'config.env':
            continue
        safe_rel(rel.as_posix())
        out[rel.as_posix()] = p
    return out

def verify_source(source: Path, files: dict[str, Path]) -> None:
    checksum = source / 'SHA256SUMS'
    if not checksum.is_file():
        raise MigrationError('Kildepakken mangler SHA256SUMS')
    seen = set()
    for line in checksum.read_text(encoding='utf-8').splitlines():
        if not line:
            continue
        if '  ' not in line:
            raise MigrationError('Ugyldigt checksumformat')
        expected, rel = line.split('  ', 1)
        safe_rel(rel)
        if rel not in files or rel in seen or digest(files[rel]) != expected:
            raise MigrationError(f'Integritetskontrol fejlede: {rel}')
        seen.add(rel)
    wanted = set(files) - {'SHA256SUMS'}
    if seen != wanted:
        raise MigrationError('SHA256SUMS dækker ikke praecis kildepakkens filer')

def plan_migration(source: Path, target: Path) -> tuple[list[tuple[str, str]], dict[str, Path]]:
    source, target = source.resolve(), target.resolve()
    if source == target or beneath(source, target) or beneath(target, source):
        raise MigrationError('Kilde og maal skal vaere adskilte mapper, ikke inde i hinanden')
    if not (target / '.git').is_dir() or (target / '.git').is_symlink():
        raise MigrationError('Maalet skal vaere et almindeligt eksisterende Git-repo med .git-mappe')
    top = Path(git(target, 'rev-parse', '--show-toplevel').strip()).resolve()
    if top != target:
        raise MigrationError('Angiv repo-roden som --target')
    dirty = git(target, 'status', '--porcelain', '--untracked-files=normal')
    if dirty.strip():
        raise MigrationError('Arbejdsmappen er ikke ren. Commit/gennemgaa egne aendringer foerst:\n' + dirty)
    # Afvis links, saa filkopiering/backup ikke foelger dem ud af repoet.
    for p in target.rglob('*'):
        if p.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(p)):
            raise MigrationError(f'Symlink/junction i maal: {p.relative_to(target)}')
    files = source_files(source)
    verify_source(source, files)
    baseline = json.loads((source / 'tools/migration-baseline.json').read_text(encoding='utf-8'))['files']
    for rel in baseline:
        safe_rel(rel)
    actions, conflicts = [], []
    for rel, p in sorted(files.items()):
        old = target / rel
        if old.exists():
            if not old.is_file():
                conflicts.append(rel + ' (er ikke en fil)')
                continue
            if digest(old) == digest(p):
                continue
            if digest(old, True) == digest(p, True) or baseline.get(rel) == digest(old, True):
                actions.append(('UPDATE', rel))
            else:
                conflicts.append(rel + ' (egne/ukendte aendringer)')
        else:
            # En parent skal ikke vaere en almindelig fil.
            parent = old.parent
            while parent != target:
                if parent.exists() and not parent.is_dir():
                    conflicts.append(rel + ' (parent er ikke en mappe)')
                    break
                parent = parent.parent
            else:
                actions.append(('ADD', rel))
    for rel, expected in sorted(baseline.items()):
        old = target / rel
        if rel not in files and old.exists():
            if not old.is_file() or digest(old, True) != expected:
                conflicts.append(rel + ' (gammel sti med egne aendringer)')
            else:
                actions.append(('REMOVE-OLD-PATH', rel))
    if conflicts:
        raise MigrationError('Ingen filer aendret. Gennemgaa disse konflikter manuelt:\n  ' + '\n  '.join(conflicts))
    return actions, files

def apply_plan(source: Path, target: Path) -> tuple[Path | None, list[tuple[str, str]]]:
    actions, files = plan_migration(source, target)
    if not actions:
        return None, actions
    # Fuld lokal backup inkl. Git-historik; vi aendrer aldrig repoets .git.
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = target.parent / f'{target.name}-backup-{stamp}-{uuid.uuid4().hex[:8]}'
    shutil.copytree(target, backup)
    try:
        for action, rel in actions:
            dest = target / rel
            if action == 'REMOVE-OLD-PATH':
                dest.unlink()
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(files[rel], dest)
        # Fjern kun mapper, der nu er tomme; aldrig .git.
        for p in sorted(target.rglob('*'), key=lambda x: len(x.parts), reverse=True):
            if '.git' in p.relative_to(target).parts:
                continue
            if p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass
    except Exception as exc:
        raise MigrationError(f'Kopiering stoppede: {exc}. Fuld backup findes: {backup}') from exc
    return backup, actions

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='Eksisterende Git-repo paa din PC')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='Vis kun filplanen (standard)')
    modes.add_argument('--apply', action='store_true', help='Backup og kopier; ingen commit/push')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    target = args.target.expanduser().resolve()
    try:
        if args.apply:
            backup, actions = apply_plan(source, target)
            print('Backup:', backup or 'Ingen aendringer; backup ikke noedvendig')
        else:
            actions, _ = plan_migration(source, target)
        for action, rel in actions:
            print(f'{action:16} {rel}')
        print(f'\n{len(actions)} filhandlinger. .git og lokal config.env bevares.')
        print('Ingen commit, push eller GitHub-synlighed er aendret.')
        print('Naeste: gennemgaa git diff, stage og commit fra dit eksisterende repo.')
        return 0
    except (MigrationError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'[STOP] {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
