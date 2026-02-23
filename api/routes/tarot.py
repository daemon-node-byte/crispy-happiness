from __future__ import annotations

from flask import Blueprint, request

from api.routes.http_utils import error, success
from api.services.tarot_data import TarotDataService


tarot_blueprint = Blueprint("tarot", __name__, url_prefix="/api/tarot")
_data_service = TarotDataService()


@tarot_blueprint.get("/cards")
def list_cards():
  arcana = request.args.get("arcana")
  suit = request.args.get("suit")
  search = request.args.get("search")

  cards = _data_service.list_cards(arcana=arcana, suit=suit, search=search)
  return success({"cards": [_data_service.serialize(card) for card in cards]})


@tarot_blueprint.get("/cards/<slug>")
def get_card(slug: str):
  card = _data_service.get_card(slug)
  if card is None:
    return error("NOT_FOUND", "Card not found", 404)
  return success({"card": _data_service.serialize(card)})
