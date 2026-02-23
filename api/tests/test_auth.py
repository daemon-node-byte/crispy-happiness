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
def test_app() -> Flask:
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
    return app


@pytest.fixture()
def client(test_app: Flask) -> Generator:
    with test_app.test_client() as client:
        yield client


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


def test_signup_and_login_flow(client):
    response, payload = _signup(client)
    assert response.status_code == 201
    assert payload["data"]["token"]
    session = payload["data"]["session"]
    assert session["user"]["email"] == "user@example.com"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.get_json()["data"]
    assert login_payload["session"]["user"]["id"] == session["user"]["id"]

    session_response = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {login_payload['token']}"},
    )
    assert session_response.status_code == 200
    session_body = session_response.get_json()["data"]["session"]
    assert session_body["profile"]["displayName"] == "Seeker"


def test_profile_patch(client):
    _, payload = _signup(client)
    token = payload["data"]["token"]

    patch_response = client.patch(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"displayName": "Reader", "timezone": "America/New_York"},
    )
    assert patch_response.status_code == 200
    profile = patch_response.get_json()["data"]["profile"]
    assert profile["displayName"] == "Reader"
    assert profile["timezone"] == "America/New_York"


def test_telemetry_requires_valid_event_and_session(client):
    signup_resp, payload = _signup(client)
    token = payload["data"]["token"]
    session = payload["data"]["session"]

    ok_response = client.post(
        "/api/telemetry/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "eventName": "dashboard_view",
            "sessionId": session["sessionId"],
            "properties": {"screen": "dashboard"},
        },
    )
    assert ok_response.status_code == 201

    bad_response = client.post(
        "/api/telemetry/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "eventName": "unknown_event",
            "sessionId": session["sessionId"],
            "properties": {},
        },
    )
    assert bad_response.status_code == 400


def test_login_rejects_wrong_password(client):
    _signup(client)
    login_response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrongpass"},
    )
    assert login_response.status_code == 401
