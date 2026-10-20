def test_patch_keeps_fields_not_in_request(client):
    """#6: marking a task as done must not wipe its description and due date."""
    task = client.post(
        "/tasks",
        json={"title": "Write report", "description": "Q3 numbers", "due_date": "2026-10-31"},
    ).json()

    client.patch(f"/tasks/{task['id']}", json={"status": "done"})

    body = client.get(f"/tasks/{task['id']}").json()
    assert body["status"] == "done"
    assert body["description"] == "Q3 numbers"
    assert body["due_date"] == "2026-10-31"


def test_patch_title_only_keeps_other_fields(client):
    task = client.post(
        "/tasks",
        json={"title": "Old", "description": "Q3 numbers", "due_date": "2026-10-31"},
    ).json()

    body = client.patch(f"/tasks/{task['id']}", json={"title": "New"}).json()

    assert body["title"] == "New"
    assert body["description"] == "Q3 numbers"
    assert body["due_date"] == "2026-10-31"


def test_patch_null_title_is_ignored(client):
    task = client.post("/tasks", json={"title": "Keep me"}).json()

    response = client.patch(f"/tasks/{task['id']}", json={"title": None})

    assert response.status_code == 200
    assert response.json()["title"] == "Keep me"
