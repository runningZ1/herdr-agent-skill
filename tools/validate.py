#!/usr/bin/env python3
"""Validate public snapshots and skill completeness (maintenance: Python 3.11+)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

from collect import PUBLIC_SNAPSHOTS, VERSION, render_api_index, tui_methods, named_operations

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    'LICENSE', 'THIRD_PARTY_NOTICES.md', 'LICENSES/Apache-2.0.txt', 'SKILL.md', 'README.md',
    'scripts/herdr_agent.py', 'scripts/herdr_api.py', 'scripts/doctor.py',
    'references/core.md', 'references/app.md',
    'plugins/auto-name/herdr-plugin.toml', 'plugins/auto-name/main.py',
    'tests/test_adapter.py', 'tests/test_socket_api.py', 'tests/test_auto_name.py', 'tests/test_tools.py',
    'tools/build.py', 'tools/collect.py', 'tools/validate.py',
    *PUBLIC_SNAPSHOTS.values(),
)


def validate_snapshots(root):
    tui = json.loads((root / 'sources/herdr-api.schema.json').read_text(encoding='utf-8'))
    core = json.loads((root / 'sources/core-api.schema.json').read_text(encoding='utf-8'))
    app = json.loads((root / 'sources/app-commands.json').read_text(encoding='utf-8'))
    expected = render_api_index(tui, core, app)
    if (root / 'references/api-methods.md').read_text(encoding='utf-8') != expected:
        raise ValueError('Public API index differs from bundled snapshots; review tools/collect.py --publish output')
    return {'tui': len(tui_methods(tui)), 'core': len(named_operations(core['methods'], 'Core')),
            'app': len(named_operations(app, 'App'))}


def validate_plugins(root):
    manifests = sorted((root / 'plugins').rglob('herdr-plugin.toml'))
    if not manifests:
        raise ValueError('Missing bundled plugin manifest')
    plugins = []
    for manifest in manifests:
        data = tomllib.loads(manifest.read_text(encoding='utf-8'))
        for key in ('id', 'name', 'version'):
            if not isinstance(data.get(key), str) or not data[key]:
                raise ValueError('Missing plugin metadata ' + key + ': ' + str(manifest))
        commands = [entry['command'] for kind in ('startup', 'actions', 'events')
                    for entry in data.get(kind, []) if 'command' in entry]
        if not commands:
            raise ValueError('Plugin has no command entrypoint: ' + str(manifest))
        for command in commands:
            if not isinstance(command, list) or not command or not all(isinstance(arg, str) for arg in command):
                raise ValueError('Invalid plugin command: ' + str(manifest))
            # Bundled Python launchers refer to a real local source file. Refuse
            # paths escaping their plugin, including symlink entrypoints.
            entrypoints = [arg for arg in command if arg.endswith('.py')]
            if not entrypoints:
                raise ValueError('Bundled plugin lacks a Python entrypoint: ' + str(manifest))
            for entrypoint in entrypoints:
                target = (manifest.parent / entrypoint).resolve()
                if not target.is_relative_to(manifest.parent.resolve()) or not target.is_file():
                    raise ValueError('Missing or escaping plugin entrypoint: ' + str(manifest))
        plugins.append(data['id'])
    if len(plugins) != len(set(plugins)):
        raise ValueError('Duplicate bundled plugin IDs')
    return plugins


def validate(root=ROOT, live=False):
    root = Path(root)
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            raise ValueError('Missing required skill file: ' + relative)
    entry = (root / 'SKILL.md').read_text(encoding='utf-8')
    if not re.match(r'^---\r?\nname: herdr\r?\ndescription: .+', entry):
        raise ValueError('Invalid skill frontmatter')
    sources = []
    docs = [root / 'SKILL.md', root / 'README.md', *(root / 'references').glob('*.md')]
    for folder in ('scripts', 'tests', 'tools', 'plugins'):
        for path in sorted((root / folder).rglob('*.py')):
            if '__pycache__' in path.parts:
                continue
            compile(path.read_text(encoding='utf-8'), str(path), 'exec')
            sources.append(str(path.relative_to(root)))
    for path in docs:
        text = path.read_text(encoding='utf-8')
        if text.count('```') % 2:
            raise ValueError('Unclosed code fence: ' + str(path))
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in link or link.startswith('#'):
                continue
            target = path.parent / link.split('#')[0]
            if not target.exists():
                raise ValueError('Broken link in ' + str(path) + ': ' + link)
    snapshot_counts = validate_snapshots(root)
    plugins = validate_plugins(root)
    adapter = root / 'scripts/herdr_agent.py'
    version = subprocess.run([sys.executable, '-B', str(adapter), 'version'], capture_output=True, check=True, timeout=10)
    metadata = json.loads(version.stdout)['data']
    if version.stderr:
        raise ValueError('Version output contaminated stderr')
    if metadata['tool_version'] != VERSION:
        raise ValueError('Adapter/tool version mismatch: expected ' + VERSION)
    schema = subprocess.run([sys.executable, '-B', str(adapter), 'schema'], capture_output=True, check=True, timeout=10)
    capabilities = json.loads(schema.stdout)['data']
    if schema.stderr:
        raise ValueError('Schema output contaminated stderr')
    result = {'ok': True, 'version': VERSION, 'sources': sources, 'source_count': len(sources),
              'operations': len(capabilities['commands']), 'public_operations': snapshot_counts,
              'plugins': plugins, 'snapshots': 'passed', 'links': 'passed', 'syntax': 'passed', 'live': 'not_requested'}
    if live:
        # Only TUI is contacted. hc's apparently read-only commands may start
        # Core on demand; App commands can open a window and are never used here.
        raw = subprocess.check_output(['herdr', '--skill'], timeout=15).decode('utf-8').replace('\r\n', '\n').rstrip() + '\n'
        if raw != (root / 'references/official-skill.md').read_text(encoding='utf-8'):
            raise ValueError('Bundled TUI official skill differs from installed binary')
        for arguments in (['doctor'], ['workspace', 'list', '--limit', '1']):
            proc = subprocess.run([sys.executable, '-B', str(adapter), *arguments], capture_output=True, timeout=60)
            response = json.loads(proc.stdout)
            if proc.returncode or not response['ok'] or proc.stderr:
                raise ValueError('Live TUI verification failed: ' + str(response.get('error', {}).get('code')))
        result['live'] = 'TUI official_skill_match + doctor + bounded_workspace_list passed'
        result['official_skill_sha256'] = hashlib.sha256(raw.encode()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Also perform read-only TUI checks; never start Core or App')
    args = parser.parse_args()
    try:
        result = validate(live=args.live)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        sys.stdout.write(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=True) + '\n')
        return 1
    sys.stdout.write(json.dumps(result, ensure_ascii=True, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
