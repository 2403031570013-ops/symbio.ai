from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.email_service import send_email, EmailNotConfigured


def create_notification(
    db: Session,
    user_id: str,
    category: str,
    title: str,
    message: str,
    action_url: str | None = None,
    email: str | None = None,
) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        user_id=user_id,
        category=category,
        title=title,
        message=message,
        action_url=action_url,
    )
    if email:
        try:
            send_email(email, title, message)
            notification.delivered_email = True
        except EmailNotConfigured:
            notification.delivered_email = False
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
