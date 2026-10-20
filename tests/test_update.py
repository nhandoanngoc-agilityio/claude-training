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
