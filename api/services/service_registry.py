from __future__ import annotations

from dataclasses import dataclass

from api.config import AppConfig, load_config
from api.services.in_memory_repository import InMemoryUserRepository
from api.services.in_memory_reading_repository import InMemoryReadingRepository
from api.services.in_memory_journal_repository import InMemoryJournalRepository
from api.services.repository import UserRepository
from api.services.reading_repository import ReadingRepository
from api.services.journal_repository import JournalRepository
from api.services.session import SessionManager
from api.services.supabase_repository import SupabaseRepository
from api.services.supabase_reading_repository import SupabaseReadingRepository
from api.services.supabase_journal_repository import SupabaseJournalRepository


@dataclass(frozen=True)
class Services:
    config: AppConfig
    repository: UserRepository  # deprecated alias for user_repository
    user_repository: UserRepository
    reading_repository: ReadingRepository
    journal_repository: JournalRepository
    session_manager: SessionManager


_in_memory_repository = InMemoryUserRepository()
_in_memory_readings = InMemoryReadingRepository()
_in_memory_journal = InMemoryJournalRepository()


def build_services() -> Services:
    config = load_config()
    user_repo = _select_user_repository(config)
    reading_repo = _select_reading_repository(config)
    journal_repo = _select_journal_repository(config)
    session_manager = SessionManager(
        secret=config.session_secret,
        max_age_seconds=config.session_ttl_seconds,
    )
    return Services(
        config=config,
        repository=user_repo,
        user_repository=user_repo,
        reading_repository=reading_repo,
        journal_repository=journal_repo,
        session_manager=session_manager,
    )


def _select_user_repository(config: AppConfig) -> UserRepository:
    if config.supabase_url and config.supabase_service_role_key:
        return SupabaseRepository(
            base_url=config.supabase_url,
            service_role_key=config.supabase_service_role_key,
        )
    return _in_memory_repository


def _select_reading_repository(config: AppConfig) -> ReadingRepository:
    if config.supabase_url and config.supabase_service_role_key:
        return SupabaseReadingRepository(
            base_url=config.supabase_url,
            service_role_key=config.supabase_service_role_key,
        )
    return _in_memory_readings


def _select_journal_repository(config: AppConfig) -> JournalRepository:
    if config.supabase_url and config.supabase_service_role_key:
        return SupabaseJournalRepository(
            base_url=config.supabase_url,
            service_role_key=config.supabase_service_role_key,
        )
    return _in_memory_journal
