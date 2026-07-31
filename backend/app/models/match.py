from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document
from pydantic import Field


class Match(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    partner_name: str
    symbio_score: int
    distance_km: float
    carbon_savings: str
    summary: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "matches"

