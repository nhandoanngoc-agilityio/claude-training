def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_task(client):
    created = client.post("/tasks", json={"title": "Write report"})
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Write report"
    assert body["status"] == "todo"

    fetched = client.get(f"/tasks/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Write report"


def test_create_task_requires_title(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_get_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_list_first_page(client):
    for i in range(20):
        client.post("/tasks", json={"title": f"Task {i}"})

    body = client.get("/tasks", params={"page": 1, "size": 10}).json()
    assert len(body["items"]) == 10
    assert body["total"] == 20
    assert body["total_pages"] == 2


def test_filter_by_status(client):
    client.post("/tasks", json={"title": "A", "status": "done"})
    client.post("/tasks", json={"title": "B"})

    body = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in body["items"]] == ["A"]


def test_filter_due_before(client):
    client.post("/tasks", json={"title": "Early", "due_date": "2026-10-01"})
    client.post("/tasks", json={"title": "Late", "due_date": "2026-12-01"})

    body = client.get("/tasks", params={"due_before": "2026-11-01"}).json()
    assert [t["title"] for t in body["items"]] == ["Early"]


def test_update_title(client):
    task = client.post("/tasks", json={"title": "Old"}).json()
    updated = client.patch(f"/tasks/{task['id']}", json={"title": "New"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "New"


def test_delete_task(client):
    task = client.post("/tasks", json={"title": "Temp"}).json()
    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404
