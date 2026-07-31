from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document
from pydantic import Field


class Transaction(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    partner_name: str
    amount: float
    status: str = Field(default="Pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "transactions"

