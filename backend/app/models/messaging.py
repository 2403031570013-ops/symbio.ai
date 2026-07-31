from datetime import datetime
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class Conversation(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")

    match_id: Optional[str] = Field(default=None)
    material_name: str
    partner_name: str

    buyer_id: Optional[str] = Field(default=None)
    seller_id: str

    status: str = Field(default="negotiating")
    unread_count: int = Field(default=0)

    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "conversations"


class Message(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")

    conversation_id: str
    sender_id: str
    sender_name: str

    message_type: str = Field(default="text")
    body: str

    attachment_name: Optional[str] = Field(default=None)
    attachment_type: Optional[str] = Field(default=None)

    offer_amount: Optional[str] = Field(default=None)
    offer_status: Optional[str] = Field(default=None)

    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "messages"