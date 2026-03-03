from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import storage


@pytest.fixture
def client(tmp_path: Path):
    storage.DB_PATH = tmp_path / "test_urls.db"
    storage.initialize_database()
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_page_served(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "URL Shortener" in response.text


def test_shorten_url_returns_short_link(client: TestClient):
    response = client.post("/shorten", json={"url": "https://www.python.org"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["original_url"] == "https://www.python.org/"
    assert payload["short_code"]
    assert payload["short_url"].endswith(f"/{payload['short_code']}")


def test_custom_alias_conflict_returns_409(client: TestClient):
    first = client.post(
        "/shorten",
        json={"url": "https://example.com", "custom_alias": "example"},
    )
    assert first.status_code == 200

    second = client.post(
        "/shorten",
        json={"url": "https://another.example", "custom_alias": "example"},
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "Custom alias already in use"


def test_redirect_for_existing_short_code(client: TestClient):
    create_response = client.post(
        "/shorten",
        json={"url": "https://example.com", "custom_alias": "go"},
    )
    assert create_response.status_code == 422

    create_response = client.post(
        "/shorten",
        json={"url": "https://example.com", "custom_alias": "goto"},
    )
    assert create_response.status_code == 200

    redirect_response = client.get("/goto", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/"
