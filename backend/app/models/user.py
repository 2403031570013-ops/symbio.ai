from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import Field


class UserRole(str, Enum):
    SUPER_ADMIN = "Super Admin"
    WASTE_PRODUCER = "Waste Producer"
    RAW_MATERIAL_CONSUMER = "Raw Material Consumer"
    ADMIN = "Admin"


class User(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")

    # Indexed field
    email: str = Indexed(unique=True)

    hashed_password: str
    full_name: str

    role: UserRole = Field(default=UserRole.WASTE_PRODUCER)

    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)

    email_verification_token: Optional[str] = Field(default=None)
    password_reset_token: Optional[str] = Field(default=None)

    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: Optional[str] = Field(default=None)
    recovery_codes: Optional[str] = Field(default=None)
    trusted_device_token: Optional[str] = Field(default=None)

    profile_image_url: Optional[str] = Field(default=None)
    factory_logo_url: Optional[str] = Field(default=None)

    factory_verified: bool = Field(default=False)
    mobile_verified: bool = Field(default=False)

    # Removed incompatible Indexed(Optional[str])
    phone_number: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "users"