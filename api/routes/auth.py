from __future__ import annotations

from flask import Blueprint, current_app, request

from api.routes.auth_context import require_auth
from api.routes.http_utils import error, success
from api.services.security import hash_password, verify_password
from api.types import SessionData


auth_blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_blueprint.post("/signup")
def sign_up():
    services = current_app.extensions["services"]
    payload = request.get_json(silent=True) or {}

    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    display_name = str(payload.get("displayName", "")).strip() or "Seeker"
    user_timezone = str(payload.get("timezone", "UTC")).strip() or "UTC"
    locale = str(payload.get("locale", "en-US")).strip() or "en-US"

    if not email or "@" not in email:
        return error("VALIDATION_ERROR", "A valid email is required", 400)
    if len(password) < 8:
        return error("VALIDATION_ERROR", "Password must be at least 8 characters", 400)

    try:
        user = services.repository.create_user(
            email=email,
            password_hash=hash_password(password),
        )
        profile = services.repository.upsert_profile(
            user_id=user.user_id,
            display_name=display_name,
            timezone_name=user_timezone,
            locale=locale,
        )
        token, session_id, expires_at = services.session_manager.issue_token(
            user_id=user.user_id,
            email=user.email,
        )
        services.repository.record_telemetry(
            user_id=user.user_id,
            session_id=session_id,
            event_name="auth_signup_success",
            properties={"auth_provider": "password"},
        )
    except ValueError as err:
        return error("VALIDATION_ERROR", str(err), 400)

    session = SessionData(
        session_id=session_id,
        user=user,
        profile=profile,
        expires_at=expires_at,
    )
    return success({"token": token, "session": _serialize_session(session)}, 201)


@auth_blueprint.post("/login")
def log_in():
    services = current_app.extensions["services"]
    payload = request.get_json(silent=True) or {}

    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    user_row = services.repository.get_user_by_email(email)
    if user_row is None:
        return error("UNAUTHORIZED", "Invalid credentials", 401)

    user, password_hash = user_row
    if not verify_password(password, password_hash):
        return error("UNAUTHORIZED", "Invalid credentials", 401)

    profile = services.repository.get_profile(user.user_id)
    if profile is None:
        profile = services.repository.upsert_profile(
            user_id=user.user_id,
            display_name="Seeker",
            timezone_name="UTC",
            locale="en-US",
        )

    token, session_id, expires_at = services.session_manager.issue_token(
        user_id=user.user_id,
        email=user.email,
    )

    services.repository.record_telemetry(
        user_id=user.user_id,
        session_id=session_id,
        event_name="auth_login_success",
        properties={"auth_provider": "password"},
    )

    session = SessionData(
        session_id=session_id,
        user=user,
        profile=profile,
        expires_at=expires_at,
    )
    return success({"token": token, "session": _serialize_session(session)})


@auth_blueprint.post("/logout")
def log_out():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    services = current_app.extensions["services"]
    user, token_payload = auth_result
    services.repository.record_telemetry(
        user_id=user.user_id,
        session_id=token_payload["session_id"],
        event_name="auth_logout",
        properties={},
    )
    return success({"ok": True})


@auth_blueprint.get("/session")
def get_session():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    services = current_app.extensions["services"]
    user, token_payload = auth_result
    profile = services.repository.get_profile(user.user_id)
    if profile is None:
        return error("NOT_FOUND", "Profile not found", 404)

    expires_at = services.session_manager.get_expiry_from_now()
    session = SessionData(
        session_id=token_payload["session_id"],
        user=user,
        profile=profile,
        expires_at=expires_at,
    )
    return success({"session": _serialize_session(session)})


def _serialize_session(session: SessionData) -> dict[str, object]:
    return {
        "sessionId": session.session_id,
        "user": {
            "id": session.user.user_id,
            "email": session.user.email,
        },
        "profile": {
            "userId": session.profile.user_id,
            "displayName": session.profile.display_name,
            "timezone": session.profile.timezone,
            "locale": session.profile.locale,
            "createdAt": session.profile.created_at.isoformat(),
            "updatedAt": session.profile.updated_at.isoformat(),
        },
        "expiresAt": session.expires_at.isoformat(),
    }
