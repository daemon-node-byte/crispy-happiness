from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from api.services.journal_repository import JournalRepository
from api.types import JournalEntry


class InMemoryJournalRepository(JournalRepository):
    def __init__(self) -> None:
        self._entries: dict[str, JournalEntry] = {}

    def create_entry(self, user_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        now = datetime.now(tz=timezone.utc)
        entry = JournalEntry(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            body=body,
            tags=tags,
            created_at=now,
            updated_at=now,
        )
        self._entries[entry.id] = entry
        return entry

    def list_entries(self, user_id: str) -> list[JournalEntry]:
        return [e for e in self._entries.values() if e.user_id == user_id]

    def get_entry(self, user_id: str, entry_id: str) -> JournalEntry | None:
        entry = self._entries.get(entry_id)
        if entry is None or entry.user_id != user_id:
            return None
        return entry

    def update_entry(self, user_id: str, entry_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        entry = self.get_entry(user_id, entry_id)
        if entry is None:
            raise ValueError("Entry not found")
        updated = JournalEntry(
            id=entry.id,
            user_id=entry.user_id,
            title=title,
            body=body,
            tags=tags,
            created_at=entry.created_at,
            updated_at=datetime.now(tz=timezone.utc),
        )
        self._entries[entry.id] = updated
        return updated

    def delete_entry(self, user_id: str, entry_id: str) -> None:
        entry = self.get_entry(user_id, entry_id)
        if entry is None:
            raise ValueError("Entry not found")
        self._entries.pop(entry.id, None)
