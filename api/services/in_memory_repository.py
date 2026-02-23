from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, Tuple
from uuid import uuid4

from api.services.repository import UserRepository
from api.types import UserIdentity, UserProfile


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users_by_id: dict[str, tuple[UserIdentity, str]] = {}
        self._users_by_email: dict[str, str] = {}
        self._profiles: dict[str, UserProfile] = {}
        self._telemetry: list[dict[str, Any]] = []

    def create_user(self, email: str, password_hash: str) -> UserIdentity:
        email_key = email.strip().lower()
        if email_key in self._users_by_email:
            raise ValueError("Email already exists")

        user = UserIdentity(user_id=str(uuid4()), email=email_key)
        self._users_by_id[user.user_id] = (user, password_hash)
        self._users_by_email[email_key] = user.user_id
        return user

    def get_user_by_email(self, email: str) -> Optional[Tuple[UserIdentity, str]]:
        user_id = self._users_by_email.get(email.strip().lower())
        if user_id is None:
            return None
        return self._users_by_id.get(user_id)

    def get_user_by_id(self, user_id: str) -> Optional[UserIdentity]:
        user_row = self._users_by_id.get(user_id)
        if user_row is None:
            return None
        return user_row[0]

    def upsert_profile(
        self,
        user_id: str,
        display_name: str,
        timezone_name: str,
        locale: str,
    ) -> UserProfile:
        now = datetime.now(tz=timezone.utc)
        existing = self._profiles.get(user_id)
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            timezone=timezone_name,
            locale=locale,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        self._profiles[user_id] = profile
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self._profiles.get(user_id)

    def record_telemetry(
        self,
        user_id: str,
        session_id: str,
        event_name: str,
        properties: dict[str, Any],
    ) -> None:
        self._telemetry.append(
            {
                "user_id": user_id,
                "session_id": session_id,
                "event_name": event_name,
                "properties": properties,
                "created_at": datetime.now(tz=timezone.utc).isoformat(),
            }
        )
