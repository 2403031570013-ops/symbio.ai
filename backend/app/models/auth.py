from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class RefreshToken(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    token: Indexed(str, unique=True)
    expires_at: datetime
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "refresh_tokens"


class EmailOtp(Document):
    """A one-time email-verification challenge. Only an HMAC of the OTP is stored."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    email: Indexed(str)
    otp_hash: str
    expires_at: Indexed(datetime)
    used_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "email_otps"


class MobileOtp(Document):
    """A one-time mobile phone verification challenge. Only an HMAC of the OTP is stored."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    phone_number: Indexed(str)
    otp_hash: str
    expires_at: Indexed(datetime)
    used_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "mobile_otps"


def build_refresh_token_expiry(days: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)

