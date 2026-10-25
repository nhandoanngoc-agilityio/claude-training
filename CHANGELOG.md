# Changelog

## [Unreleased]

### Added
- Claude Code `PreToolUse` hook (`.claude/hooks/block_forbidden.py`) that blocks the CLAUDE.md "Never do" commands: `rm -rf`, `git push --force`, pushing or committing to `main`, and `git reset --hard`. Covered by `tests/test_hooks.py`.
- The hook also blocks `git push` / `git push origin [HEAD|@]` from `main`, `git push --all` / `--mirror`, and `git merge` / `cherry-pick` / `revert` / `rebase` on `main` (#3, #9).
- The hook asks for approval before adding a dependency (`uv add`, `uv pip install`, `pip install`) (#9).
- Versioned git hook `.githooks/pre-commit` rejects commits on `main` from any terminal. Enable it with `git config core.hooksPath .githooks` (#3).
- Team-wide Claude Code hooks: format-on-edit (`uvx ruff format`) and a desktop notification when Claude finishes (#7).

### Changed
- Ruff line length is 100, and the codebase was formatted once to match (#5).
- The Claude review workflow shows Claude's report in the run's Step Summary and declares the `gh` tools it uses (#8).

## [0.3.0] - 2026-10-22

### Added
- Search tasks with `GET /tasks?q=`. Matching is case-insensitive and looks at the title and description (#9).
- List overdue tasks with `GET /tasks/overdue`. Each task includes `days_late` (#10).

### Changed
- `DELETE /tasks/{id}` now returns 404 for a task that doesn't exist, instead of reporting success (#11).
- Titles that are only whitespace are now rejected with 422 (#12).

### Fixed
- `PATCH /tasks/{id}` changes only the fields you send; other fields are no longer cleared (#6).
- The `due_before` filter skips tasks that have no due date (#7).
- `total_pages` counts a partial last page, and is 0 when there are no tasks (#8).
- Search finds text written in different Unicode forms, e.g. "é" typed as one character or as "e" plus an accent (#13).

## [0.2.0]

- Version bump for the training release.
