from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document
from pydantic import Field


class Factory(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    industry: str
    location: str
    verified: bool = Field(default=False)
    owner_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "factories"

