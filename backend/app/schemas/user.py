from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[UserRole] = UserRole.WASTE_PRODUCER


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OtpRequest(BaseModel):
    email: EmailStr


class OtpVerification(OtpRequest):
    otp: str


class FactoryVerification(BaseModel):
    factory_code: str


class MobileOtpRequest(BaseModel):
    user_id: str
    phone_number: str


class MobileOtpVerification(BaseModel):
    user_id: str
    otp: str


class UserOut(UserBase):
    id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
