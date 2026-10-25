"""Tests for the Claude Code PostToolUse hook in .claude/hooks/format_on_edit.py."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "format_on_edit.py"


def run_hook(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True)


@pytest.mark.skipif(not shutil.which("uvx"), reason="hook needs uvx")
def test_formats_edited_python_file(tmp_path):
    path = tmp_path / "x.py"
    path.write_text("y=[1,2 ,3]\n")
    assert run_hook(json.dumps({"tool_input": {"file_path": str(path)}})).returncode == 0
    assert path.read_text() == "y = [1, 2, 3]\n"


def test_leaves_other_files_alone(tmp_path):
    path = tmp_path / "notes.md"
    path.write_text("y=[1,2 ,3]\n")
    assert run_hook(json.dumps({"tool_input": {"file_path": str(path)}})).returncode == 0
    assert path.read_text() == "y=[1,2 ,3]\n"


def test_malformed_input_never_blocks():
    assert run_hook("not json").returncode == 0
