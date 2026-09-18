#!/usr/bin/env python3
"""Generer SHA256SUMS for versionerede leverancefiler; aldrig lokal config.env."""
from pathlib import Path
import hashlib
ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.pytest_cache', '.venv'}

def included_files(root=ROOT):
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root)
        if any(x in SKIP for x in rel.parts) or p.is_symlink() or not p.is_file():
            continue
        if rel.as_posix() in ('SHA256SUMS', 'config.env') or p.suffix in ('.pyc', '.log', '.zip') or p.name.endswith('.tar.gz'):
            continue
        yield p

def main():
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix() for p in included_files()]
    (ROOT/'SHA256SUMS').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print(f'SHA256SUMS: {len(lines)} filer. Lokal config.env og .git er udeladt.')

if __name__ == '__main__':
    main()
