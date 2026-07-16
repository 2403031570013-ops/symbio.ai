from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize(item: Notification) -> dict:
    return {
        "id": item.id,
        "category": item.category,
        "title": item.title,
        "message": item.message,
        "action_url": item.action_url,
        "read": item.read,
        "delivered_email": item.delivered_email,
        "delivered_push": item.delivered_push,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("", response_model=SuccessResponse)
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return {"success": True, "message": "Notifications loaded", "data": {"notifications": [serialize(item) for item in notifications], "unread_count": sum(1 for item in notifications if not item.read)}}


@router.put("/{notification_id}/read", response_model=SuccessResponse)
def mark_read(notification_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = True
    db.commit()
    return {"success": True, "message": "Notification marked read", "data": {"notification": serialize(notification)}}
