import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.auth import get_current_user
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.get("", response_model=SuccessResponse)
def list_shipments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transactions = _run(Transaction.find(Transaction.status != "Draft").to_list())
    return {"success": True, "message": "Operation successful", "data": {"shipments": [{"id": txn.id, "partner_name": txn.partner_name, "status": txn.status} for txn in transactions]}}


@router.post("", response_model=SuccessResponse)
def create_shipment(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction_id = payload.get("transaction_id") or str(uuid4())
    return {"success": True, "message": "Operation successful", "data": {"shipment": {"id": transaction_id, "status": "Scheduled"}}}
