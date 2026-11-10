"""Behavioral boundaries for the optional auto-name plugin."""
import io
import json
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "auto_name", Path(__file__).resolve().parents[1] / "plugins" / "auto-name" / "main.py"
)
auto_name = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_name)


class NamingTests(unittest.TestCase):
    def test_custom_names_are_preserved_after_automatic_naming(self):
        previous = {"label": "修复登录失败"}
        self.assertTrue(auto_name.eligible("修复登录失败", previous))
        self.assertFalse(auto_name.eligible("我自己的项目名称", previous))
        self.assertFalse(auto_name.eligible("magpie", {}))
        self.assertFalse(auto_name.eligible("12345", previous))
        self.assertTrue(auto_name.eligible("12345", {}))

    def test_spinner_changes_do_not_change_conversation_name(self):
        pane = {"agent": "omp", "cwd": r"C:\work\project"}
        titles = ["π > 🏷️ NAME: 为 Agent 对话窗口自动命名", "π ⠧ 🏷️ NAME: 为 Agent 对话窗口自动命名"]
        for title in titles:
            with self.subTest(title=title):
                pane["terminal_title_stripped"] = title
                self.assertEqual(auto_name.candidate(pane), ("为 Agent 对话窗口自动命名", 2))

    def test_generic_agent_title_uses_project_until_topic_arrives(self):
        pane = {"agent": "claude", "cwd": r"D:\Projects\Qsenso", "terminal_title_stripped": "Claude Code"}
        self.assertEqual(auto_name.candidate(pane), ("CLAUDE · Qsenso", 1))
        pane["terminal_title_stripped"] = "梳理服装设计需求"
        self.assertEqual(auto_name.candidate(pane), ("梳理服装设计需求", 2))

    def test_elevated_windows_shell_title_is_not_a_conversation(self):
        pane = {
            "cwd": r"C:\work\herdr",
            "terminal_title_stripped": r"管理员: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        }
        self.assertEqual(auto_name.candidate(pane), ("终端 · herdr", 1))


    def test_null_cwd_uses_safe_fallback(self):
        self.assertEqual(auto_name.candidate({"cwd": None}), ("终端 · 新对话", 1))
        self.assertEqual(
            auto_name.candidate({"cwd": None, "terminal_title": "Investigate crash"}),
            ("Investigate crash", 2),
        )

    def test_common_secrets_are_removed_before_title_truncation(self):
        secrets = [
            "api_key=" + "a" * 24, '"password": "secret with spaces"',
            "OPENAI_API_KEY=" + "a" * 24, "AWS_SECRET_ACCESS_KEY=" + "a" * 24,
            "Authorization: Bearer private-token", "Bearer private-token",
            "sk-" + "a" * 24, "ghp_" + "a" * 24,
            "AKIA" + "A" * 16, "xoxb-" + "a" * 16,
            "eyJabc.eyJdef.signature", "https://alice:" + "p" * 8 + "@example.com/path",
        ]
        for secret in secrets:
            with self.subTest(secret=secret):
                name, quality = auto_name.candidate({"terminal_title": f"Fix {secret}"})
                self.assertEqual(quality, 2)
                self.assertIn("[redacted]", name)
                self.assertNotIn("super-secret", name)
                self.assertNotIn("private", name)
                self.assertNotIn("secret with spaces", name)

    def test_claude_first_line_is_redacted_using_only_a_synthetic_session(self):
        with tempfile.TemporaryDirectory() as directory:
            session_id = "00000000-0000-0000-0000-000000000000"
            project = Path(directory) / "projects" / "synthetic"
            project.mkdir(parents=True)
            (project / f"{session_id}.jsonl").write_text(json.dumps({
                "type": "user", "message": {"content": "Fix token=private-token\nMore detail"},
            }), encoding="utf-8")
            with patch.dict(auto_name.os.environ, {"CLAUDE_CONFIG_DIR": directory}):
                self.assertEqual(auto_name.claude_topic({
                    "agent": "claude", "agent_session": {"value": session_id},
                }), "Fix [redacted]")

    def test_request_uses_remaining_deadline_and_does_not_expose_timeout_arguments(self):
        failure = subprocess.TimeoutExpired(["herdr", "rename", "secret-title"], 2)
        with patch.object(auto_name.time, "monotonic", return_value=10), patch.object(
            auto_name.subprocess, "run", side_effect=failure,
        ) as run:
            with self.assertRaises(TimeoutError) as raised:
                auto_name.herdr("tab", "rename", "A", "secret-title", deadline=12)
            self.assertEqual(run.call_args.kwargs["timeout"], 2)
            self.assertNotIn("secret-title", str(raised.exception))


class SyncTests(unittest.TestCase):
    """All requests and labels below are synthetic; no Herdr process is called."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        environment = patch.dict(auto_name.os.environ, {
            "HERDR_ENV": "1", "HERDR_PLUGIN_STATE_DIR": directory.name,
            "HERDR_SOCKET_PATH": "synthetic-test-socket",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.file = self.directory / f"names-{auto_name.label_hash('synthetic-test-socket')[:16]}.json"
        self.labels = {"A": "1"}
        self.titles = {"A": "First topic"}
        self.rename_errors = {}
        self.get_failures = set()
        self.get_overrides = {}
        self.get_calls = {}
        self.renames = []
        self.output = io.StringIO()
        stdout = patch.object(auto_name.sys, "stdout", self.output)
        stdout.start()
        self.addCleanup(stdout.stop)
        requests = patch.object(auto_name, "herdr", side_effect=self.request)
        requests.start()
        self.addCleanup(requests.stop)

    def state(self):
        return json.loads(self.file.read_text(encoding="utf-8"))

    def request(self, *args, deadline=None):
        self.assertIsNotNone(deadline)
        if args == ("tab", "list"):
            return {"tabs": [{"tab_id": tab, "label": label} for tab, label in self.labels.items()]}
        if args == ("pane", "list"):
            return {"panes": [
                {"tab_id": tab, "cwd": None, "terminal_title": self.titles[tab]}
                for tab in self.labels
            ]}
        action, tab = args[1:3]
        if action == "get":
            count = self.get_calls[tab] = self.get_calls.get(tab, 0) + 1
            if (tab, count) in self.get_failures:
                raise TimeoutError("synthetic get timeout")
            if (tab, count) in self.get_overrides:
                self.labels[tab] = self.get_overrides[(tab, count)]
            return {"tab": {"label": self.labels[tab]}}
        if action == "rename":
            name = args[3]
            # The durable pending record must exist before the mutation is invoked.
            pending = self.state()[tab]["pending"]
            self.assertEqual(pending["old_hash"], auto_name.label_hash(self.labels[tab]))
            self.assertEqual(pending["new_hash"], auto_name.label_hash(name))
            self.renames.append((tab, name))
            error = self.rename_errors.get(tab)
            if error and error[0] == "before":
                raise error[1]
            self.labels[tab] = name
            if error:
                raise error[1]
            return {}
        self.fail(f"Unexpected synthetic request action: {action}")

    def test_null_cwd_works_through_sync(self):
        self.titles["A"] = ""
        auto_name.sync()
        self.assertEqual(self.labels["A"], "终端 · 新对话")

    def test_a_success_is_durable_when_b_fails_and_b_is_not_blindly_retried(self):
        self.labels["B"] = "2"
        self.titles["B"] = "Second topic"
        self.rename_errors["B"] = ("before", TimeoutError("synthetic rename timeout"))
        with self.assertRaises(TimeoutError):
            auto_name.sync()
        state = self.state()
        self.assertEqual(state["A"]["label_hash"], auto_name.label_hash("First topic"))
        self.assertIn("pending", state["B"])
        self.rename_errors.clear()
        self.titles["A"] = "Improved first topic"
        auto_name.sync()
        self.assertEqual(self.labels["A"], "Improved first topic")
        self.assertEqual([tab for tab, _ in self.renames].count("B"), 1)
        self.assertIn("pending", self.state()["B"])
        # A delayed server commit can still be recognized after observing the old label.
        self.labels["B"] = "Second topic"
        auto_name.sync()
        self.assertNotIn("pending", self.state()["B"])
        self.assertEqual([tab for tab, _ in self.renames].count("B"), 1)

    def test_total_deadline_stops_before_any_mutation(self):
        with patch.object(auto_name.time, "monotonic", side_effect=[0, 0, 46]):
            with self.assertRaises(TimeoutError):
                auto_name.sync()
        self.assertEqual(self.renames, [])

    def test_manual_rename_before_confirmation_is_persisted(self):
        self.get_overrides[("A", 2)] = "Human choice"
        with self.assertRaises(RuntimeError):
            auto_name.sync()
        self.assertEqual(self.state()["A"], {"manual": True})
        auto_name.sync()
        self.assertEqual(self.labels["A"], "Human choice")
        self.assertEqual(len(self.renames), 1)

    def test_successful_rename_followed_by_get_timeout_is_reconciled(self):
        self.get_failures.add(("A", 2))
        with self.assertRaises(TimeoutError):
            auto_name.sync()
        self.assertEqual(self.labels["A"], "First topic")
        self.assertIn("pending", self.state()["A"])
        self.get_failures.add(("A", 3))
        with self.assertRaises(TimeoutError):
            auto_name.sync()
        self.assertIn("pending", self.state()["A"])
        self.assertEqual(len(self.renames), 1)
        auto_name.sync()
        self.assertNotIn("pending", self.state()["A"])
        self.assertEqual(len(self.renames), 1)
        self.titles["A"] = "Follow-up topic"
        auto_name.sync()
        self.assertEqual(self.labels["A"], "Follow-up topic")

    def test_timed_out_rename_that_committed_is_not_repeated(self):
        self.rename_errors["A"] = ("after", TimeoutError("synthetic rename timeout"))
        with self.assertRaises(TimeoutError):
            auto_name.sync()
        self.rename_errors.clear()
        auto_name.sync()
        self.assertEqual(len(self.renames), 1)
        self.assertNotIn("pending", self.state()["A"])

    def test_manual_rename_after_confirmation_is_preserved_even_if_numeric(self):
        auto_name.sync()
        self.labels["A"] = "12345"
        self.titles["A"] = "Another topic"
        auto_name.sync()
        auto_name.sync()
        self.assertEqual(self.labels["A"], "12345")
        self.assertEqual(len(self.renames), 1)
        self.assertEqual(self.state()["A"], {"manual": True})

    def test_manual_rename_while_pending_is_preserved(self):
        self.get_failures.add(("A", 2))
        with self.assertRaises(TimeoutError):
            auto_name.sync()
        self.labels["A"] = "My own name"
        auto_name.sync()
        self.assertEqual(self.labels["A"], "My own name")
        self.assertEqual(self.state()["A"], {"manual": True})
        self.assertEqual(len(self.renames), 1)

    def test_manual_rename_between_list_and_mutation_is_preserved(self):
        self.get_overrides[("A", 1)] = "My own name"
        auto_name.sync()
        self.assertEqual(self.labels["A"], "My own name")
        self.assertEqual(self.renames, [])
        self.assertEqual(self.state()["A"], {"manual": True})

    def test_pending_persistence_failure_prevents_mutation(self):
        save_state = auto_name.save_state

        def fail_pending(file, state):
            if any("pending" in previous for previous in state.values()):
                raise OSError("synthetic storage failure")
            save_state(file, state)

        with patch.object(auto_name, "save_state", side_effect=fail_pending):
            with self.assertRaises(OSError):
                auto_name.sync()
        self.assertEqual(self.renames, [])
        self.assertEqual(self.labels["A"], "1")

    def test_state_and_output_do_not_contain_titles_or_secrets(self):
        self.titles["A"] = "Fix api_key=super-secret-value"
        auto_name.sync()
        self.assertEqual(self.labels["A"], "Fix [redacted]")
        for text in (self.file.read_text(encoding="utf-8"), self.output.getvalue()):
            self.assertNotIn("Fix", text)
            self.assertNotIn("super-secret", text)

    def test_legacy_plaintext_ownership_is_migrated(self):
        self.labels["A"] = "Legacy topic"
        self.file.write_text(json.dumps({"A": {"label": "Legacy topic", "quality": 2}}), encoding="utf-8")
        auto_name.sync()
        self.assertEqual(self.labels["A"], "First topic")
        self.assertNotIn("Legacy topic", self.file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
