#!/usr/bin/env python3
"""Read-only bounded diagnostics for Herdr TUI; Python standard library only."""
import argparse, json, os, shutil, sys
from pathlib import Path
sys.dont_write_bytecode = True
from herdr_agent import Backend, Failure, clean

def run(binary, args, timeout, limit):
    try:
        backend = Backend.__new__(Backend)
        backend.binary, backend.timeout = Path(binary).resolve(), timeout
        value = backend.raw(args)
        try:
            value = json.dumps(clean(json.loads(value)), ensure_ascii=True)
        except ValueError:
            value = clean(value)
        item = {'args': args, 'exit_code': 0, 'stdout': value[:limit]}
        if len(value) > limit:
            item['stdout_truncated'] = True
        return item
    except Failure as error:
        return {'args': args, 'exit_code': 1, 'error': error.code, 'details': clean(error.details)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, default=10, help='Seconds per command, maximum 60')
    parser.add_argument('--max-chars', type=int, default=4000, help='Characters per stdout/stderr')
    args = parser.parse_args()
    if not 0 < args.timeout <= 60 or not 256 <= args.max_chars <= 20000:
        parser.error('timeout must be in (0,60]; max-chars must be in [256,20000]')
    candidate = os.environ.get('HERDR_BIN_PATH') or shutil.which('herdr')
    binary = str(Path(candidate).resolve()) if candidate else None
    inside = os.environ.get('HERDR_ENV') == '1'
    report = {'product':'Herdr TUI', 'binary':binary, 'managed_pane':inside,
              'context':{key:os.environ.get(key) for key in
                         ['HERDR_WORKSPACE_ID','HERDR_TAB_ID','HERDR_PANE_ID']}, 'checks':[]}
    if not binary or not Path(binary).is_file() or Path(binary).name.lower() not in ['herdr', 'herdr.exe']:
        report['error'] = 'herdr is not on PATH; see references/setup-recovery.md'
        code = 1
    else:
        groups = [['--version']]
        if inside:
            groups += [['status'],['config','check'],['pane','current','--current']]
        else:
            report['note'] = 'Outside Herdr: skipped all runtime session inspection. Do not forge HERDR_ENV.'
        report['checks'] = [run(binary, group, args.timeout, args.max_chars) for group in groups]
        code = int(any(x.get('exit_code') != 0 for x in report['checks']))
    print(json.dumps(clean(report), ensure_ascii=True, indent=2))
    return code

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
