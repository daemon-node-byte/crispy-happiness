from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import yaml

from api.types import TarotCard


class TarotDataService:
    def __init__(self, data_path: Path | None = None) -> None:
        self._data_path = data_path or Path(__file__).resolve().parent.parent.parent / "data" / "tarot" / "cards.yaml"
        self._cards: list[TarotCard] | None = None

    def _load(self) -> list[TarotCard]:
        if self._cards is not None:
            return self._cards

        with self._data_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)

        cards: list[TarotCard] = []
        for card in payload.get("cards", []):
            cards.append(
                TarotCard(
                    id=card["id"],
                    name=card["name"],
                    slug=card["slug"],
                    arcana=card["arcana"],
                    suit=card.get("suit"),
                    number=card.get("number"),
                    keywords=list(card.get("keywords", [])),
                    description=card.get("description", ""),
                    upright=list(card.get("upright", [])),
                    reversed=list(card.get("reversed", [])),
                    image=card.get("image", ""),
                )
            )

        self._cards = cards
        return cards

    def list_cards(
        self,
        arcana: str | None = None,
        suit: str | None = None,
        search: str | None = None,
    ) -> list[TarotCard]:
        cards = self._load()
        results: Iterable[TarotCard] = cards

        if arcana:
            results = [card for card in results if card.arcana == arcana]
        if suit:
            results = [card for card in results if card.suit == suit]
        if search:
            q = search.lower()
            results = [
                card
                for card in results
                if q in card.name.lower()
                or any(q in kw.lower() for kw in card.keywords)
                or (card.description and q in card.description.lower())
            ]

        return list(results)

    def get_card(self, slug: str) -> TarotCard | None:
        for card in self._load():
            if card.slug == slug:
                return card
        return None

    @staticmethod
    def serialize(card: TarotCard) -> dict[str, object]:
        data = asdict(card)
        return {
            "id": data["id"],
            "name": data["name"],
            "slug": data["slug"],
            "arcana": data["arcana"],
            "suit": data.get("suit"),
            "number": data.get("number"),
            "keywords": data.get("keywords", []),
            "description": data.get("description", ""),
            "upright": data.get("upright", []),
            "reversed": data.get("reversed", []),
            "image": data.get("image", ""),
        }
