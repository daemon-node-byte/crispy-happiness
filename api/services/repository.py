from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from api.types import UserIdentity, UserProfile


class UserRepository(ABC):
    @abstractmethod
    def create_user(self, email: str, password_hash: str) -> UserIdentity:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Tuple[UserIdentity, str]]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[UserIdentity]:
        raise NotImplementedError

    @abstractmethod
    def upsert_profile(
        self,
        user_id: str,
        display_name: str,
        timezone_name: str,
        locale: str,
    ) -> UserProfile:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        raise NotImplementedError

    @abstractmethod
    def record_telemetry(
        self,
        user_id: str,
        session_id: str,
        event_name: str,
        properties: dict[str, Any],
    ) -> None:
        raise NotImplementedError
