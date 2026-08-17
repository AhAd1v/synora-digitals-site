import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CoreAdmin(Base):
    """A company official with access to synoradigitals.com/coreadmin. Deliberately
    a single flat table for now (one seeded account) — the role-hierarchy split
    (owner vs. support, scoped visibility) flagged in the design review is real future
    work, not something to guess the shape of before there's an actual second admin."""

    __tablename__ = "core_admin"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    # A session JWT is stateless by design (no server-side session table to check on
    # every request) — but that alone means logout can only ever ask the browser to
    # forget the cookie, not actually invalidate it: a token captured before logout
    # would stay valid until its natural expiry regardless. This column closes that
    # gap cheaply: logout bumps it to now(), and any token issued (iat) before this
    # timestamp is rejected even if its signature and expiry are still otherwise valid.
    session_valid_after: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    otps: Mapped[list["CoreAdminOtp"]] = relationship(
        back_populates="admin", cascade="all, delete-orphan"
    )


class CoreAdminOtp(Base):
    """One row per issued login code. A fresh row is created each time a code is
    (re)sent; old unconsumed rows are left to expire naturally — authorize-equivalent
    logic only ever trusts the most recent unconsumed, unexpired row and enforces the
    attempt cap per row, so a stale row can't be replayed."""

    __tablename__ = "core_admin_otp"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    admin_id: Mapped[str] = mapped_column(
        ForeignKey("core_admin.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    admin: Mapped["CoreAdmin"] = relationship(back_populates="otps")


class CoreAdminAuditLog(Base):
    """Every auth-relevant event, so 'who at Synora accessed what, when' is always
    answerable. Direct fix for the missing-audit-trail flaw in the original design:
    core admin has visibility into every client's data, so that visibility needs to
    be accountable. admin_id is nullable + SET NULL on delete so a log entry survives
    even if the admin account is later removed."""

    __tablename__ = "core_admin_audit_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    admin_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("core_admin.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
