from app.store import store


def test_clear_done_with_nothing_done(client):
    client.post("/tasks", json={"title": "still open"})
    assert store.clear_done() == 0
    assert client.get("/tasks").json()["total"] == 1
