"""Tests for the versioned git hooks in .githooks/ (enabled with `git config core.hooksPath .githooks`)."""

import subprocess
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent / ".githooks"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "git",
            "-c",
            f"core.hooksPath={HOOKS_DIR}",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.com",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def test_pre_commit_rejects_commit_on_main(tmp_path):
    git(tmp_path, "init", "-b", "main")
    result = git(tmp_path, "commit", "--allow-empty", "-m", "x")
    assert result.returncode != 0
    assert "main" in result.stderr
    assert (
        git(tmp_path, "rev-parse", "--verify", "-q", "HEAD").returncode != 0
    )  # nothing was committed


def test_pre_commit_allows_commit_on_branch(tmp_path):
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "checkout", "-b", "fix/1-x")
    result = git(tmp_path, "commit", "--allow-empty", "-m", "x")
    assert result.returncode == 0, result.stderr
