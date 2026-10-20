def test_total_pages_counts_partial_last_page(client):
    """#8: 25 tasks at size 10 reported 2 pages, hiding tasks 21-25 from the UI."""
    for i in range(25):
        client.post("/tasks", json={"title": f"Task {i + 1}"})

    body = client.get("/tasks", params={"page": 1, "size": 10}).json()

    assert body["total"] == 25
    assert body["total_pages"] == 3


def test_total_pages_is_zero_for_empty_list(client):
    body = client.get("/tasks").json()

    assert body["total"] == 0
    assert body["total_pages"] == 0


def test_page_past_the_end_is_empty(client):
    client.post("/tasks", json={"title": "Only task"})

    response = client.get("/tasks", params={"page": 5})

    assert response.status_code == 200
    assert response.json()["items"] == []
