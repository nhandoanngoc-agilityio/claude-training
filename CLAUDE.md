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
- `.claude/hooks/` (Claude Code hooks, wired in `.claude/settings.json`) and `.githooks/` (git hooks): tested in `tests/test_hooks.py`, `test_format_hook.py`, `test_githooks.py`. A hook block or approval prompt is team policy: change the approach (branch, PR, specific files) rather than reaching the same result another way.

## Conventions

- Bug fix = failing test commit first, then the fix, as small separate commits.
- Branch `fix/<issue>-<slug>` from `main`. PR description: what / why / how tested / screenshots (curl output), with `Closes #<issue>`.
- Invalid input gets a 422 from the models. Reject it; don't silently clean it up (e.g. titles are stored exactly as sent).
- `due_before` is strict and skips undated tasks. `total_pages` rounds up and is 0 for an empty list. Keep these unless a ticket says otherwise.
- Length limits (`title`, `q`) count code points; NFD text is not normalized before the check (#14).
- We work on GitHub for now. The remote `origin` is GitHub (`nhandoanngoc-agilityio/claude-training`). Push with `git push origin <branch>` and open PRs with `gh pr create --base main`.
- CI runs in GitHub Actions (`.github/workflows/ci.yml`). `.gitlab-ci.yml` is kept only for switching back to GitLab later; don't change it unless asked.

## Never do

- Never commit or push directly to `main`; everything goes through a PR.
- Never remove the `title` null guard in `TaskStore.update`: `{"title": null}` must not wipe a title.
- Never merge with conflict markers left in, or with failing tests.
- Never use `git push --force`. Use `--force-with-lease` only right after `git pull --rebase`; a plain `git fetch` resets the lease and lets you overwrite a partner's commit.
- Never add a database or a new dependency without asking first.
