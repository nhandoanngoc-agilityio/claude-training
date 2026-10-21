import unicodedata

import pytest


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


# Non-ASCII text is written with escapes so editors can't re-normalize it.
E_CIRCUMFLEX_ACUTE = "\u1ebf"  # "ế": 1 code point in NFC, 3 in NFD


def nfd(text):
    text = unicodedata.normalize("NFD", text)
    assert text != unicodedata.normalize("NFC", text)
    return text


# #14: max_length counts code points, so NFD text hits the 200 limit sooner.
TITLES_WITHIN_LIMIT = [
    pytest.param(E_CIRCUMFLEX_ACUTE * 70, id="nfc-70cp"),
    pytest.param(nfd(E_CIRCUMFLEX_ACUTE * 66) + "ab", id="nfd-200cp"),
]
TITLES_OVER_LIMIT = [
    pytest.param(nfd(E_CIRCUMFLEX_ACUTE * 67), id="nfd-201cp"),
    pytest.param(nfd(E_CIRCUMFLEX_ACUTE * 70), id="nfd-210cp"),
]


@pytest.mark.parametrize("title", TITLES_WITHIN_LIMIT)
def test_create_accepts_title_within_code_point_limit(client, title):
    response = client.post("/tasks", json={"title": title})

    assert response.status_code == 201
    assert response.json()["title"] == title


@pytest.mark.parametrize("title", TITLES_OVER_LIMIT)
def test_create_rejects_title_over_code_point_limit(client, title):
    response = client.post("/tasks", json={"title": title})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_long"


@pytest.mark.parametrize("title", TITLES_WITHIN_LIMIT)
def test_patch_accepts_title_within_code_point_limit(client, title):
    task = client.post("/tasks", json={"title": "Real title"}).json()

    response = client.patch(f"/tasks/{task['id']}", json={"title": title})

    assert response.status_code == 200
    assert response.json()["title"] == title


@pytest.mark.parametrize("title", TITLES_OVER_LIMIT)
def test_patch_rejects_title_over_code_point_limit(client, title):
    task = client.post("/tasks", json={"title": "Real title"}).json()

    response = client.patch(f"/tasks/{task['id']}", json={"title": title})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_long"
    assert client.get(f"/tasks/{task['id']}").json()["title"] == "Real title"
