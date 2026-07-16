from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, nullable=True, index=True)
    material_name = Column(String, nullable=False)
    partner_name = Column(String, nullable=False)
    buyer_id = Column(String, nullable=True, index=True)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="negotiating")
    unread_count = Column(Integer, nullable=False, default=0)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    sender_name = Column(String, nullable=False)
    message_type = Column(String, nullable=False, default="text")
    body = Column(Text, nullable=False)
    attachment_name = Column(String, nullable=True)
    attachment_type = Column(String, nullable=True)
    offer_amount = Column(String, nullable=True)
    offer_status = Column(String, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
