import asyncio
from uuid import uuid4

from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _run(coro):
    return asyncio.run(coro)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_user(db, *, email: str, full_name: str, password: str, role: str) -> User:
    user = User(
        id=str(uuid4()),
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
    )
    _run(user.insert())
    return user
