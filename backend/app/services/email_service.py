import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings

logger = logging.getLogger("symbioai.email")


class EmailNotConfigured(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    """Raised when the configured mail provider cannot accept a message."""

    pass


def send_resend_verification_otp(to_email: str, otp: str) -> None:
    """Deliver an OTP via Resend without logging the OTP or API key."""
    if not settings.RESEND_API_KEY:
        raise EmailNotConfigured("RESEND_API_KEY is not configured")

    html = f"""<h2>Verify Your Email</h2>
<p>Your One-Time Password (OTP) is:</p>
<h1>{otp}</h1>
<p>This OTP is valid for 5 minutes.</p>
<p>If you didn't request this, please ignore this email.</p>"""
    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={
                "from": settings.SMTP_FROM_EMAIL or "noreply@symbioai.com",
                "to": [to_email],
                "subject": "SymbioAI Email Verification",
                "html": html,
            },
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        logger.warning("Resend OTP delivery failed for %s: %s", to_email, type(exc).__name__)
        raise EmailDeliveryError("Email provider is temporarily unavailable") from exc

    if response.status_code >= 400:
        logger.warning("Resend rejected OTP delivery for %s with status %s", to_email, response.status_code)
        raise EmailDeliveryError("Email provider could not send the verification code")

    logger.info("Verification OTP accepted by Resend for %s", to_email)


def ensure_email_configured() -> None:
    missing = [name for name in ["SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"] if not getattr(settings, name)]
    if missing:
        raise EmailNotConfigured(f"SMTP email is not configured. Missing: {', '.join(missing)}")


def send_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    # Try SMTP if configured
    if settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
            logger.info("Email sent to %s subject=%s", to_email, subject)
            return
        except Exception as e:
            logger.error("Failed to send email via SMTP: %s", e)
            raise EmailDeliveryError(f"Failed to send email: {e}")
    
    # If SMTP not configured, try Resend
    if settings.RESEND_API_KEY:
        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json={
                    "from": settings.SMTP_FROM_EMAIL,
                    "to": [to_email],
                    "subject": subject,
                    "text": body,
                },
                timeout=15.0,
            )
            if response.status_code >= 400:
                raise EmailDeliveryError(f"Resend API returned status {response.status_code}")
            logger.info("Email sent via Resend to %s subject=%s", to_email, subject)
            return
        except Exception as e:
            logger.error("Failed to send email via Resend: %s", e)
            raise EmailDeliveryError(f"Failed to send email via Resend: {e}")
    
    # No email provider configured
    raise EmailNotConfigured("No email provider configured. Please configure SMTP or RESEND_API_KEY")


def send_welcome_email(to_email: str, full_name: str) -> None:
    try:
        send_email(to_email, "Welcome to SymbioAI", f"Hi {full_name},\n\nWelcome to SymbioAI. Your circular marketplace account is ready.")
    except (EmailNotConfigured, EmailDeliveryError) as e:
        logger.info("Welcome email not sent for %s: %s", to_email, e)


def send_verification_email(to_email: str, token: str) -> None:
    try:
        link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        send_email(to_email, "Verify your SymbioAI email", f"Verify your email using this link:\n{link}")
    except (EmailNotConfigured, EmailDeliveryError) as e:
        logger.info("Verification email not sent for %s: %s", to_email, e)


def send_password_reset_email(to_email: str, token: str) -> None:
    try:
        link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        send_email(to_email, "Reset your SymbioAI password", f"Reset your password using this secure link:\n{link}")
    except (EmailNotConfigured, EmailDeliveryError) as e:
        logger.info("Password reset email not sent for %s: %s", to_email, e)


class SmsNotConfigured(RuntimeError):
    pass


class SmsDeliveryError(RuntimeError):
    """Raised when SMS provider cannot send the message."""
    pass


def send_sms_otp(phone_number: str, otp: str) -> None:
    """Send OTP via SMS using Twilio."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
        raise SmsNotConfigured("Twilio is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER")
    
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your SymbioAI verification code is: {otp}. Valid for 5 minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info("SMS OTP sent to %s via Twilio", phone_number)
        return message.sid
        
    except ImportError:
        raise SmsNotConfigured("Twilio library not installed. Install with: pip install twilio")
    except Exception as e:
        logger.error("Failed to send SMS via Twilio: %s", e)
        raise SmsDeliveryError(f"Failed to send SMS: {e}")
