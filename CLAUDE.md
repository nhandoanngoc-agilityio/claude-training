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

## Conventions

- Bug fix = failing test commit first, then the fix, as small separate commits.
- Branch `fix/<issue>-<slug>` from `main`. MR description: what / why / how tested / screenshots (curl output), with `Closes #<issue>`.
- Invalid input gets a 422 from the models. Reject it; don't silently clean it up (e.g. titles are stored exactly as sent).
- `due_before` is strict and skips undated tasks. `total_pages` rounds up and is 0 for an empty list. Keep these unless a ticket says otherwise.
- Length limits (`title`, `q`) count code points; NFD text is not normalized before the check (#14).
- The remote `origin` is GitLab. A `github` remote also exists and local `main` tracks it, so always name `origin` when pushing: `git push origin <branch>`.

## Never do

- Never commit or push directly to `main`; everything goes through an MR.
- Never remove the `title` null guard in `TaskStore.update`: `{"title": null}` must not wipe a title.
- Never merge with conflict markers left in, or with failing tests.
- Never use `git push --force`. Use `--force-with-lease` only right after `git pull --rebase`; a plain `git fetch` resets the lease and lets you overwrite a partner's commit.
- Never add a database or a new dependency without asking first.
