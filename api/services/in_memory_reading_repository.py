from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from api.services.reading_repository import ReadingRepository


class InMemoryReadingRepository(ReadingRepository):
    def __init__(self) -> None:
        self._readings: list[dict[str, Any]] = []

    def save_reading(
        self,
        user_id: str,
        spread_type: str,
        seed: str,
        cards: list[dict[str, Any]],
    ) -> dict[str, Any]:
        reading = {
            "id": str(uuid4()),
            "user_id": user_id,
            "spread_type": spread_type,
            "seed": seed,
            "cards": cards,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._readings.append(reading)
        return reading

    def list_readings(self, user_id: str) -> list[dict[str, Any]]:
        return [r for r in self._readings if r["user_id"] == user_id]
