from __future__ import annotations

from typing import Any

import requests

from api.services.reading_repository import ReadingRepository


class SupabaseReadingRepository(ReadingRepository):
    def __init__(self, base_url: str, service_role_key: str) -> None:
        self._rest_url = f"{base_url.rstrip('/')}/rest/v1"
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }

    def save_reading(
        self,
        user_id: str,
        spread_type: str,
        seed: str,
        cards: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {
            "user_id": user_id,
            "spread_type": spread_type,
            "seed": seed,
            "cards": cards,
        }
        response = requests.post(
            f"{self._rest_url}/tarot_readings",
            headers={**self._headers, "Prefer": "return=representation"},
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)
        return response.json()[0]

    def list_readings(self, user_id: str) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self._rest_url}/tarot_readings",
            headers=self._headers,
            params={
                "select": "*",
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
            },
            timeout=10,
        )
        self._raise_if_error(response)
        return response.json()

    @staticmethod
    def _raise_if_error(response: requests.Response) -> None:
        if response.ok:
            return
        raise ValueError(f"Supabase request failed: {response.status_code} {response.text}")
