# Task Tracker

A small FastAPI service for creating and tracking tasks. It is the practice codebase for the Claude Code training: the issue board holds real bugs and feature requests against it.

Data is kept in memory, so it resets every time the server restarts.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for the interactive API docs.

## Run tests

```bash
uv run pytest
```

## API

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/version` | Running app version |
| `POST` | `/tasks` | Create a task (`title`, optional `description`, `due_date`, `status`) |
| `GET` | `/tasks` | List tasks. Query: `page`, `size`, `status`, `due_before` |
| `GET` | `/tasks/{id}` | Get one task |
| `PATCH` | `/tasks/{id}` | Update only the fields sent in the body |
| `DELETE` | `/tasks/{id}` | Delete a task |

`status` is one of `todo`, `in_progress`, `done`.

`due_before=YYYY-MM-DD` returns tasks due strictly before that date. Tasks without a due date are not included.

`GET /tasks` pages results: `size` defaults to 10 (max 100), and the response includes `total` and `total_pages`.

## Project layout

```text
app/
  main.py          FastAPI app and router wiring
  models.py        Pydantic request/response models
  store.py         In-memory task storage
  routers/tasks.py /tasks endpoints
tests/             pytest suite (uses FastAPI's TestClient)
```

## Claude Code hooks

`.claude/settings.json` registers a team-wide `PreToolUse` hook, `.claude/hooks/block_forbidden.py`. Before Claude runs a shell command, the hook blocks anything on the CLAUDE.md "Never do" list and tells Claude why:

- `rm` with recursive + force flags (`rm -rf`, `rm -r -f`, ...)
- `git push --force` / `-f` / `+refspec` (`--force-with-lease` is still allowed)
- pushing to `main` (including `git push` / `git push origin HEAD` while on `main`, and `--all` / `--mirror`), or committing while on `main`
- `git reset --hard`

It needs only `python3`. Run `/hooks` in Claude Code to see it, and `uv run pytest tests/test_hooks.py` to test it.

Known limits (not blocked):

- `git -C <dir> commit` and `cd <dir> && git commit` are judged on the branch of the directory Claude runs in, not `<dir>`.
- Other ways to delete or discard work, such as `find -delete` and `git clean -fdx`.
- Commands inside scripts the hook can't see into (`./script.sh`, `make`, `uv run ...`).

## Git hooks

`.githooks/pre-commit` rejects commits on `main` from any terminal, not just Claude's. Branch protection isn't available on this repo, so enable it once per clone:

```bash
git config core.hooksPath .githooks
```

It can be skipped with `git commit --no-verify`, and it doesn't run for merge commits (`git merge`, `git pull` without fast-forward). Test it with `uv run pytest tests/test_githooks.py`.

Optional personal hooks (format-on-edit with ruff, notify-on-finish) live in `.claude/settings.local.json`, which is git-ignored.
