from app import app, entries

import pytest

# Use Flask's test client for testing

TEST_PASSWORD = "testpasswort"


@pytest.fixture()
def client(monkeypatch):
    app.config["TESTING"] = True
    # Tests sollen nicht von einer lokalen .env abhaengen
    monkeypatch.setattr("app.PASSWORD", TEST_PASSWORD)
    # entries ist eine globale Liste: vor jedem Test leeren,
    # damit sich die Tests nicht gegenseitig beeinflussen
    entries.clear()
    client = app.test_client()

    yield client


def login(client):
    with client.session_transaction() as session:
        session["logged_in"] = True


def test_add_entry(client):
    # Test adding an entry
    response = client.post("/add_entry", data={"content": "Test Entry Content"})

    # Check if the response is a redirect to the index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Check if the entry was added to the database
    entry = entries[0]
    assert entry is not None
    assert entry.content == "Test Entry Content"


def test_add_entry_without_content_is_ignored(client):
    response = client.post("/add_entry", data={"content": ""})

    assert response.status_code == 302
    assert entries == []


def test_index_asks_for_login(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Please log in" in response.get_data(as_text=True)


def test_index_shows_entries_when_logged_in(client):
    login(client)
    client.post("/add_entry", data={"content": "Mein erster Eintrag"})

    page = client.get("/").get_data(as_text=True)

    assert "Welcome, you are logged in!" in page
    assert "Mein erster Eintrag" in page


def test_login_page_is_shown(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert 'name="password"' in response.get_data(as_text=True)


def test_login_with_correct_password(client):
    response = client.post("/login", data={"password": TEST_PASSWORD})

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with client.session_transaction() as session:
        assert session["logged_in"] is True


def test_login_with_wrong_password(client):
    response = client.post("/login", data={"password": "falsch"})

    assert response.status_code == 200
    assert "Incorrect password" in response.get_data(as_text=True)
    with client.session_transaction() as session:
        assert "logged_in" not in session


def test_logout(client):
    login(client)

    response = client.get("/logout")

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert "logged_in" not in session


def test_add_entry_with_happiness(client):
    # Test adding an entry with happiness
    response = client.post(
        "/add_entry", data={"content": "Test Entry Content", "happiness": "😃"}
    )

    # Check if the response is a redirect to the index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Check if the entry was added to the database with the correct happiness
    entry = entries[0]
    assert entry is not None
    assert entry.content == "Test Entry Content"
    assert entry.happiness == "😃"


def test_add_entry_without_happiness_has_no_mood(client):
    client.post("/add_entry", data={"content": "Ohne Laune"})

    assert entries[0].happiness == ""


def test_index_shows_happiness(client):
    login(client)
    client.post("/add_entry", data={"content": "Guter Tag", "happiness": "🙂"})

    page = client.get("/").get_data(as_text=True)

    assert 'name="happiness"' in page
    assert "🙂 - Guter Tag" in page
