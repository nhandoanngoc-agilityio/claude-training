import unicodedata

import pytest


def titles(response):
    return [t["title"] for t in response.json()["items"]]


def nfc(text):
    return unicodedata.normalize("NFC", text)


def nfd(text):
    text = unicodedata.normalize("NFD", text)
    assert text != nfc(text)
    return text


def test_search_is_case_insensitive_substring(client):
    """#9: "rep" finds "Report"."""
    client.post("/tasks", json={"title": "Report"})
    client.post("/tasks", json={"title": "Plan sprint"})

    response = client.get("/tasks", params={"q": "rep"})

    assert response.status_code == 200
    assert titles(response) == ["Report"]


def test_search_matches_description(client):
    client.post("/tasks", json={"title": "Write up", "description": "Quarterly REPORT"})
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks", params={"q": "report"})

    assert titles(response) == ["Write up"]


def test_search_skips_tasks_without_description(client):
    client.post("/tasks", json={"title": "Read docs"})

    response = client.get("/tasks", params={"q": "report"})

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_search_matches_whole_phrase(client):
    client.post("/tasks", json={"title": "Send weekly report"})
    client.post("/tasks", json={"title": "Report weekly"})

    response = client.get("/tasks", params={"q": "weekly report"})

    assert titles(response) == ["Send weekly report"]


def test_search_keeps_id_order(client):
    client.post("/tasks", json={"title": "Report B"})
    client.post("/tasks", json={"title": "Other"})
    client.post("/tasks", json={"title": "Report A"})

    response = client.get("/tasks", params={"q": "report"})

    assert titles(response) == ["Report B", "Report A"]


def test_search_combines_with_filters(client):
    client.post("/tasks", json={"title": "Report", "status": "done", "due_date": "2026-10-22"})
    client.post("/tasks", json={"title": "Report", "status": "todo", "due_date": "2026-10-22"})
    client.post("/tasks", json={"title": "Report late", "status": "done", "due_date": "2026-11-30"})
    client.post("/tasks", json={"title": "Plan", "status": "done", "due_date": "2026-10-22"})

    response = client.get(
        "/tasks", params={"q": "report", "status": "done", "due_before": "2026-10-26"}
    )

    assert [t["id"] for t in response.json()["items"]] == [1]


def test_search_paging_counts_only_matches(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Report {i}"})
        client.post("/tasks", json={"title": f"Other {i}"})

    response = client.get("/tasks", params={"q": "report", "page": 3, "size": 2})

    body = response.json()
    assert body["total"] == 5
    assert body["total_pages"] == 3
    assert titles(response) == ["Report 4"]


@pytest.mark.parametrize(
    ("q", "error_type"),
    [
        pytest.param("", "string_too_short", id="empty"),
        pytest.param("   ", "string_pattern_mismatch", id="blank"),
        pytest.param("a" * 201, "string_too_long", id="ascii-201cp"),
        # #14: max_length counts code points, so NFD text hits the limit sooner.
        pytest.param(nfd("\u1ec7" * 67), "string_too_long", id="nfd-201cp"),  # "ệ"
        pytest.param(nfd("\u1ec7" * 70), "string_too_long", id="nfd-210cp"),
    ],
)
def test_search_rejects_invalid_query(client, q, error_type):
    response = client.get("/tasks", params={"q": q})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == error_type


@pytest.mark.parametrize(
    "q",
    [
        pytest.param("a" * 200, id="ascii-200cp"),
        pytest.param("\u1ec7" * 70, id="nfc-70cp"),  # "ệ"
        pytest.param(nfd("\u1ec7" * 66) + "ab", id="nfd-200cp"),
    ],
)
def test_search_accepts_max_length_query(client, q):
    response = client.get("/tasks", params={"q": q})

    assert response.status_code == 200


# Non-ASCII text is written with escapes so editors can't re-normalize it.
REPORT_TITLE = "B\u00e1o c\u00e1o tu\u1ea7n"  # "Báo cáo tuần"
REPORT_QUERY = "b\u00e1o c\u00e1o"  # "báo cáo"


@pytest.mark.parametrize("title_form", [nfc, nfd])
@pytest.mark.parametrize("query_form", [nfc, nfd])
def test_search_ignores_unicode_normalization_form(client, title_form, query_form):
    """#13: the same visible text matches whether it arrives as NFC or NFD."""
    title = title_form(REPORT_TITLE)
    client.post("/tasks", json={"title": title})

    response = client.get("/tasks", params={"q": query_form(REPORT_QUERY)})

    assert titles(response) == [title]


def test_search_normalizes_description(client):
    client.post("/tasks", json={"title": "Write up", "description": nfd(REPORT_TITLE)})

    response = client.get("/tasks", params={"q": nfc(REPORT_QUERY)})

    assert titles(response) == ["Write up"]


def test_search_normalization_combines_with_case(client):
    client.post("/tasks", json={"title": nfc(REPORT_TITLE)})

    response = client.get("/tasks", params={"q": nfd(REPORT_QUERY.upper())})

    assert titles(response) == [nfc(REPORT_TITLE)]


@pytest.mark.parametrize(
    "he",
    [
        "h\u1ec7",  # precomposed
        "he\u0323\u0302",  # canonical mark order
        "he\u0302\u0323",  # marks in the other order
        "h\u1eb9\u0302",  # partly composed
        "h\u00ea\u0323",  # partly composed
    ],
)
def test_search_matches_any_vietnamese_mark_order(client, he):
    client.post("/tasks", json={"title": "Ki\u1ec3m tra h\u1ec7 th\u1ed1ng"})

    response = client.get("/tasks", params={"q": he})

    assert response.json()["total"] == 1


@pytest.mark.parametrize("title_form", [nfc, nfd])
@pytest.mark.parametrize("q", ["bao cao", "ba", "\u0301"])
def test_search_stays_accent_sensitive(client, title_form, q):
    """Accent-insensitive search is out of scope (#9): "ba" must not find "Báo"."""
    client.post("/tasks", json={"title": title_form(REPORT_TITLE)})

    response = client.get("/tasks", params={"q": q})

    assert response.status_code == 200
    assert response.json()["items"] == []
