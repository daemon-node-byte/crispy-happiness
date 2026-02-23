from __future__ import annotations

from api.app_factory import create_app
from api.config import AppConfig
from api.services.in_memory_repository import InMemoryUserRepository
from api.services.service_registry import Services
from api.services.session import SessionManager


def _build_test_app():
    services = Services(
        config=AppConfig(
            app_env="test",
            session_secret="test-secret",
            session_ttl_seconds=3600,
            supabase_url=None,
            supabase_service_role_key=None,
        ),
        repository=InMemoryUserRepository(),
        session_manager=SessionManager(secret="test-secret", max_age_seconds=3600),
    )
    app = create_app(services=services)
    app.config["TESTING"] = True
    return app


def test_signup_login_session_and_profile_update_flow():
    app = _build_test_app()
    client = app.test_client()

    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "password": "password123",
            "displayName": "Sky Seeker",
            "timezone": "UTC",
            "locale": "en-US",
        },
    )
    assert signup_response.status_code == 201
    signup_payload = signup_response.get_json()
    token = signup_payload["data"]["token"]
    session = signup_payload["data"]["session"]
    assert session["profile"]["displayName"] == "Sky Seeker"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    session_response = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert session_response.status_code == 200

    patch_response = client.patch(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"displayName": "Nova Reader", "timezone": "America/Chicago"},
    )
    assert patch_response.status_code == 200
    patch_payload = patch_response.get_json()
    assert patch_payload["data"]["profile"]["displayName"] == "Nova Reader"
    assert patch_payload["data"]["profile"]["timezone"] == "America/Chicago"


def test_telemetry_event_requires_matching_session_id():
    app = _build_test_app()
    client = app.test_client()

    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "telemetry@example.com",
            "password": "password123",
            "displayName": "Telemetry Tester",
        },
    )
    payload = signup_response.get_json()["data"]
    token = payload["token"]

    bad_event_response = client.post(
        "/api/telemetry/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "eventName": "dashboard_view",
            "sessionId": "mismatch",
            "properties": {"screen": "dashboard"},
        },
    )
    assert bad_event_response.status_code == 400

    good_event_response = client.post(
        "/api/telemetry/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "eventName": "dashboard_view",
            "sessionId": payload["session"]["sessionId"],
            "properties": {"screen": "dashboard"},
        },
    )
    assert good_event_response.status_code == 201
