from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


class SessionManager:
    def __init__(self, secret: str, max_age_seconds: int) -> None:
        self._serializer = URLSafeTimedSerializer(secret_key=secret)
        self._max_age_seconds = max_age_seconds

    def issue_token(self, user_id: str, email: str) -> tuple[str, str, datetime]:
        session_id = str(uuid4())
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "email": email,
        }
        token = self._serializer.dumps(payload)
        expires_at = self.get_expiry_from_now()
        return token, session_id, expires_at

    def get_expiry_from_now(self) -> datetime:
        expires_at_ts = datetime.now(tz=timezone.utc).timestamp() + self._max_age_seconds
        return datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)

    def validate_token(self, token: str) -> dict[str, str]:
        try:
            payload = self._serializer.loads(token, max_age=self._max_age_seconds)
        except SignatureExpired as error:
            raise ValueError("Session expired") from error
        except BadSignature as error:
            raise ValueError("Invalid session token") from error

        required_keys = {"session_id", "user_id", "email"}
        if not required_keys.issubset(payload.keys()):
            raise ValueError("Invalid session payload")
        return payload
