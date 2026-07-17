import asyncio
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


def _run(coro):
    return asyncio.run(coro)


@router.get("", response_model=SuccessResponse)
def list_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transactions = _run(Transaction.find_all().to_list())
    return {"success": True, "message": "Operation successful", "data": {"transactions": [TransactionOut.model_validate(transaction).model_dump() for transaction in transactions]}}


@router.post("", response_model=SuccessResponse)
def create_transaction(transaction_in: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction = Transaction(id=str(uuid4()), **transaction_in.model_dump())
    _run(transaction.insert())
    return {"success": True, "message": "Operation successful", "data": {"transaction": TransactionOut.model_validate(transaction).model_dump()}}


@router.get("/{transaction_id}", response_model=SuccessResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    transaction = _run(Transaction.find_one(Transaction.id == transaction_id))
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"success": True, "message": "Operation successful", "data": {"transaction": TransactionOut.model_validate(transaction).model_dump()}}
