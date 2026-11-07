#!/usr/bin/env python3
"""Validate this self-contained skill without third-party dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT, live=False):
    entry=(root/'SKILL.md').read_text(encoding='utf-8')
    if not re.match(r'^---\r?\nname: herdr\r?\ndescription: .+',entry):
        raise ValueError('Invalid skill frontmatter')
    sources=[]
    docs=[root/'SKILL.md',root/'README.md',*(root/'references').glob('*.md')]
    for folder in ['scripts','tests','tools']:
        for path in sorted((root/folder).glob('*.py')):
            compile(path.read_text(encoding='utf-8'),str(path),'exec')
            sources.append(str(path.relative_to(root)))
    for path in docs:
        text=path.read_text(encoding='utf-8')
        if text.count('```')%2: raise ValueError('Unclosed code fence: '+str(path))
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in link or link.startswith('#'): continue
            target=path.parent/link.split('#')[0]
            if not target.exists(): raise ValueError('Broken link in '+str(path)+': '+link)
    adapter=root/'scripts/herdr_agent.py'
    version=subprocess.run([sys.executable,'-B',str(adapter),'version'],capture_output=True,check=True,timeout=10)
    metadata=json.loads(version.stdout)['data']
    if version.stderr: raise ValueError('Version output contaminated stderr')
    schema=subprocess.run([sys.executable,'-B',str(adapter),'schema'],capture_output=True,check=True,timeout=10)
    capabilities=json.loads(schema.stdout)['data']
    if schema.stderr: raise ValueError('Schema output contaminated stderr')
    result={'ok':True,'version':metadata['tool_version'],'sources':sources,'source_count':len(sources),'operations':len(capabilities['commands']),'links':'passed','syntax':'passed','live':'not_requested'}
    if live:
        raw=subprocess.check_output(['herdr','--skill'],timeout=15).decode('utf-8')
        if raw!=(root/'references/official-skill.md').read_text(encoding='utf-8'):
            raise ValueError('Bundled official skill differs from installed binary')
        for args in [['doctor'],['workspace','list','--limit','1']]:
            proc=subprocess.run([sys.executable,'-B',str(adapter),*args],capture_output=True,timeout=60)
            response=json.loads(proc.stdout)
            if proc.returncode or not response['ok'] or proc.stderr:
                raise ValueError('Live verification failed: '+str(response.get('error',{}).get('code')))
        result['live']='official_skill_match + doctor + bounded_workspace_list passed'
        result['official_skill_sha256']=hashlib.sha256(raw.encode()).hexdigest()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Also perform read-only checks against installed Herdr')
    args=parser.parse_args()
    try: result=validate(live=args.live)
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        sys.stdout.write(json.dumps({'ok':False,'error':str(error)},ensure_ascii=True)+'\n')
        return 1
    sys.stdout.write(json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    return 0


if __name__=='__main__': raise SystemExit(main())
