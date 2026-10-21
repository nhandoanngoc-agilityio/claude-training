import pytest


def titles(response):
    return [t["title"] for t in response.json()["items"]]


def test_search_is_case_insensitive_substring(client):
    """#9: "rep" finds "Report"."""
    client.post("/tasks", json={"title": "Report"})
    client.post("/tasks", json={"title": "Plan sprint"})

    response = client.get("/tasks", params={"q": "rep"})

    assert response.status_code == 200
    assert titles(response) == ["Report"]


def test_search_matches_description(client):
    client.post("/tasks", json={"title": "Write up", "description": "Quarterly REPORT"})
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks", params={"q": "report"})

    assert titles(response) == ["Write up"]


def test_search_skips_tasks_without_description(client):
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks", params={"q": "report"})

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_search_matches_whole_phrase(client):
    client.post("/tasks", json={"title": "Send weekly report"})
    client.post("/tasks", json={"title": "Report weekly"})

    response = client.get("/tasks", params={"q": "weekly report"})

    assert titles(response) == ["Send weekly report"]


def test_search_keeps_id_order(client):
    client.post("/tasks", json={"title": "Report B"})
    client.post("/tasks", json={"title": "Other"})
    client.post("/tasks", json={"title": "Report A"})

    response = client.get("/tasks", params={"q": "report"})

    assert titles(response) == ["Report B", "Report A"]


def test_search_combines_with_filters(client):
    client.post("/tasks", json={"title": "Report", "status": "done", "due_date": "2026-10-22"})
    client.post("/tasks", json={"title": "Report", "status": "todo", "due_date": "2026-10-22"})
    client.post("/tasks", json={"title": "Report late", "status": "done", "due_date": "2026-11-30"})
    client.post("/tasks", json={"title": "Plan", "status": "done", "due_date": "2026-10-22"})

    response = client.get(
        "/tasks", params={"q": "report", "status": "done", "due_before": "2026-10-26"}
    )

    assert [t["id"] for t in response.json()["items"]] == [1]


def test_search_paging_counts_only_matches(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Report {i}"})
        client.post("/tasks", json={"title": f"Other {i}"})

    response = client.get("/tasks", params={"q": "report", "page": 3, "size": 2})

    body = response.json()
    assert body["total"] == 5
    assert body["total_pages"] == 3
    assert titles(response) == ["Report 4"]


@pytest.mark.parametrize("q", ["", "   ", "a" * 201])
def test_search_rejects_invalid_query(client, q):
    response = client.get("/tasks", params={"q": q})

    assert response.status_code == 422


def test_search_accepts_max_length_query(client):
    response = client.get("/tasks", params={"q": "a" * 200})

    assert response.status_code == 200
