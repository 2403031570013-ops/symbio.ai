from datetime import datetime
from typing import Optional
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class Material(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    chemical_composition: str
    physical_state: str
    quantity: str
    frequency: str
    certificate: str
    certificate_url: Optional[str] = Field(default=None)
    photo_url: Optional[str] = Field(default=None)
    lab_report_url: Optional[str] = Field(default=None)
    storage_provider: Optional[str] = Field(default=None)
    owner_id: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "materials"

