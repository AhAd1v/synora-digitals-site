from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration comes from environment variables (.env locally, real
    env vars in production) — nothing here is hardcoded, since these values
    legitimately differ between dev and production (see README.md)."""

    RESEND_API_KEY: str
    RESEND_FROM: str = "Synora Digitals <onboarding@resend.dev>"
    RESEND_TO: str = "synoradigitals@gmail.com"
    ALLOWED_ORIGIN: str = "http://127.0.0.1:5500"

    class Config:
        env_file = ".env"


settings = Settings()
