from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from api.types import JournalEntry


class JournalRepository(ABC):
    @abstractmethod
    def create_entry(self, user_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        raise NotImplementedError

    @abstractmethod
    def list_entries(self, user_id: str) -> list[JournalEntry]:
        raise NotImplementedError

    @abstractmethod
    def get_entry(self, user_id: str, entry_id: str) -> JournalEntry | None:
        raise NotImplementedError

    @abstractmethod
    def update_entry(self, user_id: str, entry_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        raise NotImplementedError

    @abstractmethod
    def delete_entry(self, user_id: str, entry_id: str) -> None:
        raise NotImplementedError
