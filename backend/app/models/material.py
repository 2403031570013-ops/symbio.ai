from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    chemical_composition = Column(Text, nullable=False)
    physical_state = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    certificate = Column(String, nullable=False)
    certificate_url = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    lab_report_url = Column(String, nullable=True)
    storage_provider = Column(String, nullable=True)
    owner_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
