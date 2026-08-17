from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration comes from environment variables (.env locally, real
    env vars in production) — nothing here is hardcoded, since these values
    legitimately differ between dev and production (see README.md)."""

    RESEND_API_KEY: str
    RESEND_FROM: str = "Synora Digitals <onboarding@resend.dev>"
    RESEND_TO: str = "synoradigitals@gmail.com"
    ALLOWED_ORIGIN: str = "http://127.0.0.1:5500"

    # --- Core admin (synoradigitals.com/coreadmin) ---
    # Left optional (empty-string default) rather than required: this file is
    # instantiated eagerly at import time, so making these required would crash
    # the whole app — including the already-working /api/consult endpoint — on
    # any deployment that hasn't set them yet. The coreadmin router itself checks
    # for these and returns a clean 503 instead of ever touching an unset value.
    DATABASE_URL: str = ""
    CORE_ADMIN_JWT_SECRET: str = ""
    CORE_ADMIN_OTP_TTL_MINUTES: int = 10
    # One-time DB bootstrap (create tables + seed first admin) — see the /setup
    # route's docstring. Empty by default so the route 401s unless explicitly
    # configured; meant to be unset again once used.
    CORE_ADMIN_SETUP_TOKEN: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
