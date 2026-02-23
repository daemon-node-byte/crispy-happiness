from __future__ import annotations

from typing import Any, Dict, Tuple, Union

from flask import current_app, request

from api.routes.http_utils import error
from api.types import UserIdentity


def require_auth() -> Union[Tuple[UserIdentity, Dict[str, str]], Tuple[Any, int]]:
    services = current_app.extensions["services"]
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return error("UNAUTHORIZED", "Missing bearer token", 401)

    token = auth_header.split(" ", 1)[1].strip()
    try:
        token_payload = services.session_manager.validate_token(token)
    except ValueError as err:
        return error("UNAUTHORIZED", str(err), 401)

    user = services.repository.get_user_by_id(token_payload["user_id"])
    if user is None:
        return error("UNAUTHORIZED", "User not found", 401)

    return user, token_payload
