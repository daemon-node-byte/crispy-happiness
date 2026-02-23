from __future__ import annotations

from flask import Blueprint, current_app, request

from api.routes.auth_context import require_auth
from api.routes.http_utils import error, success


profile_blueprint = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_blueprint.get("")
def get_profile():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    profile = current_app.extensions["services"].repository.get_profile(user.user_id)
    if profile is None:
        return error("NOT_FOUND", "Profile not found", 404)

    return success(
        {
            "profile": {
                "userId": profile.user_id,
                "displayName": profile.display_name,
                "timezone": profile.timezone,
                "locale": profile.locale,
                "createdAt": profile.created_at.isoformat(),
                "updatedAt": profile.updated_at.isoformat(),
            }
        }
    )


@profile_blueprint.patch("")
def patch_profile():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    payload = request.get_json(silent=True) or {}
    display_name = str(payload.get("displayName", "")).strip()
    timezone_value = str(payload.get("timezone", "")).strip()
    locale_value = str(payload.get("locale", "")).strip()

    current_profile = current_app.extensions["services"].repository.get_profile(user.user_id)
    if current_profile is None:
        return error("NOT_FOUND", "Profile not found", 404)

    profile = current_app.extensions["services"].repository.upsert_profile(
        user_id=user.user_id,
        display_name=display_name or current_profile.display_name,
        timezone_name=timezone_value or current_profile.timezone,
        locale=locale_value or current_profile.locale,
    )

    return success(
        {
            "profile": {
                "userId": profile.user_id,
                "displayName": profile.display_name,
                "timezone": profile.timezone,
                "locale": profile.locale,
                "createdAt": profile.created_at.isoformat(),
                "updatedAt": profile.updated_at.isoformat(),
            }
        }
    )
