import logging
from typing import List

from app.models.schemas import ChatRequest, KnowledgeItem

logger = logging.getLogger(__name__)


class RAGService:
    """
    Simplified retrieval stub. Replace with vector search later.
    """

    def __init__(self) -> None:
        self._memory: list[KnowledgeItem] = []

    async def upsert(self, items: List[KnowledgeItem]) -> None:
        try:
            self._memory.extend(items)
            logger.info("Upserted %s knowledge items", len(items))
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to upsert knowledge")
            raise exc

    async def retrieve(self, payload: ChatRequest) -> List[str]:
        try:
            # Very naive keyword match as placeholder.
            keywords = {word.lower() for msg in payload.messages for word in msg.content.split()}
            hits = [item.content for item in self._memory if any(tag.lower() in keywords for tag in item.tags)]
            return hits[:5]
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to retrieve context")
            return []
