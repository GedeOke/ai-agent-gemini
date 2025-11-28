import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import dependencies
from app.models.schemas import KnowledgeUpsertRequest
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upsert")
async def upsert_kb(payload: KnowledgeUpsertRequest, _: ApiKeyDep) -> dict:
    try:
        await dependencies.rag_service.upsert(payload.items)
        return {"status": "ok", "count": len(payload.items)}
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("KB upsert failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upsert knowledge base",
        ) from exc
