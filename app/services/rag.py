import logging
from typing import List

import math
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import KnowledgeItemModel
from app.models.schemas import ChatRequest, KnowledgeItem
from app.services.embeddings import EmbeddingClient

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, embedding_client: EmbeddingClient) -> None:
        self.embedding_client = embedding_client

    async def upsert(self, session: AsyncSession, tenant_id: str, items: List[KnowledgeItem]) -> None:
        try:
            contents = [item.content for item in items]
            vectors = await self.embedding_client.embed(contents)
            for item in items:
                vec = vectors.pop(0) if vectors else []
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
                    db_item.embedding = vec
                else:
                    session.add(
                        KnowledgeItemModel(
                            tenant_id=tenant_id,
                            title=item.title,
                            content=item.content,
                            tags=item.tags,
                            embedding=vec,
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
            user_query = " ".join(msg.content for msg in payload.messages if msg.role == "user")
            user_vecs = await self.embedding_client.embed([user_query])
            if not user_vecs:
                return []
            user_vec = user_vecs[0]

            stmt = select(KnowledgeItemModel).where(KnowledgeItemModel.tenant_id == payload.tenant_id).limit(100)
            result = await session.execute(stmt)
            items = result.scalars().all()

            scored = []
            for item in items:
                if not item.embedding:
                    continue
                score = self._cosine_similarity(user_vec, item.embedding)
                scored.append((score, item.content))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [text for _, text in scored[:5]]
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to retrieve context")
            return []

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        if len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
