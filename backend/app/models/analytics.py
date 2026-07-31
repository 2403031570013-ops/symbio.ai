from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document
from pydantic import Field


class Analytics(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    revenue_generated: float = Field(default=0.0)
    co2_avoided: float = Field(default=0.0)
    landfill_diversion: float = Field(default=0.0)
    active_matches: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "analytics"

