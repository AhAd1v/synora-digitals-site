from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..email_service import UpstreamError, send_coreadmin_otp_email
from ..rate_limit import client_ip_key, limiter
from .db import Base, get_session, _engine
from .models import CoreAdmin, CoreAdminAuditLog, CoreAdminOtp
from .security import (
    HOURLY_REQUEST_CAP,
    OTP_MAX_ATTEMPTS,
    OTP_RESEND_COOLDOWN_SECONDS,
    OTP_TTL_MINUTES,
    SESSION_COOKIE_NAME,
    SESSION_TTL_HOURS,
    CoreAdminSecretNotConfigured,
    generate_otp_code,
    hash_otp_code,
    hash_password,
    issue_session_token,
    verify_otp_code,
    verify_password,
    verify_session_token,
)

router = APIRouter(prefix="/api/coreadmin", tags=["coreadmin"])


@router.post("/setup")
async def setup(request: Request, session: AsyncSession = Depends(get_session)):
    """TEMPORARY, ONE-TIME USE — creates the coreadmin tables and seeds the first
    admin account, run once against the live DATABASE_URL right after it's
    provisioned. Token-gated via CORE_ADMIN_SETUP_TOKEN. Delete this route (and
    unset that env var) once used — do not leave a standing table-creation/seed
    endpoint in the deployed app."""
    token = request.headers.get("x-setup-token")
    if not settings.CORE_ADMIN_SETUP_TOKEN or token != settings.CORE_ADMIN_SETUP_TOKEN:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    if _engine is None:
        return JSONResponse({"error": "not_configured"}, status_code=503)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    body = await request.json()
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    name = str(body.get("name", "Core Admin"))
    if not email or not password:
        return JSONResponse({"ok": True, "tablesCreated": True, "adminSeeded": False})

    result = await session.execute(select(CoreAdmin).where(CoreAdmin.email == email))
    existing = result.scalar_one_or_none()
    seeded = False
    if not existing:
        session.add(CoreAdmin(name=name, email=email, password_hash=hash_password(password)))
        await session.commit()
        seeded = True

    return JSONResponse({"ok": True, "tablesCreated": True, "adminSeeded": seeded, "email": email})


def _aware(dt: datetime) -> datetime:
    """Some DB drivers (confirmed with SQLite/aiosqlite in tests; Postgres/asyncpg
    should round-trip DateTime(timezone=True) as aware, but this guards against any
    driver/config that doesn't) hand back naive datetimes even for a
    DateTime(timezone=True) column. Subtracting an aware `now()` from a naive value
    raises TypeError — normalize defensively rather than trust the round-trip."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _generic_response() -> JSONResponse:
    # Identical response on every path (unknown email, wrong password, rate-limited,
    # cooldown hit) — this endpoint must never act as an oracle for enumerating core
    # admin emails or brute-forcing passwords. Only a genuinely correct email+password
    # ever results in an email actually being sent. Timing differences between paths
    # are a known, accepted limitation (unavoidable without constant-time DB round
    # trips) — same trade-off documented in blackbuc's request-otp route.
    return JSONResponse(
        {"ok": True, "message": "If that account exists, a verification code has been sent."}
    )


async def _log(session: AsyncSession, admin_id: Optional[str], action: str, request: Request) -> None:
    session.add(CoreAdminAuditLog(admin_id=admin_id, action=action, ip=client_ip_key(request)))
    await session.commit()


@router.post("/login")
@limiter.limit("20/hour")  # coarse per-IP belt-and-suspenders; the real cap is per-account, DB-backed below
async def login(request: Request, session: AsyncSession = Depends(get_session)):
    body = await request.json()
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    if not email or not password:
        return _generic_response()

    result = await session.execute(select(CoreAdmin).where(CoreAdmin.email == email))
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(password, admin.password_hash):
        return _generic_response()

    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    count_result = await session.execute(
        select(func.count())
        .select_from(CoreAdminOtp)
        .where(CoreAdminOtp.admin_id == admin.id, CoreAdminOtp.created_at > hour_ago)
    )
    if count_result.scalar_one() >= HOURLY_REQUEST_CAP:
        return _generic_response()

    latest_result = await session.execute(
        select(CoreAdminOtp)
        .where(CoreAdminOtp.admin_id == admin.id)
        .order_by(CoreAdminOtp.created_at.desc())
        .limit(1)
    )
    latest = latest_result.scalar_one_or_none()
    if latest and (datetime.now(timezone.utc) - _aware(latest.created_at)).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
        return _generic_response()

    code = generate_otp_code()
    session.add(
        CoreAdminOtp(
            admin_id=admin.id,
            code_hash=hash_otp_code(code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
        )
    )
    await session.commit()

    try:
        await send_coreadmin_otp_email(admin.email, code)
    except UpstreamError:
        pass  # never leak delivery-failure state to the client — same reasoning as above

    return _generic_response()


@router.post("/verify-otp")
async def verify_otp(request: Request, session: AsyncSession = Depends(get_session)):
    body = await request.json()
    email = str(body.get("email", "")).strip().lower()
    code = str(body.get("otp", "")).strip()
    invalid = JSONResponse({"ok": False, "error": "invalid_code"}, status_code=401)
    if not email or not code:
        return invalid

    result = await session.execute(select(CoreAdmin).where(CoreAdmin.email == email))
    admin = result.scalar_one_or_none()
    if not admin:
        return invalid

    otp_result = await session.execute(
        select(CoreAdminOtp)
        .where(
            CoreAdminOtp.admin_id == admin.id,
            CoreAdminOtp.consumed_at.is_(None),
            CoreAdminOtp.expires_at > datetime.now(timezone.utc),
        )
        .order_by(CoreAdminOtp.created_at.desc())
        .limit(1)
    )
    record = otp_result.scalar_one_or_none()
    if not record or record.attempts >= OTP_MAX_ATTEMPTS:
        return invalid

    if not verify_otp_code(code, record.code_hash):
        record.attempts += 1
        await session.commit()
        return invalid

    # One-time use — a consumed row can never authorize a second session.
    record.consumed_at = datetime.now(timezone.utc)
    await session.commit()
    await _log(session, admin.id, "login", request)

    try:
        token = issue_session_token(admin.id, admin.email)
    except CoreAdminSecretNotConfigured:
        return JSONResponse({"ok": False, "error": "not_configured"}, status_code=503)

    resp = JSONResponse({"ok": True, "name": admin.name, "email": admin.email})
    resp.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=SESSION_TTL_HOURS * 3600,
        path="/",
    )
    return resp


async def _current_admin(session: AsyncSession, token: Optional[str]) -> Optional[CoreAdmin]:
    if not token:
        return None
    payload = verify_session_token(token)
    if not payload:
        return None
    result = await session.execute(select(CoreAdmin).where(CoreAdmin.id == payload["sub"]))
    admin = result.scalar_one_or_none()
    if not admin:
        return None
    # Reject any token issued before the admin's last logout (or a future
    # "revoke all sessions" action) — see the column's docstring in models.py.
    if admin.session_valid_after is not None:
        issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        if issued_at < _aware(admin.session_valid_after):
            return None
    return admin


@router.get("/me")
async def me(
    session: AsyncSession = Depends(get_session),
    coreadmin_session: Optional[str] = Cookie(default=None),
):
    admin = await _current_admin(session, coreadmin_session)
    if not admin:
        return JSONResponse({"ok": False}, status_code=401)
    return {"ok": True, "name": admin.name, "email": admin.email}


@router.post("/logout")
async def logout(
    request: Request,
    session: AsyncSession = Depends(get_session),
    coreadmin_session: Optional[str] = Cookie(default=None),
):
    admin = await _current_admin(session, coreadmin_session)
    if admin:
        # Actually invalidates the token server-side (see session_valid_after's
        # docstring) — not just clearing the cookie, which a captured token would
        # ignore entirely.
        admin.session_valid_after = datetime.now(timezone.utc)
        await session.commit()
        await _log(session, admin.id, "logout", request)
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return resp
