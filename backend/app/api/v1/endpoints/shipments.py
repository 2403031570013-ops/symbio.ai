import asyncio
from inspect import isawaitable
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


async def _run(coro):
    if isawaitable(coro):
        return await coro
    return coro


@router.get("", response_model=SuccessResponse)
async def list_shipments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transactions = await _run(Transaction.find(Transaction.status != "Draft").to_list())
    return {"success": True, "message": "Operation successful", "data": {"shipments": [{"id": txn.id, "partner_name": txn.partner_name, "status": txn.status} for txn in transactions]}}


@router.post("", response_model=SuccessResponse)
async def create_shipment(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction_id = payload.get("transaction_id") or str(uuid4())
    return {"success": True, "message": "Operation successful", "data": {"shipment": {"id": transaction_id, "status": "Scheduled"}}}
