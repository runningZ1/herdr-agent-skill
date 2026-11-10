"""Offline regression boundaries for publication, help discovery and packaging."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import collect
import build
import validate


def snapshots():
    tui = {'protocol': 22, 'schemas': {'request': {'oneOf': [
        {'properties': {'method': {'const': 'ping'}, 'params': {'type': 'object'}}}
    ]}}}
    core = {'openrpc': '1.3.2', 'methods': [{'name': 'hello', 'params': []}]}
    app = [{'name': 'space.new', 'args': []}]
    return tui, core, app


class CollectionTests(unittest.TestCase):
    def test_help_recurses_using_only_explicit_help(self):
        root_help = 'Usage: hc <command>\n  server start|stop|status   Manage core\n'
        responses = {
            ('server', '--help'): 'Commands:\n  stop    Stop core\n  status  Inspect core\n  help    Show help\nOptions:\n  --json  JSON\n',
            ('server', 'stop', '--help'): 'Usage: hc server stop [OPTIONS]\n',
            ('server', 'status', '--help'): 'Usage: hc server status [OPTIONS]\n',
        }
        requests = []

        def run(binary, arguments):
            requests.append(tuple(arguments))
            return responses[tuple(arguments)]

        with patch.object(collect, 'static_command', side_effect=run):
            text = collect.collect_help('hc', 'hc', root_help)
        self.assertEqual(set(requests), set(responses))
        self.assertTrue(all(arguments[-1] == '--help' for arguments in requests))
        self.assertIn('## hc server stop --help', text)

    def test_static_discovery_accepts_future_versions_without_runtime_calls(self):
        tui, core, app = snapshots()
        calls = []
        metadata = {
            ('herdr', ('api', 'schema', '--json')): json.dumps(tui),
            ('hc', ('schema',)): json.dumps(core),
            ('herdr-app', ('commands',)): json.dumps(app),
        }

        def run(binary, arguments):
            calls.append((binary, tuple(arguments)))
            if arguments == ['--version']:
                return binary + ' 99.99.99\n'
            if arguments == ['--help']:
                return 'Usage: ' + binary + ' [OPTIONS]\n'
            if arguments == ['--skill']:
                return '# Official static skill\n'
            return metadata[(binary, tuple(arguments))]

        with patch.object(collect.shutil, 'which', side_effect=lambda binary: binary), \
             patch.dict(collect.os.environ, {}, clear=True), \
             patch.object(collect, 'static_command', side_effect=run), \
             patch.object(collect, 'collect_help', return_value='## static help\n'):
            exports, versions = collect.collect()
        self.assertEqual(set(exports), set(collect.PUBLIC_SNAPSHOTS))
        self.assertEqual(versions['herdr'], 'herdr 99.99.99')
        self.assertEqual([arguments for _, arguments in calls[:3]], [('--help',)] * 3)
        self.assertTrue(all(arguments in {('--help',), ('--version',), ('--skill',),
                                         ('api', 'schema', '--json'), ('schema',), ('commands',)}
                            for _, arguments in calls))

    def test_diff_reports_added_changed_and_unchanged_snapshots(self):
        exports = {name: 'new\n' for name in collect.PUBLIC_SNAPSHOTS}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in collect.PUBLIC_SNAPSHOTS.values():
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / 'sources/herdr-api.schema.json').write_text('new\n', encoding='utf-8')
            (root / 'sources/core-api.schema.json').write_text('old\n', encoding='utf-8')
            differences = {item['path']: item for item in collect.snapshot_diff(exports, root)}
        self.assertNotIn('sources/herdr-api.schema.json', differences)
        self.assertEqual(differences['sources/core-api.schema.json']['status'], 'changed')
        self.assertEqual(differences['sources/app-commands.json']['status'], 'added')

    def test_default_collection_does_not_replace_public_snapshots(self):
        exports = {name: 'fresh\n' for name in collect.PUBLIC_SNAPSHOTS}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'sources/herdr-api.schema.json'
            target.parent.mkdir(parents=True)
            target.write_text('published\n', encoding='utf-8')
            with patch.object(collect, 'ROOT', root), \
                 patch.object(collect, 'collect', return_value=(exports, {})), \
                 patch.object(sys, 'argv', ['collect.py']), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(collect.main(), 0)
            self.assertEqual(target.read_text(encoding='utf-8'), 'published\n')
            self.assertEqual((root / 'sources/current/herdr-api.schema.json').read_text(encoding='utf-8'), 'fresh\n')

    def test_output_directory_cannot_bypass_publish_flag(self):
        with patch.object(sys, 'argv', ['collect.py', '--output-dir', str(ROOT / 'references')]), \
             patch.object(collect, 'collect') as discover, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(collect.main(), 1)
        discover.assert_not_called()


class CompletenessTests(unittest.TestCase):
    def test_package_includes_plugin_assets_and_only_public_source_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required = ['LICENSE', 'THIRD_PARTY_NOTICES.md', 'LICENSES/Apache-2.0.txt',
                        'SKILL.md', 'README.md', 'plugins/example/herdr-plugin.toml',
                        'plugins/example/main.py', 'plugins/example/icon.svg',
                        'plugins/example/settings.toml', 'tools/collect.py',
                        *[relative for relative in collect.PUBLIC_SNAPSHOTS.values() if relative.startswith('sources/')]]
            excluded = ['sources/current/private.json', 'sources/history/schema.json',
                        'development/evidence/private.md', 'dist/old.zip',
                        'plugins/example/__pycache__/main.pyc',
                        'plugins/example/.env', 'plugins/example/.env.local',
                        'plugins/example/actions.log']
            for relative in required + excluded:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic', encoding='utf-8')
            packaged = {path.relative_to(root).as_posix() for path in build.package_files(root)}
        self.assertTrue(set(required).issubset(packaged))
        self.assertFalse(set(excluded) & packaged)

    def test_api_index_drift_is_detected_for_all_products(self):
        tui, core, app = snapshots()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'sources').mkdir()
            (root / 'references').mkdir()
            for name, data in [('herdr-api.schema.json', tui), ('core-api.schema.json', core), ('app-commands.json', app)]:
                (root / 'sources' / name).write_text(json.dumps(data), encoding='utf-8')
            index = root / 'references/api-methods.md'
            text = collect.render_api_index(tui, core, app)
            index.write_text(text, encoding='utf-8')
            self.assertEqual(validate.validate_snapshots(root), {'tui': 1, 'core': 1, 'app': 1})
            for name in ('ping', 'hello', 'space.new'):
                index.write_text(text.replace('- `' + name + '`', '- `missing`'), encoding='utf-8')
                with self.subTest(name=name), self.assertRaises(ValueError):
                    validate.validate_snapshots(root)

    def test_plugin_missing_or_escaping_entrypoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'plugins/example'
            folder.mkdir(parents=True)
            manifest = folder / 'herdr-plugin.toml'
            text = 'id="example"\nname="Example"\nversion="1.0.0"\n[[startup]]\ncommand=["python","-B","main.py"]\n'
            manifest.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError):
                validate.validate_plugins(root)
            (folder / 'main.py').write_text('pass\n', encoding='utf-8')
            self.assertEqual(validate.validate_plugins(root), ['example'])
            (root / 'outside.py').write_text('pass\n', encoding='utf-8')
            manifest.write_text(text.replace('main.py', '../../outside.py'), encoding='utf-8')
            with self.assertRaises(ValueError):
                validate.validate_plugins(root)


if __name__ == '__main__':
    unittest.main()
