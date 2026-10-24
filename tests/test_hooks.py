"""Tests for the Claude Code PreToolUse hook in .claude/hooks/block_forbidden.py."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "block_forbidden.py"


def run_hook(command: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    if cwd:
        payload["cwd"] = cwd
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf build",
        "rm -fr build",
        "rm -r -f build",
        "rm --recursive --force build",
        "sudo rm -Rf /tmp/x",
        "cd app && rm -rf __pycache__",
        'bash -c "rm -rf build"',
        "git push --force origin fix/1-x",
        "git push -f origin fix/1-x",
        "git push origin +fix/1-x",
        "git push origin main",
        "git push origin HEAD:main",
        "git reset --hard HEAD~1",
        "git -C . reset --hard",
    ],
)
def test_blocks_forbidden_commands(command):
    result = run_hook(command)
    assert result.returncode == 2
    assert "Blocked by team policy" in result.stderr


@pytest.mark.parametrize(
    "command",
    [
        "uv run pytest",
        "rm build/old.log",
        "rm -r empty_dir",
        "git push origin fix/14-nfd-titles",
        "git push --force-with-lease origin fix/14-nfd-titles",
        "git reset --soft HEAD~1",
        "git status && git diff",
        "echo 'rm -rf is dangerous'",
        "grep -rf patterns.txt app",
    ],
)
def test_allows_safe_commands(command):
    result = run_hook(command)
    assert result.returncode == 0, result.stderr


def test_blocks_commit_on_main_but_not_on_branch(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    assert run_hook("git commit -m x", cwd=str(tmp_path)).returncode == 2

    git("checkout", "-b", "fix/1-x")
    assert run_hook("git commit -m x", cwd=str(tmp_path)).returncode == 0


def test_malformed_input_never_blocks():
    result = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
    assert result.returncode == 0
