from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class Notification(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: Indexed(str)
    category: str
    title: str
    message: str
    action_url: Optional[str] = Field(default=None)
    read: bool = Field(default=False)
    delivered_email: bool = Field(default=False)
    delivered_push: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "notifications"

