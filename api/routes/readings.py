from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, current_app, request

from api.routes.auth_context import require_auth
from api.routes.http_utils import error, success
from api.services.tarot_data import TarotDataService

readings_blueprint = Blueprint("readings", __name__, url_prefix="/api/readings")
_data_service = TarotDataService()


@readings_blueprint.post("")
def create_reading():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    payload = request.get_json(silent=True) or {}
    spread_type = str(payload.get("spreadType", "three-card")).strip() or "three-card"
    cards_count = int(payload.get("cardsCount", 3))
    cards_count = min(max(cards_count, 1), 10)

    cards_source = _data_service.list_cards()
    seed = str(uuid4())
    rng = random.Random(seed)
    sampled = rng.sample(cards_source, k=min(cards_count, len(cards_source)))

    drawn = []
    for card in sampled:
        orientation = rng.choice(["upright", "reversed"])
        drawn.append({"slug": card.slug, "orientation": orientation})

    saved = current_app.extensions["services"].reading_repository.save_reading(
        user_id=user.user_id,
        spread_type=spread_type,
        seed=seed,
        cards=drawn,
    )

    return success(
        {
            "reading": {
                "id": saved.get("id"),
                "spreadType": spread_type,
                "seed": seed,
                "cards": drawn,
                "createdAt": saved.get("created_at", datetime.now(tz=timezone.utc).isoformat()),
            }
        },
        201,
    )


@readings_blueprint.get("")
def list_readings():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    rows = current_app.extensions["services"].reading_repository.list_readings(user.user_id)
    readings = [
        {
            "id": row.get("id"),
            "spreadType": row.get("spread_type", row.get("spreadType")),
            "seed": row.get("seed"),
            "cards": row.get("cards", []),
            "createdAt": row.get("created_at", datetime.now(tz=timezone.utc).isoformat()),
        }
        for row in rows
    ]
    return success({"readings": readings})


@readings_blueprint.get("/card-of-day")
def card_of_day():
    auth_result = require_auth()
    if isinstance(auth_result, tuple) and len(auth_result) == 2 and isinstance(auth_result[1], int):
        return auth_result

    user, _ = auth_result
    tz = request.args.get("timezone", "UTC")
    now = datetime.now(tz=timezone.utc)
    try:
        tzinfo = timezone.utc if tz.upper() == "UTC" else datetime.now().astimezone().tzinfo
        today = now.astimezone(tzinfo).date()
    except Exception:
        today = now.date()

    cards = _data_service.list_cards()
    if not cards:
        return error("NOT_FOUND", "No cards available", 404)

    key = f"{user.user_id}-{today.isoformat()}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    index = int.from_bytes(digest[:4], "big") % len(cards)
    card = cards[index]

    payload = {
        "slug": card.slug,
        "name": card.name,
        "image": card.image,
        "keywords": card.keywords,
        "upright": card.upright,
        "reversed": card.reversed,
        "forDate": today.isoformat(),
        "timezone": tz,
    }

    return success({"cardOfDay": payload})
