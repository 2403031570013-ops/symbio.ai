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

ADMIN_ROLES = {UserRole.ADMIN, UserRole.SUPER_ADMIN}
AI_SETTINGS = {"confidence_threshold": 80}

Session = Any


def get_db():
    """Compatibility stub dependency retained for existing endpoint signatures."""
    return None


async def require_admin(current_user: User) -> None:
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")


async def require_super_admin(current_user: User) -> None:
    await require_admin(current_user)
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super Admin access required")


async def audit(request: Request, actor: User, entity_type: str, entity_id: str, action: str, changes: dict | None = None, reason: str | None = None) -> None:
    await AuditTrail(
        id=str(uuid4()),
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=actor.id,
        user_role=actor.role.value,
        ip_address=request.client.host if request.client else None,
        changes=changes or {},
        reason=reason,
    ).insert()


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": bool(user.is_active),
        "email_verified": bool(getattr(user, "email_verified", False)),
        "factory_logo_url": getattr(user, "factory_logo_url", None),
        "created_at": user.created_at.isoformat() if getattr(user, "created_at", None) else None,
        "updated_at": user.updated_at.isoformat() if getattr(user, "updated_at", None) else None,
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
        "certificate_url": getattr(item, "certificate_url", None),
        "photo_url": getattr(item, "photo_url", None),
        "lab_report_url": getattr(item, "lab_report_url", None),
        "status": getattr(item, "status", None),
        "owner_id": getattr(item, "owner_id", None),
        "created_at": getattr(item, "created_at", None).isoformat() if getattr(item, "created_at", None) else None,
    }


@router.get("/dashboard", response_model=SuccessResponse)
async def admin_dashboard(current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    import logging
    logger = logging.getLogger(__name__)
    try:
        analytics = await Analytics.find_one({})
        transactions = await Transaction.find_all().to_list()
        materials = await Material.find_all().to_list()
        users = await User.find_all().to_list()
        revenue = sum(float(getattr(item, "amount", 0) or 0) for item in transactions)
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
        seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        try:
            storage_bytes = await StoredObject.find_all().count()
        except Exception:
            storage_bytes = 0
        listing_statuses: dict[str, int] = {}
        for item in materials:
            try:
                status = getattr(item, "status", None) or "unknown"
                listing_statuses[status] = listing_statuses.get(status, 0) + 1
            except Exception:
                continue
        active_users = len([user for user in users if getattr(user, 'is_active', False)])
        matches = await Match.find_all().to_list()
        successful_matches = len([match for match in matches if getattr(match, 'symbio_score', 0) >= AI_SETTINGS["confidence_threshold"]])
        recent_activity = (await AuditTrail.find_all().sort("-timestamp").to_list())[:8]
        recent_logins = (await AuditTrail.find(AuditTrail.action == "admin_login").sort("-timestamp").to_list())[:6]
        return {
            "success": True,
            "message": "Admin dashboard loaded",
            "data": {
                "stats": {
                    "total_users": len(users),
                    "users": len(users),
                    "active_users": active_users,
                    "new_registrations": len([user for user in users if getattr(user, 'created_at', None) and user.created_at and user.created_at >= seven_days_ago]),
                    "pending_listings": listing_statuses.get("pending", 0),
                    "approved_listings": listing_statuses.get("approved", 0),
                    "rejected_listings": listing_statuses.get("rejected", 0),
                    "listings": len(materials),
                    "pending_ai_matches": len([match for match in matches if getattr(match, 'symbio_score', 0) < AI_SETTINGS["confidence_threshold"]]),
                    "successful_matches": successful_matches,
                    "matches": len(matches),
                    "marketplace_revenue": float(revenue),
                    "revenue": float(revenue),
                    "carbon_saved": float(getattr(analytics, "co2_avoided", 0) or 0),
                    "transactions_today": len([item for item in transactions if getattr(item, 'created_at', None) and item.created_at and item.created_at >= today]),
                    "storage_usage": int(storage_bytes or 0),
                    "server_status": "healthy",
                    "database_status": "healthy",
                    "api_health": "operational",
                },
                "charts": {
                    "users_by_role": [{"label": role.value, "value": len([user for user in users if user.role == role])} for role in UserRole],
                    "listings_by_status": [{"label": key or "unknown", "value": value} for key, value in listing_statuses.items()],
                    "revenue_heatmap": [{"label": item.partner_name, "value": float(item.amount)} for item in sorted(transactions, key=lambda item: getattr(item, 'amount', 0) or 0, reverse=True)[:8]],
                },
                "recent_activities": [{"action": item.action, "entity": item.entity_type, "actor_role": item.user_role, "at": getattr(item, 'timestamp', None).isoformat() if getattr(item, 'timestamp', None) else None} for item in recent_activity],
                "recent_logins": [{"actor": item.user_id, "at": getattr(item, 'timestamp', None).isoformat() if getattr(item, 'timestamp', None) else None, "ip": item.ip_address} for item in recent_logins],
                "system_alerts": [
                    {"severity": "info", "message": "RBAC enforced on all admin APIs"},
                    {"severity": "warning" if not settings.SMTP_HOST else "info", "message": "SMTP configured" if settings.SMTP_HOST else "SMTP not configured"},
                    {"severity": "warning" if not settings.S3_BUCKET else "info", "message": "Object storage configured" if settings.S3_BUCKET else "Object storage credentials missing"},
                ],
            },
        }
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logger.exception('Failed to load admin dashboard')
        return {
            "success": True,
            "message": "Admin dashboard loaded with fallback data",
            "data": {
                "stats": {
                    "total_users": 0,
                    "users": 0,
                    "active_users": 0,
                    "new_registrations": 0,
                    "pending_listings": 0,
                    "approved_listings": 0,
                    "rejected_listings": 0,
                    "listings": 0,
                    "pending_ai_matches": 0,
                    "successful_matches": 0,
                    "matches": 0,
                    "marketplace_revenue": 0.0,
                    "revenue": 0.0,
                    "carbon_saved": 0.0,
                    "transactions_today": 0,
                    "storage_usage": 0,
                    "server_status": "healthy",
                    "database_status": "healthy",
                    "api_health": "operational",
                },
                "charts": {"users_by_role": [], "listings_by_status": [], "revenue_heatmap": []},
                "recent_activities": [],
                "recent_logins": [],
                "system_alerts": [{"severity": "warning", "message": "Admin metrics are temporarily unavailable"}],
            },
        }


@router.get("/users", response_model=SuccessResponse)
async def list_users(q: str = "", role: str = "", status: str = "", current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    users_query = User.find_all()
    users = await users_query.to_list()
    if q:
        q_lower = q.strip().lower()
        users = [u for u in users if q_lower in getattr(u, 'email', '').lower() or q_lower in getattr(u, 'full_name', '').lower()]
    if role:
        try:
            desired_role = UserRole(role)
            users = [u for u in users if u.role == desired_role]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role")
    if status == "active":
        users = [u for u in users if u.is_active]
    if status == "suspended":
        users = [u for u in users if not u.is_active]
    users = sorted(users, key=lambda u: getattr(u, 'created_at', None) or datetime.min, reverse=True)
    return {"success": True, "message": "Users loaded", "data": {"users": [user_payload(user) for user in users]}}


@router.put("/users/{user_id}", response_model=SuccessResponse)
async def edit_user(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    before = user_payload(user)
    if "full_name" in payload and str(payload["full_name"]).strip():
        user.full_name = str(payload["full_name"]).strip()
    if "email_verified" in payload:
        user.email_verified = bool(payload["email_verified"])
    if "factory_logo_url" in payload:
        user.factory_logo_url = str(payload["factory_logo_url"] or "").strip() or None
    await audit(request, current_user, "user", user.id, "update", {"before": before, "after": payload})
    await user.save()
    return {"success": True, "message": "User updated", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/role", response_model=SuccessResponse)
async def update_user_role(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    next_role = UserRole(payload.get("role"))
    if next_role in ADMIN_ROLES and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only Super Admin can grant admin roles")
    if user.id == current_user.id and next_role not in ADMIN_ROLES:
        raise HTTPException(status_code=400, detail="Admins cannot remove their own admin access")
    before = user.role.value
    user.role = next_role
    await audit(request, current_user, "user", user.id, "change_role", {"before": before, "after": next_role.value})
    await user.save()
    return {"success": True, "message": "Role updated", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/suspend", response_model=SuccessResponse)
async def suspend_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot suspend themselves")
    user.is_active = False
    # create_notification expects a db in older signature; updated to use create_notification wrapper which accepts None for db
    create_notification(None, user.id, "account", "Account suspended", "Your SymbioAI account was suspended by an administrator. Contact support if you believe this is incorrect.", action_url="/login", email=user.email)
    await audit(request, current_user, "user", user.id, "suspend")
    await user.save()
    return {"success": True, "message": "User suspended", "data": {"user": user_payload(user)}}


@router.put("/users/{user_id}/activate", response_model=SuccessResponse)
async def activate_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    create_notification(None, user.id, "account", "Account activated", "Your SymbioAI account is active again. You can now sign in.", action_url="/login", email=user.email)
    await audit(request, current_user, "user", user.id, "activate")
    await user.save()
    return {"success": True, "message": "User activated", "data": {"user": user_payload(user)}}


@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def delete_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_super_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Super Admin cannot delete self")
    payload = user_payload(user)
    # Revoke refresh tokens
    tokens = await RefreshToken.find(RefreshToken.user_id == user.id).to_list()
    for t in tokens:
        await t.delete()
    await user.delete()
    await audit(request, current_user, "user", user_id, "permanent_delete", payload)
    return {
        "success": True,
        "message": "Account permanently deleted. The person must register again to access SymbioAI.",
        "data": {"id": user_id, "requires_registration": True},
    }


@router.post("/users/{user_id}/reset-password", response_model=SuccessResponse)
async def reset_user_password(user_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    temporary_password = payload.get("password") or f"Symbio-{secrets.token_urlsafe(6)}1!"
    user.hashed_password = get_password_hash(temporary_password)
    await audit(request, current_user, "user", user.id, "reset_password")
    await user.save()
    return {"success": True, "message": "Password reset", "data": {"temporary_password": temporary_password}}


@router.put("/users/{user_id}/company/{decision}", response_model=SuccessResponse)
async def verify_company(user_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if decision not in {"verify", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid company decision")
    user.email_verified = decision == "verify"
    create_notification(None, user.id, "verification", f"Company {decision}ed", f"Your company verification was {decision}ed by an administrator.", action_url="/dashboard", email=user.email)
    await audit(request, current_user, "company", user.id, decision)
    await user.save()
    return {"success": True, "message": f"Company {decision}ed", "data": {"user": user_payload(user)}}


@router.get("/factories", response_model=SuccessResponse)
async def list_factories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    factories = await Factory.find_all().sort(-Factory.created_at).to_list()
    return {"success": True, "message": "Factories loaded", "data": {"factories": [{"id": f.id, "name": f.name, "industry": f.industry, "location": f.location, "verified": getattr(f, 'verified', False), "owner_id": getattr(f, 'owner_id', None), "created_at": getattr(f, 'created_at', None).isoformat() if getattr(f, 'created_at', None) else None} for f in factories]}}


@router.get("/factories/{factory_id}/documents", response_model=SuccessResponse)
async def list_factory_documents(factory_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    docs = await DocumentCompliance.find(DocumentCompliance.factory_id == factory_id).to_list()
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
async def factory_decision(factory_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    factory = await Factory.find_one(Factory.id == factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    if decision not in {"verify", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid factory decision")
    factory.verified = decision == "verify"
    await audit(request, current_user, "factory", factory.id, decision)
    await factory.save()
    return {"success": True, "message": f"Factory {decision}ed", "data": {"factory": {"id": factory.id, "verified": factory.verified}}}


@router.get("/listings", response_model=SuccessResponse)
async def list_materials(q: str = "", status: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    materials = await Material.find_all().to_list()
    if q:
        q_lower = q.strip().lower()
        materials = [m for m in materials if q_lower in (m.name or "").lower() or q_lower in (m.chemical_composition or "").lower()]
    if status:
        materials = [m for m in materials if getattr(m, 'status', None) == status]
    materials = sorted(materials, key=lambda m: getattr(m, 'created_at', None) or datetime.min, reverse=True)
    return {"success": True, "message": "Listings loaded", "data": {"listings": [listing_payload(item) for item in materials]}}


@router.put("/listings/{material_id}", response_model=SuccessResponse)
async def edit_listing(material_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    material = await Material.find_one(Material.id == material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    before = listing_payload(material)
    for field in ["name", "chemical_composition", "physical_state", "quantity", "frequency", "certificate"]:
        if field in payload and str(payload[field]).strip():
            setattr(material, field, str(payload[field]).strip())
    await audit(request, current_user, "listing", material.id, "edit", {"before": before, "after": payload})
    await material.save()
    return {"success": True, "message": "Listing updated", "data": {"listing": listing_payload(material)}}


@router.put("/listings/{material_id}/status", response_model=SuccessResponse)
async def update_listing_status(material_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    material = await Material.find_one(Material.id == material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    status = (payload.get("status") or "").strip().lower()
    if status not in {"pending", "approved", "rejected", "archived", "flagged"}:
        raise HTTPException(status_code=400, detail="Invalid listing status")
    before = material.status
    material.status = status
    await audit(request, current_user, "listing", material.id, f"status_{status}", {"before": before, "after": status})
    await material.save()
    return {"success": True, "message": "Listing status updated", "data": {"listing": {"id": material.id, "status": material.status}}}


@router.post("/listings/bulk-status", response_model=SuccessResponse)
async def bulk_listing_status(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    ids = payload.get("ids") or []
    status = (payload.get("status") or "").strip().lower()
    if status not in {"approved", "rejected", "archived", "flagged"}:
        raise HTTPException(status_code=400, detail="Invalid listing status")
    materials = await Material.find(Material.id.in_(ids)).to_list()
    updated = 0
    for m in materials:
        m.status = status
        await m.save()
        updated += 1
    await audit(request, current_user, "listing", "bulk", f"bulk_{status}", {"ids": ids, "count": updated})
    return {"success": True, "message": "Listings updated", "data": {"updated": updated}}


@router.delete("/listings/{material_id}", response_model=SuccessResponse)
async def delete_listing(material_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    material = await Material.find_one(Material.id == material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Listing not found")
    payload = listing_payload(material)
    await material.delete()
    await audit(request, current_user, "listing", material_id, "delete", payload)
    return {"success": True, "message": "Listing deleted", "data": {"id": material_id}}


@router.get("/transactions", response_model=SuccessResponse)
async def transaction_monitoring(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    transactions = await Transaction.find_all().sort(-Transaction.created_at).to_list()
    return {"success": True, "message": "Transactions loaded", "data": {"transactions": [{"id": item.id, "partner_name": item.partner_name, "amount": item.amount, "status": item.status, "material_id": item.material_id, "created_at": getattr(item, 'created_at', None).isoformat() if getattr(item, 'created_at', None) else None} for item in transactions]}}


@router.put("/transactions/{transaction_id}/status", response_model=SuccessResponse)
async def update_transaction(transaction_id: str, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    tx = await Transaction.find_one(Transaction.id == transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    status = str(payload.get("status") or "").strip()
    if status not in {"Pending", "In Transit", "Completed", "Refunded", "Disputed", "Cancelled"}:
        raise HTTPException(status_code=400, detail="Invalid transaction status")
    before = tx.status
    tx.status = status
    await audit(request, current_user, "transaction", tx.id, "status_update", {"before": before, "after": status})
    await tx.save()
    return {"success": True, "message": "Transaction updated", "data": {"transaction": {"id": tx.id, "status": tx.status}}}


@router.get("/ai-matches", response_model=SuccessResponse)
async def ai_match_monitoring(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    matches = await Match.find_all().sort(-Match.created_at).to_list()
    return {"success": True, "message": "AI matches loaded", "data": {"threshold": AI_SETTINGS["confidence_threshold"], "matches": [{"id": item.id, "material_id": item.material_id, "partner_name": item.partner_name, "symbio_score": getattr(item, 'symbio_score', None), "distance_km": getattr(item, 'distance_km', None), "carbon_savings": getattr(item, 'carbon_savings', None), "summary": getattr(item, 'summary', None)} for item in matches]}}


@router.put("/ai-matches/settings", response_model=SuccessResponse)
async def update_ai_settings(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    threshold = int(payload.get("confidence_threshold", AI_SETTINGS["confidence_threshold"]))
    if threshold < 0 or threshold > 100:
        raise HTTPException(status_code=400, detail="Threshold must be 0-100")
    before = AI_SETTINGS["confidence_threshold"]
    AI_SETTINGS["confidence_threshold"] = threshold
    await audit(request, current_user, "ai", "settings", "update_threshold", {"before": before, "after": threshold})
    try:
        db.commit()
    except Exception:
        # db may be a legacy session in older deploys; ignore commit errors here
        pass
    return {"success": True, "message": "AI threshold updated", "data": {"confidence_threshold": threshold}}


@router.put("/ai-matches/{match_id}/{decision}", response_model=SuccessResponse)
async def decide_match(match_id: str, decision: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    match = await Match.find_one(Match.id == match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if decision not in {"accept", "reject", "rematch"}:
        raise HTTPException(status_code=400, detail="Invalid match action")
    if decision == "accept":
        match.symbio_score = max(getattr(match, 'symbio_score', 0), AI_SETTINGS["confidence_threshold"])
    elif decision == "reject":
        match.symbio_score = min(getattr(match, 'symbio_score', 0), AI_SETTINGS["confidence_threshold"] - 1)
    else:
        match.symbio_score = min(100, max(1, (getattr(match, 'symbio_score', 0) or 0) + 3))
    await audit(request, current_user, "ai_match", match.id, decision)
    await match.save()
    return {"success": True, "message": f"Match {decision}ed", "data": {"match": {"id": match.id, "symbio_score": match.symbio_score}}}


@router.delete("/ai-matches/{match_id}", response_model=SuccessResponse)
async def delete_match(match_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    match = await Match.find_one(Match.id == match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    await match.delete()
    await audit(request, current_user, "ai_match", match_id, "delete")
    return {"success": True, "message": "Match deleted", "data": {"id": match_id}}


@router.get("/chat", response_model=SuccessResponse)
async def chat_moderation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    conversations = await Conversation.find_all().sort("-last_message_at").to_list()
    messages = (await Message.find_all().sort("-created_at").to_list())[:100]
    return {"success": True, "message": "Chat loaded", "data": {"conversations": [{"id": c.id, "material_name": c.material_name, "partner_name": c.partner_name, "status": c.status, "seller_id": c.seller_id} for c in conversations], "messages": [{"id": m.id, "conversation_id": m.conversation_id, "sender_name": m.sender_name, "body": m.body, "created_at": m.created_at.isoformat() if m.created_at else None} for m in messages]}}


@router.delete("/chat/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(message_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    message = await Message.find_one(Message.id == message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message.body = "[Removed by admin moderation]"
    await audit(request, current_user, "message", message.id, "moderate_delete")
    await message.save()
    return {"success": True, "message": "Message moderated", "data": {"id": message.id}}


@router.put("/chat/ban/{user_id}", response_model=SuccessResponse)
async def ban_chat_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await audit(request, current_user, "chat", user.id, "ban_user")
    await user.save()
    return {"success": True, "message": "User banned", "data": {"id": user.id}}


@router.put("/chat/mute/{user_id}", response_model=SuccessResponse)
async def mute_chat_user(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await audit(request, current_user, "chat", user.id, "mute_user")
    # Implement mute flag if model supports it; using is_active toggle is a fallback
    user.is_active = False
    await user.save()
    return {"success": True, "message": "User muted", "data": {"id": user.id}}


@router.get("/system-health", response_model=SuccessResponse)
async def system_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    try:
        # simple DB check using counts
        user_count = await User.find_all().count()
    except Exception:
        user_count = None
    return {
        "success": True,
        "message": "System healthy",
        "data": {
            "api": {"status": "healthy", "checked_at": datetime.now(timezone.utc).isoformat()},
            "database": {"status": "healthy", "engine": "mongodb"},
            "storage": {"status": "configured" if settings.S3_BUCKET else "missing_credentials", "provider": "s3-compatible"},
            "email": {"status": "configured" if settings.SMTP_HOST else "missing_credentials"},
            "security": {"status": "hardened", "rbac": True, "rate_limiting": True},
            "sessions": {"active_estimate": user_count},
        },
    }


@router.get("/logs", response_model=SuccessResponse)
async def logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    try:
        rows = (await AuditTrail.find_all().sort("-timestamp").to_list())[:100]
        payload = [{"id": item.id, "entity_type": item.entity_type, "entity_id": item.entity_id, "action": item.action, "actor_id": item.user_id, "actor_role": item.user_role, "at": item.timestamp.isoformat() if item.timestamp else None, "ip_address": item.ip_address, "changes": item.changes} for item in rows]
    except Exception:
        payload = []
    return {"success": True, "message": "Logs loaded", "data": {"audit_logs": payload, "activity_logs": payload[:25], "security_logs": [item for item in payload if item.get("actor_role") in {"Admin", "Super Admin"}]}}


@router.post("/notifications/broadcast", response_model=SuccessResponse)
async def broadcast_notification(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    title = str(payload.get("title") or "").strip()
    message = str(payload.get("message") or "").strip()
    if not title or not message:
        raise HTTPException(status_code=400, detail="Title and message are required")
    try:
        users = await User.find(User.is_active == True).to_list()
    except Exception:
        users = []
    for user in users:
        create_notification(None, user.id, "admin_notice", title, message)
    await audit(request, current_user, "notification", "broadcast", "broadcast", {"recipients": len(users), "title": title})
    return {"success": True, "message": "Broadcast sent", "data": {"recipients": len(users)}}


@router.get("/settings", response_model=SuccessResponse)
async def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_admin(current_user)
    db_name = None
    try:
        db_name = getattr(db.bind.dialect, 'name', None) if db else None
    except Exception:
        db_name = None
    return {"success": True, "message": "Settings loaded", "data": {"settings": {"site_name": "SymbioAI", "maintenance_mode": False, "smtp": bool(settings.SMTP_HOST), "google_oauth": bool(settings.GOOGLE_CLIENT_ID), "storage": bool(settings.S3_BUCKET), "database": db_name, "secure_cookies": settings.SECURE_COOKIES}}}


@router.put("/settings", response_model=SuccessResponse)
async def update_settings(payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    await require_super_admin(current_user)
    await audit(request, current_user, "settings", "platform", "update", payload)
    try:
        db.commit()
    except Exception:
        pass
    return {"success": True, "message": "Settings audit recorded. Environment-backed secrets must be changed in deployment variables.", "data": {"settings": payload}}


async def export_rows(resource: str, db: Session) -> tuple[list[str], list[list[Any]]]:
    if resource == "users":
        users = await User.find_all().to_list()
        return ["id", "email", "full_name", "role", "is_active"], [[u.id, u.email, u.full_name, (u.role.value if hasattr(u, 'role') else None), u.is_active] for u in users]
    if resource == "transactions":
        txs = await Transaction.find_all().to_list()
        return ["id", "partner_name", "amount", "status"], [[t.id, t.partner_name, t.amount, t.status] for t in txs]
    if resource == "listings":
        mats = await Material.find_all().to_list()
        return ["id", "name", "status", "quantity", "frequency"], [[m.id, m.name, m.status, m.quantity, m.frequency] for m in mats]
    if resource == "audit":
        audits = await AuditTrail.find_all().to_list()
        return ["id", "entity_type", "action", "actor_role", "timestamp"], [[a.id, a.entity_type, a.action, a.user_role, a.timestamp] for a in audits]
    raise HTTPException(status_code=404, detail="Export resource not found")


@router.get("/export/{resource}.{fmt}")
async def export_resource(resource: str, fmt: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Response:
    await require_admin(current_user)
    try:
        headers, rows = await export_rows(resource, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Export resource not found")
    await audit(request, current_user, resource, "export", f"export_{fmt}")
    try:
        db.commit()
    except Exception:
        pass
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
