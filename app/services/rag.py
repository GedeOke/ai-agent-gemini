import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import KnowledgeItemModel
from app.models.schemas import ChatRequest, KnowledgeItem

logger = logging.getLogger(__name__)


class RAGService:
    """
    Simple DB-backed retrieval; still placeholder before vector search.
    """

    async def upsert(self, session: AsyncSession, tenant_id: str, items: List[KnowledgeItem]) -> None:
        try:
            for item in items:
                db_item = None
                if item.id:
                    result = await session.execute(
                        select(KnowledgeItemModel).where(
                            KnowledgeItemModel.id == item.id, KnowledgeItemModel.tenant_id == tenant_id
                        )
                    )
                    db_item = result.scalar_one_or_none()
                if db_item:
                    db_item.title = item.title
                    db_item.content = item.content
                    db_item.tags = item.tags
                else:
                    session.add(
                        KnowledgeItemModel(
                            tenant_id=tenant_id,
                            title=item.title,
                            content=item.content,
                            tags=item.tags,
                        )
                    )
            await session.commit()
            logger.info("Upserted %s knowledge items for tenant=%s", len(items), tenant_id)
        except Exception as exc:  # pragma: no cover - defensive
            await session.rollback()
            logger.exception("Failed to upsert knowledge")
            raise exc

    async def retrieve(self, session: AsyncSession, payload: ChatRequest) -> List[str]:
        try:
            keywords = {word.lower() for msg in payload.messages for word in msg.content.split()}
            stmt = select(KnowledgeItemModel).where(KnowledgeItemModel.tenant_id == payload.tenant_id).limit(25)
            result = await session.execute(stmt)
            items = result.scalars().all()
            hits = [item.content for item in items if any(tag.lower() in keywords for tag in (item.tags or []))]
            return hits[:5]
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to retrieve context")
            return []
