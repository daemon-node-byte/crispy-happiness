from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ReadingRepository(ABC):
    @abstractmethod
    def save_reading(
        self,
        user_id: str,
        spread_type: str,
        seed: str,
        cards: list[dict[str, Any]],
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_readings(self, user_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError
