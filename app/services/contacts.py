import logging
from typing import List, Optional

import phonenumbers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ChatMessageModel, ContactModel
from app.models.schemas import ChatMessage, Contact, ContactCreate

logger = logging.getLogger(__name__)


def _normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    try:
        parsed = phonenumbers.parse(phone, "ID")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return phone.strip()
    return phone.strip()


class ContactService:
    async def upsert(self, session: AsyncSession, payload: ContactCreate) -> Contact:
        norm_phone = _normalize_phone(payload.phone)
        stmt = select(ContactModel).where(
            ContactModel.tenant_id == payload.tenant_id,
            ContactModel.phone == norm_phone,
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        try:
            if existing:
                if payload.name:
                    existing.name = payload.name
                if payload.email:
                    existing.email = payload.email
                existing.meta = payload.metadata or existing.meta
                await session.commit()
                await session.refresh(existing)
                logger.info("Updated contact %s", existing.id)
                return self._to_schema(existing)
            contact = ContactModel(
                tenant_id=payload.tenant_id,
                name=payload.name,
                phone=norm_phone,
                email=payload.email,
                meta=payload.metadata or {},
            )
            session.add(contact)
            await session.commit()
            await session.refresh(contact)
            logger.info("Created contact %s", contact.id)
            return self._to_schema(contact)
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to upsert contact")
            raise exc

    async def get(self, session: AsyncSession, contact_id: str, tenant_id: str) -> Optional[Contact]:
        stmt = select(ContactModel).where(ContactModel.id == contact_id, ContactModel.tenant_id == tenant_id)
        row = (await session.execute(stmt)).scalar_one_or_none()
        return self._to_schema(row) if row else None

    async def list(self, session: AsyncSession, tenant_id: str, limit: int = 50) -> List[Contact]:
        stmt = select(ContactModel).where(ContactModel.tenant_id == tenant_id).order_by(ContactModel.created_at.desc()).limit(
            limit
        )
        rows = (await session.execute(stmt)).scalars().all()
        return [self._to_schema(r) for r in rows]

    async def log_message(self, session: AsyncSession, msg: ChatMessage) -> None:
        try:
            model = ChatMessageModel(
                tenant_id=msg.tenant_id,
                contact_id=msg.contact_id,
                user_id=msg.user_id,
                role=msg.role,
                content=msg.content,
                meta=msg.metadata,
            )
            session.add(model)
            await session.commit()
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to log chat message")
            raise exc

    async def history(self, session: AsyncSession, tenant_id: str, contact_id: Optional[str] = None, limit: int = 50) -> List[ChatMessage]:
        stmt = select(ChatMessageModel).where(ChatMessageModel.tenant_id == tenant_id).order_by(
            ChatMessageModel.created_at.desc()
        ).limit(limit)
        if contact_id:
            stmt = stmt.where(ChatMessageModel.contact_id == contact_id)
        rows = (await session.execute(stmt)).scalars().all()
        return [self._msg_schema(r) for r in rows]

    @staticmethod
    def _to_schema(model: ContactModel) -> Contact:
        return Contact(
            id=str(model.id),
            tenant_id=model.tenant_id,
            name=model.name,
            phone=model.phone,
            email=model.email,
            metadata=model.meta or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _msg_schema(model: ChatMessageModel) -> ChatMessage:
        return ChatMessage(
            id=str(model.id),
            tenant_id=model.tenant_id,
            contact_id=str(model.contact_id) if model.contact_id else None,
            user_id=model.user_id,
            role=model.role,
            content=model.content,
            metadata=model.meta or {},
            created_at=model.created_at,
        )
