import asyncio
from typing import Any
from uuid import uuid4

from app.models.material import Material


def _run(coro):
    return asyncio.run(coro)


def create_material(db, *, owner_id: str, payload: dict[str, Any]) -> Material:
    material = Material(id=str(uuid4()), owner_id=owner_id, **payload)
    _run(material.insert())
    return material
