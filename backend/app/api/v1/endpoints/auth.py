import base64
import asyncio
import hashlib
import hmac
import io
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
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
    send_password_reset_email,
    send_resend_verification_otp,
    send_verification_email,
    send_welcome_email,
)

try:  # google auth is optional until configured
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
except Exception:  # pragma: no cover
    google_id_token = None
    google_requests = None

router = APIRouter()
logger = logging.getLogger(__name__)
Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


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
def health_check() -> dict:
    return {"success": True, "message": "ok"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
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


def _now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_utc_naive(value: datetime) -> datetime:
    """Normalize datetimes before comparing them."""
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value


def _otp_digest(otp: str) -> str:
    """Return a keyed digest so a database leak does not expose valid OTPs."""
    return hmac.new(settings.SECRET_KEY.encode(), otp.encode(), hashlib.sha256).hexdigest()


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
def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)) -> Any:
    existing = _run(User.find_one(User.email == user_in.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="Admin accounts must be provisioned through the secure admin bootstrap process")

    user = User(
        id=str(uuid4()),
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        email_verification_token=secrets.token_urlsafe(32),
        factory_verified=False,
        email_verified=False,
        mobile_verified=False,
    )
    _run(user.insert())
    logger.info("Registered user %s", user.email)
    try:
        send_welcome_email(user.email, user.full_name)
    except EmailNotConfigured:
        logger.info("SMTP not configured; skipped welcome email for %s", user.email)

    return {
        "success": True,
        "message": "Account created. Please verify your factory.",
        "data": {"user_id": user.id, "email": user.email},
    }


@router.post("/send-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
def send_otp(payload: OtpRequest, db: Session = Depends(get_db)) -> Any:
    """Issue a rate-limited, five-minute verification OTP through Resend."""
    email = str(payload.email).strip().lower()
    user = _run(User.find_one(User.email == email))
    if not user:
        # Do not turn this endpoint into an account-enumeration oracle.
        return {"success": True, "message": "If the account exists, a verification code has been sent.", "data": {"cooldown_seconds": 60}}
    if user.email_verified:
        return {"success": True, "message": "Email is already verified.", "data": {"verified": True}}

    now = _now_utc_naive()
    latest = _run(EmailOtp.find(EmailOtp.email == email).sort(-EmailOtp.created_at).first_or_none())
    latest_created_at = _as_utc_naive(latest.created_at) if latest and latest.created_at else None
    if latest_created_at and (now - latest_created_at).total_seconds() < 60:
        remaining = max(1, 60 - int((now - latest_created_at).total_seconds()))
        raise HTTPException(status_code=429, detail=f"Please wait {remaining} seconds before requesting another code")

    request_count = _run(EmailOtp.find(EmailOtp.email == email, EmailOtp.created_at >= now - timedelta(hours=1)).count())
    if request_count >= 5:
        raise HTTPException(status_code=429, detail="Verification request limit reached. Try again in one hour.")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    challenge = EmailOtp(
        id=str(uuid4()),
        email=email,
        otp_hash=_otp_digest(otp),
        expires_at=now + timedelta(minutes=5),
    )
    try:
        # Commit only after the provider accepts the email; failed sends do not consume a quota slot.
        send_resend_verification_otp(email, otp)
        _run(challenge.insert())
    except EmailNotConfigured:
        logger.error("OTP requested but Resend is not configured")
        raise HTTPException(status_code=503, detail="Email verification is temporarily unavailable")
    except EmailDeliveryError:
        raise HTTPException(status_code=502, detail="Unable to send verification email. Please try again.")
    except Exception:
        logger.exception("Unexpected failure while issuing email OTP")
        raise HTTPException(status_code=500, detail="Unable to create verification code")

    logger.info("Verification OTP issued for %s", email)
    return {"success": True, "message": "Verification code sent. It expires in 5 minutes.", "data": {"cooldown_seconds": 60, "expires_in_seconds": 300}}


@router.post("/verify-otp", response_model=SuccessResponse)
def verify_otp(payload: OtpVerification, db: Session = Depends(get_db)) -> Any:
    """Validate an unused OTP and mark the associated account email as verified."""
    email = str(payload.email).strip().lower()
    otp = payload.otp.strip()
    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    now = _now_utc_naive()
    challenge = _run(EmailOtp.find(EmailOtp.email == email, EmailOtp.used_at == None).sort(-EmailOtp.created_at).first_or_none())
    if not challenge or _as_utc_naive(challenge.expires_at) <= now:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if not hmac.compare_digest(challenge.otp_hash, _otp_digest(otp)):
        logger.warning("Invalid email OTP submitted for %s", email)
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = _run(User.find_one(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    challenge.used_at = now
    user.email_verified = True
    user.email_verification_token = None
    _run(challenge.save())
    _run(user.save())
    logger.info("Email verified with OTP for %s", email)
    return {"success": True, "message": "Email verified successfully.", "data": {"verified": True}}


@router.post("/verify-factory", response_model=SuccessResponse)
def verify_factory(payload: FactoryVerification, db: Session = Depends(get_db)) -> Any:
    """Verify factory using factory code (temporarily 654321 for all users during setup period)."""
    factory_code = str(payload.factory_code).strip()
    
    # Temporary: Accept 654321 as valid factory code during setup period
    if factory_code != "654321":
        raise HTTPException(status_code=400, detail="Invalid factory code")
    
    # In a real implementation, you would:
    # 1. Look up factory by code
    # 2. Verify the user belongs to that factory
    # For now, we just return success
    logger.info("Factory verified with code %s", factory_code)
    return {"success": True, "message": "Factory verified successfully.", "data": {"factory_verified": True}}


@router.post("/send-mobile-otp", response_model=SuccessResponse, responses={429: {"model": ErrorResponse}})
def send_mobile_otp(payload: MobileOtpRequest, db: Session = Depends(get_db)) -> Any:
    """Issue a rate-limited mobile phone verification OTP."""
    user = _run(User.find_one(User.id == payload.user_id))
    if not user:
        return {"success": True, "message": "If the account exists, a verification code has been sent.", "data": {"cooldown_seconds": 60}}
    
    phone_number = str(payload.phone_number).strip()
    if not phone_number or len(phone_number) < 10:
        raise HTTPException(status_code=400, detail="Valid phone number is required")
    
    if user.mobile_verified:
        return {"success": True, "message": "Phone is already verified.", "data": {"verified": True}}
    
    now = _now_utc_naive()
    latest = _run(MobileOtp.find(MobileOtp.user_id == payload.user_id, MobileOtp.phone_number == phone_number).sort(-MobileOtp.created_at).first_or_none())
    latest_created_at = _as_utc_naive(latest.created_at) if latest and latest.created_at else None
    if latest_created_at and (now - latest_created_at).total_seconds() < 60:
        remaining = max(1, 60 - int((now - latest_created_at).total_seconds()))
        raise HTTPException(status_code=429, detail=f"Please wait {remaining} seconds before requesting another code")
    
    request_count = _run(MobileOtp.find(MobileOtp.user_id == payload.user_id, MobileOtp.created_at >= now - timedelta(hours=1)).count())
    if request_count >= 5:
        raise HTTPException(status_code=429, detail="Verification request limit reached. Try again in one hour.")
    
    otp = f"{secrets.randbelow(1_000_000):06d}"
    mobile_challenge = MobileOtp(
        id=str(uuid4()),
        user_id=payload.user_id,
        phone_number=phone_number,
        otp_hash=_otp_digest(otp),
        expires_at=now + timedelta(minutes=5),
    )
    _run(mobile_challenge.insert())
    
    # In a real implementation, you would send SMS here
    # For now, log the OTP for testing
    logger.info("Mobile verification OTP issued for user %s: %s", payload.user_id, otp)
    
    user.phone_number = phone_number
    _run(user.save())
    
    return {"success": True, "message": "Verification code sent. It expires in 5 minutes.", "data": {"cooldown_seconds": 60, "expires_in_seconds": 300}}


@router.post("/verify-mobile", response_model=SuccessResponse)
def verify_mobile(payload: MobileOtpVerification, db: Session = Depends(get_db)) -> Any:
    """Validate mobile OTP and mark the phone as verified."""
    otp = payload.otp.strip()
    if len(otp) != 6 or not otp.isdigit():
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")
    
    user = _run(User.find_one(User.id == payload.user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    now = _now_utc_naive()
    challenge = _run(MobileOtp.find(MobileOtp.user_id == payload.user_id, MobileOtp.used_at == None).sort(-MobileOtp.created_at).first_or_none())
    
    if not challenge or _as_utc_naive(challenge.expires_at) <= now:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    if not hmac.compare_digest(challenge.otp_hash, _otp_digest(otp)):
        logger.warning("Invalid mobile OTP submitted for user %s", payload.user_id)
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    challenge.used_at = now
    user.mobile_verified = True
    _run(challenge.save())
    _run(user.save())
    
    logger.info("Mobile verified with OTP for user %s", payload.user_id)
    return {"success": True, "message": "Mobile verified successfully.", "data": {"verified": True}}


@router.post("/login", response_model=SuccessResponse)
def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)) -> Any:
    user = _run(User.find_one(User.email == user_in.email))
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.email)
    refresh_token = _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    logger.info("Authenticated user %s", user.email)
    return {
        "success": True,
        "message": "Operation successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/admin-login", response_model=SuccessResponse)
def admin_login(user_in: UserLogin, response: Response, request: Request = None, db: Session = Depends(get_db)) -> Any:
    user = _run(User.find_one(User.email == user_in.email))
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    if user.role not in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="Admin access required")

    if user.two_factor_enabled and not user_in.model_extra:
        raise HTTPException(status_code=202, detail={"two_factor_required": True, "email": user.email})

    token = create_access_token(user.email)
    refresh_token = _issue_refresh_token(user)
    _set_refresh_cookie(response, refresh_token)
    _run(AuditTrail(
        id=str(uuid4()),
        entity_type="admin_session",
        entity_id=user.id,
        action="admin_login",
        user_id=user.id,
        user_role=user.role.value,
        ip_address=request.client.host if request and request.client else None,
        changes={},
    ).insert())
    logger.info("Authenticated admin %s", user.email)
    return {
        "success": True,
        "message": "Admin sign-in successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/google", response_model=SuccessResponse)
def google_login(payload: dict, response: Response, db: Session = Depends(get_db)) -> Any:
    credential: str = (payload.get("credential") or "").strip()
    email: Optional[str] = None
    full_name: Optional[str] = None

    if credential:
        if not (google_id_token and google_requests):
            raise HTTPException(status_code=500, detail="Google login is not fully configured on the server")
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google client ID is not configured on the server")
        try:
            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        email = (idinfo.get("email") or "").strip().lower() or None
        full_name = (idinfo.get("name") or idinfo.get("given_name") or idinfo.get("family_name") or "").strip() or None

    if not email:
        raise HTTPException(status_code=400, detail="A valid Google credential is required")

    user = _run(User.find_one(User.email == email))
    if user and full_name and user.full_name != full_name:
        user.full_name = full_name
        _run(user.save())
    if not user:
        user = User(
            id=str(uuid4()),
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(secrets.token_urlsafe(24)),
            role=UserRole.RAW_MATERIAL_CONSUMER,
        )
        _run(user.insert())

    token = create_access_token(user.email)
    refresh_token = _run(_issue_refresh_token(user))
    _set_refresh_cookie(response, refresh_token)
    logger.info("Authenticated Google user %s", user.email)
    return {
        "success": True,
        "message": "Google sign-in successful",
        "data": {"token": token, "user": _public_user(user)},
    }


@router.post("/forgot-password", response_model=SuccessResponse)
def forgot_password(payload: dict) -> Any:
    email = (payload.get("email") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = _run(User.find_one(User.email == email))
    if user:
        user.password_reset_token = secrets.token_urlsafe(32)
        _run(user.save())
        try:
            send_password_reset_email(user.email, user.password_reset_token)
        except EmailNotConfigured:
            logger.info("SMTP not configured; password reset token generated for %s", email)
    logger.info("Password reset requested for %s", email)
    return {"success": True, "message": "If that email exists, reset instructions have been queued.", "data": {"email": email}}


@router.post("/reset-password", response_model=SuccessResponse)
def reset_password(payload: dict, db: Session = Depends(get_db)) -> Any:
    token = (payload.get("token") or "").strip()
    password = (payload.get("password") or "").strip()
    if not token or len(password) < 8:
        raise HTTPException(status_code=400, detail="Valid reset token and password are required")
    user = _run(User.find_one(User.password_reset_token == token))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.hashed_password = get_password_hash(password)
    user.password_reset_token = None
    _run(user.save())
    return {"success": True, "message": "Password reset successful", "data": {}}


@router.post("/verify-email", response_model=SuccessResponse)
def verify_email(payload: dict) -> Any:
    token = (payload.get("token") or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Verification token is required")
    user = _run(User.find_one(User.email_verification_token == token))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.email_verified = True
    user.email_verification_token = None
    _run(user.save())
    return {"success": True, "message": "Email verified", "data": {"verified": True}}

@router.post("/logout", response_model=SuccessResponse)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="symbioai_refresh_token"),
    db: Session = Depends(get_db),
) -> Any:
    is_secure_cookie = settings.SECURE_COOKIES or settings.ENVIRONMENT.lower() == "production"
    if refresh_token:
        token_obj = _run(RefreshToken.find_one(RefreshToken.token == refresh_token, RefreshToken.revoked == False))
        if token_obj:
            token_obj.revoked = True
            _run(token_obj.save())
    response.delete_cookie(
        "symbioai_refresh_token",
        path="/api/auth",
        secure=is_secure_cookie,
        samesite="none" if is_secure_cookie else "lax",
    )
    return {"success": True, "message": "Operation successful", "data": {}}


@router.get("/me", response_model=SuccessResponse)
def me(current_user: User = Depends(get_current_user)) -> Any:
    return {"success": True, "message": "Operation successful", "data": {"user": _public_user(current_user)}}


@router.post("/refresh", response_model=SuccessResponse, responses={401: {"model": ErrorResponse}})
def refresh_access_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias="symbioai_refresh_token"),
    db: Session = Depends(get_db),
) -> Any:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_obj = _run(RefreshToken.find_one(RefreshToken.token == refresh_token, RefreshToken.revoked == False))
    if not token_obj or token_obj.expires_at <= _now_utc_naive():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    user = _run(User.find_one(User.id == token_obj.user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    token_obj.revoked = True
    _run(token_obj.save())
    new_refresh = _run(_issue_refresh_token(user))
    _set_refresh_cookie(response, new_refresh)

    new_access = create_access_token(user.email)
    return {"success": True, "message": "Token refreshed", "data": {"token": new_access}}


@router.post("/2fa/setup", response_model=SuccessResponse)
def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = _run(User.find_one(User.id == current_user.id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    secret = pyotp.random_base32()
    db_user.two_factor_secret = secret
    _run(db_user.save())
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=db_user.email, issuer_name="SymbioAI")
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return {"success": True, "message": "2FA setup created", "data": {"secret": secret, "otpauth_url": uri, "qr_code": qr_data_url}}


@router.post("/2fa/enable", response_model=SuccessResponse)
def enable_2fa(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = _run(User.find_one(User.id == current_user.id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    code = (payload.get("code") or "").strip()
    if not db_user.two_factor_secret or not pyotp.TOTP(db_user.two_factor_secret).verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    recovery_codes = [secrets.token_hex(4) for _ in range(8)]
    db_user.two_factor_enabled = True
    db_user.recovery_codes = json.dumps(recovery_codes)
    _run(db_user.save())
    return {"success": True, "message": "2FA enabled", "data": {"recovery_codes": recovery_codes}}


@router.post("/2fa/verify-login", response_model=SuccessResponse)
def verify_2fa_login(payload: dict, response: Response, db: Session = Depends(get_db)) -> Any:
    email = (payload.get("email") or "").strip()
    code = (payload.get("code") or "").strip()
    user = _run(User.find_one(User.email == email))
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
        _run(user.save())
    token = create_access_token(user.email)
    refresh_token = _run(_issue_refresh_token(user))
    _set_refresh_cookie(response, refresh_token)
    return {"success": True, "message": "2FA verified", "data": {"token": token, "user": _public_user(user)}}


@router.post("/2fa/disable", response_model=SuccessResponse)
def disable_2fa(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    db_user = _run(User.find_one(User.id == current_user.id))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    code = (payload.get("code") or "").strip()
    if db_user.two_factor_secret and not pyotp.TOTP(db_user.two_factor_secret).verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    db_user.two_factor_enabled = False
    db_user.two_factor_secret = None
    db_user.recovery_codes = None
    db_user.trusted_device_token = None
    _run(db_user.save())
    return {"success": True, "message": "2FA disabled", "data": {}}