from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.db.session import Base


class StoredObject(Base):
    __tablename__ = "stored_objects"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, nullable=False, index=True)
    purpose = Column(String, nullable=False, index=True)
    object_key = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="s3")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
