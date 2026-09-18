#!/usr/bin/env python3
"""Create a SHA-256 manifest of explicit deliverables; exclude local environment."""
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_files import included_files as public_files


def included_files(root=ROOT):
    return public_files(Path(root))


def main():
    rows = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}' for p in included_files()]
    (ROOT / 'SHA256SUMS').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')
    print(f'SHA256SUMS: {len(rows)} kildefiler; lokal config.env, .git og _site er udeladt.')


if __name__ == '__main__':
    main()
