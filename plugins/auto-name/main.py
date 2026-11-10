"""Herdr TUI event hook: name default tabs, preserve human names."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata
from contextlib import contextmanager


def remaining(deadline):
    if deadline is None:
        return 15
    seconds = deadline - time.monotonic()
    if seconds <= 0:
        raise TimeoutError("auto-name sync deadline exceeded")
    return seconds


def herdr(*args, deadline=None):
    try:
        result = subprocess.run(
            [os.environ.get("HERDR_BIN_PATH", "herdr"), *args],
            capture_output=True, encoding="utf-8", timeout=min(15, remaining(deadline)),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        # TimeoutExpired includes command arguments, which can contain a title.
        raise TimeoutError("Herdr request timed out") from None
    if result.returncode:
        raise RuntimeError("Herdr request failed")
    try:
        response = json.loads(result.stdout)
    except ValueError:
        raise RuntimeError("Herdr returned invalid JSON") from None
    if "error" in response:
        raise RuntimeError("Herdr reported a request error")
    return response["result"]


def redact(text):
    """Best-effort common credential removal before truncating a display name."""
    text = re.sub(
        r"(?i)\b(?:[A-Za-z0-9]+[_-])*(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
        r"client[_-]?secret|authorization)\b[\"']?\s*[:=]\s*"
        r"(?:\"[^\"]*\"|'[^']*'|(?:Bearer\s+|Basic\s+)?[^\s,;]+)",
        "[redacted]", text,
    )
    text = re.sub(r"(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", "[redacted]", text)
    text = re.sub(
        r"\b(?:sk-(?:ant-)?[A-Za-z0-9_-]{16,}|(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{16,}|"
        r"(?:AKIA|ASIA)[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|"
        r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b",
        "[redacted]", text,
    )
    return re.sub(r"(?i)(https?://)[^/\s:@]+:[^/\s@]+@", r"\1[redacted]@", text)


def compact(text):
    text = "".join(c for c in text if c.isspace() or not unicodedata.category(c).startswith("C"))
    text = re.sub(r"\s+", " ", text)
    return redact(text).strip()[:36]


def native_title(pane):
    title = redact(pane.get("terminal_title_stripped") or pane.get("terminal_title") or "")
    title = re.sub(r"^(?:管理员|Administrator):\s*", "", title, flags=re.I)
    if re.match(r"^[A-Za-z]:\\", title):
        return ""
    title = re.sub(r"^π\s*(?:>|[\u2800-\u28ff])?\s*", "", title)
    title = re.sub(r"^[^\w\u3400-\u9fff]+", "", title)
    title = re.sub(r"^[A-Z][A-Z0-9_-]{0,15}:\s*", "", title)
    title = compact(title)
    folder = re.split(r"[/\\]", (pane.get("cwd") or "").rstrip("/\\"))[-1]
    generic = {"claude code", "codex", "omp", "pi", "powershell", "windows powershell", "powershell.exe", "bash", "zsh", "cmd.exe"}
    if not title or title.casefold() in generic or title == folder or re.match(r"^[A-Za-z]:\\", title):
        return ""
    return title


def claude_topic(pane, deadline=None):
    """Read only the first bounded chunk of the exact active session, locally."""
    session = pane.get("agent_session") or {}
    session_id = session.get("value", "")
    if pane.get("agent") != "claude" or not re.fullmatch(r"[a-fA-F0-9-]{36}", session_id):
        return ""
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))) / "projects"
    for file in root.glob(f"*/{session_id}.jsonl"):
        remaining(deadline)
        with file.open(encoding="utf-8") as stream:
            chunk = stream.read(262144)
        for line in chunk.splitlines():
            remaining(deadline)
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


def candidate(pane, deadline=None):
    topic = native_title(pane) or claude_topic(pane, deadline=deadline)
    if topic:
        return topic, 2
    folder = re.split(r"[/\\]", (pane.get("cwd") or "").rstrip("/\\"))[-1] or "新对话"
    agent = pane.get("agent") or "终端"
    return compact(f"{agent.upper() if agent != '终端' else agent} · {folder}"), 1


def label_hash(label):
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def eligible(label, previous):
    if previous.get("manual"):
        return False
    if "label_hash" in previous:
        return label_hash(label) == previous["label_hash"]
    if "label" in previous:  # Read version 1 ownership until the next state save.
        return label == previous["label"]
    return not label or label.isdecimal()


@contextmanager
def state_lock(path, deadline=None):
    with path.open("a+b") as stream:
        stream.seek(0, 2)
        if not stream.tell():
            stream.write(b"0")
            stream.flush()
        deadline = min(time.monotonic() + 20, deadline or float("inf"))
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
                time.sleep(min(0.05, remaining(deadline)))
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def save_state(file, state):
    """Commit the whole ownership journal before any external mutation."""
    temporary = file.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(state, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(file)


def sync():
    if os.environ.get("HERDR_ENV") != "1":
        raise RuntimeError("Run inside Herdr or through the installed plugin")
    deadline = time.monotonic() + 45
    directory = Path(os.environ["HERDR_PLUGIN_STATE_DIR"])
    directory.mkdir(parents=True, exist_ok=True)
    # Isolate named sessions even though the plugin registration is user-wide.
    scope = hashlib.sha256(os.environ.get("HERDR_SOCKET_PATH", "default").encode()).hexdigest()[:16]
    file = directory / f"names-{scope}.json"
    with state_lock(directory / f"names-{scope}.lock", deadline=deadline):
        state = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
        # Migrate old state without retaining plaintext conversation names.
        for previous in state.values():
            if "label" in previous:
                previous["label_hash"] = label_hash(previous.pop("label"))
        save_state(file, state)
        tabs = herdr("tab", "list", deadline=deadline)["tabs"]
        panes = herdr("pane", "list", deadline=deadline)["panes"]
        live = {tab["tab_id"] for tab in tabs}
        state = {key: value for key, value in state.items() if key in live}
        save_state(file, state)
        changed = []
        for tab in tabs:
            remaining(deadline)
            tab_id = tab["tab_id"]
            previous = state.get(tab_id, {})
            label = tab.get("label") or ""
            if "pending" in previous:
                pending = previous["pending"]
                label = herdr("tab", "get", tab_id, deadline=deadline)["tab"].get("label") or ""
                actual_hash = label_hash(label)
                if actual_hash == pending["new_hash"]:
                    previous = {"label_hash": actual_hash, "quality": pending["quality"]}
                    state[tab_id] = previous
                    save_state(file, state)
                elif actual_hash == pending["old_hash"]:
                    # A timed-out request may still commit later. Never retry it blindly.
                    continue
                else:
                    state[tab_id] = {"manual": True}
                    save_state(file, state)
                    continue
            if not eligible(label, previous):
                if not previous.get("manual"):
                    state[tab_id] = {"manual": True}
                    save_state(file, state)
                continue
            members = [p for p in panes if p.get("tab_id") == tab_id]
            if not members:
                continue
            # Prefer an agent over an auxiliary shell in split tabs; stable pane order.
            pane = next((p for p in members if p.get("agent")), members[0])
            name, quality = candidate(pane, deadline=deadline)
            if quality < previous.get("quality", 0):
                continue
            if name != label:
                # Recheck immediately before mutation to respect a concurrent manual rename.
                current = herdr("tab", "get", tab_id, deadline=deadline)["tab"].get("label") or ""
                if current != label:
                    state[tab_id] = {"manual": True}
                    save_state(file, state)
                    continue
                remaining(deadline)
                pending = {"old_hash": label_hash(label), "new_hash": label_hash(name), "quality": quality}
                state[tab_id] = {"pending": pending}
                save_state(file, state)
                herdr("tab", "rename", tab_id, name, deadline=deadline)
                actual = herdr("tab", "get", tab_id, deadline=deadline)["tab"].get("label") or ""
                if actual != name:
                    if label_hash(actual) != pending["old_hash"]:
                        state[tab_id] = {"manual": True}
                        save_state(file, state)
                    raise RuntimeError("Rename not confirmed")
                changed.append(tab_id)
            state[tab_id] = {"label_hash": label_hash(name), "quality": quality}
            # A later tab's failure must not lose confirmed ownership of this one.
            save_state(file, state)
        print(json.dumps({"renamed": changed}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        sync()
    except Exception as error:
        # Never print request arguments, server output, or conversation text.
        print(f"auto-name sync failed ({type(error).__name__})", file=sys.stderr)
        sys.exit(1)
