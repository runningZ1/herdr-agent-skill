#!/usr/bin/env python3
"""Build a source-inclusive skill package; exclude local history and evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from validate import ROOT, validate
from collect import PUBLIC_SNAPSHOTS, VERSION


def package_files(root=ROOT):
    """Package runtime assets and explicit public snapshots, never evidence."""
    files = [root / name for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md',
                                     'LICENSES/Apache-2.0.txt', 'SKILL.md', 'README.md')]
    for folder in ('scripts', 'references', 'tests', 'tools', 'plugins'):
        for path in (root / folder).rglob('*'):
            if not path.is_file() or any(part in ('__pycache__', '.pytest_cache', '.git') for part in path.parts):
                continue
            if path.name == '.env' or path.name.startswith('.env.') or path.suffix == '.log':
                continue
            if path.suffix in ('.pyc', '.pyo'):
                continue
            if folder == 'plugins' or path.suffix in ('.py', '.md', '.toml', '.json'):
                files.append(path)
    files.extend(root / relative for relative in PUBLIC_SNAPSHOTS.values() if relative.startswith('sources/'))
    if any(not path.resolve().is_relative_to(root.resolve()) for path in files):
        raise ValueError('Refusing to package a source link outside this skill')
    if any(not path.is_file() for path in files):
        raise ValueError('Missing required package source')
    return sorted(set(files))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'dist')
    parser.add_argument('--verify',action='store_true',help='Extract inside output directory and run packaged contract tests')
    args=parser.parse_args()
    validate()
    files=package_files()
    destination=args.output_dir.resolve()
    destination.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='herdr-',suffix='.tmp',dir=destination)
    os.close(fd)
    temporary=Path(name)
    try:
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(set(files)):
                info=zipfile.ZipInfo('herdr/'+path.relative_to(ROOT).as_posix(),date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip(): raise ValueError('Archive integrity failure')
        target=destination/'herdr.zip'
        os.replace(temporary,target)
        sha=hashlib.sha256(target.read_bytes()).hexdigest()
        (destination/'SHA256SUMS.txt').write_text(sha+'  herdr.zip\n',encoding='ascii')
    finally:
        if temporary.exists(): temporary.unlink()
    verification='not_requested'
    if args.verify:
        with tempfile.TemporaryDirectory(prefix='package-check-',dir=destination) as folder:
            unpacked=Path(folder).resolve()
            if unpacked.parent!=destination: raise ValueError('Unsafe temporary extraction location')
            with zipfile.ZipFile(target) as archive:
                if any(not name.startswith('herdr/') or '..' in Path(name).parts for name in archive.namelist()):
                    raise ValueError('Unsafe archive path')
                archive.extractall(unpacked)
            result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=unpacked/'herdr',capture_output=True,timeout=120)
            if result.returncode: raise ValueError('Packaged contract tests failed: '+(result.stdout+result.stderr).decode('utf-8',errors='replace')[-4000:])
            verification='packaged contract, socket API, plugin, and maintenance tool tests passed'
    print(json.dumps({'ok':True,'version':VERSION,'archive':str(target),'files':len(files),'sha256':sha,'verification':verification},ensure_ascii=True))


if __name__=='__main__': main()
