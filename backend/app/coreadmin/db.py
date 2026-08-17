from urllib.parse import urlsplit, urlunsplit, parse_qsl

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase

from ..config import settings


class Base(DeclarativeBase):
    pass


class CoreAdminNotConfigured(RuntimeError):
    """Raised instead of letting an unset DATABASE_URL blow up at import time —
    see config.py for why these settings have empty-string defaults."""


def _prepare_db_url(raw_url: str) -> tuple[str, dict]:
    """Neon (and most managed Postgres hosts) hand out a psycopg-style connection
    string with query params like `sslmode=require` and `channel_binding=require`.
    asyncpg needs the +asyncpg dialect prefix and doesn't accept psycopg-style query
    params the same way — SQLAlchemy's asyncpg dialect passes any unrecognized query
    param straight through as a kwarg to asyncpg.connect(), which raises TypeError on
    anything it doesn't know (confirmed in practice: `channel_binding` crashed this
    exact way). Strip the whole query string and express SSL via connect_args instead,
    so a Neon URL pasted in as-is just works without hand-editing — and without this
    breaking again the next time Neon adds another libpq-style param we don't know to
    allowlist."""
    url = raw_url
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    elif url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    ssl_mode = query.get("sslmode")
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", parts.fragment))

    # Default to requiring SSL even if sslmode was absent — Neon (and any managed
    # Postgres worth using) always requires it; failing closed is the safer default.
    connect_args = {} if ssl_mode == "disable" else {"ssl": "require"}
    return url, connect_args


if settings.DATABASE_URL:
    _url, _connect_args = _prepare_db_url(settings.DATABASE_URL)
    # NullPool: a Vercel serverless invocation may run in a fresh container with no
    # warm connections to reuse, and Neon's own pooler (use Neon's *pooled* connection
    # string) already does real cross-invocation pooling upstream — pooling again
    # in-process here would just risk holding connections open past their invocation.
    _engine = create_async_engine(_url, poolclass=NullPool, connect_args=_connect_args)
    _SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)
else:
    _engine = None
    _SessionLocal = None


async def get_session():
    if _SessionLocal is None:
        raise CoreAdminNotConfigured(
            "DATABASE_URL is not set — core admin is not configured on this deployment."
        )
    async with _SessionLocal() as session:
        yield session
