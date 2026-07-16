from sqlalchemy import Boolean, Column, String, Enum, DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "Super Admin"
    WASTE_PRODUCER = "Waste Producer"
    RAW_MATERIAL_CONSUMER = "Raw Material Consumer"
    ADMIN = "Admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.WASTE_PRODUCER)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    recovery_codes = Column(Text, nullable=True)
    trusted_device_token = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    factory_logo_url = Column(String, nullable=True)
    factory_verified = Column(Boolean, default=False)
    mobile_verified = Column(Boolean, default=False)
    phone_number = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
