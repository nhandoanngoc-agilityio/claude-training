import csv
import io


def rows(response):
    return list(csv.reader(io.StringIO(response.text)))


def test_export_has_header_and_one_row_per_task(client):
    client.post("/tasks", json={"title": "Plan sprint", "due_date": "2026-11-02"})
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks/export.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "tasks.csv" in response.headers["content-disposition"]
    table = rows(response)
    assert table[0] == ["id", "title", "status", "due_date", "created_at"]
    assert [row[:4] for row in table[1:]] == [
        ["1", "Plan sprint", "todo", "2026-11-02"],
        ["2", "Read docs", "todo", ""],
    ]


def test_export_empty_store_has_only_header(client):
    response = client.get("/tasks/export.csv")

    assert rows(response) == [["id", "title", "status", "due_date", "created_at"]]


def test_export_filters_by_status(client):
    client.post("/tasks", json={"title": "open"})
    client.post("/tasks", json={"title": "finished", "status": "done"})

    response = client.get("/tasks/export.csv", params={"status": "done"})

    assert [row[1] for row in rows(response)[1:]] == ["finished"]


def test_export_title_with_comma_is_quoted(client):
    client.post("/tasks", json={"title": "Buy milk, eggs"})

    response = client.get("/tasks/export.csv")

    assert rows(response)[1][1] == "Buy milk, eggs"


def test_export_rejects_unknown_status(client):
    response = client.get("/tasks/export.csv", params={"status": "archived"})

    assert response.status_code == 422
