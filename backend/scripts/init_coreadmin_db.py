"""One-time setup script: creates the coreadmin tables and seeds the first
core admin account. Run once after DATABASE_URL is set:

    cd backend
    python -m scripts.init_coreadmin_db

Reads SEED_COREADMIN_EMAIL / SEED_COREADMIN_PASSWORD from the environment
(falls back to the printed defaults below for local dev only — always set
real values via env vars before running this against production). Safe to
re-run: table creation is idempotent (CREATE TABLE IF NOT EXISTS under the
hood) and the admin upsert won't overwrite an existing password.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select  # noqa: E402

from app.coreadmin.db import _engine, _SessionLocal, Base  # noqa: E402
from app.coreadmin.models import CoreAdmin  # noqa: E402
from app.coreadmin.security import hash_password  # noqa: E402


async def main() -> None:
    if _engine is None:
        print("DATABASE_URL is not set — nothing to do. Set it in backend/.env first.")
        return

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ensured: core_admin, core_admin_otp, core_admin_audit_log")

    email = os.environ.get("SEED_COREADMIN_EMAIL", "admin@synoradigitals.com").strip().lower()
    password = os.environ.get("SEED_COREADMIN_PASSWORD", "ChangeMe123!")

    async with _SessionLocal() as session:
        result = await session.execute(select(CoreAdmin).where(CoreAdmin.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Core admin already exists: {email} (password unchanged)")
            return

        session.add(
            CoreAdmin(name="Synora Core Admin", email=email, password_hash=hash_password(password))
        )
        await session.commit()
        print(f"Core admin created: {email} / {password}")
        print("Log in at /coreadmin, then change this password immediately if you used the default.")


if __name__ == "__main__":
    asyncio.run(main())
