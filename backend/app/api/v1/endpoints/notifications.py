import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


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
    notifications = _run(Notification.find(Notification.user_id == current_user.id).sort(-Notification.created_at).limit(100).to_list())
    return {"success": True, "message": "Notifications loaded", "data": {"notifications": [serialize(item) for item in notifications], "unread_count": sum(1 for item in notifications if not item.read)}}


@router.put("/{notification_id}/read", response_model=SuccessResponse)
def mark_read(notification_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    notification = _run(Notification.find_one(Notification.id == notification_id, Notification.user_id == current_user.id))
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = True
    _run(notification.save())
    return {"success": True, "message": "Notification marked read", "data": {"notification": serialize(notification)}}
