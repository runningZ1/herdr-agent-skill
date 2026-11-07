#!/usr/bin/env python3
"""Export static metadata from the installed official binary, without replacing references."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
from herdr_agent import Backend, Failure, clean


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'sources'/'current')
    args=parser.parse_args()
    try:
        backend=Backend(15)
        # All of these requests are static discovery, even outside Herdr panes.
        official=backend.raw(['--skill'])
        schema=json.loads(backend.raw(['api','schema','--json']))
        groups=['workspace','worktree','tab','pane','agent','terminal','notification','session','machine','server','integration','plugin','config','channel','api']
        help_text='\n\n'.join('## '+group+'\n\n```text\n'+backend.raw([group,'--help'])+'\n```' for group in groups)
        args.output_dir.mkdir(parents=True,exist_ok=True)
        (args.output_dir/'official-skill.md').write_text(official,encoding='utf-8')
        (args.output_dir/'herdr-api.schema.json').write_text(json.dumps(schema,ensure_ascii=True,indent=2),encoding='utf-8')
        (args.output_dir/'installed-cli-help.md').write_text(help_text,encoding='utf-8')
        print(json.dumps({'ok':True,'version':backend.version,'output_dir':str(args.output_dir.resolve()),'official_sha256':hashlib.sha256(official.encode()).hexdigest()},ensure_ascii=True))
        return 0
    except (Failure,ValueError,OSError) as error:
        print(json.dumps({'ok':False,'error':clean(str(error))},ensure_ascii=True))
        return 1


if __name__=='__main__': raise SystemExit(main())
