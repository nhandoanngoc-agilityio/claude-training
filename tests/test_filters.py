def test_due_before_skips_undated_tasks(client):
    """#7: the due date filter returned 500 once any task had no due date."""
    client.post("/tasks", json={"title": "Plan sprint", "due_date": "2026-10-22"})
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks", params={"due_before": "2026-10-26"})

    assert response.status_code == 200
    assert [t["title"] for t in response.json()["items"]] == ["Plan sprint"]


def test_due_before_with_only_undated_tasks(client):
    client.post("/tasks", json={"title": "Read docs"})
    client.post("/tasks", json={"title": "Tidy desk"})

    response = client.get("/tasks", params={"due_before": "2026-10-26"})

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_due_before_is_exclusive(client):
    client.post("/tasks", json={"title": "On the day", "due_date": "2026-10-26"})

    response = client.get("/tasks", params={"due_before": "2026-10-26"})

    assert response.json()["items"] == []
