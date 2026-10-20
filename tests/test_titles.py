def test_create_rejects_whitespace_only_title(client):
    """#12: a title of only spaces was accepted and showed as a blank row."""
    assert client.post("/tasks", json={"title": "   "}).status_code == 422


def test_patch_rejects_whitespace_only_title(client):
    task = client.post("/tasks", json={"title": "Real title"}).json()

    response = client.patch(f"/tasks/{task['id']}", json={"title": "  "})

    assert response.status_code == 422
    assert client.get(f"/tasks/{task['id']}").json()["title"] == "Real title"


def test_title_is_stored_exactly_as_sent(client):
    response = client.post("/tasks", json={"title": " padded "})

    assert response.status_code == 201
    assert response.json()["title"] == " padded "
