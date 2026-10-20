def test_total_pages_counts_partial_last_page(client):
    """#8: 25 tasks at size 10 reported 2 pages, hiding tasks 21-25 from the UI."""
    for i in range(25):
        client.post("/tasks", json={"title": f"Task {i + 1}"})

    body = client.get("/tasks", params={"page": 1, "size": 10}).json()

    assert body["total"] == 25
    assert body["total_pages"] == 3
