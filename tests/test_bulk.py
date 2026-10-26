def test_bulk_sets_status_on_every_task(client):
    for title in ["a", "b", "c"]:
        client.post("/tasks", json={"title": title})

    response = client.patch("/tasks/bulk", json={"ids": [1, 3], "status": "done"})

    assert response.status_code == 200
    assert response.json() == {"updated": 2}
    statuses = {t["id"]: t["status"] for t in client.get("/tasks").json()["items"]}
    assert statuses == {1: "done", 2: "todo", 3: "done"}


def test_bulk_unknown_id_is_404(client):
    client.post("/tasks", json={"title": "a"})

    response = client.patch("/tasks/bulk", json={"ids": [42], "status": "done"})

    assert response.status_code == 404


def test_bulk_needs_at_least_one_id(client):
    response = client.patch("/tasks/bulk", json={"ids": [], "status": "done"})

    assert response.status_code == 422


def test_bulk_needs_a_status(client):
    client.post("/tasks", json={"title": "a"})

    response = client.patch("/tasks/bulk", json={"ids": [1]})

    assert response.status_code == 422


def test_bulk_does_not_shadow_single_task_update(client):
    client.post("/tasks", json={"title": "a"})

    response = client.patch("/tasks/1", json={"status": "in_progress"})

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
