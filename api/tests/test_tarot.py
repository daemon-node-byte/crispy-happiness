from __future__ import annotations

from typing import Generator

import pytest
from flask import Flask

from api.app_factory import create_app
from api.config import AppConfig
from api.services.in_memory_repository import InMemoryUserRepository
from api.services.in_memory_reading_repository import InMemoryReadingRepository
from api.services.service_registry import Services
from api.services.session import SessionManager


@pytest.fixture()
def client() -> Generator:
    repository = InMemoryUserRepository()
    reading_repo = InMemoryReadingRepository()
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
        session_manager=session_manager,
    )
    app = create_app(services)
    app.testing = True

    with app.test_client() as client:
        yield client


def test_list_cards(client):
    response = client.get("/api/tarot/cards")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data["cards"]) >= 3


def test_filter_cards_by_arcana(client):
    response = client.get("/api/tarot/cards?arcana=major")
    assert response.status_code == 200
    cards = response.get_json()["data"]["cards"]
    assert all(card["arcana"] == "major" for card in cards)


def test_get_card_detail(client):
    response = client.get("/api/tarot/cards/the-fool")
    assert response.status_code == 200
    card = response.get_json()["data"]["card"]
    assert card["name"] == "The Fool"


def test_get_card_not_found(client):
    response = client.get("/api/tarot/cards/not-real")
    assert response.status_code == 404
