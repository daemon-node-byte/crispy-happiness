from __future__ import annotations

from flask import Blueprint, current_app, request

from api.routes.auth_context import require_auth
from api.routes.http_utils import error, success

journal_blueprint = Blueprint("journal", __name__, url_prefix="/api/journal")


def _sanitize_text(value: str, default: str = "") -> str:
    return str(value or default).strip()


def _sanitize_tags(raw_tags) -> list[str]:
    if not raw_tags:
        return []
    if isinstance(raw_tags, list):
        return [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    return []


@journal_blueprint.post("")
def create_entry():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    payload = request.get_json(silent=True) or {}
    title = _sanitize_text(payload.get("title"), "Untitled")
    body = _sanitize_text(payload.get("body"), "")
    tags = _sanitize_tags(payload.get("tags"))

    entry = current_app.extensions["services"].journal_repository.create_entry(
        user_id=user.user_id,
        title=title,
        body=body,
        tags=tags,
    )

    return success({"entry": _serialize_entry(entry)}, 201)


@journal_blueprint.get("")
def list_entries():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    entries = current_app.extensions["services"].journal_repository.list_entries(user.user_id)
    return success({"entries": [_serialize_entry(entry) for entry in entries]})


@journal_blueprint.get("/<entry_id>")
def get_entry(entry_id: str):
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    entry = current_app.extensions["services"].journal_repository.get_entry(user.user_id, entry_id)
    if entry is None:
        return error("NOT_FOUND", "Entry not found", 404)
    return success({"entry": _serialize_entry(entry)})


@journal_blueprint.patch("/<entry_id>")
def update_entry(entry_id: str):
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    payload = request.get_json(silent=True) or {}
    title = _sanitize_text(payload.get("title"), "Untitled")
    body = _sanitize_text(payload.get("body"), "")
    tags = _sanitize_tags(payload.get("tags"))

    try:
        entry = current_app.extensions["services"].journal_repository.update_entry(
            user_id=user.user_id,
            entry_id=entry_id,
            title=title,
            body=body,
            tags=tags,
        )
    except ValueError:
        return error("NOT_FOUND", "Entry not found", 404)

    return success({"entry": _serialize_entry(entry)})


@journal_blueprint.delete("/<entry_id>")
def delete_entry(entry_id: str):
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    try:
        current_app.extensions["services"].journal_repository.delete_entry(user.user_id, entry_id)
    except ValueError:
        return error("NOT_FOUND", "Entry not found", 404)
    return success({"ok": True})


@journal_blueprint.get("/<entry_id>/export")
def export_entry(entry_id: str):
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    entry = current_app.extensions["services"].journal_repository.get_entry(user.user_id, entry_id)
    if entry is None:
        return error("NOT_FOUND", "Entry not found", 404)

    export_format = request.args.get("format", "markdown")
    if export_format not in {"markdown", "html"}:
        export_format = "markdown"

    if export_format == "html":
        content = f"<h1>{entry.title}</h1><p>{entry.body}</p>"
    else:
        content = f"# {entry.title}\n\n{entry.body}"

    return success({"entryId": entry.id, "format": export_format, "content": content})


def _serialize_entry(entry) -> dict[str, object]:
    return {
        "id": entry.id,
        "title": entry.title,
        "body": entry.body,
        "tags": entry.tags,
        "createdAt": entry.created_at.isoformat(),
        "updatedAt": entry.updated_at.isoformat(),
    }
