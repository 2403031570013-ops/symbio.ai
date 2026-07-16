"""Persisted admin service and verification cases."""
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, DateTime, JSON, String, Text
from app.db.session import Base


class ServiceCase(Base):
    __tablename__ = "service_cases"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    case_number = Column(String, unique=True, nullable=False, index=True)
    case_type = Column(String, nullable=False, index=True)
    subject_user_id = Column(String, nullable=True, index=True)
    factory_id = Column(String, nullable=True, index=True)
    assigned_to = Column(String, nullable=True)
    priority = Column(String, nullable=False, default="Medium")
    status = Column(String, nullable=False, default="Pending", index=True)
    timeline = Column(JSON, nullable=False, default=list)
    comments = Column(JSON, nullable=False, default=list)
    internal_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
