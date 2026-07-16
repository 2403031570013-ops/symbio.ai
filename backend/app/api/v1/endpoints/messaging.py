from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import SessionLocal
from app.models.messaging import Conversation, Message
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.core.security import get_user_from_token
from app.services.notification_service import create_notification
from app.services.realtime import realtime_manager

router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_conversation(conversation: Conversation) -> dict:
    return {
        "id": conversation.id,
        "match_id": conversation.match_id,
        "material_name": conversation.material_name,
        "partner_name": conversation.partner_name,
        "seller_id": conversation.seller_id,
        "buyer_id": conversation.buyer_id,
        "status": conversation.status,
        "unread_count": conversation.unread_count,
        "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
    }


def serialize_message(message: Message) -> dict:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "sender_name": message.sender_name,
        "message_type": message.message_type,
        "body": message.body,
        "attachment_name": message.attachment_name,
        "attachment_type": message.attachment_type,
        "offer_amount": message.offer_amount,
        "offer_status": message.offer_status,
        "is_read": message.is_read,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


@router.get("/conversations", response_model=SuccessResponse)
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    conversations = (
        db.query(Conversation)
        .filter(Conversation.seller_id == current_user.id)
        .order_by(desc(Conversation.last_message_at))
        .all()
    )
    return {"success": True, "message": "Conversations loaded", "data": {"conversations": [serialize_conversation(item) for item in conversations]}}


@router.post("/conversations", response_model=SuccessResponse)
def create_conversation(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    material_name = (payload.get("material_name") or payload.get("match_name") or "").strip()
    partner_name = (payload.get("partner_name") or "").strip()
    initial_message = (payload.get("message") or "").strip()
    match_id = (payload.get("match_id") or "").strip() or None

    if not material_name or not partner_name:
        raise HTTPException(status_code=400, detail="Material and partner are required")
    if not initial_message:
        raise HTTPException(status_code=400, detail="Initial message is required")

    conversation = None
    if match_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.match_id == match_id, Conversation.seller_id == current_user.id)
            .first()
        )

    if not conversation:
        conversation = Conversation(
            id=str(uuid4()),
            match_id=match_id,
            material_name=material_name,
            partner_name=partner_name,
            seller_id=current_user.id,
            status="negotiating",
            unread_count=0,
            last_message_at=datetime.now(timezone.utc),
        )
        db.add(conversation)
        db.flush()

    message = Message(
        id=str(uuid4()),
        conversation_id=conversation.id,
        sender_id=current_user.id,
        sender_name=current_user.full_name,
        message_type="text",
        body=initial_message,
        is_read=True,
    )
    conversation.last_message_at = datetime.now(timezone.utc)
    db.add(message)
    db.commit()
    db.refresh(conversation)
    db.refresh(message)
    create_notification(
        db,
        current_user.id,
        "message",
        f"Conversation opened with {partner_name}",
        initial_message,
        action_url="/matches",
    )

    return {
        "success": True,
        "message": "Conversation created",
        "data": {"conversation": serialize_conversation(conversation), "message": serialize_message(message)},
    }


@router.get("/conversations/{conversation_id}/messages", response_model=SuccessResponse)
def list_messages(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.seller_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    conversation.unread_count = 0
    for message in messages:
        message.is_read = True
    db.commit()
    return {"success": True, "message": "Messages loaded", "data": {"messages": [serialize_message(item) for item in messages]}}


@router.post("/conversations/{conversation_id}/messages", response_model=SuccessResponse)
async def send_message(conversation_id: str, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.seller_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    body = (payload.get("body") or "").strip()
    message_type = (payload.get("message_type") or "text").strip()
    if not body:
        raise HTTPException(status_code=400, detail="Message body is required")

    message = Message(
        id=str(uuid4()),
        conversation_id=conversation.id,
        sender_id=current_user.id,
        sender_name=current_user.full_name,
        message_type=message_type,
        body=body,
        attachment_name=(payload.get("attachment_name") or "").strip() or None,
        attachment_type=(payload.get("attachment_type") or "").strip() or None,
        offer_amount=(payload.get("offer_amount") or "").strip() or None,
        offer_status=(payload.get("offer_status") or "").strip() or None,
        is_read=True,
    )
    conversation.last_message_at = datetime.now(timezone.utc)
    db.add(message)
    db.commit()
    db.refresh(message)
    notification = create_notification(db, current_user.id, "message", f"New message in {conversation.partner_name}", body, action_url="/matches")
    await realtime_manager.send_user(current_user.id, {"type": "message", "conversation_id": conversation.id, "message": serialize_message(message)})
    await realtime_manager.send_user(current_user.id, {"type": "notification", "notification": {"id": notification.id, "title": notification.title, "message": notification.message}})
    return {"success": True, "message": "Message sent", "data": {"message": serialize_message(message)}}


@router.put("/conversations/{conversation_id}/offer", response_model=SuccessResponse)
async def update_offer(conversation_id: str, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.seller_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    status = (payload.get("status") or "").strip().lower()
    if status not in {"accepted", "rejected", "countered"}:
        raise HTTPException(status_code=400, detail="Offer status must be accepted, rejected, or countered")

    message = Message(
        id=str(uuid4()),
        conversation_id=conversation.id,
        sender_id=current_user.id,
        sender_name=current_user.full_name,
        message_type="offer",
        body=f"Offer {status}",
        offer_amount=(payload.get("offer_amount") or "").strip() or None,
        offer_status=status,
        is_read=True,
    )
    conversation.status = "offer_" + status
    conversation.last_message_at = datetime.now(timezone.utc)
    db.add(message)
    db.commit()
    db.refresh(message)
    await realtime_manager.send_user(current_user.id, {"type": "offer", "conversation_id": conversation.id, "message": serialize_message(message), "status": status})
    return {"success": True, "message": f"Offer {status}", "data": {"message": serialize_message(message), "conversation": serialize_conversation(conversation)}}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    db = SessionLocal()
    user = get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008)
        db.close()
        return

    await realtime_manager.connect(user.id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            event_type = payload.get("type")
            if event_type in {"typing", "read_receipt", "presence"}:
                await realtime_manager.send_user(user.id, {**payload, "user_id": user.id})
    except WebSocketDisconnect:
        realtime_manager.disconnect(user.id, websocket)
    finally:
        db.close()
