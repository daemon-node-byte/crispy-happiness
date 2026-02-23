from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Tuple

import requests

from api.services.repository import UserRepository
from api.types import UserIdentity, UserProfile


class SupabaseRepository(UserRepository):
    def __init__(self, base_url: str, service_role_key: str) -> None:
        self._rest_url = f"{base_url.rstrip('/')}/rest/v1"
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }

    def create_user(self, email: str, password_hash: str) -> UserIdentity:
        payload = {
            "email": email.strip().lower(),
            "password_hash": password_hash,
        }
        response = requests.post(
            f"{self._rest_url}/app_users",
            headers={**self._headers, "Prefer": "return=representation"},
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)
        user_row = response.json()[0]
        return UserIdentity(user_id=user_row["id"], email=user_row["email"])

    def get_user_by_email(self, email: str) -> Optional[Tuple[UserIdentity, str]]:
        response = requests.get(
            f"{self._rest_url}/app_users",
            headers=self._headers,
            params={
                "select": "id,email,password_hash",
                "email": f"eq.{email.strip().lower()}",
                "limit": "1",
            },
            timeout=10,
        )
        self._raise_if_error(response)
        rows = response.json()
        if not rows:
            return None
        user_row = rows[0]
        return (
            UserIdentity(user_id=user_row["id"], email=user_row["email"]),
            user_row["password_hash"],
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserIdentity]:
        response = requests.get(
            f"{self._rest_url}/app_users",
            headers=self._headers,
            params={
                "select": "id,email",
                "id": f"eq.{user_id}",
                "limit": "1",
            },
            timeout=10,
        )
        self._raise_if_error(response)
        rows = response.json()
        if not rows:
            return None
        user_row = rows[0]
        return UserIdentity(user_id=user_row["id"], email=user_row["email"])

    def upsert_profile(
        self,
        user_id: str,
        display_name: str,
        timezone_name: str,
        locale: str,
    ) -> UserProfile:
        payload = {
            "user_id": user_id,
            "display_name": display_name,
            "timezone": timezone_name,
            "locale": locale,
        }
        response = requests.post(
            f"{self._rest_url}/profiles",
            headers={
                **self._headers,
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)
        profile_row = response.json()[0]
        return self._to_profile(profile_row)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        response = requests.get(
            f"{self._rest_url}/profiles",
            headers=self._headers,
            params={
                "select": "*",
                "user_id": f"eq.{user_id}",
                "limit": "1",
            },
            timeout=10,
        )
        self._raise_if_error(response)
        rows = response.json()
        if not rows:
            return None
        return self._to_profile(rows[0])

    def record_telemetry(
        self,
        user_id: str,
        session_id: str,
        event_name: str,
        properties: dict[str, Any],
    ) -> None:
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "event_name": event_name,
            "properties": properties,
        }
        response = requests.post(
            f"{self._rest_url}/telemetry_events",
            headers=self._headers,
            json=payload,
            timeout=10,
        )
        self._raise_if_error(response)

    @staticmethod
    def _to_profile(profile_row: dict[str, Any]) -> UserProfile:
        return UserProfile(
            user_id=profile_row["user_id"],
            display_name=profile_row["display_name"],
            timezone=profile_row["timezone"],
            locale=profile_row["locale"],
            created_at=datetime.fromisoformat(profile_row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(profile_row["updated_at"].replace("Z", "+00:00")),
        )

    @staticmethod
    def _raise_if_error(response: requests.Response) -> None:
        if response.ok:
            return
        raise ValueError(f"Supabase request failed: {response.status_code} {response.text}")
