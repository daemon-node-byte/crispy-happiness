from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    session_secret: str
    session_ttl_seconds: int
    supabase_url: Optional[str]
    supabase_service_role_key: Optional[str]


def load_config() -> AppConfig:
    return AppConfig(
        app_env=os.getenv("APP_ENV", "development"),
        session_secret=os.getenv("SESSION_SECRET", "local-dev-secret"),
        session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "86400")),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )
