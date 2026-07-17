import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.endpoints.auth import get_current_user
from app.core.cache import cache_service
from app.models.material import Material
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.material import MaterialCreate, MaterialOut, MaterialUpdate

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.get("", response_model=SuccessResponse)
def list_materials(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cache_key = f"materials:{current_user.id}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    materials = _run(Material.find_all().to_list())
    payload = {"success": True, "message": "Operation successful", "data": {"materials": [MaterialOut.model_validate(material).model_dump() for material in materials]}}
    cache_service.set(cache_key, payload, ttl_seconds=60)
    return payload


@router.post("", response_model=SuccessResponse)
def create_material(material_in: MaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    material = Material(
        id=str(uuid4()),
        name=material_in.name,
        chemical_composition=material_in.chemical_composition,
        physical_state=material_in.physical_state,
        quantity=material_in.quantity,
        frequency=material_in.frequency,
        certificate=material_in.certificate,
        certificate_url=material_in.certificate_url,
        photo_url=material_in.photo_url,
        lab_report_url=material_in.lab_report_url,
        storage_provider=material_in.storage_provider,
        owner_id=current_user.id,
    )
    _run(material.insert())
    cache_service.invalidate("materials:")
    return {"success": True, "message": "Operation successful", "data": {"material": MaterialOut.model_validate(material).model_dump()}}


@router.get("/{material_id}", response_model=SuccessResponse)
def get_material(material_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    material = _run(Material.find_one(Material.id == material_id))
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"success": True, "message": "Operation successful", "data": {"material": MaterialOut.model_validate(material).model_dump()}}


@router.put("/{material_id}", response_model=SuccessResponse)
def update_material(material_id: str, material_in: MaterialUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    material = _run(Material.find_one(Material.id == material_id))
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    for field, value in material_in.model_dump().items():
        setattr(material, field, value)

    _run(material.save())
    return {"success": True, "message": "Operation successful", "data": {"material": MaterialOut.model_validate(material).model_dump()}}


@router.delete("/{material_id}", response_model=SuccessResponse)
def delete_material(material_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    material = _run(Material.find_one(Material.id == material_id))
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    _run(material.delete())
    return {"success": True, "message": "Operation successful", "data": {}}
