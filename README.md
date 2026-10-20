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
