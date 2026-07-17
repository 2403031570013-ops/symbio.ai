import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.auth import get_current_user
from app.models.storage import StoredObject
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.storage_service import StorageNotConfigured, create_presigned_upload

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.post("/presign", response_model=SuccessResponse)
def presign_upload(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    filename = (payload.get("filename") or "").strip()
    content_type = (payload.get("content_type") or "application/octet-stream").strip()
    purpose = (payload.get("purpose") or "attachment").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    try:
        signed = create_presigned_upload(current_user.id, purpose, filename, content_type)
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    stored = StoredObject(
        id=str(uuid4()),
        owner_id=current_user.id,
        purpose=purpose,
        object_key=signed["object_key"],
        url=signed["url"],
        content_type=content_type,
        original_name=filename,
        provider="s3",
    )
    _run(stored.insert())
    return {"success": True, "message": "Upload URL created", "data": {"upload": {**signed, "id": stored.id}}}


@router.get("/objects", response_model=SuccessResponse)
def list_objects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    objects = _run(StoredObject.find(StoredObject.owner_id == current_user.id).sort(-StoredObject.created_at).to_list())
    return {
        "success": True,
        "message": "Objects loaded",
        "data": {"objects": [{"id": item.id, "purpose": item.purpose, "url": item.url, "original_name": item.original_name, "content_type": item.content_type} for item in objects]},
    }
