import asyncio
from inspect import isawaitable
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.auth import get_current_user
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.transaction import TransactionCreate, TransactionOut

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


async def _run(coro):
    if isawaitable(coro):
        return await coro
    return coro


@router.get("", response_model=SuccessResponse)
async def list_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transactions = await _run(Transaction.find_all().to_list())
    return {"success": True, "message": "Operation successful", "data": {"transactions": [TransactionOut.model_validate(transaction).model_dump() for transaction in transactions]}}


@router.post("", response_model=SuccessResponse)
async def create_transaction(transaction_in: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction = Transaction(id=str(uuid4()), **transaction_in.model_dump())
    await _run(transaction.insert())
    return {"success": True, "message": "Operation successful", "data": {"transaction": TransactionOut.model_validate(transaction).model_dump()}}


@router.get("/{transaction_id}", response_model=SuccessResponse)
async def get_transaction(transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction = await _run(Transaction.find_one(Transaction.id == transaction_id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"success": True, "message": "Operation successful", "data": {"transaction": TransactionOut.model_validate(transaction).model_dump()}}
