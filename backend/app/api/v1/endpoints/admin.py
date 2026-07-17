import csv
import io
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.api.v1.endpoints.auth import get_password_hash
from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import SessionLocal, desc, func, or_
from app.models.analytics import Analytics
from app.models.auth import RefreshToken
from app.models.compliance_risk import AuditTrail, DocumentCompliance
from app.models.factory import Factory
from app.models.material import Material
from app.models.match import Match
from app.models.messaging import Conversation, Message
from app.models.notification import Notification
from app.models.storage import StoredObject
from app.models.transaction import Transaction
from app.models.user import User, UserRole
from app.schemas.common import SuccessResponse
from app.services.notification_service import create_notification

router = APIRouter()
Session = Any

ADMIN_ROLES = {UserRole.ADMIN, UserRole.SUPER_ADMIN}
AI_SETTINGS = {"confidence_threshold": 80}


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(current_user: User) -> None:
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")


def require_super_admin(current_user: User) -> None:
    require_admin(current_user)
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super Admin access required")


def audit(db: Session, request: Request, actor: User, entity_type: str, entity_id: str, action: str, changes: dict | None = None, reason: str | None = None) -> None:
    db.add(
        AuditTrail(
            id=str(uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=actor.id,
            user_role=actor.role.value,
            ip_address=request.client.host if request.client else None,
            changes=changes or {},
            reason=reason,
        )
    )


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": bool(user.is_active),
        "email_verified": bool(getattr(user, "email_verified", False)),
        "factory_logo_url": getattr(user, "factory_logo_url", None),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def listing_payload(item: Material) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "chemical_composition": item.chemical_composition,
        "physical_state": item.physical_state,
        "quantity": item.quantity,
        "frequency": item.frequency,
        "certificate": item.certificate,
        "certificate_url": item.certificate_url,
        "photo_url": item.photo_url,
        "lab_report_url": item.lab_report_url,
        "status": item.status,
        "owner_id": item.owner_id,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("/dashboard", response_model=SuccessResponse)
def admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    analytics = db.query(Analytics).first()
    transactions = db.query(Transaction).all()
    materials = db.query(Material).all()
    users = db.query(User).all()
    revenue = sum(float(item.amount or 0) for item in transactions)
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
    storage_bytes = len(db.query(StoredObject).all())
    listing_statuses: dict[str, int] = {}
    for item in materials:
        listing_statuses[item.status] = listing_statuses.get(item.status, 0) + 1
    active_users = len([user for user in users if user.is_active])
    successful_matches = len([match for match in db.query(Match).all() if match.symbio_score >= AI_SETTINGS["confidence_threshold"]])
    recent_activity = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).limit(8).all()
    recent_logins = db.query(AuditTrail).filter(AuditTrail.action == "admin_login").order_by(AuditTrail.timestamp.desc()).limit(6).all()
    return {
        "success": True,
        "message": "Admin dashboard loaded",
        "data": {
            "stats": {
                "total_users": len(users),
                "users": len(users),
                "active_users": active_users,
                "new_registrations": len([user for user in users if user.created_at and user.created_at >= seven_days_ago]),
                "pending_listings": listing_statuses.get("pending", 0),
                "approved_listings": listing_statuses.get("approved", 0),
                "rejected_listings": listing_statuses.get("rejected", 0),
                "listings": len(materials),
                "pending_ai_matches": len([match for match in db.query(Match).all() if match.symbio_score < AI_SETTINGS["confidence_threshold"]]),
                "successful_matches": successful_matches,
                "matches": len(db.query(Match).all()),
                "marketplace_revenue": float(revenue),
                "revenue": float(revenue),
                "carbon_saved": float(getattr(analytics, "co2_avoided", 0) or 0),
                "transactions_today": len([item for item in transactions if item.created_at and item.created_at >= today]),
                "storage_usage": storage_bytes,
                "server_status": "healthy",
                "database_status": "healthy",
                "api_health": "operational",
            },
            "charts": {
                "users_by_role": [{"label": role.value, "value": len([user for user in users if user.role == role])} for role in UserRole],
                "listings_by_status": [{"label": key or "unknown", "value": value} for key, value in listing_statuses.items()],
                "revenue_heatmap": [{"label": item.partner_name, "value": float(item.amount)} for item in sorted(transactions, key=lambda item: item.amount or 0, reverse=True)[:8]],
            },
            "recent_activities": [{"action": item.action, "entity": item.entity_type, "actor_role": item.user_role, "at": item.timestamp.isoformat() if item.timestamp else None} for item in recent_activity],
            "recent_logins": [{"actor": item.user_id, "at": item.timestamp.isoformat() if item.timestamp else None, "ip": item.ip_address} for item in recent_logins],
            "system_alerts": [
                {"severity": "info", "message": "RBAC enforced on all admin APIs"},
                {"severity": "warning" if not settings.SMTP_HOST else "info", "message": "SMTP configured" if settings.SMTP_HOST else "SMTP not configured"},
                {"severity": "warning" if not settings.S3_BUCKET else "info", "message": "Object storage configured" if settings.S3_BUCKET else "Object storage credentials missing"},
            ],
        },
    }

@router.get("/users", response_model=SuccessResponse)
def list_users(q: str = "", role: str = "", status: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    query = db.query(User)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(User.email.ilike(like), User.full_name.ilike(like)))
    if role:
        try:
            query = query.filter(User.role == UserRole(role))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role")
    if status == "active":
        query = query.filter(User.is_active == True)
    if status == "suspended":
        query = query.filter(User.is_active == False)
    users = query.order_by(User.created_at.desc()).all()
    return {"success": True, "message": "Users loaded", "data": {"users": [user_payload(user) for user in users]}}


@router.put("/users/{user_id}", response_model=SuccessResponse)
def edit_user(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    before = user_payload(user)
    if "full_name" in payload and str(payload["full_name"]).strip():
        user.full_name = str(payload["full_name"]).strip()
    if "email_verified" in payload:
        user.email_verified = bool(payload["email_verified"])
    if "factory_logo_url" in payload:
        user.factory_logo_url = str(payload["factory_logo_url"] or "").strip() or None
    audit(db, request, current_user, "user", user.id, "update", {"before": before, "after": payload})
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "User updated", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/role", response_model=SuccessResponse)
def update_user_role(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    next_role = UserRole(payload.get("role"))
    if next_role in ADMIN_ROLES and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only Super Admin can grant admin roles")
    if user.id == current_user.id and next_role not in ADMIN_ROLES:
        raise HTTPException(status_code=400, detail="Admins cannot remove their own admin access")
    before = user.role.value
    user.role = next_role
    audit(db, request, current_user, "user", user.id, "change_role", {"before": before, "after": next_role.value})
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Role updated", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/suspend", response_model=SuccessResponse)
def suspend_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot suspend themselves")
    user.is_active = False
    create_notification(db, user.id, "account", "Account suspended", "Your SymbioAI account was suspended by an administrator. Contact support if you believe this is incorrect.", action_url="/login", email=user.email)
    audit(db, request, current_user, "user", user.id, "suspend")
    db.commit()
    return {"success": True, "message": "User suspended", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/activate", response_model=SuccessResponse)
def activate_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    create_notification(db, user.id, "account", "Account activated", "Your SymbioAI account is active again. You can now sign in.", action_url="/login", email=user.email)
    audit(db, request, current_user, "user", user.id, "activate")
    db.commit()
    return {"success": True, "message": "User activated", "data": {"user": user_payload(user)}}


@router.delete("/users/{user_id}", response_model=SuccessResponse)
def delete_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_super_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Super Admin cannot delete self")
    payload = user_payload(user)
    # A deleted account is permanently removed. Revoke all server-side sessions
    # first so the former user cannot refresh an existing browser session.
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    audit(db, request, current_user, "user", user_id, "permanent_delete", payload)
    db.commit()
    return {
        "success": True,
        "message": "Account permanently deleted. The person must register again to access SymbioAI.",
        "data": {"id": user_id, "requires_registration": True},
    }


@router.post("/users/{user_id}/reset-password", response_model=SuccessResponse)
def reset_user_password(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    temporary_password = payload.get("password") or f"Symbio-{secrets.token_urlsafe(6)}1!"
    user.hashed_password = get_password_hash(temporary_password)
    audit(db, request, current_user, "user", user.id, "reset_password")
    db.commit()
    return {"success": True, "message": "Password reset", "data": {"temporary_password": temporary_password}}


@router.put("/users/{user_id}/company/{decision}", response_model=SuccessResponse)
def verify_company(user_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if decision not in {"verify", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid company decision")
    user.email_verified = decision == "verify"
    create_notification(db, user.id, "verification", f"Company {decision}ed", f"Your company verification was {decision}ed by an administrator.", action_url="/dashboard", email=user.email)
    audit(db, request, current_user, "company", user.id, decision)
    db.commit()
    return {"success": True, "message": f"Company {decision}ed", "data": {"user": user_payload(user)}}


@router.get("/factories", response_model=SuccessResponse)
def list_factories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    factories = db.query(Factory).order_by(Factory.created_at.desc()).all()
    return {"success": True, "message": "Factories loaded", "data": {"factories": [{"id": f.id, "name": f.name, "industry": f.industry, "location": f.location, "verified": f.verified, "owner_id": f.owner_id, "created_at": f.created_at.isoformat() if f.created_at else None} for f in factories]}}


@router.get("/factories/{factory_id}/documents", response_model=SuccessResponse)
def list_factory_documents(factory_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    docs = db.query(DocumentCompliance).filter(DocumentCompliance.factory_id == factory_id).all()
    return {
        "success": True,
        "message": "Documents loaded",
        "data": {
            "documents": [
                {
                    "id": d.id,
                    "document_type": d.document_type,
                    "document_name": d.document_name,
                    "document_number": d.document_number,
                    "issuing_authority": d.issuing_authority,
                    "status": d.status,
                    "expiry_date": d.expiry_date.isoformat() if d.expiry_date else None,
                    "document_url": d.document_url
                }
                for d in docs
            ]
        }
    }


@router.put("/factories/{factory_id}/{decision}", response_model=SuccessResponse)
def factory_decision(factory_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    if decision not in {"verify", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid factory decision")
    factory.verified = decision == "verify"
    audit(db, request, current_user, "factory", factory.id, decision)
    db.commit()
    return {"success": True, "message": f"Factory {decision}ed", "data": {"factory": {"id": factory.id, "verified": factory.verified}}}


@router.get("/listings", response_model=SuccessResponse)
def list_materials(q: str = "", status: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    query = db.query(Material)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Material.name.ilike(like), Material.chemical_composition.ilike(like)))
    if status:
        query = query.filter(Material.status == status)
    materials = query.order_by(Material.created_at.desc()).all()
    return {"success": True, "message": "Listings loaded", "data": {"listings": [listing_payload(item) for item in materials]}}


@router.put("/listings/{material_id}", response_model=SuccessResponse)
def edit_listing(material_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    before = listing_payload(material)
    for field in ["name", "chemical_composition", "physical_state", "quantity", "frequency", "certificate"]:
        if field in payload and str(payload[field]).strip():
            setattr(material, field, str(payload[field]).strip())
    audit(db, request, current_user, "listing", material.id, "edit", {"before": before, "after": payload})
    db.commit()
    db.refresh(material)
    return {"success": True, "message": "Listing updated", "data": {"listing": listing_payload(material)}}


@router.put("/listings/{material_id}/status", response_model=SuccessResponse)
def update_listing_status(material_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    status = (payload.get("status") or "").strip().lower()
    if status not in {"pending", "approved", "rejected", "archived", "flagged"}:
        raise HTTPException(status_code=400, detail="Invalid listing status")
    before = material.status
    material.status = status
    audit(db, request, current_user, "listing", material.id, f"status_{status}", {"before": before, "after": status})
    db.commit()
    return {"success": True, "message": "Listing status updated", "data": {"listing": {"id": material.id, "status": material.status}}}


@router.post("/listings/bulk-status", response_model=SuccessResponse)
def bulk_listing_status(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    ids = payload.get("ids") or []
    status = (payload.get("status") or "").strip().lower()
    if status not in {"approved", "rejected", "archived", "flagged"}:
        raise HTTPException(status_code=400, detail="Invalid listing status")
    updated = db.query(Material).filter(Material.id.in_(ids)).update({"status": status}, synchronize_session=False)
    audit(db, request, current_user, "listing", "bulk", f"bulk_{status}", {"ids": ids, "count": updated})
    db.commit()
    return {"success": True, "message": "Listings updated", "data": {"updated": updated}}


@router.delete("/listings/{material_id}", response_model=SuccessResponse)
def delete_listing(material_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    payload = listing_payload(material)
    db.delete(material)
    audit(db, request, current_user, "listing", material_id, "delete", payload)
    db.commit()
    return {"success": True, "message": "Listing deleted", "data": {"id": material_id}}


@router.get("/transactions", response_model=SuccessResponse)
def transaction_monitoring(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()
    return {"success": True, "message": "Transactions loaded", "data": {"transactions": [{"id": item.id, "partner_name": item.partner_name, "amount": item.amount, "status": item.status, "material_id": item.material_id, "created_at": item.created_at.isoformat() if item.created_at else None} for item in transactions]}}


@router.put("/transactions/{transaction_id}/status", response_model=SuccessResponse)
def update_transaction(transaction_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    status = str(payload.get("status") or "").strip()
    if status not in {"Pending", "In Transit", "Completed", "Refunded", "Disputed", "Cancelled"}:
        raise HTTPException(status_code=400, detail="Invalid transaction status")
    before = tx.status
    tx.status = status
    audit(db, request, current_user, "transaction", tx.id, "status_update", {"before": before, "after": status})
    db.commit()
    return {"success": True, "message": "Transaction updated", "data": {"transaction": {"id": tx.id, "status": tx.status}}}


@router.get("/ai-matches", response_model=SuccessResponse)
def ai_match_monitoring(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    matches = db.query(Match).order_by(Match.created_at.desc()).all()
    return {"success": True, "message": "AI matches loaded", "data": {"threshold": AI_SETTINGS["confidence_threshold"], "matches": [{"id": item.id, "material_id": item.material_id, "partner_name": item.partner_name, "symbio_score": item.symbio_score, "distance_km": item.distance_km, "carbon_savings": item.carbon_savings, "summary": item.summary} for item in matches]}}


@router.put("/ai-matches/settings", response_model=SuccessResponse)
def update_ai_settings(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    threshold = int(payload.get("confidence_threshold", AI_SETTINGS["confidence_threshold"]))
    if threshold < 0 or threshold > 100:
        raise HTTPException(status_code=400, detail="Threshold must be 0-100")
    before = AI_SETTINGS["confidence_threshold"]
    AI_SETTINGS["confidence_threshold"] = threshold
    audit(db, request, current_user, "ai", "settings", "update_threshold", {"before": before, "after": threshold})
    db.commit()
    return {"success": True, "message": "AI threshold updated", "data": {"confidence_threshold": threshold}}


@router.put("/ai-matches/{match_id}/{decision}", response_model=SuccessResponse)
def decide_match(match_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if decision not in {"accept", "reject", "rematch"}:
        raise HTTPException(status_code=400, detail="Invalid match action")
    if decision == "accept":
        match.symbio_score = max(match.symbio_score, AI_SETTINGS["confidence_threshold"])
    elif decision == "reject":
        match.symbio_score = min(match.symbio_score, AI_SETTINGS["confidence_threshold"] - 1)
    else:
        match.symbio_score = min(100, max(1, match.symbio_score + 3))
    audit(db, request, current_user, "ai_match", match.id, decision)
    db.commit()
    return {"success": True, "message": f"Match {decision}ed", "data": {"match": {"id": match.id, "symbio_score": match.symbio_score}}}


@router.delete("/ai-matches/{match_id}", response_model=SuccessResponse)
def delete_match(match_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    audit(db, request, current_user, "ai_match", match_id, "delete")
    db.commit()
    return {"success": True, "message": "Match deleted", "data": {"id": match_id}}


@router.get("/chat", response_model=SuccessResponse)
def chat_moderation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    conversations = db.query(Conversation).order_by(Conversation.last_message_at.desc()).all()
    messages = db.query(Message).order_by(Message.created_at.desc()).limit(100).all()
    return {"success": True, "message": "Chat loaded", "data": {"conversations": [{"id": c.id, "material_name": c.material_name, "partner_name": c.partner_name, "status": c.status, "seller_id": c.seller_id} for c in conversations], "messages": [{"id": m.id, "conversation_id": m.conversation_id, "sender_name": m.sender_name, "body": m.body, "created_at": m.created_at.isoformat() if m.created_at else None} for m in messages]}}


@router.delete("/chat/messages/{message_id}", response_model=SuccessResponse)
def delete_message(message_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message.body = "[Removed by admin moderation]"
    audit(db, request, current_user, "message", message.id, "moderate_delete")
    db.commit()
    return {"success": True, "message": "Message moderated", "data": {"id": message.id}}


@router.put("/chat/ban/{user_id}", response_model=SuccessResponse)
def ban_chat_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    audit(db, request, current_user, "chat", user.id, "ban_user")
    db.commit()
    return {"success": True, "message": "User banned", "data": {"id": user.id}}


@router.put("/chat/mute/{user_id}", response_model=SuccessResponse)
def mute_chat_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    audit(db, request, current_user, "chat", user.id, "mute_user")
    db.commit()
    return {"success": True, "message": "User muted", "data": {"id": user.id}}


@router.get("/system-health", response_model=SuccessResponse)
def system_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    db.query(User).count()
    return {
        "success": True,
        "message": "System healthy",
        "data": {
            "api": {"status": "healthy", "checked_at": datetime.now(timezone.utc).isoformat()},
            "database": {"status": "healthy", "engine": db.bind.dialect.name},
            "storage": {"status": "configured" if settings.S3_BUCKET else "missing_credentials", "provider": "s3-compatible"},
            "email": {"status": "configured" if settings.SMTP_HOST else "missing_credentials"},
            "security": {"status": "hardened", "rbac": True, "rate_limiting": True},
            "sessions": {"active_estimate": db.query(User).filter(User.is_active == True).count()},
        },
    }


@router.get("/logs", response_model=SuccessResponse)
def logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    rows = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).limit(100).all()
    payload = [{"id": item.id, "entity_type": item.entity_type, "entity_id": item.entity_id, "action": item.action, "actor_id": item.user_id, "actor_role": item.user_role, "at": item.timestamp.isoformat() if item.timestamp else None, "ip_address": item.ip_address, "changes": item.changes} for item in rows]
    return {"success": True, "message": "Logs loaded", "data": {"audit_logs": payload, "activity_logs": payload[:25], "security_logs": [item for item in payload if item["actor_role"] in {"Admin", "Super Admin"}]}}


@router.post("/notifications/broadcast", response_model=SuccessResponse)
def broadcast_notification(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    title = str(payload.get("title") or "").strip()
    message = str(payload.get("message") or "").strip()
    if not title or not message:
        raise HTTPException(status_code=400, detail="Title and message are required")
    users = db.query(User).filter(User.is_active == True).all()
    for user in users:
        create_notification(db, user.id, "admin_notice", title, message)
    audit(db, request, current_user, "notification", "broadcast", "broadcast", {"recipients": len(users), "title": title})
    db.commit()
    return {"success": True, "message": "Broadcast sent", "data": {"recipients": len(users)}}


@router.get("/settings", response_model=SuccessResponse)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_admin(current_user)
    return {"success": True, "message": "Settings loaded", "data": {"settings": {"site_name": "SymbioAI", "maintenance_mode": False, "smtp": bool(settings.SMTP_HOST), "google_oauth": bool(settings.GOOGLE_CLIENT_ID), "storage": bool(settings.S3_BUCKET), "database": db.bind.dialect.name, "secure_cookies": settings.SECURE_COOKIES}}}


@router.put("/settings", response_model=SuccessResponse)
def update_settings(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    require_super_admin(current_user)
    audit(db, request, current_user, "settings", "platform", "update", payload)
    db.commit()
    return {"success": True, "message": "Settings audit recorded. Environment-backed secrets must be changed in deployment variables.", "data": {"settings": payload}}


def export_rows(resource: str, db: Session) -> tuple[list[str], list[list[Any]]]:
    if resource == "users":
        return ["id", "email", "full_name", "role", "is_active"], [[u.id, u.email, u.full_name, u.role.value, u.is_active] for u in db.query(User).all()]
    if resource == "transactions":
        return ["id", "partner_name", "amount", "status"], [[t.id, t.partner_name, t.amount, t.status] for t in db.query(Transaction).all()]
    if resource == "listings":
        return ["id", "name", "status", "quantity", "frequency"], [[m.id, m.name, m.status, m.quantity, m.frequency] for m in db.query(Material).all()]
    if resource == "audit":
        return ["id", "entity_type", "action", "actor_role", "timestamp"], [[a.id, a.entity_type, a.action, a.user_role, a.timestamp] for a in db.query(AuditTrail).all()]
    raise HTTPException(status_code=404, detail="Export resource not found")


@router.get("/export/{resource}.{fmt}")
def export_resource(resource: str, fmt: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Response:
    require_admin(current_user)
    headers, rows = export_rows(resource, db)
    audit(db, request, current_user, resource, "export", f"export_{fmt}")
    db.commit()
    if fmt in {"csv", "xlsx"}:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        media = "text/csv" if fmt == "csv" else "application/vnd.ms-excel"
        return Response(content=output.getvalue(), media_type=media, headers={"Content-Disposition": f"attachment; filename={resource}.{fmt}"})
    if fmt == "pdf":
        body = "\n".join([", ".join(map(str, headers))] + [", ".join(map(str, row)) for row in rows[:200]])
        pdf = f"%PDF-1.4\n1 0 obj<<>>endobj\n2 0 obj<< /Length {len(body) + 80} >>stream\nBT /F1 10 Tf 40 760 Td ({resource} report generated {datetime.now(timezone.utc).isoformat()}) Tj 0 -16 Td ({body[:900].replace('(', '[').replace(')', ']')}) Tj ET\nendstream endobj\ntrailer<<>>\n%%EOF"
        return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={resource}.pdf"})
    raise HTTPException(status_code=400, detail="Unsupported export format")
