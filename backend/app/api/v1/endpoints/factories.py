import asyncio
from inspect import isawaitable
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.auth import get_current_user
from app.models.factory import Factory
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.factory import FactoryCreate, FactoryOut, FactoryUpdate

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


async def _run(coro):
    if isawaitable(coro):
        return await coro
    return coro


@router.get("", response_model=SuccessResponse)
async def list_factories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    factories = await _run(Factory.find(Factory.owner_id == current_user.id).to_list())
    return {"success": True, "message": "Operation successful", "data": {"factories": [FactoryOut.model_validate(factory).model_dump() for factory in factories]}}


@router.post("", response_model=SuccessResponse)
async def create_factory(factory_in: FactoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    factory = Factory(id=str(uuid4()), owner_id=current_user.id, **factory_in.model_dump())
    await _run(factory.insert())
    return {"success": True, "message": "Operation successful", "data": {"factory": FactoryOut.model_validate(factory).model_dump()}}


@router.put("/{factory_id}", response_model=SuccessResponse)
async def update_factory(factory_id: str, factory_in: FactoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    factory = await _run(Factory.find_one(Factory.id == factory_id))
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    if factory.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in factory_in.model_dump(exclude_unset=True).items():
        setattr(factory, field, value)

    await _run(factory.save())
    return {"success": True, "message": "Operation successful", "data": {"factory": FactoryOut.model_validate(factory).model_dump()}}
