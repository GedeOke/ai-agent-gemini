from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = Field(default=None, description="image|audio|video|pdf|sticker")


class ChatRequest(BaseModel):
    tenant_id: str
    user_id: str
    locale: Optional[str] = "id"
    channel: Optional[str] = "web"
    messages: List[Message]
    typing_debounce_ms: Optional[int] = Field(default=800, description="Delay before responding to simulate natural wait")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Bubble(BaseModel):
    text: str
    delay_ms: Optional[int] = None


class ChatResponse(BaseModel):
    bubbles: List[Bubble]
    full_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    retrieved_context: List[str] = Field(default_factory=list)


class KnowledgeItem(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeUpsertRequest(BaseModel):
    tenant_id: str
    items: List[KnowledgeItem]


class PersonaSettings(BaseModel):
    persona: str = Field(default="sales", description="sales|support|custom")
    style_prompt: str = Field(default="Ramah, informatif, ringkas")
    tone: str = Field(default="neutral")
    language: str = Field(default="id")


class SopStep(BaseModel):
    name: str
    description: str
    order: int


class SalesSop(BaseModel):
    steps: List[SopStep] = Field(default_factory=list)


class TenantSettings(BaseModel):
    tenant_id: str
    api_key: Optional[str] = Field(default=None, description="API key per tenant")
    persona: PersonaSettings = Field(default_factory=PersonaSettings)
    sop: SalesSop = Field(default_factory=SalesSop)
    working_hours: str = Field(default="09:00-17:00")
    timezone: str = Field(default="Asia/Jakarta")
    followup_enabled: bool = True
    followup_interval_minutes: int = 60


class FollowUpRequest(BaseModel):
    tenant_id: str
    user_id: str
    reason: str
    scheduled_at: datetime
    channel: str = "web"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Contact(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactCreate(BaseModel):
    tenant_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    contact_id: Optional[str] = None
    user_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class SopState(BaseModel):
    tenant_id: str
    contact_id: Optional[str] = None
    user_id: Optional[str] = None
    current_step: Optional[str] = None
