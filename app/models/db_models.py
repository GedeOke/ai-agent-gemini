import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id = Column(String, primary_key=True, index=True)
    api_key = Column(String, nullable=False)
    persona = Column(JSON, nullable=False, default=dict)
    sop = Column(JSON, nullable=False, default=dict)
    working_hours = Column(String, nullable=False, default="09:00-17:00")
    timezone = Column(String, nullable=False, default="Asia/Jakarta")
    followup_enabled = Column(Boolean, nullable=False, default=True)
    followup_interval_minutes = Column(Float, nullable=False, default=60.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    knowledge_items = relationship("KnowledgeItemModel", back_populates="tenant", cascade="all, delete-orphan")
    followups = relationship("FollowUpModel", back_populates="tenant", cascade="all, delete-orphan")


class KnowledgeItemModel(Base):
    __tablename__ = "knowledge_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    embedding = Column(JSON, default=list)  # store vector as list of floats (for sqlite/postgres json)

    tenant = relationship("Tenant", back_populates="knowledge_items")


class FollowUpModel(Base):
    __tablename__ = "followups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    channel = Column(String, nullable=False, default="web")
    meta = Column("metadata", JSON, default=dict)  # store in DB column "metadata" but avoid reserved attr name
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="pending")  # pending|sent|failed
    last_error = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="followups")


class ContactModel(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    meta = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant")
    chat_messages = relationship("ChatMessageModel", back_populates="contact", cascade="all, delete-orphan")


class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # user|assistant|system
    content = Column(Text, nullable=False)
    meta = Column("metadata", JSON, default=dict)  # avoid reserved attr name
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("ContactModel", back_populates="chat_messages")
