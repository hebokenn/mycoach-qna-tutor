#!/usr/bin/env python3
"""Install the complete skill locally, preserving existing installations by default."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/mycoach-qna-tutor'

def verify(source):
    manifest = json.loads((source/'PACKAGE-SHA256.json').read_text(encoding='utf-8'))
    for relative, expected in manifest.items():
        file = (source/relative).resolve()
        if not file.is_relative_to(source.resolve()) or not file.is_file():
            raise ValueError(f'Invalid manifest path: {relative}')
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError(f'File checksum mismatch: {relative}')

def install(parent, backup=False):
    verify(SOURCE)
    parent = parent.expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    target = parent/SOURCE.name
    old = None
    if target.exists() or target.is_symlink():
        if not backup:
            raise ValueError(f'{target} already exists. Use --backup-existing to preserve it and install this version.')
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        old = parent/(SOURCE.name+'.backup-'+stamp)
        target.rename(old)
    try:
        shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
        verify(target)
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if old is not None:
            old.rename(target)
        raise
    return {'installed': str(target), 'backup': str(old) if old else None}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['codex'], default='codex', help='WorkBuddy uses the dedicated ZIP uploader, not an assumed filesystem path.')
    parser.add_argument('--skills-dir', type=Path, default=Path.home()/'.agents/skills')
    parser.add_argument('--backup-existing', action='store_true')
    args=parser.parse_args()
    try:
        result=install(args.skills_dir,args.backup_existing)
    except (OSError,ValueError) as error:
        parser.exit(2,str(error)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
