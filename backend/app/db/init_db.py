import base64
import hashlib
import logging
import secrets

from app.models.user import User, UserRole

logger = logging.getLogger("symbioai.db")


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16).encode()
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + derived).decode()


async def seed_database() -> None:
    admin = await User.find_one({"email": "admin@symbioai.com"})
    if not admin:
        await User(
            id="user-admin-production-id",
            email="admin@symbioai.com",
            full_name="Super Admin",
            hashed_password=_hash_password("Admin@123"),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        ).insert()
        logger.info("Default admin account created")
        return

    if admin.role != UserRole.SUPER_ADMIN:
        admin.role = UserRole.SUPER_ADMIN
        await admin.save()
        logger.info("Default admin role corrected")


async def init_db() -> None:
    try:
        await seed_database()
    except Exception as exc:
        logger.exception("Error seeding database: %s", str(exc))
