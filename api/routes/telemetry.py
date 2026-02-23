from __future__ import annotations

from flask import Blueprint, current_app, request

from api.routes.auth_context import require_auth
from api.routes.http_utils import error, success


telemetry_blueprint = Blueprint("telemetry", __name__, url_prefix="/api/telemetry")
_ALLOWED_EVENTS = {
    "auth_signup_success",
    "auth_login_success",
    "auth_logout",
    "dashboard_view",
}


@telemetry_blueprint.post("/events")
def create_telemetry_event():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, token_payload = auth_result
    payload = request.get_json(silent=True) or {}
    event_name = str(payload.get("eventName", "")).strip()
    session_id = str(payload.get("sessionId", "")).strip()
    properties = payload.get("properties") or {}

    if event_name not in _ALLOWED_EVENTS:
        return error("VALIDATION_ERROR", "Invalid event name", 400)
    if session_id != token_payload["session_id"]:
        return error("VALIDATION_ERROR", "Session mismatch", 400)
    if not isinstance(properties, dict):
        return error("VALIDATION_ERROR", "Properties must be an object", 400)

    current_app.extensions["services"].repository.record_telemetry(
        user_id=user.user_id,
        session_id=session_id,
        event_name=event_name,
        properties=properties,
    )
    return success({"ok": True}, 201)
