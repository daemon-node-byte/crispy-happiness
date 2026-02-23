from __future__ import annotations

from typing import Generator

import pytest
from flask import Flask

from api.app_factory import create_app
from api.config import AppConfig
from api.services.in_memory_reading_repository import InMemoryReadingRepository
from api.services.in_memory_journal_repository import InMemoryJournalRepository
from api.services.in_memory_repository import InMemoryUserRepository
from api.services.service_registry import Services
from api.services.session import SessionManager
from api.services.tarot_data import TarotDataService


def _signup(client):
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "password": "supersecret",
            "displayName": "Seeker",
            "timezone": "UTC",
            "locale": "en-US",
        },
    )
    payload = response.get_json()
    return response, payload


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


def test_create_reading(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    response = client.post(
        "/api/readings",
        headers={"Authorization": f"Bearer {token}"},
        json={"spreadType": "three-card", "cardsCount": 3},
    )
    assert response.status_code == 201
    reading = response.get_json()["data"]["reading"]
    assert len(reading["cards"]) == 3


def test_card_of_day_is_stable(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    first = client.get(
        "/api/readings/card-of-day?timezone=UTC",
        headers={"Authorization": f"Bearer {token}"},
    )
    second = client.get(
        "/api/readings/card-of-day?timezone=UTC",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()["data"]["cardOfDay"]["slug"] == second.get_json()["data"]["cardOfDay"]["slug"]


def test_reading_list_returns_history(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    client.post(
        "/api/readings",
        headers={"Authorization": f"Bearer {token}"},
        json={"spreadType": "three-card", "cardsCount": 2},
    )
    list_response = client.get(
        "/api/readings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    readings = list_response.get_json()["data"]["readings"]
    assert len(readings) >= 1
