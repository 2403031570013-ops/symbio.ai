"""Persisted admin service and verification cases."""
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class ServiceCase(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    case_number: Indexed(str, unique=True)
    case_type: Indexed(str)
    subject_user_id: Indexed(Optional[str]) = Field(default=None)
    factory_id: Indexed(Optional[str]) = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    priority: str = Field(default="Medium")
    status: Indexed(str, default="Pending")
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    comments: List[Dict[str, Any]] = Field(default_factory=list)
    internal_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    class Settings:
        collection = "service_cases"
