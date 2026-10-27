# Changelog

## [Unreleased]

### Added
- AI-native SDLC Stages 1–3: an `intent/` home for `intent.md` and `spec.md`, the `write-intent` and `intent-to-spec` skills, and a CLAUDE.md "Workflow" section that starts every issue in plan mode. `intent/_example-tasks-sort/` is a worked example from #16.
- Sort `GET /tasks` with `sort=created_at|due_date|title` and `order=asc|desc`. Undated tasks go last; unknown values return 422 (#16).
- Project-level `security-guidance` and `claude-security` Claude Code plugins, with project rules in `.claude/claude-security-guidance.md` (#20).
- Claude Code `PreToolUse` hook (`.claude/hooks/block_forbidden.py`) that blocks the CLAUDE.md "Never do" commands: `rm -rf`, `git push --force`, pushing or committing to `main`, and `git reset --hard`. Covered by `tests/test_hooks.py`.
- The hook also blocks `git push` / `git push origin [HEAD|@]` from `main`, `git push --all` / `--mirror`, and `git merge` / `cherry-pick` / `revert` / `rebase` on `main` (#3, #9).
- The hook asks for approval before adding a dependency (`uv add`, `uv pip install`, `pip install`) (#9).
- Versioned git hook `.githooks/pre-commit` rejects commits on `main` from any terminal. Enable it with `git config core.hooksPath .githooks` (#3).
- `review-checklist` skill for reviewing branches and PRs against the team's conventions, and a `CONTEXT.md` glossary (#26).
- Team-wide Claude Code hooks: format-on-edit (`uvx ruff format`) and a desktop notification when Claude finishes (#7).

### Changed
- `loop.md` covers GitHub instead of GitLab: watch-a-PR and babysit-CI loops, and a `/schedule` morning maintenance routine (#24).
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
