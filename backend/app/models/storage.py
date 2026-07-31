from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class StoredObject(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    owner_id: Indexed(str)
    purpose: Indexed(str)
    object_key: str
    url: str
    content_type: str
    original_name: str
    provider: str = Field(default="s3")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "stored_objects"

