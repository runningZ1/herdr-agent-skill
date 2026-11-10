"""Herdr TUI event hook: name default tabs, preserve human names."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata
from contextlib import contextmanager


def herdr(*args):
    result = subprocess.run(
        [os.environ.get("HERDR_BIN_PATH", "herdr"), *args],
        capture_output=True, encoding="utf-8", timeout=15,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    response = json.loads(result.stdout)
    if "error" in response:
        raise RuntimeError(str(response["error"]))
    return response["result"]


def compact(text):
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C"))
    return re.sub(r"\s+", " ", text).strip()[:36]


def native_title(pane):
    title = pane.get("terminal_title_stripped") or pane.get("terminal_title") or ""
    title = re.sub(r"^(?:管理员|Administrator):\s*", "", title, flags=re.I)
    if re.match(r"^[A-Za-z]:\\", title):
        return ""
    title = re.sub(r"^π\s*(?:>|[\u2800-\u28ff])?\s*", "", title)
    title = re.sub(r"^[^\w\u3400-\u9fff]+", "", title)
    title = re.sub(r"^[A-Z][A-Z0-9_-]{0,15}:\s*", "", title)
    title = compact(title)
    folder = re.split(r"[/\\]", pane.get("cwd", "").rstrip("/\\"))[-1]
    generic = {"claude code", "codex", "omp", "pi", "powershell", "windows powershell", "powershell.exe", "bash", "zsh", "cmd.exe"}
    if not title or title.casefold() in generic or title == folder or re.match(r"^[A-Za-z]:\\", title):
        return ""
    return title


def claude_topic(pane):
    """Read only the first bounded chunk of the exact active session, locally."""
    session = pane.get("agent_session") or {}
    session_id = session.get("value", "")
    if pane.get("agent") != "claude" or not re.fullmatch(r"[a-fA-F0-9-]{36}", session_id):
        return ""
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))) / "projects"
    for file in root.glob(f"*/{session_id}.jsonl"):
        with file.open(encoding="utf-8") as stream:
            chunk = stream.read(262144)
        for line in chunk.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "user" or row.get("isMeta"):
                continue
            content = row.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(item.get("text", "") for item in content if item.get("type") == "text")
            if not isinstance(content, str):
                continue
            content = re.sub(r"<[^>]+>.*?</[^>]+>", "", content, flags=re.S).strip()
            if content and not content.startswith(("/", "[Request interrupted", "This session is being continued")):
                return compact(content.splitlines()[0])
    return ""


def candidate(pane):
    topic = native_title(pane) or claude_topic(pane)
    if topic:
        return topic, 2
    folder = re.split(r"[/\\]", pane.get("cwd", "").rstrip("/\\"))[-1] or "新对话"
    agent = pane.get("agent") or "终端"
    return compact(f"{agent.upper() if agent != '终端' else agent} · {folder}"), 1


def eligible(label, previous):
    return not label or label.isdecimal() or label == previous.get("label")


@contextmanager
def state_lock(path):
    with path.open("a+b") as stream:
        stream.seek(0, 2)
        if not stream.tell():
            stream.write(b"0")
            stream.flush()
        deadline = time.monotonic() + 20
        while True:
            stream.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("auto-name state is busy")
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def sync():
    if os.environ.get("HERDR_ENV") != "1":
        raise RuntimeError("Run inside Herdr or through the installed plugin")
    directory = Path(os.environ["HERDR_PLUGIN_STATE_DIR"])
    directory.mkdir(parents=True, exist_ok=True)
    # Isolate named sessions even though the plugin registration is user-wide.
    import hashlib
    scope = hashlib.sha256(os.environ.get("HERDR_SOCKET_PATH", "default").encode()).hexdigest()[:16]
    file = directory / f"names-{scope}.json"
    with state_lock(directory / f"names-{scope}.lock"):
        state = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
        tabs = herdr("tab", "list")["tabs"]
        panes = herdr("pane", "list")["panes"]
        live = {tab["tab_id"] for tab in tabs}
        state = {key: value for key, value in state.items() if key in live}
        changed = []
        for tab in tabs:
            tab_id = tab["tab_id"]
            previous = state.get(tab_id, {})
            label = tab.get("label", "")
            if not eligible(label, previous):
                state.pop(tab_id, None)
                continue
            members = [p for p in panes if p.get("tab_id") == tab_id]
            if not members:
                continue
            # Prefer an agent over an auxiliary shell in split tabs; stable pane order.
            pane = next((p for p in members if p.get("agent")), members[0])
            name, quality = candidate(pane)
            if quality < previous.get("quality", 0) and label == previous.get("label"):
                continue
            if name != label:
                # Recheck immediately before mutation to respect a concurrent manual rename.
                current = herdr("tab", "get", tab_id)["tab"].get("label", "")
                if current != label:
                    continue
                herdr("tab", "rename", tab_id, name)
                actual = herdr("tab", "get", tab_id)["tab"]["label"]
                if actual != name:
                    raise RuntimeError(f"Rename not confirmed: {tab_id}")
                changed.append({"tab": tab_id, "name": name})
            state[tab_id] = {"label": name, "quality": quality}
        temporary = file.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(file)
        print(json.dumps({"renamed": changed}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sync()
