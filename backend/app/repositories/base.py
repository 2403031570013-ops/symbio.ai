import asyncio
from typing import Generic, TypeVar, Any

ModelType = TypeVar("ModelType")


def _run(coro):
    return asyncio.run(coro)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Any):
        self.model = model
        self.db = db

    def get_all(self):
        return _run(self.model.find_all().to_list())

    def get_by_id(self, id: str):
        return _run(self.model.find_one(self.model.id == id))
