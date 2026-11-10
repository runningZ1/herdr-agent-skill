#!/usr/bin/env python3
"""Collect static TUI/Core/App metadata; publish reviewed snapshots with --publish.

Default output is sources/current, which is deliberately excluded from packages.
No server queries, application launch, or exact installed-version gate are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '2.0.0'
PUBLIC_SNAPSHOTS = {
    'herdr-api.schema.json': 'sources/herdr-api.schema.json',
    'core-api.schema.json': 'sources/core-api.schema.json',
    'app-commands.json': 'sources/app-commands.json',
    'official-skill.md': 'references/official-skill.md',
    'official-core-skill.md': 'references/official-core-skill.md',
    'official-app-skill.md': 'references/official-app-skill.md',
    'installed-cli-help.md': 'references/installed-cli-help.md',
    'api-methods.md': 'references/api-methods.md',
}


def static_command(binary, arguments, timeout=20):
    """Run explicit static commands directly, never through the live adapter."""
    result = subprocess.run([binary, *arguments], capture_output=True, timeout=timeout)
    if result.returncode:
        raise ValueError('Static command failed: ' + ' '.join([Path(binary).name, *arguments]) +
                         ' (exit ' + str(result.returncode) + ')')
    return result.stdout.decode('utf-8').replace('\r\n', '\n').rstrip() + '\n'


def help_children(text, executable, parent=()):
    """Discover only literal command names advertised by this help document."""
    children = set()
    in_commands = False
    for line in text.splitlines():
        if line.strip() == 'Commands:':
            in_commands = True
            continue
        if in_commands:
            if line and not line[0].isspace():
                in_commands = False
            else:
                match = re.match(r'^  ([a-z][a-z0-9_-]*)(?:\s{2,}|\s*$)', line)
                if match and match[1] != 'help':
                    children.add(match[1])
        if not parent:
            # The custom root help of herdr/hc uses usage lines and sections
            # instead of Clap's Commands block. Never parse prose or examples.
            if executable == 'herdr':
                match = re.match(r'^\s*(?:Usage:\s*)?herdr ([a-z][a-z0-9_-]*)(?:\s|$)', line)
                if match:
                    children.add(match[1])
            elif executable == 'hc':
                match = re.match(r'^  ([a-z][a-z0-9_-]*)(?=[ \t])', line)
                if match and re.match(r'^  [a-z][a-z0-9_-]*(?:\s{2,}|\s+(?:<|\[|[a-z]+(?:\||\s{2,})))', line):
                    children.add(match[1])
    return sorted(children)


def collect_help(binary, executable, root_help):
    pending = [()]
    # The custom TUI root help omits these public groups; they are present in
    # the installed CLI and the previous collector's public help inventory.
    if executable == 'herdr':
        pending.extend([('plugin',), ('terminal',)])
    documents = {}
    while pending:
        path = pending.pop(0)
        if path in documents:
            continue
        text = root_help if not path else static_command(binary, [*path, '--help'])
        documents[path] = text
        for child in help_children(text, executable, path):
            pending.append((*path, child))
        if len(documents) + len(pending) > 512:
            raise ValueError('Unexpectedly large help command tree: ' + executable)
    return '\n'.join('## ' + ' '.join([executable, *path, '--help']) +
                     '\n\n```text\n' + text + '```\n' for path, text in documents.items())


def tui_methods(schema):
    methods = {}
    for variant in schema['schemas']['request']['oneOf']:
        properties = variant['properties']
        method = properties['method']['const']
        if method in methods:
            raise ValueError('Duplicate TUI method: ' + method)
        methods[method] = properties.get('params', {})
    if not methods:
        raise ValueError('Empty TUI method schema')
    return methods


def named_operations(entries, label):
    operations = {}
    for entry in entries:
        name = entry['name']
        if name in operations:
            raise ValueError('Duplicate ' + label + ' operation: ' + name)
        operations[name] = entry
    if not operations:
        raise ValueError('Empty ' + label + ' operations')
    return operations


def render_api_index(tui, core, app):
    """Render every public operation; presence documents discovery, not live tests."""
    tui_ops = tui_methods(tui)
    core_ops = named_operations(core['methods'], 'Core')
    app_ops = named_operations(app, 'App')
    lines = [
        '# 公开 API 与操作索引', '',
        '由 `tools/collect.py --publish` 从安装的官方 CLI 静态导出，技能版本 ' + VERSION + '。', '',
        '本索引逐项覆盖三份公开快照；列入索引表示已发现操作，不表示已执行或实测。参数、必填项、枚举和返回值以对应快照为准。', '',
        '## TUI socket API', '',
        '公开快照：[herdr-api.schema.json](../sources/herdr-api.schema.json)。协议 ' +
        str(tui.get('protocol', 'unknown')) + '；共 ' + str(len(tui_ops)) + ' 个方法。', '',
        '所有方法可通过 [herdr_api.py](../scripts/herdr_api.py) 的 schema 驱动通道调用；它们不等同于 typed adapter 的便捷操作。', '',
        '离线发现：`python -B scripts/herdr_api.py schema --method METHOD`。调用：`python -B scripts/herdr_api.py call METHOD --file params.json`；写调用默认仅生成 dry-run 计划，执行需 `--commit --confirm HASH`。', '',
        '顺序批次使用 `batch --file requests.json`（`[{"method": "...", "params": {...}}, ...]`）；普通请求各自连接，SSH Agent 登记保留独立租约。事件订阅使用 `subscribe --file params.json`，以 timeout/max-events 限界。批量非事务，非幂等操作不自动重试。', '',
        '实时通道要求真正的 TUI 上下文（`HERDR_ENV=1` 且无 `HC_TERMINAL_ID`）；Core/App 终端不能借用继承标记冒充 TUI。', '',
    ]
    for name, params in sorted(tui_ops.items()):
        lines.append('- `' + name + '` → `' + json.dumps(params, ensure_ascii=False, sort_keys=True) + '`')
    lines.extend(['', '## Core JSON-RPC API', '',
                  '公开快照：[core-api.schema.json](../sources/core-api.schema.json)。OpenRPC ' +
                  str(core.get('openrpc', 'unknown')) + '；共 ' + str(len(core_ops)) + ' 个方法。', '',
                  'Core 与 TUI 独立；原生 `hc` 操作与 Core JSON-RPC 方法也不是一一同名。此处提供完整协议发现，不声明自动适配所有方法。', ''])
    for name, entry in sorted(core_ops.items()):
        lines.append('- `' + name + '` → `' + json.dumps(entry.get('params', []), ensure_ascii=False, sort_keys=True) + '`')
    lines.extend(['', '## App commands', '',
                  '公开快照：[app-commands.json](../sources/app-commands.json)。共 ' + str(len(app_ops)) + ' 个公开命令。', '',
                  '调用方式：`herdr-app do <command> [args]`。以下参数由静态 `herdr-app commands` 导出；执行命令需单独判断影响。', ''])
    for name, entry in sorted(app_ops.items()):
        lines.append('- `' + name + '` → `' + json.dumps(entry.get('args', []), ensure_ascii=False, sort_keys=True) + '`')
    return '\n'.join(lines) + '\n'


def snapshot_diff(snapshots, root=ROOT):
    differences = []
    for name, relative in PUBLIC_SNAPSHOTS.items():
        target = root / relative
        current = snapshots[name].replace('\r\n', '\n').encode('utf-8')
        previous = target.read_bytes().replace(b'\r\n', b'\n') if target.exists() else None
        if previous != current:
            differences.append({'path': relative, 'status': 'added' if previous is None else 'changed',
                                'before_sha256': hashlib.sha256(previous).hexdigest() if previous is not None else None,
                                'after_sha256': hashlib.sha256(current).hexdigest(),
                                'before_bytes': len(previous) if previous is not None else 0,
                                'after_bytes': len(current)})
    return differences


def collect():
    binaries = {}
    for name, variable in [('herdr', 'HERDR_BIN_PATH'), ('hc', 'HERDR_CORE_BIN_PATH'),
                           ('herdr-app', 'HERDR_APP_BIN_PATH')]:
        candidate = os.environ.get(variable) or shutil.which(name)
        if not candidate:
            raise ValueError('Missing static metadata binary: ' + name)
        binaries[name] = candidate
    # Read each root help before discovering any child; every help request uses
    # --help explicitly, never a bare command (which can start a runtime).
    roots = {name: static_command(binary, ['--help']) for name, binary in binaries.items()}
    versions = {name: static_command(binary, ['--version']).strip() for name, binary in binaries.items()}
    tui = json.loads(static_command(binaries['herdr'], ['api', 'schema', '--json']))
    core = json.loads(static_command(binaries['hc'], ['schema']))
    app = json.loads(static_command(binaries['herdr-app'], ['commands']))
    snapshots = {
        'herdr-api.schema.json': json.dumps(tui, ensure_ascii=True, indent=2) + '\n',
        'core-api.schema.json': json.dumps(core, ensure_ascii=True, indent=2) + '\n',
        'app-commands.json': json.dumps(app, ensure_ascii=True, indent=2) + '\n',
        'official-skill.md': static_command(binaries['herdr'], ['--skill']),
        'official-core-skill.md': static_command(binaries['hc'], ['--skill']),
        'official-app-skill.md': static_command(binaries['herdr-app'], ['--skill']),
        'api-methods.md': render_api_index(tui, core, app),
    }
    help_text = ['# 已安装 CLI 静态帮助', '',
                 '由 `tools/collect.py` 静态采集。所有帮助请求都显式使用 `--help`；不查询运行时，不启动 Core 或 App。', '',
                 '版本：' + '；'.join('`' + value + '`' for value in versions.values()) + '。', '']
    for name in ['herdr', 'hc']:
        help_text.append(collect_help(binaries[name], name, roots[name]))
    # App's custom help advertises no per-command --help contract. Its entire
    # public command tree comes from the safe, static `commands` export above.
    help_text.extend(['## herdr-app --help', '', '```text', roots['herdr-app'].rstrip(), '```', '',
                      'App 根帮助未声明逐命令 `--help`；完整公开操作与参数见 [API 索引](api-methods.md) 和 `herdr-app commands` 静态快照。', ''])
    snapshots['installed-cli-help.md'] = '\n'.join(help_text)
    return snapshots, versions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'sources' / 'current')
    parser.add_argument('--publish', action='store_true', help='Explicitly replace the bundled public snapshots and API index')
    args = parser.parse_args()
    try:
        output = args.output_dir.resolve()
        # A custom staging location must not bypass the explicit publish flag.
        if output == ROOT.resolve() or any((output / name).resolve() == (ROOT / relative).resolve()
                                           for name, relative in PUBLIC_SNAPSHOTS.items()):
            raise ValueError('Output directory overlaps published snapshots; use --publish')
        snapshots, versions = collect()
        differences = snapshot_diff(snapshots)
        output.mkdir(parents=True, exist_ok=True)
        for name, text in snapshots.items():
            (output / name).write_text(text, encoding='utf-8', newline='\n')
        if args.publish:
            for name, relative in PUBLIC_SNAPSHOTS.items():
                (ROOT / relative).write_text(snapshots[name], encoding='utf-8', newline='\n')
        print(json.dumps({'ok': True, 'tool_version': VERSION, 'versions': versions,
                          'output_dir': str(output), 'published': args.publish,
                          'differences': differences}, ensure_ascii=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
