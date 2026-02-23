from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserIdentity:
    user_id: str
    email: str


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    display_name: str
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SessionData:
    session_id: str
    user: UserIdentity
    profile: UserProfile
    expires_at: datetime


@dataclass(frozen=True)
class TelemetryEvent:
    user_id: str
    session_id: str
    event_name: str
    properties: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class TarotCard:
    id: str
    name: str
    slug: str
    arcana: str
    suit: str | None
    number: int | None
    keywords: list[str]
    description: str
    upright: list[str]
    reversed: list[str]
    image: str


@dataclass(frozen=True)
class TarotReading:
    id: str
    user_id: str
    spread_type: str
    seed: str
    cards: list[dict[str, str]]
    created_at: datetime


@dataclass(frozen=True)
class JournalEntry:
    id: str
    user_id: str
    title: str
    body: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
