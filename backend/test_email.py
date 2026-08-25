#!/usr/bin/env python3
"""Test email configuration"""
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.email_service import send_email, EmailNotConfigured, EmailDeliveryError

def test_email_config():
    """Test email configuration"""
    print("Testing Email Configuration...")
    print(f"SMTP_HOST: {settings.SMTP_HOST}")
    print(f"SMTP_PORT: {settings.SMTP_PORT}")
    print(f"SMTP_USERNAME: {settings.SMTP_USERNAME}")
    print(f"SMTP_FROM_EMAIL: {settings.SMTP_FROM_EMAIL}")
    print(f"SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
    print(f"SMTP_PASSWORD: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'Not set'}")
    print(f"RESEND_API_KEY: {'*' * len(settings.RESEND_API_KEY) if settings.RESEND_API_KEY else 'Not set'}")
    
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("❌ SMTP is not properly configured")
        return False
    
    try:
        print("\n📧 Sending test email to", settings.SMTP_USERNAME)
        send_email(
            settings.SMTP_USERNAME,
            "SymbioAI Email Test",
            "This is a test email from SymbioAI. If you receive this, your email configuration is working!"
        )
        print("✅ Test email sent successfully!")
        return True
    except EmailNotConfigured as e:
        print(f"❌ Email not configured: {e}")
        return False
    except EmailDeliveryError as e:
        print(f"❌ Email delivery failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_email_config()
    sys.exit(0 if success else 1)
