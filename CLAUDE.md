# Task Tracker

FastAPI task API used for team training. Data is in memory and resets on restart.

## Commands

- Install: `uv sync`
- Run: `uv run uvicorn app.main:app --reload` (docs at http://127.0.0.1:8000/docs)
- Test: `uv run pytest`. One test: `uv run pytest tests/test_paging.py -k empty`

## Layout

- `app/models.py`: request/response models. Body validation lives here; query-param limits (`page`, `size`) are in the router.
- `app/store.py`: `TaskStore`, the only place that touches stored tasks. Writes take `self._lock`.
- `app/routers/tasks.py`: `/tasks` endpoints. Thin: validate, call the store, map `None` to 404. Declare static paths (`/tasks/overdue`) before `/{task_id}`.
- `tests/`: one file per area (`test_update.py`, `test_filters.py`, `test_paging.py`, ...). Use the `client` fixture; it clears the store per test.
- `intent/`: one folder per feature, holding `intent.md` (what and why) and `spec.md` (the agreed contract). See `intent/README.md`.
- `.claude/hooks/` (Claude Code hooks, wired in `.claude/settings.json`) and `.githooks/` (git hooks): tested in `tests/test_hooks.py`, `test_format_hook.py`, `test_githooks.py`. A hook block or approval prompt is team policy: change the approach (branch, PR, specific files) rather than reaching the same result another way.

## Workflow

New features follow intent → spec → issue → build. Small bug fixes can start from an issue.

1. **Plan**: capture the idea as `intent/<date>-<slug>/intent.md` (`write-intent` skill). The product owner reviews and merges it.
2. **Design**: write `spec.md` beside it (`intent-to-spec` skill). The product owner resolves its concerns and merges it; the spec's issues are then opened.
3. **Build**: start every issue in plan mode. Read the linked spec, propose the plan (files, tests, commits), and wait for approval before editing.
4. **Test and ship**: failing tests first, then code; PR with `Closes #<issue>`; `review-checklist` before opening; Claude review runs in CI.

## Conventions

- Bug fix = failing test commit first, then the fix, as small separate commits.
- Branch `fix/<issue>-<slug>` from `main`. PR description: what / why / how tested / screenshots (curl output), with `Closes #<issue>`.
- Invalid input gets a 422 from the models. Reject it; don't silently clean it up (e.g. titles are stored exactly as sent).
- `due_before` is strict and skips undated tasks. `total_pages` rounds up and is 0 for an empty list. Keep these unless a ticket says otherwise.
- Length limits (`title`, `q`) count code points; NFD text is not normalized before the check (#14).
- We work on GitHub for now. The remote `origin` is GitHub (`nhandoanngoc-agilityio/claude-training`). Push with `git push origin <branch>` and open PRs with `gh pr create --base main`.
- CI runs in GitHub Actions (`.github/workflows/ci.yml`). `.gitlab-ci.yml` is kept only for switching back to GitLab later; don't change it unless asked.

## Where deep reasoning pays

- Default to normal effort for routine edits: single-file fixes with a clear test, docs, small endpoints. On S6 (#25), `low`, `high` and `high` + `ultrathink` made the same correct fix, and `ultrathink` cost ~55% more and took ~2× as long.
- Use `high` or `ultrathink` when the bug isn't visible in one file or one test:
  - Concurrency in `TaskStore`: multi-step writes under `self._lock`, partial updates, read-then-write.
  - Security: user input reaching a shell, a file path, CSV/spreadsheet output, or workflow `permissions`.
  - Multi-file bugs, where the cause and the symptom are in different files (e.g. a `str` from `models.py` crashing the export in `tasks.py`).
  - Review triage: deciding whether a finding is real (e.g. #23 row 3, lock-free reads on GIL CPython).
- Those cases come from #23 (what reviewers missed), not from the #25 timing, which measured a single-file fix only.

## Never do

- Never commit or push directly to `main`; everything goes through a PR.
- Never remove the `title` null guard in `TaskStore.update`: `{"title": null}` must not wipe a title.
- Never merge with conflict markers left in, or with failing tests.
- Never use `git push --force`. Use `--force-with-lease` only right after `git pull --rebase`; a plain `git fetch` resets the lease and lets you overwrite a partner's commit.
- Never add a database or a new dependency without asking first.
