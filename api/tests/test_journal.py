from __future__ import annotations

from typing import Generator

import pytest

from api.app_factory import create_app
from api.config import AppConfig
from api.services.in_memory_journal_repository import InMemoryJournalRepository
from api.services.in_memory_reading_repository import InMemoryReadingRepository
from api.services.in_memory_repository import InMemoryUserRepository
from api.services.service_registry import Services
from api.services.session import SessionManager


@pytest.fixture()
def client() -> Generator:
    repository = InMemoryUserRepository()
    reading_repo = InMemoryReadingRepository()
    journal_repo = InMemoryJournalRepository()
    config = AppConfig(
        app_env="test",
        session_secret="test-secret",
        session_ttl_seconds=3600,
        supabase_url=None,
        supabase_service_role_key=None,
    )
    session_manager = SessionManager(secret=config.session_secret, max_age_seconds=config.session_ttl_seconds)
    services = Services(
        config=config,
        repository=repository,
        user_repository=repository,
        reading_repository=reading_repo,
        journal_repository=journal_repo,
        session_manager=session_manager,
    )
    app = create_app(services)
    app.testing = True

    with app.test_client() as client:
        yield client


def _signup(client):
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "journal-user@example.com",
            "password": "supersecret",
            "displayName": "Seeker",
            "timezone": "UTC",
            "locale": "en-US",
        },
    )
    payload = response.get_json()
    return response, payload


def test_journal_requires_auth(client):
    response = client.get("/api/journal")
    assert response.status_code == 401


def test_create_list_and_get_entry(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    create_response = client.post(
        "/api/journal",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Morning Draw", "body": "I pulled The Fool.", "tags": ["morning", "fool"]},
    )
    assert create_response.status_code == 201
    entry = create_response.get_json()["data"]["entry"]
    assert entry["title"] == "Morning Draw"
    assert entry["tags"] == ["morning", "fool"]

    list_response = client.get("/api/journal", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    entries = list_response.get_json()["data"]["entries"]
    assert len(entries) == 1
    assert entries[0]["id"] == entry["id"]

    get_response = client.get(f"/api/journal/{entry['id']}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 200
    fetched = get_response.get_json()["data"]["entry"]
    assert fetched["body"] == "I pulled The Fool."


def test_update_delete_and_not_found_entry(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    create_response = client.post(
        "/api/journal",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Draft", "body": "Initial body", "tags": ["draft"]},
    )
    entry_id = create_response.get_json()["data"]["entry"]["id"]

    update_response = client.patch(
        f"/api/journal/{entry_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Revised", "body": "Updated body", "tags": ["revised", "reflection"]},
    )
    assert update_response.status_code == 200
    updated = update_response.get_json()["data"]["entry"]
    assert updated["title"] == "Revised"
    assert updated["tags"] == ["revised", "reflection"]

    delete_response = client.delete(f"/api/journal/{entry_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete_response.status_code == 200
    assert delete_response.get_json()["data"]["ok"] is True

    get_response = client.get(f"/api/journal/{entry_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 404


def test_export_entry_markdown_and_html(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    create_response = client.post(
        "/api/journal",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Export me", "body": "This should export.", "tags": ["export"]},
    )
    entry = create_response.get_json()["data"]["entry"]

    markdown_response = client.get(
        f"/api/journal/{entry['id']}/export?format=markdown",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert markdown_response.status_code == 200
    markdown = markdown_response.get_json()["data"]
    assert markdown["format"] == "markdown"
    assert markdown["content"] == "# Export me\n\nThis should export."

    html_response = client.get(
        f"/api/journal/{entry['id']}/export?format=html",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert html_response.status_code == 200
    html = html_response.get_json()["data"]
    assert html["format"] == "html"
    assert html["content"] == "<h1>Export me</h1><p>This should export.</p>"
