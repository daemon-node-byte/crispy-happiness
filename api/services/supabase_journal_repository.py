from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from api.services.journal_repository import JournalRepository
from api.types import JournalEntry


class SupabaseJournalRepository(JournalRepository):
    def __init__(self, base_url: str, service_role_key: str) -> None:
        self._rest_url = f"{base_url.rstrip('/')}/rest/v1"
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }

    def create_entry(self, user_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        payload = {"user_id": user_id, "title": title, "body": body, "tags": tags}
        response = requests.post(
            f"{self._rest_url}/journal_entries",
            headers={**self._headers, "Prefer": "return=representation"},
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)
        return self._to_entry(response.json()[0])

    def list_entries(self, user_id: str) -> list[JournalEntry]:
        response = requests.get(
            f"{self._rest_url}/journal_entries",
            headers=self._headers,
            params={
                "select": "*",
                "user_id": f"eq.{user_id}",
                "is_deleted": "eq.false",
                "order": "created_at.desc",
            },
            timeout=10,
        )
        self._raise_if_error(response)
        return [self._to_entry(row) for row in response.json()]

    def get_entry(self, user_id: str, entry_id: str) -> JournalEntry | None:
        response = requests.get(
            f"{self._rest_url}/journal_entries",
            headers=self._headers,
            params={"select": "*", "id": f"eq.{entry_id}", "user_id": f"eq.{user_id}", "limit": "1"},
            timeout=10,
        )
        self._raise_if_error(response)
        rows = response.json()
        if not rows:
            return None
        return self._to_entry(rows[0])

    def update_entry(self, user_id: str, entry_id: str, title: str, body: str, tags: list[str]) -> JournalEntry:
        payload = {"title": title, "body": body, "tags": tags}
        response = requests.patch(
            f"{self._rest_url}/journal_entries",
            headers={
                **self._headers,
                "Prefer": "return=representation",
            },
            params={"id": f"eq.{entry_id}", "user_id": f"eq.{user_id}"},
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)
        return self._to_entry(response.json()[0])

    def delete_entry(self, user_id: str, entry_id: str) -> None:
        payload = {"is_deleted": True}
        response = requests.patch(
            f"{self._rest_url}/journal_entries",
            headers={**self._headers, "Prefer": "return=representation"},
            params={"id": f"eq.{entry_id}", "user_id": f"eq.{user_id}"},
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)

    @staticmethod
    def _to_entry(row: dict[str, Any]) -> JournalEntry:
        return JournalEntry(
            id=row["id"],
            user_id=row["user_id"],
            title=row.get("title", ""),
            body=row.get("body", ""),
            tags=list(row.get("tags", [])),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
        )

    @staticmethod
    def _raise_if_error(response: requests.Response) -> None:
        if response.ok:
            return
        raise ValueError(f"Supabase request failed: {response.status_code} {response.text}")
