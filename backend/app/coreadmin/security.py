import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from ..config import settings

OTP_TTL_MINUTES = settings.CORE_ADMIN_OTP_TTL_MINUTES
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
HOURLY_REQUEST_CAP = 5
SESSION_TTL_HOURS = 12
SESSION_COOKIE_NAME = "coreadmin_session"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def generate_otp_code() -> str:
    """Cryptographically random 6-digit code (000000-999999, zero-padded)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp_code(code: str) -> str:
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()


def verify_otp_code(code: str, code_hash: str) -> bool:
    try:
        return bcrypt.checkpw(code.encode(), code_hash.encode())
    except ValueError:
        return False


class CoreAdminSecretNotConfigured(RuntimeError):
    pass


def issue_session_token(admin_id: str, email: str) -> str:
    if not settings.CORE_ADMIN_JWT_SECRET:
        raise CoreAdminSecretNotConfigured("CORE_ADMIN_JWT_SECRET is not set.")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": admin_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=SESSION_TTL_HOURS),
    }
    return jwt.encode(payload, settings.CORE_ADMIN_JWT_SECRET, algorithm="HS256")


def verify_session_token(token: str) -> Optional[dict]:
    if not settings.CORE_ADMIN_JWT_SECRET:
        return None
    try:
        return jwt.decode(token, settings.CORE_ADMIN_JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
