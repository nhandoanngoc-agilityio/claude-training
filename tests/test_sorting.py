from datetime import datetime, timezone


def titles(response):
    return [t["title"] for t in response.json()["items"]]


def make(client, *tasks):
    for task in tasks:
        client.post("/tasks", json=task)


def test_no_sort_keeps_id_order(client):
    make(client, {"title": "b"}, {"title": "a"}, {"title": "c"})

    assert titles(client.get("/tasks")) == ["b", "a", "c"]


def test_order_without_sort_is_ignored(client):
    make(client, {"title": "b"}, {"title": "a"})

    response = client.get("/tasks", params={"order": "desc"})

    assert response.status_code == 200
    assert titles(response) == ["b", "a"]


def test_sort_by_created_at(client):
    make(client, {"title": "first"}, {"title": "second"}, {"title": "third"})

    asc = client.get("/tasks", params={"sort": "created_at"})
    desc = client.get("/tasks", params={"sort": "created_at", "order": "desc"})

    assert titles(asc) == ["first", "second", "third"]
    assert titles(desc) == ["third", "second", "first"]


def test_sort_by_title_is_case_insensitive(client):
    make(client, {"title": "banana"}, {"title": "Apple"}, {"title": "cherry"})

    asc = client.get("/tasks", params={"sort": "title"})
    desc = client.get("/tasks", params={"sort": "title", "order": "desc"})

    assert titles(asc) == ["Apple", "banana", "cherry"]
    assert titles(desc) == ["cherry", "banana", "Apple"]


def test_title_ties_break_by_id_ascending_in_both_orders(client):
    make(client, {"title": "Same"}, {"title": "same"}, {"title": "Other"})

    asc = client.get("/tasks", params={"sort": "title"}).json()["items"]
    desc = client.get("/tasks", params={"sort": "title", "order": "desc"}).json()["items"]

    assert [t["id"] for t in asc] == [3, 1, 2]
    assert [t["id"] for t in desc] == [1, 2, 3]


def test_sort_by_due_date(client):
    make(
        client,
        {"title": "late", "due_date": "2026-12-01"},
        {"title": "early", "due_date": "2026-10-01"},
        {"title": "middle", "due_date": "2026-11-01"},
    )

    asc = client.get("/tasks", params={"sort": "due_date"})
    desc = client.get("/tasks", params={"sort": "due_date", "order": "desc"})

    assert titles(asc) == ["early", "middle", "late"]
    assert titles(desc) == ["late", "middle", "early"]


def test_undated_tasks_go_last_in_both_orders(client):
    make(
        client,
        {"title": "undated 1"},
        {"title": "early", "due_date": "2026-10-01"},
        {"title": "undated 2"},
        {"title": "late", "due_date": "2026-12-01"},
    )

    asc = client.get("/tasks", params={"sort": "due_date"})
    desc = client.get("/tasks", params={"sort": "due_date", "order": "desc"})

    assert titles(asc) == ["early", "late", "undated 1", "undated 2"]
    assert titles(desc) == ["late", "early", "undated 1", "undated 2"]


def test_due_date_ties_break_by_id(client):
    make(
        client,
        {"title": "b", "due_date": "2026-10-01"},
        {"title": "a", "due_date": "2026-10-01"},
    )

    desc = client.get("/tasks", params={"sort": "due_date", "order": "desc"})

    assert titles(desc) == ["b", "a"]


def test_sort_applies_after_filters_and_before_paging(client):
    make(
        client,
        {"title": "d", "status": "done"},
        {"title": "c"},
        {"title": "b"},
        {"title": "a"},
    )

    response = client.get(
        "/tasks", params={"sort": "title", "status": "todo", "size": 2, "page": 1}
    )
    body = response.json()

    assert titles(response) == ["a", "b"]
    assert body["total"] == 3
    assert body["total_pages"] == 2
    page2 = client.get("/tasks", params={"sort": "title", "status": "todo", "size": 2, "page": 2})
    assert titles(page2) == ["c"]


def test_unknown_sort_is_rejected(client):
    response = client.get("/tasks", params={"sort": "priority"})

    assert response.status_code == 422


def test_unknown_order_is_rejected(client):
    response = client.get("/tasks", params={"sort": "title", "order": "up"})

    assert response.status_code == 422


def test_unknown_order_without_sort_is_rejected(client):
    response = client.get("/tasks", params={"order": "sideways"})

    assert response.status_code == 422


def test_title_sort_treats_nfc_and_nfd_the_same(client):
    """#22: NFC "é" sorted after "z" while NFD "é" sorted with "e"."""
    make(client, {"title": "éb"}, {"title": "éa"}, {"title": "f"})

    response = client.get("/tasks", params={"sort": "title"})

    assert [t["id"] for t in response.json()["items"]] == [3, 2, 1]


def test_sort_combined_with_search(client):
    make(
        client,
        {"title": "write report"},
        {"title": "read mail"},
        {"title": "draft report"},
    )

    response = client.get("/tasks", params={"q": "report", "sort": "title"})

    assert titles(response) == ["draft report", "write report"]


def test_sort_combined_with_due_before(client):
    make(
        client,
        {"title": "late", "due_date": "2026-10-20"},
        {"title": "too late", "due_date": "2026-11-30"},
        {"title": "undated"},
        {"title": "early", "due_date": "2026-10-01"},
    )

    response = client.get(
        "/tasks", params={"due_before": "2026-11-01", "sort": "due_date", "order": "desc"}
    )

    assert titles(response) == ["late", "early"]


def test_sort_by_created_at_not_id(client, monkeypatch):
    """#22: created_at order can differ from id order (e.g. the clock steps back)."""
    stamps = iter(
        [
            datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc),
        ]
    )

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(stamps)

    monkeypatch.setattr("app.store.datetime", FakeDatetime)
    make(client, {"title": "noon"}, {"title": "nine"}, {"title": "ten"})

    asc = client.get("/tasks", params={"sort": "created_at"})
    desc = client.get("/tasks", params={"sort": "created_at", "order": "desc"})

    assert titles(asc) == ["nine", "ten", "noon"]
    assert titles(desc) == ["noon", "ten", "nine"]
