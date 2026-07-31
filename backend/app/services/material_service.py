import asyncio
from inspect import isawaitable
from typing import Any
from uuid import uuid4

from app.models.material import Material


def _run(coro):
    if isawaitable(coro):
        async def _awaitable_wrapper():
            return await coro

        return asyncio.run(_awaitable_wrapper())
    return asyncio.run(coro)


def create_material(db, *, owner_id: str, payload: dict[str, Any]) -> Material:
    material = Material(id=str(uuid4()), owner_id=owner_id, **payload)
    _run(material.insert())
    return material
