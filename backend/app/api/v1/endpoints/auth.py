import base64
import asyncio
import hashlib
import hmac
import io
import json
import logging
import secrets
from inspect import isawaitable
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from jose import jwt
import pyotp
import qrcode

from app.core.config import settings
from app.db.session import get_database
from app.models.auth import EmailOtp, MobileOtp, RefreshToken, build_refresh_token_expiry
from app.models.compliance_risk import AuditTrail
from app.models.user import User, UserRole
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.user import OtpRequest, OtpVerification, UserCreate, UserLogin, FactoryVerification, MobileOtpRequest, MobileOtpVerification
from app.core.security import get_current_user
from app.services.email_service import (
    EmailDeliveryError,
    EmailNotConfigured,
    send_email,
    send_password_reset_email,
    send_resend_verification_otp,
    send_verification_email,
    send_welcome_email,
)

try:  # google auth is optional until configured
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
    google_auth_available = True
except Exception as e:  # pragma: no cover
    google_id_token = None
    google_requests = None
    google_auth_available = False
    logger.warning(f"Google auth libraries not available: {e}. Google login will be disabled.")

router = APIRouter()
logger = logging.getLogger(__name__)
Session = Any


def get_db() -> None:
    return None


async def _run(coro):
    if isawaitable(coro):
        return await coro
    return coro


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16).encode()
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + derived).decode()


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        decoded = base64.b64decode(stored_hash.encode())
    except Exception:
        return False
    salt = decoded[:32]
    derived = decoded[32:]
    expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(expected, derived)


@router.get("/health-check")
async def health_check() -> dict:
    return {"success": True, "message": "ok"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return _verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return _hash_password(password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _public_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "email_verified": bool(getattr(user, "email_verified", False)),
        "two_factor_enabled": bool(getattr(user, "two_factor_enabled", False)),
    }


def _normalize_email(email: str) -> str:
    return str(email).strip().lower()


def _now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_utc_naive(value: datetime) -> datetime:
    """Normalize datetimes before comparing them."""
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value


def _otp_digest(otp: str) -> str:
    """Return a keyed digest so a database leak does not expose valid OTPs."""
    return hmac.new(settings.SECRET_KEY.encode(), otp.encode(), hashlib.sha256).hexdigest()


def _development_email_otp() -> str:
    return (settings.DEV_EMAIL_OTP or "654321").strip() or "654321"


def _development_mobile_otp() -> str:
    return (settings.DEV_MOBILE_OTP or "123456").strip() or "123456"


def _factory_verification_code() -> str:
    if settings.ENVIRONMENT.lower() != "production":
        return (settings.DEV_FACTORY_CODE or "123456").strip() or "123456"
    # In production, use the configured code or a default if not set
    return (settings.FACTORY_VERIFICATION_CODE or "SYMBIO2024").strip()


async def _issue_refresh_token(user: User) -> str:
    token = secrets.token_urlsafe(48)
    rt = RefreshToken(
        id=str(uuid4()),
        user_id=user.id,
        token=token,
        expires_at=build_refresh_token_expiry(settings.REFRESH_TOKEN_EXPIRE_DAYS).replace(tzinfo=None),
        revoked=False,
    )
    await rt.insert()
    return token


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    is_secure_cookie = settings.SECURE_COOKIES or settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="symbioai_refresh_token",
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=is_secure_cookie,
        samesite="none" if is_secure_cookie else "lax",
        path="/api/auth",
    )


# get_current_user is imported from app.core.security


@router.post("/register", response_model=SuccessResponse)
async def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)) -> Any:
    email = _normalize_email(user_in.email)
    existing = await User.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="Admin accounts must be provisioned through the secure admin bootstrap process")

    user = User(
        id=str(uuid4()),
        email=email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        email_verification_token=secrets.token_urlsafe(32),
        factory_verified=False,
        email_verified=False,
        mobile_verified=False,
    )
    await user.insert()
    logger.info("Registered user %s", user.email)
    try:
        send_welcome_email(user.email, user.full_name)
    except EmailNotConfigured:
        logger.info("SMTP not configured; skipped welcome email for %s", user.email)

    token = create_access_token(user.email)
    refresh_token = await _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)

    return {
        "success": True,
        "message": "Account created. Please verify your factory.",
        "data": {"user_id": user.id, "email": user.email, "token": token, "user": _public_user(user)},
    }


async def _send_otp_for_email(email: str) -> Any:
    """Issue a rate-limited, five-minute verification OTP through Resend."""
    email = str(email).strip().lower()
    user = await User.find_one({"email": email})
    if not user:
        # Do not turn this endpoint into an account-enumeration oracle.
        return {"success": True, "message": "If the account exists, a verification code has been sent.", "data": {"cooldown_seconds": 60}}
    if user.email_verified:
        return {"success": True, "message": "Email is already verified.", "data": {"verified": True}}

    now = _now_utc_naive()
    latest = await EmailOtp.find({"email": email}).sort("-created_at").first_or_none()
    latest_created_at = _as_utc_naive(latest.created_at) if latest and latest.created_at else None
    if latest_created_at and (now - latest_created_at).total_seconds() < 60:
        remaining = max(1, 60 - int((now - latest_created_at).total_seconds()))
        raise HTTPException(status_code=429, detail=f"Please wait {remaining} seconds before requesting another code")

    request_count = await EmailOtp.find({"email": email, "created_at": {"$gte": now - timedelta(hours=1)}}).count()
    if request_count >= 5:
        raise HTTPException(status_code=429, detail="Verification request limit reached. Try again in one hour.")

    otp = _development_email_otp() if settings.ENVIRONMENT.lower() != "production" else f"{secrets.randbelow(1_000_000):06d}"
    challenge = EmailOtp(
        id=str(uuid4()),
        email=email,
        otp_hash=_otp_digest(otp),
        expires_at=now + timedelta(minutes=5),
    )
    await challenge.insert()
    
    # Only try to send email in production if configured
    if settings.ENVIRONMENT.lower() == "production":
        try:
            if settings.OTP_PROVIDER.lower() == "resend" and settings.RESEND_API_KEY:
                send_resend_verification_otp(email, otp)
            elif settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                # Fallback to SMTP if configured
                from app.services.email_service import send_email
                send_email(email, "SymbioAI Email Verification", f"Your verification code is: {otp}")
            else:
                # Email not configured but still allow verification with the generated OTP
                logger.warning("Email provider not configured in production. OTP generated but not sent: %s", email)
        except EmailNotConfigured:
            logger.warning("Email provider not configured. OTP generated but not sent: %s", email)
        except EmailDeliveryError as e:
            logger.error("Failed to send email OTP: %s", e)
            # Continue anyway - the OTP is still valid
        except Exception as e:
            logger.exception("Unexpected error while sending email OTP: %s", e)
            # Continue anyway - the OTP is still valid

    logger.info("Verification OTP issued for %s", email)
    
    # In development or if email not configured, include the OTP in response for testing
    dev_mode = settings.ENVIRONMENT.lower() != "production"
    email_configured = settings.RESEND_API_KEY or (settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    response_data = {"cooldown_seconds": 60, "expires_in_seconds": 300}
    if dev_mode or not email_configured:
        response_data["dev_otp"] = otp
        message = f"Verification code: {otp} (Development mode - code shown for testing)"
    else:
        message = "Verification code sent. It expires in 5 minutes."
    
    return {"success": True, "message": message, "data": response_data}


@router.get("/send-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
async def send_otp_get(email: str = Query(...), db: Session = Depends(get_db)) -> Any:
    return await _send_otp_for_email(email)


@router.post("/send-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
async def send_otp(payload: OtpRequest, db: Session = Depends(get_db)) -> Any:
    return await _send_otp_for_email(payload.email)


@router.post("/verify-otp", response_model=SuccessResponse)
async def verify_otp(payload: OtpVerification, db: Session = Depends(get_db)) -> Any:
    """Validate an unused OTP and mark the associated account email as verified."""
    email = str(payload.email).strip().lower()
    otp = payload.otp.strip()
    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    dev_otp = _development_email_otp()
    if settings.ENVIRONMENT.lower() != "production" and hmac.compare_digest(otp, dev_otp):
        user = await User.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        if user.email_verified:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        user.email_verified = True
        user.email_verification_token = None
        await user.save()
        return {"success": True, "message": "Email verified successfully.", "data": {"verified": True}}

    now = _now_utc_naive()
    challenge = await EmailOtp.find({"email": email, "used_at": None}).sort("-created_at").first_or_none()
    if not challenge or _as_utc_naive(challenge.expires_at) <= now:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if not hmac.compare_digest(challenge.otp_hash, _otp_digest(otp)):
        logger.warning("Invalid email OTP submitted for %s", email)
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = await User.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    challenge.used_at = now
    user.email_verified = True
    user.email_verification_token = None
    await challenge.save()
    await user.save()
    logger.info("Email verified with OTP for %s", email)
    return {"success": True, "message": "Email verified successfully.", "data": {"verified": True}}


@router.post("/verify-factory", response_model=SuccessResponse)
async def verify_factory(payload: FactoryVerification, db: Session = Depends(get_db)) -> Any:
    """Verify factory using the configured factory verification code."""
    factory_code = str(payload.factory_code).strip()
    expected_code = _factory_verification_code()

    if factory_code != expected_code:
        raise HTTPException(status_code=400, detail="Invalid factory code")

    logger.info("Factory verified with code %s", factory_code)
    return {"success": True, "message": "Factory verified successfully.", "data": {"factory_verified": True}}


async def _send_mobile_otp_for_user(user_id: str, phone_number: str) -> Any:
    """Issue a rate-limited mobile phone verification OTP."""
    user = await User.find_one({"_id": user_id})
    if not user:
        return {"success": True, "message": "If the account exists, a verification code has been sent.", "data": {"cooldown_seconds": 60}}
    
    phone_number = str(phone_number).strip()
    if not phone_number or len(phone_number) < 10:
        raise HTTPException(status_code=400, detail="Valid phone number is required")
    
    if user.mobile_verified:
        return {"success": True, "message": "Phone is already verified.", "data": {"verified": True}}
    
    now = _now_utc_naive()
    latest = await MobileOtp.find({"user_id": user_id, "phone_number": phone_number}).sort("-created_at").first_or_none()
    latest_created_at = _as_utc_naive(latest.created_at) if latest and latest.created_at else None
    if latest_created_at and (now - latest_created_at).total_seconds() < 60:
        remaining = max(1, 60 - int((now - latest_created_at).total_seconds()))
        raise HTTPException(status_code=429, detail=f"Please wait {remaining} seconds before requesting another code")
    
    request_count = await MobileOtp.find({"user_id": user_id, "created_at": {"$gte": now - timedelta(hours=1)}}).count()
    if request_count >= 5:
        raise HTTPException(status_code=429, detail="Verification request limit reached. Try again in one hour.")
    
    otp = _development_mobile_otp() if settings.ENVIRONMENT.lower() != "production" else f"{secrets.randbelow(1_000_000):06d}"
    mobile_challenge = MobileOtp(
        id=str(uuid4()),
        user_id=user_id,
        phone_number=phone_number,
        otp_hash=_otp_digest(otp),
        expires_at=now + timedelta(minutes=5),
    )
    await mobile_challenge.insert()
    
    # Development uses deterministic OTPs; production should plug in an SMS provider.
    # For now, we'll use the same approach as email OTP - allow testing without SMS
    
    user.phone_number = phone_number
    await user.save()
    
    # In development, include the OTP in response for testing
    dev_mode = settings.ENVIRONMENT.lower() != "production"
    response_data = {"cooldown_seconds": 60, "expires_in_seconds": 300}
    if dev_mode:
        response_data["dev_otp"] = otp
        message = f"Verification code: {otp} (Development mode - code shown for testing)"
    else:
        message = "Verification code sent. It expires in 5 minutes."
    
    return {"success": True, "message": message, "data": response_data}


@router.get("/send-mobile-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
async def send_mobile_otp_get(user_id: str = Query(...), phone_number: str = Query(...), db: Session = Depends(get_db)) -> Any:
    return await _send_mobile_otp_for_user(user_id, phone_number)


@router.post("/send-mobile-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
async def send_mobile_otp(payload: MobileOtpRequest, db: Session = Depends(get_db)) -> Any:
    return await _send_mobile_otp_for_user(payload.user_id, payload.phone_number)


@router.post("/verify-mobile", response_model=SuccessResponse)
async def verify_mobile(payload: MobileOtpVerification, db: Session = Depends(get_db)) -> Any:
    """Validate mobile OTP and mark the phone as verified."""
    otp = payload.otp.strip()
    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    dev_otp = _development_mobile_otp()
    if settings.ENVIRONMENT.lower() != "production" and hmac.compare_digest(otp, dev_otp):
        user = await User.find_one({"_id": payload.user_id})
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        if user.mobile_verified:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        user.mobile_verified = True
        await user.save()
        return {"success": True, "message": "Mobile verified successfully.", "data": {"verified": True}}
    
    user = await User.find_one({"_id": payload.user_id})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    now = _now_utc_naive()
    challenge = await MobileOtp.find({"user_id": payload.user_id, "used_at": None}).sort("-created_at").first_or_none()
    
    if not challenge or _as_utc_naive(challenge.expires_at) <= now:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    if not hmac.compare_digest(challenge.otp_hash, _otp_digest(otp)):
        logger.warning("Invalid mobile OTP submitted for user %s", payload.user_id)
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    challenge.used_at = now
    user.mobile_verified = True
    await challenge.save()
    await user.save()
    
    logger.info("Mobile verified with OTP for user %s", payload.user_id)
    return {"success": True, "message": "Mobile verified successfully.", "data": {"verified": True}}


@router.post("/login", response_model=SuccessResponse)
async def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)) -> Any:
    email = _normalize_email(user_in.email)
    user = await User.find_one({"email": email})
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.email)
    refresh_token = await _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    logger.info("Authenticated user %s", user.email)
    return {
        "success": True,
        "message": "Operation successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/admin-login", response_model=SuccessResponse)
async def admin_login(user_in: UserLogin, response: Response, request: Request = None, db: Session = Depends(get_db)) -> Any:
    email = _normalize_email(user_in.email)
    user = await User.find_one({"email": email})
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    if user.role not in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="Admin access required")

    if user.two_factor_enabled and not user_in.model_extra:
        raise HTTPException(status_code=202, detail={"two_factor_required": True, "email": user.email})

    token = create_access_token(user.email)
    refresh_token = await _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    await AuditTrail(
        id=str(uuid4()),
        entity_type="admin_session",
        entity_id=user.id,
        action="admin_login",
        user_id=user.id,
        user_role=user.role.value,
        ip_address=request.client.host if request and request.client else None,
        changes={},
    ).insert()
    logger.info("Authenticated admin %s", user.email)
    return {
        "success": True,
        "message": "Admin sign-in successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/google", response_model=SuccessResponse)
async def google_login(payload: dict, response: Response, db: Session = Depends(get_db)) -> Any:
    credential: str = (payload.get("credential") or "").strip()
    email: Optional[str] = None
    full_name: Optional[str] = None

    if credential:
        if not google_auth_available:
            raise HTTPException(status_code=500, detail="Google login is not fully configured on the server. Please contact administrator.")
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google client ID is not configured on the server. Please set GOOGLE_CLIENT_ID environment variable.")
        if not settings.GOOGLE_CLIENT_SECRET:
            logger.warning("GOOGLE_CLIENT_SECRET not configured - Google login may have limited functionality")
        try:
            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception as e:
            logger.error(f"Google token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid Google token")

        email = (idinfo.get("email") or "").strip().lower() or None
        full_name = (idinfo.get("name") or idinfo.get("given_name") or idinfo.get("family_name") or "").strip() or None

    if not email:
        raise HTTPException(status_code=400, detail="A valid Google credential is required")

    user = await User.find_one({"email": email})
    if user and full_name and user.full_name != full_name:
        user.full_name = full_name
        await user.save()
    if not user:
        user = User(
            id=str(uuid4()),
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(secrets.token_urlsafe(24)),
            role=UserRole.RAW_MATERIAL_CONSUMER,
        )
        await user.insert()

    token = create_access_token(user.email)
    refresh_token = await _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    logger.info("Authenticated Google user %s", user.email)
    return {
        "success": True,
        "message": "Google sign-in successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(payload: dict) -> Any:
    email = _normalize_email(payload.get("email") or "")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = await User.find_one({"email": email})
    if user:
        user.password_reset_token = secrets.token_urlsafe(32)
        await user.save()
        try:
            send_password_reset_email(user.email, user.password_reset_token)
        except EmailNotConfigured:
            logger.info("SMTP not configured; password reset token generated for %s", email)
    logger.info("Password reset requested for %s", email)
    return {"success": True, "message": "If that email exists, reset instructions have been queued.", "data": {"email": email}}


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(payload: dict, db: Session = Depends(get_db)) -> Any:
    token = (payload.get("token") or "").strip()
    password = (payload.get("password") or "").strip()
    if not token or len(password) < 8:
        raise HTTPException(status_code=400, detail="Valid reset token and password are required")
    user = await User.find_one({"password_reset_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.hashed_password = get_password_hash(password)
    user.password_reset_token = None
    await user.save()
    return {"success": True, "message": "Password reset successful", "data": {}}


@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(payload: dict) -> Any:
    token = (payload.get("token") or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Verification token is required")
    user = await User.find_one({"email_verification_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.email_verified = True
    user.email_verification_token = None
    await user.save()
    return {"success": True, "message": "Email verified", "data": {"verified": True}}


@router.post("/admin-secret/verify", response_model=SuccessResponse)
async def verify_admin_secret(payload: dict) -> Any:
    if settings.ENVIRONMENT.lower() == "production":
        raise HTTPException(status_code=403, detail="Access denied")
    expected_secret = (settings.ADMIN_DEV_SECRET or "").strip()
    submitted_secret = str(payload.get("secret") or "").strip()
    if not expected_secret or not hmac.compare_digest(submitted_secret, expected_secret):
        raise HTTPException(status_code=403, detail="Access denied")
    return {"success": True, "message": "Admin secret verified", "data": {"verified": True}}

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="symbioai_refresh_token"),
    db: Session = Depends(get_db),
) -> Any:
    is_secure_cookie = settings.SECURE_COOKIES or settings.ENVIRONMENT.lower() == "production"
    if refresh_token:
        token_obj = await RefreshToken.find_one({"token": refresh_token, "revoked": False})
        if token_obj:
            token_obj.revoked = True
            await token_obj.save()
    response.delete_cookie(
        "symbioai_refresh_token",
        path="/api/auth",
        secure=is_secure_cookie,
        samesite="none" if is_secure_cookie else "lax",
    )
    return {"success": True, "message": "Operation successful", "data": {}}


@router.get("/me", response_model=SuccessResponse)
async def me(current_user: User = Depends(get_current_user)) -> Any:
    return {"success": True, "message": "Operation successful", "data": {"user": _public_user(current_user)}}


@router.post("/refresh", response_model=SuccessResponse, responses={401: {"model": ErrorResponse}})
async def refresh_access_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="symbioai_refresh_token"),
    db: Session = Depends(get_db),
) -> Any:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_obj = await RefreshToken.find_one({"token": refresh_token, "revoked": False})
    if not token_obj or token_obj.expires_at <= _now_utc_naive():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    user = await User.find_one({"_id": token_obj.user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    token_obj.revoked = True
    await token_obj.save()
    new_refresh = await _issue_refresh_token(user)
    _set_refresh_cookie(response, new_refresh)

    new_access = create_access_token(user.email)
    return {"success": True, "message": "Token refreshed", "data": {"token": new_access}}


@router.post("/2fa/setup", response_model=SuccessResponse)
async def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = await User.find_one({"_id": current_user.id})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()
    db_user.two_factor_secret = secret
    await db_user.save()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=db_user.email, issuer_name="SymbioAI")
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return {"success": True, "message": "2FA setup created", "data": {"secret": secret, "otpauth_url": uri, "qr_code": qr_data_url}}


@router.post("/2fa/enable", response_model=SuccessResponse)
async def enable_2fa(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = await User.find_one({"_id": current_user.id})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    code = (payload.get("code") or "").strip()
    if not db_user.two_factor_secret or not pyotp.TOTP(db_user.two_factor_secret).verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    recovery_codes = [secrets.token_hex(4) for _ in range(8)]
    db_user.two_factor_enabled = True
    db_user.recovery_codes = json.dumps(recovery_codes)
    await db_user.save()
    return {"success": True, "message": "2FA enabled", "data": {"recovery_codes": recovery_codes}}


@router.post("/2fa/verify-login", response_model=SuccessResponse)
async def verify_2fa_login(payload: dict, response: Response, db: Session = Depends(get_db)) -> Any:
    email = (payload.get("email") or "").strip()
    code = (payload.get("code") or "").strip()
    user = await User.find_one({"email": email})
    if not user or not user.two_factor_secret:
        raise HTTPException(status_code=401, detail="Invalid 2FA request")
    recovery_codes = json.loads(user.recovery_codes or "[]")
    valid_recovery = code in recovery_codes
    valid_totp = pyotp.TOTP(user.two_factor_secret).verify(code, valid_window=1)
    if not (valid_totp or valid_recovery):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    if valid_recovery:
        recovery_codes.remove(code)
        user.recovery_codes = json.dumps(recovery_codes)
        await user.save()
    token = create_access_token(user.email)
    refresh_token = await _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    return {"success": True, "message": "2FA verified", "data": {"token": token, "user": _public_user(user)}}


@router.post("/2fa/disable", response_model=SuccessResponse)
async def disable_2fa(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = await User.find_one({"_id": current_user.id})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    code = (payload.get("code") or "").strip()
    if db_user.two_factor_secret and not pyotp.TOTP(db_user.two_factor_secret).verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    db_user.two_factor_enabled = False
    db_user.two_factor_secret = None
    db_user.recovery_codes = None
    db_user.trusted_device_token = None
    await db_user.save()
    return {"success": True, "message": "2FA disabled", "data": {}}
