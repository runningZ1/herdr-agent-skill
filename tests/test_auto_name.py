"""Behavioral boundaries for the optional auto-name plugin."""
import importlib.util
from pathlib import Path
import unittest

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
        self.assertTrue(auto_name.eligible("12345", previous))

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


if __name__ == "__main__":
    unittest.main()
