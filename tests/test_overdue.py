from datetime import date

import pytest

from app.routers import tasks as tasks_router

TODAY = date(2026, 10, 21)


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    monkeypatch.setattr(tasks_router, "utc_today", lambda: TODAY)


def test_overdue_empty_list(client):
    response = client.get("/tasks/overdue")

    assert response.status_code == 200
    assert response.json() == []


def test_task_due_today_is_not_overdue(client):
    client.post("/tasks", json={"title": "Due today", "due_date": "2026-10-21"})
    client.post("/tasks", json={"title": "Due tomorrow", "due_date": "2026-10-22"})

    response = client.get("/tasks/overdue")

    assert response.json() == []


def test_overdue_skips_undated_and_done_tasks(client):
    client.post("/tasks", json={"title": "No date"})
    client.post("/tasks", json={"title": "Done late", "due_date": "2026-10-01", "status": "done"})
    client.post("/tasks", json={"title": "Todo late", "due_date": "2026-10-20"})
    client.post(
        "/tasks", json={"title": "Started late", "due_date": "2026-10-20", "status": "in_progress"}
    )

    response = client.get("/tasks/overdue")

    assert response.status_code == 200
    assert [t["title"] for t in response.json()] == ["Todo late", "Started late"]


def test_overdue_includes_days_late(client):
    client.post("/tasks", json={"title": "Yesterday", "due_date": "2026-10-20"})

    item = client.get("/tasks/overdue").json()[0]

    assert item["days_late"] == 1
    assert item["due_date"] == "2026-10-20"


def test_overdue_sorted_most_late_first_then_by_id(client):
    client.post("/tasks", json={"title": "A", "due_date": "2026-10-19"})
    client.post("/tasks", json={"title": "B", "due_date": "2026-10-01"})
    client.post("/tasks", json={"title": "C", "due_date": "2026-10-19"})

    response = client.get("/tasks/overdue")

    assert [(t["title"], t["days_late"]) for t in response.json()] == [
        ("B", 20),
        ("A", 2),
        ("C", 2),
    ]
