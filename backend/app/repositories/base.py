import asyncio
from inspect import isawaitable
from typing import Generic, TypeVar, Any

ModelType = TypeVar("ModelType")


def _run(coro):
    if isawaitable(coro):
        async def _awaitable_wrapper():
            return await coro

        return asyncio.run(_awaitable_wrapper())
    return asyncio.run(coro)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Any):
        self.model = model
        self.db = db

    def get_all(self):
        return _run(self.model.find_all().to_list())

    def get_by_id(self, id: str):
        return _run(self.model.find_one(self.model.id == id))
