#!/usr/bin/env python3
"""Explicit publication boundary shared by checksums, source ZIP and public audit."""
from pathlib import Path

ROOT_FILES = {'README.md', 'CHANGELOG.md', 'START_HER.html', 'VERSION',
              '.gitattributes', '.gitignore', 'requirements-site.txt'}
EXTENSIONS = {
    'docs': {'.md', '.txt'}, 'evidence': {'.md', '.json', '.png'},
    'scripts': {'.sh', '.py', '.md'}, 'tests': {'.py', '.json'},
    'tools': {'.py'}, 'site': {'.css', '.js', '.html', '.json', '.svg', '.md'},
    'reports': {'.docx'},
}
SKIP_PARTS = {'.git', '__pycache__', '.pytest_cache', '.venv', '.venv-site', '_site',
              'node_modules', 'site-preview', 'playwright-report'}


def included_files(root: Path):
    """Yield allowed source files. Local additions outside these types never ship."""
    root = Path(root).resolve()
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root)
        if any(s in SKIP_PARTS or (s.startswith('.') and s not in {'.github', '.gitattributes', '.gitignore'}) for s in rel.parts):
            continue
        name = rel.as_posix()
        if name in {'config.env', 'SHA256SUMS'} or not p.is_file():
            continue
        allowed = name in ROOT_FILES or name in {'config/config.env.example', 'keys/secureadmin.pub', '.github/workflows/pages.yml'}
        if len(rel.parts) > 1 and rel.parts[0] in EXTENSIONS:
            allowed = p.suffix in EXTENSIONS[rel.parts[0]]
        if not allowed:
            continue
        if p.is_symlink() or any(a.is_symlink() for a in p.parents if a != root.parent):
            raise ValueError(f'Symbolic link not allowed in publication: {name}')
        yield p
