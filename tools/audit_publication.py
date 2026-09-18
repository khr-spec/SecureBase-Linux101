#!/usr/bin/env python3
"""Read-only checks for selected secrets, never a claim of comprehensive auditing.

--history additionally scans reachable local Git objects. It never fetches, changes
visibility, rewrites history, rotates credentials or interprets screenshot pixels.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys
from public_files import included_files

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    ('Private key block', re.compile(r'^-----BEGIN [A-Z ]*PRIVATE KEY-----\s*$', re.M)),
    ('GitHub token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b')),
    ('AWS access key identifier', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
]
BINARY = {'.png', '.jpg', '.jpeg', '.docx', '.pdf', '.gz', '.zip'}


def findings(raw: bytes):
    if b'\0' in raw:
        return []
    text = raw.decode('utf-8', errors='replace')
    return [label for label, regex in PATTERNS if regex.search(text)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    bad = []
    count = 0
    for p in included_files(ROOT):
        if p.suffix in BINARY:
            continue
        count += 1
        bad.extend(f'{p.relative_to(ROOT)}: {f}' for f in findings(p.read_bytes()))
    print(f'[INFO] {count} aktuelle tekstfiler kontrolleret efter udvalgte hemmelighedsformater.')
    print('[INFO] Public key er tilsigtet. Billeder og Word-rapport er ikke anonymiseret.')
    if args.history:
        try:
            proc = subprocess.run(['git', 'rev-list', '--objects', '--all'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
            objects = 0
            for line in proc.stdout.splitlines():
                oid, sep, filename = line.partition(' ')
                if not sep or Path(filename).suffix.lower() in BINARY:
                    continue
                typ = subprocess.run(['git', 'cat-file', '-t', oid], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
                if typ != 'blob':
                    continue
                data = subprocess.run(['git', 'cat-file', 'blob', oid], cwd=ROOT, capture_output=True, check=True).stdout
                objects += 1
                bad.extend(f'Git {oid[:12]} {filename}: {f}' for f in findings(data))
            identities = subprocess.run(['git', 'log', '--all', '--format=%an <%ae>'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True).stdout
            print(f'[INFO] {objects} tekstlige Git-objekter kontrolleret (kun lokalt naaelige refs).')
            print('[INFO] Forfatteridentiteter i historikken — gennemgaa personoplysninger:')
            for identity in sorted(set(identities.splitlines())):
                print('  ' + identity)
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f'[FAIL] Historikkontrollen kunne ikke gennemfoeres: {exc}', file=sys.stderr)
            return 2
    else:
        print('[INFO] Git-historik er IKKE kontrolleret. Brug --history i det rigtige repo.')
    for result in bad:
        print('[FUND] ' + result)
    if bad:
        print('[STOP] Gennemgaa fundene foer publicering. Fund er ikke automatisk bekraeftede secrets.')
        return 1
    print('[OK] Ingen match for de valgte hemmelighedsformater. Det er ikke en fuld privacy-/secret-audit.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
